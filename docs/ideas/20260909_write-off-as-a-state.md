---
id: IDEA-0024
lens: formal-loan-record
capability: lending-ledger
status: seed
effort: S
value: medium
promoted_to: 
---

# A loan you decide not to collect is written off — dated, reasoned, and moved to the budget

Fineract keeps write-off as a state with a date and a reason, never a deletion; LENS keeps a
retired idea for the same reason. Our ledger's outstanding balance can only fall by receipts,
so a loan that will not come back stays an asset forever, quietly inflating the "outstanding"
line the plan rests on.

Add `written_off: {date, amount, reason}` to a `lent:` entry. The written-off amount leaves the
asset column and enters the budget as a dated one-off (a gift, in the intake form's terms) in
the month it was decided — not the month it was lent. It buys an honest balance sheet and an
honest exit; it costs one more pin shape, and the courage to use it.
