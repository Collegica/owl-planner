# What the IOU and split-expense tools record, and what they refuse to

**Answered:** 2026-09-09, by Behzad Samadi with Claude
**Mined:** IDEA-0021, IDEA-0025, IDEA-0026, IDEA-0027

The question: *the most-used tools for money between friends are not lending tools at all —
they are split-expense and IOU trackers. What do they record, in what states, and what do the
good ones deliberately leave out?* This is the lens with users behind it: two of its
repositories pass the health rule, and the commercial apps have the largest installed bases in
the category.

## Which repos count

`pixi run repo-health`, 2026-09-09:

| repo | stars | owner | age | contrib/top | commits90d | last_release | licence | pypi30d | verdict |
|---|---|---|---|---|---|---|---|---|---|
| spliit-app/spliit | 2,924 | org | 33mo | 100/39% | 100+ | 2026-09-08 | MIT | - | PASS |
| oss-apps/split-pro | 1,429 | org | 31mo | 48/45% | 32 | 2026-08-01 | MIT | - | PASS |
| SFTtech/abrechnung | 207 | org | 73mo | 28/84% | 12 | 2026-03-08 | AGPL-3.0 | - | FAIL stars,release,bus_factor |
| Marmo/debitum | 107 | use | 66mo | 9/88% | 0 | 2022-11-22 | GPL-3.0 | - | FAIL stars,active,release,bus_factor |
| michaelroudnitski/Tabs | 292 | use | 86mo | 2/99% | 0 | none | GPL-3.0 | - | FAIL stars,active,release,bus_factor |

Two pass: [Spliit](https://github.com/spliit-app/spliit) and
[split-pro](https://github.com/oss-apps/split-pro), both open-source Splitwise alternatives,
both self-hostable. [Debitum](https://github.com/Marmo/debitum) — a local-only IOU tracker
that lends *items* as well as money and explicitly refuses interest, deadlines and fees — is
**watched** for its restraint, not depended on.

The commercial apps: **Splitwise** (largest user base; built for group expenses, not
one-sided loans), **Tricount** and **Settle Up** (trip trackers with balances), and
**ExpenseSumo**, the one built for personal loans, whose method is the clearest statement of
the category: four states — *Lent, Borrowed, Paid, Received* — one account per person, each
repayment a separate entry, a running balance, "settled" when it reaches zero. Its advice:
"disputes almost always happen because no one kept a record."

## What they would keep from what we have

- **Receipts as dated legs against a named counterparty**, not a balance edited by hand:
  `loans.yml` → `receipts:` is exactly ExpenseSumo's "log each repayment as a separate entry".
- **A loan is an asset.** ExpenseSumo says it in as many words — "money other people owe you
  is still your money".
- **No online service.** Debitum's "your data is saved on your device only" and our privacy
  spec are the same sentence.

## What they would replace, and with what

- Two states (lent, received) → **four**. `loans.yml` has no way to say *someone lent me
  money*; that inflow is income today (IDEA-0021).
- "Paid for a friend, e-transfer back next week" as spending plus income → a **reimbursable**
  state, the split tools' native object (IDEA-0025).
- The lender's memory → the **per-person statement** with running balance (IDEA-0026).
- A loan with no rate → an optional `rate:` and the one date that matters for a family
  investment loan in Canada (IDEA-0027).

## What they would never do

- **Simplify debts.** Splitwise's signature feature rearranges who pays whom in a group. A
  ledger with one lender has nothing to simplify; filing it would be mistaking a mechanism for
  a need.
- **Track items.** Debitum lends drills. Out of scope, and correctly so.
- **Sync.** Every tool here that passed the health rule is self-hostable precisely because
  people did not want the hosted one. We are already on the right side of that.

## The three things they would ship first

1. The fourth state, *borrowed* (IDEA-0021) — the missing direction is a correctness bug.
2. Reimbursables (IDEA-0025) — the commonest case of money between friends is not a loan.
3. The per-person statement (IDEA-0026).

## What this lens does not see

- **Terms, schedules, arrears.** These tools are balance trackers; none knows when money is
  *due*. The formal-loan lens covers that (IDEA-0022 … IDEA-0024).
- **The plan.** No split tool cares what a receivable means for next year's cash flow
  (IDEA-0028, in the planning row).
- **Group expenses among many people.** Deliberately: OWL Planner is one household's ledger.
