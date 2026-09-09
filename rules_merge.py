#!/usr/bin/env python3
"""Append a rules.yml fragment to a personal rules.yml without losing a line.

rules.yml is read with yaml.safe_load, which throws the comments away — and
the comments are where a person wrote down why each rule exists. So this
works on the text: find the section, find the line, insert after it. Nothing
already there is rewritten, and a fragment that names a section or a budget
line the tool does not know is refused rather than guessed at. The same
functions run in the browser under Pyodide and behind `budget.py --merge`.

    preview(rules_text, fragment) -> [(section, line, pattern), ...]
    merge(rules_text, fragment)   -> the merged text

The fragment is what ask-your-ai.md asks an AI for: `categories:` mapping a
budget line to patterns, `transfers:` and `income:` as lists, and `unsure:`
for what it would not guess, which is reported and never merged.
"""
from __future__ import annotations
import re
from pathlib import Path

import yaml

HERE = Path(__file__).parent
SECTIONS = ('categories', 'transfers', 'income')
LISTS = ('transfers', 'income')


class MergeError(ValueError):
    """The fragment cannot be merged as it stands; the message says why."""


def budget_lines(path: Path | None = None) -> list[str]:
    """Every line in categories.yml, savings first — the only names a
    fragment may assign to."""
    defs = yaml.safe_load(Path(path or HERE / 'categories.yml').read_text())
    lines = list((defs.get('savings') or {}).get('lines') or [])
    for grp in (defs.get('expenses') or {}).values():
        lines += grp.get('lines') or []
    return lines


def _as_patterns(value, where: str) -> list[str]:
    if value is None:
        return []
    items = [value] if isinstance(value, str) else value
    if not isinstance(items, list):
        raise MergeError(f"{where} should be a list of patterns")
    out = []
    for p in items:
        if not isinstance(p, str) or not p.strip():
            raise MergeError(f"{where} holds {p!r}, which is not a pattern")
        try:
            re.compile(p, re.I)
        except re.error as e:
            raise MergeError(f"'{p}' is not a valid regular expression: {e}") from None
        out.append(p)
    return out


def parse(fragment: str, lines: list[str] | None = None) -> dict:
    """Validate a fragment and return it in one shape: categories as a
    mapping of canonical line name to patterns, transfers and income as
    lists, unsure as a list of strings. Raises MergeError, naming the
    problem, for anything else."""
    try:
        data = yaml.safe_load(fragment)
    except yaml.YAMLError as e:
        mark = getattr(e, 'problem_mark', None)
        at = f" at line {mark.line + 1}" if mark else ''
        raise MergeError(f"not valid YAML{at}: {getattr(e, 'problem', None) or e}") from None
    if data is None:
        raise MergeError("the fragment is empty")
    if not isinstance(data, dict):
        raise MergeError("the fragment should start with a section name such as categories:")
    known = lines if lines is not None else budget_lines()
    canonical = {l.lower(): l for l in known}
    out = {'categories': {}, 'transfers': [], 'income': [], 'unsure': []}
    for key, value in data.items():
        if key == 'categories':
            if value is None:
                continue
            if not isinstance(value, dict):
                raise MergeError("categories: should map a budget line to its patterns")
            for line, pats in value.items():
                name = canonical.get(str(line).lower())
                if name is None:
                    raise MergeError(f"'{line}' is not a budget line in categories.yml")
                out['categories'].setdefault(name, [])
                for p in _as_patterns(pats, f"categories: {name}"):
                    if p not in out['categories'][name]:
                        out['categories'][name].append(p)
        elif key in LISTS:
            for p in _as_patterns(value, f"{key}:"):
                if p not in out[key]:
                    out[key].append(p)
        elif key == 'unsure':
            items = value if isinstance(value, list) else [value] if value is not None else []
            for item in items:
                if isinstance(item, dict):
                    out['unsure'] += [f"{k}: {v}" if v is not None else str(k) for k, v in item.items()]
                elif item is not None:
                    out['unsure'].append(str(item))
        else:
            raise MergeError(f"'{key}' is not a section this merge knows "
                             f"(categories, transfers, income, unsure)")
    return out


def _existing(rules_text: str) -> dict:
    try:
        data = yaml.safe_load(rules_text) if rules_text.strip() else {}
    except yaml.YAMLError as e:
        raise MergeError(f"rules.yml is not valid YAML: {getattr(e, 'problem', None) or e}") from None
    return data if isinstance(data, dict) else {}


def preview(rules_text: str, fragment: str, lines: list[str] | None = None) -> list[tuple[str, str, str]]:
    """The entries merge() would add, as (section, line, pattern) — line is
    empty for transfers and income. A pattern already in place is left out,
    so merging the same answer twice adds nothing the second time."""
    frag = parse(fragment, lines)
    have = _existing(rules_text)
    entries = []
    for section in LISTS:
        present = have.get(section) or []
        present = [present] if isinstance(present, str) else present
        entries += [(section, '', p) for p in frag[section] if p not in present]
    cats = have.get('categories') or {}
    for line, pats in frag['categories'].items():
        present = cats.get(line) or []
        present = [present] if isinstance(present, str) else present
        entries += [('categories', line, p) for p in pats if p not in present]
    return entries


def merge(rules_text: str, fragment: str, lines: list[str] | None = None) -> str:
    """rules_text with the fragment's entries appended in place. Every
    existing line is kept; the only rewritten line is a flow list such as
    `Groceries: ['a','b']`, which gains its new pattern before the bracket."""
    entries = preview(rules_text, fragment, lines)
    text = rules_text
    for section, line, pattern in entries:
        text = _insert(text, section, line, pattern)
    # the one thing worse than refusing is writing a file the engine cannot
    # read; check the result parses and carries what was asked for
    result = _existing(text)
    for section, line, pattern in entries:
        got = result.get(section) or {}
        got = (got.get(line) or []) if line else got
        got = [got] if isinstance(got, str) else got
        if pattern not in got:
            raise MergeError(f"could not place '{pattern}' under {line or section}; nothing written")
    return text


# ---- the text surgery ------------------------------------------------------

TOP_KEY = re.compile(r'^([^\s#][^:#]*?)\s*:(.*)$')
SUB_KEY = re.compile(r'^(\s+)("([^"]*)"|\'([^\']*)\'|([^\s#][^:#]*?))\s*:(.*)$')


def _q(pattern: str) -> str:
    return "'" + pattern.replace("'", "''") + "'"


def _key(name: str) -> str:
    return f'"{name}"' if any(c in name for c in ',:#\'"[]{}&*!|>%@`') else name


def _blank(row: str) -> bool:
    return row.strip() == '' or row.lstrip().startswith('#')


def _rest(rest: str) -> str:
    """What follows the colon, with a trailing comment dropped."""
    rest = rest.strip()
    return '' if rest.startswith('#') else rest


def _section(rows: list[str], name: str):
    """(start, end) rows of a top-level section, or None."""
    start = next((i for i, r in enumerate(rows)
                  if (m := TOP_KEY.match(r)) and m.group(1) == name), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(rows))
                if TOP_KEY.match(rows[i]) and not rows[i].startswith(' ')), len(rows))
    return start, end


def _last_content(rows: list[str], start: int, end: int) -> int:
    """Row to insert after: the last non-blank, non-comment row of the span,
    or the span's first row when it holds nothing yet."""
    for i in range(end - 1, start, -1):
        if not _blank(rows[i]):
            return i
    return start


def _flow_append(row: str, pattern: str) -> str:
    before, _, after = row.rpartition(']')
    sep = ', ' if "', '" in before or '", "' in before else ','
    if before.rstrip().endswith('['):
        sep = ''
    return f"{before}{sep}{_q(pattern)}]{after}"


def _insert(text: str, section: str, line: str, pattern: str) -> str:
    nl = '\r\n' if '\r\n' in text else '\n'
    rows = text.split(nl)
    trailing = rows[-1] == '' if rows else True
    if trailing and rows:
        rows.pop()
    span = _section(rows, section)
    if span is None:
        # a missing section goes at the end of the file, after a blank line
        if rows and rows[-1].strip():
            rows.append('')
        rows.append(f'{section}:')
        rows.append(f"  {_key(line)}: [{_q(pattern)}]" if section == 'categories' else f"  - {_q(pattern)}")
        return nl.join(rows) + nl
    start, end = span
    if section in LISTS:
        head = _rest(TOP_KEY.match(rows[start]).group(2))
        if head.startswith('['):
            rows[start] = _flow_append(rows[start], pattern)
        else:
            item = next((re.match(r'^(\s*)- ', rows[i]).group(1) for i in range(start + 1, end)
                         if re.match(r'^\s*- ', rows[i])), '  ')
            rows.insert(_last_content(rows, start, end) + 1, f"{item}- {_q(pattern)}")
        return nl.join(rows) + (nl if trailing else '')
    # categories: find the budget line at the section's item indent
    keys = [(i, m) for i in range(start + 1, end)
            if not _blank(rows[i]) and (m := SUB_KEY.match(rows[i]))]
    indent = min((m.group(1) for _, m in keys), key=len, default='  ')
    hit = next(((i, m) for i, m in keys
                if m.group(1) == indent and (m.group(3) or m.group(4) or m.group(5)) == line), None)
    if hit is None:
        rows.insert(_last_content(rows, start, end) + 1, f"{indent}{_key(line)}: [{_q(pattern)}]")
        return nl.join(rows) + (nl if trailing else '')
    i, m = hit
    rest = _rest(m.group(6))
    # the line's own block: rows below it indented deeper than the key
    block_end = next((j for j in range(i + 1, end)
                      if not _blank(rows[j]) and len(rows[j]) - len(rows[j].lstrip()) <= len(indent)), end)
    if rest.startswith('['):
        close = next((j for j in range(i, block_end) if ']' in rows[j].split('#')[0]), None)
        if close is None:
            raise MergeError(f"could not find the end of the {line} list; nothing written")
        rows[close] = _flow_append(rows[close], pattern)
    elif rest == '':
        item = next((re.match(r'^(\s*)- ', rows[j]).group(1) for j in range(i + 1, block_end)
                     if re.match(r'^\s*- ', rows[j])), indent + '  ')
        rows.insert(_last_content(rows, i, block_end) + 1, f"{item}- {_q(pattern)}")
    else:
        # a single scalar pattern becomes a two-item list
        rows[i] = rows[i][:m.start(6)] + f" [{rest}, {_q(pattern)}]"
    return nl.join(rows) + (nl if trailing else '')
