---
id: IDEA-0014
lens: canadian-planners
capability: privacy
status: seed
effort: S
value: high
promoted_to: 
---

# `OWL_HOME`: keep the personal files outside the repository directory altogether

The retirement toolkit reads its one personal config from a path an environment variable can
override (`RPT_CONFIG`) and states "no personal data is in any script"; FUNDerelele keeps its
database under `instance/`, outside the source. OWL Planner relies on `.gitignore` — and the
day it was extracted from the website repo, the personal files had been committed for
twenty-four local commits before anyone noticed. A gitignore is one `git add -f` from failure.

Read `rules.yml`, `loans.yml`, `known-annual.yml` and `statements/` from `$OWL_HOME` (default
`~/.owl/`) when it is set, falling back to the repo directory. It buys a layout where the
personal files cannot be committed by accident because they are not in the tree; it costs
one path resolution and a line in the README.
