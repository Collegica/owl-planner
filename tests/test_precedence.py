"""Golden tests on invented rows: what kind each transaction lands in, the
coverage guard, and the three states. Every assertion reads ledger.csv or the
console text that budget.run() returns; nothing here touches a real statement.

    pixi run test
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import budget  # noqa: E402

RULES = """
transfers:
  - 'payment.*(thank you|received)'
  - 'transfer to\\s+credit\\s*card'
income:
  - 'payroll'
categories:
  Groceries: ['grocer']
  Child support: ['withdrawal.*interac']
  Gifts: ['florist']
  Registered investments: ['rrsp contribution']
passthrough:
  - date: 2026-03-15
    amount: 250
  - date: 2026-03-15
    amount: 250
"""
LOANS = """
lent:
  - to: Friend A
    principal: 3000
    repaid: 0
review: ['e-?transfer']
review_min: 500
disbursements:
  - date: 2026-02-14
    amount: 3000
    to: Friend A
"""


def household(tmp_path: Path, rows: list[tuple[str, str, float]], chequing_only=False):
    """Write one invented chequing export (and, unless chequing_only, the card it
    pays) plus a configuration, and return the folder."""
    st = tmp_path / 'statements'; st.mkdir()
    with open(st / 'chequing.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['Date', 'Description', 'Amount'])
        for d, desc, amt in rows: w.writerow([d, desc, f'{amt:.2f}'])
    if not chequing_only:
        with open(st / 'card.csv', 'w', newline='') as fh:
            w = csv.writer(fh); w.writerow(['Date', 'Description', 'Amount'])
            for d, desc, amt in rows:
                if 'TRANSFER TO CREDIT CARD' in desc:
                    w.writerow([d, 'PAYMENT - THANK YOU', -amt])
                    w.writerow([d, 'CORNER GROCER', amt * 0.9])
    (tmp_path / 'rules.yml').write_text(RULES)
    (tmp_path / 'loans.yml').write_text(LOANS)
    return tmp_path


def run(folder: Path, *extra: str):
    text = budget.run(['--dir', str(folder / 'statements'), '--config', str(folder),
                       '--out', str(folder / 'budget.md'), *extra])
    ledger = {}
    with open(folder / 'ledger.csv') as fh:
        for r in csv.DictReader(fh):
            ledger[(r['date'], r['description'])] = r
    return text, ledger


# eight complete months of the same invented life, so the state is MEASURED
def eight_months(extra: list[tuple[str, str, float]] = ()):
    rows = []
    for m in range(1, 9):
        rows += [(f'2026-{m:02d}-01', 'PAYROLL DEPOSIT ACME', 4000.00),
                 (f'2026-{m:02d}-05', 'CORNER GROCER', -320.00),
                 (f'2026-{m:02d}-08', 'RRSP CONTRIBUTION', -400.00),
                 (f'2026-{m:02d}-20', 'MB-TRANSFER TO CREDIT CARD 4512', -900.00),
                 (f'2026-{m:02d}-28', 'WITHDRAWAL FREE INTERAC E-TRANSFER', -700.00)]
    rows.append(('2026-08-31', 'CORNER GROCER', -10.00))   # closes August
    return rows + list(extra)


def test_pinned_loan_beats_the_support_pattern(tmp_path):
    # a chequing Interac withdrawal matches the Child support pattern, but this
    # one is pinned as a loan disbursement: the pin wins
    rows = eight_months([('2026-02-14', 'WITHDRAWAL FREE INTERAC E-TRANSFER', -3000.00)])
    _, ledger = run(household(tmp_path, rows))
    pinned = ledger[('2026-02-14', 'WITHDRAWAL FREE INTERAC E-TRANSFER')]
    assert (pinned['kind'], pinned['rule']) == ('lending', 'pin')
    ordinary = ledger[('2026-02-28', 'WITHDRAWAL FREE INTERAC E-TRANSFER')]
    assert (ordinary['kind'], ordinary['line']) == ('spending', 'Child support')


def test_review_is_the_last_resort(tmp_path):
    # an e-transfer above review_min that matches a category is categorised,
    # not sent for review; one that matches nothing is
    rows = eight_months([('2026-03-03', 'E-TRANSFER SENT FLORIST', -800.00),
                         ('2026-03-04', 'E-TRANSFER SENT', -800.00)])
    _, ledger = run(household(tmp_path, rows))
    assert ledger[('2026-03-03', 'E-TRANSFER SENT FLORIST')]['line'] == 'Gifts'
    assert ledger[('2026-03-04', 'E-TRANSFER SENT')]['kind'] == 'review'


def test_savings_and_transfers_and_income_are_not_spending(tmp_path):
    text, ledger = run(household(tmp_path, eight_months()))
    assert ledger[('2026-01-08', 'RRSP CONTRIBUTION')]['kind'] == 'savings'
    assert ledger[('2026-01-20', 'MB-TRANSFER TO CREDIT CARD 4512')]['kind'] == 'transfer'
    assert ledger[('2026-01-01', 'PAYROLL DEPOSIT ACME')]['kind'] == 'income'
    assert ledger[('2026-01-05', 'CORNER GROCER')]['kind'] == 'spending'
    assert 'SAVINGS     $400/month' in text


def test_passthrough_cancels_on_both_legs(tmp_path):
    rows = eight_months([('2026-03-15', 'CASHBACK REWARD', 250.00),
                         ('2026-03-15', 'E-TRANSFER SENT', -250.00)])
    text, ledger = run(household(tmp_path, rows))
    assert ledger[('2026-03-15', 'CASHBACK REWARD')]['kind'] == 'passthrough'
    assert ledger[('2026-03-15', 'E-TRANSFER SENT')]['kind'] == 'passthrough'
    assert 'pass-throughs (in and straight out)    $       500' in text


def test_coverage_warning_when_the_card_is_missing(tmp_path):
    text, _ = run(household(tmp_path, eight_months(), chequing_only=True))
    assert text.lstrip().startswith('COVERAGE'), text[:200]
    assert "A card's export is missing" in text


def test_no_coverage_warning_when_both_sides_are_present(tmp_path):
    text, _ = run(household(tmp_path, eight_months()))
    assert 'COVERAGE' not in text


def test_measured_state_prints_an_annual_figure(tmp_path):
    text, _ = run(household(tmp_path, eight_months()))
    assert 'MEASURED over 8 complete months' in text
    assert '/year' in text and 'PLANNING FIGURE  $' in text
    assert '(* the median' in text


def test_estimate_state_refuses_an_annual_figure(tmp_path):
    # seven weeks: one complete month
    rows = [r for r in eight_months() if '2026-01-15' <= r[0] <= '2026-03-07']
    text, _ = run(household(tmp_path, rows))
    assert 'ESTIMATE — 1 complete month(s)' in text
    assert '/year' not in text
    assert 'PLANNING FIGURE  not yet' in text
    assert '**ESTIMATE**' in (tmp_path / 'budget.md').read_text()


def test_unknown_state_when_no_month_is_complete(tmp_path):
    rows = [r for r in eight_months() if '2026-01-03' <= r[0] <= '2026-02-10']
    text, _ = run(household(tmp_path, rows))
    assert 'RECURRING   UNKNOWN' in text
    assert '/month' not in text.split('RECURRING')[1].split('\n')[0]
    assert 'no complete month observed' in text


def test_ledger_covers_every_transaction(tmp_path):
    rows = eight_months()
    _, ledger = run(household(tmp_path, rows))
    assert len(ledger) >= len(rows)
    kinds = {r['kind'] for r in ledger.values()}
    assert kinds <= {'passthrough', 'lending', 'repayment', 'transfer', 'income', 'refund',
                     'savings', 'spending', 'review', 'uncategorised'}


# ---- an annotated ledger: verified labels, all or nothing per file ----------
LEDGER_HEADER = ['date', 'description', 'amount', 'kind', 'line', 'rule']


def annotate(folder: Path, rows: list[tuple], name='annotated.csv'):
    """Write an annotated ledger beside the statements: rows are (date,
    description, signed amount as the bank shows it, kind, line)."""
    with open(folder / 'statements' / name, 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(LEDGER_HEADER)
        for d, desc, amt, kind, line in rows: w.writerow([d, desc, amt, kind, line, ''])
    return folder


BOOK = ('2026-06-03', 'THE BOOK NOOK NEWTOWN', -38.50)   # matches no pattern in RULES


def test_annotated_label_lands_on_its_line(tmp_path):
    # the row is labelled with a line no pattern would give it; the ledger
    # records the label and the rule that applied it, and the file is reported
    # with the number of rows applied — a row left 'uncategorised' carries no
    # label and is classified as before, and whitespace inside a description
    # does not break the match
    folder = household(tmp_path, eight_months([BOOK]))
    annotate(folder, [('2026-06-03', 'THE  BOOK   NOOK NEWTOWN', '-38.50', 'spending', 'Newspapers, magazines, music'),
                      ('2026-01-05', 'CORNER GROCER', '-320.00', 'uncategorised', '')])
    text, ledger = run(folder)
    row = ledger[('2026-06-03', 'THE BOOK NOOK NEWTOWN')]
    assert (row['kind'], row['line'], row['rule']) == ('spending', 'Newspapers, magazines, music', 'annotated')
    assert ledger[('2026-01-05', 'CORNER GROCER')]['line'] == 'Groceries'
    assert 'annotated   annotated.csv — 1 row applied' in text
    assert 'refused' not in text


def test_annotated_label_beats_a_pattern(tmp_path):
    folder = household(tmp_path, eight_months([('2026-06-09', 'CORNER GROCER', -50.00)]))
    annotate(folder, [('2026-06-09', 'CORNER GROCER', '-50.00', 'spending', 'Gifts')])
    _, ledger = run(folder)
    assert (ledger[('2026-06-09', 'CORNER GROCER')]['line'], ledger[('2026-06-09', 'CORNER GROCER')]['rule']) == ('Gifts', 'annotated')
    assert ledger[('2026-06-05', 'CORNER GROCER')]['line'] == 'Groceries'   # the pattern still holds elsewhere


def test_a_dated_pin_still_beats_an_annotated_label(tmp_path):
    folder = household(tmp_path, eight_months([BOOK]))
    (folder / 'rules.yml').write_text(RULES + "dated:\n  - date: 2026-06-03\n    amount: 38.50\n    line: Gifts\n")
    annotate(folder, [('2026-06-03', 'THE BOOK NOOK NEWTOWN', '-38.50', 'spending', 'Groceries')])
    text, ledger = run(folder)
    row = ledger[('2026-06-03', 'THE BOOK NOOK NEWTOWN')]
    assert (row['line'], row['rule']) == ('Gifts', 'dated pin')
    assert 'annotated.csv — 0 rows applied' in text   # accepted, but the pin took the row


def test_an_altered_amount_refuses_the_whole_file(tmp_path):
    # one shifted decimal point refuses the file and names the row; the other,
    # correct row in the same file is not applied either, and the run goes on
    folder = household(tmp_path, eight_months([BOOK, ('2026-06-09', 'CORNER GROCER', -50.00)]))
    annotate(folder, [('2026-06-03', 'THE BOOK NOOK NEWTOWN', '-3.85', 'spending', 'Newspapers, magazines, music'),
                      ('2026-06-09', 'CORNER GROCER', '-50.00', 'spending', 'Gifts')])
    text, ledger = run(folder)
    assert '! annotated.csv: refused — 1 of 2 rows' in text
    assert "2026-06-03  THE BOOK NOOK NEWTOWN  -3.85  — amount differs from the statement's -38.50" in text
    assert ledger[('2026-06-03', 'THE BOOK NOOK NEWTOWN')]['kind'] == 'uncategorised'
    assert ledger[('2026-06-09', 'CORNER GROCER')]['line'] == 'Groceries'
    assert 'RECURRING' in text and 'annotated   annotated.csv' not in text


def test_a_row_that_matches_nothing_refuses_the_file(tmp_path):
    folder = household(tmp_path, eight_months([BOOK]))
    annotate(folder, [('2026-06-04', 'THE BOOK NOOK NEWTOWN', '-38.50', 'spending', 'Newspapers, magazines, music')])
    text, ledger = run(folder)
    assert 'refused — 1 of 1 rows' in text and 'no matching transaction in the statements' in text
    assert ledger[('2026-06-03', 'THE BOOK NOOK NEWTOWN')]['kind'] == 'uncategorised'


def test_an_unknown_line_or_kind_refuses_the_file(tmp_path):
    folder = household(tmp_path, eight_months([BOOK, ('2026-06-09', 'CORNER GROCER', -50.00)]))
    annotate(folder, [('2026-06-03', 'THE BOOK NOOK NEWTOWN', '-38.50', 'spending', 'Books'),
                      ('2026-06-09', 'CORNER GROCER', '-50.00', 'gift', '')])
    text, ledger = run(folder)
    assert 'refused — 2 of 2 rows' in text
    assert "line 'Books' is not in categories.yml" in text
    assert "kind 'gift' is not one of" in text
    assert ledger[('2026-06-03', 'THE BOOK NOOK NEWTOWN')]['kind'] == 'uncategorised'


def test_at_most_ten_offenders_are_named(tmp_path):
    folder = household(tmp_path, eight_months())
    annotate(folder, [(f'2026-06-{d:02d}', 'NOWHERE SHOP', '-1.00', 'spending', 'Gifts') for d in range(1, 14)])
    text, _ = run(folder)
    assert 'refused — 13 of 13 rows' in text and 'and 3 more' in text
    assert text.count('NOWHERE SHOP') == 10


def test_a_ledger_is_annotations_not_a_statement(tmp_path):
    # the same row count with and without the annotated file: it added nothing
    rows = eight_months([BOOK])
    for sub in ('a', 'b'): (tmp_path / sub).mkdir()
    plain, _ = run(household(tmp_path / 'a', rows))
    folder = annotate(household(tmp_path / 'b', rows),
                      [('2026-06-03', 'THE BOOK NOOK NEWTOWN', '-38.50', 'spending', 'Gifts')])
    text, _ = run(folder)
    files_line = lambda t: next(l for l in t.splitlines() if l.startswith('  files '))
    assert files_line(text) == files_line(plain)
    assert files_line(text).startswith('  files 2 ')


def test_a_ledger_alone_is_refused(tmp_path):
    folder = household(tmp_path, eight_months())
    for f in (folder / 'statements').glob('*.csv'): f.unlink()
    annotate(folder, [('2026-06-03', 'THE BOOK NOOK NEWTOWN', '-38.50', 'spending', 'Gifts')])
    text = budget.run(['--dir', str(folder / 'statements'), '--config', str(folder), '--out', str(folder / 'budget.md')])
    assert 'Annotations need the original exports' in text
    assert not (folder / 'ledger.csv').exists()


def test_the_tools_own_ledger_round_trips(tmp_path):
    # ledger.csv handed straight back is accepted whole, and every kind is the
    # same as before: the labels only restate what the rules decided
    rows = eight_months([BOOK, ('2026-02-14', 'WITHDRAWAL FREE INTERAC E-TRANSFER', -3000.00),
                         ('2026-03-15', 'CASHBACK REWARD', 250.00), ('2026-03-15', 'E-TRANSFER SENT', -250.00)])
    folder = household(tmp_path, rows)
    _, before = run(folder)
    (folder / 'ledger.csv').rename(folder / 'statements' / 'annotated.csv')
    text, after = run(folder)
    assert 'refused' not in text and 'annotated   annotated.csv — ' in text
    assert {k: (r['kind'], r['line']) for k, r in before.items()} == {k: (r['kind'], r['line']) for k, r in after.items()}
    assert after[('2026-02-14', 'WITHDRAWAL FREE INTERAC E-TRANSFER')]['rule'] == 'pin'   # the loan pin still wins
    assert after[('2026-01-01', 'PAYROLL DEPOSIT ACME')]['rule'] == 'annotated'
