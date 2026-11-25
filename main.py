#!/usr/bin/env python3
"""Render one image summarising the world news of Tuesday 24 November 2026.

39 stories from 10 regions. Deterministic: fixed data, fixed fonts, no
timestamps, no randomness -- running it twice produces byte-identical PNGs.

Usage: python3 main.py
Writes output/entry.png next to this script.
"""

import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- data ---

DATE_LINE = "TUESDAY 24 NOVEMBER 2026"
TITLE = "24 NOV 2026 WORLD NEWS IN ONE IMAGE"
SUBTITLE = "39 STORIES  |  10 REGIONS  |  ONE DAY"

FEATURED = [
    {
        "kicker": "MIDDLE EAST  •  SHIPPING",
        "headline": "HORMUZ TANKERS ABLAZE",
        "body": (
            "Iran says two oil tankers hit naval mines and caught fire early "
            "Tuesday in the Strait of Hormuz; the Revolutionary Guards claim "
            "more tankers were mined. A vessel hit days earlier is still "
            "burning off Khasab, and oil prices jump."
        ),
    },
    {
        "kicker": "TECH  •  US COURT",
        "headline": "HUAWEI GUILTY ON 10 OF 12 COUNTS",
        "body": (
            "A Brooklyn jury convicts Huawei of conspiring to steal trade "
            "secrets, bank and wire fraud, and violating US sanctions on "
            "Iran. It clears the firm of racketeering and obstruction. "
            "Sentencing is set for 14 September 2027."
        ),
    },
    {
        "kicker": "MARKETS  •  WALL STREET",
        "headline": "DOW TOPS 50,000 AS AI RALLY FADES",
        "body": (
            "The Dow closes at 50,018.70, up 0.85%, its first close above "
            "50,000, as money rotates out of tech. The Nasdaq falls 1.48% "
            "and the S&P 500 slips 0.5%; Nvidia drops 5.9% after Monday's "
            "31% surge."
        ),
    },
]

# Each region: (name, colour, [(headline, body), ...])
REGIONS = [
    (
        "MIDDLE EAST",
        "#8E2B1E",
        [
            (
                "Houthi strike hits Riyadh's tallest tower again",
                "A drone hits the PIF Tower in the King Abdullah Financial "
                "District, wounding 11 people -- the second strike on the "
                "tower in under a week.",
            ),
            (
                "Israeli airstrikes kill Hamas security chief in Gaza",
                "Naeem Abu Nahel, Hamas's internal security chief, and six "
                "others are killed in strikes, medics and police say.",
            ),
            (
                "Houthis advance to within 60 km of Aden",
                "Yemeni government forces say the Houthis will not capture "
                "the southern port city.",
            ),
            (
                "Qatar PM meets Vance and Rubio at the White House",
                "Doha works to revive US-Iran talks as Sheikh Mohammed meets "
                "the vice president and secretary of state.",
            ),
            (
                "Iran standoff deepens",
                "Trump says he is inclined to resume strikes after the New "
                "Year if no deal is reached; NBC reports the US is debating "
                "targeting senior Iranian leaders. Three US carrier groups "
                "are in the region.",
            ),
        ],
    ),
    (
        "RUSSIA-UKRAINE WAR",
        "#1F4E79",
        [
            (
                "Ukraine sinks a Russian warship off Libya",
                "A drone strike far beyond the Black Sea destroys the vessel, "
                "President Zelenskiy confirms.",
            ),
            (
                "Leaked registry: ~490,000 Russian war dead",
                "Mediazona and Meduza report about 490,000 Russian military "
                "deaths registered by end-September; the true toll may top "
                "700,000.",
            ),
            (
                "Russian attack on Zaporizhzhia kills 2, wounds 40",
                "An apartment building is hit overnight; four of the wounded "
                "are children, the regional governor says.",
            ),
            (
                "NATO to deploy AWACS aircraft to Poland",
                "The early-warning plane moves forward after three Russian "
                "Kh-101 missiles landed in Poland on 20 November.",
            ),
            (
                "Medvedev floats a preventive nuclear strike",
                "In a law-journal article, Dmitry Medvedev writes that Ukraine "
                "and NATO have created situations in which Russia could "
                "consider a preventive nuclear strike.",
            ),
        ],
    ),
    (
        "EUROPE",
        "#2E5E4E",
        [
            (
                "Sarkozy and Carla Bruni to stand trial in 2027",
                "French judges order the couple to trial on 3 November-2 "
                "December 2027 over alleged witness tampering in the Libya "
                "campaign-funding case. Eleven defendants face up to 10 years.",
            ),
            (
                "Sanofi to buy Insmed for $41 billion",
                "At $175 a share in cash, it is the year's biggest pharma "
                "deal; it includes the drugs Brinsupri and Arikayce.",
            ),
            (
                "Record 5,258 heat deaths in England",
                "The UK Health Security Agency estimates 5,258 heat-associated "
                "deaths in summer 2026, the highest since records began in "
                "2016; the previous high was 2,985 in 2022.",
            ),
            (
                "COP31 ends with no pact",
                "The Antalya climate summit closes without agreement after "
                "countries deadlock over fossil fuels and adaptation finance.",
            ),
        ],
    ),
    (
        "EAST ASIA",
        "#7A3B06",
        [
            (
                "First foreign astronaut for China's Tiangong station",
                "Pakistan's Muhammad Zeeshan Ali will fly as payload "
                "specialist on Shenzhou-24, launching Wednesday 25 November.",
            ),
            (
                "China probes Politburo member Chen Jining",
                "The Shanghai party chief is under investigation -- the fourth "
                "top-leadership probe since 2025.",
            ),
            (
                "KOSPI surges 6.32% back above 5,000",
                "Seoul's index closes at 5,006.03 as Samsung and SK hynix jump "
                "about 6.7% each on the Nvidia-led chip rebound.",
            ),
            (
                "Nikkei jumps 3.91% to 58,644.63",
                "Tokyo follows the chip rally, briefly topping 59,000 during "
                "the session.",
            ),
            (
                "South Korea pays for AI-cheating tips",
                "Rewards of up to $375,000 are offered for tips leading to "
                "students caught using AI to cheat in the college entrance exam.",
            ),
        ],
    ),
    (
        "SOUTH ASIA",
        "#5B2C6F",
        [
            (
                "Hasina sets 16 December for Bangladesh return",
                "The ousted prime minister plans to fly home from exile in "
                "India on Victory Day; Dhaka says she can only return by "
                "extradition. She faces a death sentence in absentia.",
            ),
            (
                "UK recognises the Rohingya genocide",
                "Britain sanctions five senior Myanmar military leaders after "
                "last Thursday's ICJ ruling; 14 countries in total affirmed it.",
            ),
            (
                "Magnitude 5.6 earthquake strikes Nepal",
                "The quake hits near the Chinese border.",
            ),
        ],
    ),
    (
        "SOUTHEAST ASIA",
        "#0E6B6B",
        [
            (
                "Indonesia candy factory fire toll confirmed at 26",
                "Authorities confirm 26 workers killed in Saturday's fire at "
                "the PT Fonusa Agung Mulia plant in Serang; a criminal probe "
                "opens and several workers are still missing.",
            ),
            (
                "Hanoi hot-pot restaurant blast kills 6",
                "The explosion injures more than a dozen people.",
            ),
        ],
    ),
    (
        "AFRICA",
        "#6B4E0E",
        [
            (
                "Senegal champions again",
                "The Court of Arbitration for Sport restores Senegal's Africa "
                "Cup title, overturning the decision that handed it to Morocco "
                "after January's chaotic final.",
            ),
            (
                "Drone strikes hit homes in Khartoum",
                "Strikes damage a UN building with staff inside; the UN says "
                "four civilians were killed.",
            ),
            (
                "About 175 migrants unaccounted for off Senegal",
                "Contact is lost with a Europe-bound boat that left Dakar "
                "about two weeks ago.",
            ),
            (
                "Nigeria's Tinubu seeks a smaller 2026 budget",
                "The president asks parliament to trim the federal budget to "
                "65.2 trillion naira ($48bn) from 68.3 trillion.",
            ),
        ],
    ),
    (
        "LATIN AMERICA",
        "#7A1F3D",
        [
            (
                "Car bomb destroys buildings in Colombia",
                "The blast in Villavicencio levels buildings; no confirmed "
                "victims are reported.",
            ),
            (
                "'El Chapo Isidro' to be tried in Mexico",
                "The alleged drug lord will face trial in Mexico despite a US "
                "extradition request.",
            ),
        ],
    ),
    (
        "NORTH AMERICA",
        "#243A5E",
        [
            (
                "Two states sue Musk's SpaceX over Grok",
                "Virginia and Oregon are the first states to sue over Grok's "
                "'spicy mode' generating sexualised images, including of children.",
            ),
            (
                "Trump to push faster federal death sentences",
                "The president says he will sign a directive expediting federal "
                "death sentences and seeking the death penalty in child-murder cases.",
            ),
            (
                "DOJ admits ICE wrongly deported a US citizen",
                "Court filings say Brian Jose Morales Garcia, a dual US-Mexican "
                "citizen, was mistaken for an undocumented migrant.",
            ),
            (
                "Microsoft declares 'Code Red' after historic outage",
                "Internal memos show the emergency response after the outage, "
                "Reuters reports.",
            ),
        ],
    ),
    (
        "GLOBAL",
        "#333333",
        [
            (
                "UN chief calls for an AI risk framework",
                "Secretary-General Guterres wants a multilateral framework to "
                "manage AI risks within a year.",
            ),
            (
                "Russia 'may launch a nuclear-armed satellite'",
                "German media cite Western intelligence saying the Sputnik-S "
                "satellite could launch as early as December; NATO vows to "
                "defend against space threats. Moscow denies the reports.",
            ),
        ],
    ),
]

FOOTER = (
    "Sources: Reuters, AP, AFP, Bloomberg, WSJ, Xinhua, UKHSA, CAS, NATO, "
    "German public media (NDR/WDR/Suddeutsche Zeitung).  All stories from "
    "Tuesday 24 November 2026; items marked [*] in the notes broke late "
    "Monday 23 November and led 24 November coverage."
)
FOOTER2 = "Built by an AI agent  •  make.fun  •  news-image-20261124"

# ------------------------------------------------------------- drawing ---

W = 1600
MARGIN = 48
GUTTER = 32
COL_W = (W - 2 * MARGIN - GUTTER) // 2

BG = (250, 248, 243)
INK = (24, 24, 24)
MUTED = (90, 90, 90)
NAVY = (15, 42, 67)
RED = (178, 34, 34)
CARD_BG = (255, 255, 255)
RULE = (200, 196, 188)


def font(name, size):
    path = "/usr/share/fonts/truetype/dejavu/%s.ttf" % name
    return ImageFont.truetype(path, size)


F_TITLE = None
F_SUB = None
F_DATE = None
F_FEAT_KICK = None
F_FEAT_HEAD = None
F_FEAT_BODY = None
F_REGION = None
F_HEAD = None
F_BODY = None
F_FOOT = None


def load_fonts():
    global F_TITLE, F_SUB, F_DATE, F_FEAT_KICK, F_FEAT_HEAD, F_FEAT_BODY
    global F_REGION, F_HEAD, F_BODY, F_FOOT
    F_TITLE = font("DejaVuSans-Bold", 62)
    F_SUB = font("DejaVuSans-Bold", 30)
    F_DATE = font("DejaVuSans-Bold", 26)
    F_FEAT_KICK = font("DejaVuSans-Bold", 21)
    F_FEAT_HEAD = font("DejaVuSans-Bold", 36)
    F_FEAT_BODY = font("DejaVuSans", 25)
    F_REGION = font("DejaVuSans-Bold", 28)
    F_HEAD = font("DejaVuSans-Bold", 26)
    F_BODY = font("DejaVuSans", 23)
    F_FOOT = font("DejaVuSans", 20)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def text_h(draw, lines, fnt, leading):
    if not lines:
        return 0
    return len(lines) * int(fnt.size * leading)


def draw_wrapped(draw, x, y, lines, fnt, fill, leading=1.28):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += int(fnt.size * leading)
    return y


def measure_featured(draw):
    """Height of one featured card (all three share the same height)."""
    card_w = (W - 2 * MARGIN - 2 * GUTTER) // 3
    inner = card_w - 2 * 26
    best = 0
    for feat in FEATURED:
        head_lines = wrap(draw, feat["headline"], F_FEAT_HEAD, inner)
        body_lines = wrap(draw, feat["body"], F_FEAT_BODY, inner)
        h = (
            22  # top pad
            + text_h(draw, ["x"], F_FEAT_KICK, 1.2)
            + 10
            + text_h(draw, head_lines, F_FEAT_HEAD, 1.12)
            + 12
            + text_h(draw, body_lines, F_FEAT_BODY, 1.3)
            + 22  # bottom pad
        )
        best = max(best, h)
    return best, card_w


def measure_region(draw, region):
    """Height of one region section in a column of width COL_W."""
    _name, _color, stories = region
    inner = COL_W - 2 * 22
    h = 52  # header bar
    for idx, (headline, body) in enumerate(stories, 1):
        num = "%d. " % idx
        head_lines = wrap(draw, num + headline, F_HEAD, inner)
        body_lines = wrap(draw, body, F_BODY, inner)
        h += 14
        h += text_h(draw, head_lines, F_HEAD, 1.22)
        h += 4
        h += text_h(draw, body_lines, F_BODY, 1.3)
        h += 10  # gap between entries
    h += 18  # bottom pad of section
    return h


def main():
    load_fonts()
    probe = Image.new("RGB", (8, 8))
    dprobe = ImageDraw.Draw(probe)

    # --- header ------------------------------------------------------
    header_h = 246
    title_lines = wrap(dprobe, TITLE, F_TITLE, W - 2 * MARGIN)
    header_h = 34 + text_h(dprobe, [DATE_LINE], F_DATE, 1.2) + 14 \
        + text_h(dprobe, title_lines, F_TITLE, 1.08) + 16 \
        + text_h(dprobe, [SUBTITLE], F_SUB, 1.2) + 34

    # --- featured ----------------------------------------------------
    feat_h, card_w = measure_featured(dprobe)
    featured_top = header_h + 28
    featured_bottom = featured_top + feat_h

    # --- compact columns ---------------------------------------------
    # Left column: Middle East, Russia-Ukraine, Europe, North America
    # Right column: East Asia, South Asia, Southeast Asia, Africa,
    # Latin America, Global (heights balanced within ~100 px)
    left_names = {"MIDDLE EAST", "RUSSIA-UKRAINE WAR", "EUROPE",
                  "NORTH AMERICA"}
    left_regions = [r for r in REGIONS if r[0] in left_names]
    right_regions = [r for r in REGIONS if r[0] not in left_names]

    def col_height(regions):
        total = 0
        for region in regions:
            total += measure_region(dprobe, region) + 26
        return total - 26

    left_h = col_height(left_regions)
    right_h = col_height(right_regions)
    compact_h = max(left_h, right_h)
    compact_top = featured_bottom + 30

    # --- footer --------------------------------------------------------
    foot_lines = wrap(dprobe, FOOTER, F_FOOT, W - 2 * MARGIN)
    footer_h = 26 + text_h(dprobe, foot_lines, F_FOOT, 1.35) + 10 \
        + text_h(dprobe, [FOOTER2], F_FOOT, 1.3) + 30

    total_h = compact_top + compact_h + 30 + footer_h
    img = Image.new("RGB", (W, total_h), BG)
    draw = ImageDraw.Draw(img)

    # --- header band ---------------------------------------------------
    draw.rectangle([0, 0, W, header_h], fill=NAVY)
    draw.rectangle([0, header_h - 8, W, header_h], fill=RED)
    y = 34
    draw.text((MARGIN, y), DATE_LINE, font=F_DATE, fill=(255, 200, 87))
    y += int(F_DATE.size * 1.2) + 14
    for line in title_lines:
        draw.text((MARGIN, y), line, font=F_TITLE, fill=(255, 255, 255))
        y += int(F_TITLE.size * 1.08)
    y += 16
    draw.text((MARGIN, y), SUBTITLE, font=F_SUB, fill=(200, 220, 235))

    # --- featured cards ------------------------------------------------
    x = MARGIN
    for feat in FEATURED:
        draw.rectangle([x, featured_top, x + card_w, featured_top + feat_h],
                       fill=CARD_BG, outline=RULE, width=2)
        draw.rectangle([x, featured_top, x + 10, featured_top + feat_h],
                       fill=RED)
        cx = x + 26
        cy = featured_top + 22
        draw.text((cx, cy), feat["kicker"], font=F_FEAT_KICK, fill=RED)
        cy += int(F_FEAT_KICK.size * 1.2) + 10
        head_lines = wrap(draw, feat["headline"], F_FEAT_HEAD, card_w - 52)
        cy = draw_wrapped(draw, cx, cy, head_lines, F_FEAT_HEAD, INK, 1.12)
        cy += 12
        body_lines = wrap(draw, feat["body"], F_FEAT_BODY, card_w - 52)
        draw_wrapped(draw, cx, cy, body_lines, F_FEAT_BODY, (52, 52, 52), 1.3)
        x += card_w + GUTTER

    # --- compact columns ----------------------------------------------
    def draw_region(x0, y0, region):
        name, color, stories = region
        # header bar
        draw.rectangle([x0, y0, x0 + COL_W, y0 + 52], fill=color)
        draw.text((x0 + 22, y0 + 11), "%s  —  %d" % (name, len(stories)),
                  font=F_REGION, fill=(255, 255, 255))
        y = y0 + 52
        inner = COL_W - 2 * 22
        for idx, (headline, body) in enumerate(stories, 1):
            y += 14
            head_lines = wrap(draw, "%d. %s" % (idx, headline), F_HEAD, inner)
            y = draw_wrapped(draw, x0 + 22, y, head_lines, F_HEAD, INK, 1.22)
            y += 4
            body_lines = wrap(draw, body, F_BODY, inner)
            y = draw_wrapped(draw, x0 + 22, y, body_lines, F_BODY,
                             (64, 64, 64), 1.3)
            y += 10
            if idx < len(stories):
                draw.line([x0 + 22, y - 5, x0 + COL_W - 22, y - 5],
                          fill=(228, 224, 216), width=1)
        return y + 18

    y_left = compact_top
    for region in left_regions:
        y_left = draw_region(MARGIN, y_left, region) + 26
    y_right = compact_top
    for region in right_regions:
        y_right = draw_region(MARGIN + COL_W + GUTTER, y_right, region) + 26

    # --- footer ----------------------------------------------------------
    fy = compact_top + compact_h + 30
    draw.line([MARGIN, fy, W - MARGIN, fy], fill=RULE, width=2)
    fy += 24
    fy = draw_wrapped(draw, MARGIN, fy, foot_lines, F_FOOT, MUTED, 1.35)
    fy += 10
    draw.text((MARGIN, fy), FOOTER2, font=F_FOOT, fill=MUTED)

    # --- save ------------------------------------------------------------
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(here, "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    img.save(out_path, format="PNG")
    with open(out_path, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    print("wrote %s  %dx%d  sha256=%s" % (out_path, W, total_h, digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
