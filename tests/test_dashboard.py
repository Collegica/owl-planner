"""dashboard.html on invented rows: the four first-screen figures, the
coverage arithmetic, the months drawn, no identifier, no external
reference, and the same bytes twice. Nothing here touches a real statement.

    pixi run test
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import budget      # noqa: E402
import dashboard   # noqa: E402

RULES = """transfers:
  - 'transfer to\\s+credit\\s*card'
income:
  - 'payroll'
categories:
  Groceries: ['grocer']
  Registered investments: ['rrsp contribution']
"""


def household(tmp_path: Path, rows, months=8):
    st = tmp_path / 'statements'; st.mkdir()
    with open(st / 'chequing.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['Date', 'Description', 'Amount'])
        for d, desc, amt in rows: w.writerow([d, desc, f'{amt:.2f}'])
    (tmp_path / 'rules.yml').write_text(RULES)
    return tmp_path


def rows_for(months):
    rows = []
    for m in range(1, months + 1):
        rows += [(f'2026-{m:02d}-01', 'PAYROLL DEP', 4000.00),          # the 1st, so the month is complete
                 (f'2026-{m:02d}-05', 'NEWTOWN GROCER #12', -300.00),
                 (f'2026-{m:02d}-07', 'RRSP CONTRIBUTION', -200.00),
                 (f'2026-{m:02d}-15', 'TRANSFER TO CREDIT CARD', -500.00),
                 (f'2026-{m:02d}-20', 'NEWTOWN DENTAL', -100.00)]     # unclassified
    rows.append((f'2026-{months + 1:02d}-15', 'NEWTOWN GROCER #12', -1.00))   # a partial month: excluded
    return rows


def run(folder):
    text = budget.run(['--dir', str(folder / 'statements'), '--config', str(folder),
                       '--out', str(folder / 'budget.md')])
    return text, (folder / 'dashboard.html').read_text()


def test_coverage_step_counts_answers_to_the_goal():
    # 87% known; questions worth 9% and 4% of spending → 2 answers reach 100%
    assert dashboard.coverage_step(87, 1000, [50, 80]) == (2, 100.0)
    # one answer is enough when it crosses the goal
    assert dashboard.coverage_step(87, 1000, [90, 40], goal=95) == (1, 96.0)
    assert dashboard.coverage_step(90, 1000, [60, 40]) == (1, 96.0)
    # every answer still short: all of them, and where that lands
    n, after = dashboard.coverage_step(50, 1000, [100, 100])
    assert n == 2 and after == 70.0
    assert dashboard.coverage_step(100, 1000, []) is None


def test_measured_window_shows_the_four_figures(tmp_path):
    folder = household(tmp_path, rows_for(8))
    text, html = run(folder)
    assert 'wrote dashboard.html' in text
    assert 'class="state MEASURED"' in html and '>MEASURED<' in html
    # 300 grocer + 100 dental a month is spending; 75% known
    assert '75%<small> of spending rests on a rule' in html
    assert 'Answer the next 1 question' in html and 'coverage reaches 100%' in html
    assert '$400<small>/month' in html and '$4,800<small>/year' in html          # median and 12×
    assert 'Transfers between your own accounts' in html and '$4,000' in html    # 8 × 500
    assert 'Savings' in html and '$1,600' in html                                # 8 × 200
    assert 'Income' in html and '$32,000' in html                                # 8 × 4000
    assert html.count('<rect class="bar') == 8 and 'median $400' in html


def test_estimate_window_withholds_the_annual_figure(tmp_path):
    folder = household(tmp_path, rows_for(2))
    text, html = run(folder)
    assert 'class="state ESTIMATE"' in html
    assert 'Not printed: 1 more complete month needed' in html
    assert '/year' not in html


def test_no_identifier_no_external_reference_and_deterministic(tmp_path):
    folder = household(tmp_path, rows_for(8))
    _, html = run(folder)
    for desc in ('NEWTOWN DENTAL', 'NEWTOWN GROCER', 'PAYROLL', 'RRSP CONTRIBUTION', 'newtown'):
        assert desc not in html
    assert not re.search(r'https?:', html)
    assert '<script' not in html
    _, again = run(folder)
    assert again == html


def test_everything_classified_says_so(tmp_path):
    rows = [r for r in rows_for(8) if 'DENTAL' not in r[1]]
    folder = household(tmp_path, rows)
    _, html = run(folder)
    assert '100%<small> of spending rests on a rule' in html
    assert 'Every transaction is classified' in html and 'Answer the next' not in html
