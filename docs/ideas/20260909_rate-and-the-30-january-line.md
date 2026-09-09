---
id: IDEA-0027
lens: iou-trackers
capability: lending-ledger
status: seed
effort: S
value: low
promoted_to: 
---

# An optional `rate:` on a loan, and the one date that matters for a family investment loan

Pigeon and Chipkie compute interest against the tax authority's published rate because an
undocumented family loan can be reclassified as a gift. In Canada the analogous rule is the
prescribed-rate loan: a loan to a spouse or child for investment stays out of the attribution
rules only if interest at the CRA prescribed rate (3% through Q3 2026) is actually paid by 30
January every year — miss it once and the loan is tainted permanently. Nothing in our ledger
carries a rate; nothing can remind anyone of the date.

Add optional `rate:` and `prescribed: true` to a `lent:` entry; print accrued interest to the
window's end and, for a prescribed loan, a line naming the 30 January deadline and the amount.
It buys a real Canadian edge case for the people it applies to; it costs a rate field and a
sentence, and it stays `low` because most personal loans carry no interest at all.
