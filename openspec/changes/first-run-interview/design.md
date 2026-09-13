## Context

Classification is a single pass in `budget.py` that ends with an `uncategorised` bucket; reporting follows immediately. The personal yml files are read with `yaml.safe_load`, which discards comments, so they cannot be rewritten in place without losing the reasons people put in them. See proposal.md for motivation.

## Goals / Non-Goals

**Goals:**
- Ask in dollar order, one question per signature, answers durable on the first run.
- Work identically in a terminal session and when driven by an AI assistant reading the output.
- Leave every existing rule and comment untouched.

**Non-Goals:**
- Suggesting an answer. The tool surfaces, the person decides.
- A TUI or web form. Plain prompts on stdin, and a `--no-interview` flag for scripted runs.
- Rewriting `rules.yml` wholesale.

## Decisions

- **Append-only writer, not YAML round-tripping — `rules_merge` for the three pattern sections, plus a mapping-item appender for `level`, `one_off`, `passthrough` and loans' `disbursements`/`lent`.** Each section (`transfers`, `income`, `categories.<line>`, `level`, `one_off`, `passthrough`, `dated`) is located by its top-level key with a regex on the raw text and the new entry is inserted at the end of that section, preserving everything else byte-for-byte. Alternative: `ruamel.yaml` round-tripping — adds a dependency and still reorders in edge cases.
- **Signature as the unit of a question.** Reuses the existing `signature()` so the interview and the recurring test agree on what "the same payment" means. Alternative: exact description — asks the same question five times.
- **No threshold; ask whenever anything is unclassified, capped at 20 questions a run.** The original decision — ask only above 5% of outflow or a `--lumpy` item — would have hidden the invented household's own two-merchant residue, which is exactly the two keypresses worth making. The interruption is one line per merchant, Enter skips, `q` stops; `uncategorised.csv` still exists. (Changed during apply, 2026-09-13.)
- **Pattern generation is conservative.** The written pattern is the lower-cased signature words escaped, e.g. `new grocer`, never a bare merchant number. The user can tighten it by hand.
- **Interview before reporting, in the same run.** A person answering sees the effect immediately; the alternative — write rules, ask the user to re-run — is what the tool does today and is the thing being fixed.

## Risks / Trade-offs

- [A pattern written from a signature is too broad and swallows another merchant] → the pattern is the signature's words, which already governed the recurring test; the note records the date so the rule is easy to find and tighten.
- [stdin prompts are awkward under an AI assistant] → the question list is printed in full before any prompt, and `--no-interview` prints it and continues, so an assistant can read it and write the rules itself.
- [Appending to a section that does not exist in a hand-written file] → the writer creates the section at the end of the file with a one-line comment.

## Open Questions

- Whether "level" should be offered as an answer on the first run, or only once a signature has recurred in three months. Deferrable: the rule can be offered and the levelling requirement's three-payment guard already protects the baseline.
