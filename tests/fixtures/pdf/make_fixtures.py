"""Invented statements as positioned text fragments, one per supported bank.

    python tests/fixtures/pdf/make_fixtures.py     # rewrites the files beside it

Each bank gets two files: `<bank>.json`, the pages of text items the browser
would get from pdf.js for the statement (string, x, y, width, height, and
the rotation for text printed sideways), and `<bank>.csv`, the transactions
the statement must yield. Both come from the same invented rows below, so
the CSV is what the statement says and not what the extractor happened to
produce. Every name, date and amount is made up; the layouts copy only the
shape of each bank's statement — which columns exist, how amounts are
aligned, where the totals are printed — and nothing from any real one.

The typesetter is deliberately crude: a proportional width per character,
right alignment by subtracting the width, one fragment per cell as pdf.js
returns them. It is enough to exercise what pdf_layout.py must get right:
the baseline clustering, the column mapping, the join of split words, and
the sideways serial number a statement prints in its margin.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE_W, PAGE_H = 612, 792
BODY = 9.0

# Advance widths in em for a Helvetica-like face. Anything else is 0.55.
EM = {' ': 0.278, '.': 0.278, ',': 0.278, ':': 0.278, '/': 0.278, "'": 0.191,
      '-': 0.333, '(': 0.333, ')': 0.333, '*': 0.389, '$': 0.556, '#': 0.556,
      '&': 0.667, '+': 0.584, '=': 0.584, '@': 1.015,
      'I': 0.278, 'J': 0.5, 'M': 0.833, 'W': 0.944,
      'i': 0.222, 'j': 0.222, 'l': 0.222, 'f': 0.278, 't': 0.278, 'r': 0.333,
      'm': 0.833, 'w': 0.722}
for ch in '0123456789':
    EM[ch] = 0.556
for ch in 'ABCDEFGHKLNOPQRSTUVXYZ':
    EM.setdefault(ch, 0.667)
for ch in 'abcdeghknopqsuvxyz':
    EM.setdefault(ch, 0.5)


def width(s: str, size: float = BODY) -> float:
    return sum(EM.get(ch, 0.55) for ch in s) * size


class Page:
    """Collects fragments the way pdf.js reports them. y grows upward."""

    def __init__(self):
        self.items = []

    def text(self, x, y, s, size=BODY):
        self.items.append({'str': s, 'x': x, 'y': y, 'width': round(width(s, size), 2), 'height': size})
        return self

    def right(self, x_right, y, s, size=BODY):
        return self.text(round(x_right - width(s, size), 2), y, s, size)

    def words(self, x, y, s, size=BODY):
        """One fragment per word, as some PDFs emit their text."""
        for word in s.split(' '):
            self.text(round(x, 2), y, word, size)
            x += width(word + ' ', size)
        return self

    def sideways(self, x, y, s, size=6.0):
        """A number printed bottom-to-top in the margin: a form or serial
        number, or a barcode. Its width runs along the text."""
        self.items.append({'str': s, 'x': x, 'y': y, 'width': round(width(s, size), 2), 'height': size, 'rot': 1})
        return self


def money(v: float) -> str:
    return f'{v:,.2f}'


def csv_text(rows) -> str:
    """The normalised CSV budget.py reads, money out negative — the same
    shape pdf_import.rows_to_csv writes, spelled out here so the fixture
    does not depend on the code it tests."""
    out = ['Date,Description,Amount']
    for d, desc, out_amount in sorted(rows):
        desc = f'"{desc}"' if ',' in desc else desc
        out.append(f'{d},{desc},{-out_amount:.2f}')
    return '\n'.join(out) + '\n'


# ------------------------------------------------------------------ CIBC card
def cibc():
    """Two dates, a description, an amount; a payment and a refund carry a
    leading minus. The summary above the card section states purchases,
    cash advances and fees separately. A statement dated January carries
    December transactions from the year before."""
    rows = [  # (trans, post, description, amount, iso date)
        ('Dec 30', 'Jan 02', 'CORNER GROCER', 45.67, '2025-12-30'),
        ('Jan 03', 'Jan 05', 'MAPLE TRANSIT', 3.35, '2026-01-03'),
        ('Jan 06', 'Jan 07', 'PAYMENT THANK YOU', -800.00, '2026-01-06'),
        ('Jan 09', 'Jan 10', 'BLUE HERON CAFE', 14.20, '2026-01-09'),
        ('Jan 12', 'Jan 13', 'RIVERSIDE PHARMACY', -12.00, '2026-01-12'),
        ('Jan 15', 'Jan 16', 'NORTHWIND UTILITIES', 132.40, '2026-01-15'),
        ('Jan 21', 'Jan 22', 'HARBOUR HARDWARE', 1058.15, '2026-01-21'),
        ('Jan 27', 'Jan 28', 'CASH ADVANCE ATM', 100.00, '2026-01-27'),
        ('Jan 31', 'Jan 31', 'ANNUAL FEE', 120.00, '2026-01-31'),
    ]
    purchases = sum(a for _, _, d, a, _ in rows if a > 0 and d not in ('CASH ADVANCE ATM', 'ANNUAL FEE'))
    cash = sum(a for _, _, d, a, _ in rows if d == 'CASH ADVANCE ATM')
    fees = sum(a for _, _, d, a, _ in rows if d == 'ANNUAL FEE')
    payments = -sum(a for _, _, d, a, _ in rows if a < 0)

    p = Page()
    p.text(40, 750, 'CIBC', 14).text(40, 730, 'Statement', 10)
    p.text(400, 750, 'Statement date', 8).text(400, 740, 'January 31, 2026', 8)
    p.text(40, 700, 'Your account at a glance', 10)
    for k, (label, v) in enumerate([('Previous balance', 900.00), ('Payments', -payments),
                                    ('Purchases', purchases), ('Cash advances', cash),
                                    ('Fees', fees), ('Interest', 0.00)]):
        y = 682 - 12 * k
        p.text(40, y, label).right(230, y, '$' + money(v) if v >= 0 else '-$' + money(-v))
    p.text(300, 682, 'Minimum payment').right(500, 682, '$10.00')
    p.text(300, 670, 'Payment due date').right(500, 670, 'February 21, 2026')
    p.text(40, 560, 'Card number 4500 XXXX XXXX 1234', 10)
    p.text(40, 542, 'Trans', 8).text(90, 542, 'Post', 8).text(140, 542, 'Description', 8).right(560, 542, 'Amount($)', 8)
    p.text(40, 534, 'date', 8).text(90, 534, 'date', 8)
    p.sideways(18, 400, '*4500123456*', 10)
    for k, (t, post, desc, amount, _) in enumerate(rows):
        y = 518 - 14 * k
        p.text(40, y, t).text(90, y, post)
        if desc == 'BLUE HERON CAFE':
            p.words(140, y, desc)          # split into words, as pdf.js sometimes does
        else:
            p.text(140, y, desc)
        p.right(560, y, money(amount) if amount >= 0 else '-' + money(-amount))
    p.text(40, 380 - 14 * len(rows), 'Total for 4500 XXXX XXXX 1234').right(560, 380 - 14 * len(rows), money(purchases + cash + fees - payments))
    p.text(40, 60, 'Page 1 of 1', 8)
    return [p.items], csv_text((d, desc, a) for _, _, desc, a, d in rows)


# --------------------------------------------------------- Scotiabank Ultimate
def ultimate():
    """Date, description, one amount and the running balance; the sign of
    each movement is what the balance did. A continuation line carries the
    rest of a description, a marketing panel shares rows with the table, and
    a serial number is printed sideways in the margin."""
    opening = 2000.00
    rows = [  # (date label, description, continuation, signed movement, iso)
        ('Dec 31', 'CHEQUE 0042', None, -150.00, '2025-12-31'),
        ('Jan 02', 'PAYROLL DEPOSIT ACME', None, 3000.00, '2026-01-02'),
        ('Jan 05', 'CORNER GROCER', None, -120.00, '2026-01-05'),
        ('Jan 08', 'E-TRANSFER SENT', 'REF 7A2B', -700.00, '2026-01-08'),
        ('Jan 15', 'MB-TRANSFER TO CREDIT CARD 4512', None, -800.00, '2026-01-15'),
        ('Jan 20', 'NORTHWIND UTILITIES', None, -132.40, '2026-01-20'),
        ('Jan 28', 'INTEREST', None, 0.35, '2026-01-28'),
    ]
    withdrawals = -sum(m for _, _, _, m, _ in rows if m < 0)
    deposits = sum(m for _, _, _, m, _ in rows if m > 0)

    p = Page()
    p.text(40, 750, 'Scotiabank', 14).text(40, 732, 'Ultimate Package', 10)
    p.text(360, 750, 'Statement period', 8).text(360, 740, 'January 1, 2026 to January 31, 2026', 8)
    p.text(40, 690, 'Account summary', 10)
    p.text(40, 674, 'Opening balance').right(240, 674, '$' + money(opening))
    p.text(40, 662, 'Total withdrawals').right(240, 662, '$' + money(withdrawals))
    p.text(40, 650, 'Total deposits').right(240, 650, '$' + money(deposits))
    p.text(40, 638, 'Closing balance').right(240, 638, '$' + money(opening - withdrawals + deposits))
    y = 600
    p.text(40, y, 'Date', 8).text(100, y, 'Description', 8).right(360, y, 'Withdrawals ($)', 8).right(440, y, 'Deposits ($)', 8).right(540, y, 'Balance ($)', 8)
    y -= 16
    p.text(40, y, 'Dec 31').text(100, y, 'Opening Balance').right(540, y, money(opening))
    p.sideways(26, y - 40, '000117', 6)
    balance = opening
    expected = []
    for k, (label, desc, cont, movement, iso) in enumerate(rows):
        y -= 16
        balance += movement
        p.text(40, y, label).text(100, y, desc)
        if movement < 0:
            p.right(360, y, money(-movement))
        else:
            p.right(440, y, money(movement))
        p.right(540, y, money(balance))
        if k in (1, 2):   # a marketing panel on the same baseline as the rows
            p.text(570, y, 'Ask us about a savings account', 7)
        full = desc
        if cont:
            y -= 12
            p.text(100, y, cont)
            full = desc + ' ' + cont
        expected.append((iso, full, -movement))
    y -= 16
    p.text(40, y, 'Jan 31').text(100, y, 'Closing Balance').right(540, y, money(balance))
    p.text(40, 60, 'Page 1 of 1', 8)
    return [p.items], csv_text(expected)


# -------------------------------------------------------------------- RBC
def rbc():
    """Three right-aligned money columns whose header is repeated on every
    page, and the columns move between pages; the column an amount sits in
    decides its direction. Descriptions wrap onto a line of their own before
    the amount, and a day's later transactions omit the date."""
    opening = 1500.00
    rows = [  # (date label or None, description lines, signed movement, iso)
        ('2 Mar', ['PAYROLL DEPOSIT ACME'], 3000.00, '2026-03-02'),
        ('4 Mar', ['CORNER GROCER'], -85.20, '2026-03-04'),
        (None, ['MAPLE TRANSIT'], -3.35, '2026-03-04'),
        ('7 Mar', ['E-TRANSFER SENT', 'RIVERSIDE PHARMACY'], -40.00, '2026-03-07'),
        ('12 Mar', ['MB-TRANSFER TO CREDIT CARD 4512'], -900.00, '2026-03-12'),
        # page 2
        ('18 Mar', ['NORTHWIND UTILITIES'], -132.40, '2026-03-18'),
        ('25 Mar', ['WITHDRAWAL FREE INTERAC E-TRANSFER'], -700.00, '2026-03-25'),
        ('31 Mar', ['INTEREST'], 0.42, '2026-03-31'),
    ]
    withdrawals = -sum(m for _, _, m, _ in rows if m < 0)
    deposits = sum(m for _, _, m, _ in rows if m > 0)

    def header(p, y, w, d, b):
        p.text(40, y, 'Date', 8).text(100, y, 'Description', 8).text(w, y, 'Withdrawals ($)', 8).text(d, y, 'Deposits ($)', 8).text(b, y, 'Balance ($)', 8)

    pages, expected = [], []
    balance = opening
    # page 1: columns at 330, 420, 510; page 2: the same table 18 points to the right
    for pn, (chunk, shift) in enumerate([(rows[:5], 0), (rows[5:], 18)]):
        p = Page()
        w, d, b = 330 + shift, 420 + shift, 510 + shift
        wr, dr, br = w + width('Withdrawals ($)', 8), d + width('Deposits ($)', 8), b + width('Balance ($)', 8)
        p.text(40, 750, 'RBC Royal Bank', 14)
        p.text(360, 750, 'From February 28, 2026 to March 31, 2026', 8)
        if pn == 0:
            p.text(40, 700, 'Summary of your account', 10)
            p.text(40, 684, 'Your opening balance on February 28, 2026').right(400, 684, '$' + money(opening))
            p.text(40, 672, 'Total deposits into your account').right(400, 672, '+ $' + money(deposits))
            p.text(40, 660, 'Total withdrawals from your account').right(400, 660, '- $' + money(withdrawals))
            p.text(40, 648, 'Your closing balance on March 31, 2026').right(400, 648, '= $' + money(opening + deposits - withdrawals))
        y = 600
        header(p, y, w, d, b)
        y -= 16
        if pn == 0:
            p.text(40, y, '28 Feb').text(100, y, 'Opening Balance').right(br, y, money(balance))
        for label, lines, movement, iso in chunk:
            balance += movement
            for k, line in enumerate(lines):
                y -= 14
                if k == 0 and label:
                    p.text(40, y, label)
                p.text(100, y, line)
                if k == len(lines) - 1:
                    if movement < 0:
                        p.right(wr, y, money(-movement))
                    else:
                        p.right(dr, y, money(movement))
                    p.right(br, y, money(balance))
            expected.append((iso, ' '.join(lines), -movement))
        if pn == 1:
            y -= 14
            p.text(100, y, 'Closing Balance').right(br, y, money(balance))
        p.text(40, 60, f'Page {pn + 1} of 2', 8)
        pages.append(p.items)
    return pages, csv_text(expected)


# ------------------------------------------------------------- ScotiaLine LOC
def scotia_line():
    """A sequence number, two dates, a description and an amount; a trailing
    minus marks a payment onto the line. The summary states advances and
    interest separately and the transaction list carries both. Every cell
    is emitted one word at a time, as this bank's PDFs do."""
    rows = [
        ('001', 'Apr 02', 'Apr 03', 'CORNER GROCER', 45.67, '2026-04-02'),
        ('002', 'Apr 06', 'Apr 07', 'HARBOUR HARDWARE', 612.30, '2026-04-06'),
        ('003', 'Apr 15', 'Apr 15', 'PAYMENT THANK YOU', -500.00, '2026-04-15'),
        ('004', 'Apr 19', 'Apr 20', 'BLUE HERON CAFE', 22.75, '2026-04-19'),
        ('005', 'Apr 30', 'Apr 30', 'INTEREST CHARGE', 9.84, '2026-04-30'),
    ]
    advances = sum(a for _, _, _, d, a, _ in rows if a > 0 and d != 'INTEREST CHARGE')
    interest = sum(a for _, _, _, d, a, _ in rows if d == 'INTEREST CHARGE')
    payments = -sum(a for _, _, _, _, a, _ in rows if a < 0)

    p = Page()
    p.words(40, 750, 'Scotiabank ScotiaLine Personal Line of Credit', 12)
    p.words(360, 750, 'Statement date April 30, 2026', 8)
    p.words(40, 700, 'Account summary', 10)
    for k, (label, sign, v) in enumerate([('Previous balance', '', 1200.00), ('Payments', '-', payments),
                                          ('Advances/charges', '+', advances), ('Interest', '+', interest)]):
        y = 682 - 12 * k
        p.words(40, y, label).text(200, y, sign).right(280, y, '$' + money(v))
    p.words(40, 560, 'Ref Trans Post Description Amount', 8)
    for k, (seq, t, post, desc, amount, _) in enumerate(rows):
        y = 540 - 14 * k
        p.text(40, y, seq).words(70, y, t).words(115, y, post).words(160, y, desc)
        p.right(540, y, money(amount) if amount >= 0 else money(-amount) + '-')
    p.words(40, 60, 'Page 1 of 1', 8)
    return [p.items], csv_text((d, desc, a) for _, _, _, desc, a, d in rows)


FIXTURES = {'cibc-2026-01-31': cibc, 'ultimate-2026-01-31': ultimate,
            'rbc-2026-03-31': rbc, 'scotialine-2026-04-30': scotia_line}


def main():
    for name, make in FIXTURES.items():
        pages, csv = make()
        (HERE / f'{name}.json').write_text(json.dumps(pages, indent=None, separators=(',', ':')) + '\n')
        (HERE / f'{name}.csv').write_text(csv)
        print(f'  wrote {name}.json ({sum(len(p) for p in pages)} fragments, {len(pages)} page(s)) and {name}.csv')


if __name__ == '__main__':
    main()
