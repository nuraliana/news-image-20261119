"""Render THE WORLD IN ONE DAY — news-image-20261119, PIL only, deterministic."""
import json, math, os, random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIFB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def F(path, size):
    return ImageFont.truetype(path, size)

PAPER = (253, 251, 245)
INK = (24, 24, 22)
TEAL = (13, 71, 76)
TEAL2 = (18, 96, 102)
RED = (178, 34, 34)
GOLD = (176, 141, 44)
GREY = (110, 110, 104)
LAND = (227, 211, 160)
LANDLINE = (122, 106, 63)
OCEAN = (214, 232, 240)

def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_globe(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(30, 110, 140), outline=INK, width=2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=1)
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(255, 255, 255), width=2)
    d.arc([cx - r, cy - r, cx + r, cy + r], 20, 160, fill=(255, 255, 255), width=2)
    d.line([cx - r, cy, cx + r, cy], fill=(255, 255, 255), width=1)
    d.ellipse([cx - r // 2, cy - r // 2, cx - r // 4, cy - r // 4], fill=(120, 190, 120))
    d.ellipse([cx + r // 5, cy + r // 4, cx + r // 2, cy + r // 2], fill=(120, 190, 120))

def draw_summit(d, x0, y0):
    # three leaders: heads + shoulders, flags above (US / China / Russia)
    cols = [(178, 34, 34), (200, 40, 40), (30, 60, 140)]
    flagcols = [[(200, 30, 30), (255, 255, 255), (30, 60, 140)],
                [(200, 30, 30), (255, 220, 0)],
                [(255, 255, 255), (30, 60, 160), (200, 30, 30)]]
    for i in range(3):
        cx = x0 + 22 + i * 42
        d.line([cx, y0 + 2, cx, y0 + 20], fill=INK, width=2)
        fc = flagcols[i]
        for j, c in enumerate(fc):
            d.rectangle([cx, y0 + 2 + j * 6, cx + 20, y0 + 7 + j * 6], fill=c, outline=INK)
        d.ellipse([cx - 9, y0 + 24, cx + 9, y0 + 42], fill=(232, 200, 160), outline=INK)
        d.pieslice([cx - 16, y0 + 44, cx + 16, y0 + 72], 180, 360, fill=cols[i], outline=INK)
    d.line([x0, y0 + 72, x0 + 128, y0 + 72], fill=INK, width=2)

def draw_rocket(d, x0, y0, s=1.0):
    # flat rocket, tilted up-right; s scales it
    def P(pts):
        return [(x0 + int(px * s), y0 + int(py * s)) for px, py in pts]
    d.polygon(P([(20, 0), (32, 26), (20, 20), (8, 26)]),
              fill=(220, 225, 230), outline=INK)
    d.polygon(P([(20, 0), (26, 12), (20, 10), (14, 12)]),
              fill=RED, outline=INK)
    d.ellipse([x0 + int(16 * s), y0 + int(14 * s), x0 + int(24 * s), y0 + int(22 * s)], fill=TEAL, outline=INK)
    d.polygon(P([(8, 26), (2, 38), (12, 30)]), fill=RED, outline=INK)
    d.polygon(P([(32, 26), (38, 38), (28, 30)]), fill=RED, outline=INK)
    d.polygon(P([(17, 22), (23, 22), (20, 40)]), fill=(255, 170, 30), outline=(200, 100, 0))
    for sx, sy in [(-6, 4), (44, 2), (48, 22), (-2, 30)]:
        d.ellipse([x0 + int(sx * s), y0 + int(sy * s), x0 + int(sx * s) + 3, y0 + int(sy * s) + 3], fill=GOLD)

def draw_frame(d, x0, y0, w=34, h=24):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=GOLD, outline=INK)
    d.rectangle([x0 + 4, y0 + 4, x0 + w - 4, y0 + h - 4], fill=(250, 235, 180), outline=INK)
    d.ellipse([x0 + 9, y0 + 8, x0 + 17, y0 + 16], fill=(255, 200, 40), outline=(200, 140, 0))
    d.ellipse([x0 + 18, y0 + 10, x0 + 25, y0 + 17], fill=(255, 170, 20), outline=(200, 140, 0))
    d.line([x0 + 8, y0 + 18, x0 + 26, y0 + 18], fill=(90, 140, 60), width=2)

def draw_cyclone(d, cx, cy, r):
    for k in range(5):
        rr = r * (k + 1) / 5.0
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 20 + k * 40, 300 + k * 40,
              fill=(30, 90, 160), width=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)

def draw_map(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=OCEAN, outline=INK, width=2)
    for gx in range(x0 + 60, x1, 80):
        d.line([gx, y0, gx, y1], fill=(255, 255, 255), width=1)
    for gy in range(y0 + 24, y1, 24):
        d.line([x0, gy, x1, gy], fill=(255, 255, 255), width=1)
    for sx in range(x0 + 8, x1, 11):
        for sy in range(y0 + 8, y1, 11):
            if (sx * 7 + sy * 13) % 5 == 0:
                d.point((sx, sy), fill=(170, 200, 215))
    conts = [
        [(70, 215), (150, 200), (225, 205), (240, 220), (215, 232), (190, 245), (165, 258), (140, 250), (115, 262), (90, 245), (65, 232)],
        [(180, 185), (215, 182), (225, 192), (195, 198), (178, 193)],
        [(225, 245), (255, 238), (272, 252), (262, 278), (240, 292), (222, 272)],
        [(470, 205), (505, 196), (535, 200), (545, 212), (520, 222), (495, 222), (472, 215)],
        [(462, 200), (470, 198), (472, 206), (464, 208)],
        [(468, 228), (515, 222), (545, 232), (540, 255), (515, 282), (492, 288), (478, 262), (462, 242)],
        [(550, 200), (640, 188), (740, 190), (830, 200), (860, 215), (820, 232), (770, 240), (720, 252), (660, 248), (600, 238), (560, 222), (545, 210)],
        [(770, 262), (815, 256), (835, 268), (815, 282), (775, 280)],
    ]
    DY = 48  # map panel starts at y=232; polygon coords were drafted at y~184
    conts = [[(x, yy + DY) for x, yy in poly] for poly in conts]
    for poly in conts:
        d.polygon(poly, fill=LAND, outline=LANDLINE)
    for jx, jy in [(845, 215), (852, 222), (880, 285)]:
        jy += DY
        d.ellipse([jx - 2, jy - 2, jx + 2, jy + 2], fill=LAND, outline=LANDLINE)
    labels = [("N. AMERICA", 105, 222), ("S. AMERICA", 218, 262), ("EUROPE", 478, 188),
              ("AFRICA", 478, 250), ("ASIA", 640, 208), ("OCEANIA", 762, 268)]
    fl = F(SANSB, 8)
    for txt, lx, ly in labels:
        d.text((lx, ly + DY), txt, font=fl, fill=(90, 80, 50))
    pins = [(1, 745, 222), (2, 492, 206), (3, 548, 238), (4, 185, 228),
            (5, 688, 240), (6, 545, 206), (7, 775, 238), (8, 505, 248)]
    pf = F(SANSB, 9)
    for n, px, py in pins:
        py += DY
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED, outline=(255, 255, 255), width=2)
        tw = d.textlength(str(n), font=pf)
        d.text((px - tw / 2, py - 6), str(n), font=pf, fill=(255, 255, 255))
    return pins

def build():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    rng = random.Random(20261119)
    # deterministic paper speckle + dot texture (visual richness / file size)
    for _ in range(42000):
        x = rng.randint(0, W - 1); y = rng.randint(0, H - 1)
        v = rng.randint(225, 245)
        d.point((x, y), fill=(v, v, 235))
    for gx in range(14, W - 10, 6):
        for gy in range(14, H - 10, 6):
            d.point((gx, gy), fill=(238, 236, 228))
    for x in range(0, W, 6):
        d.point((x, 4), fill=(200, 190, 170))
    # double outer border
    d.rectangle([6, 6, W - 7, H - 7], outline=INK, width=2)
    d.rectangle([11, 11, W - 12, H - 12], outline=GOLD, width=1)

    # ---- kicker ----
    kf = F(SANSB, 12)
    kt = data["kicker"]
    d.text(((W - d.textlength(kt, font=kf)) / 2, 20), kt, font=kf, fill=RED)
    d.line([28, 40, 996, 40], fill=INK, width=1)

    # ---- masthead ----
    mf = F(SERIFB, 54)
    title = data["title"]
    d.text(((W - d.textlength(title, font=mf)) / 2, 46), title, font=mf, fill=INK)
    draw_globe(d, 62, 72, 20)
    draw_globe(d, 962, 72, 20)
    df = F(SERIF, 17)
    dt = "Thursday, 19 November 2026  —  The day's news, verified against the wires"
    d.text(((W - d.textlength(dt, font=df)) / 2, 104), dt, font=df, fill=(60, 60, 55))
    d.line([28, 128, 996, 128], fill=INK, width=2)
    d.line([28, 131, 996, 131], fill=INK, width=1)

    # ---- lead banner (dark teal) ----
    d.rectangle([28, 138, 996, 200], fill=TEAL, outline=INK, width=1)
    d.rectangle([28, 138, 996, 146], fill=TEAL2)
    for hx in range(28, 996, 14):
        d.line([hx, 200, hx + 40, 138], fill=(22, 88, 94), width=1)
    lf = F(SERIFB, 23)
    d.text((44, 150), data["lead"]["headline"], font=lf, fill=(255, 255, 255))
    sf = F(SANS, 12)
    sub = wrap(d, data["lead"]["subhead"], sf, 780)
    d.text((44, 180), sub[0] if sub else "", font=sf, fill=(220, 235, 235))
    draw_summit(d, 852, 146)

    # ---- atlas map strip, directly under the lead ----
    d.rectangle([28, 208, 996, 212], fill=RED, width=1)
    mapf = F(SANSB, 11)
    d.text((28, 214), "ATLAS  —  WHERE THE DAY HAPPENED", font=mapf, fill=INK)
    draw_map(d, 28, 232, 996, 330)
    lg = F(SANSB, 9)
    d.text((28, 334), "PINS:  1 SHENZHEN   2 THE HAGUE   3 GAZA   4 NEW YORK   5 ODISHA   6 KYIV   7 MANILA   8 KHARTOUM",
           font=lg, fill=INK)
    d.line([28, 350, 996, 350], fill=INK, width=2)

    # ---- story columns ----
    cols = [(28, ["ASIA-PACIFIC", "AFRICA"]), (360, ["EUROPE", "MIDDLE EAST"]),
            (692, ["NORTH AMERICA", "WORLD, SCIENCE & CULTURE"])]
    secmap = {s["name"]: s for s in data["sections"]}
    disp = {"WORLD, SCIENCE & CULTURE": "WORLD & CULTURE"}
    hf = F(SANSB, 11)
    bf = F(SANS, 10)
    tf = F(SANSB, 9)
    col_bottom = 836
    for cx, names in cols:
        y = 360
        for name in names:
            sec = secmap[name]
            d.rectangle([cx, y, cx + 304, y + 20], fill=TEAL, outline=INK, width=1)
            d.text((cx + 6, y + 4), "%s  —  %d STORIES" % (disp.get(name, name), sec["count"]), font=hf, fill=(255, 255, 255))
            # section accent illustration at header right edge (small, clear of text)
            if name == "ASIA-PACIFIC":
                draw_cyclone(d, cx + 294, y + 10, 7)
            elif name == "NORTH AMERICA":
                draw_frame(d, cx + 276, y + 3, 24, 14)
            elif name == "WORLD, SCIENCE & CULTURE":
                draw_rocket(d, cx + 284, y + 2, 0.4)
            y += 24
            for si, st in enumerate(sec["stories"]):
                lines = wrap(d, st["h"], bf, 292)
                lines = lines[:2]
                if si % 2 == 0:
                    d.rectangle([cx, y, cx + 304, y + len(lines) * 12 + 3], fill=(246, 244, 236))
                d.text((cx + 2, y), "▪", font=bf, fill=RED)
                for i, ln in enumerate(lines):
                    d.text((cx + 12, y + i * 12), ln, font=bf, fill=INK)
                tag = " [" + st["s"] + "]"
                tw = d.textlength(tag, font=tf)
                last = lines[-1]
                lw = d.textlength(last, font=bf)
                if lw + tw <= 292:
                    d.text((cx + 12 + lw, y + (len(lines) - 1) * 12 + 1), tag, font=tf, fill=RED)
                y += len(lines) * 12 + 4
                d.line([cx, y - 1, cx + 304, y - 1], fill=(228, 226, 218), width=1)
            y += 4
        # fill remaining column space to the timeline with a drawn scene
        if y < col_bottom - 24:
            d.rectangle([cx, y, cx + 304, col_bottom], outline=GREY, width=1)
            mid = y + (col_bottom - y) // 2
            capf = F(SANS, 9)
            if cx == 28:
                draw_cyclone(d, cx + 34, mid, 20)
                d.text((cx + 66, y + 4), "CYCLONE AKVAN", font=F(SANSB, 11), fill=TEAL)
                cap = wrap(d, "Severe storm in the Bay of Bengal; winds 90-100 km/h, landfall Friday.", capf, 225)
                for i, ln in enumerate(cap[:2]):
                    d.text((cx + 66, y + 20 + i * 10), ln, font=capf, fill=INK)
            elif cx == 692:
                draw_rocket(d, cx + 18, mid - 18, 0.9)
                d.text((cx + 66, y + 4), "VOYAGER 1", font=F(SANSB, 11), fill=TEAL)
                cap = wrap(d, "One light-day from Earth: 16 billion miles, 49 years out.", capf, 225)
                for i, ln in enumerate(cap[:2]):
                    d.text((cx + 66, y + 20 + i * 10), ln, font=capf, fill=INK)
            else:
                draw_frame(d, cx + 16, mid - 14, 40, 28)
                d.text((cx + 66, y + 4), "THE $190.4m VAN GOGH", font=F(SANSB, 11), fill=TEAL)
                cap = wrap(d, "Blossoming Chestnut Trees, 1890 — a new artist record.", capf, 225)
                for i, ln in enumerate(cap[:2]):
                    d.text((cx + 66, y + 20 + i * 10), ln, font=capf, fill=INK)

    # ---- UTC timeline ----
    d.line([28, 844, 996, 844], fill=INK, width=2)
    d.text((28, 850), "THE DAY IN UTC  —  HOUR BY HOUR", font=F(SANSB, 11), fill=INK)
    tl = data["timeline"]
    cell_w, cell_h = 194, 42
    tf2 = F(SANSB, 10)
    xf = F(SANS, 9)
    for i, item in enumerate(tl):
        r, c = divmod(i, 5)
        x = 28 + c * cell_w
        yy = 868 + r * cell_h
        d.rectangle([x, yy, x + cell_w - 4, yy + cell_h - 4], fill=(238, 240, 235), outline=GREY, width=1)
        d.text((x + 4, yy + 2), item["t"], font=tf2, fill=RED)
        lines = wrap(d, item["h"], xf, cell_w - 10)
        for j, ln in enumerate(lines[:2]):
            d.text((x + 4, yy + 16 + j * 11), ln, font=xf, fill=INK)

    # ---- by the numbers ----
    d.rectangle([28, 956, 996, 988], fill=(245, 238, 210), outline=INK, width=1)
    nf = F(SANSB, 13)
    lf2 = F(SANS, 8)
    for i, nb in enumerate(data["numbers"]):
        x = 28 + i * 194
        d.text((x + 10, 960), nb["v"], font=nf, fill=RED)
        d.text((x + 10, 976), nb["l"], font=lf2, fill=INK)
        if i:
            d.line([x, 960, x, 984], fill=GREY, width=1)

    # ---- footer: date check + sources ----
    ff = F(SANS, 9)
    d.text((28, 994), data["datecheck"], font=ff, fill=INK)
    d.text((28, 1006), data["sources"], font=ff, fill=GREY)
    return img

if __name__ == "__main__":
    out = os.path.join(HERE, "entry.png")
    build().save(out, "PNG")
    print("wrote", out, os.path.getsize(out), "bytes")
