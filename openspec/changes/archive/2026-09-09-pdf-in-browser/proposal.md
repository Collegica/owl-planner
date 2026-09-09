## Why

Most people have PDFs, not CSVs. The CLI converts them with poppler and a reconciliation gate; the browser page declines them. pdf.js can supply the text with positions in the browser, and the gate makes a second text source safe: a layout that comes out wrong fails to reconcile and is refused, never miscounted.

## What Changes

- **A layout reconstructor**, `pdf_layout.py`: from a list of positioned text fragments (as pdf.js `getTextContent` returns them — string, x, y, width, per page) to the fixed-width, column-aligned text that `pdftotext -layout` produces, page by page. Pure Python, unit-tested, runs in Pyodide and in the CLI.
- **`pdf_import.py` split** into text acquisition and extraction: `extract(text, bank)` runs on text from either poppler or the reconstructor; the CLI path is unchanged in behaviour. The reconciliation gate applies to both.
- **The page accepts PDFs**: pdf.js (vendored, pinned, served first-party) reads the file in the worker, the reconstructor and extractor run in Pyodide, and the result is a normalised CSV the user can keep — offered for download and added to the run as if dropped. A statement that does not reconcile is reported by name with the extracted and stated totals, and not used.
- **Synthetic fixtures**: one invented statement per supported bank as positioned-fragment JSON plus its expected CSV, so CI covers the reconstruction without any real statement. Promotes IDEA-0002.
- Non-goals: banks without an extractor (the page names the four it knows and points at the CSV path); OCR of scanned statements; PDFs on the CLI without poppler.

Personal data: fixtures are invented; no real statement enters the repository. Real statements on the developer's machine may be used to verify locally and must never be copied, quoted, or committed.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
- `pdf-reconciliation`: text may come from a browser-side reconstruction as well as poppler; the gate applies identically; the page reports refusals.

## Impact

`pdf_import.py` (split), new `pdf_layout.py`, `web/worker.js` (pdf.js + the conversion), `web/app.js` (accept `.pdf`, show conversions and refusals, offer the CSVs), `scripts/web_build.py` (vendor pdf.js with a recorded SHA-256), `tests/fixtures/pdf/*`, `tests/test_pdf_layout.py`, README and the article's PDF sentence.
