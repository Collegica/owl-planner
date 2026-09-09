# OWL Planner

Tools for the [OWL framework](https://www.collegica.org/aging-well/ai-planning/)
— Optimal Wealth and Longevity. The first one measures what a year costs
you: it turns a folder of bank exports into the annual spending figure every
financial plan starts with, and a budget broken down the way a planner's
intake form expects it.

```bash
git clone https://github.com/Collegica/owl-planner
cd owl-planner
pixi run budget          # after dropping your CSV exports in statements/
```

Requires [pixi](https://pixi.sh); it fetches Python, PyYAML and poppler and
nothing else. No accounts, no API keys, no network after install.

Everything runs on this machine. Nothing is uploaded and no credentials are
involved: you export the CSVs yourself. Your statements and the budget they
produce are gitignored.

## 1. Export the statements

In online banking, for **every account you spend from** — chequing, each credit
card, any line of credit — export the last 12 months as CSV and drop the files
in `statements/`.

Filenames do not matter. Formats do not need to match: the tool reads each file
on its own terms.

If a bank only offers PDF statements, `pdf_import.py` turns them into the same
CSV shape — and refuses any statement it cannot reconcile against the totals
printed on the statement itself. That check is what lets you trust the numbers
downstream: a parsing bug and a real transaction look identical until you have
a figure the bank itself asserts to compare against.

**Export the credit cards, not just the chequing account.** If you only export
chequing, your spending looks like a handful of card payments and you learn
nothing about where the money went.

## 2. Run it

```bash
pixi run budget
```

That writes `budget.md` and prints the headline:

```
files 4   transactions 565   duplicates dropped 0
categorised 98% of spending
observed 2026-01-01 to 2026-08-31  (8 complete month(s))

RECURRING   $4,150/month   ->  $49,800/year
            months ranged $3,720-$4,520 (90%-109% of median); steady
```

(The figures in this document are illustrative, not anyone's.)

Useful flags: `--year 2026` to restrict to one calendar year, `--dir` to read
from somewhere else, `--date-order dmy|mdy` for the ambiguous-date case below.

## 3. Triage what it could not categorise

Anything unmatched goes to `uncategorised.csv`, sorted by amount — largest
first, because that is the order worth working in. Add a pattern to
`rules.yml` for the top few and run again. Ten minutes of this usually gets
coverage past 90%.

```yaml
categories:
  Groceries: ['loblaw', 'metro\b', 'your local shop']
```

`rules.yml` is yours and gitignored — it names your employer, your
counterparties, and the dates and amounts of things only you can classify.
Copy `rules.example.yml` to start it. Keep it under your own version control
if you like; it should never land in a shared repository.

## How much data you need

**A few months is enough for the part that matters.** Recurring spending —
groceries, fuel, restaurants, subscriptions, transit — settles down after two
or three complete months. On a real eight-month sample the monthly baseline
stayed within ±10% of its median: enough to plan on.

**A full year does not fix the rest, and waiting for one is not the answer.**
Irregular items are events, not averages. An insurance renewal, property tax, a
holiday, a car — you either observed it in your window or you did not, and
twelve months only means you got luckier. In that same sample, a single car
repair was close to a full month of everything else. Averaged into a monthly
figure it would have added a month and a half of imaginary spending to the
year; ignored, it would have hidden a real expense.

So the tool splits them:

- **Recurring** — the median complete month, annualised. Stable, measured.
- **Irregular** — anything at or above `--lumpy` (default $1,000) is listed
  individually and never averaged. For each one you decide: one-off, yearly, or
  the start of a monthly payment.
- **Known yearly** — `known-annual.yml`, for the things you know you pay and
  simply did not observe. State them rather than infer them. This is what a
  planner's intake form does, and it is why the form asks for annual insurance
  and tax figures instead of guessing them from a bank feed.

The planning figure is recurring + known yearly, with the irregular items in
front of you as decisions rather than folded silently into an average.

## What it handles, and why

**Different CSV shapes.** Separate Debit/Credit columns or one signed Amount;
comma, semicolon or tab; with or without a header row; UTF-8, CP1252 or
Latin-1; `1,234.56` or `1 234,56`.

**Only one of six kinds of money movement is spending.** Money leaves an
account for many reasons, and a bank feed shows them all the same way. The
tool tells them apart, and prints what it set aside so nothing disappears
silently:

| What it is | Why it is not spending | Where you declare it |
|---|---|---|
| Transfer between your own accounts | The card *payment* is not spending; the card *purchases* already are. Counting both doubles every dollar on the card. | `rules.yml` → `transfers` |
| Money lent out | An asset, unsecured. Not spending going out, not income coming back. | `loans.yml` |
| Savings contribution | It moves money, it does not consume it. | `rules.yml` → the savings lines in `categories.yml` |
| Pass-through | A rebate received and forwarded the same day is neither income nor spending. | `rules.yml` → `passthrough` |
| Income | Named, because e-transfers from an employer look like any other e-transfer. | `rules.yml` → `income` |
| Spending | What is left — and what the annual figure measures. | `rules.yml` → `categories` |

On a real eight-month sample, every one of the first five was counted as
spending at some point during development. The recurring figure fell by
about 7% between the first run and the last — and almost the whole gap was
classification, not arithmetic.

**Calendar artefacts are not behaviour.** A payment made on the last day of
the month sometimes clears on the 1st, and a $3,000 e-transfer cap splits a
larger payment into pieces that straddle the boundary. Bucketed by clearing
date, three months looked empty and three looked double, and the monthly
spread read 57%–134% of the median when the spending was steady. An obligation
listed under `level:` in `rules.yml` is charged at its monthly rate instead —
what was actually paid, divided by the months observed. This is a fix for a
calendar artefact, not a way to smooth real variation, which is why it refuses
to level anything with fewer than three payments.

**Decisions are recorded, not repeated.** An irregular item you have judged
one-time goes under `one_off:` with the reason; a transaction only you can
classify goes under `dated:`, pinned to date and amount so nothing else is
swept up. The tool then reports them as decided rather than asking again.

**Duplicates across overlapping exports** are dropped, and the count reported.

**Ambiguous dates are not guessed.** `01/07/2026` is 7 January at one bank and
1 July at another. The tool infers the convention per file — a day past the
12th in the first position proves day-first — and when a file contains no such
day it says so and asks, rather than silently turning seven weeks into ten
months. (It did exactly that during development, which is why it now asks.)

## The files

Nothing about any particular person lives in the code. Everything personal is
data, in four files that are meant to be version-controlled:

- `rules.yml` — how descriptions map to transfers, income, categories; the
  levelled, pass-through, dated and one-off entries, each with a `note:`
  saying why.
- `loans.yml` — who you have lent to, what came back, and the legs that fall
  outside the exported window.
- `categories.yml` — the budget lines, grouped the way a planner's intake
  form groups them, with savings kept separate from expenses.
- `known-annual.yml` — the yearly items you know about but did not observe.

## What building it taught

The tool was developed against one person's real accounts, and every wrong
number it produced along the way came from the same place. Worth writing down,
because it is the design of the thing.

**The hard problem is taxonomy, not summation.** The tool was never bad at
adding up. It was bad at knowing what a transaction *was*. "Money left the
account" is easy to detect; "money was consumed" is the question, and most
budgeting tools quietly answer the first while claiming the second.

**Almost nothing that mattered was in the statements.** That a large cheque
was a loan to a friend; that a series of e-transfers was a family obligation;
that a monthly fund purchase was savings — none of that is inferable, and
every attempt to infer it was wrong. Lending inferred from an e-transfer
pattern came to more than twice what had actually been lent. The tool's skill has to be
asking well, not guessing well: surface what it cannot classify, ranked by
dollars, and turn each answer into a durable rule with the reason attached.

**Reconciliation is what separates parsing from knowing.** Thirty-two
statements, each checked against the total the bank printed. Without that
there is no way to tell a regex bug from a real transaction — and there were
several: a stripped leading minus sign that turned a refund into a charge;
column offsets read once instead of per page that overstated one month's
withdrawals more than threefold.

**An extrapolation printed like a measurement is a lie.** The first version
announced an annual figure from seven weeks of data. Complete months only;
the median rather than the mean; the spread stated; lumpy items held out and
listed rather than smeared across the year. The tool should be willing to say
"not enough data to give you that" — it is a better answer than a confident
one.

**Variance in the bookkeeping looks exactly like variance in the life.** A
tool that reports a swing has to be able to say whether the world moved or
the calendar did. False alarms are why people stop using budgeting tools.

**Load everything before concluding anything.** With only the credit cards
imported, card payments looked like spending with no income behind them and
the loans looked like a large unexplained hole. Partial data does not produce partial
conclusions; it produces confident wrong ones.

## Making it work for someone else

The load-bearing decision is already made: the code is generic and the
knowledge is data. Keep it that way absolutely. What is still missing is the
part that was done by hand during development — the interview:

1. **First run should produce questions, not a budget.** A ranked list —
   "these descriptions account for 78% of unclassified money; what is each?" —
   with each answer written straight into `rules.yml`. Rank by dollars, never
   by count: one $10,000 line outranks seventeen small ones.
2. **Every number should answer "why".** Provenance per classification — you
   said so, the bank's own category, or a pattern match — so any figure in the
   budget can be traced to the rule that produced it.
3. **Three states, not one.** MEASURED, ESTIMATE, UNKNOWN as first-class
   outputs, typographically distinct.
4. **A verified import layer over a plain CSV waist.** Anyone can hand-write
   the normalised CSV; extractors are a convenience above it that must
   reconcile or decline to run. That is also what makes a new bank safe for a
   stranger to contribute.

What does not generalise yet: joint finances, where transfers between
partners are neither spending nor lending; irregular self-employment income;
and a fair amount of Canadian specificity — the $3,000 e-transfer cap is not
a law of nature.

And the constraint that is not technical: this only works if someone is
willing to answer questions about family obligations, money lent to friends,
and what they actually earn. The tool has to ask neutrally and record the answer
without comment. That is a design requirement, not a courtesy — it is the
difference between a tool people finish setting up and one they close.

## Changing it

Behaviour is specified before it is built. `openspec/specs/` describes what the
tool does today, one file per capability; `openspec/changes/` holds proposals
that have not landed. To propose something, run `pixi run openspec new change <name>`
(or `/opsx:propose` in Claude Code, from inside `pixi shell`) and fill in the
proposal, spec delta, design and tasks; `pixi run specs` checks the lot. The
OpenSpec CLI comes from conda-forge with everything else — nothing to install
separately. The first open
change, `first-run-interview`, is the tool asking its own questions instead of
leaving you a CSV.

## Then what

The tool is written up — the file formats, an illustrative run, the core of
the computation, and the prompts to use on its output — in [A Year of
Spending, from Your Own
Statements](https://www.collegica.org/aging-well/budget-from-statements/).

The number this produces is step 1 of the funds plan in
[Planning to Age Well, with AI](https://www.collegica.org/aging-well/ai-planning/):
*measure what a year costs you — twelve months of actual spending, not an
estimate.* Everything downstream is a multiple of it.

If you want an AI's help interpreting the result, translate it to ratios
first — the article's "Giving an AI your numbers" section explains how, and
`budget.md` is already aggregated, with no account numbers in it.
