## ADDED Requirements

### Requirement: Partial coverage is detected before any figure
When transfers to a credit card leave an exported account and the card's own export is absent — detected as card-payment inflows totalling less than half the card-payment outflows — the tool SHALL print a COVERAGE warning naming the amount and the missing export before any figure, and SHALL still produce the budget.

#### Scenario: Chequing only
- **WHEN** only a chequing export is given and it contains payments to a credit card
- **THEN** the first block of the headline is a COVERAGE warning that the card's export is missing, and the budget follows it

#### Scenario: Both sides present
- **WHEN** chequing and the card are both exported and the payments appear on both
- **THEN** no COVERAGE warning is printed
