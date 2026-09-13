# OWL Planner — instructions for agents working in this checkout

You are in a tool that reads a person's bank statements. Everything under
`statements/`, and the files `rules.yml`, `loans.yml`, `known-annual.yml`,
`ledger.csv`, `uncategorised.csv` and `budget.md` at this root, describe a
real person's money. **Do not read, print, summarise or quote them**, and do
not put anything from them into a file that git tracks. `git status --ignored`
lists what is ignored; that list is the boundary.

The one file about the user's money you may read is `ask-your-ai.md`. It is
written to be read by an AI: merchant names, how often each appeared, a size
band — no amounts, dates, accounts or names of people. The skill
`owl-interview` (in `skills/`) is the supported way to act on it.

The invented household in `sample/` is safe to read and to demonstrate with.
`pixi run sample` runs the tool on it.

Working here as a developer: `CLAUDE.md` has the conventions (OpenSpec for
behaviour changes, ideas in `docs/ideas/`, British spelling, no marketing).
