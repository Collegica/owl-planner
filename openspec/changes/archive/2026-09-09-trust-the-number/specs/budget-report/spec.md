## MODIFIED Requirements

### Requirement: The headline separates measured from stated
The console output SHALL open with a coverage warning if one applies, then present, in order: what was read; LEVELLED obligations if any; RECURRING with its state, range and stability; ONE-OFF decided items; IRREGULAR undecided items; LENDING; SAVINGS; INCOME with savings rate and surplus; KNOWN YEARLY from `known-annual.yml`; SET ASIDE totals; and a PLANNING FIGURE equal to recurring plus known yearly. The RECURRING state SHALL be MEASURED with three or more complete months, ESTIMATE with one or two, and UNKNOWN with none. An annual figure — RECURRING per year, INCOME per year, the PLANNING FIGURE — SHALL be printed only when MEASURED; otherwise the line SHALL say what is missing.

#### Scenario: No known yearly items
- **WHEN** `known-annual.yml` has every line commented out
- **THEN** PLANNING FIGURE equals RECURRING and no KNOWN YEARLY block is printed

#### Scenario: Seven weeks of statements
- **WHEN** the window contains exactly one complete calendar month
- **THEN** RECURRING shows a monthly figure labelled ESTIMATE, no per-year figure, and the PLANNING FIGURE line says an annual figure needs three complete months

#### Scenario: No complete month
- **WHEN** the window starts and ends inside the same calendar month, or spans two partial months
- **THEN** RECURRING is labelled UNKNOWN, names the window, and asks for whole months; no per-month or per-year figure is printed

### Requirement: Nothing disappears silently
Every dollar set aside — transfers, lending, pass-throughs, unidentified — SHALL be totalled under SET ASIDE with the number of transactions behind each line, so the reader can reconcile the statements against the budget.

#### Scenario: Transfers excluded
- **WHEN** 40,000 of transfers between own accounts were excluded across 48 transactions
- **THEN** SET ASIDE lists that amount under transfers with the count 48

### Requirement: budget.md follows the intake form
`budget.md` SHALL open with the state and the number of complete months, present spending by the groups and lines in `categories.yml` with a savings section separate from expenses, label its two amount columns as the window total and a per-month average, mark lines filled by the bank-category fallback, and end with a section showing how the recurring figure was made.

#### Scenario: Savings section
- **WHEN** any transaction matched a savings line
- **THEN** budget.md has a Savings table above the expense groups

#### Scenario: The arithmetic
- **WHEN** the state is MEASURED
- **THEN** budget.md's final section lists each complete month with its recurring total, marks the median month or months, and shows the count behind every set-aside line

## ADDED Requirements

### Requirement: The arithmetic behind the recurring figure is shown
Under RECURRING the console SHALL list every complete month with its total and mark the month or months that form the median; under a LEVELLED line it SHALL list the transfers that were levelled with their dates.

#### Scenario: Eight complete months
- **WHEN** eight complete months are observed
- **THEN** eight month totals are printed in date order and the two middle values by size are marked as the median

### Requirement: A ledger of every transaction and its kind
The tool SHALL write `ledger.csv` beside `budget.md` with one row per transaction after de-duplication: date, description, amount, kind, budget line, and the rule that decided it, where kind is one of passthrough, lending, repayment, transfer, income, refund, savings, spending, review, uncategorised.

#### Scenario: A pinned loan
- **WHEN** a withdrawal is pinned in `loans.yml` as a disbursement
- **THEN** its ledger row has kind `lending` and rule `pin`
