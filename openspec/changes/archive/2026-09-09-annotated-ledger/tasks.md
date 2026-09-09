## 1. Recognition and verification

- [x] 1.1 Detect the ledger header in `budget.py` before column inference; verify a ledger-only folder refuses with the message from the spec
- [x] 1.2 Verify rows against the transaction set (date, whitespace-collapsed description, amount) and against `categories.yml` and the kind set; refuse the file naming offenders; verify with tests for an altered amount, a missing row, an unknown line

## 2. Precedence

- [x] 2.1 Apply matched labels after pins and before patterns with `rule: annotated`; verify with tests that a pin still wins and that a labelled row lands on its line

## 3. Page and docs

- [x] 3.1 Mark an annotated file in the page's file list and surface the refusal message; verify in the browser with an edited sample ledger
- [x] 3.2 README paragraph; `check-all` green
