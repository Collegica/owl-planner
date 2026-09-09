# Budget Report Specification

## Purpose

Prints the headline and writes `budget.md` so that a measured figure, an estimate and a decision are never confused with one another, and nothing that moved disappears silently.

## Requirements

### Requirement: The headline separates measured from stated
The console output SHALL present, in order: what was read; LEVELLED obligations if any; RECURRING with its range and stability; ONE-OFF decided items; IRREGULAR undecided items; LENDING; SAVINGS; INCOME with savings rate and surplus; KNOWN YEARLY from `known-annual.yml`; SET ASIDE totals; and a PLANNING FIGURE equal to recurring plus known yearly.

#### Scenario: No known yearly items
- **WHEN** `known-annual.yml` has every line commented out
- **THEN** PLANNING FIGURE equals RECURRING and no KNOWN YEARLY block is printed

### Requirement: Nothing disappears silently
Every dollar set aside — transfers, lending, pass-throughs, unidentified — SHALL be totalled under SET ASIDE so the reader can reconcile the statements against the budget.

#### Scenario: Transfers excluded
- **WHEN** 40,000 of transfers between own accounts were excluded
- **THEN** SET ASIDE lists that amount under transfers

### Requirement: budget.md follows the intake form
`budget.md` SHALL present spending by the groups and lines in `categories.yml`, with a savings section separate from expenses, monthly and annual columns, and a marker on lines filled by the bank-category fallback.

#### Scenario: Savings section
- **WHEN** any transaction matched a savings line
- **THEN** budget.md has a Savings table above the expense groups

### Requirement: Income is a median too
INCOME SHALL be the median of complete-month identified income, annualised, with the observed range printed.

#### Scenario: One bonus month
- **WHEN** one month's income is three times the others
- **THEN** the annual income figure is the median month times twelve and the range shows the bonus month
