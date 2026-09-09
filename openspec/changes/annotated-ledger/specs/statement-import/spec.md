## ADDED Requirements

### Requirement: A ledger-shaped file is annotations, not statements
A CSV whose header is `date,description,amount,kind,line,rule` SHALL be treated as an annotated ledger: its rows SHALL not be added as transactions, and the file SHALL be reported as annotations with the number of rows applied.

#### Scenario: Only a ledger is given
- **WHEN** the statements folder contains an annotated ledger and no statement exports
- **THEN** the tool refuses with a message that annotations need the original exports
