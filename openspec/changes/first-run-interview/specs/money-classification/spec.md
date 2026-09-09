## MODIFIED Requirements

### Requirement: What could not be classified is listed largest first
Unmatched spending SHALL be grouped by description signature and sorted by total amount descending. This ordered list SHALL be the input to the first-run interview and SHALL also be written to `uncategorised.csv`; the percentage of spending categorised SHALL be printed.

#### Scenario: Three unknown merchants
- **WHEN** three descriptions match nothing, totalling 900, 40 and 12
- **THEN** the interview asks about them in that order and the file lists them in that order with their totals
