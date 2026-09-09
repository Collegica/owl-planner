#!/usr/bin/env python
"""Write the invented household's statements to sample/statements/.

Eight months, four accounts, every kind of money movement the tool knows about,
three different CSV dialects so the importer's inference is exercised — and not
one real person's transaction. Deterministic: the same files every run.

    python scripts/make_sample.py
"""
from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'sample' / 'statements'
rng = random.Random(2026)

MONTHS = [date(2026, m, 1) for m in range(1, 9)]


def month_end(d: date) -> date:
    nxt = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
    return nxt - timedelta(days=1)


def day(d: date, n: int) -> date:
    return d.replace(day=min(n, month_end(d).day))


def money(lo, hi):
    return round(rng.uniform(lo, hi), 2)


# ----------------------------------------------------------------- chequing
# "Northbank" chequing. ISO dates, one signed Amount column. The household's
# income, mortgage, utilities, savings, support payments, a loan to a friend,
# a cashback pass-through, a wedding gift, and a line-of-credit round trip.
chq: list[tuple[date, str, float]] = []
for m in MONTHS:
    chq.append((day(m, 15), 'PAYROLL DEPOSIT MAPLEWORKS INC', 3850.00))
    chq.append((month_end(m), 'PAYROLL DEPOSIT MAPLEWORKS INC', 3850.00))
    chq.append((day(m, 1), 'MORTGAGE PAYMENT #778812', -2150.00))
    chq.append((day(m, 3), 'RRSP CONTRIBUTION FIDELITY 4471', -500.00))
    chq.append((day(m, 12), 'BILL PAYMENT HYDRO ONE', -money(105, 140)))
    chq.append((day(m, 12), 'BILL PAYMENT ENBRIDGE GAS', -money(60, 130) if m.month in (1, 2, 3, 11, 12) else -money(28, 40)))
    chq.append((day(m, 19), 'BILL PAYMENT TEKSAVVY', -74.99))
    chq.append((day(m, 2), 'MONTHLY PLAN FEE', -16.95))
    # the two cards are paid in full from chequing — transfers, not spending
    chq.append((day(m, 21), 'MB-TRANSFER TO CREDIT CARD 4512', -money(1400, 1900)))
    chq.append((day(m, 22), 'MB-TRANSFER TO CREDIT CARD 7730', -money(300, 700)))

# child support: made on the last day of each month, and some clear on the 1st
# or 2nd of the next one — the calendar wobble the `level` rule exists for.
for m, slip in zip(MONTHS, [0, 0, 1, 0, 1, 0, 0, 2]):
    chq.append((month_end(m) + timedelta(days=slip), 'WITHDRAWAL FREE INTERAC E-TRANSFER', -950.00))

chq += [
    (date(2026, 1, 20), 'CHEQUE 0042', -5000.00),                       # loan to Friend A
    (date(2026, 4, 5), 'MOBILE CHEQUE DEPOSIT', 2000.00),                # Friend A repays part
    (date(2026, 3, 15), 'CASHBACK REWARD CREDIT', 250.00),               # pass-through, in
    (date(2026, 3, 15), 'E-TRANSFER SENT', -250.00),                     # pass-through, out
    (date(2026, 2, 10), 'E-TRANSFER SENT', -1500.00),                    # wedding gift (dated pin)
    (date(2026, 3, 9), 'ONLINE BANKING TRANSFER FROM LOC', 2000.00),     # LoC advance lands
    (date(2026, 4, 14), 'ONLINE BANKING LOAN PAYMENT LOC', -2000.00),    # and is repaid
    (date(2026, 6, 26), 'TAX REFUND CANADA', 812.40),
]

# ----------------------------------------------------------------- visa
# Semicolon-separated, day-first dates, separate Debit and Credit columns,
# amounts with a comma decimal — the awkward dialect.
GROCERS = ['LOBLAWS #1043 NEWTOWN ON', 'COSTCO WHSL #921 NEWTOWN ON', 'NO FRILLS 2277 NEWTOWN ON']
EATS = ['TIM HORTONS #4410', 'UBER EATS TORONTO ON', 'THE DAILY GRIND CAFE', 'MAPLE LEAF RESTAURANT']
visa: list[tuple[date, str, float, float]] = []   # date, desc, debit, credit
for m in MONTHS:
    for _ in range(rng.randint(5, 7)):
        visa.append((day(m, rng.randint(1, 28)), rng.choice(GROCERS), money(38, 210), 0))
    for _ in range(rng.randint(4, 6)):
        visa.append((day(m, rng.randint(1, 28)), rng.choice(EATS), money(9, 64), 0))
    for _ in range(3):
        visa.append((day(m, rng.randint(1, 28)), rng.choice(['PETRO-CANADA 2210', 'SHELL C21188']), money(48, 82), 0))
    visa.append((day(m, rng.randint(2, 26)), 'SHOPPERS DRUG MART #0771', money(18, 70), 0))
    visa.append((day(m, 6), 'FIDO MOBILE', 65.00, 0))
    visa.append((day(m, 9), 'NETFLIX.COM', 17.99, 0))
    visa.append((day(m, 11), 'SPOTIFY', 11.99, 0))
    visa.append((day(m, 23), 'PAYMENT - THANK YOU', 0, money(1400, 1900)))
visa += [
    (date(2026, 2, 3), 'WINNERS #302 NEWTOWN ON', 148.20, 0),
    (date(2026, 2, 17), 'WINNERS #302 NEWTOWN ON', 0, 42.10),          # a refund
    (date(2026, 5, 1), 'UNIQLO CANADA ONLINE', 96.55, 0),
    (date(2026, 8, 8), 'WINNERS #302 NEWTOWN ON', 121.00, 0),
]

# ----------------------------------------------------------------- mastercard
# Comma-separated, month-first dates, one signed column, a header row with
# an extra Category column the way some banks add one.
mc: list[tuple[date, str, float, str]] = []
for m in MONTHS:
    mc.append((day(m, 4), 'ALLSTATE INSURANCE CO', -141.30, 'Insurance'))
    mc.append((day(m, 8), 'GOODLIFE FITNESS', -44.99, 'Recreation'))
    mc.append((day(m, rng.randint(10, 27)), 'CANADIAN TIRE #244', -money(22, 95), 'Retail and Grocery'))
    mc.append((day(m, 24), 'PAYMENT - THANK YOU', money(300, 700), ''))
    if m.month in (1, 4, 7):
        mc.append((day(m, 16), 'NEWTOWN DENTAL', -money(110, 180), 'Health and Education'))
mc += [
    (date(2026, 3, 2), 'IKEA VAUGHAN', -412.77, 'Home and Office Improvement'),
    (date(2026, 5, 20), 'MAIN STREET AUTO', -3800.00, 'Transportation'),       # one-off repair
    (date(2026, 7, 14), 'AIR CANADA', -2400.00, 'Travel'),                      # irregular, undecided
    (date(2026, 6, 3), 'THE BOOK NOOK NEWTOWN', -38.50, 'Entertainment and Recreation'),
    (date(2026, 8, 19), 'THE BOOK NOOK NEWTOWN', -27.90, 'Entertainment and Recreation'),
]

# ----------------------------------------------------------------- line of credit
loc = [
    (date(2026, 3, 9), 'CASH ADVANCE TO - CHQ 5513', -2000.00),
    (date(2026, 3, 31), 'INTEREST CHARGE', -9.86),
    (date(2026, 4, 14), 'PAYMENT FROM - CHQ 5513', 2000.00),
    (date(2026, 4, 30), 'INTEREST CHARGE', -5.12),
]


def write():
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / 'northbank-chequing.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['Date', 'Description', 'Amount'])
        for d, desc, amt in sorted(chq):
            w.writerow([d.isoformat(), desc, f'{amt:.2f}'])
    with open(OUT / 'northbank-visa.csv', 'w', newline='') as fh:
        w = csv.writer(fh, delimiter=';')
        w.writerow(['Date', 'Description', 'Debit', 'Credit'])
        for d, desc, deb, cre in sorted(visa):
            w.writerow([d.strftime('%d/%m/%Y'), desc,
                        f'{deb:.2f}'.replace('.', ',') if deb else '',
                        f'{cre:.2f}'.replace('.', ',') if cre else ''])
    with open(OUT / 'maple-mastercard.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['Transaction Date', 'Description', 'Category', 'Amount'])
        for d, desc, amt, cat in sorted(mc):
            w.writerow([d.strftime('%m/%d/%Y'), desc, cat, f'{amt:.2f}'])
    with open(OUT / 'northbank-loc.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['Date', 'Description', 'Amount'])
        for d, desc, amt in sorted(loc):
            w.writerow([d.isoformat(), desc, f'{amt:.2f}'])
    n = len(chq) + len(visa) + len(mc) + len(loc)
    print(f'wrote 4 statements, {n} transactions, to {OUT.relative_to(ROOT)}/')


if __name__ == '__main__':
    write()
