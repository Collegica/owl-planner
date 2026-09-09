---
id: IDEA-0004
lens: incident
capability: money-classification
status: seed
effort: S
value: medium
promoted_to: 
---

# A pin that matches no transaction is reported, not silently ignored

A `one_off` entry was written with a guessed amount (7654.32 for a charge of 7653.99). Nothing
matched, nothing warned, and the item stayed in the IRREGULAR list as if the pin did not exist.
The same silence applies to `dated`, `passthrough`, `disbursements` and `receipts`.

After classification, list every pin that matched zero transactions, with the nearest
transaction by date and amount. It buys trust in the pins — the reader learns that a pin is
either working or reported; it costs a pass over the pin tables.
