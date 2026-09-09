---
id: IDEA-0010
lens: canadian-planners
capability: budget-report
status: seed
effort: S
value: medium
promoted_to: 
---

# Every run prints its assumptions and its out-of-scope list

Retire, Eh? opens with "conservative assumptions" and closes with an explicit out-of-scope list
(no bank integrations, no Monte Carlo, no early-retirement advocacy). OWL Planner's knobs —
the irregular threshold, the three-payment guard on levelling, the 75%–135% steady band, the
complete-month rule — live in code and in the handbook, not in the output.

Print an ASSUMPTIONS block at the end of every run with the knob values and one line each on
what the tool deliberately does not do. It buys a reader who knows what they are holding; it
costs nothing but the discipline to keep the block honest when a knob changes.
