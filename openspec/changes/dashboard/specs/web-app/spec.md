## ADDED Requirements

### Requirement: The dashboard is a tab
The page SHALL show the engine's `dashboard.html` in a Dashboard tab, rendered in a sandboxed frame from the text the worker returned, and SHALL offer it for download; the page SHALL not alter its content.

#### Scenario: After a run
- **WHEN** the budget has been built in the page
- **THEN** the Dashboard tab shows the same page the CLI would have written, and the download is that file
