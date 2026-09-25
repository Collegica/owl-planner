## ADDED Requirements

### Requirement: A statement is identified by the bank it names most
When a PDF's file name does not name a supported bank, the tool SHALL identify the statement by the supported bank whose name appears most often in its text, and SHALL NOT identify it when two supported banks appear equally often, reporting it as an unknown layout instead.

#### Scenario: A savings statement mentions a card at another bank
- **WHEN** an RBC statement named `statement.pdf` carries one transaction line `PAYMENT CIBC VISA`
- **THEN** it is identified as RBC, and reconciles as it does without that line

#### Scenario: A card statement mentions a payment from another bank
- **WHEN** a CIBC card statement named `statement.pdf` carries one transaction line `PAYMENT FROM RBC`
- **THEN** it is identified as CIBC

#### Scenario: Two banks named equally often
- **WHEN** a statement's text names CIBC once and RBC once and nothing else identifies it
- **THEN** it is reported as an unknown layout, the page names the banks it knows and suggests the bank's CSV export, and nothing from it is used
