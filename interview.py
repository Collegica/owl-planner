#!/usr/bin/env python3
"""The first-run interview: what the tool could not classify, asked as
questions, and each answer written to the personal configuration as a rule.

The tool surfaces, the person decides. Questions are ranked by the money
behind them, one per description signature so one answer covers every
recurrence, and every answer is appended to rules.yml or loans.yml without
touching a line already there. Nothing here guesses.

    questions(uncategorised, signature)      -> ranked list of Question
    render(qs, ...)                          -> the printed question list
    ask(qs, lines, ...)                      -> [(Question, Answer), ...] from stdin
    write(answers, rules_text, loans_text)   -> (rules_text, loans_text, summary lines)

Runs unchanged under Pyodide; only ask() needs a terminal, and the caller
checks for one.
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date as _date
from typing import Callable

import rules_merge

ASK_MOST = 20          # questions per run; the rest wait for the next run
KINDS = ('line', 'transfer', 'income', 'lending', 'passthrough', 'one_off', 'level', 'skip')


@dataclass
class Question:
    signature: str
    count: int
    total: float
    txns: list = field(default_factory=list)   # (date, description, amount)

    @property
    def each(self) -> float:
        return self.total / self.count if self.count else 0.0


@dataclass
class Answer:
    kind: str                 # one of KINDS
    line: str = ''            # budget line, for kind == 'line'
    who: str = ''             # counterparty, for kind == 'lending'
    reason: str = ''          # the person's stated reason, optional


def questions(uncategorised, signature: Callable[[str], str]) -> list[Question]:
    """Group unclassified outflows by signature, largest total first."""
    by_sig: dict[str, Question] = {}
    for d, desc, out, *_ in uncategorised:
        sig = signature(desc) or desc.lower().strip()
        q = by_sig.setdefault(sig, Question(sig, 0, 0.0))
        q.count += 1
        q.total += out
        q.txns.append((d, desc, out))
    return sorted(by_sig.values(), key=lambda q: (-q.total, q.signature))


def render(qs: list[Question], *, asked: int = ASK_MOST, width: int = 12) -> list[str]:
    """The question list as console lines, in the report's own layout."""
    if not qs:
        return []
    top = qs[:asked]
    total = sum(q.total for q in qs)
    share = 100 * sum(q.total for q in top) / total if total else 0
    pad = ' ' * (width + 2)
    head = (f"  {'QUESTIONS':<{width}}{len(top)} description{'s' if len(top) != 1 else ''} "
            f"account{'' if len(top) != 1 else 's'} for {share:.0f}% of what was not classified"
            + (f" (the top {asked} of {len(qs)}; re-run for the rest)" if len(qs) > asked else ''))
    lines = [head]
    for i, q in enumerate(top, 1):
        lines.append(f"{pad}{i:>2}. {q.signature} — {q.count} transaction{'s' if q.count != 1 else ''}, "
                     f"${q.total:,.0f}" + (f" (~${q.each:,.0f} each)" if q.count > 1 else ''))
    lines.append(f"{pad}Run in a terminal to answer them; --no-interview prints this and carries on.")
    return lines


def _menu(lines: list[str]) -> list[str]:
    cols = 2
    rows = []
    width = max(len(l) for l in lines) + 6
    for i in range(0, len(lines), cols):
        rows.append(''.join(f"{i + j + 1:>3}. {lines[i + j]:<{width}}"
                            for j in range(cols) if i + j < len(lines)).rstrip())
    return rows


def ask(qs: list[Question], lines: list[str], *, prompt: Callable[[str], str] | None = None,
        say: Callable[[str], None] = print, asked: int = ASK_MOST) -> list[tuple[Question, Answer]]:
    """Ask each question on the terminal. Returns what was answered; a question
    answered with Enter (don't know) or after `q` is not in the result."""
    import builtins
    prompt = prompt or builtins.input   # resolved now, so a test can replace it
    top = qs[:asked]
    say('')
    say("  Answer each with a budget-line number, or a letter:")
    say("    t transfer between your own accounts   i income   l lending (asks who)")
    say("    p pass-through   o one-off, decided   v level (a month-end obligation)")
    say("    Enter = don't know (stays unclassified)   q = stop")
    say('')
    for row in _menu(lines):
        say(f"  {row}")
    say('')
    out: list[tuple[Question, Answer]] = []
    for i, q in enumerate(top, 1):
        while True:
            try:
                raw = prompt(f"  {i}/{len(top)}  {q.signature} — {q.count} transaction{'s' if q.count != 1 else ''}, "
                         f"${q.total:,.0f}{f' (~${q.each:,.0f} each)' if q.count > 1 else ''}\n       > ").strip()
            except (EOFError, KeyboardInterrupt):
                say('')
                return out          # Ctrl-D or Ctrl-C: keep what was answered so far
            if raw == '':
                break
            if raw.lower() == 'q':
                return out
            ans = _parse(raw, lines)
            if ans is None:
                say("       a number from the list, one of t i l p o v, Enter, or q")
                continue
            if ans.kind == 'lending' and not ans.who:
                try:
                    ans.who = prompt("       lent to whom? > ").strip()
                except (EOFError, KeyboardInterrupt):
                    return out
                if not ans.who:
                    say("       lending needs a name")
                    continue
            try:
                ans.reason = prompt("       why? (optional) > ").strip()
            except (EOFError, KeyboardInterrupt):
                ans.reason = ''
            out.append((q, ans))
            break
    return out


def _parse(raw: str, lines: list[str]) -> Answer | None:
    head, _, rest = raw.partition(' ')
    key = head.lower()
    if key.isdigit():
        n = int(key)
        return Answer('line', line=lines[n - 1]) if 1 <= n <= len(lines) else None
    table = {'t': 'transfer', 'i': 'income', 'l': 'lending', 'p': 'passthrough',
             'o': 'one_off', 'v': 'level'}
    if key in table:
        return Answer(table[key], who=rest.strip() if key == 'l' else '')
    # a budget line typed in full
    match = next((l for l in lines if l.lower() == raw.lower()), None)
    return Answer('line', line=match) if match else None


# ---- writing answers ---------------------------------------------------------

def pattern_for(q: Question) -> str:
    """A pattern that matches every description behind the question. The
    signature's words with plain spaces when that already matches them all
    (`newtown dental`); otherwise the words joined by `\\W+`, which is what
    `SQ *CAFE 4471` needs. Never a bare number."""
    words = q.signature.split()
    plain = ' '.join(words)
    if all(re.search(plain, desc, re.I) for _, desc, _ in q.txns):
        return plain
    return r'\W+'.join(words)


def _note(reason: str, today: _date) -> str:
    return f"{today.isoformat()} interview" + (f": {reason}" if reason else '')


def _annotate(text: str, pattern: str, comment: str) -> str:
    """Put the note on the line rules_merge just wrote the pattern to, as a
    trailing YAML comment. A line with a comment already gets it appended."""
    nl = '\r\n' if '\r\n' in text else '\n'
    rows = text.split(nl)
    needle = rules_merge._q(pattern)
    for i in range(len(rows) - 1, -1, -1):
        if needle in rows[i]:
            # only a # after the pattern is a comment; a # inside an earlier
            # pattern on the same row is part of a regex
            after = rows[i].find(needle) + len(needle)
            j = rows[i].find('#', after)
            if j < 0:
                rows[i] = f"{rows[i].rstrip()}  # {comment}"
            else:
                rows[i] = f"{rows[i][:j].rstrip()}  # {rows[i][j + 1:].strip()}; {comment}"
            break
    return nl.join(rows)


def _append_items(text: str, section: str, items: list[list[str]], created_comment: str) -> str:
    """Append mapping items (each a list of `key: value` strings) to a list
    section such as one_off, passthrough, level or disbursements, creating the
    section at the end of the file if it is missing. Byte-for-byte otherwise."""
    nl = '\r\n' if '\r\n' in text else '\n'
    rows = text.split(nl)
    trailing = rows[-1] == '' if rows else True
    if trailing and rows:
        rows.pop()
    span = rules_merge._section(rows, section)
    block = []
    for item in items:
        block.append(f"  - {item[0]}")
        block += [f"    {kv}" for kv in item[1:]]
    if span is None:
        if rows and rows[-1].strip():
            rows.append('')
        rows += [f"# {created_comment}", f"{section}:"] + block
        return nl.join(rows) + nl
    start, end = span
    at = rules_merge._last_content(rows, start, end) + 1
    rows[at:at] = block
    return nl.join(rows) + (nl if trailing else '')


def _yq(s: str) -> str:
    return "'" + str(s).replace("'", "''") + "'"


def write(answers: list[tuple[Question, Answer]], rules_text: str, loans_text: str,
          *, today: _date | None = None, lines: list[str] | None = None):
    """Apply answers to the two personal files' text. Returns the new texts
    and one summary line per answer. Raises rules_merge.MergeError for a
    budget line the tool does not know."""
    today = today or _date.today()
    summary = []
    for q, a in answers:
        note = _note(a.reason, today)
        pattern = pattern_for(q)
        if a.kind in ('line', 'transfer', 'income'):
            fragment = (f"categories:\n  {rules_merge._key(a.line)}: [{rules_merge._q(pattern)}]\n"
                        if a.kind == 'line' else f"{a.kind}s:\n  - {rules_merge._q(pattern)}\n")
            rules_text = rules_merge.merge(rules_text, fragment, lines)
            rules_text = _annotate(rules_text, pattern, note)
            summary.append(f"{q.signature} → {a.line if a.kind == 'line' else a.kind}")
        elif a.kind == 'level':
            rules_text = _append_items(rules_text, 'level',
                                       [[f"match: {_yq(pattern)}", f"note: {_yq(a.reason or q.signature)}  # {note}"]],
                                       "month-end obligations, charged at their monthly rate (added by the interview)")
            summary.append(f"{q.signature} → levelled")
        elif a.kind in ('one_off', 'passthrough'):
            items = [[f"date: {d.isoformat() if hasattr(d, 'isoformat') else d}",
                      f"amount: {out:.2f}", f"note: {_yq(a.reason or q.signature)}  # {note}"]
                     for d, _, out in q.txns]
            rules_text = _append_items(rules_text, a.kind, items,
                                       f"{'decided one-offs' if a.kind == 'one_off' else 'pass-throughs'} (added by the interview)")
            summary.append(f"{q.signature} → {'one-off' if a.kind == 'one_off' else 'pass-through'} × {len(items)}")
        elif a.kind == 'lending':
            items = [[f"date: {d.isoformat() if hasattr(d, 'isoformat') else d}",
                      f"amount: {out:.2f}", f"to: {_yq(a.who)}  # {note}"] for d, _, out in q.txns]
            loans_text = _append_items(loans_text, 'disbursements', items,
                                       "money lent, pinned by date and amount (added by the interview)")
            if not re.search(r'^\s*-\s*to:\s*' + re.escape(_yq(a.who)) + r'\s*$', loans_text, re.M):
                loans_text = _append_items(loans_text, 'lent',
                                           [[f"to: {_yq(a.who)}", f"principal: {q.total:.2f}", f"repaid: 0  # {note}"]],
                                           "what is owed to you (added by the interview)")
            summary.append(f"{q.signature} → lent to {a.who} × {len(items)}")
    return rules_text, loans_text, summary
