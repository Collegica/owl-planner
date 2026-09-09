## Context

`pdf_import.py` calls `pdftotext -layout` and parses the text per bank with column offsets read from header lines. pdf.js returns per-page text items with a transform (x, y), width and the string. See proposal.md.

## Goals / Non-Goals

**Goals:** same extractors, second text source, same gate; the conversion output is the same normalised CSV the CLI writes.
**Non-Goals:** a generic statement parser; changing any extractor's parsing rules except where reconstruction demands a tolerance.

## Decisions

- **Reconstruct in Python, not JS.** The worker passes pdf.js items as JSON to Pyodide; `pdf_layout.py` does the geometry. Testable with pytest on fixtures, shared by CLI (a `--from-items` path useful for debugging) and browser.
- **Geometry:** cluster items into lines by y within a tolerance derived from font height; within a line, sort by x; map x to a character column by a page-wide character width estimated from the items (median of width/len); pad with spaces. Aim for column *alignment*, which the extractors depend on, not exact poppler byte-equality.
- **Split `pdf_import.py`:** `text_from_pdf(path)` (poppler) and `extract(text, bank)`; `main()` unchanged in behaviour. Bank detection stays as it is (by text markers).
- **Fixtures are invented twice:** a positioned-fragment JSON and the CSV it must yield, per bank, written by a small generator (`tests/fixtures/pdf/make_fixtures.py`) from an invented household month so nothing real is involved. Their totals lines make reconciliation exercisable.
- **Page:** dropping a PDF triggers a `convert` message; the worker replies with `{name, csv, reconciled, stated, extracted, bank}`; converted CSVs join `state.files` with a marker and a download link; refusals show in the notice area.
- **Vendoring:** `pdf.min.mjs` and `pdf.worker.min.mjs` from the pinned pdfjs-dist release on npm (registry tarball, SHA-256 recorded), loaded with `import()` inside the module worker.

## Risks / Trade-offs

- [Reconstruction misaligns a column on a real statement] → reconciliation refuses; the page shows both totals; the CLI path with poppler remains. A tolerance parameter can be tuned per bank without touching parsing rules.
- [pdf.js size, ~1.5 MB] → loaded lazily on the first PDF drop, not at page load.
- [Fixtures diverge from real layouts] → the developer verifies locally against real statements before merging; nothing from them is recorded.
