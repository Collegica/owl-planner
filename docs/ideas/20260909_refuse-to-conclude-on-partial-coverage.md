---
id: IDEA-0005
lens: customer
capability: statement-import
status: seed
effort: S
value: high
promoted_to: 
---

# Detect a card paid from chequing whose own export is missing, and say so before reporting

"You were supposed to import everything." With only the credit cards loaded, card payments
looked like spending with no income behind them and the loans looked like a large hole. Every
conclusion drawn from the partial set was wrong, and confidently so.

A chequing export that contains payments to a card, with no export whose transactions those
payments settle, is provably incomplete. Detect it from the transfer patterns and print a
coverage warning naming the missing account before any figure. It buys the single most
important guard against a wrong budget; it costs matching payment descriptions to account
names, which the transfer rules already do.
