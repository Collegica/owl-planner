---
id: IDEA-0001
lens: data
capability: money-classification
status: seed
effort: M
value: high
promoted_to: 
---

# Every figure in the budget can say which rule produced it

Over the first week of development on real accounts, the recurring baseline moved by about 7%
with no change to the arithmetic — every point of it was a transaction changing kind:
transfer, lending, savings, pass-through. At no point could the output say *which* rule had
put a given dollar where it was; the only way to find out was to re-read `budget.py`.

Carry provenance on every classified transaction — `you said so (rules.yml:transfers)`,
`bank category`, `pattern 'costco'`, `pinned 2026-05-20` — and let `budget.md` show, per line,
how much rests on each kind of evidence. It buys the ability to ask any number "why?"; it
costs a field on the transaction tuple and a column in the report.
