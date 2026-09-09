#!/usr/bin/env python3
"""Turn a folder of bank and credit-card CSV exports into a budget.

Everything happens on this machine. Nothing is uploaded, and no credentials
are involved: you export the CSVs from online banking yourself.

    pixi run budget                      # reads ./statements/*.csv
    pixi run budget -- --dir ~/exports   # or point it somewhere else
"""
from __future__ import annotations
import argparse, csv, io, re, sys
from collections import defaultdict
from datetime import datetime, date
from pathlib import Path

import yaml

HERE = Path(__file__).parent

# Banks disagree about column names. These are the ones seen in the wild,
# English and French, across the big Canadian institutions.
DATE_H   = ('date', 'transaction date', 'posting date', 'date de transaction',
            'date d\'inscription', 'date effective')
DESC_H   = ('description', 'description 1', 'details', 'detail', 'memo', 'payee',
            'narrative', 'transaction', 'libelle', 'libellé', 'description ')
AMOUNT_H = ('amount', 'montant', 'transaction amount')
DEBIT_H  = ('debit', 'withdrawal', 'withdrawals', 'debits', 'débit', 'retrait',
            'funds out', 'money out')
CREDIT_H = ('credit', 'deposit', 'deposits', 'credits', 'crédit', 'dépôt',
            'depot', 'funds in', 'money in')

DATE_FORMATS = ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%b-%Y', '%b %d, %Y',
                '%Y/%m/%d', '%d.%m.%Y', '%m/%d/%y', '%d/%m/%y')

# The header ledger.csv is written with. A file that carries it exactly is an
# annotated ledger: someone (or their AI) has filled in kind and line, and the
# rows are labels for transactions the statements already hold, never new ones.
LEDGER_HEADER = ('date', 'description', 'amount', 'kind', 'line', 'rule')
# The kinds a label may name, and the ones the tool writes for a row it could
# not label itself. The second set is left in place when a ledger is handed
# back with only some rows filled in, so it carries no label and is not an error.
LABEL_KINDS = {'transfer', 'income', 'savings', 'spending', 'lending', 'repayment', 'passthrough'}
UNLABELLED_KINDS = {'refund', 'review', 'uncategorised'}
MONEY_OUT_KINDS, MONEY_IN_KINDS = {'spending', 'savings', 'lending'}, {'income', 'repayment'}


def pick_delimiter(text: str) -> str:
    """Most consistent delimiter across the first rows. csv.Sniffer gets this
    wrong on short semicolon files and silently returns one column."""
    lines = [l for l in text.splitlines()[:12] if l.strip()]
    best, best_score = ',', -1
    for d in (',', ';', '\t', '|'):
        counts = [l.count(d) for l in lines]
        if not counts or counts[0] == 0: continue
        score = counts[0] * (2 if len(set(counts)) == 1 else 1)
        if score > best_score: best, best_score = d, score
    return best


NUMERIC_DATE = re.compile(r'^\s*(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2,4})')


def infer_date_order(samples):
    """DMY, MDY, or None when the file is genuinely ambiguous.

    A day past the 12th in the first position proves day-first; one in the
    second proves month-first. If neither appears, no amount of staring at
    the file will tell you — so the caller must ask rather than guess."""
    a = b = 0
    for s in samples:
        m = NUMERIC_DATE.match(s or '')
        if m: a, b = max(a, int(m.group(1))), max(b, int(m.group(2)))
    if a > 12: return 'DMY'
    if b > 12: return 'MDY'
    return None


def parse_date(s: str, order: str | None = None):
    s = (s or '').strip().strip('"')
    if order and NUMERIC_DATE.match(s):
        seps = ('%d/%m/%Y', '%d.%m.%Y', '%d-%m-%Y') if order == 'DMY' else \
               ('%m/%d/%Y', '%m.%d.%Y', '%m-%d-%Y')
        for f in seps + tuple(x.replace('Y', 'y') for x in seps):
            try: return datetime.strptime(s, f).date()
            except ValueError: pass
    for f in DATE_FORMATS:
        try: return datetime.strptime(s, f).date()
        except ValueError: pass
    return None


def parse_amount(s: str):
    if s is None: return None
    s = s.strip().replace('$', '').replace(' ', '').replace(' ', '')
    if not s: return None
    neg = s.startswith('(') and s.endswith(')')
    s = s.strip('()')
    # 1.234,56 (fr) vs 1,234.56 (en)
    if ',' in s and '.' in s:
        s = s.replace(',', '') if s.rfind('.') > s.rfind(',') else s.replace('.', '').replace(',', '.')
    elif ',' in s:
        s = s.replace(',', '.') if len(s.split(',')[-1]) == 2 else s.replace(',', '')
    try: v = float(s)
    except ValueError: return None
    return -v if neg else v


def norm(h: str) -> str:
    return re.sub(r'\s+', ' ', (h or '').strip().lower())


def decode(raw: bytes) -> str | None:
    """Banks export in whichever encoding their vendor chose; try the usual ones."""
    for enc in ('utf-8-sig', 'utf-8', 'cp1252', 'latin-1'):
        try: return raw.decode(enc)
        except UnicodeDecodeError: continue
    return None


def read_csv(path: Path, forced_order=None):
    """Yield (date, description, amount) with amount POSITIVE for money out."""
    text = decode(path.read_bytes())
    if text is None:
        print(f"  ! {path.name}: cannot decode", file=sys.stderr); return

    rows = list(csv.reader(io.StringIO(text), delimiter=pick_delimiter(text)))
    if not rows: return
    header = [norm(c) for c in rows[0]]
    # an annotated ledger has a date, a description and an amount column too,
    # and would parse as a statement; recognise it before inferring anything
    if header == list(LEDGER_HEADER): return
    has_header = any(h in DATE_H for h in header) or any(
        h in DESC_H or h in AMOUNT_H or h in DEBIT_H for h in header)

    if has_header:
        idx = {name: i for i, name in enumerate(header)}
        di = next((idx[h] for h in DATE_H if h in idx), None)
        si = next((idx[h] for h in DESC_H if h in idx), None)
        ai = next((idx[h] for h in AMOUNT_H if h in idx), None)
        wi = next((idx[h] for h in DEBIT_H if h in idx), None)
        ci = next((idx[h] for h in CREDIT_H if h in idx), None)
        body = rows[1:]
    else:
        # Headerless (several banks do this). Infer by shape.
        di = si = ai = wi = ci = None
        for i, cell in enumerate(rows[0]):
            if di is None and parse_date(cell): di = i
        cand = [i for i, c in enumerate(rows[0]) if parse_amount(c) is not None and i != di]
        if len(cand) >= 2: wi, ci = cand[0], cand[1]
        elif cand: ai = cand[0]
        si = next((i for i, c in enumerate(rows[0])
                   if i not in (di, ai, wi, ci) and any(ch.isalpha() for ch in c)), None)
        body = rows

    if di is None or si is None or (ai is None and wi is None):
        print(f"  ! {path.name}: could not identify date/description/amount columns",
              file=sys.stderr)
        return

    order = infer_date_order([r[di] for r in body if len(r) > di]) or forced_order
    if order is None and any(NUMERIC_DATE.match((r[di] or '')) for r in body if len(r) > di):
        print(f"  ? {path.name}: ambiguous date format (no day past the 12th). "
              f"Assuming day/month; pass --date-order mdy if that is wrong.",
              file=sys.stderr)
        order = 'DMY'

    for r in body:
        if len(r) <= max(x for x in (di, si, ai, wi, ci) if x is not None): continue
        d = parse_date(r[di], order)
        if not d: continue
        desc = re.sub(r'\s+', ' ', r[si]).strip()
        if ai is not None:
            amt = parse_amount(r[ai])
            if amt is None: continue
            # convention differs; a majority-negative column means outflow<0
            out = -amt
        else:
            debit = parse_amount(r[wi]) if wi is not None else None
            credit = parse_amount(r[ci]) if ci is not None else None
            out = (debit or 0) - (credit or 0)
        yield d, desc, out


def read_annotations(path: Path):
    """The rows of an annotated ledger as dicts keyed by the ledger header, or
    None when the file is not one. Recognition is by the exact header and
    nothing else, so a statement is never taken for annotations."""
    text = decode(path.read_bytes())
    if text is None: return None
    rows = list(csv.reader(io.StringIO(text), delimiter=pick_delimiter(text)))
    if not rows or [norm(c) for c in rows[0]] != list(LEDGER_HEADER): return None
    width = len(LEDGER_HEADER)
    return [dict(zip(LEDGER_HEADER, (r + [''] * width)[:width]))
            for r in rows[1:] if any(c.strip() for c in r)]


def verify_annotations(rows, txns, cat_defs, year=None):
    """Check every annotated row against the transactions the statements gave
    and against categories.yml. Returns (labels, offenders): labels keyed by
    (date, description, amount signed like the bank) -> (kind, line), and one
    printable line per row that cannot be applied. A single offender means the
    caller applies none of the labels — a shifted amount or a dropped row is
    exactly what this pass exists to catch, and partial acceptance would hide it.

    The match is date, description with runs of whitespace collapsed (a
    spreadsheet round trip changes nothing else), and amount to the cent."""
    keys = {(d, desc, round(-out, 2)) for d, desc, out, _ in txns}
    by_row = defaultdict(list)   # (date, description) -> amounts, to say what differs
    for d, desc, out, _ in txns: by_row[(d, desc)].append(-out)
    savings_lines = set(cat_defs.get('savings', {}).get('lines', []))
    all_lines = savings_lines | {l for g in cat_defs.get('expenses', {}).values()
                                 for l in g.get('lines', [])}
    labels, offenders = {}, []
    for r in rows:
        d, amt = parse_date(r['date']), parse_amount(r['amount'])
        desc = re.sub(r'\s+', ' ', r['description']).strip()
        kind, line = r['kind'].strip(), r['line'].strip()
        shown = f"{r['date'].strip()}  {desc}  {r['amount'].strip()}"
        def refuse(why): offenders.append(f"{shown}  — {why}")
        if d is None or amt is None:
            refuse("date or amount not readable"); continue
        if year and d.year != year: continue   # outside the window asked for, like any statement row
        amt = round(amt, 2)
        if (d, desc, amt) not in keys:
            others = by_row.get((d, desc))
            refuse(f"amount differs from the statement's {others[0]:.2f}" if others
                   else "no matching transaction in the statements"); continue
        if kind in UNLABELLED_KINDS: continue   # the tool's own verdict, handed back unchanged
        if kind not in LABEL_KINDS:
            refuse(f"kind '{kind}' is not one of {', '.join(sorted(LABEL_KINDS))}"); continue
        if kind == 'spending' and not line:
            refuse("spending needs a line from categories.yml"); continue
        if kind == 'spending' and line not in all_lines:
            refuse(f"line '{line}' is not in categories.yml"); continue
        if kind == 'savings' and line not in savings_lines:
            refuse("savings needs a line listed under savings in categories.yml"); continue
        if kind in MONEY_OUT_KINDS and amt > 0:
            refuse(f"'{kind}' is money out, but this row is money in"); continue
        if kind in MONEY_IN_KINDS and amt < 0:
            refuse(f"'{kind}' is money in, but this row is money out"); continue
        labels[(d, desc, amt)] = (kind, line)
    return labels, offenders


def compile_rules(rules):
    cats = [(line, [re.compile(p, re.I) for p in pats])
            for line, pats in rules.get('categories', {}).items()]
    bank = [(re.compile(re.escape(k) + r'\s*$', re.I), v)
            for k, v in (rules.get('bank_categories') or {}).items()]
    return (cats,
            [re.compile(p, re.I) for p in rules.get('transfers', [])],
            [re.compile(p, re.I) for p in rules.get('income', [])],
            bank)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dir', default=str(HERE / 'statements'))
    ap.add_argument('--config', default=str(HERE),
                    help='folder holding rules.yml, loans.yml, known-annual.yml '
                         '(default: beside budget.py); the examples fill in for any missing one')
    ap.add_argument('--year', type=int, help='keep only this calendar year')
    ap.add_argument('--out', default=str(HERE / 'budget.md'))
    ap.add_argument('--date-order', choices=['dmy', 'mdy'],
                    help='force date interpretation when a file is ambiguous')
    ap.add_argument('--lumpy', type=float, default=1000.0,
                    help='transactions at or above this are treated as irregular '
                         'and reported individually rather than averaged (default 1000)')
    a = ap.parse_args(argv)

    def cfg(name):
        """Your own file if you have made one, else the committed example.
        The personal files are gitignored: they describe your money."""
        f = Path(a.config) / f'{name}.yml'
        return f if f.exists() else HERE / f'{name}.example.yml'

    cat_defs = yaml.safe_load((HERE / 'categories.yml').read_text())
    cats, transfer_pats, income_pats, bank_cats = compile_rules(
        yaml.safe_load(cfg('rules').read_text()))
    _rules_yaml = yaml.safe_load(cfg('rules').read_text())
    passthrough = {(str(x['date']), round(float(x['amount']), 2))
                   for x in (_rules_yaml.get('passthrough') or [])}
    one_off = {(str(x['date']), round(float(x['amount']), 2)): x.get('note', '')
               for x in (_rules_yaml.get('one_off') or [])}
    dated_rules = {(str(x['date']), round(float(x['amount']), 2)): x['line']
                   for x in (yaml.safe_load(cfg('rules').read_text())
                             .get('dated') or [])}
    loans_f = cfg('loans')
    loans_cfg = (yaml.safe_load(loans_f.read_text()) or {}) if loans_f.exists() else {}

    files = sorted(Path(a.dir).glob('*.csv'))
    if not files:
        sys.exit(f"No CSVs in {a.dir}. Export them from online banking first.")
    # an annotated ledger labels transactions; it never supplies them, so it
    # is set apart here and the statement files are what remain
    annotated = {}
    for f in files:
        rows = read_annotations(f)
        if rows is not None: annotated[f] = rows
    files = [f for f in files if f not in annotated]
    if not files:
        sys.exit(f"{', '.join(f.name for f in annotated)}: an annotated ledger labels transactions, "
                 f"it does not add them. Annotations need the original exports beside them.")

    seen, txns, dropped = set(), [], 0
    for f in files:
        for d, desc, out in read_csv(f, (a.date_order or '').upper() or None):
            if a.year and d.year != a.year: continue
            key = (d, desc.lower(), round(out, 2))
            if key in seen: dropped += 1; continue   # same txn in two exports
            seen.add(key)
            txns.append((d, desc, out, f.name))

    if not txns: sys.exit("No transactions parsed. Check --year and the CSV format.")

    # Verify each annotated file against the de-duplicated transactions. All or
    # nothing per file: one bad row refuses it and the run goes on without it.
    labels, applied = {}, {}   # applied: file name -> rows whose label was used
    for f, rows in annotated.items():
        found, offenders = verify_annotations(rows, txns, cat_defs, a.year)
        if offenders:
            print(f"  ! {f.name}: refused — {len(offenders)} of {len(rows)} rows cannot be "
                  f"applied, so none were:", file=sys.stderr)
            for line in offenders[:10]: print(f"      {line}", file=sys.stderr)
            if len(offenders) > 10: print(f"      and {len(offenders) - 10} more", file=sys.stderr)
            continue
        labels.update({k: (kind, line, f.name) for k, (kind, line) in found.items()})
        applied[f.name] = 0

    totals, uncategorised, from_bank = defaultdict(float), [], defaultdict(float)
    savings_lines = set(cat_defs.get('savings', {}).get('lines', []))
    savings = defaultdict(float)
    transfers_total = income_total = 0.0
    review_pats = [re.compile(p, re.I) for p in (loans_cfg.get('review') or [])]
    review_min = float(loans_cfg.get('review_min', 0))
    disb = {(str(x['date']), round(float(x['amount']), 2))
            for x in (loans_cfg.get('disbursements') or [])}
    recv = {(str(x['date']), round(float(x['amount']), 2))
            for x in (loans_cfg.get('receipts') or [])}
    # a ledger entry the statements cannot confirm is worth saying out loud,
    # rather than quietly counting or quietly dropping
    matched = set()
    cparty = [(c['name'], re.compile(c['match'], re.I))
              for c in (loans_cfg.get('counterparties') or [])]
    cparty_flow = defaultdict(lambda: [0.0, 0.0])   # name -> [out, in]
    lent_out = repaid_in = passthrough_total = 0.0
    review = []
    income_month = defaultdict(float)
    spend_txns = []   # only what survives as real spending
    # every transaction, the kind it was judged to be, and the rule that judged
    # it — written to ledger.csv, counted under SET ASIDE, asserted by the tests
    ledger = []
    def note(d, desc, out, kind, line='', rule=''):
        ledger.append((d, desc, -out, kind, line, rule))   # signed like the bank
    CARD_OUT = re.compile(r'credit\s*card|visa|master\s*card|amex', re.I)
    CARD_IN = re.compile(r'payment.*(thank you|received)', re.I)
    card_out = card_in = 0.0
    def apply_label(d, desc, out, src):
        """A verified annotated label, applied as the loop's own branch would
        apply it, with rule 'annotated'. Sits after the date-and-amount pins
        and before every pattern; a dated pin on the same transaction still
        wins, so the label is left for the pin to overrule further down."""
        nonlocal passthrough_total, lent_out, repaid_in, transfers_total, income_total, card_out, card_in
        hit = labels.get((d, desc, round(-out, 2)))
        if hit is None or (d.isoformat(), round(out, 2)) in dated_rules: return False
        kind, line, origin = hit
        if kind == 'passthrough': passthrough_total += abs(out); note(d, desc, out, kind, rule='annotated')
        elif kind == 'lending':   lent_out += out; note(d, desc, out, kind, rule='annotated')
        elif kind == 'repayment': repaid_in += -out; note(d, desc, out, kind, rule='annotated')
        elif kind == 'transfer':
            transfers_total += abs(out); note(d, desc, out, kind, rule='annotated')
            if out > 0 and CARD_OUT.search(desc): card_out += out
            if out < 0 and CARD_IN.search(desc): card_in += -out
        elif kind == 'income':
            income_total += -out; income_month[f"{d.year}-{d.month:02d}"] += -out
            note(d, desc, out, kind, rule='annotated')
        elif line in savings_lines:   # the line decides, as it does for a pattern
            savings[line] += out; note(d, desc, out, 'savings', line, 'annotated')
        else:
            spend_txns.append((d, desc, out, src)); totals[line] += out
            note(d, desc, out, 'spending', line, 'annotated')
        applied[origin] += 1
        return True
    for d, desc, out, src in txns:
        if (d.isoformat(), round(abs(out), 2)) in passthrough:
            passthrough_total += abs(out); note(d, desc, out, 'passthrough', rule='pin'); continue
        hit = next((n for n, pat in cparty if pat.search(desc)), None)
        if hit:
            if out > 0: lent_out += out; cparty_flow[hit][0] += out; note(d, desc, out, 'lending', rule=f'counterparty:{hit}')
            else:       repaid_in += -out; cparty_flow[hit][1] += -out; note(d, desc, out, 'repayment', rule=f'counterparty:{hit}')
            continue
        if (d.isoformat(), round(out, 2)) in disb:
            lent_out += out; matched.add((d.isoformat(), round(out, 2))); note(d, desc, out, 'lending', rule='pin'); continue
        if (d.isoformat(), round(-out, 2)) in recv:
            repaid_in += -out; matched.add((d.isoformat(), round(-out, 2))); note(d, desc, out, 'repayment', rule='pin'); continue
        if labels and apply_label(d, desc, out, src): continue
        if any(p.search(desc) for p in transfer_pats):
            transfers_total += abs(out); note(d, desc, out, 'transfer', rule='transfer pattern')
            if out > 0 and CARD_OUT.search(desc): card_out += out
            if out < 0 and CARD_IN.search(desc): card_in += -out
            continue
        if out < 0:
            if any(p.search(desc) for p in income_pats):
                income_total += -out
                income_month[f"{d.year}-{d.month:02d}"] += -out
                note(d, desc, out, 'income', rule='income pattern')
            else:
                note(d, desc, out, 'refund')          # other inflows: refunds
            continue
        spend_txns.append((d, desc, out, src))
        line = dated_rules.get((d.isoformat(), round(out, 2)))
        rule = 'dated pin' if line else ''
        if line is None:
            line = next((l for l, pats in cats if any(p.search(desc) for p in pats)), None)
            rule = 'category pattern' if line else ''
        if line in savings_lines:
            savings[line] += out; spend_txns.pop(); note(d, desc, out, 'savings', line, rule); continue
        if line:
            totals[line] += out; note(d, desc, out, 'spending', line, rule)
        else:
            line = next((v for pat, v in bank_cats if pat.search(desc)), None)
            if line:
                totals[line] += out; from_bank[line] += out; note(d, desc, out, 'spending', line, 'bank category')
            elif (review_pats and out >= review_min
                  and any(p.search(desc) for p in review_pats)):
                # only an outflow nothing else could name goes to review
                spend_txns.pop(); review.append((d, desc, out)); note(d, desc, out, 'review', rule='review pattern')
            else:
                uncategorised.append((d, desc, out, src)); note(d, desc, out, 'uncategorised')
    kind_count = defaultdict(int)
    for row in ledger: kind_count[row[3]] += 1

    lo, hi = min(t[0] for t in txns), max(t[0] for t in txns)
    span = (hi - lo).days + 1
    months = max(span / 30.44, 1)

    def complete_months(lo, hi):
        """Months fully inside the observed window. A statement ending on the
        20th does not give you that month; counting it drags the average."""
        import calendar
        out = []
        y, m = lo.year, lo.month
        while (y, m) <= (hi.year, hi.month):
            last = calendar.monthrange(y, m)[1]
            if date(y, m, 1) >= lo and date(y, m, last) <= hi:
                out.append(f"{y}-{m:02d}")
            m += 1
            if m == 13: y, m = y + 1, 1
        return out
    spend = sum(totals.values()) + sum(t[2] for t in uncategorised)
    whole = complete_months(lo, hi)
    # Three states, and the annual figure exists only in the first. Seven
    # weeks printed in the same form as eight months is how a tool lies.
    state = 'MEASURED' if len(whole) >= 3 else 'ESTIMATE' if whole else 'UNKNOWN'

    # ---- the budget table, in the intake form's structure -------------------
    lines = ["# Budget", "",
             f"Generated from {len(files)} statement file(s), {len(txns)} transactions, "
             f"{min(t[0] for t in txns)} to {max(t[0] for t in txns)}.", "",
             {'MEASURED': f"**{state}** — {len(whole)} complete calendar months.",
              'ESTIMATE': f"**{state}** — only {len(whole)} complete calendar month(s); "
                          f"an annual figure needs three. Monthly figures below are averages over the window.",
              'UNKNOWN': f"**{state}** — no complete calendar month in the window. "
                         f"The tables below total what was seen; nothing here is a monthly rate."}[state],
             ""]
    for key, grp in cat_defs['expenses'].items():
        rows = [(l, totals.get(l, 0.0)) for l in grp['lines'] if totals.get(l, 0.0)]
        if not rows: continue
        lines += [f"## {grp['label']}", "", "| Line | In window | Per month |", "|---|---:|---:|"]
        lines += [f"| {l}{' ᵇ' if from_bank.get(l) else ''} | {v:,.0f} | {v/months:,.0f} |"
                  for l, v in rows]
        sub = sum(v for _, v in rows)
        lines += [f"| **Total {grp['label'].lower()}** | **{sub:,.0f}** | **{sub/months:,.0f}** |", ""]
    if uncategorised:
        u = sum(t[2] for t in uncategorised)
        lines += ["## Uncategorised", "",
                  f"| Not yet matched | {u:,.0f} | {u/months:,.0f} |", "|---|---:|---:|", ""]
    lines += ["## Result", "",
              f"| | In window | Per month |", "|---|---:|---:|",
              f"| **Total expenses** | **{spend:,.0f}** | **{spend/months:,.0f}** |"]
    if income_total:
        lines.append(f"| Income seen | {income_total:,.0f} | {income_total/months:,.0f} |")
    if from_bank:
        lines += ["", "ᵇ *filled from the bank's own coarse category, not a specific "
                  "rule — refine in rules.yml if the split matters.*"]
    lines += ["", f"*Excluded as transfers between your own accounts: "
                  f"{transfers_total:,.0f}. Counting these would double every dollar "
                  f"you put on a credit card.*", ""]
    md_tail = lines   # the arithmetic section is appended once it exists

    if uncategorised:
        by_desc = defaultdict(float)
        for _, desc, out, _ in uncategorised: by_desc[desc] += out
        with open(Path(a.out).parent / 'uncategorised.csv', 'w', newline='') as fh:
            w = csv.writer(fh); w.writerow(['total', 'description'])
            for desc, v in sorted(by_desc.items(), key=lambda x: -x[1]):
                w.writerow([f"{v:.2f}", desc])

    pct = 100 * (spend - sum(t[2] for t in uncategorised)) / spend if spend else 0

    # A few months is enough to pin the RECURRING baseline; it is never enough
    # to infer the irregular items, and neither is a year — you either saw the
    # insurance renewal or you did not. So separate them and ask about the rest.
    def signature(desc):
        """Description with reference numbers stripped, so the same recurring
        payment matches itself month to month."""
        d = re.sub(r'[#\d]{3,}', '', desc.lower())
        # first few words only: "Mortgage payment #4985" and "Mortgage payment
        # Term Life, Travel, Accident" are the same standing payment
        return ' '.join(re.sub(r'[^a-z ]', ' ', d).split()[:2])

    # Size alone is the wrong test: a mortgage is large AND perfectly regular.
    # Something is irregular only if it is large and does NOT repeat.
    months_seen = defaultdict(set)
    for d, desc, out, _ in spend_txns:
        if out > 0: months_seen[signature(desc)].add((d.year, d.month))
    recurring_sig = {k for k, v in months_seen.items() if len(v) >= 3}
    lumpy = sorted((t for t in spend_txns
                    if t[2] >= a.lumpy and signature(t[1]) not in recurring_sig),
                   key=lambda t: -t[2])
    # A month-end payment that clears on the 1st lands in the wrong bucket.
    # Charge these at their monthly rate instead of on the date they cleared.
    level_pats = [(re.compile(r['match'], re.I), r.get('note', ''))
                  for r in (_rules_yaml.get('level') or [])]
    def levelled(desc): return next((n for p, n in level_pats if p.search(desc)), None)
    levels = defaultdict(lambda: [0.0, 0])
    for d, desc, out, _ in spend_txns:
        note = levelled(desc)
        if note is not None and out > 0 and f"{d.year}-{d.month:02d}" in whole:
            levels[note][0] += out; levels[note][1] += 1
    # too few payments to call it monthly — leave them where they fell
    levels = {n: v for n, v in levels.items() if v[1] >= 3}
    lumpy = [t for t in lumpy if levelled(t[1]) not in levels]

    per_month = defaultdict(float)
    for d, desc, out, _ in spend_txns:
        if out > 0 and levelled(desc) in levels: continue
        if out > 0 and (out < a.lumpy or signature(desc) in recurring_sig):
            per_month[f"{d.year}-{d.month:02d}"] += out
    for note, (total, n) in levels.items():
        for m in whole: per_month[m] += total / len(whole)
    vals = sorted(per_month[m] for m in whole) or [0]
    median = vals[len(vals)//2] if len(vals) % 2 else (vals[len(vals)//2-1]+vals[len(vals)//2])/2
    baseline = median * 12
    # the month or months the median is made of — shown, not asserted
    order = sorted(whole, key=lambda m: per_month[m])
    median_months = ({order[len(order)//2]} if len(order) % 2 else
                     {order[len(order)//2-1], order[len(order)//2]}) if order else set()
    one_year = len({m[:4] for m in whole}) <= 1
    def mon(m): return datetime.strptime(m, '%Y-%m').strftime('%b' if one_year else '%b %Y')
    months_line = ' · '.join(f"{mon(m)} {per_month[m]:,.0f}{'*' if m in median_months else ''}" for m in whole)

    known_f = cfg('known-annual')
    known = {k: float(v) for k, v in (yaml.safe_load(known_f.read_text()) or {}).items()} \
            if known_f.exists() else {}

    # Half the card payments leaving chequing never arrive on a card export:
    # the card is missing, and every figure below would be wrong. Say so first.
    if card_out and card_in < 0.5 * card_out:
        print(f"  COVERAGE    ${card_out:,.0f} of credit-card payments leave these accounts, but card")
        print(f"              exports show only ${card_in:,.0f} arriving. A card's export is missing —")
        print(f"              without it the card's purchases are invisible and the figures below")
        print(f"              are wrong. Export every card you pay from these accounts, then re-run.")
        print()
    print(f"  files {len(files)}   transactions {len(txns)}   duplicates dropped {dropped}")
    for name, n in applied.items():
        print(f"  annotated   {name} — {n} row{'s' if n != 1 else ''} applied")
    print(f"  categorised {pct:.0f}% of spending")
    print(f"  observed {lo} to {hi}  ({len(whole)} complete month(s))")
    print()
    for lnote, (total, n) in sorted(levels.items()):
        print(f"  LEVELLED    ${total/len(whole):,.0f}/month — {lnote}")
        print(f"              ${total:,.0f} over {n} transfer(s) in {len(whole)} months — a transfer "
              f"cap can split the bigger ones, and a month-end")
        print(f"              payment often clears on the 1st; charged monthly instead of on "
              f"the dates they cleared")
        legs = [(d, out) for d, desc, out, _ in sorted(spend_txns)
                if out > 0 and levelled(desc) == lnote and f"{d.year}-{d.month:02d}" in whole]
        print(f"              {' · '.join(f'{d.strftime('%b %-d')} {out:,.0f}' for d, out in legs)}")
        print()
    if state == 'MEASURED':
        print(f"  RECURRING   ${median:,.0f}/month   ->  ${baseline:,.0f}/year   MEASURED over {len(whole)} complete months")
    elif state == 'ESTIMATE':
        print(f"  RECURRING   ${median:,.0f}/month   ESTIMATE — {len(whole)} complete month(s); an annual figure needs three")
    else:
        print(f"  RECURRING   UNKNOWN — no complete calendar month between {lo} and {hi}.")
        print(f"              Export whole months; a month that starts or ends mid-way is not a month.")
    if whole:
        print(f"              {months_line}")
        print(f"              (* the median{'s' if len(median_months) > 1 else ''}; complete months only)")
    if len(vals) > 1:
        hi_r = max(vals) / median if median else 0
        lo_r = min(vals) / median if median else 0
        steady = hi_r <= 1.35 and lo_r >= 0.75
        print(f"              months ranged ${min(vals):,.0f}-${max(vals):,.0f} "
              f"({lo_r:.0%}-{hi_r:.0%} of median); "
              f"{'steady' if steady else 'UNEVEN — the annual figure is soft'}")
    decided = [t for t in lumpy if (t[0].isoformat(), round(t[2], 2)) in one_off]
    lumpy = [t for t in lumpy if (t[0].isoformat(), round(t[2], 2)) not in one_off]
    if decided:
        print()
        print(f"  ONE-OFF     {len(decided)} item(s) you have judged one-time, "
              f"held out of the average:")
        for d, desc, out, _ in decided:
            print(f"              {d}  ${out:>9,.0f}  {desc[:44]}")
            print(f"                          {one_off[(d.isoformat(), round(out, 2))]}")
    if lumpy:
        print()
        print(f"  IRREGULAR   {len(lumpy)} transaction(s) at or above ${a.lumpy:,.0f}, "
              f"held out of the average and not yet decided:")
        for d, desc, out, _ in lumpy[:8]:
            print(f"              {d}  ${out:>9,.0f}  {desc[:44]}")
        print(f"              Decide for each: one-off, yearly, or the start of a "
              f"monthly payment. Averaging them is what makes a short window lie.")
    if lent_out or repaid_in or loans_cfg.get('lent'):
        print()
        print(f"  LENDING     not spending, and not income when it comes back")
        if lent_out:  print(f"              lent out in this window      ${lent_out:>10,.0f}")
        if repaid_in: print(f"              repaid in this window        ${repaid_in:>10,.0f}")
        unseen = [(k, v) for k, v in (disb | recv) - matched]
        if unseen:
            print(f"              recorded but not in these statements:")
            for k, v in sorted(unseen):
                print(f"                {k}  ${v:>10,.0f}  outside the exported window")
        for n, (o, i) in cparty_flow.items():
            print(f"              {n:<24s} ${o:>10,.0f} out, ${i:,.0f} back "
                  f"this window (opening position unknown)")
        book = loans_cfg.get('lent') or []
        if book:
            owed = sum(float(x['principal']) - float(x.get('repaid', 0)) for x in book)
            for x in book:
                out_ = float(x['principal']) - float(x.get('repaid', 0))
                print(f"              {x['to']:<24s} ${out_:>10,.0f} outstanding "
                      f"of ${float(x['principal']):,.0f}")
            print(f"              {'TOTAL OUTSTANDING':<24s} ${owed:>10,.0f}  "
                  f"an asset, but unsecured and earning nothing")
    if known:
        print()
        print(f"  KNOWN YEARLY  from known-annual.yml, not from your statements:")
        for k, v in known.items(): print(f"              {k:28s} ${v:>9,.0f}")
    if savings:
        stot = sum(savings.values())
        smonth = stot / len(whole) if whole else 0
        print()
        if state == 'MEASURED':
            print(f"  SAVINGS     ${smonth:,.0f}/month  ->  ${smonth*12:,.0f}/year")
        else:
            print(f"  SAVINGS     ${smonth:,.0f}/month   {state} — no annual figure yet")
        for k, v in sorted(savings.items(), key=lambda x: -x[1]):
            print(f"              {k:<28s} ${v:>10,.0f} over the window")
        print(f"              not spending — it moves money, it does not consume it")

    if income_total:
        ivals = sorted(income_month[m] for m in whole) or [0]
        imed = ivals[len(ivals)//2] if len(ivals) % 2 else (ivals[len(ivals)//2-1]+ivals[len(ivals)//2])/2
        print()
        if state == 'MEASURED':
            print(f"  INCOME      ${imed:,.0f}/month (median)  ->  ${imed*12:,.0f}/year")
        else:
            print(f"  INCOME      ${imed:,.0f}/month (median)   {state} — no annual figure yet")
        print(f"              ${income_total:,.0f} identified over the window; "
              f"months ranged ${min(ivals):,.0f}-${max(ivals):,.0f}")
        srate = (sum(savings.values()) / len(whole) * 12 / (imed * 12) * 100
                 if savings and whole and imed else 0)
        if srate: print(f"              savings rate {srate:.1f}% of income")
        gap = imed * 12 - baseline
        if state == 'MEASURED':
            print(f"              against ${baseline:,.0f} of recurring spending, "
                  f"a surplus of ${gap:,.0f}/year" if gap > 0 else
                  f"              against ${baseline:,.0f} of recurring spending, "
                  f"a SHORTFALL of ${-gap:,.0f}/year")

    if review:
        by = defaultdict(float)
        for d, desc, v in review: by[signature(desc)] += v
        print()
        print(f"  NEEDS IDENTIFYING  {len(review)} outflow(s), "
              f"${sum(v for _, _, v in review):,.0f} — counted as neither "
              f"spending nor lending:")
        for sig, v in sorted(by.items(), key=lambda x: -x[1])[:6]:
            print(f"              ${v:>10,.0f}  {sig}")
        print(f"              Tell me which are loans and I will add them to "
              f"loans.yml as dated disbursements.")

    set_aside = [('lending (an asset, not spending)', lent_out, kind_count['lending']),
                 ('pass-throughs (in and straight out)', passthrough_total, kind_count['passthrough']),
                 ('awaiting identification', sum(v for _, _, v in review), kind_count['review']),
                 ('transfers between your own accounts', transfers_total, kind_count['transfer']),
                 ('still unidentified', sum(t[2] for t in uncategorised), kind_count['uncategorised'])]
    set_aside = [(k, v, n) for k, v, n in set_aside if v]
    if set_aside:
        print()
        print(f"  SET ASIDE   money that moved but was not spending:")
        for k, v, n in set_aside:
            print(f"              {k:<38s} ${v:>10,.0f}   {n:>3} transaction{'s' if n != 1 else ''}")
        print(f"              {'':38s} {'-'*11}")
        print(f"              {'total held out':<38s} ${sum(v for _, v, _ in set_aside):>10,.0f}")

    total = baseline + sum(known.values())
    print()
    if state == 'MEASURED':
        print(f"  PLANNING FIGURE  ${total:,.0f}/year  =  recurring ${baseline:,.0f}"
              + (f" + known yearly ${sum(known.values()):,.0f}" if known else ""))
        print(f"  Add any irregular item you decide is yearly to known-annual.yml and re-run.")
    elif state == 'ESTIMATE':
        print(f"  PLANNING FIGURE  not yet — an annual figure needs three complete months; "
              f"{len(whole)} observed.")
        print(f"  What can be said: about ${median:,.0f}/month recurring so far, from what was categorised.")
    else:
        print(f"  PLANNING FIGURE  not yet — no complete month observed. Export whole months and re-run.")

    # ---- how the number was made, appended to budget.md ------------------
    md = md_tail + ["## How the number was made", ""]
    if whole:
        md += [f"Recurring is the median of {len(whole)} complete calendar months, "
               f"large one-time items held out{', levelled obligations charged monthly' if levels else ''}:", "",
               "| Month | Recurring | |", "|---|---:|---|"]
        md += [f"| {m} | {per_month[m]:,.0f} | {'median' if m in median_months else ''} |" for m in whole]
        md += ["", f"Median {median:,.0f} per month" + (f"; {baseline:,.0f} per year." if state == 'MEASURED' else ".")]
    else:
        md += ["No complete calendar month was observed, so there is no recurring figure."]
    if set_aside:
        md += ["", "Set aside, not spending:", "", "| | Amount | Transactions |", "|---|---:|---:|"]
        md += [f"| {k} | {v:,.0f} | {n} |" for k, v, n in set_aside]
    md += ["", f"Every transaction, its kind and the rule that decided it: `ledger.csv`.", ""]
    Path(a.out).write_text("\n".join(md) + "\n")
    with open(Path(a.out).parent / 'ledger.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['date', 'description', 'amount', 'kind', 'line', 'rule'])
        for d, desc, amt, kind, line, rule in sorted(ledger):
            w.writerow([d.isoformat(), desc, f"{amt:.2f}", kind, line, rule])
    print(f"  wrote {a.out}")
    if uncategorised:
        print(f"  wrote uncategorised.csv — {len(by_desc)} descriptions, "
              f"${sum(by_desc.values()):,.0f}. Add rules for the top few and re-run.")


def run(argv):
    """Run with CLI arguments and return the console report as text — the entry
    point the browser build uses. A refusal (no CSVs, an ambiguous date file)
    comes back as the message rather than a process exit."""
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            main(list(argv))
        except SystemExit as e:
            if e.code not in (None, 0):
                print(e.code)
    return buf.getvalue()


if __name__ == '__main__':
    main()
