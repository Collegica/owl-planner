## Purpose

Turns what the tool cannot classify into a short, dollar-ranked set of questions, and turns each answer into a durable rule so the same question is never asked twice.

## ADDED Requirements

### Requirement: Questions are ranked by money, not count
When unclassified spending exceeds a threshold share of total outflow, the tool SHALL print a question list ordered by the total amount each description signature accounts for, descending, and SHALL state what share of unclassified money the listed questions cover.

#### Scenario: Three unknown signatures
- **WHEN** unclassified money is 900 under `NEW GROCER`, 300 under `SQ *CAFE` and 12 under `PARKING LOT 7`
- **THEN** the questions appear in that order and the header states that the first two cover 93% of unclassified money

### Requirement: One question per signature
Descriptions sharing a signature SHALL produce one question that shows the count and total of its recurrences, so one answer covers all of them.

#### Scenario: Recurring unknown merchant
- **WHEN** `NEW GROCER #12` appears in five months
- **THEN** a single question shows 5 transactions and their total, and the answer applies to all five

### Requirement: Every kind of money movement is an available answer
Each question SHALL accept, as an answer, any budget line from `categories.yml` or any of: transfer, income, lending (with counterparty), savings line, pass-through, one-off, level. An answer of "don't know" SHALL leave the transactions unclassified and SHALL not be asked again in the same run.

#### Scenario: Answer is a transfer
- **WHEN** the user answers that `TFR TO 4412` is a transfer
- **THEN** a pattern for it is appended under `transfers` in `rules.yml` and the transactions leave spending on the next run

#### Scenario: Answer is lending
- **WHEN** the user answers that an e-transfer is a loan to a named person
- **THEN** a counterparty entry is appended to `loans.yml` and the transactions are reported under LENDING

### Requirement: Answers become rules with reasons
Every answer SHALL be written to the personal configuration as a pattern with a `note:` recording the answer's date and the user's stated reason, and SHALL never be written to a tracked file.

#### Scenario: Written rule is durable
- **WHEN** an answer has been recorded and the tool is run again
- **THEN** the same signature is classified without a question and the note is present in the yml

### Requirement: Existing rules are preserved when writing
Writing an answer SHALL not remove or reorder existing entries or comments in the personal yml.

#### Scenario: Append to a hand-edited file
- **WHEN** `rules.yml` contains comments and an answer is recorded
- **THEN** the comments and prior entries are unchanged and the new entry follows them in its section

### Requirement: The budget is still produced, with its coverage stated
The same run SHALL produce the budget after the question list, and the headline SHALL state the categorised percentage so the reader knows how much of the figure rests on answered questions.

#### Scenario: Unanswered questions
- **WHEN** the user skips all questions
- **THEN** the budget is still written and its headline shows the unchanged categorised percentage
