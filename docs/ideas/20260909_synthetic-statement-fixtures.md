---
id: IDEA-0002
lens: incident
capability: pdf-reconciliation
status: promoted
effort: M
value: high
promoted_to: openspec/changes/pdf-in-browser
---

# A regression suite of invented statements, one per bug the reconciler has caught

Three parsing bugs reached a number before reconciliation refused them: a leading minus
stripped by `.strip('()-')` turned a refund into a charge; column offsets read once instead of
per page overstated one month's withdrawals threefold; a December line on a January statement
took the January year. Each was found by a statement failing to reconcile — none by a test.

Write one small invented PDF (or `pdftotext -layout` text) per bank layout, each carrying the
shape of one caught bug, and run the extractors against them in CI with reconciliation as the
assertion. It buys the reconciler's judgement without a real statement; it costs authoring the
fixtures so they contain no real person's data.
