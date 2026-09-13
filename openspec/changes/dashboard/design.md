## Context

The console and `budget.md` already compute everything the first screen needs: `pct`, `state`, `whole`, `per_month`, `median`, `median_months`, `baseline`, the five set-aside totals, and — since the interview — the ranked question list. The dashboard is a projection of those, not a new measurement. See proposal.md.

## Goals / Non-Goals

**Goals:** a glance; coverage as a number of answers; the state visible before the figure; the same file from the CLI and the browser, byte for byte.

**Non-Goals:** interactivity, a second layout for print, anything not already on the console.

## Decisions

- **HTML from Python, one file, no script.** Inline CSS and inline SVG. A dashboard that needs a font or a chart library from a CDN would break the privacy spec's "no request after load" for the browser build and the "no network" rule for the CLI. Alternative: a Markdown dashboard — cannot draw the months.
- **"N more answers" from the ranked list, without the names.** `coverage_step` walks the question totals in order until the goal (95%) is reached and reports the count and the resulting percentage. Merchant signatures stay out of the file — `budget.md`'s "no identifiers" rule applies to the dashboard too — so the line says *how many*, and the terminal says *which*.
- **State first.** The badge sits in the heading; the annual card prints a dash and the reason when the state is not MEASURED, mirroring the console's refusal.
- **Deterministic output.** No timestamp, no random id, so the browser engine and the CLI produce identical bytes and parity can compare them.
- **A tab, not a new page.** The web page renders the file in a sandboxed `<iframe srcdoc>` — the file is the engine's, the page only carries it — and offers it for download.

## Risks / Trade-offs

- [The months chart on a very long window becomes cramped] → bars scale to the count; labels are month names; beyond ~24 months the console list remains the reference.
- [Coverage goal of 95% is arbitrary] → a constant, named, in one place; the line also says how many questions there are in all.
