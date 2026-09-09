## Context

The engine already computes `uncategorised` grouped by description and the `signature()` function used for recurring detection. `rules.yml` is read with `yaml.safe_load`, which loses comments, so merging must edit text. See proposal.md.

## Goals / Non-Goals

**Goals:** a pack with nothing sensitive in it; an answer format that is also what the interview will produce; a merge that never loses a line.
**Non-Goals:** calling an AI; smoothing over ambiguity.

## Decisions

- **Signatures, not descriptions.** `signature()` collapses store numbers and cities; one question per merchant, and the pattern the AI returns is the signature words, safe to append. Size band = total/count rounded to one significant figure, prefixed `~$`.
- **Text-level merge in `rules_merge.py`.** Locate a top-level section (`categories:` etc.) and, within `categories`, a line (`  Groceries:`); append to the flow list on that line if it is `[...]`, or add a new `  Line: ['pattern']` at the end of the section. Unknown section or line → refuse with a message. Pure functions on strings, so the page can call the same logic in Pyodide and the CLI via `--merge`.
- **Pack as Markdown** so it pastes cleanly into any chat and reads as a document.
- **Page:** a fourth output tab; the paste box lives under it. Validation and preview run in the worker via `rules_merge.preview(fragment)` returning the entries it would add.

## Risks / Trade-offs

- [An AI returns a pattern that is too broad] → the preview shows exactly what will be added; the user confirms; the next run's ledger shows what it matched.
- [The size band leaks something] → one significant figure of an average; the pack's header says what is and is not in it.
