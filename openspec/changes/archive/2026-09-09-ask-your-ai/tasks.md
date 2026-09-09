## 1. The pack

- [x] 1.1 Write `ask-your-ai.md` beside `budget.md`: header stating what it contains, prompt, budget lines from `categories.yml`, rule format, ranked signatures with count and size band; verify `pixi run sample` writes it with the two unclassified signatures and no digit sequence of four or more anywhere in it
- [x] 1.2 Add a test that the pack never contains an amount, a date, or a loans.yml counterparty name; verify `pixi run test`

## 2. The merge

- [x] 2.1 `rules_merge.py`: `preview(rules_text, fragment) -> list[(section, line, pattern)]` and `merge(rules_text, fragment) -> str`, append-only, comment-preserving, refusing unknown lines against `categories.yml`; verify with tests on a commented file (diff is additive) and an unknown line (refused, named)
- [x] 2.2 `budget.py --merge <fragment.yml>` writes the merged personal `rules.yml`; verify on a copy of the sample config

## 3. The page

- [x] 3.1 Fourth output tab "Ask your AI" with copy and download; verify in the browser on the sample
- [x] 3.2 Paste box: validate via the worker, preview entries, merge into the editor, persist, re-run; verify the round trip on the sample removes the covered signatures from the pack
- [x] 3.3 `sample-regen`, README paragraph, `check-all` green
