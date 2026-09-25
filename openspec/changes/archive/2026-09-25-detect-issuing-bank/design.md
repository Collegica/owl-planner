## Context

`detect_bank(name, text)` tries the file name first, then `TEXT_MARKERS` in insertion order and returns the first marker found anywhere in the text. The markers are `ScotiaLine`, `Ultimate`, `CIBC`, then `RBC|Royal Bank`.

## Decisions

- **Count, don't search.** For each marker, count its matches in the text; take the bank with the most. A statement prints its own bank's name in its header, footer and legal text on every page; another bank appears only in a transaction description. A statement names its own bank many times over; a card at another bank appears once per payment.
- **A tie is not identified.** Equal counts return `None`, which the page already reports as an unknown layout with the CSV export suggested. Refusing is preferred to guessing.
- **The file name still wins.** Unchanged: a name that contains a bank's name is what the command line has always matched, and the person chose it.

## Risks

- The Ultimate marker is weak: a Scotiabank Ultimate statement may name "Ultimate" only once or twice, so a statement whose transactions named ScotiaLine more often would be read as ScotiaLine. That is no worse than the first-found order, which tried ScotiaLine first; the ScotiaLine extractor would then fail to reconcile it and refuse it.
- A statement that names another bank more often than its own would still be misread. The extractor would then fail to reconcile it and refuse it, which is the existing safety net; it is not silently wrong.
