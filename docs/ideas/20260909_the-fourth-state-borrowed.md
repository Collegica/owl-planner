---
id: IDEA-0021
lens: iou-trackers
capability: lending-ledger
status: seed
effort: S
value: high
promoted_to: 
---

# The ledger gets its missing direction: money someone lent to you

Every IOU tracker with users carries four states — lent, borrowed, paid, received — and
ExpenseSumo builds its whole method on them. `loans.yml` has two: money out to a counterparty
and money back from one. Money *in* from a person who lent it to you has no representation,
and the classification order would land it in income (a named e-transfer) or in the review
bucket. Our own record already shows the shape of the bug: e-transfers from an employer had to
be named as income precisely because inbound e-transfers all look alike.

Add `borrowed:` entries mirroring `lent:` — counterparty, principal, repaid — with dated
receipts and repayments, and report them under LENDING as a liability alongside the assets.
It buys correctness for a common case; it costs a second sign on the same code path.
