## Why

The tool's whole argument is that a person's statements never leave their machine — and today
that requires cloning a repository and installing pixi, which is a wall for nearly everyone the
website article is written for. A browser is the machine most people already have. Running
the same engine there, with nothing uploaded, extends the promise instead of breaking it.

## What Changes

- A static web app, `web/`, that runs `budget.py` unchanged in the browser via Pyodide
  (CPython compiled to WebAssembly; pyyaml is a built-in package). The user drops CSV exports
  on the page, edits the three personal YAML files in the page, presses run, and reads the
  same console headline and `budget.md` the CLI produces.
- Personal files persist in the browser only (IndexedDB), with export and import as plain
  YAML so they are portable and deletable. Nothing is sent anywhere; the app makes no network
  request after its own assets load.
- Pyodide and every asset are served from the Collegica site itself, keeping the site's
  standing claim of no third-party requests. Published under `www.collegica.org/owl/`.
- The CLI remains the reference; `web/` consumes the same `budget.py`, `categories.yml` and
  `*.example.yml` at build time, so there is one engine and one set of specs.
- Non-goals: PDF statements in the browser (`pdf_import.py` needs poppler; v1 says so and
  points at the CLI); a hosted backend of any kind; a rewrite in another language.

Personal data: the app holds the user's files in their own browser storage and in memory.
The repository gains no personal content; the sample household (IDEA-0008) is the only data
the page ships with.

## Capabilities

### New Capabilities
- `web-app`: the browser-hosted runner — loading the engine, taking files, persisting personal
  configuration locally, running, and rendering output, with the privacy guarantees stated
  as requirements.

### Modified Capabilities
- `privacy`: the "no network, no credentials" requirement gains a scenario for the browser —
  no request after asset load, and personal data confined to the user's own browser storage.

## Impact

- New: `web/` (HTML, one JS module, a Web Worker running Pyodide), a pixi task `web-build`
  that assembles `web/dist/` from the engine files and the pinned Pyodide release, and a CI job
  that builds and attaches `owl-web.tar.gz` to each GitHub release.
- `budget.py`: `main()` takes `argv` and returns the report text instead of printing, with a
  thin CLI wrapper — the only engine change, and it makes the CLI easier to test too.
- Collegica site: a CI step that unpacks the latest `owl-web.tar.gz` into `public/owl/` after
  the Quarto render; the article's "Where it lives" section gains a "run it here" link.
- Size: about 12 MB of Pyodide assets on first visit (9.6 MB wasm + 2.5 MB stdlib), cached
  thereafter. Within Cloudflare Pages limits (25 MB per file).
