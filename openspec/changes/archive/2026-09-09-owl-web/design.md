## Context

`budget.py` is stdlib plus pyyaml, reads its inputs from a directory, and prints. Pyodide
(current release: Python 3.14.2, pyodide-lock `abi 2026_0`) ships pyyaml 6.0.3 as a built-in
package, and exposes a virtual filesystem the page can write files into. `pdf_import.py` shells
out to poppler's `pdftotext`, which has no browser equivalent in this design. The Collegica site
is a Quarto static build deployed to Cloudflare Pages via a `gh-pages` branch, and states on its
About page that it makes no third-party requests. See proposal.md for motivation.

## Goals / Non-Goals

**Goals:**
- One engine. The browser runs the same `budget.py`; the specs stay singular.
- First-party only. Pyodide is vendored into the build and served from collegica.org.
- Personal data stays in the browser, portable as YAML, deletable in one action.

**Non-Goals:**
- PDFs in the browser. A pdf.js-based layout reconstruction is possible later; not in v1.
- Any server, account, sync, or analytics.
- Replacing the CLI, which stays the reference and the developer's tool.

## Decisions

- **Pyodide over a rewrite** (TypeScript, or Rust→wasm as Retire, Eh? does). A rewrite would
  fork the engine and the specs; every future change would land twice. Pyodide costs about
  12 MB on first visit and a 2–4 s cold start, which is acceptable for a tool used a few times a
  year and cached after the first. Alternative considered: a Rust port — rejected for the fork.
- **A Web Worker owns the runtime.** The main thread never blocks; messages carry files in and
  text out. `budget.py` gains a `run(argv) -> str` that returns the console text, with `main()`
  reduced to a wrapper that prints it — the only engine change.
- **Virtual filesystem, not a code change.** The worker writes the dropped CSVs to
  `/work/statements/`, the three YAML files beside them, and calls `run(['--dir', ...])`. The
  engine's `HERE`-relative loading of `categories.yml` and the example files works unchanged
  because the build copies them next to `budget.py`.
- **IndexedDB for persistence, YAML for portability.** Local storage is capped and
  string-only; IndexedDB holds the three files and the last set of statements if the user
  opts in. Export writes the YAML the CLI would read, so a user can move between web and CLI.
- **Vendored Pyodide, pinned.** `web-build` downloads the pinned release tarball, takes only
  `pyodide.js`, `pyodide.asm.js`, `pyodide.asm.wasm`, `python_stdlib.zip`, `pyodide-lock.json`
  and the pyyaml wheel (about 12 MB), and writes `web/dist/`. No CDN.
- **Delivery to the site by release artifact, not submodule.** CI attaches `owl-web.tar.gz` to
  each GitHub release; the Collegica workflow unpacks the latest into `public/owl/` after the
  Quarto render. The two repositories stay decoupled and the site can pin a version.

## Risks / Trade-offs

- [12 MB first load on a slow connection] → progress indicator with the size stated; assets
  cached with long `Cache-Control`; the page is usable for editing configuration while loading.
- [Personal data in a shared computer's browser] → the delete-everything action is on the
  page, not buried, and the app says where data is stored on first run.
- [Pyodide ABI moves; a wheel stops matching] → the build pins one release and the lock file;
  the sample-household test in CI catches a broken runtime.
- [Cloudflare Pages file limits] → largest file 9.6 MB against a 25 MB cap; verified.
- [Drift between web and CLI output] → the byte-identical scenario is a CI test on the sample.

## Migration Plan

No migration: the CLI is unchanged for existing users. The site gains a new path, `/owl/`;
the article links to it once the page is live.

## Open Questions

- Whether to offer "remember my statements" at all, or only the configuration. Deferrable:
  the configuration is what takes effort to recreate; statements are a re-export away.
