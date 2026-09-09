---
id: IDEA-0023
lens: formal-loan-record
capability: lending-ledger
status: seed
effort: S
value: medium
promoted_to: 
---

# Show the repayment schedule against what actually arrived

Zirtue and Chipkie put a shared dashboard in front of both parties: upcoming payments, payment
history, balance. Fineract's schedule is the same object for an institution. Given terms on the
book (IDEA-0022), the tool already holds everything needed to print the schedule with each
instalment marked received, partial, or missed, and a running balance.

Print it under LENDING for any loan with a schedule, and in `budget.md` as a small table per
counterparty. It buys the shared record without a shared service — the lender can hand the
table to the borrower; it costs rendering. It depends on IDEA-0022.
