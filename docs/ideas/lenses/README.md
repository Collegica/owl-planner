# Lenses

One file per question, answered once, thoroughly, and mined for ideas. A lens is not an idea:
it is the argument that produces several. Write the lens, then write each idea it yields as
its own `ideas/<date>_<slug>.md` with `lens: <this file's slug>`.

## Candidate lenses

Group them by the question they ask; several companies usually ask the same one.

| question | candidate lenses |
|---|---|
| how the system tells the truth about what it knows | an AI lab (evals, calibration, refusing rather than degrading) |
| what the buyer requires before a pilot becomes a contract | the enterprise vendor (identity, audit, compliance, the surfaces people already use) |
| where the model of the world comes from | the GIS vendor (drawn), the reconstruction company (recovered from imagery), the simulation company (simulated), the physical-AI company (learned) |
| what the evidence is | the measurement company (a number on a surface), the capture company (intent recorded, change over time) |
| who does the work | the robotics company (a mission as the unit of evidence), the direct competitor (what a buyer compares against) |
| what the most-used open repositories in our space do that we do not | GitHub topics adjacent to the product, filtered by the rule below (see "Repos as sources") |

## A lens document

```
# How <X> would build <us>

**Answered:** <date>, by <who>
**Mined:** IDEA-0012, IDEA-0013, …

## What they would keep from what we have       — cite the code, the doc, the decision
## What they would replace, and with what       — each replacement names an idea file
## What they would never do                     — each prohibition names an idea file
## The three things they would ship first
## What this lens does not see                  — name the blind spot and the lens that covers it
```

Keep it honest: the value is in the specific move they would make, not in admiration. A lens
that cannot cite the codebase is a blog post.

## Repos as sources

Stars measure attention; the failures that hurt are one-person projects, launch-week hype and
abandonment. A repo counts as a source for a lens only when it passes **all** of: ≥ 1,000 stars ·
≥ 12 months old · commits in the last 90 days · a release in the last 6 months · top contributor
< 70 % of commits (or an Organization with ≥ 3 contributors above 10 %) · OSI licence.

`python scripts/repo_health.py owner/repo ...` prints the columns with a PASS/FAIL verdict
(`--markdown` for pasting into a lens; `owner/repo=pypi-package` adds 30-day downloads). Cite the
table in the lens under "Which repos count". A repo that fails may be *watched* in the blind-spot
section — never depended on, never the sole evidence for an idea.
