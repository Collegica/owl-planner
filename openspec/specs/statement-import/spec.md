# Statement Import Specification

## Purpose

Reads bank and credit-card exports of any common CSV shape and reduces each to one normalised form — date, description, signed amount — so that the rest of the tool never has to know which bank a file came from.

## Requirements

### Requirement: Any common CSV shape is accepted
The tool SHALL read every `*.csv` file in the statements folder regardless of delimiter (comma, semicolon, tab), encoding (UTF-8, CP1252, Latin-1), presence of a header row, amount format (`1,234.56` or `1 234,56`), and whether amounts are one signed column or separate debit and credit columns.

#### Scenario: Semicolon file with separate debit and credit columns
- **WHEN** a file uses `;` as delimiter and has `Debit` and `Credit` columns
- **THEN** each row becomes one transaction with debits negative and credits positive

#### Scenario: Delimiter chosen by row consistency
- **WHEN** a file's delimiter cannot be sniffed from the header alone
- **THEN** the delimiter that yields the same column count on every row is used

### Requirement: Dates are normalised and never guessed
Each file's date convention SHALL be inferred from its own content: a day value greater than 12 in the first position proves day-first, in the second position proves month-first. `--date-order` is a fallback used only when a file contains no such proof.

#### Scenario: Ambiguous file without proof
- **WHEN** every date in a file has both parts at or below 12 and `--date-order` is not given
- **THEN** the tool reports the file as ambiguous and asks for `--date-order` rather than picking a convention

#### Scenario: Proof overrides the flag
- **WHEN** `--date-order mdy` is given and a file contains `25/03/2026`
- **THEN** the file is read day-first because its own content proves it

### Requirement: Duplicates across overlapping exports are dropped
When two exports overlap in time, a transaction with the same date, description and amount appearing in both SHALL be counted once, and the number dropped SHALL be reported.

#### Scenario: Overlapping monthly exports
- **WHEN** a March export and a February-to-March export both contain `2026-03-02, GROCER, -41.20`
- **THEN** the transaction appears once and the summary line reports `duplicates dropped 1`

### Requirement: The normalised shape is the only contract
Every transaction SHALL be reduced to `Date` (ISO 8601), `Description` (as printed by the bank) and `Amount` (negative for money out). A hand-written file in that shape SHALL be accepted like any export.

#### Scenario: Hand-written three-column file
- **WHEN** the folder contains a file whose header is exactly `Date,Description,Amount`
- **THEN** it is read without any inference and its rows are treated identically to an exported file

### Requirement: A runnable sample ships with the tool
The repository SHALL contain an invented household — statements in several CSV dialects and a complete configuration — such that `pixi run sample` produces a full budget on a fresh clone, and CI SHALL fail when the sample's output changes unintentionally.

#### Scenario: Fresh clone
- **WHEN** the repository is cloned and `pixi run sample` is run with no personal files present
- **THEN** the headline reports four files, a steady RECURRING figure, LEVELLED, ONE-OFF, IRREGULAR, LENDING, SAVINGS, INCOME and KNOWN YEARLY blocks, with no real person's data involved

#### Scenario: Output drifts
- **WHEN** a change alters any line of the sample's console output
- **THEN** `pixi run sample-check` fails with a diff, and `pixi run sample-regen` is the deliberate way to accept the new output

### Requirement: Configuration can live anywhere
`--config <dir>` SHALL select the folder holding `rules.yml`, `loans.yml` and `known-annual.yml`; any file missing there SHALL fall back to the tool's `*.example.yml`.

#### Scenario: Sample configuration
- **WHEN** `--config sample` is given and `sample/` holds the three files
- **THEN** they are used and the tool's own personal files, if any, are not read
