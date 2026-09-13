"""The first-run interview on invented rows: ranking, the printed list, each
kind of answer becoming a rule that survives a re-run, files left byte-for-
byte otherwise, and the two ways of not answering. Nothing here touches a
real statement.

    pixi run test
"""
from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import budget          # noqa: E402
import interview       # noqa: E402
import rules_merge     # noqa: E402

RULES = """# my rules
transfers:
  - 'payment.*(thank you|received)'   # the card
income:
  - 'payroll'
categories:
  Groceries: ['grocer']   # the usual
  Dentist: ['dentist']
"""
LOANS = """lent:
counterparties:
review: ['e-?transfer']
review_min: 500
disbursements:
receipts:
"""


def household(tmp_path: Path, rows):
    st = tmp_path / 'statements'; st.mkdir()
    with open(st / 'chequing.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['Date', 'Description', 'Amount'])
        for d, desc, amt in rows: w.writerow([d, desc, f'{amt:.2f}'])
    (tmp_path / 'rules.yml').write_text(RULES)
    (tmp_path / 'loans.yml').write_text(LOANS)
    return tmp_path


def base_rows():
    rows = []
    for m in range(1, 9):   # eight complete months of ordinary life
        rows += [(f'2026-{m:02d}-02', 'PAYROLL DEP', 4000.00),
                 (f'2026-{m:02d}-05', 'NEWTOWN GROCER #12', -300.00),
                 (f'2026-{m:02d}-09', 'SQ *CAFE 4471', -30.00),
                 (f'2026-{m:02d}-15', 'TFR TO 4412', -500.00)]
    rows.append(('2026-09-30', 'NEWTOWN GROCER #12', -1.00))   # extends the window; classified
    return rows


def run(folder, *extra, tty=False, answers=(), monkeypatch=None):
    if monkeypatch is not None:
        monkeypatch.setattr(sys.stdin, 'isatty', lambda: tty)
        it = iter(answers)
        monkeypatch.setattr('builtins.input', lambda prompt='': next(it, ''))
    return budget.run(['--dir', str(folder / 'statements'), '--config', str(folder),
                       '--out', str(folder / 'budget.md'), *extra])


def ledger(folder):
    with open(folder / 'ledger.csv') as fh:
        return {(r['date'], r['description']): r for r in csv.DictReader(fh)}


# ---- ranking and the printed list ------------------------------------------

def test_questions_are_ranked_by_money_one_per_signature():
    unc = [(date(2026, m, 5), 'SQ *CAFE 4471', 30.0, 'c') for m in range(1, 6)] + \
          [(date(2026, 3, 1), 'TFR TO 4412', 500.0, 'c'), (date(2026, 4, 2), 'PARKING LOT 7', 12.0, 'c')]
    sig = lambda d: ' '.join(__import__('re').sub(r'[^a-z ]', ' ', __import__('re').sub(r'[#\d]{3,}', '', d.lower())).split()[:2])
    qs = interview.questions(unc, sig)
    assert [q.signature for q in qs] == ['tfr to', 'sq cafe', 'parking lot']
    assert (qs[1].count, qs[1].total) == (5, 150.0)
    text = '\n'.join(interview.render(qs))
    assert 'QUESTIONS' in text and '3 descriptions account for 100%' in text
    assert '1. tfr to — 1 transaction, $500' in text
    assert '2. sq cafe — 5 transactions, $150 (~$30 each)' in text


def test_no_terminal_prints_the_questions_and_still_writes_the_budget(tmp_path, monkeypatch):
    folder = household(tmp_path, base_rows())
    text = run(folder, monkeypatch=monkeypatch, tty=False)
    assert 'QUESTIONS' in text and 'tfr to' in text and 'sq cafe' in text
    assert 'RECURRING' in text and (folder / 'budget.md').exists()
    assert (folder / 'rules.yml').read_text() == RULES           # nothing written
    assert 'categorised 36% of spending' in text                  # 300 of 830 a month is known


def test_no_interview_flag_on_a_terminal_does_not_prompt(tmp_path, monkeypatch):
    folder = household(tmp_path, base_rows())
    text = run(folder, '--no-interview', monkeypatch=monkeypatch, tty=True, answers=['1'])
    assert 'QUESTIONS' in text and 'Answer each' not in text
    assert (folder / 'rules.yml').read_text() == RULES


# ---- answers become rules, and the run repeats -----------------------------

def test_a_budget_line_answer_is_appended_with_a_note_and_reruns(tmp_path, monkeypatch):
    folder = household(tmp_path, base_rows())
    lines = rules_merge.budget_lines()
    n = lines.index('Restaurants') + 1
    # question 1 is tfr to (500/month): transfer. question 2 is sq cafe: Restaurants, with a reason.
    text = run(folder, monkeypatch=monkeypatch, tty=True,
               answers=['t', 'the card payment', str(n), 'coffee'])
    after = (folder / 'rules.yml').read_text()
    assert after.startswith('# my rules')                                   # comment kept
    assert "  Groceries: ['grocer']   # the usual" in after                  # untouched line
    assert "Restaurants: ['sq\\W+cafe']  # " in after and 'interview: coffee' in after   # 'sq cafe' would miss 'SQ *CAFE'
    assert "  - 'tfr to'  # " in after and 'interview: the card payment' in after
    assert '2 answer(s) recorded' in text and text.count('RECURRING') == 1  # report printed once, after the rerun
    lg = ledger(folder)
    assert lg[('2026-03-09', 'SQ *CAFE 4471')]['line'] == 'Restaurants'
    assert lg[('2026-03-15', 'TFR TO 4412')]['kind'] == 'transfer'
    assert 'categorised 100% of spending' in text
    # a second run asks nothing
    again = run(folder, monkeypatch=monkeypatch, tty=True, answers=['q'])
    assert 'QUESTIONS' not in again


def test_dont_know_leaves_it_unclassified_and_q_stops(tmp_path, monkeypatch):
    folder = household(tmp_path, base_rows())
    text = run(folder, monkeypatch=monkeypatch, tty=True, answers=['', 'q'])
    assert (folder / 'rules.yml').read_text() == RULES
    assert 'categorised 36% of spending' in text and 'answer(s) recorded' not in text


def test_one_off_and_passthrough_pin_every_transaction(tmp_path, monkeypatch):
    rows = base_rows() + [('2026-05-20', 'MAIN STREET AUTO', -3800.00), ('2026-06-01', 'REBATE IN', 250.00),
                          ('2026-06-01', 'REBATE OUT', -250.00)]
    folder = household(tmp_path, rows)
    # questions: main street auto (3800), tfr to (4000 over 8 — larger), ... order by total: tfr to 4000, main street 3800, sq cafe 240, rebate out 250
    text = run(folder, monkeypatch=monkeypatch, tty=True, answers=['', 'o', 'a repair', 'p', 'the rebate', 'q'])
    after = (folder / 'rules.yml').read_text()
    assert 'one_off:' in after and 'date: 2026-05-20' in after and 'amount: 3800.00' in after
    assert "note: 'a repair'  # 2026-" in after
    assert 'passthrough:' in after and 'amount: 250.00' in after
    assert 'ONE-OFF' in text and 'MAIN STREET AUTO' in text
    lg = ledger(folder)
    assert lg[('2026-06-01', 'REBATE OUT')]['kind'] == 'passthrough'


def test_lending_writes_loans_yml_and_the_transactions_leave_spending(tmp_path, monkeypatch):
    rows = base_rows() + [('2026-02-14', 'CHEQUE 0042', -3000.00)]   # not an e-transfer: those go to review first
    folder = household(tmp_path, rows)
    # order: tfr to 4000, cheque 3000, sq cafe 240
    text = run(folder, monkeypatch=monkeypatch, tty=True, answers=['', 'l', 'Friend A', 'a loan', 'q'])
    loans = (folder / 'loans.yml').read_text()
    assert "to: 'Friend A'" in loans and 'amount: 3000.00' in loans and 'principal: 3000.00' in loans
    assert loans.startswith('lent:')                                       # file kept, sections filled
    assert ledger(folder)[('2026-02-14', 'CHEQUE 0042')]['kind'] == 'lending'
    assert 'LENDING' in text


def test_level_appends_a_match_and_note(tmp_path, monkeypatch):
    rows = base_rows() + [(f'2026-{m:02d}-28', 'WITHDRAWAL INTERAC', -950.00) for m in range(1, 9)]
    folder = household(tmp_path, rows)
    text = run(folder, monkeypatch=monkeypatch, tty=True, answers=['v', 'support, paid month-end', 'q'])
    after = (folder / 'rules.yml').read_text()
    assert 'level:' in after and "match: 'withdrawal interac'" in after
    assert "note: 'support, paid month-end'  # 2026-" in after
    assert 'LEVELLED' in text


def test_an_unknown_line_is_refused_and_nothing_is_written():
    q = interview.Question('sq cafe', 1, 30.0, [(date(2026, 1, 9), 'SQ *CAFE', 30.0)])
    with pytest.raises(rules_merge.MergeError):
        interview.write([(q, interview.Answer('line', line='Boats'))], RULES, LOANS)


def test_write_is_byte_for_byte_elsewhere():
    q = interview.Question('sq cafe', 1, 30.0, [(date(2026, 1, 9), 'SQ CAFE', 30.0)])
    rules, loans, summary = interview.write([(q, interview.Answer('line', line='Restaurants', reason='coffee'))],
                                            RULES, LOANS, today=date(2026, 9, 13))
    assert loans == LOANS
    added = [l for l in rules.splitlines() if l not in RULES.splitlines()]
    assert added == ["  Restaurants: ['sq cafe']  # 2026-09-13 interview: coffee"]   # plain: 'SQ *CAFE' is not among these txns
    assert summary == ['sq cafe → Restaurants']
