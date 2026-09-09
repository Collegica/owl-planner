#!/usr/bin/env python3
"""Maintenance signals for GitHub repos considered as idea sources or dependencies.

Stars measure attention. The failures we screen for are one-person projects, launch-week hype
with no track record, and abandonment — none of which stars catch. This prints, per repo, the
signals that do, and a PASS/FAIL against the LENS rule for repository lenses
(LENS-Handbook, "Repository lenses"; `templates/lenses-README.md`, "Repos as sources"):

    stars >= 1000, age >= 12 months, commits in the last 90 days, a release in the last
    6 months, top contributor < 70 % of commits (or an Organization with >= 3 contributors
    above 10 %), OSI licence.

Usage:
    python scripts/repo_health.py owner/repo [owner/repo=pypi-package ...] [--markdown]

`=pypi-package` adds last-30-day PyPI downloads from pypistats.org (informational, not gated).
Uses the `gh` CLI for GitHub (inherits its auth); stdlib only.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

MIN_STARS = 1000
MIN_AGE_DAYS = 365
ACTIVE_WINDOW_DAYS = 90
RELEASE_WINDOW_DAYS = 183
MAX_TOP_SHARE = 0.70
ORG_MIN_CORE = 3  # contributors above 10 % that let an org pass a concentrated top share
NON_OSI = {None, "NOASSERTION", "OTHER"}


def gh(path: str):
    """Return parsed JSON from `gh api <path>`; None when the call fails."""
    proc = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def pypi_downloads(package: str) -> int | None:
    url = f"https://pypistats.org/api/packages/{package}/recent"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:  # noqa: S310 - fixed https host
            return json.load(resp)["data"]["last_month"]
    except Exception:  # noqa: BLE001 - informational column
        return None


@dataclass
class Health:
    repo: str
    stars: int
    owner_type: str
    created: datetime
    licence: str | None
    contributors: int
    top_share: float
    core: int  # contributors above 10 % of commits
    commits_90d: int
    last_release: datetime | None
    downloads: int | None

    def checks(self, now: datetime) -> dict[str, bool]:
        age_ok = (now - self.created).days >= MIN_AGE_DAYS
        release_ok = (
            self.last_release is not None and (now - self.last_release).days <= RELEASE_WINDOW_DAYS
        )
        bus_ok = self.top_share < MAX_TOP_SHARE or (
            self.owner_type == "Organization" and self.core >= ORG_MIN_CORE
        )
        return {
            "stars": self.stars >= MIN_STARS,
            "age": age_ok,
            "active": self.commits_90d > 0,
            "release": release_ok,
            "bus_factor": bus_ok,
            "licence": self.licence not in NON_OSI,
        }


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def inspect(repo: str, package: str | None, now: datetime) -> Health | None:
    meta = gh(f"repos/{repo}")
    if not meta:
        return None
    contributors = gh(f"repos/{repo}/contributors?per_page=100&anon=false") or []
    counts = [c.get("contributions", 0) for c in contributors]
    total = sum(counts) or 1
    since = (now - timedelta(days=ACTIVE_WINDOW_DAYS)).strftime("%Y-%m-%d")
    commits = gh(f"repos/{repo}/commits?since={since}&per_page=100") or []
    releases = gh(f"repos/{repo}/releases?per_page=1") or []
    return Health(
        repo=repo,
        stars=meta.get("stargazers_count", 0),
        owner_type=meta.get("owner", {}).get("type", "User"),
        created=parse_ts(meta.get("created_at")) or now,
        licence=(meta.get("license") or {}).get("spdx_id"),
        contributors=len(contributors),
        top_share=(max(counts) / total) if counts else 1.0,
        core=sum(1 for c in counts if c / total > 0.10),
        commits_90d=len(commits),
        last_release=parse_ts(releases[0].get("published_at")) if releases else None,
        downloads=pypi_downloads(package) if package else None,
    )


def fmt_row(h: Health, now: datetime, markdown: bool) -> str:
    checks = h.checks(now)
    verdict = (
        "PASS"
        if all(checks.values())
        else "FAIL " + ",".join(k for k, ok in checks.items() if not ok)
    )
    age_m = (now - h.created).days // 30
    release = h.last_release.strftime("%Y-%m-%d") if h.last_release else "none"
    dl = f"{h.downloads:,}" if h.downloads is not None else "-"
    cells = [
        h.repo,
        f"{h.stars:,}",
        h.owner_type[:3].lower(),
        f"{age_m}mo",
        f"{h.contributors}/{h.top_share:.0%}",
        str(h.commits_90d) + ("+" if h.commits_90d >= 100 else ""),
        release,
        h.licence or "none",
        dl,
        verdict,
    ]
    return "| " + " | ".join(cells) + " |" if markdown else "\t".join(cells)


HEADER = [
    "repo",
    "stars",
    "owner",
    "age",
    "contrib/top",
    "commits90d",
    "last_release",
    "licence",
    "pypi30d",
    "verdict",
]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("repos", nargs="+", help="owner/repo or owner/repo=pypi-package")
    ap.add_argument("--markdown", action="store_true", help="emit a Markdown table")
    args = ap.parse_args(argv)

    now = datetime.now(UTC)
    if args.markdown:
        print("| " + " | ".join(HEADER) + " |")
        print("|" + "---|" * len(HEADER))
    else:
        print("\t".join(HEADER))
    failures = 0
    for spec in args.repos:
        repo, _, package = spec.partition("=")
        health = inspect(repo, package or None, now)
        if health is None:
            print(f"{repo}\t(not found or gh api failed)", file=sys.stderr)
            failures += 1
            continue
        print(fmt_row(health, now, args.markdown))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
