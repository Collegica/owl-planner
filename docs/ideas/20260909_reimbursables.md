---
id: IDEA-0025
lens: iou-trackers
capability: lending-ledger
status: seed
effort: S
value: high
promoted_to: 
---

# Money paid on someone's behalf and coming back later: a reimbursable, not a loan and not spending

Spliit and split-pro have a first-class object for it — a reimbursement — because it is the
most common kind of money between friends: you pay for the tickets, they e-transfer their half
next week. Today the tool sees a purchase (spending) and an inbound e-transfer (income or
review), and the only way to correct it is two `passthrough` pins, which require the same date.
The cashback pass-through in the real sample was pinned exactly that way and worked only
because both legs cleared on one day.

Add `reimbursable:` entries — a dated outflow, the counterparty, the amount expected back —
with the receipt matched by counterparty and amount within a window. The outflow is set aside
as a receivable until the receipt arrives; the receipt is neither income nor a loan repayment;
an unmatched reimbursable after N days is listed under LENDING as owed. It buys the commonest
case; it costs a matcher that `passthrough` already half-implements.
