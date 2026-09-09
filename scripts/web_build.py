#!/usr/bin/env python
"""Assemble web/dist/: the page, the engine, the sample, and a pinned Pyodide.

    python scripts/web_build.py            # build into web/dist/
    python scripts/web_build.py --clean    # drop the download cache first

Pyodide is vendored, never loaded from a CDN: the page is served from the
Collegica site, which makes no third-party requests, and this build keeps it
that way. The runtime files come from the pinned GitHub release; the pyyaml
wheel from the matching release channel on jsdelivr — downloaded here, at build
time, and checked against the SHA-256 recorded below. pdf.js, which reads PDF
statements in the browser, comes the same way from the npm registry tarball.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / 'web'
DIST = WEB / 'dist'
CACHE = WEB / '.cache'

PYODIDE = '314.0.6'   # CPython 3.14.2, abi 2026_0
CORE_URL = f'https://github.com/pyodide/pyodide/releases/download/{PYODIDE}/pyodide-core-{PYODIDE}.tar.bz2'
WHEEL = 'pyyaml-6.0.3-cp314-cp314-pyemscripten_2026_0_wasm32.whl'
WHEEL_URL = f'https://cdn.jsdelivr.net/pyodide/v{PYODIDE}/full/{WHEEL}'
PDFJS = '6.3.289'
PDFJS_TARBALL = f'pdfjs-dist-{PDFJS}.tgz'
PDFJS_URL = f'https://registry.npmjs.org/pdfjs-dist/-/{PDFJS_TARBALL}'

# Recorded on first build; a mismatch means the upstream file changed under
# the same name, which is exactly the thing to stop on.
SHA256 = {
    f'pyodide-core-{PYODIDE}.tar.bz2': '1016c31e39ce3764d9a418cbb491a392c802c1b86ccc1367f009f5c59bf8f5fd',
    WHEEL: 'b1447216501f0d3aef290558fe33691dd51b0839e70f9a970defb12b36d82df8',
    PDFJS_TARBALL: '06f25e887adc6489f04c9fcb14198c77e4e5623a59a0bba5c4cea5838a4f1241',
}

# The runtime files the page needs — nothing else from the tarball.
RUNTIME = ['pyodide.mjs', 'pyodide.asm.mjs', 'pyodide.asm.wasm',
           'python_stdlib.zip', 'pyodide-lock.json']
ENGINE = ['budget.py', 'rules_merge.py', 'pdf_import.py', 'pdf_layout.py',
          'categories.yml', 'rules.example.yml', 'loans.example.yml',
          'known-annual.example.yml']
# The two pdf.js modules the worker imports, plus the licence they come
# under; nothing else from the package.
PDFJS_FILES = ['build/pdf.min.mjs', 'build/pdf.worker.min.mjs', 'LICENSE']


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def fetch(url: str, dest: Path) -> Path:
    if not dest.exists():
        print(f'  downloading {url}')
        dest.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=120) as resp, open(dest, 'wb') as out:  # noqa: S310
            shutil.copyfileobj(resp, out)
    want = SHA256.get(dest.name)
    got = sha256(dest)
    if want and want != got:
        sys.exit(f'{dest.name}: SHA-256 {got} does not match the recorded {want}. '
                 f'Upstream changed under the same name; look before trusting it.')
    if not want:
        print(f'  {dest.name}: sha256 {got}  (record this in SHA256)')
    return dest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--clean', action='store_true')
    a = ap.parse_args(argv)
    if a.clean and CACHE.exists():
        shutil.rmtree(CACHE)
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / 'pyodide').mkdir(parents=True)

    print('runtime')
    core = fetch(CORE_URL, CACHE / f'pyodide-core-{PYODIDE}.tar.bz2')
    with tarfile.open(core, 'r:bz2') as tar:
        members = {m.name.split('/', 1)[1]: m for m in tar.getmembers() if '/' in m.name}
        for name in RUNTIME:
            fh = tar.extractfile(members[name])
            (DIST / 'pyodide' / name).write_bytes(fh.read())
    shutil.copy(fetch(WHEEL_URL, CACHE / WHEEL), DIST / 'pyodide' / WHEEL)

    print('pdf.js')
    (DIST / 'pdfjs').mkdir()
    with tarfile.open(fetch(PDFJS_URL, CACHE / PDFJS_TARBALL), 'r:gz') as tar:
        members = {m.name.split('/', 1)[1]: m for m in tar.getmembers() if '/' in m.name}
        for name in PDFJS_FILES:
            fh = tar.extractfile(members[name])
            (DIST / 'pdfjs' / Path(name).name).write_bytes(fh.read())

    print('engine')
    (DIST / 'app').mkdir()
    for name in ENGINE:
        shutil.copy(ROOT / name, DIST / 'app' / name)

    print('sample')
    (DIST / 'sample' / 'statements').mkdir(parents=True)
    for f in (ROOT / 'sample' / 'statements').glob('*.csv'):
        shutil.copy(f, DIST / 'sample' / 'statements' / f.name)
    for name in ('rules.yml', 'loans.yml', 'known-annual.yml'):
        shutil.copy(ROOT / 'sample' / name, DIST / 'sample' / name)
    (DIST / 'sample' / 'manifest.json').write_text(
        '[' + ', '.join(f'"{f.name}"' for f in sorted((ROOT / 'sample' / 'statements').glob('*.csv'))) + ']\n')

    print('page')
    for name in ('index.html', 'app.js', 'worker.js', 'style.css'):
        shutil.copy(WEB / name, DIST / name)
    (DIST / 'VERSION').write_text(f'pyodide {PYODIDE}\npdfjs {PDFJS}\n')

    total = sum(p.stat().st_size for p in DIST.rglob('*') if p.is_file())
    biggest = max((p for p in DIST.rglob('*') if p.is_file()), key=lambda p: p.stat().st_size)
    print(f'wrote {DIST.relative_to(ROOT)}/  {total/1e6:.1f} MB; largest file '
          f'{biggest.name} {biggest.stat().st_size/1e6:.1f} MB')
    if biggest.stat().st_size > 25e6:
        sys.exit('a file exceeds Cloudflare Pages\' 25 MB limit')
    return 0


if __name__ == '__main__':
    sys.exit(main())
