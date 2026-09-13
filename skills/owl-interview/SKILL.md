---
name: owl-interview
description: Interview the user about unclassified merchants; write rules.
version: 0.1.0
author: Behzad Samadi, Hermes Agent
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [finance, budget, owl, privacy]
    category: productivity
---

# OWL Interview Skill

Runs OWL Planner's own ask-your-AI loop with the user in the room. The tool
writes `ask-your-ai.md` — merchant signatures it could not classify, with a
count and a size band, and nothing else. This skill reads that file, asks the
user what each merchant is, writes the answers as a `rules.yml` fragment,
merges it with the tool's own `--merge`, and reruns until nothing is left to
ask. It never reads a statement, a ledger or a budget.

## When to Use

- The user has run `pixi run budget` (or the sample) and wants the unclassified
  merchants sorted out by answering questions rather than editing YAML.
- `/owl-interview` in a Hermes session opened in the OWL Planner checkout.
- Not for: reading or summarising the budget, editing `budget.py`, or anything
  that needs a transaction amount. Those are outside this skill on purpose.

## Prerequisites

- A Hermes session whose working directory is the OWL Planner checkout, with
  the `terminal`, `file` and `clarify` toolsets enabled. Web and browser
  toolsets should be off: a merchant name is the only personal thing this
  skill handles, and it must not leave the machine by any route other than the
  model call the user chose.
- `pixi` on the path; `pixi run budget` works.
- The user's model choice is theirs. With a cloud model the merchant names in
  `ask-your-ai.md` go to that provider — and only those. With a local model
  nothing leaves the machine.

## How to Run

```
/owl-interview                 # the user's own statements, from statements/
/owl-interview sample          # the invented household in sample/ — safe to demo
```

## Quick Reference

| Step | Tool | What |
|---|---|---|
| 1 | `terminal` | `pixi run budget` (or `pixi run sample`) |
| 2 | `read_file` | `ask-your-ai.md` (or `sample/ask-your-ai.md`) |
| 3 | `clarify` | One batch of questions per run, largest merchants first |
| 4 | `write_file` | `answer.yml` in the rule format the pack shows |
| 5 | `terminal` | `pixi run budget -- --merge answer.yml` |
| 6 | `read_file` | `ask-your-ai.md` again; stop when it says nothing to ask |

## Procedure

1. **Run the tool.** `pixi run budget` for the user's statements, or
   `pixi run sample` when the argument is `sample`. Report only the last line
   the tool prints about `ask-your-ai.md` — how many merchants there are to
   ask about. Do not repeat any other output.
2. **Read the pack** with `read_file`: `ask-your-ai.md` at the checkout root,
   or `sample/ask-your-ai.md` for the sample. It lists the budget lines, the
   rule format, and the merchants in descending order of money, without the
   money. Read all of it; the budget lines are the only lines you may use.
3. **Ask, do not guess.** Call `clarify` once with a batch of questions — the
   first merchants in the pack, up to the batch limit — one question per
   merchant. Each question is the signature as printed plus its count and size
   band, for example *"newtown dental — 3 times, ~$200 each. What is it?"*.
   Offer choices, recommended first: your best reading of the budget line,
   then the other plausible lines, then `Transfer between my accounts`,
   `Income`, `Don't know`. Never write an option into the question text.
4. **Write the fragment.** From the answers, write `answer.yml` with
   `write_file` in exactly the shape the pack's "Rule format" shows:
   `categories:` for budget lines, `transfers:` for money between the user's
   own accounts, `income:` for payroll and refunds, `unsure:` for `Don't
   know` and for anything you would have had to guess. The pattern is the
   signature's words, lower-case, as a case-insensitive regular expression;
   escape anything that is not a letter, digit or space. A line name must
   match the pack's list exactly, including capitals.
5. **Merge and rerun.** `pixi run budget -- --merge answer.yml` (with
   `--dir sample/statements --config sample --out sample/budget.md` for the
   sample). The tool appends to the personal `rules.yml`, touches nothing
   already there, and refuses a fragment that names a line not in
   `categories.yml` — if it refuses, fix the name and merge again; never edit
   `rules.yml` directly.
6. **Loop.** Read `ask-your-ai.md` again. If merchants remain, go to step 3
   with the next batch. If it says nothing to ask, say how many merchants were
   classified in total, and stop.
7. **Hand over.** Tell the user the budget is in `budget.md` and that the
   browser page at collegica.org/owl shows the same figures. Do not read
   `budget.md` yourself.

## Pitfalls

- **Amounts.** The pack carries none, and neither may you: never open
  `statements/`, `ledger.csv`, `uncategorised.csv` or `budget.md`. If the user
  pastes a transaction, answer from the merchant name only.
- **Guessing.** A wrong rule silently misclassifies every future transaction
  from that merchant. `unsure:` is the correct answer whenever you are not.
- **Chained clarify calls.** One batch, then write, then merge. Do not ask one
  question per call.
- **Editing rules.yml.** Only `--merge` writes to it. It preserves the user's
  comments byte for byte; you would not.
- **The sample.** `pixi run sample` writes into `sample/`, which is tracked in
  git. Merging into `sample/rules.yml` changes a tracked file; tell the user,
  and do not commit it.

## Verification

- After the last merge, `ask-your-ai.md` says there is nothing to ask, or
  lists only merchants the user answered `Don't know` to.
- `git status --ignored` still shows `rules.yml` and `statements/` as
  ignored, and `git status` shows no new tracked file with a merchant name in
  it (other than `sample/` if the sample was used).
- Every line name in `answer.yml` appears in the pack's "Budget lines".
