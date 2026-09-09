## 1. Reconstruction

- [x] 1.1 `pdf_layout.py`: `layout(pages: list[list[item]]) -> str` per the design; verify unit tests on hand-built item lists (two columns, right-aligned amounts, a wrapped line)
- [x] 1.2 Split `pdf_import.py` into `text_from_pdf` and `extract(text, bank)` with `main()` unchanged; verify `pixi run pdf-import -- --dir <folder>` on the developer's local statements still reconciles every one (report pass/fail counts only)

## 2. Fixtures and tests

- [x] 2.1 `tests/fixtures/pdf/make_fixtures.py` writing one invented positioned-fragment JSON and expected CSV per supported bank, with totals lines; verify the files are generated deterministically
- [x] 2.2 `tests/test_pdf_layout.py`: each fixture reconstructs, extracts to the expected CSV, and reconciles; verify `pixi run test`

## 3. The page

- [x] 3.1 Vendor pdf.js in `scripts/web_build.py` (pinned, SHA-256 recorded, first-party); verify `web/dist/` contains it and `grep -r cdn web/dist/*.js` is empty
- [x] 3.2 Worker `convert` message: pdf.js items → Pyodide → CSV or refusal; verify on a fixture-derived PDF or the developer's local statements
- [x] 3.3 Page: accept `.pdf`, list conversions with download, show refusals and unknown layouts; verify in the browser
- [x] 3.4 README and the article sentence about PDFs; `check-all` green
