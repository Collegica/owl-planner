---
id: IDEA-0003
lens: data
capability: recurring-baseline
status: seed
effort: S
value: medium
promoted_to: 
---

# Notice a month-end payment that wobbles across the boundary, and suggest `level`

The monthly spread first read 57%–134% of the median. All of it was one obligation paid on the
last day of the month, sometimes clearing on the 1st or 2nd, and split by the $3,000 e-transfer
cap. The person had to diagnose that by listing the dates by hand.

A signature that recurs in most months with payment days clustered at 28–31 and 1–3 is a
wobble by construction. Detect it and print one line: *"'withdrawal interac' looks like a
month-end obligation split across the boundary — consider `level:`"*. It buys a fix the reader
can apply in a minute instead of an hour of forensics; it costs a small heuristic that must not
fire on genuinely irregular payments.
