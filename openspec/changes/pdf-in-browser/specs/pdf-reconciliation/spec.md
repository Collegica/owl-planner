## ADDED Requirements

### Requirement: Layout text can come from positioned fragments
Given the text fragments of a page with their positions, the tool SHALL reconstruct a fixed-width text in which fragments on the same line share a row and columns keep their horizontal order and alignment, such that the bank extractors produce the same transactions from it as from poppler's layout text for the same statement.

#### Scenario: Synthetic statement
- **WHEN** the invented fragment fixture for a bank is reconstructed and extracted
- **THEN** the transactions equal the fixture's expected CSV and the statement reconciles

### Requirement: The page converts PDFs and refuses what does not reconcile
The page SHALL accept a PDF statement, convert it in the browser, add the resulting CSV to the run and offer it for download, and SHALL report a statement that fails to reconcile by file name with the extracted and stated totals without using it.

#### Scenario: Known bank, reconciles
- **WHEN** a PDF from a supported bank is dropped
- **THEN** a CSV named after it appears in the file list, marked converted, with a download link

#### Scenario: Unknown layout
- **WHEN** a PDF matches none of the supported banks
- **THEN** the page says which banks it knows, suggests the bank's CSV export, and does not add anything to the run

#### Scenario: Does not reconcile
- **WHEN** the extracted total differs from the statement's stated total
- **THEN** the file is listed as refused with both figures and is not part of the run

### Requirement: pdf.js is first-party and pinned
The page SHALL load pdf.js from its own origin, at a version pinned in the build with a recorded checksum.

#### Scenario: Build
- **WHEN** `pixi run web-build` runs
- **THEN** `web/dist/` contains the pinned pdf.js files and no reference to a CDN
