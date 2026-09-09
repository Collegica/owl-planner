"""Reconstruct fixed-width, column-aligned text from positioned text fragments.

A browser has no poppler. pdf.js can read a statement and return, per page,
the text fragments it found with their position and width; this module turns
those fragments into the kind of text `pdftotext -layout` prints, so the bank
extractors in pdf_import.py can read it unchanged. They depend on two things:
fragments on one baseline sharing a row, and a fragment's horizontal position
mapping to a character column consistently across the page, so that an amount
lands under the header it belongs to and a description is separated from its
amount by more than one space. Byte equality with poppler is not the aim;
reconciliation against the statement's own totals is what decides whether the
reconstruction was good enough.

A fragment is a mapping with `str`, `x`, `y` and `width` in PDF user units
(y grows upward, as pdf.js reports it), and optionally `height`, the font
size, and `rot`, quarter turns anticlockwise (0 for ordinary text). `layout()`
takes a list of pages, each a list of fragments or a mapping with an `items`
key, and returns one string with a form feed after every page, which is what
pdftotext writes.
"""
from __future__ import annotations

# A fragment closer than this to the previous one, in character widths, is
# the same word split by kerning or a font change: no space between them.
JOIN_GAP = 0.3
# A gap wider than this many character widths is a column boundary; keep at
# least two spaces there even when an over-wide fragment has pushed the
# cursor past where the column should start, because the extractors split
# description from amount on two or more spaces.
COLUMN_GAP = 1.5


def _text(item) -> str:
    return item.get('str') or ''


def char_width(items) -> float:
    """One character's width, page-wide: the median of width over length
    across the fragments. The same figure maps every fragment on the page to
    a column, so header and amounts stay aligned even where the estimate is
    off for one font."""
    ratios = sorted(item['width'] / len(_text(item)) for item in items
                    if len(_text(item).strip()) >= 3 and item['width'] > 0)
    if not ratios:
        return 5.0
    return ratios[len(ratios) // 2]


def _height(item, fallback: float) -> float:
    h = item.get('height')
    return float(h) if h else fallback


def lines(items, cw: float) -> list[list[dict]]:
    """Cluster fragments into baselines. Sorted top to bottom, a fragment
    joins the current line while it lies within half a font height of the
    line's first fragment; otherwise it starts the next line."""
    rows: list[list[dict]] = []
    ref_y = None
    ref_tol = 0.0
    for item in sorted(items, key=lambda i: (-i['y'], i['x'])):
        tol = 0.5 * _height(item, 2 * cw)
        if ref_y is None or ref_y - item['y'] > max(tol, ref_tol):
            rows.append([item])
            ref_y, ref_tol = item['y'], tol
        else:
            rows[-1].append(item)
    return rows


def render_line(row, cw: float) -> str:
    """Place each fragment at the column its x maps to, padding with spaces.
    A fragment wider than its columns pushes the next one right rather than
    overwriting it; the gap in points then decides whether they are one word,
    neighbouring words, or separate columns."""
    out: list[str] = []
    cursor = 0
    prev_end = None
    prev = None
    for item in sorted(row, key=lambda i: i['x']):
        s = _text(item)
        if not s.strip():
            continue
        # some PDFs draw a glyph twice for a fake bold; poppler collapses the
        # overlap and so must this
        if prev is not None and s == _text(prev) and abs(item['x'] - prev['x']) < 0.5 * cw:
            continue
        col = int(round(item['x'] / cw))
        if prev_end is None:
            target = col
        else:
            gap = (item['x'] - prev_end) / cw
            if gap < COLUMN_GAP:
                # the same word, or the next word of the same text: pdftotext
                # joins these with nothing or one space and does not pad
                # them out to a column, so neither does this
                target = cursor + (0 if gap < JOIN_GAP else 1)
            else:
                target = max(col, cursor + 2)
        out.append(' ' * (target - cursor))
        out.append(s)
        cursor = target + len(s)
        prev_end = item['x'] + item['width']
        prev = item
    return ''.join(out).rstrip()


# How far the top of a glyph box sits above its baseline, as a fraction of
# the font size; pdftotext orders rows by that top edge, not the baseline.
ASCENT = 0.8


def _top(item) -> float:
    """The highest point of a fragment, for ordering rows. Text running
    upward starts at its bottom, so its top is a width away; upright text
    reaches an ascent above its baseline. Rows are ordered by this edge as
    pdftotext orders them, which puts a sideways margin number after the
    row it starts beside rather than before that row's continuation line."""
    rot = int(item.get('rot') or 0) % 4
    if rot == 1:
        return item['y'] + item['width']
    if rot == 3:
        return item['y']
    return item['y'] + ASCENT * _height(item, 0.0)


def sideways_lines(items, cw: float) -> list[dict]:
    """Join fragments of text printed sideways into the lines they form: the
    same rotation, the same x within half a font height, contiguous along
    the direction of reading. Each line comes back as one upright pseudo
    fragment placed at the line's x, with the words a space apart, so it
    renders as a single row the way pdftotext prints a rotated line. A
    margin that carries a form number, a date and a few dashes is one row
    that way, not six rows scattered among the transactions."""
    out = []
    by_rot: dict[int, list] = {}
    for i in items:
        by_rot.setdefault(int(i.get('rot') or 0) % 4, []).append(i)
    for rot, group in by_rot.items():
        # reading order: upward text starts at the bottom (y ascending),
        # downward text at the top
        group.sort(key=lambda i: (i['x'], i['y'] if rot == 1 else -i['y']))
        line: list = []
        for i in group:
            if line:
                prev = line[-1]
                h = max(_height(i, 2 * cw), _height(prev, 2 * cw))
                far = abs(i['x'] - prev['x']) > 0.5 * h
                if rot == 1:
                    gap = i['y'] - (prev['y'] + prev['width'])
                else:
                    gap = (prev['y'] - prev['width']) - i['y']
                if far or gap > 2 * h:
                    out.append(_join_sideways(line, rot)); line = []
            line.append(i)
        if line:
            out.append(_join_sideways(line, rot))
    return out


def _join_sideways(line, rot: int) -> dict:
    parts = [_text(line[0])]
    for prev, i in zip(line, line[1:]):
        gap = (i['y'] - (prev['y'] + prev['width'])) if rot == 1 else ((prev['y'] - prev['width']) - i['y'])
        parts.append(('' if gap < JOIN_GAP * _height(i, 5.0) else ' ') + _text(i))
    top = max(_top(i) for i in line)
    return {'str': ''.join(parts), 'x': min(i['x'] for i in line), 'y': top,
            'width': sum(i['width'] for i in line), 'height': _height(line[0], 0.0)}


def layout_page(items) -> str:
    items = [i for i in items if _text(i).strip()]
    if not items:
        return ''
    cw = char_width(items)
    # Statements carry text printed sideways in the margin: a form or serial
    # number in a small font, a barcode. pdftotext keeps rotated text off the
    # rows it crosses and prints it on a row of its own; do the same, or a
    # vertical number lands in front of the date on a transaction line and
    # the extractor no longer recognises the line.
    upright = [i for i in items if int(i.get('rot') or 0) % 4 == 0]
    sideways = sideways_lines([i for i in items if int(i.get('rot') or 0) % 4 != 0], cw)
    rows = [(max(_top(i) for i in row), row[0]['y'], row) for row in lines(upright, cw)]
    rows += [(i['y'], i['y'], [i]) for i in sideways]
    rows.sort(key=lambda r: -r[0])
    out = []
    prev_y = None
    prev_h = None
    for _, y, row in rows:
        if prev_y is not None:
            # pdftotext leaves one blank line per font height of vertical
            # gap beyond the first, up to four; the CIBC extractor counts
            # lines from the top to find the summary, so keep the same shape
            out.extend([''] * (min(5, max(1, int((prev_y - y) / prev_h))) - 1))
        out.append(render_line(row, cw))
        prev_y, prev_h = y, max(_height(row[0], 2 * cw), 1.0)
    return '\n'.join(out)


def layout(pages) -> str:
    """Pages to text, with a form feed after every page as pdftotext prints
    it, so the extractors that count lines from the top see the same shape."""
    out = []
    for page in pages:
        items = page['items'] if isinstance(page, dict) else page
        out.append(layout_page(items) + '\n\f')
    return ''.join(out)
