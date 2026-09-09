## ADDED Requirements

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
