## Why

A fresh clone had nothing to run on and nothing to test against: the example rules categorised about half of whatever a stranger dropped in, and no change to the engine could be checked without a real person's statements. The web build (owl-web) needs something to ship with and a fixture for its parity test. See IDEA-0008.

## What Changes

- `sample/statements/` — four invented accounts over eight months of 2026, written by `scripts/make_sample.py` deterministically, in three CSV dialects (ISO/signed, `;` day-first debit/credit with comma decimals, month-first with a bank category column) so the importer's inference is exercised.
- `sample/rules.yml`, `sample/loans.yml`, `sample/known-annual.yml` — the household's configuration, using every section: transfers, income, categories, level, passthrough, dated, one_off, a loan with a partial repayment, two known yearly items.
- `sample/expected.txt` — the console output, checked by `pixi run sample-check` in CI.
- `budget.py --config <dir>` so a configuration can live anywhere, and `run(argv) -> str` returning the report as text; both are also what the browser build needs.
- Non-goals: PDF samples; a second household.

The sample is the only data the repository will ever contain, and every name, date and amount in it is invented.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
- `statement-import`: the tool ships with a runnable sample; `--config` lets the personal files live outside the tool's directory.

## Impact

`budget.py` (two small additions), `scripts/make_sample.py`, `sample/`, three pixi tasks, `check-all` gains `sample-check`.
