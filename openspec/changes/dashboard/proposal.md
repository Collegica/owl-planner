## Why

`budget.md` is a report in a planner's intake-form order, and the console headline is a wall of labelled lines. Both are right and neither is a glance. The number a person came for — what a month costs, and how far it can be trusted — should be visible without reading, and the one figure that turns a report into a loop is coverage: how much of the figure rests on answered questions, and how many more answers would raise it. Without that, the interview is a chore; with it, the dashboard is the reason to answer.

## What Changes

- The engine writes **`dashboard.html`** beside `budget.md` on every run: one self-contained file, inline style and inline SVG, no script, no request to anywhere. Opens offline in any browser.
- Its first screen carries four things, labelled as the console labels them: **coverage** (percent of spending on a rule, and "answer the next N questions and coverage reaches X%"); the **recurring figure** with its state (MEASURED / ESTIMATE / UNKNOWN); the **annual figure**, printed only when measured; and the **five kinds set aside** — transfers, lending, savings, pass-throughs, income — with their totals.
- Below the fold: the complete months as bars with the median marked — the arithmetic behind the recurring figure, drawn rather than listed.
- The browser page shows the same file as a fifth tab, and can download it. Parity now compares `dashboard.html` as well as `budget.md`.
- Non-goals: net worth from closing balances (IDEA-0021, separate); charts beyond the months; any recommendation; any external asset or font; changes to how anything is classified or measured.

Nothing personal enters the repository: the dashboard carries budget lines and amounts, like `budget.md`, and no merchant, account or person. It is written beside `budget.md` and is gitignored with it.

## Capabilities

### New Capabilities
- `dashboard`: writing the first screen as a self-contained page, with coverage stated as a number of answers.

### Modified Capabilities
- `web-app`: the page gains a Dashboard tab showing the engine's `dashboard.html`.

## Impact

- `dashboard.py` (new): `render(data)`; `budget.py` assembles `data` from figures it already has and writes the file.
- `web/worker.js`, `web/app.js`, `web/index.html`: the tab; `scripts/web_parity.mjs`: compares the new file; `scripts/web_build.py`: ships the module.
- README: one line under *Run it* and a row in *The files*. No new dependency.
