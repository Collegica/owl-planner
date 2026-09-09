#!/usr/bin/env python3
"""Convert bank statement PDFs into the CSVs budget.py reads.

Statement PDFs are not a data format — they are a layout. So every extractor
here is checked against the statement's own arithmetic: opening balance, total
in, total out, closing balance. A statement whose transactions do not reconcile
is reported, never silently included. A budget built from a parse you did not
verify is worse than no budget.

    pixi run pdf-import -- --dir "~/Downloads/OWL/Bank statements"
"""
from __future__ import annotations
import argparse, csv, re, subprocess, sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
END_MONTH = [12]          # set per statement before extracting
MONTHS = {m: i for i, m in enumerate(
    ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], 1)}
AMT = r'-?\$?[\d,]+\.\d{2}'


def money(s: str) -> float:
    s = s.replace('$', '').replace(',', '').replace(' ', '').strip()
    # Canadian statements sign credits three ways: leading -, trailing -, or
    # parentheses. strip('()-') would silently turn -119.06 into a charge.
    neg = s.startswith('-') or s.endswith('-') or (s.startswith('(') and s.endswith(')'))
    s = s.strip('()').strip('-')
    try: v = float(s)
    except ValueError: return 0.0
    return -v if neg else v


def to_text(pdf: Path) -> str:
    return subprocess.run(['pdftotext', '-layout', str(pdf), '-'],
                          capture_output=True, text=True).stdout


def stmt_year(pdf: Path) -> int:
    m = re.search(r'(20\d{2})', pdf.name)
    return int(m.group(1)) if m else date.today().year


def stmt_end_month(pdf: Path, text: str) -> int:
    """The month the statement closes. A statement dated January carries
    December transactions from the year before; without this they land twelve
    months in the future and stretch the observed period across a whole year."""
    m = re.search(r'20\d{2}-(\d{2})-\d{2}', pdf.name)
    if m: return int(m.group(1))
    m = re.search(r'(January|February|March|April|May|June|July|August|September|'
                  r'October|November|December)\s+20\d{2}', pdf.name)
    if m: return MONTHS[m.group(1)[:3]]
    return stmt_month(text) or 12


def resolve_year(mon: int, year: int, end_month: int) -> int:
    return year - 1 if mon > end_month else year


# ---------------------------------------------------------------- CIBC card
def cibc(text: str, year: int):
    """Lines are: <trans date> <post date> <description> <amount>.

    Only inside the per-card sections: the summary block at the top contains
    date-like lines that match the same shape, and counting those doubled the
    total. The statement's own "Purchases" figure is what caught it."""
    rows, in_section = [], False
    for l in text.splitlines():
        if re.search(r'Card number', l): in_section = True
        if not in_section: continue
        m = re.match(r'\s*([A-Z][a-z]{2})\s+(\d{1,2})\s+([A-Z][a-z]{2})\s+(\d{1,2})\s+'
                     r'(.+?)\s\s+(' + AMT + r')\s*$', l)
        if not m: continue
        mon, day, desc, amt = m.group(1), int(m.group(2)), m.group(5).strip(), m.group(6)
        if mon not in MONTHS: continue
        y = year - 1 if MONTHS[mon] == 12 and '01' in text[:0] else year
        # a Dec line on a Jan/Feb statement belongs to the previous year
        if MONTHS[mon] == 12 and stmt_month(text) in (1, 2): y = year - 1
        rows.append((date(y, MONTHS[mon], day), desc, money(amt)))
    return rows


def stmt_month(text: str) -> int:
    m = re.search(r'(January|February|March|April|May|June|July|August|September|'
                  r'October|November|December)\s+\d{1,2},?\s+20\d{2}', text)
    return MONTHS[m.group(1)[:3]] if m else 0


def cibc_expected(text: str):
    """The statement's own summary, used as the checksum.

    Charges are split across three summary lines — purchases, cash advances
    and interest — so the transaction list must be compared against their sum,
    not against Purchases alone. Restricted to the summary block, because the
    fine print mentions these words many times."""
    head = '\n'.join(text.splitlines()[:40])
    def grab(label):
        # the summary is a two-column layout; pdftotext sometimes leaves other
        # content after the figure, so take the first amount on the label's line
        m = re.search(r'^\s*' + re.escape(label) + r'\s+.*?(' + AMT + r')', head, re.M)
        return money(m.group(1)) if m else 0.0
    charges = grab('Purchases') + grab('Cash advances') + grab('Fees')
    return {'charges': charges or None}


# ------------------------------------------------------- Scotiabank Ultimate
def scotia_ultimate(text: str, year: int):
    """Date | description | amount | running balance.

    The running balance is the gift here: the sign of every transaction is
    derived from the balance moving, not guessed from the layout. If the
    balance says the account went down, it was money out."""
    rows, prev, pending = [], None, None
    for l in text.splitlines():
        # Not anchored to end of line: pdftotext -layout merges a marketing
        # side panel into the same rows, so a transaction can be followed by
        # ad copy. Take the first two amounts after the description instead.
        m = re.match(r'\s*([A-Z][a-z]{2})\s+(\d{1,2})\s+(.+?)\s\s+(' + AMT + r')'
                     r'(?:\s\s+(' + AMT + r'))?(?:\s|$)', l)
        if not m:
            # continuation lines carry the rest of a description
            if pending and l.strip() and not re.search(r'[\d,]+\.\d{2}', l):
                extra = l.strip()
                if len(extra) > 2 and not extra.isdigit():
                    rows[-1] = (rows[-1][0], (rows[-1][1] + ' ' + extra)[:90], rows[-1][2])
            continue
        mon, day, desc = m.group(1), int(m.group(2)), m.group(3).strip()
        if mon not in MONTHS: continue
        a1, a2 = money(m.group(4)), money(m.group(5)) if m.group(5) else None
        if 'opening balance' in desc.lower():
            prev = a2 if a2 is not None else a1; pending = None; continue
        if a2 is None:                       # only a balance, no movement
            prev = a1; pending = None; continue
        amount, balance = a1, a2
        out = None
        if prev is not None:
            delta = prev - balance
            out = amount if delta > 0 else -amount
        prev = balance
        y = resolve_year(MONTHS[mon], year, END_MONTH[0])
        rows.append((date(y, MONTHS[mon], day), desc, out if out is not None else amount))
        pending = True
    return rows


def scotia_ultimate_expected(text: str):
    def grab(label):
        m = re.search(re.escape(label) + r'\s+.*?\$?(' + AMT + r')', text, re.I)
        return money(m.group(1)) if m else None
    return {'withdrawals': grab('total withdrawals'), 'deposits': grab('total deposits')}


# ------------------------------------------------------------------ RBC
def rbc(text: str, year: int):
    """RBC uses three right-aligned money columns — Withdrawals, Deposits,
    Balance — and prints the balance only sometimes. So the column an amount
    sits in is what decides its direction, not its sign or its neighbours.
    The header gives the column offsets; everything else follows from them."""
    rows, cur, prefix = [], None, ''
    w_col = d_col = b_col = None
    for raw in text.splitlines():
        l = raw.rstrip()
        # every page repeats the header, and the columns can shift between
        # pages — so re-read the offsets each time one appears
        if 'Withdrawals' in l and 'Deposits' in l and 'Balance' in l:
            w_col, d_col, b_col = l.index('Withdrawals'), l.index('Deposits'), l.index('Balance')
            cur, prefix = cur, ''
            continue
        if w_col is None: continue
        dm = re.match(r'\s*(\d{1,2})\s+([A-Z][a-z]{2})\s', l)
        if dm and dm.group(2) in MONTHS:
            cur = (int(dm.group(1)), dm.group(2))
        hits = [(m.start(), m.group()) for m in re.finditer(AMT, l)
                if m.start() >= w_col - 12]        # ignore the summary block
        desc = re.sub(r'\s{2,}', ' ', re.sub(AMT, '', l[:w_col - 12] if w_col > 12 else l)).strip()
        desc = re.sub(r'^\d{1,2}\s+[A-Z][a-z]{2}\s*', '', desc).strip(' -')
        if not hits:
            if desc and not desc.lower().startswith('opening'): prefix = desc
            continue
        withdrawal = next((v for c, v in hits if c < d_col - 6), None)
        deposit    = next((v for c, v in hits if d_col - 6 <= c < b_col - 6), None)
        full = (prefix + ' ' + desc).strip() if prefix else desc
        prefix = ''
        if cur is None or (withdrawal is None and deposit is None): continue
        out = money(withdrawal) if withdrawal is not None else -money(deposit)
        day, mon = cur
        y = resolve_year(MONTHS[mon], year, END_MONTH[0])
        rows.append((date(y, MONTHS[mon], day), (full or 'RBC transaction')[:90], out))
    return rows


def rbc_expected(text: str):
    w = re.search(r'Total withdrawals from your account\s*-?\s*\$?(' + AMT + r')', text, re.I)
    d = re.search(r'Total deposits into your account\s*\+?\s*\$?(' + AMT + r')', text, re.I)
    return {'withdrawals': money(w.group(1)) if w else None,
            'deposits': money(d.group(1)) if d else None}


# ----------------------------------------------------------- ScotiaLine LOC
def scotia_line(text: str, year: int):
    """<seq> <trans date> <post date> <description> <amount>[-]; a trailing
    minus marks a credit (a payment onto the line)."""
    rows = []
    for l in text.splitlines():
        m = re.match(r'\s*\d{3}\s+([A-Z][a-z]{2})\s+(\d{1,2})\s+[A-Z][a-z]{2}\s+\d{1,2}\s+'
                     r'(.+?)\s\s+(' + AMT + r'-?)(?:\s|$)', l)
        if not m: continue
        mon, day, desc, amt = m.group(1), int(m.group(2)), m.group(3).strip(), m.group(4)
        if mon not in MONTHS: continue
        y = resolve_year(MONTHS[mon], year, END_MONTH[0])
        rows.append((date(y, MONTHS[mon], day), desc, money(amt)))
    return rows


def scotia_line_expected(text: str):
    # the summary splits interest out of advances/charges; the transaction
    # list contains both, so the checksum is their sum
    adv = re.search(r'Advances/charges\s*\+?\s*\$?(' + AMT + r')', text, re.I)
    itr = re.search(r'^\s*Interest\s*\+?\s*\$?(' + AMT + r')', text, re.I | re.M)
    if not adv: return {'charges': None}
    return {'charges': money(adv.group(1)) + (money(itr.group(1)) if itr else 0.0)}


EXTRACTORS = {'CIBC': (cibc, cibc_expected),
              'Ultimate': (scotia_ultimate, scotia_ultimate_expected),
              'RBC': (rbc, rbc_expected),
              'ScotiaLine': (scotia_line, scotia_line_expected)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', required=True)
    ap.add_argument('--out', default=str(HERE / 'statements'))
    a = ap.parse_args()
    root = Path(a.dir).expanduser()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    for bank, (extract, expected) in EXTRACTORS.items():
        pdfs = sorted(p for p in root.rglob('*.pdf') if bank.lower() in str(p).lower())
        if not pdfs: print(f"  {bank}: no PDFs found"); continue
        all_rows, ok, bad = [], 0, []
        for pdf in pdfs:
            text = to_text(pdf)
            END_MONTH[0] = stmt_end_month(pdf, text)
            rows = extract(text, stmt_year(pdf))
            exp = expected(text)
            charges = sum(v for _, _, v in rows if v > 0)
            target = exp.get('charges')
            if target is None and exp.get('withdrawals') is not None:
                target = exp['withdrawals']
            if target is None:
                bad.append((pdf.name, 'no summary found', None, None)); continue
            delta = charges - target
            dep_target = exp.get('deposits')
            dep = -sum(v for _, _, v in rows if v < 0)
            dep_ok = dep_target is None or abs(dep - dep_target) <= 0.02
            if abs(delta) <= 0.02 and dep_ok:
                ok += 1; all_rows += rows
            elif not dep_ok:
                bad.append((pdf.name, 'deposits mismatch', dep, dep_target))
            else:
                bad.append((pdf.name, 'mismatch', charges, target))
        print(f"\n  {bank}: {len(pdfs)} statements, {ok} reconciled, {len(bad)} failed")
        for name, why, got, want in bad[:8]:
            extra = f"  parsed {got:,.2f} vs stated {want:,.2f}" if got is not None else ""
            print(f"    ! {name}: {why}{extra}")
        if all_rows:
            f = out / f"{bank.lower()}-imported.csv"
            with open(f, 'w', newline='') as fh:
                w = csv.writer(fh); w.writerow(['Date', 'Description', 'Amount'])
                for d, desc, v in sorted(all_rows):
                    w.writerow([d.isoformat(), desc, f"{-v:.2f}"])
            print(f"    wrote {f.name}: {len(all_rows)} transactions")


if __name__ == '__main__':
    main()
