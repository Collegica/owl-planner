# Privacy Specification

## Purpose

Guarantees that a person's financial data stays on their machine and out of any repository, because a tool that reads bank statements is only acceptable if it cannot leak them.

## Requirements

### Requirement: No network, no credentials
The tool SHALL make no network requests and SHALL require no bank credentials, API keys or accounts. Input is files the user exported themselves.

#### Scenario: Offline run
- **WHEN** the machine has no network connection
- **THEN** `pixi run budget` completes normally

### Requirement: Personal files are never tracked
`statements/`, `budget.md`, `uncategorised.csv`, `rules.yml`, `loans.yml` and `known-annual.yml` SHALL be ignored by version control. Only `*.example.yml` files with invented values SHALL be tracked.

#### Scenario: Git status after a run
- **WHEN** the tool has been run on real statements
- **THEN** `git status` shows no new tracked or untracked file containing transaction data

### Requirement: Aggregated output carries no identifiers
`budget.md` SHALL contain no account numbers, card numbers or counterparty names — only budget lines and amounts — so it can be shared or given to an AI after translation to ratios.

#### Scenario: Card number in a description
- **WHEN** a description contains a masked card number
- **THEN** it does not appear in budget.md
