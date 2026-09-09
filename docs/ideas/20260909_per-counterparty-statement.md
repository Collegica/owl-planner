---
id: IDEA-0026
lens: iou-trackers
capability: lending-ledger
status: seed
effort: S
value: medium
promoted_to: 
---

# A statement per person: every leg, dated, with a running balance

ExpenseSumo's accounts screen, Debitum's per-person view, Chipkie's shared dashboard, and
Fineract's transaction history are one object: the record that prevents "I thought I already
paid that". Our ledger prints one summary line per counterparty. When the real sample was
built, the dates of individual legs had to be reconstructed from memory ("now I remember, on
the 28th…") because nothing printed them.

`pixi run ledger <counterparty>` prints every disbursement, receipt, write-off and
reimbursable for one person in date order with the running balance, and `budget.md` carries
the same as an appendix per counterparty. It buys the record both parties can agree on; it
costs a sort and a print.
