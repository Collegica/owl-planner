# web-app Specification

## Purpose
Runs the budget engine inside the user's browser so that anyone with a folder of exports can get the same measured figure the CLI gives, without installing anything and without any file leaving their machine.

## Requirements

### Requirement: The same engine, unchanged
The web app SHALL run the repository's `budget.py`, `categories.yml` and `*.example.yml` as built, and SHALL produce byte-identical console output and `budget.md` to the CLI for the same inputs and configuration.

#### Scenario: Sample household in both
- **WHEN** the shipped sample statements and example configuration are run in the CLI and in the web app
- **THEN** the RECURRING line, the categorised percentage and `budget.md` are identical

### Requirement: Files are taken from the user, never fetched
The app SHALL accept statement CSVs by drag-and-drop or a file picker and SHALL hold them in memory or browser storage only.

#### Scenario: Drop four CSVs
- **WHEN** the user drops four CSV files on the page and presses run
- **THEN** the headline appears with `files 4`, and the browser's network log shows no request carrying file content

### Requirement: Personal configuration lives in the browser and is portable
The app SHALL provide editors for `rules.yml`, `loans.yml` and `known-annual.yml`, persist them in the browser's local storage, and SHALL offer export as plain YAML and import from it, and a single action that deletes everything it stored.

#### Scenario: Return a week later
- **WHEN** the user edited `rules.yml` in the app, closed the tab, and returns on the same browser
- **THEN** the edited rules are present and the app says where they are stored

#### Scenario: Clear
- **WHEN** the user chooses "delete everything stored here"
- **THEN** the editors return to the example files and the browser storage for the app is empty

### Requirement: PDF statements are declined with directions
The app SHALL not accept PDF statements and SHALL say that PDFs need the local tool, with a link.

#### Scenario: Drop a PDF
- **WHEN** a `.pdf` file is dropped
- **THEN** it is not read, and a message names `pixi run pdf-import` and links to the repository

### Requirement: The engine runs off the main thread
The app SHALL run the engine in a Web Worker so the page stays responsive, and SHALL show load progress while the runtime downloads on first visit.

#### Scenario: First visit
- **WHEN** the page is opened with an empty cache
- **THEN** a progress indicator shows the runtime loading, and the page remains scrollable and editable throughout
