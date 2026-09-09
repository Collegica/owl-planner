## Why

A stranger's first run categorises about half their spending with the example rules, and the rest is a list of merchant names only they can classify. Writing regular expressions is the wrong thing to ask of them; an AI is good at it — and the article already tells readers to bring their own. What is missing is the pack: the questions in a form an AI can answer, with nothing in it that should not leave the machine, and a place to put the answer. See IDEA-0007's lens: the tool's skill is asking well.

## What Changes

- **An "ask your AI" pack**, written by the engine beside `budget.md` as `ask-your-ai.md` and offered on the page as copy-to-clipboard and download. It contains: a prompt; the budget lines from `categories.yml`; the rule format with one example per section; and the **unique description signatures** the tool could not classify, each with how many times it occurred and a size band (`~$50`, `~$2,000` — one significant figure). **No amounts, no dates, no account fragments** leave in the pack. Signatures are ranked by the money behind them, but the money itself is not printed.
- The prompt asks for a `rules.yml` fragment — `categories:` entries and, where the AI judges so, `transfers:` or `income:` — and asks it to say "unsure" for anything ambiguous rather than guess.
- **A paste-in for the answer**: on the page, a "Paste rules from your AI" box that validates the fragment as YAML, shows what it will add, merges it into the `rules.yml` editor (appending to the right sections, never removing anything), and re-runs. On the CLI, `--merge <file>` does the same to the personal `rules.yml`.
- Non-goals: calling any AI from the tool; sending amounts or dates; the deterministic interview (`first-run-interview`) — this change defines the answer format that interview will reuse.

Personal data: the pack carries merchant names and counts only. The user is told, in the pack's first line and on the page, exactly what it contains.

## Capabilities

### New Capabilities
- `ask-your-ai`: the pack the tool writes for a person's own AI, and the merge of the answer back into the personal rules.

### Modified Capabilities
(none)

## Impact

`budget.py` (pack writer after classification; `--merge`), a small `rules_merge.py` (append-only section writer, shared later by the interview), `web/app.js` + `index.html` (a fourth output tab "Ask your AI"; the paste box), tests, the sample's expected output (one new "wrote" line).
