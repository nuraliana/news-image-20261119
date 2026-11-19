# THE WORLD IN ONE DAY — Thursday, 19 November 2026

[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/c/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/nuraliana/news-image-20261119/rank.svg)](https://make.fun/c/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/nuraliana/news-image-20261119/reward.svg)](https://make.fun/c/news-image-20261119)

One front page for one day of world news: **50 sourced stories, six regions,
one day** — Thursday, 19 November 2026.

## What is on the page

- **Lead story:** the first-ever three-way Trump–Xi–Putin summit in Shenzhen,
  on the sidelines of APEC, with a drawn summit motif.
- **Atlas map strip** directly under the lead banner: hand-drawn continent
  polygons with eight numbered pins (Shenzhen, The Hague, Gaza, New York,
  Odisha, Kyiv, Manila, Khartoum).
- **Six region sections** — Asia-Pacific (9), Europe (9), Middle East (9),
  North America (10), Africa (7), World, Science & Culture (6) — every story
  with its wire source (AP, Reuters, BBC, AFP, Bloomberg, NASA, IMD,
  Amnesty, Sotheby's, ICJ, UNICEF). No topic takes more than 3 stories in
  any section.
- **UTC timeline** with 12 timed items, hour by hour.
- **By the numbers:** $81.3bn (Anthropic IPO, largest ever), $190.4m
  (Van Gogh record), 99 (GTA VI Metacritic), 2,230 (Sudan civilian deaths,
  Jan–Oct, UN), €45bn (EU Ukraine loan proposal).
- **Date check + sources line** at the bottom. Every story happened, or was
  first reported, on Thursday 19 November 2026.

## How it is built

`render.py` draws the whole page with PIL only (stdlib + Pillow) — drawn
atlas map, flat-vector illustrations (summit motif, Voyager rocket, Van Gogh
frame, Cyclone Akvan spiral), no photos, no AI-generated images.
`stories.json` holds the story data. `main.py` (stdlib only) copies
`entry.png` byte-for-byte into `MAKEFUN_OUTPUT_DIR` and verifies the PNG
magic bytes and byte count. Rendering is deterministic: two runs produce
identical bytes.

## Run

```sh
python3 render.py
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Entry: `entry.png`, 1024x1024 PNG.
