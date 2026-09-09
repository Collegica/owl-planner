---
id: IDEA-0029
lens: customer
capability: onboarding
status: promoted
effort: M
value: high
promoted_to: openspec/changes/owl-web
---

# Run the engine in the browser, with nothing uploaded

"Can we publish owl-planner as a WASM app that runs on the Collegica website?" The tool's
audience is the article's readers, and a clone-and-pixi install is a wall for most of them.
The engine is stdlib plus pyyaml, and Pyodide ships both, so the same `budget.py` can run in a
Web Worker against dropped CSVs with every asset served first-party.

Promoted to the OpenSpec change `owl-web`; the change is now the record.
