---
id: IDEA-0012
lens: canadian-planners
capability: household
status: seed
effort: L
value: medium
promoted_to: 
---

# Two people, one budget: transfers between partners are a third kind of movement

Retire, Eh? is household-first — "one household balance sheet, multiple tax wrappers" — and
the toolkit models two spouses with independent claim ages. OWL Planner models one person: the
"own accounts" set is one person's, and a transfer to a partner is currently either spending
or, if pinned, lending. The lending ledger already had to model a counterparty who is neither
an account nor a merchant; a partner is that case with the arrow pointing both ways.

Let `rules.yml` declare a household: each person's accounts, and transfers between them set
aside as neither spending nor lending, with income and savings reported per person and in
total. It buys the tool for couples, which is most households; it costs a real change to the
classification model and to every report section, hence L.
