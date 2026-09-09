## 1. Engine surface

- [x] 1.1 Refactor `budget.py` so `run(argv: list[str]) -> str` returns the console text and `main()` prints it; verify `pixi run budget` output is unchanged on the sample (diff against a saved run)
- [x] 1.2 Add `--dir` handling for absolute virtual paths and `--out` for `budget.md` location; verify with `--dir /tmp/x --out /tmp/x/budget.md`

## 2. Web build

- [x] 2.1 Add `web/` with `index.html`, `app.js` (UI, IndexedDB, messages) and `worker.js` (Pyodide, virtual FS, `run`); verify the page loads locally with `python -m http.server` from `web/dist/`
- [x] 2.2 Add the `web-build` pixi task: download the pinned Pyodide release, copy the six runtime files plus the pyyaml wheel, copy `budget.py`, `categories.yml`, `*.example.yml` and the sample statements into `web/dist/`; verify `du -sh web/dist` is about 12 MB and no file exceeds 25 MB
- [x] 2.3 Implement drop/picker for CSVs, refuse `.pdf` with the message and link; verify by dropping a PDF and a CSV
- [x] 2.4 Implement the three YAML editors with IndexedDB persistence, export, import and delete-everything; verify the "return a week later" and "clear" scenarios by reloading the page
- [x] 2.5 Show runtime load progress with the size, off the main thread; verify the page stays editable during a cold load with cache disabled

## 3. Parity and privacy checks

- [x] 3.1 CI job: run the sample household through the CLI and through Pyodide in Node (`pyodide` npm package) and diff the console text and `budget.md`; verify the job fails when a line differs
- [x] 3.2 Verify in the browser's network panel that no request is made after assets load and that every request is same-origin; record the check in the README

## 4. Release and site

- [x] 4.1 CI: on a GitHub release, build `web/dist/` and attach `owl-web.tar.gz`; verify the asset appears on the release page
- [x] 4.2 Collegica workflow: after `pixi run public`, fetch the latest `owl-web.tar.gz` and unpack into `public/owl/`; verify `https://www.collegica.org/owl/` serves the page and its About-page claim still holds (no third-party requests)
- [x] 4.3 Add "run it in your browser" to the article's "Where it lives" section and to the README; verify both render and link to the live page
