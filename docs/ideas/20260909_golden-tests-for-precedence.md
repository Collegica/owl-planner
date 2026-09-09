---
id: IDEA-0016
lens: canadian-planners
capability: money-classification
status: seed
effort: M
value: high
promoted_to: 
---

# Golden tests for the classification order, on an invented CSV

Arrive Finance keeps its eligibility rules in a tested engine because the edge cases are the
product. OWL Planner's classification precedence — pin, counterparty, transfer, income, pin,
category, savings, bank fallback, review, uncategorised — is the part that has been wrong most
often: the review bucket once ran before category matching and swallowed a whole budget line;
a pattern once outranked a dated pin.

One invented CSV per precedence edge (a pinned loan that matches a support pattern; an
e-transfer above `review_min` that matches a category; a savings pattern that also matches a
transfer) and an assertion per row on the kind it lands in. It buys a fence around the most
fragile logic in the tool; it costs writing the cases, which the specs already describe as
scenarios.
