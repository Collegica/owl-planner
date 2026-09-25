---
id: IDEA-0033
lens: review
capability: recurring-baseline
status: seed
effort: S
value: medium
promoted_to: 
---

# A levelled payment that clears just after the window is dropped, understating the rate

`level:` charges an obligation at its monthly rate: the payments that cleared inside the
complete months, divided by the number of complete months. On the sample household the
support payment is $950 a month, made on the last day of the month, and the last one cleared
on 2 September — after August, the last complete month. It is not counted, so the report
prints **$831/month** (7 payments over 8 months) for an obligation that is $950 every month,
and RECURRING is about $1,400 a year low. Two independent agents, asked to follow the
article's method on the same files, both got $950 and flagged the difference.

The obvious fix — count a payment that clears in the first few days of a month toward the
previous month — repairs a month-end payer but breaks one that pays on the 3rd: its first
payment would move out of the window and the rate would drop the same way. The statements do
not say which month a payment is for. Options worth weighing in a proposal: count by *payment
periods observed* (payments ÷ distinct months they fall due) rather than by window; use the
median payment as the rate when the count is within one of the months; or print both figures
and ask, the way irregular items are asked, and record the answer with `level:`.

Cost is small either way; the value is that the one number the tool exists for stops being
low by the size of one payment, silently. Related: IDEA-0003 (detecting the wobble at all).
