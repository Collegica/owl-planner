# Money Classification Specification

## Purpose

Decides what each transaction is — a transfer, lending, savings, a pass-through, income, or spending — because only the last of those belongs in a budget, and a bank feed shows them all the same way.

## Requirements

### Requirement: Only spending is spending
Every outflow SHALL be classified as exactly one of: transfer between own accounts, lending disbursement, savings contribution, pass-through, or spending. Every inflow SHALL be classified as exactly one of: transfer, loan repayment, pass-through, income, or refund. Only spending contributes to the budget, and each other kind SHALL be totalled and reported separately.

#### Scenario: Credit card payment from chequing
- **WHEN** a chequing outflow matches a transfer pattern such as `payment - thank you` or `transfer to credit card`
- **THEN** it is set aside as a transfer and does not appear in any budget line

#### Scenario: RRSP contribution
- **WHEN** an outflow matches a pattern under a savings line such as `Registered investments`
- **THEN** it is reported under SAVINGS, not under spending, and the savings rate is computed from it

### Requirement: Rules are data, and the personal file wins
Classification SHALL be driven by `rules.yml`, `loans.yml` and `known-annual.yml` when present, else by the corresponding `*.example.yml`. The code SHALL contain no pattern specific to any person.

#### Scenario: Fresh clone
- **WHEN** no personal yml files exist
- **THEN** the tool runs using the example files and reports its coverage rather than failing

### Requirement: Precedence is fixed and pins beat patterns
A transaction SHALL be tested in this order: pass-through pin, loan counterparty, dated disbursement or receipt, transfer pattern, income pattern, dated one-off pin, category pattern, savings line, bank-category fallback, review bucket, uncategorised. A pin by date and amount SHALL override any pattern.

#### Scenario: A loan that matches a support pattern
- **WHEN** an Interac withdrawal matches a `Child support` category pattern but its date and amount are pinned in `loans.yml` as a disbursement
- **THEN** it is recorded as lending and not as support

#### Scenario: Review bucket is a last resort
- **WHEN** an e-transfer at or above `review_min` matches a category pattern
- **THEN** it is categorised, not sent to the review bucket

### Requirement: Pass-throughs cancel on both legs
A transaction pinned under `passthrough` SHALL be excluded from both income and spending, and the total passed through SHALL be reported.

#### Scenario: Rebate received and forwarded
- **WHEN** an inflow and an outflow of the same amount are both pinned on the same date
- **THEN** neither appears in income or spending, and SET ASIDE lists the pass-through total

### Requirement: The bank's category is a fallback, and marked as such
When no rule matches and the description carries a bank-supplied category, the tool SHALL map it through `bank_categories` and mark lines filled this way in the budget.

#### Scenario: Unknown merchant with a bank category
- **WHEN** `NEW SHOP  Retail and Grocery` matches no pattern
- **THEN** it lands in Groceries with a marker showing the bank's category was used

### Requirement: What could not be classified is listed largest first
Unmatched spending SHALL be written to `uncategorised.csv` grouped by description and sorted by total amount descending, and the percentage of spending categorised SHALL be printed.

#### Scenario: Three unknown merchants
- **WHEN** three descriptions match nothing, totalling 900, 40 and 12
- **THEN** the file lists them in that order with their totals
