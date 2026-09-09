# What a loan record contains when somebody's job depends on it

**Answered:** 2026-09-09, by Behzad Samadi with Claude
**Mined:** IDEA-0022, IDEA-0023, IDEA-0024, IDEA-0026, IDEA-0028

The question: *what does a loan record hold in systems that collect on loans for a living — a
core-banking platform and the apps that formalise loans between friends — and which of those
fields does a personal ledger actually need?* Our `loans.yml` holds a principal, a repaid
total, and dated legs. Everything else — when it was due, whether it is late, whether it is
still expected — lives in the lender's memory.

## Which repos count

`pixi run repo-health`, 2026-09-09. One repository in this space passes the rule; it is the
only open lending system with a track record, and it is a bank's.

| repo | stars | owner | age | contrib/top | commits90d | last_release | licence | pypi30d | verdict |
|---|---|---|---|---|---|---|---|---|---|
| apache/fineract | 2,467 | org | 130mo | 100/14% | 100+ | 2026-07-14 | Apache-2.0 | - | PASS |
| chandachewe10/loan-management-system | 148 | use | 58mo | 6/97% | 0 | none | NOASSERTION | - | FAIL stars,active,release,bus_factor,licence |
| bertvandepoel/tabby | 74 | use | 90mo | 2/98% | 0 | 2022-01-15 | AGPL-3.0 | - | FAIL stars,active,release,bus_factor |

The commercial apps in this lens — [Zirtue](https://www.zirtue.com/lend),
[Pigeon](https://www.producthunt.com/products/pigeon-7),
[Chipkie](https://chipkie.com/blog/2026/07/29/family-loan-app/) — are companies, not repos,
and are read the company-lens way: for the specific move they make, with our own record as the
second witness on every idea.

## What the sources hold that we do not

**Apache Fineract** (the reference model for a loan account): a *product* with terms; a
*repayment schedule* — expected instalments by date; *arrears ageing* — days past due,
with a grace parameter before a loan counts as late; *reschedule* and *refinance* as recorded
events; *write-off* as a state with a date and a reason, not a deletion; interest
recalculated on the outstanding balance. The ledger has none of these fields; it cannot say
whether an outstanding balance is on track, late, or quietly abandoned.

**Zirtue / Pigeon / Chipkie** (loans between people, formalised): a written agreement with
principal, term, rate and default terms; a schedule; *reminders before and after due dates* —
sold explicitly as removing the awkward conversation from the relationship; a *shared record*
both parties can see; interest referenced to the tax authority's published rate (AFR in the
US; the CRA prescribed rate here — 3% through Q3 2026, interest payable by 30 January to keep
a family investment loan out of the attribution rules); insurance and autopay on the
commercial tier. Chipkie's stated failure modes for undocumented loans: reclassified as a
gift, unprovable, statute of limitations never starts, "I thought I already paid that".

## What they would keep from what we have

- **Lending is an asset, not spending, and repayment is not income.**
  `openspec/specs/lending-ledger/spec.md` states it as a requirement; the LENDING block prints
  "an asset, but unsecured and earning nothing". Fineract would recognise the accounting.
- **The book, not the pattern.** Outstanding is `principal − repaid` from `lent:`, never
  inferred from an e-transfer pattern — after inference overstated lending more than twofold.
  Every source here starts from a declared loan; so do we.
- **Legs outside the window are named.** A receipt dated after the last statement is printed
  as "outside the exported window" rather than dropped. The reconciliation instinct applied to
  the ledger.

## What they would replace, and with what

- `principal` + `repaid` → terms on the book: dates, an expected schedule, and days past due
  (IDEA-0022), with expected-to-date against received (IDEA-0023).
- An outstanding balance that can only grow smaller → a recorded write-off, dated and
  reasoned, which turns the remainder into a one-off gift in the budget (IDEA-0024).
- A lender's memory → a per-counterparty statement: every leg, running balance, the record
  that stops the dispute (IDEA-0026, filed under the IOU lens; both lenses arrive at it).
- Loans invisible to the plan → expected repayments as dated inflows in the ratio profile
  (IDEA-0028).
- An undocumented family investment loan → a `rate:` field and a 30 January line
  (IDEA-0027, filed with the IOU lens's evidence).

## What they would never do

- **Move money.** Autopay, direct bill pay, e-signatures, insurance are the commercial tier's
  business. The ledger records; it does not collect. No idea filed — it is the premise.
- **Interest recalculation as a feature.** Fineract's daily-interest engine is for a bank. A
  personal loan has a rate or it does not; one field, one line a year.

## The three things they would ship first

1. Terms and days-past-due (IDEA-0022) — the difference between "$X outstanding" and
   "$X outstanding, of which $Y is 90 days late".
2. Write-off as a state (IDEA-0024) — the only honest exit for a loan that will not come back.
3. The per-counterparty statement (IDEA-0026) — the record every source agrees prevents the
   quarrel.

## What this lens does not see

- **Money going the other way.** A bank is always the lender. Nothing here covers money
  *borrowed* from a person, which today would be counted as income. The IOU lens sees it
  (IDEA-0021).
- **Money paid on someone's behalf.** Reimbursables are not loans in a bank's model; the
  split-expense tools have the word for it (IDEA-0025).
- **Whether any of this is worth it for two loans.** A personal ledger with two counterparties
  does not need arrears ageing; the ideas are filed at `S` on purpose and should stay simple.
