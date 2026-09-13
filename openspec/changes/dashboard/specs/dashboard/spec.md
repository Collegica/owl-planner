## Purpose

Writes the budget's first screen as one self-contained page beside `budget.md`, so the figure a person came for — and how far it can be trusted — is visible at a glance, and coverage is stated as a number of answers.

## ADDED Requirements

### Requirement: The dashboard is written beside budget.md
Every run that writes `budget.md` SHALL also write `dashboard.html` in the same folder, as a single file with inline style and no script that references no external resource.

#### Scenario: A run on invented statements
- **WHEN** the tool runs on a folder of invented CSV exports
- **THEN** `dashboard.html` exists beside `budget.md` and contains no `http:` or `https:` reference

### Requirement: The first screen carries coverage, the recurring figure, the annual figure and the set-asides
The page SHALL show, before any scrolling: the percentage of spending resting on a rule; the recurring monthly figure with its state (MEASURED, ESTIMATE or UNKNOWN); the annual figure only when the state is MEASURED, otherwise a dash and the reason; and the totals set aside as transfers, lending, savings, pass-throughs and income.

#### Scenario: Measured window
- **WHEN** the window holds three or more complete months
- **THEN** the page shows the MEASURED badge, the median per month, and twelve times it as the annual figure

#### Scenario: Estimate window
- **WHEN** the window holds one or two complete months
- **THEN** the page shows the ESTIMATE badge and a dash for the annual figure with the number of months still needed

### Requirement: Coverage is stated as a number of answers
When any spending is unclassified, the page SHALL say how many of the ranked interview questions, answered, would lift coverage to at least 95%, and to what percentage — or, when every question falls short of that, how far all of them would take it.

#### Scenario: Two questions
- **WHEN** 87% of spending is classified and the two unclassified signatures account for 9% and 4% of spending
- **THEN** the page says answering the next 2 questions takes coverage to 100%

#### Scenario: Nothing unclassified
- **WHEN** every transaction is classified
- **THEN** the page says so and names no count

### Requirement: The months behind the figure are drawn
The page SHALL draw one bar per complete month with the median month or months marked and a rule at the median, each bar labelled with its month and amount.

#### Scenario: Eight complete months
- **WHEN** the window holds eight complete months
- **THEN** the page holds eight bars and the median label

### Requirement: No identifier, and no advice
The page SHALL contain no merchant description, account or card number, or person's name, and SHALL contain no recommendation.

#### Scenario: Descriptions absent
- **WHEN** the statements contain the description `NEWTOWN DENTAL`
- **THEN** that text does not appear in `dashboard.html`

### Requirement: The same bytes from the CLI and the browser
Given the same statements and configuration, the browser engine SHALL produce a `dashboard.html` identical to the command line's.

#### Scenario: Parity on the sample
- **WHEN** the parity check runs on the invented household
- **THEN** `dashboard.html` from Pyodide equals the CLI's byte for byte
