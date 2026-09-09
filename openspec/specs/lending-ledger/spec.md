# Lending Ledger Specification

## Purpose

Keeps money lent to people out of spending and money repaid out of income, and reports what is outstanding — including legs that fall outside the exported statements.

## Requirements

### Requirement: Lending is an asset, not spending
An outflow identified as a loan disbursement — by counterparty pattern or by a dated pin — SHALL be excluded from spending and totalled under LENDING. An inflow identified as a repayment SHALL be excluded from income.

#### Scenario: Cheque to a friend
- **WHEN** a branch withdrawal is pinned in `loans.yml` as a disbursement to Friend A
- **THEN** it appears under LENDING as lent out and in no budget line

### Requirement: Outstanding is computed from the book, not inferred from patterns
For each entry under `lent`, the tool SHALL report `principal - repaid` as outstanding. The tool SHALL NOT infer a loan from an e-transfer pattern alone.

#### Scenario: Partly repaid loan
- **WHEN** `lent` lists principal 5,000 and repaid 2,000
- **THEN** LENDING reports 3,000 outstanding of 5,000

### Requirement: Legs outside the window are named, not lost
A disbursement or receipt in `loans.yml` whose date falls outside the exported statements SHALL be listed as recorded but not in these statements.

#### Scenario: Repayment after the last statement
- **WHEN** a receipt is dated after the latest statement close
- **THEN** it is printed under LENDING as outside the exported window

### Requirement: Unexplained large transfers are questions, not guesses
An outflow matching a `review` pattern at or above `review_min` that matches no other rule SHALL be counted as neither spending nor lending and SHALL be listed for the user to identify.

#### Scenario: Large e-transfer with no rule
- **WHEN** an e-transfer of 2,500 matches nothing else
- **THEN** it appears in a NEEDS IDENTIFYING list and in no total
