# How the Canadian planners on either side of `$X` would build OWL Planner

**Answered:** 2026-09-09, by Behzad Samadi with Claude
**Mined:** IDEA-0008 … IDEA-0020

The question this lens asks: *what do the open tools that sit just before and just after our
one number expect from it, and what have they learned that we have not?* Four repositories
were named as references. Two of them start where we stop — a household retirement planner
([halfguru/retire-eh](https://github.com/halfguru/retire-eh)) and a tax-and-drawdown toolkit
([616fun/retirement-planning-toolkit-canada](https://github.com/616fun/retirement-planning-toolkit-canada));
one covers the asset side we ignore
([toma-nator/FUNDerelele](https://github.com/toma-nator/FUNDerelele)); one is the opposite
architecture, a hosted platform fed by open banking
([vivekally/AI-Personal-Finance-Advisor](https://github.com/vivekally/AI-Personal-Finance-Advisor)).

## Which repos count

`python scripts/repo_health.py … --markdown`, 2026-09-09:

| repo | stars | owner | age | contrib/top | commits90d | last_release | licence | pypi30d | verdict |
|---|---|---|---|---|---|---|---|---|---|
| halfguru/retire-eh | 2 | use | 7mo | 2/85% | 21 | 2026-02-18 | MIT | - | FAIL stars,age,release,bus_factor |
| toma-nator/FUNDerelele | 0 | use | 3mo | 1/100% | 52 | 2026-06-08 | MIT | - | FAIL stars,age,bus_factor |
| 616fun/retirement-planning-toolkit-canada | 0 | use | 2mo | 1/100% | 18 | none | MIT | - | FAIL stars,age,release,bus_factor |
| vivekally/AI-Personal-Finance-Advisor | 0 | use | 3mo | 0/100% | 4 | none | none | - | FAIL stars,age,release,bus_factor,licence |

**None passes.** Under the repository-lens rule none of the four may be depended on or be the
sole evidence for an idea. So this is not a repository lens; it is a company-style audit — what
would these four *designs* keep, replace and never do — and the discipline applied is that
**every idea mined below carries a second piece of evidence from our own `data`, `review` or
`incident` record**, stated in the idea's prose. Where a repo's design is the only argument,
the idea is retired or the point is left in the blind-spot section as watched.

## What they would keep from what we have

- **Reconcile or refuse.** `pdf_import.py` compares every statement against its own printed
  totals and writes nothing for one that disagrees. None of the four has an equivalent — they
  take imports on trust — and the toolkit's "no personal data in any script" would recognise
  the reason ours exists.
- **The precedence order and the pins.** `budget.py`'s classification loop (pass-through pin →
  counterparty → dated → transfer → income → one-off pin → category → savings → bank fallback →
  review → uncategorised) is the same shape as Arrive Finance's rules engine: edge cases first,
  patterns after. They would keep it and test it (IDEA-0016).
- **Personal-over-example.** `cfg()` in `budget.py` loads `rules.yml` if present, else
  `rules.example.yml`; `.gitignore` keeps the personal three out. The toolkit does exactly this
  with one config file and would keep it — and move it further out (IDEA-0014).
- **The median of complete months, and irregular = large AND non-repeating.** Retire, Eh?'s
  "conservative assumptions" principle is this in a different domain. They would keep the
  method and print it (IDEA-0009, IDEA-0010).
- **Local, no network, no credentials.** Retire, Eh? states it as scope; FUNDerelele states it
  as a creed; the toolkit states it as structure. Ours is in `openspec/specs/privacy/spec.md`
  as a requirement with a scenario. Kept.

## What they would replace, and with what

- `uncategorised.csv` as the feedback loop → the tool asking (IDEA-0007, promoted). Arrive
  Finance's seven-step wizard is the same instinct applied to onboarding.
- Trust the headline → show the months behind it (IDEA-0009) and the knobs (IDEA-0010).
- A hand-written prompt after the run → a generated ratio profile (IDEA-0011).
- `.gitignore` as the whole privacy story → `$OWL_HOME` outside the tree (IDEA-0014).
- Forgetting the exports → a durable, re-importable ledger (IDEA-0015).
- A fresh clone that half-works → an invented household that fully works (IDEA-0008).
- One person's accounts → a household (IDEA-0012).
- `budget.md` alone → a workbook a planner can open (IDEA-0017); a footer that says what the
  figures are (IDEA-0018); a net-position line from balances we already parse (IDEA-0013).

## What they would never do

- **Connect to a bank.** Retire, Eh? lists bank integrations as out of scope; Arrive Finance
  builds on them. For a tool whose premise is *no credentials*, the aggregator path is retired
  with its reason on file (IDEA-0019) and watched, because the Consumer-Driven Banking Act's
  read-only phase will make it tempting.
- **Grow a tax engine.** The toolkit already is one, for all thirteen jurisdictions. OWL
  Planner hands off instead (IDEA-0011); the engine is retired (IDEA-0020).
- **Print a number without its derivation.** Retire, Eh?'s "the math is always visible" is the
  rule they would enforce on us first.

## The three things they would ship first

1. **The invented household** (IDEA-0008) — it is the demo, the fixture and the safe example
   at once, and every other idea becomes testable the day it exists.
2. **Show the arithmetic** (IDEA-0009) — cheapest change with the largest effect on trust.
3. **The ratio profile** (IDEA-0011) — the actual hand-off to the two planners on the far side
   of `$X`, and the thing the website article currently asks the reader to write by hand.

## What this lens does not see

- **Import quality.** None of the four reads bank statements; all take positions or manual
  entries. Everything about parsing, reconciliation and date inference is invisible here and is
  covered by the `incident` and `data` lenses (IDEA-0002 … IDEA-0005).
- **The other half of OWL.** Muscles, not money. No planner in this set touches it and neither
  does this repository yet; the capability catalogue does not even have a row for it, which is
  the correct finding for now.
- **Track record.** Every repo here fails the health rule, so this lens says what four thoughtful
  designs would do — not what has survived contact with users. A repository lens over the
  `personal-finance` and `budgeting` GitHub topics, filtered by the rule, is the lens that
  covers that, and is the next one to write.
