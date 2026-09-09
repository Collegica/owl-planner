# PDF Reconciliation Specification

## Purpose

Converts PDF statements from supported banks into the normalised CSV shape, and refuses any statement whose extracted transactions do not add up to the totals the statement itself prints.

## Requirements

### Requirement: Every statement reconciles or is refused
For each PDF, the extractor SHALL compare the sum of extracted transactions against the totals printed in the statement's own summary and SHALL refuse to write output for a statement that does not reconcile, reporting the extracted and stated figures.

#### Scenario: Statement reconciles
- **WHEN** the extracted purchases, cash advances and fees sum to the statement's stated totals within one cent
- **THEN** the statement's transactions are written to the output CSV and the file is reported as reconciled

#### Scenario: Statement does not reconcile
- **WHEN** the extracted sum differs from the stated total
- **THEN** nothing from that statement is written, and the report names the statement, the extracted sum and the stated sum

### Requirement: Both directions are checked where the statement states both
For a chequing or savings statement that prints total deposits and total withdrawals, the extractor SHALL reconcile each direction independently.

#### Scenario: Withdrawals match but deposits do not
- **WHEN** extracted withdrawals equal the stated total and extracted deposits do not
- **THEN** the statement is refused

### Requirement: Statement year is resolved from the statement period
A transaction whose month is later than the statement's closing month SHALL be dated in the year before the closing year.

#### Scenario: December transaction on a January statement
- **WHEN** a statement closes in January 2026 and lists a transaction dated `Dec 19`
- **THEN** the transaction is dated `2025-12-19`

### Requirement: Column positions are read per page
For layouts whose column offsets can differ between pages, the extractor SHALL re-read the column headers on every page rather than assuming the first page's positions.

#### Scenario: Second page shifts the balance column
- **WHEN** the withdrawals column starts at a different character offset on page 2 than on page 1
- **THEN** page 2 amounts are still assigned to the correct column and the statement reconciles

### Requirement: Sign is never lost to formatting
A negative amount SHALL be recognised whether it is written with a leading minus, a trailing minus, or parentheses.

#### Scenario: Refund with a leading minus
- **WHEN** a purchase line shows `-119.06`
- **THEN** it is recorded as money in, not as a charge of 119.06

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
