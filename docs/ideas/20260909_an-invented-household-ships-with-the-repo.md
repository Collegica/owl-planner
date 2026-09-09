---
id: IDEA-0008
lens: canadian-planners
capability: statement-import
status: promoted
effort: M
value: high
promoted_to: openspec/changes/sample-household
---

# Ship an invented household: sample statements so a fresh clone produces a complete budget

FUNDerelele loads a sample of five accounts and five years on request; the retirement toolkit
onboards with two fictional households, one per tax regime. Both let a stranger see the whole
tool working before they trust it with their own files. A fresh clone of OWL Planner today
categorises about half of an invented sample with the example rules and produces a budget with
holes in it — and there are no tests, because there is nothing to test against.

Author eight months of statements for a fictional household across a chequing account, two
cards and a line of credit — every kind of money movement present, every rule section
exercised — in the three-column CSV shape, plus a matching `rules.example.yml`. `pixi run
budget --sample` runs on it; CI asserts its headline figures. It buys a demonstration, a test
fixture and a safe example for the article in one artefact; it costs a day of invention.
