"""The layout reconstruction and the browser's PDF path, on invented text.

Hand-built fragment lists check the geometry: two columns keep their order
and spacing, right-aligned amounts land under their header, a word split
into fragments is joined, sideways text gets a row of its own. The fixtures
in tests/fixtures/pdf/ then take each bank's invented statement through
layout, extraction and the reconciliation gate, and must yield exactly the
CSV written beside them. Nothing here touches a real statement.

    pixi run test
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import pdf_import  # noqa: E402
from pdf_layout import layout, layout_page  # noqa: E402

FIXTURES = ROOT / 'tests' / 'fixtures' / 'pdf'
CW = 5.0   # the character width the hand-built fragments below are drawn at


def frag(s, x, y, size=9.0, **extra):
    return {'str': s, 'x': x, 'y': y, 'width': len(s) * CW, 'height': size, **extra}


# ---------------------------------------------------------------- geometry
def test_two_columns_keep_their_order_and_a_wide_gap():
    text = layout_page([frag('Amount', 300, 700), frag('Description', 50, 700),
                        frag('45.67', 305, 686), frag('CORNER GROCER', 50, 686)])
    lines = text.splitlines()
    assert lines[0].index('Description') < lines[0].index('Amount')
    assert '  ' in lines[1].split('GROCER')[1]      # column gap survives as two or more spaces
    assert lines[1].index('45.67') - lines[1].index('CORNER') == pytest.approx(255 / CW, abs=1)


def test_right_aligned_amounts_sit_under_their_header():
    header = frag('Withdrawals', 300, 700)
    a = frag('1,234.56', 300 + len('Withdrawals') * CW - len('1,234.56') * CW, 686)
    b = frag('9.99', 300 + len('Withdrawals') * CW - len('9.99') * CW, 672)
    lines = layout_page([header, a, b]).splitlines()
    right = lines[0].index('Withdrawals') + len('Withdrawals')
    assert lines[1].index('1,234.56') + len('1,234.56') == right
    assert lines[2].index('9.99') + len('9.99') == right


def test_fragments_on_one_baseline_share_a_row_and_wrapped_text_does_not():
    rows = layout_page([frag('Jan 05', 40, 500), frag('E-TRANSFER SENT', 100, 500.3),
                        frag('700.00', 300, 499.8), frag('REF 7A2B', 100, 488)]).splitlines()
    assert len(rows) == 2
    assert rows[0].lstrip().startswith('Jan 05') and '700.00' in rows[0]
    assert rows[1].strip() == 'REF 7A2B'


def test_a_word_split_by_kerning_is_joined_and_words_get_one_space():
    items = [frag('BL', 100, 500), {'str': 'UE', 'x': 100 + 2 * CW + 0.4, 'y': 500, 'width': 2 * CW, 'height': 9.0},
             {'str': 'HERON', 'x': 100 + 4 * CW + 0.3 * CW + 2.5, 'y': 500, 'width': 5 * CW, 'height': 9.0}]
    assert layout_page(items).strip() == 'BLUE HERON'


def test_sideways_text_gets_a_row_of_its_own():
    items = [frag('Jan 05', 40, 500), frag('CORNER GROCER', 100, 500), frag('45.67', 300, 500),
             frag('000117', 20, 495, size=6.0, rot=1)]
    rows = [r for r in layout_page(items).splitlines() if r.strip()]
    assert len(rows) == 2
    assert any(r.strip() == '000117' for r in rows)
    assert any(r.lstrip().startswith('Jan 05') for r in rows)


def test_a_stack_of_sideways_fragments_is_one_row():
    # a margin carrying a form number, a date and dashes, printed upward as
    # several fragments: one row, in reading order, between the rows it
    # spans — not one row per fragment scattered among the transactions
    stack = [frag('2026', 20, 470, size=6.0, rot=1), frag('-', 20, 470 + 4 * CW + 1.0, size=6.0, rot=1),
             frag('0042', 20, 470 + 5 * CW + 2.0, size=6.0, rot=1)]
    for i in stack:
        i['width'] = len(i['str']) * 3.0
    items = [frag('Jan 05', 40, 500), frag('E-TRANSFER SENT', 100, 500), frag('700.00', 300, 500),
             frag('REF 7A2B', 100, 488), frag('Jan 06', 40, 476), frag('CORNER GROCER', 100, 476), frag('45.67', 300, 476)]
    rows = [r.strip() for r in layout_page(items + stack).splitlines() if r.strip()]
    assert rows.count('2026 - 0042') == 1
    assert rows.index('REF 7A2B') == rows.index('E-TRANSFER SENT') + 1 if 'E-TRANSFER SENT' in rows else True
    assert [r for r in rows if r.startswith('Jan 05')][0].endswith('700.00')
    assert rows[rows.index([r for r in rows if r.startswith('Jan 05')][0]) + 1] == 'REF 7A2B'


def test_a_vertical_gap_leaves_blank_lines_and_pages_end_with_a_form_feed():
    text = layout([[frag('a', 40, 700), frag('b', 40, 660)], [frag('c', 40, 700)]])
    pages = text.split('\f')
    assert len(pages) == 3 and pages[2] == ''
    lines = pages[0].split('\n')
    assert lines[0].strip() == 'a' and lines[-2].strip() == 'b'
    assert sum(1 for l in lines if l == '') >= 2    # 40 points at 9-point text: blank lines between


def test_empty_pages_and_pages_as_mappings():
    assert layout([[]]) == '\n\f'
    assert layout([{'items': [frag('x', 0, 0)]}]).startswith('x')


# ---------------------------------------------------------------- fixtures
@pytest.mark.parametrize('name', ['cibc-2026-01-31', 'ultimate-2026-01-31',
                                  'rbc-2026-03-31', 'scotialine-2026-04-30'])
def test_fixture_reconstructs_extracts_and_reconciles(name):
    pages = json.loads((FIXTURES / f'{name}.json').read_text())
    text = layout(pages)
    bank = pdf_import.detect_bank(name + '.pdf', text)
    assert bank is not None
    r = pdf_import.extract(text, bank, name + '.pdf')
    assert r['reconciled'], (r['why'], r['extracted'], r['stated'])
    assert pdf_import.rows_to_csv(r['rows']) == (FIXTURES / f'{name}.csv').read_text()


def test_convert_is_what_the_worker_calls():
    name = 'rbc-2026-03-31'
    out = json.loads(pdf_import.convert_json(name + '.pdf', (FIXTURES / f'{name}.json').read_text()))
    assert out['bank'] == 'RBC' and out['reconciled'] is True
    assert out['csv'] == (FIXTURES / f'{name}.csv').read_text()
    assert out['transactions'] == out['csv'].count('\n') - 1


def test_a_statement_whose_total_disagrees_is_refused():
    pages = json.loads((FIXTURES / 'scotialine-2026-04-30.json').read_text())
    for item in pages[0]:
        if item['str'] == '$9.84':        # the stated interest; the list still carries 9.84
            item['str'] = '$9.48'
    out = pdf_import.convert('scotialine-2026-04-30.pdf', pages)
    assert out['reconciled'] is False and out['csv'] == ''
    assert out['why'] == 'mismatch'
    assert out['stated'] != out['extracted']


def test_a_chequing_statement_is_refused_when_only_deposits_disagree():
    pages = json.loads((FIXTURES / 'rbc-2026-03-31.json').read_text())
    for item in pages[0]:
        if item['str'].startswith('+ $'):
            item['str'] = '+ $3,000.99'
    out = pdf_import.convert('rbc-2026-03-31.pdf', pages)
    assert out['reconciled'] is False and out['why'] == 'deposits mismatch'


def test_an_unknown_layout_names_the_banks_it_knows():
    pages = [[frag('Some Other Bank', 40, 700), frag('Jan 05  CORNER GROCER  45.67', 40, 680)]]
    out = pdf_import.convert('statement.pdf', pages)
    assert out['bank'] is None and out['csv'] == '' and out['why'] == 'unknown layout'
    assert set(out['banks']) == set(pdf_import.EXTRACTORS)


def test_the_bank_is_read_from_the_text_when_the_name_says_nothing():
    pages = json.loads((FIXTURES / 'ultimate-2026-01-31.json').read_text())
    assert pdf_import.detect_bank('statement.pdf', layout(pages)) == 'Ultimate'
    assert pdf_import.stmt_year('statement.pdf', layout(pages)) == 2026


def test_fixtures_are_generated_deterministically(tmp_path):
    # the generator writes beside itself; run a copy of it in a temporary
    # folder and compare with what is committed
    script = tmp_path / 'make_fixtures.py'
    script.write_text((FIXTURES / 'make_fixtures.py').read_text())
    subprocess.run([sys.executable, str(script)], check=True, capture_output=True)
    for f in FIXTURES.glob('*.json'):
        assert (tmp_path / f.name).read_text() == f.read_text(), f.name
    for f in FIXTURES.glob('*.csv'):
        assert (tmp_path / f.name).read_text() == f.read_text(), f.name
