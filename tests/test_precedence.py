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
