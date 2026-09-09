---
id: IDEA-0022
lens: formal-loan-record
capability: lending-ledger
status: seed
effort: S
value: high
promoted_to: 
---

# Terms on the book: when it was lent, when it is due, and how many days late it is

Apache Fineract's loan account is, at its core, a schedule and an arrears age; every
friends-and-family app sells the same two things as "clear terms" and "reminders". Our ledger
prints an outstanding balance with no date on it. Two loans outstanding in the real sample are
reported identically whether they are on schedule or eighteen months overdue, and the phrase
the tool uses — "unsecured and earning nothing" — is the only warning it can give.

Add optional `lent_on`, `due`, and either `monthly` or `schedule:` to a `lent:` entry. The
LENDING block then prints, per loan, expected-to-date, received, and days past due after a
grace period, and the summary line separates current from late. It buys the difference between
an asset and a problem; it costs a date arithmetic that `complete_months()` mostly has.
