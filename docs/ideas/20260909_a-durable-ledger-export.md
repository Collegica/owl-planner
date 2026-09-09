---
id: IDEA-0015
lens: canadian-planners
capability: statement-import
status: seed
effort: S
value: medium
promoted_to: 
---

# One normalised, classified, re-importable ledger that outlives any bank's export window

FUNDerelele exports its transactions as a CSV it can re-import, and backs up its database
whole. OWL Planner reads whatever exports exist and forgets them; banks limit how far back an
export reaches, and two loan repayments in the real sample fell outside the exported window
and had to be recorded by hand in `loans.yml`.

`pixi run export` writes `ledger.csv`: every transaction after dedupe with its classification
and provenance, in the three-column shape plus a `kind` column. The next run reads the ledger
alongside new exports, so the window only ever grows. It buys a multi-year record from
short-window exports; it costs a merge on (date, description, amount) that dedupe already does.
