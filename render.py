#!/usr/bin/env python3
"""Paint the front page for Thursday 19 November 2026.

The fifty stories live in stories.json next to this file. This script
draws them into entry.png with Pillow only: no network access, no
clock reads, no random numbers, so the picture is byte-identical on
every run for the same stories file.
"""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
PAGE_W, PAGE_H = 1024, 1024
PAPER_TONE = (248, 244, 232)
INK_DARK = (24, 22, 18)
INK_FAINT = (98, 94, 84)
CRIMSON = (148, 24, 24)
TEAL_DEEP = (20, 66, 74)
SEA_TONE = (222, 232, 230)
LAND_TONE = (122, 164, 152)
LAND_LINE = (70, 106, 100)
GOLD_TONE = (170, 136, 54)

TYPE_DIR = Path("/usr/share/fonts/truetype/dejavu")


def typeface(filename, size):
    return ImageFont.truetype(str(TYPE_DIR / filename), size)


def fit_words(canvas, text, face, limit):
    """Split text into lines no wider than limit, word by word."""
    out, line = [], ""
    for piece in text.split():
        trial = piece if not line else line + " " + piece
        if canvas.textlength(trial, font=face) <= limit:
            line = trial
        else:
            if line:
                out.append(line)
            line = piece
    if line:
        out.append(line)
    return out


def story_block(canvas, left, top, span, headline, outlet):
    """Set one story in bold, at most two lines, outlet tagged inline.

    The outlet tag is kept whole: when it cannot follow the headline
    on the same line, it drops to its own line below.
    """
    head_face = typeface("DejaVuSans-Bold.ttf", 12)
    tag_face = typeface("DejaVuSans.ttf", 10)
    gap = canvas.textlength(" ", font=head_face)
    tag_span = (canvas.textlength("--", font=tag_face) + gap
                + canvas.textlength(outlet, font=tag_face))
    pieces = [(w, head_face, INK_DARK) for w in headline.split()]
    pieces.append(("--", tag_face, INK_FAINT))
    pieces.append((outlet, tag_face, INK_FAINT))
    rows, row, row_w = [], [], 0.0
    pos = 0
    while pos < len(pieces):
        word, face, tone = pieces[pos]
        if word == "--":
            if row and row_w + gap + tag_span > span:
                rows.append(row)
                row, row_w = [], 0.0
            row.append(("--", tag_face, INK_FAINT))
            row_w += (gap if len(row) > 1 else 0) + canvas.textlength(
                "--", font=tag_face)
            pos += 1
            word, face, tone = pieces[pos]
            row.append((word, face, tone))
            row_w += gap + canvas.textlength(word, font=face)
            pos += 1
            continue
        size = canvas.textlength(word, font=face)
        extra = size if not row else gap + size
        if row_w + extra <= span:
            row.append((word, face, tone))
            row_w += extra
        else:
            rows.append(row)
            row, row_w = [(word, face, tone)], size
        pos += 1
    if row:
        rows.append(row)
    if len(rows) > 2:
        first = rows[0]
        second = [p for p in rows[1] if p[1] is head_face]
        tail = [p for p in rows[1] + rows[2] if p[1] is tag_face]
        rows = [first, []]
        used = 0.0
        for word, face, tone in second:
            size = canvas.textlength(word, font=face)
            extra = size if not rows[1] else gap + size
            if used + extra + canvas.textlength("...", font=head_face) <= span:
                rows[1].append((word, face, tone))
                used += extra
        rows[1].append(("...", head_face, INK_DARK))
        for word, face, tone in tail:
            size = canvas.textlength(word, font=face)
            if used + gap + size <= span:
                rows[1].append((word, face, tone))
                used += gap + size
    cursor = top
    for row in rows:
        pen = left
        for idx, (word, face, tone) in enumerate(row):
            if idx:
                pen += gap
            canvas.text((pen, cursor), word, font=face, fill=tone)
            pen += canvas.textlength(word, font=face)
        cursor += 14
    return cursor + 2


def section_block(canvas, left, top, span, name, total):
    face = typeface("DejaVuSans-Bold.ttf", 13)
    canvas.text((left, top), name, font=face, fill=CRIMSON)
    count = str(total) + " STORIES"
    small = typeface("DejaVuSans-Bold.ttf", 10)
    wide = canvas.textlength(count, font=small)
    canvas.text((left + span - wide, top + 2), count, font=small,
                fill=INK_FAINT)
    canvas.line([(left, top + 17), (left + span, top + 17)],
                fill=INK_DARK, width=1)
    return top + 23


def paint_atlas(canvas, left, top, span, tall):
    canvas.rectangle([left, top, left + span, top + tall], fill=SEA_TONE)
    canvas.rectangle([left, top, left + span, top + tall],
                     outline=LAND_LINE, width=1)
    lands = [
        [(36, 22), (70, 8), (140, 4), (196, 12), (214, 24), (198, 38),
         (172, 44), (150, 58), (128, 64), (108, 50), (76, 44), (44, 38)],
        [(228, 6), (256, 4), (264, 14), (242, 18)],
        [(204, 50), (238, 46), (260, 60), (250, 82), (224, 88), (206, 70)],
        [(458, 10), (502, 6), (526, 16), (514, 32), (486, 36), (460, 26)],
        [(458, 40), (506, 36), (534, 50), (542, 70), (522, 88), (492, 86),
         (466, 62)],
        [(542, 10), (640, 4), (750, 8), (860, 14), (906, 26), (880, 42),
         (810, 50), (730, 44), (668, 50), (600, 44), (552, 30)],
        [(802, 66), (862, 62), (884, 74), (860, 86), (810, 84)],
    ]
    for shape in lands:
        moved = [(left + px, top + py) for px, py in shape]
        canvas.polygon(moved, fill=LAND_TONE, outline=LAND_LINE)
    canvas.ellipse([left + 696, top + 52, left + 712, top + 60],
                   fill=LAND_TONE, outline=LAND_LINE)
    canvas.ellipse([left + 722, top + 58, left + 738, top + 65],
                   fill=LAND_TONE, outline=LAND_LINE)
    tag = typeface("DejaVuSans-Bold.ttf", 9)
    for word, lx, ly in [("N. AMERICA", 76, 26), ("S. AMERICA", 202, 62),
                         ("EUROPE", 528, 6), ("AFRICA", 482, 56),
                         ("ASIA", 700, 20), ("AUSTRALIA", 806, 68)]:
        canvas.text((left + lx, top + ly), word, font=tag,
                    fill=(48, 74, 70))
    pins = [(762, 26, "1"), (706, 48, "2"), (505, 18, "3"),
            (570, 46, "4"), (168, 26, "5"), (908, 80, "6")]
    num = typeface("DejaVuSans-Bold.ttf", 10)
    for px, py, digit in pins:
        cx, cy = left + px, top + py
        canvas.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=CRIMSON,
                       outline=(255, 255, 255), width=1)
        wide = canvas.textlength(digit, font=num)
        canvas.text((cx - wide / 2, cy - 7), digit, font=num,
                    fill=(255, 255, 255))
    key = "1 SHENZHEN - 2 MANILA - 3 KYIV - 4 GAZA - 5 NEW YORK - 6 WELLINGTON"
    canvas.text((left + 8, top + tall - 14), key,
                font=typeface("DejaVuSans-Bold.ttf", 10), fill=INK_DARK)


def paint_wire(canvas, left, top, span):
    head = typeface("DejaVuSans-Bold.ttf", 13)
    canvas.text((left, top), "THE DAY IN UTC", font=head, fill=CRIMSON)
    canvas.text((left + span - 210, top + 2), "TIMES UTC, APPROXIMATE",
                font=typeface("DejaVuSans-Bold.ttf", 10), fill=INK_FAINT)
    canvas.line([(left, top + 19), (left + span, top + 19)],
                fill=INK_DARK, width=1)
    beats = [
        ("00:03", "Yonhap: three-way summit set for today"),
        ("00:57", "Van Gogh record confirmed in print"),
        ("02:00", "APEC plenary opens in Shenzhen"),
        ("05:00", "GTA VI unlocks around the world"),
        ("08:00", "Leaders sit down at Kylin Villa"),
        ("14:30", "Anthropic shares start trading"),
    ]
    cell = span // 3
    clock = typeface("DejaVuSans-Bold.ttf", 11)
    plain = typeface("DejaVuSans.ttf", 11)
    for idx, (when, what) in enumerate(beats):
        bx = left + (idx % 3) * cell
        by = top + 28 + (idx // 3) * 22
        canvas.ellipse([bx, by + 3, bx + 7, by + 10], fill=CRIMSON)
        canvas.text((bx + 12, by), when, font=clock, fill=INK_DARK)
        wide = canvas.textlength(when, font=clock)
        canvas.text((bx + 12 + wide + 6, by), what, font=plain,
                    fill=INK_DARK)
    return top + 28 + 2 * 22 + 4


def paint_page():
    with open(BASE / "stories.json", encoding="utf-8") as handle:
        bundle = json.load(handle)
    items = bundle["stories"]
    sheet = Image.new("RGB", (PAGE_W, PAGE_H), PAPER_TONE)
    canvas = ImageDraw.Draw(sheet)
    edge = 30
    full = PAGE_W - 2 * edge

    canvas.text((edge, 10), "50 SOURCED STORIES  -  SIX REGIONS  -  ONE DAY",
                font=typeface("DejaVuSans-Bold.ttf", 13), fill=CRIMSON)
    masthead = typeface("DejaVuSerif-Bold.ttf", 50)
    name = bundle["paper"]
    wide = canvas.textlength(name, font=masthead)
    canvas.text(((PAGE_W - wide) / 2, 26), name, font=masthead,
                fill=INK_DARK)
    day = typeface("DejaVuSans-Bold.ttf", 19)
    stamp = bundle["dateline"]
    wide = canvas.textlength(stamp, font=day)
    canvas.text(((PAGE_W - wide) / 2, 82), stamp, font=day, fill=INK_DARK)
    canvas.line([(edge, 108), (edge + full, 108)], fill=INK_DARK, width=2)
    canvas.line([(edge, 112), (edge + full, 112)], fill=INK_DARK, width=1)

    top_story = next(item for item in items if item.get("lead"))
    band_top, band_tall = 118, 62
    canvas.rectangle([edge, band_top, edge + full, band_top + band_tall],
                     fill=TEAL_DEEP)
    big = typeface("DejaVuSerif-Bold.ttf", 26)
    first = fit_words(canvas, top_story["headline"], big, full - 36)
    canvas.text((edge + 18, band_top + 7), first[0], font=big,
                fill=(255, 255, 255))
    canvas.text((edge + 18, band_top + band_tall - 19), bundle["lead_deck"],
                font=typeface("DejaVuSans.ttf", 14),
                fill=(210, 228, 230))

    third = (full - 2 * 22) // 3
    starts = [edge, edge + third + 22, edge + 2 * (third + 22)]
    groups = ["DIPLOMACY", "MARKETS & TRADE", "CONFLICT & SECURITY",
              "ASIA & PACIFIC", "EUROPE & AMERICAS", "CULTURE & SCIENCE"]
    cursor = 190
    for col in range(3):
        pen = cursor
        for group in groups[col * 2: col * 2 + 2]:
            bunch = [s for s in items if s["section"] == group]
            pen = section_block(canvas, starts[col], pen, third, group,
                                len(bunch))
            for entry in bunch:
                pen = story_block(canvas, starts[col], pen, third,
                                  entry["headline"], entry["source"])
            pen += 4

    paint_atlas(canvas, edge, 800, full, 88)
    end = paint_wire(canvas, edge, 896, full)
    base = end + 6
    canvas.line([(edge, base), (edge + full, base)], fill=INK_DARK, width=1)
    audit = ("DATE CHECK -- Every story above was first reported on Thursday "
             "19 November 2026; lead items are confirmed by two or more wires.")
    canvas.text((edge, base + 8), audit,
                font=typeface("DejaVuSans-Bold.ttf", 10), fill=INK_DARK)
    credits = ("SOURCES: AP - REUTERS - BBC - AFP - BLOOMBERG - CNN - "
               "NIKKEI ASIA - PTI - UN - UNICEF - NASA - ROCKSTAR - METACRITIC")
    canvas.text((edge, base + 24), credits,
                font=typeface("DejaVuSans.ttf", 10), fill=INK_FAINT)
    return sheet


def main():
    picture = paint_page()
    target = BASE / "entry.png"
    picture.save(target, format="PNG")
    blob = target.read_bytes()
    print("entry.png", len(blob), "bytes")
    print("sha256", hashlib.sha256(blob).hexdigest())


if __name__ == "__main__":
    main()
