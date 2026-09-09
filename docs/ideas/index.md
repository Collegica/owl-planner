# Ideas — index

*Generated from the headers in this folder. Do not edit; edit the idea.*

29 ideas: 24 seed, 0 explored, 3 promoted, 2 retired.

## In order

Open ideas (`seed`, `explored`) by value, then by effort — S is days, M weeks, L a quarter or a dependency we do not control. Ties keep id order; the ranking is only as good as the two header fields, which are reviewed with the idea.

| # | id | idea | value | effort | capability | lens |
|---|---|---|---|---|---|---|
| 1 | IDEA-0005 | [Detect a card paid from chequing whose own export is missing, and say so before reporting](20260909_refuse-to-conclude-on-partial-coverage.md) | high | S | `statement-import` | `customer` |
| 2 | IDEA-0006 | [Three typographic states in the report: MEASURED, ESTIMATE, UNKNOWN](20260909_measured-estimate-unknown.md) | high | S | `budget-report` | `review` |
| 3 | IDEA-0009 | [The report shows the months behind every headline number](20260909_show-the-arithmetic.md) | high | S | `budget-report` | `canadian-planners` |
| 4 | IDEA-0011 | [Emit a ratio profile — `$X` and multiples — that the planners downstream can take](20260909_a-ratio-profile-for-hand-off.md) | high | S | `planning` | `canadian-planners` |
| 5 | IDEA-0014 | [`OWL_HOME`: keep the personal files outside the repository directory altogether](20260909_personal-files-outside-the-checkout.md) | high | S | `privacy` | `canadian-planners` |
| 6 | IDEA-0021 | [The ledger gets its missing direction: money someone lent to you](20260909_the-fourth-state-borrowed.md) | high | S | `lending-ledger` | `iou-trackers` |
| 7 | IDEA-0022 | [Terms on the book: when it was lent, when it is due, and how many days late it is](20260909_terms-and-days-past-due.md) | high | S | `lending-ledger` | `formal-loan-record` |
| 8 | IDEA-0025 | [Money paid on someone's behalf and coming back later: a reimbursable, not a loan and not spending](20260909_reimbursables.md) | high | S | `lending-ledger` | `iou-trackers` |
| 9 | IDEA-0001 | [Every figure in the budget can say which rule produced it](20260909_every-figure-answers-why.md) | high | M | `money-classification` | `data` |
| 10 | IDEA-0002 | [A regression suite of invented statements, one per bug the reconciler has caught](20260909_synthetic-statement-fixtures.md) | high | M | `pdf-reconciliation` | `incident` |
| 11 | IDEA-0016 | [Golden tests for the classification order, on an invented CSV](20260909_golden-tests-for-precedence.md) | high | M | `money-classification` | `canadian-planners` |
| 12 | IDEA-0003 | [Notice a month-end payment that wobbles across the boundary, and suggest `level`](20260909_detect-month-boundary-wobble.md) | medium | S | `recurring-baseline` | `data` |
| 13 | IDEA-0004 | [A pin that matches no transaction is reported, not silently ignored](20260909_pins-that-match-nothing.md) | medium | S | `money-classification` | `incident` |
| 14 | IDEA-0010 | [Every run prints its assumptions and its out-of-scope list](20260909_print-the-assumptions.md) | medium | S | `budget-report` | `canadian-planners` |
| 15 | IDEA-0015 | [One normalised, classified, re-importable ledger that outlives any bank's export window](20260909_a-durable-ledger-export.md) | medium | S | `statement-import` | `canadian-planners` |
| 16 | IDEA-0017 | [Export the intake-form table as a workbook a planner can open](20260909_intake-form-workbook.md) | medium | S | `budget-report` | `canadian-planners` |
| 17 | IDEA-0018 | [State what the figures are and are not, on every output surface](20260909_education-not-advice-on-every-surface.md) | medium | S | `planning` | `canadian-planners` |
| 18 | IDEA-0023 | [Show the repayment schedule against what actually arrived](20260909_expected-against-received.md) | medium | S | `lending-ledger` | `formal-loan-record` |
| 19 | IDEA-0024 | [A loan you decide not to collect is written off — dated, reasoned, and moved to the budget](20260909_write-off-as-a-state.md) | medium | S | `lending-ledger` | `formal-loan-record` |
| 20 | IDEA-0026 | [A statement per person: every leg, dated, with a running balance](20260909_per-counterparty-statement.md) | medium | S | `lending-ledger` | `iou-trackers` |
| 21 | IDEA-0028 | [Expected repayments are dated inflows in the plan, not just an outstanding balance](20260909_receivables-in-the-plan.md) | medium | S | `planning` | `formal-loan-record` |
| 22 | IDEA-0013 | [A monthly net-worth line, for free, from the closing balances every statement already carries](20260909_net-worth-from-closing-balances.md) | medium | M | `planning` | `canadian-planners` |
| 23 | IDEA-0012 | [Two people, one budget: transfers between partners are a third kind of movement](20260909_household-mode.md) | medium | L | `household` | `canadian-planners` |
| 24 | IDEA-0027 | [An optional `rate:` on a loan, and the one date that matters for a family investment loan](20260909_rate-and-the-30-january-line.md) | low | S | `lending-ledger` | `iou-trackers` |

## Statement import (`statement-import`) — 4

| id | idea | lens | value | effort | status | went to |
|---|---|---|---|---|---|---|
| IDEA-0005 | [Detect a card paid from chequing whose own export is missing, and say so before reporting](20260909_refuse-to-conclude-on-partial-coverage.md) | `customer` | high | S | seed |  |
| IDEA-0008 | [Ship an invented household: sample statements so a fresh clone produces a complete budget](20260909_an-invented-household-ships-with-the-repo.md) | `canadian-planners` | high | M | promoted | `openspec/changes/sample-household` |
| IDEA-0015 | [One normalised, classified, re-importable ledger that outlives any bank's export window](20260909_a-durable-ledger-export.md) | `canadian-planners` | medium | S | seed |  |
| IDEA-0019 | [A read-only open-banking importer — retired](20260909_open-banking-import.md) | `canadian-planners` | low | L | retired |  |

## PDF reconciliation (`pdf-reconciliation`) — 1

| id | idea | lens | value | effort | status | went to |
|---|---|---|---|---|---|---|
| IDEA-0002 | [A regression suite of invented statements, one per bug the reconciler has caught](20260909_synthetic-statement-fixtures.md) | `incident` | high | M | seed |  |

## Money classification (`money-classification`) — 3

| id | idea | lens | value | effort | status | went to |
|---|---|---|---|---|---|---|
| IDEA-0001 | [Every figure in the budget can say which rule produced it](20260909_every-figure-answers-why.md) | `data` | high | M | seed |  |
| IDEA-0004 | [A pin that matches no transaction is reported, not silently ignored](20260909_pins-that-match-nothing.md) | `incident` | medium | S | seed |  |
| IDEA-0016 | [Golden tests for the classification order, on an invented CSV](20260909_golden-tests-for-precedence.md) | `canadian-planners` | high | M | seed |  |

## Recurring baseline (`recurring-baseline`) — 1

| id | idea | lens | value | effort | status | went to |
|---|---|---|---|---|---|---|
| IDEA-0003 | [Notice a month-end payment that wobbles across the boundary, and suggest `level`](20260909_detect-month-boundary-wobble.md) | `data` | medium | S | seed |  |

## Lending ledger (`lending-ledger`) — 7

| id | idea | lens | value | effort | status | went to |
|---|---|---|---|---|---|---|
| IDEA-0021 | [The ledger gets its missing direction: money someone lent to you](20260909_the-fourth-state-borrowed.md) | `iou-trackers` | high | S | seed |  |
| IDEA-0022 | [Terms on the book: when it was lent, when it is due, and how many days late it is](20260909_terms-and-days-past-due.md) | `formal-loan-record` | high | S | seed |  |
| IDEA-0023 | [Show the repayment schedule against what actually arrived](20260909_expected-against-received.md) | `formal-loan-record` | medium | S | seed |  |
| IDEA-0024 | [A loan you decide not to collect is written off — dated, reasoned, and moved to the budget](20260909_write-off-as-a-state.md) | `formal-loan-record` | medium | S | seed |  |
| IDEA-0025 | [Money paid on someone's behalf and coming back later: a reimbursable, not a loan and not spending](20260909_reimbursables.md) | `iou-trackers` | high | S | seed |  |
| IDEA-0026 | [A statement per person: every leg, dated, with a running balance](20260909_per-counterparty-statement.md) | `iou-trackers` | medium | S | seed |  |
| IDEA-0027 | [An optional `rate:` on a loan, and the one date that matters for a family investment loan](20260909_rate-and-the-30-january-line.md) | `iou-trackers` | low | S | seed |  |

## Budget report (`budget-report`) — 4

| id | idea | lens | value | effort | status | went to |
|---|---|---|---|---|---|---|
| IDEA-0006 | [Three typographic states in the report: MEASURED, ESTIMATE, UNKNOWN](20260909_measured-estimate-unknown.md) | `review` | high | S | seed |  |
| IDEA-0009 | [The report shows the months behind every headline number](20260909_show-the-arithmetic.md) | `canadian-planners` | high | S | seed |  |
| IDEA-0010 | [Every run prints its assumptions and its out-of-scope list](20260909_print-the-assumptions.md) | `canadian-planners` | medium | S | seed |  |
| IDEA-0017 | [Export the intake-form table as a workbook a planner can open](20260909_intake-form-workbook.md) | `canadian-planners` | medium | S | seed |  |

## Privacy (`privacy`) — 1

| id | idea | lens | value | effort | status | went to |
|---|---|---|---|---|---|---|
| IDEA-0014 | [`OWL_HOME`: keep the personal files outside the repository directory altogether](20260909_personal-files-outside-the-checkout.md) | `canadian-planners` | high | S | seed |  |

## Household (`household`) — 1

| id | idea | lens | value | effort | status | went to |
|---|---|---|---|---|---|---|
| IDEA-0012 | [Two people, one budget: transfers between partners are a third kind of movement](20260909_household-mode.md) | `canadian-planners` | medium | L | seed |  |

## Planning hand-off (`planning`) — 5

| id | idea | lens | value | effort | status | went to |
|---|---|---|---|---|---|---|
| IDEA-0011 | [Emit a ratio profile — `$X` and multiples — that the planners downstream can take](20260909_a-ratio-profile-for-hand-off.md) | `canadian-planners` | high | S | seed |  |
| IDEA-0013 | [A monthly net-worth line, for free, from the closing balances every statement already carries](20260909_net-worth-from-closing-balances.md) | `canadian-planners` | medium | M | seed |  |
| IDEA-0018 | [State what the figures are and are not, on every output surface](20260909_education-not-advice-on-every-surface.md) | `canadian-planners` | medium | S | seed |  |
| IDEA-0020 | [A tax and benefit engine inside OWL Planner — retired](20260909_a-tax-engine.md) | `canadian-planners` | low | L | retired |  |
| IDEA-0028 | [Expected repayments are dated inflows in the plan, not just an outstanding balance](20260909_receivables-in-the-plan.md) | `formal-loan-record` | medium | S | seed |  |

## Onboarding (`onboarding`) — 2

| id | idea | lens | value | effort | status | went to |
|---|---|---|---|---|---|---|
| IDEA-0007 | [The first run produces a ranked question list instead of an uncategorised CSV](20260909_the-tool-asks-its-own-questions.md) | `review` | high | M | promoted | `openspec/changes/first-run-interview` |
| IDEA-0029 | [Run the engine in the browser, with nothing uploaded](20260909_run-in-the-browser.md) | `customer` | high | M | promoted | `openspec/changes/owl-web` |
