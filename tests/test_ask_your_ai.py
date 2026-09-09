"""The pack the tool writes for a person's own AI, and the merge of the answer
back into rules.yml. Invented rows only; the assertions read ask-your-ai.md,
ledger.csv and the text rules_merge returns.

    pixi run test
"""
from __future__ import annotations

import difflib
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import budget  # noqa: E402
import rules_merge  # noqa: E402
from test_precedence import eight_months, household, run  # noqa: E402


def pack_after(tmp_path, rows):
    text, ledger = run(household(tmp_path, rows))
    return text, ledger, (tmp_path / 'ask-your-ai.md').read_text()


def test_pack_carries_names_and_counts_but_no_money(tmp_path):
    rows = eight_months([('2026-03-03', 'NEWTOWN DENTAL 4471', -150.00),
                         ('2026-05-03', 'NEWTOWN DENTAL 4471', -150.00),
                         ('2026-07-03', 'NEWTOWN DENTAL 4471', -152.21),
                         ('2026-04-12', 'THE BOOK NOOK NEWTOWN', -12.00),
                         # names a loans.yml counterparty in its first words: a
                         # question for the person, so it stays out of the pack
                         ('2026-06-01', 'FRIEND A LUNCH MONEY', -100.00)])
    text, _, pack = pack_after(tmp_path, rows)
    assert 'newtown dental — 3 times, ~$200 each' in pack
    assert 'the book — 1 time, ~$10 each' in pack
    asked = pack.split('## Descriptions to classify')[1]
    assert asked.index('newtown dental') < asked.index('the book')   # ranked by money
    assert 'cover 82% of what was not classified' in asked            # 464.21 of 564.21
    assert '1 description(s) withheld' in pack
    assert 'friend a' not in pack.lower()
    assert '4471' not in pack and not re.search(r'\d{4}', pack)   # no card fragment, no year
    assert not re.search(r'\d+\.\d{2}', pack)                     # no amount
    assert not re.search(r'\d{4}-\d{2}-\d{2}', pack)              # no date
    assert '452' not in pack and '564' not in pack
    assert 'wrote ask-your-ai.md — 2 merchant(s)' in text


def test_pack_names_every_budget_line_and_permits_unsure(tmp_path):
    _, _, pack = pack_after(tmp_path, eight_months([('2026-03-03', 'NEWTOWN DENTAL', -150.00)]))
    for line in rules_merge.budget_lines():
        assert line in pack
    assert '`unsure:`' in pack and 'do not guess' in pack
    assert '```yaml' in pack and 'categories:' in pack and 'transfers:' in pack and 'income:' in pack


def test_pack_says_so_when_there_is_nothing_to_ask(tmp_path):
    text, _, pack = pack_after(tmp_path, eight_months())
    assert 'Nothing to ask: every transaction was classified.' in pack
    assert not re.search(r'^- .+ — \d+ time', pack, re.M)
    assert 'nothing to ask; everything was classified' in text


COMMENTED = """# my rules — every comment here is a reason
transfers:
  - 'payment.*thank you'   # the card, from chequing

categories:
  Groceries:
    - 'corner grocer'      # the one on the corner
  Rent: 'loyer'

# --- the rest ---
one_off: []
"""


def test_merge_appends_to_a_commented_file_without_removing_a_line():
    frag = "categories:\n  Groceries: ['newtown grocer']\n"
    assert rules_merge.preview(COMMENTED, frag) == [('categories', 'Groceries', 'newtown grocer')]
    merged = rules_merge.merge(COMMENTED, frag)
    diff = [l for l in difflib.unified_diff(COMMENTED.splitlines(), merged.splitlines(), lineterm='', n=0)
            if l[:1] in '+-' and l[:3] not in ('+++', '---')]
    assert diff == ["+    - 'newtown grocer'"]
    assert '# the one on the corner' in merged and '# my rules — every comment here is a reason' in merged
    # the second merge of the same answer adds nothing
    assert rules_merge.merge(merged, frag) == merged


def test_merge_into_a_flow_list_touches_only_that_line():
    src = (ROOT / 'rules.example.yml').read_text()
    merged = rules_merge.merge(src, "categories:\n  Dentist: ['newtown dental']\nincome: ['newtown council']\n")
    before, after = src.splitlines(), merged.splitlines()
    assert len(after) == len(before) + 1
    after.remove("  - 'newtown council'")   # the one added line; what is left pairs up
    changed = [(a, b) for a, b in zip(before, after) if a != b]
    assert len(changed) == 1 and changed[0][0].startswith('  Dentist:')
    assert changed[0][1] == changed[0][0][:-1] + ",'newtown dental']"
    assert yaml_lists(merged)['income'][-1] == 'newtown council'


def yaml_lists(text):
    import yaml
    return yaml.safe_load(text)


def test_merge_creates_a_missing_section_and_line_at_the_end():
    merged = rules_merge.merge("categories:\n  Rent: ['loyer']\n",
                               "categories: {Dentist: ['newtown dental']}\ntransfers: ['move to piggy bank']\n")
    assert merged == ("categories:\n  Rent: ['loyer']\n  Dentist: ['newtown dental']\n\n"
                      "transfers:\n  - 'move to piggy bank'\n")


@pytest.mark.parametrize('fragment, names', [
    ("categories:\n  Boats: ['harbour marina']\n", 'Boats'),
    ("categories: [1\n", 'not valid YAML'),
    ("level:\n  - match: 'x'\n", "'level' is not a section"),
    ("categories:\n  Groceries: ['(']\n", 'not a valid regular expression'),
    ("", 'empty'),
])
def test_merge_refuses_and_says_why(fragment, names):
    with pytest.raises(rules_merge.MergeError) as e:
        rules_merge.preview(COMMENTED, fragment)
    assert names in str(e.value)


def test_cli_merge_writes_the_personal_rules_and_reruns(tmp_path):
    rows = eight_months([('2026-03-03', 'NEWTOWN DENTAL', -150.00)])
    folder = household(tmp_path, rows)
    before = (folder / 'rules.yml').read_text()
    (folder / 'answer.yml').write_text("categories:\n  Dentist: ['newtown dental']\n")
    text, ledger = run(folder, '--merge', str(folder / 'answer.yml'))
    assert 'merged 1 rule(s) from answer.yml into rules.yml' in text
    after = (folder / 'rules.yml').read_text()
    assert after.startswith(before.rstrip('\n')[:40]) and "'newtown dental'" in after
    assert ledger[('2026-03-03', 'NEWTOWN DENTAL')]['line'] == 'Dentist'
    assert 'nothing to ask' in (folder / 'ask-your-ai.md').read_text().lower()

    # a refused fragment writes nothing
    (folder / 'bad.yml').write_text("categories:\n  Boats: ['harbour marina']\n")
    text = budget.run(['--dir', str(folder / 'statements'), '--config', str(folder),
                       '--out', str(folder / 'budget.md'), '--merge', str(folder / 'bad.yml')])
    assert "--merge: 'Boats' is not a budget line" in text
    assert (folder / 'rules.yml').read_text() == after
