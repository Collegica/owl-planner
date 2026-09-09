#!/usr/bin/env python
"""ideas/index.md, generated from the ideas' headers — the LENS generator and gate.

    python generate_ideas_index.py            # rewrite the index
    python generate_ideas_index.py --check    # fail if it is stale or a header is wrong

Every idea file is `<IDEAS>/<YYYYMMDD>_<slug>.md` with a YAML header carrying id,
lens, capability, status, effort, value and promoted_to (see the LENS handbook).
The index opens with the open ideas in the order to work on them (value, then
effort), then one section per capability including the empty ones, and it
validates what a reader would otherwise trust: the capability id exists in the
catalogue, status / effort / value are legal, a promoted idea says where it
went, the lens is built in or a file, ids are unique.

Adapt the three paths below to the repository. Requires only pyyaml.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
IDEAS = ROOT / "docs" / "ideas"
INDEX = IDEAS / "index.md"
# the same ids as openspec/specs/<id>/, plus two the specs do not cover yet
CAPABILITIES = ROOT / "docs" / "capabilities.yaml"

STATUSES = ("seed", "explored", "promoted", "retired")
EFFORTS = ("S", "M", "L")  # days, weeks, a quarter or a dependency we do not control
VALUES = ("high", "medium", "low")
FILE_RE = re.compile(r"^(\d{8})_[a-z0-9][a-z0-9-]*\.md$")
BUILTIN_LENSES = ("data", "review", "incident", "customer")


def capability_names() -> dict[str, str]:
    data = yaml.safe_load(CAPABILITIES.read_text())
    out = {c["id"]: c["name"] for c in data.get("capabilities", [])}
    out.update({c["id"]: c["name"] for c in data.get("cross_cutting", [])})
    return out


def parse(path: Path) -> tuple[dict, str, list[str]]:
    """(header, title, problems) for one idea file."""
    text = path.read_text(encoding="utf-8")
    problems: list[str] = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, "", [f"{path.name}: no YAML header"]
    try:
        header = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return {}, "", [f"{path.name}: header is not YAML ({e})"]
    title_m = re.search(r"^# (.+)$", m.group(2), re.M)
    title = title_m.group(1).strip() if title_m else ""
    if not title:
        problems.append(f"{path.name}: no '# title'")
    return header, title, problems


def validate(path: Path, header: dict, caps: dict[str, str], lenses: set[str]) -> list[str]:
    p: list[str] = []
    name = path.name
    if not FILE_RE.match(name):
        p.append(f"{name}: filename must be <YYYYMMDD>_<slug>.md")
    if not re.match(r"^IDEA-\d{4}$", str(header.get("id", ""))):
        p.append(f"{name}: id must look like IDEA-0007")
    if header.get("capability") not in caps:
        p.append(f"{name}: capability {header.get('capability')!r} is not in the catalogue")
    if header.get("status") not in STATUSES:
        p.append(f"{name}: status must be one of {', '.join(STATUSES)}")
    if header.get("effort") not in EFFORTS:
        p.append(f"{name}: effort must be one of {', '.join(EFFORTS)}")
    if header.get("value") not in VALUES:
        p.append(f"{name}: value must be one of {', '.join(VALUES)}")
    lens = header.get("lens")
    if not lens:
        p.append(f"{name}: lens is required")
    elif lens not in BUILTIN_LENSES and lens not in lenses:
        p.append(f"{name}: lens {lens!r} is neither built in ({', '.join(BUILTIN_LENSES)}) nor a file in lenses/")
    if header.get("status") == "promoted" and not header.get("promoted_to"):
        p.append(f"{name}: promoted without promoted_to")
    return p


def priority_key(row: dict) -> tuple:
    """Highest value first, then least effort, then id — the order to work in."""
    return (VALUES.index(row["value"]), EFFORTS.index(row["effort"]), row["id"])


def render(rows: list[dict], caps: dict[str, str]) -> str:
    lines = [
        "# Ideas — index",
        "",
        "*Generated from the headers in this folder. Do not edit; edit the idea.*",
        "",
        f"{len(rows)} ideas: "
        + ", ".join(f"{sum(1 for r in rows if r['status'] == s)} {s}" for s in STATUSES)
        + ".",
        "",
        "## In order",
        "",
        "Open ideas (`seed`, `explored`) by value, then by effort — S is days, M weeks, L a quarter "
        "or a dependency we do not control. Ties keep id order; the ranking is only as good as the "
        "two header fields, which are reviewed with the idea.",
        "",
        "| # | id | idea | value | effort | capability | lens |",
        "|---|---|---|---|---|---|---|",
    ]
    open_rows = sorted((r for r in rows if r["status"] in ("seed", "explored")), key=priority_key)
    for n, r in enumerate(open_rows, 1):
        lines.append(
            f"| {n} | {r['id']} | [{r['title']}]({r['file']}) | {r['value']} | {r['effort']} | `{r['capability']}` | `{r['lens']}` |"
        )
    lines.append("")
    for cap_id, cap_name in caps.items():
        mine = [r for r in rows if r["capability"] == cap_id]
        lines.append(f"## {cap_name} (`{cap_id}`) — {len(mine)}")
        lines.append("")
        if not mine:
            lines.append("_No ideas filed._")
            lines.append("")
            continue
        lines.append("| id | idea | lens | value | effort | status | went to |")
        lines.append("|---|---|---|---|---|---|---|")
        for r in sorted(mine, key=lambda r: r["id"]):
            went = f"`{r['promoted_to']}`" if r.get("promoted_to") else ""
            lines.append(
                f"| {r['id']} | [{r['title']}]({r['file']}) | `{r['lens']}` | {r['value']} | {r['effort']} | {r['status']} | {went} |"
            )
        lines.append("")
    return "\n".join(lines)


def count(text: str) -> int:
    """Ideas in a rendered index: the by-capability tables list each once."""
    body = text[text.index("\n## ", text.index("## In order") + 1):] if "## In order" in text else text
    return body.count("| IDEA-")


def build() -> tuple[str, list[str]]:
    caps = capability_names()
    lenses = {p.stem for p in (IDEAS / "lenses").glob("*.md") if p.name != "README.md"}
    rows: list[dict] = []
    problems: list[str] = []
    seen: dict[str, str] = {}
    for path in sorted(IDEAS.glob("*.md")):
        if path.name in ("README.md", "index.md"):
            continue
        header, title, p = parse(path)
        problems += p
        if not header:
            continue
        problems += validate(path, header, caps, lenses)
        idea_id = str(header.get("id", ""))
        if idea_id in seen:
            problems.append(f"{path.name}: id {idea_id} already used by {seen[idea_id]}")
        seen[idea_id] = path.name
        rows.append({**header, "title": title, "file": path.name, "promoted_to": header.get("promoted_to") or ""})
    if problems:
        # A malformed header cannot be ranked; report every problem rather than crash on the first.
        return "", problems
    return render(rows, caps), problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail if index.md is stale or a header is malformed")
    args = ap.parse_args(argv)
    text, problems = build()
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    if args.check:
        current = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
        if current != text:
            print(f"{INDEX} is stale — regenerate it and commit the result.", file=sys.stderr)
            return 1
        print(f"{INDEX} is current ({count(text)} ideas).")
        return 0
    INDEX.write_text(text, encoding="utf-8")
    print(f"wrote {INDEX} ({count(text)} ideas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
