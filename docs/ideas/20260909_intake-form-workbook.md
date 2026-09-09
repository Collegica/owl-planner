---
id: IDEA-0017
lens: canadian-planners
capability: budget-report
status: seed
effort: S
value: medium
promoted_to: 
---

# Export the intake-form table as a workbook a planner can open

The retirement toolkit's primary output is a multi-tab workbook; a fee-only planner's intake
form is a spreadsheet. `budget.md` is arranged in the intake form's groups and lines already,
and Markdown is the wrong format to hand across a desk.

Write `budget.xlsx` (or, without a dependency, one CSV per table) mirroring `budget.md`: the
savings section, the expense groups, monthly and annual columns, the bank-category marker as a
note. It buys the hand-off to the person the plan is for; it costs a writer and, for xlsx, an
optional dependency.
