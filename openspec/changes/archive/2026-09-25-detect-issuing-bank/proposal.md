## Why

A PDF whose file name does not name its bank is identified by the first bank name found anywhere in its text, tried in a fixed order with CIBC before RBC. A chequing or savings statement names other banks in its transactions — a payment to a CIBC card from an RBC savings account prints "CIBC" on the RBC statement — so that statement is handed to the CIBC card extractor, finds no card summary, and is refused as "no totals line was found". It was seen on the page at collegica.org/owl/: bank statements that mention a card at another bank were refused, and statements from the same account that do not were read.

Changing the order would only move the fault: a CIBC card statement that shows a payment from RBC would then go to the RBC extractor.

## What Changes

- When the file name does not name a bank, the statement is identified by the bank its text names most often, not the first one found. A statement names its own bank on every page — in its header, footer and fine print — and another bank only in the odd transaction.
- When two banks are named equally often, the statement is not identified: it is reported as an unknown layout, with the bank's CSV export suggested, rather than guessed.
- Non-goals: no new extractor, no change to any extractor or to reconciliation, no change to identification from the file name.

Personal data: the scenarios and tests use the invented fixtures already in `tests/fixtures/` with an invented transaction line added; nothing from a real statement is committed.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
- `pdf-reconciliation`: how a statement's bank is identified from its text.

## Impact

`pdf_import.py` (`detect_bank`), `tests/test_pdf_layout.py`. The page uses the same function through Pyodide, so it changes too; the engine's output on the sample does not.
