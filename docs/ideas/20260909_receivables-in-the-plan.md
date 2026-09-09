---
id: IDEA-0028
lens: formal-loan-record
capability: planning
status: seed
effort: S
value: medium
promoted_to: 
---

# Expected repayments are dated inflows in the plan, not just an outstanding balance

A bank's schedule is a cash-flow forecast; so is a friend's promise to pay $1,000 a month. The
ratio profile (IDEA-0011) would carry "loans outstanding 0.2X" and stop, which is a balance
sheet fact with no time on it. With terms on the book (IDEA-0022), the same data is a set of
dated expected inflows.

Emit them in `owl-profile.yml` as `receivables: [{due, amount_x}]` and, in the LENDING block,
"expected back within 12 months". It buys the second number a plan needs about a loan — when,
not just how much; it costs nothing beyond IDEA-0022.
