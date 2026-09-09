---
id: IDEA-0013
lens: canadian-planners
capability: planning
status: seed
effort: M
value: medium
promoted_to: 
---

# A monthly net-worth line, for free, from the closing balances every statement already carries

FUNDerelele tracks the asset side that OWL Planner ignores; the toolkit's first tab is net
worth. Every PDF statement the reconciler accepts prints a closing balance — `pdf_import.py`
already reads it for the RBC and Scotia layouts to derive sign from the balance delta — and
then throws it away.

Keep the closing balance per statement, sum across accounts per month (liabilities negative),
and print one NET POSITION line with the change over the window. It buys the second number a
plan needs after `$X`; it costs carrying balances through the CSV (an optional fourth column)
and deciding what to do when one account's statement is missing for a month.
