## 1. The page

- [x] 1.1 `dashboard.py` with `render(data)` and `coverage_step`; verify on invented rows that the coverage line names the right count and percentage, the state badge matches the console, and the set-aside totals equal the console's SET ASIDE lines
- [x] 1.2 `budget.py` assembles `data` and writes `dashboard.html` beside `budget.md`, printing one `wrote dashboard.html` line without a path; verify `pixi run sample` writes the file and `sample-check` passes after `sample-regen`
- [x] 1.3 Verify the file names no merchant, account or person (assert every description in the sample is absent) and contains no `http` reference

## 2. The browser

- [x] 2.1 Ship `dashboard.py` in `web_build.py` and `worker.js`; return the file with the run result; verify `web-parity` compares `dashboard.html` byte for byte with the CLI's
- [ ] 2.2 Fifth tab *Dashboard* with a sandboxed iframe and a download button (built; the parity check proves the bytes) — verify with `pixi run web-serve` in a browser: maintainer

## 3. Docs and regression

- [x] 3.1 README: the output line under *Run it* and the row in *The files*
- [ ] 3.2 Re-run `pixi run budget` on the maintainer's statements and confirm RECURRING, categorised % and SET ASIDE are unchanged (the dashboard reads them; it must not move them)
