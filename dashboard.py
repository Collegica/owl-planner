#!/usr/bin/env python3
"""dashboard.html: the budget's first screen, written beside budget.md.

Four things, made legible at a glance and labelled the way the console
labels them: coverage — how much of spending rests on a rule, and how many
answers would raise it; the recurring figure and its state; the complete
months it was made from, with the median marked; and the five kinds of money
that moved but were not spending. No advice, no identifier — budget lines and
amounts only, like budget.md — and nothing fetched: one file, inline style,
inline SVG, no script. The same function runs in the browser.

    render(data) -> str      # data: the dict budget.py assembles
    coverage_step(...)       # the "N more answers" arithmetic, on its own for the tests
"""
from __future__ import annotations

from html import escape

GOAL = 95   # the coverage the "more answers" line aims for, in percent


def coverage_step(pct: float, spend: float, question_totals: list[float], goal: float = GOAL):
    """How many of the ranked questions, answered, would lift coverage to
    `goal` percent — and to what. Returns (n, pct_after) or None when
    nothing is unclassified. If every answer still falls short, n is all of
    them and pct_after is where that lands."""
    if not question_totals or spend <= 0:
        return None
    known = pct / 100 * spend
    running = known
    for n, t in enumerate(question_totals, 1):
        running += t
        after = 100 * running / spend
        if after >= goal:
            return n, after
    return len(question_totals), 100 * running / spend


def _money(v: float) -> str:
    return f"${v:,.0f}"


def _svg_months(whole: list[str], per_month: dict, median_months: set, median: float, mon) -> str:
    """One bar per complete month, the median month(s) filled darker, a rule
    at the median. Drawn to the tallest month; every label names a value."""
    if not whole:
        return ''
    w, h, pad_l, pad_b, pad_t = 640, 220, 8, 28, 18
    top = max(max(per_month[m] for m in whole), median, 1)
    n = len(whole)
    slot = (w - pad_l * 2) / n
    bar_w = slot * 0.66
    out = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Spending in each complete month, with the median marked" '
           f'preserveAspectRatio="xMidYMid meet">']
    y_med = pad_t + (h - pad_t - pad_b) * (1 - median / top)
    for i, m in enumerate(whole):
        v = per_month[m]
        bh = (h - pad_t - pad_b) * v / top
        x = pad_l + i * slot + (slot - bar_w) / 2
        y = h - pad_b - bh
        cls = 'bar med' if m in median_months else 'bar'
        out.append(f'<rect class="{cls}" x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bh:.1f}">'
                   f'<title>{escape(mon(m))}: {_money(v)}</title></rect>')
        out.append(f'<text class="lbl" x="{x + bar_w / 2:.1f}" y="{h - pad_b + 16}" text-anchor="middle">{escape(mon(m))}</text>')
        out.append(f'<text class="val" x="{x + bar_w / 2:.1f}" y="{max(y - 4, 12):.1f}" text-anchor="middle">{_money(v)}</text>')
    out.append(f'<line class="median" x1="{pad_l}" x2="{w - pad_l}" y1="{y_med:.1f}" y2="{y_med:.1f}"/>')
    out.append(f'<text class="medlbl" x="{w - pad_l}" y="{max(y_med - 5, 12):.1f}" text-anchor="end">median {_money(median)}</text>')
    out.append('</svg>')
    return '\n'.join(out)


CSS = """
:root{--ink:#1d2229;--muted:#5d6670;--line:#d9dde3;--paper:#fbfaf7;--card:#ffffff;
--measured:#2f6f4f;--estimate:#9a6b12;--unknown:#8a3a3a;--bar:#a9bfd6;--med:#2f5b8a;--set:#6b7c93}
@media (prefers-color-scheme:dark){:root{--ink:#e8e6e1;--muted:#a3a9b1;--line:#3a3f46;--paper:#16181b;--card:#1f2226;
--measured:#7fc39f;--estimate:#e0b25a;--unknown:#e08a8a;--bar:#3f5670;--med:#8fb6e0;--set:#98a6b8}}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);
font:15px/1.5 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
main{max-width:64rem;margin:0 auto;padding:1.5rem 1.25rem 3rem}
h1{font-size:1.35rem;font-weight:600;margin:0 0 .25rem}.sub{color:var(--muted);margin:0 0 1.25rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:1rem;margin-bottom:1.5rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:1rem 1.1rem}
.k{font-size:.78rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:0 0 .35rem}
.v{font-size:1.9rem;font-weight:600;line-height:1.1;margin:0;font-variant-numeric:tabular-nums}
.v small{font-size:.95rem;font-weight:400;color:var(--muted)}
.why{color:var(--muted);margin:.5rem 0 0;font-size:.92rem}
.state{display:inline-block;font-size:.75rem;font-weight:600;letter-spacing:.06em;padding:.15rem .5rem;border-radius:3px;
color:#fff;vertical-align:middle;margin-left:.4rem}
.MEASURED{background:var(--measured)}.ESTIMATE{background:var(--estimate)}.UNKNOWN{background:var(--unknown)}
.meter{height:.6rem;background:var(--line);border-radius:3px;overflow:hidden;margin:.6rem 0 .3rem}
.meter i{display:block;height:100%;background:var(--measured)}
section{margin:1.5rem 0}h2{font-size:1.05rem;font-weight:600;margin:0 0 .5rem}
svg{width:100%;height:auto;display:block}.bar{fill:var(--bar)}.bar.med{fill:var(--med)}
.median{stroke:var(--med);stroke-width:1.5;stroke-dasharray:4 4}
.lbl,.val,.medlbl{font-size:11px;fill:var(--muted)}.medlbl{fill:var(--med);font-weight:600}
table{border-collapse:collapse;width:100%;max-width:36rem}td,th{padding:.4rem .5rem;border-bottom:1px solid var(--line);text-align:left}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}th{font-size:.8rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.foot{color:var(--muted);font-size:.85rem;margin-top:2rem}
"""


def render(d: dict) -> str:
    """The page. `d` carries only figures the console already prints."""
    state = d['state']
    whole = d['whole']
    pct = d['pct']
    step = coverage_step(pct, d['spend'], d['question_totals'])
    n_q = len(d['question_totals'])

    if step is None:
        cov_line = "Every transaction is classified. Nothing rests on a guess."
    else:
        n, after = step
        cov_line = (f"Answer the next {n} question{'s' if n != 1 else ''} in a terminal and "
                    f"{'coverage reaches' if after >= GOAL else 'every question answered takes it to'} {after:.0f}%."
                    + (f" {n_q} question{'s' if n_q != 1 else ''} in all." if n_q > n else ''))

    if state == 'MEASURED':
        rec_v = f"{_money(d['median'])}<small>/month</small>"
        rec_why = (f"The median of {len(whole)} complete months, {'steady' if d['steady'] else 'uneven'}: "
                   f"months ranged {d['lo_r']:.0%}–{d['hi_r']:.0%} of the median. "
                   f"Large one-time items are held out.")
        annual_v = f"{_money(d['baseline'])}<small>/year</small>"
        annual_why = "Twelve times the recurring figure. Measured, so it can be quoted."
    elif state == 'ESTIMATE':
        rec_v = f"{_money(d['median'])}<small>/month</small>"
        rec_why = (f"Only {len(whole)} complete month{'s' if len(whole) != 1 else ''}; an annual figure "
                   f"needs three. Treat it as an estimate.")
        annual_v = "—"
        annual_why = f"Not printed: {3 - len(whole)} more complete month{'s' if 3 - len(whole) != 1 else ''} needed."
    else:
        rec_v = "—"
        rec_why = "No complete calendar month in the window; a month that starts or ends mid-statement is not counted."
        annual_v = "—"
        annual_why = "Not printed: no complete month to measure from."

    aside = [('Transfers between your own accounts', d['transfers'], 'Card payments, moves to savings. Counting these doubles every dollar put on a card.'),
             ('Lending', d['lending'], 'Money lent out; not spending, and not income when it comes back.'),
             ('Savings', d['savings'], 'Contributions to the savings lines in categories.yml.'),
             ('Pass-throughs', d['passthrough'], 'Arrived and left for the same reason; neither income nor spending.'),
             ('Income', d['income'], 'Identified inflows; the budget is spending, so these are shown, not netted.')]
    rows = ''.join(f"<tr><td>{escape(k)}<div class='why'>{escape(why)}</div></td><td class='n'>{_money(v)}</td></tr>"
                   for k, v, why in aside)

    html = f"""<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>OWL Planner — dashboard</title>
<style>{CSS}</style>
<main>
<h1>What a month costs <span class="state {escape(state)}">{escape(state)}</span></h1>
<p class="sub">{d['files']} file{'s' if d['files'] != 1 else ''}, {d['txns']} transactions, {escape(d['lo'])} to {escape(d['hi'])} — {len(whole)} complete month{'s' if len(whole) != 1 else ''}. Written by OWL Planner beside budget.md; the arithmetic is there.</p>

<div class="grid">
  <div class="card">
    <p class="k">Coverage</p>
    <p class="v">{pct:.0f}%<small> of spending rests on a rule</small></p>
    <div class="meter"><i style="width:{max(0, min(100, pct)):.0f}%"></i></div>
    <p class="why">{escape(cov_line)}</p>
  </div>
  <div class="card">
    <p class="k">Recurring</p>
    <p class="v">{rec_v}</p>
    <p class="why">{escape(rec_why)}</p>
  </div>
  <div class="card">
    <p class="k">Annual figure</p>
    <p class="v">{annual_v}</p>
    <p class="why">{escape(annual_why)}</p>
  </div>
</div>

<section>
<h2>The complete months behind the recurring figure</h2>
{_svg_months(whole, d['per_month'], d['median_months'], d['median'], d['mon']) or '<p class="why">No complete month to draw.</p>'}
</section>

<section>
<h2>Set aside — moved, but not spending</h2>
<table><thead><tr><th>Kind</th><th class="n">In the window</th></tr></thead><tbody>{rows}</tbody></table>
</section>

<p class="foot">Measured means three or more complete months; estimate means one or two; unknown means none. Nothing here is advice, and no merchant, account or person is named.</p>
</main>
"""
    return html
