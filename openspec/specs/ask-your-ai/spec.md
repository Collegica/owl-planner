# ask-your-ai Specification

## Purpose
Lets a person take the tool's open questions to an AI of their choice without taking their money with them, and bring the answer back as durable rules.

## Requirements

### Requirement: The pack carries names, never money
`ask-your-ai.md` SHALL contain only: a prompt, the budget lines available, the rule format, and the unclassified description signatures with an occurrence count and a size band rounded to one significant figure. It SHALL contain no transaction amount, no date, no account or card number fragment, and no counterparty name from `loans.yml`.

#### Scenario: Unclassified merchants
- **WHEN** `NEWTOWN DENTAL` appears three times totalling 452.21 and nothing else is unclassified
- **THEN** the pack lists `newtown dental — 3 times, ~$200 each` and no other figure

#### Scenario: Nothing to ask
- **WHEN** every transaction is classified
- **THEN** the pack says so and lists no signatures

### Requirement: Signatures are ranked by money, printed without it
Signatures SHALL appear in descending order of the total unclassified money behind them, and the pack SHALL state what share of unclassified money the list covers, without printing the total.

#### Scenario: Two unknowns
- **WHEN** one signature accounts for 900 and another for 12
- **THEN** the 900 one is listed first and the pack says the list covers 100% of what was not classified

### Requirement: The prompt asks for rules and permits "unsure"
The prompt SHALL ask for a `rules.yml` fragment with `categories:` (and `transfers:` / `income:` where applicable), one pattern per signature, and SHALL instruct the AI to answer `unsure` for any signature that could belong to more than one line.

#### Scenario: Prompt content
- **WHEN** the pack is written
- **THEN** it names every budget line from `categories.yml`, shows the YAML shape, and contains the word `unsure` with its instruction

### Requirement: The answer merges without loss
Merging a fragment SHALL append its entries to the matching sections of the personal `rules.yml`, SHALL create a missing section at the end of the file, SHALL preserve every existing line and comment byte for byte, and SHALL refuse a fragment that is not valid YAML or that names a budget line not in `categories.yml`, saying which.

#### Scenario: Append to a hand-edited file
- **WHEN** `rules.yml` contains comments and a fragment adds `Groceries: ['newtown grocer']`
- **THEN** the pattern is appended to the Groceries entry, the comments are unchanged, and a diff shows only added lines

#### Scenario: Unknown line
- **WHEN** a fragment names `Boats`
- **THEN** nothing is written and the message names `Boats` as not a budget line

### Requirement: The page offers the pack and takes the answer
The page SHALL show the pack in its own tab with copy and download, and SHALL provide a paste box that validates a fragment, previews the entries it will add, merges into the `rules.yml` editor, and re-runs.

#### Scenario: Round trip on the page
- **WHEN** a valid fragment is pasted and confirmed
- **THEN** the editor's `rules.yml` gains the entries, the budget is rebuilt, and the signatures the fragment covered no longer appear in the pack
