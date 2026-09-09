---
id: IDEA-0006
lens: review
capability: budget-report
status: promoted
effort: S
value: high
promoted_to: openspec/changes/trust-the-number
---

# Three typographic states in the report: MEASURED, ESTIMATE, UNKNOWN

"Is that an estimate? You don't have the whole year." The first headline was an annual figure
extrapolated from seven weeks, printed like a measurement. Complete months, the median and the
stability line fixed the arithmetic; the *report* still prints every number the same way.

Give `budget.md` and the console three visibly different states and refuse to print an annual
figure at all below three complete months — say what can be said instead. It buys the reader's
ability to tell what they are looking at without reading the method; it costs a rendering pass
and the discipline to leave a cell empty.
