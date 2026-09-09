## Context

Files are read by `read_csv`, which infers columns; the classification loop applies pins then patterns. See proposal.md.

## Goals / Non-Goals

**Goals:** verified labels, exact precedence, loud refusal.
**Non-Goals:** fuzzy matching; partial acceptance of a file with bad rows.

## Decisions

- **Recognise by exact header**, before column inference, so a ledger is never mistaken for a statement.
- **Match key** `(date, description exactly as written, amount to the cent)` — the same tuple dedupe already uses — against the de-duplicated transaction set. A row that matches more than one transaction (true duplicates) labels all of them.
- **All-or-nothing per file.** One bad row refuses the file; the message lists up to ten offenders. Partial acceptance would hide the very thing the rule exists to catch.
- **Precedence:** after `dated` / loan pins, before category patterns. `kind` values map onto the loop's branches (`transfer`, `income`, `savings`, `spending`, `lending`, `repayment`, `passthrough`); `spending` requires a `line`.

## Risks / Trade-offs

- [Descriptions differ by whitespace after a round trip through a spreadsheet] → match on the description with runs of whitespace collapsed; nothing looser.
