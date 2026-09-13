## 1. Question list

- [x] 1.1 Group unclassified spending by `signature()` with count, total and share of unclassified; verify on an invented four-file sample that the order is by total descending and the printed share matches
- [x] 1.2 ~~Add the trigger threshold~~ Decided against a threshold (see design.md); verified that a fully classified sample prints no questions
- [x] 1.3 Print the question list before the budget with the answer kinds listed once at the top; verify the output reads correctly with `--no-interview`

## 2. Answers to rules

- [x] 2.1 Write the append-only section writer for `rules.yml` and `loans.yml`; verify with a file containing comments that a diff after writing shows only the appended lines
- [x] 2.2 Map each answer kind to its section and entry shape (category line, transfers, income, savings line, level, one_off, passthrough, counterparty); verify each by answering once on the sample and re-running: the signature no longer appears as a question
- [x] 2.3 Record `note:` with the date and stated reason on every written entry; verify the note is present in the yml and absent from any tracked file (`git status --ignored`)
- [x] 2.4 Handle a missing section by creating it at the end of the file; verify against a `rules.yml` copied from the example with the `level` section deleted

## 3. Interview loop

- [x] 3.1 Prompt per question on stdin with "don't know" and "stop" available; verify skipping leaves the transactions unclassified and the budget is still written with an unchanged categorised percentage
- [x] 3.2 Add `--no-interview`; verify `pixi run budget -- --no-interview` prints questions and produces the budget without prompting

## 4. Docs and regression

- [x] 4.1 Update README step 3 (done) — the website article is left as published, by standing decision — and the website article's triage paragraph from "add a pattern to rules.yml" to "answer the questions"; verify both render and mention `--no-interview`
- [ ] 4.2 Re-run `pixi run budget` on the maintainer's real sample with all questions skipped and confirm RECURRING, categorised % and SET ASIDE totals are unchanged from before the change
