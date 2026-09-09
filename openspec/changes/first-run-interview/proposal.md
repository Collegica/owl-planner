## Why

Nobody but the author will write `rules.yml` from a blank page. Today the first run on a fresh clone categorises roughly half of spending and hands back a CSV of unmatched descriptions; every decision that made the tool accurate on real accounts — which e-transfers are an obligation, which cheque was a loan, which fund purchase is savings — was reached by a person asking the right question. The tool's skill has to be asking well, not guessing well; this change makes the tool the one that asks.

## What Changes

- A first run (or any run with material unclassified money) produces a **question list** ranked by dollars, not a budget: "these N descriptions account for P% of unclassified money — what is each?"
- Each question offers the kinds of money movement as answers (spending line, transfer, income, lending, savings, pass-through, one-off, level) and the answer is written to the personal yml as a durable rule with the reason attached.
- Questions are grouped by description signature so one answer covers every recurrence.
- The budget is still produced on the same run; the questions come first and the budget carries a coverage warning until they are answered.
- Non-goals: no attempt to guess an answer; no machine learning; no change to how a classified transaction is treated.

Nothing personal enters the repository: answers are written only to the gitignored `rules.yml` / `loans.yml`, and the question list is printed, not written to a tracked file.

## Capabilities

### New Capabilities
- `first-run-interview`: producing a ranked question list from unclassified money and turning each answer into a rule in the personal configuration.

### Modified Capabilities
- `money-classification`: the "listed largest first" requirement becomes the interview's input; `uncategorised.csv` remains but is no longer the primary feedback loop.

## Impact

- `budget.py`: a new interview step between classification and reporting; a writer for the personal yml files that preserves comments and ordering.
- `rules.example.yml`: unchanged in structure; the interview writes the same sections.
- README and the website article: "triage `uncategorised.csv`" becomes "answer the questions".
- No new dependencies. PyYAML round-tripping loses comments, so the writer appends rather than rewrites.
