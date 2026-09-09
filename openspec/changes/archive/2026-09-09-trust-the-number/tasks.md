## 1. The record

- [x] 1.1 Record a kind, line and rule for every transaction in the classification loop and write `ledger.csv` beside `budget.md`; verify `pixi run sample` writes it with 293 rows and the pinned cheque has kind `lending`, rule `pin`

## 2. The headline

- [x] 2.1 Coverage guard from card-payment outflows and inflows; verify a chequing-only run of the sample prints COVERAGE first and the full sample prints none
- [x] 2.2 States on RECURRING, INCOME and PLANNING FIGURE; verify `--year 2026` on a two-month slice prints ESTIMATE with no per-year figure, and a slice inside one month prints UNKNOWN
- [x] 2.3 The months line with the median marked, the levelled transfers, counts on SET ASIDE; verify against `sample/expected.txt` after `sample-regen`
- [x] 2.4 `budget.md`: state in the header, columns renamed, a closing "How the number was made" section; verify by reading `sample/budget.md`

## 3. Tests and the page

- [x] 3.1 `tests/test_precedence.py` on invented CSVs: pinned loan beats a support pattern; review is last; savings is not spending; pass-through cancels; card payment is a transfer; coverage guard; three states — verify `pixi run test` passes and `check-all` includes it
- [x] 3.2 Colour MEASURED / ESTIMATE / UNKNOWN / COVERAGE on the page and offer `ledger.csv` for download; verify in the browser on the sample
- [x] 3.3 Regenerate `sample/expected.txt`, update the README's example output, cut a release; verify `pixi run check-all` and the live page
