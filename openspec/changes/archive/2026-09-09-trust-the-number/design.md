## Context

The classification loop in `budget.py` decides a kind per transaction but keeps only totals; the report section prints from those totals. See proposal.md.

## Goals / Non-Goals

**Goals:** states, coverage, arithmetic, ledger, tests — with no change to what any transaction is classified as.
**Non-Goals:** provenance in `budget.md`; interview; structured output for the page beyond colouring.

## Decisions

- **Record the kind in the loop, print from the record.** Each branch of the loop appends `(date, desc, amount, kind, line, rule)` to a ledger list; counts for SET ASIDE and the ledger file both come from it. Alternative: separate counters per branch — more state, no test seam.
- **Coverage by amounts, not by file names.** Card-payment outflows (descriptions naming a card) versus card-payment inflows (`payment … thank you/received`); a ratio under one half warns. Robust to any number of cards and to a card exported for a shorter window; file names mean nothing across banks.
- **State from complete months only**, the count the baseline already uses. Three is the threshold the recurring test already applies to signatures.
- **`budget.md` columns renamed** to "In window" and "Per month" — the old "Year" header was the extrapolation the states exist to prevent.
- **Tests read the ledger**, not the console: assertions on kinds are exact and do not break when wording changes.

## Risks / Trade-offs

- [Coverage heuristic misses a card paid from a line of credit] → the warning is a floor, not a proof; the README still says to export every account.
- [Console grows longer] → the arithmetic lines are compact (one line of months) and the ledger goes to a file.
