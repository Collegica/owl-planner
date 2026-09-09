## Why

Some people will hand their AI a table rather than a list of names, and get back `ledger.csv` with `kind` and `line` filled in. Taking that file at face value would make a language model's output the source of truth — a shifted amount or a dropped row would land in the number unchecked. Taking it under the reconciliation rule makes it safe: labels are accepted only for rows that still match the original statements exactly.

## What Changes

- The engine SHALL accept an **annotated ledger** — a CSV with the `ledger.csv` header — among the statement files. For each annotated row whose date, description and amount match a transaction from the real statements, the row's `kind` and `line` are applied as if pinned. A row that matches nothing, a row whose amount differs, or a `line` not in `categories.yml` SHALL cause the whole annotated file to be refused, with the offending rows named.
- Annotated labels take precedence over patterns and sit just below the date-and-amount pins in the classification order; the ledger row records `rule: annotated`.
- An annotated file is never itself a source of transactions: it labels, it does not add.
- Non-goals: accepting arbitrary edited statement CSVs; annotated files without the originals.

Personal data: nothing new; the annotated file is the user's own ledger.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
- `money-classification`: an annotated ledger is a new, verified source of labels with a defined place in the precedence.
- `statement-import`: a file with the ledger header is recognised as annotations, not statements.

## Impact

`budget.py` (file recognition; a verification pass; one new precedence step), tests, `web/app.js` (mark an annotated file in the list), README.
