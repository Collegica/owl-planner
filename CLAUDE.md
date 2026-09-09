# OWL Planner — working notes for agents

- Specs and changes live in `openspec/`; `openspec/config.yaml` carries the project context and the rules that are not negotiable. Read it first. Use `/opsx:propose` for anything that changes behaviour, `/opsx:apply` to implement, `/opsx:archive` when done. The `openspec` CLI is a pixi dependency: run it as `pixi run openspec ...`, or start the session from `pixi shell` so the `/opsx:*` commands find it.
- Never commit, print or paste anything from `statements/`, `rules.yml`, `loans.yml`, `known-annual.yml`, `budget.md` or `uncategorised.csv`. They describe a real person's money and are gitignored for that reason. Docs use invented figures only.
- `pixi run budget` before and after a change; report any movement in RECURRING, categorised %, or SET ASIDE.
