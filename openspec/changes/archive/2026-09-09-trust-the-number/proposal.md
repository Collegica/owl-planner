## Why

The page at collegica.org/owl/ means strangers now meet the number without the person who built the tool standing beside it. Three things the tool still does would mislead them: it prints an annual figure from seven weeks in the same form as one from eight months; it says nothing when only one account was exported and the card payments have nowhere to land; and it asserts the median without showing the months behind it. See IDEA-0005, IDEA-0006, IDEA-0009 — and IDEA-0016, because the classification order these depend on has been wrong twice and has no test.

## What Changes

- **Three states on the headline.** MEASURED (three or more complete months), ESTIMATE (one or two: a monthly figure, no annual one), UNKNOWN (no complete month: what can be said, and what to export). The PLANNING FIGURE and the annualised income appear only when MEASURED. `budget.md` carries the state in its header and labels its columns as a window and a per-month average, not a year.
- **A coverage warning before any figure** when card payments leave chequing and no card export shows them arriving.
- **The arithmetic shown.** The complete months and their totals with the median marked; the transfers behind a LEVELLED line; a transaction count on every SET ASIDE line; a "How the number was made" section in `budget.md`.
- **`ledger.csv`**: every transaction with the kind it was classified as, the budget line, and the rule that decided it. The seam the golden tests need, and the first step of IDEA-0001.
- **Golden tests** for classification precedence, the coverage guard and the three states, on invented CSVs, run by `pixi run test` and in `check-all`.
- Non-goals: the interview; provenance columns in `budget.md` (IDEA-0001 proper); any change to how a transaction is classified.

Personal data: the tests use invented rows written by the test itself; `ledger.csv` is written beside `budget.md` and ignored like it.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
- `budget-report`: the headline gains states and the arithmetic; set-aside lines carry counts; the ledger is a new output.
- `statement-import`: partial coverage is detected and reported before any figure.

## Impact

`budget.py` (report section and the classification loop, which now records a kind per transaction), `web/app.js` (colour the states; offer the ledger), `sample/expected.txt`, `tests/`, pixi (`pytest`, `test` task, `check-all`).
