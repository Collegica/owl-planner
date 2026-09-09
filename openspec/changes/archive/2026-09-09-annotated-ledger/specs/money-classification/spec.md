## ADDED Requirements

### Requirement: Annotated labels are applied only to rows that still match
When an annotated ledger is present, each of its rows SHALL be matched to a statement transaction by date, description and amount; a matched row's `kind` and `line` SHALL be applied with `rule: annotated`, taking precedence over patterns and the bank fallback but not over date-and-amount pins. If any row fails to match, or names a `line` absent from `categories.yml`, or has a `kind` outside the known set, the annotated file SHALL be refused as a whole and the offending rows named.

#### Scenario: Labels applied
- **WHEN** an annotated row for `2026-06-03, THE BOOK NOOK NEWTOWN, -38.50` carries `spending` and `Newspapers, magazines, music`
- **THEN** that transaction lands on that line with rule `annotated`

#### Scenario: An amount was altered
- **WHEN** an annotated row's amount is `-3.85` for a transaction that was `-38.50`
- **THEN** the annotated file is refused, the row is named, and the run proceeds without it

#### Scenario: A pin still wins
- **WHEN** a transaction is both pinned under `dated` and labelled differently in the annotated file
- **THEN** the pin's line applies
