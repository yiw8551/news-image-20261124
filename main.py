#!/usr/bin/env python3
"""Sum up 24 November 2026 world news in one 1024x1024 image.

Deterministic, standard-library only. Renders a newspaper-style page:
masthead, 3 featured stories, then 31 compact numbered stories with
region tags (34 stories, 8 regions). Writes /output/entry.png when
/output exists, otherwise ./output/entry.png.
"""
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 243, 234)
INK = (18, 20, 24)
GRAY = (84, 88, 96)
ACCENT = (178, 32, 40)
TILE = (255, 255, 255)
MAST = (16, 17, 20)
WHITE = (250, 250, 248)
RULE = (18, 20, 24)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, rows as strings of '#' and '.'.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "'": (".##..", ".##..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "*": (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
}

# ------------------------------------------------------------- content
FEATURED = [
    ("NORTH AMERICA",
     "NVIDIA RESTORES HUANG AS CEO",
     "BOARD REVERSES COURSE 11 DAYS AFTER JENSEN HUANG QUIT; "
     "SHARES LEAPT ABOUT 30% ON TRUMP BACKING."),
    ("RUSSIA",
     "MEDVEDEV: PREVENTIVE NUCLEAR STRIKE",
     "SAYS UKRAINE AND NATO CROSSED LINES THAT COULD "
     "JUSTIFY A FIRST STRIKE."),
    ("BUSINESS",
     "SANOFI TO BUY INSMED FOR $41 BILLION",
     "PAYS $175 A SHARE IN CASH FOR THE US BIOTECH: "
     "THE YEAR'S BIGGEST PHARMA DEAL."),
]

ITEMS = [
    ("UKRAINE", "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA IN DRONE STRIKE"),
    ("RUSSIA", "LEAKED RECORDS: 490,000 RUSSIAN WAR DEAD LOGGED; TOLL MAY TOP 700,000"),
    ("UKRAINE", "STRIKE ON ZAPORIZHZHIA FLATS KILLS 2, WOUNDS 40 INCL. 4 CHILDREN"),
    ("EUROPE", "NATO SENDS AWACS RADAR PLANE TO POLAND AFTER RUSSIAN MISSILES LAND"),
    ("EUROPE", "TWO SCHOOL EMPLOYEES INJURED IN SHOOTING IN SERBIA"),
    ("EUROPE", "TWO MEN ARRESTED OVER BREAK-IN AT PRINCE WILLIAM'S HOME"),
    ("EUROPE", "GREECE'S OLDEST MODERN MUSEUM REOPENS ON THE ACROPOLIS"),
    ("MIDEAST", "ISRAELI STRIKE KILLS HAMAS SECURITY CHIEF ABU NAHEL, 6 OTHERS IN GAZA"),
    ("MIDEAST", "OXFAM: WAR HAS TURNED GAZA INTO A 'TOXIC LAND'"),
    ("MIDEAST", "HOUTHIS CLOSE TO 60 KM FROM ADEN; YEMEN ARMY VOWS TO HOLD CITY"),
    ("MIDEAST", "QATAR PM MEETS VANCE, RUBIO AS DOHA SEEKS TO REVIVE US-IRAN TALKS"),
    ("MIDEAST", "ISRAEL'S EISENKOT SIGNS FIRST COALITION DEAL WITH LIEBERMAN'S PARTY"),
    ("ASIA", "UK RECOGNISES ROHINGYA GENOCIDE, SANCTIONS 5 MYANMAR GENERALS"),
    ("ASIA", "CHINA PROBES POLITBURO MEMBER CHEN JINING, SHANGHAI PARTY CHIEF"),
    ("ASIA", "CHINA EXTENDS PAUSE ON GALLIUM, GERMANIUM EXPORT CURBS TO US"),
    ("ASIA", "SOUTH KOREA OFFERS UP TO $375,000 TO CATCH AI EXAM CHEATS"),
    ("ASIA", "REPORT: CHINA RAN AI SOCIAL-MEDIA CAMPAIGN TARGETING TAIWAN VOTE"),
    ("ASIA", "MAGNITUDE 5.6 EARTHQUAKE HITS NEPAL NEAR CHINESE BORDER"),
    ("ASIA", "MORE BODIES RECOVERED FROM INDONESIA CANDY FACTORY FIRE"),
    ("ASIA", "HANOI HOT-POT RESTAURANT BLAST KILLS 6, INJURES A DOZEN"),
    ("AFRICA", "DRONES HIT KHARTOUM HOMES, UN BUILDING; 4 CIVILIANS KILLED"),
    ("AFRICA", "175 MIGRANTS UNACCOUNTED FOR AS BOAT FROM SENEGAL LOSES CONTACT"),
    ("AFRICA", "NIGERIA'S TINUBU ASKS MPS TO TRIM 2026 BUDGET TO 65.2 TRILLION NAIRA"),
    ("LATAM", "CAR BOMB DESTROYS BUILDINGS IN VILLAVICENCIO, COLOMBIA"),
    ("LATAM", "MEXICO TO TRY 'EL CHAPO ISIDRO' AT HOME DESPITE US EXTRADITION BID"),
    ("N AMERICA", "VIRGINIA, OREGON SUE MUSK'S SPACEX FIRMS OVER GROK IMAGES"),
    ("N AMERICA", "TRUMP TO ORDER DOJ TO EXPEDITE FEDERAL EXECUTIONS"),
    ("N AMERICA", "DOJ ADMITS US CITIZEN WRONGLY DEPORTED IN ICE MIX-UP"),
    ("N AMERICA", "US CONSUMER CONFIDENCE HITS HIGHEST IN NEARLY TWO YEARS"),
    ("N AMERICA", "MICROSOFT DECLARES 'CODE RED' AFTER HISTORIC OUTAGE"),
    ("GLOBAL", "UN CHIEF URGES GLOBAL AI RISK FRAMEWORK WITHIN A YEAR"),
]

# ------------------------------------------------------------ drawing
buf = bytearray(W * H * 3)


def fill(x, y, w, h, color):
    r, g, b = color
    for yy in range(max(0, y), min(H, y + h)):
        base = (yy * W + max(0, x)) * 3
        for xx in range(max(0, x), min(W, x + w)):
            i = base + (xx - max(0, x)) * 3
            buf[i] = r
            buf[i + 1] = g
            buf[i + 2] = b


def text_w(s, scale, adv=None):
    if adv is None:
        adv = 6 * scale
    return len(s) * adv - (adv - 5 * scale)


def draw_text(x, y, s, scale, color, adv=None):
    if adv is None:
        adv = 6 * scale
    r, g, b = color
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for gy in range(7):
            row = glyph[gy]
            for gx in range(5):
                if row[gx] == "#":
                    px = cx + gx * scale
                    py = y + gy * scale
                    for dy in range(scale):
                        if 0 <= py + dy < H:
                            base = ((py + dy) * W) * 3
                            for dx in range(scale):
                                if 0 <= px + dx < W:
                                    i = base + (px + dx) * 3
                                    buf[i] = r
                                    buf[i + 1] = g
                                    buf[i + 2] = b
        cx += adv
    return cx


def wrap(s, max_chars):
    lines = []
    cur = ""
    for word in s.split(" "):
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_item(x, y, idx, tag, text, col_w):
    """One compact numbered item; returns height used."""
    scale = 2
    adv = 11  # tight tracking so items fit two lines
    prefix = "%02d %s: " % (idx, tag)
    full = prefix + text
    max_chars = (col_w - 4) // adv
    lines = wrap(full, max_chars)
    line_h = 7 * scale + 5
    for li, line in enumerate(lines):
        draw_text(x, y + li * line_h, line, scale, INK, adv)
    # overdraw number+tag prefix in accent on the first line
    draw_text(x, y, prefix.rstrip(), scale, ACCENT, adv)
    return len(lines) * line_h


def main():
    fill(0, 0, W, H, PAPER)

    # masthead
    fill(0, 0, W, 96, MAST)
    title = "THE DAY IN ONE IMAGE"
    draw_text((W - text_w(title, 6)) // 2, 9, title, 6, WHITE)
    date = "TUESDAY 24 NOVEMBER 2026"
    draw_text((W - text_w(date, 3)) // 2, 60, date, 3, (232, 120, 124))
    fill(0, 96, W, 6, ACCENT)

    # featured tiles
    fy = 110
    fh = 196
    tw = 328
    for i, (tag, head, body) in enumerate(FEATURED):
        x = 12 + i * (tw + 8)
        fill(x, fy, tw, fh, TILE)
        fill(x, fy, tw, 6, ACCENT)
        draw_text(x + 10, fy + 12, tag, 2, ACCENT)
        hy = fy + 36
        for line in wrap(head, (tw - 20) // 18):
            draw_text(x + 10, hy, line, 3, INK)
            hy += 29
        hy += 4
        for line in wrap(body, (tw - 20) // 11):
            draw_text(x + 10, hy, line, 2, GRAY, 11)
            hy += 19

    # compact grid: 2 columns, row-wise
    gy = fy + fh + 8
    col_w = 494
    xs = [12, 518]
    row_h = 42
    rows = (len(ITEMS) + 1) // 2
    fill(511, gy - 2, 2, rows * row_h - 4, (203, 198, 187))
    for n, (tag, text) in enumerate(ITEMS):
        row, col = divmod(n, 2)
        draw_item(xs[col], gy + row * row_h, n + 1, tag, text, col_w)

    # footer
    fill(0, 994, W, 2, RULE)
    left = "34 STORIES - 8 REGIONS"
    draw_text(12, 1003, left, 2, GRAY)
    right = "SOURCES: REUTERS - AP - AFP - BBC - AL JAZEERA - WSJ"
    draw_text(W - 12 - text_w(right, 2), 1003, right, 2, GRAY)

    # encode PNG
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += buf[yy * W * 3:(yy + 1) * W * 3]

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        c += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))

    if os.path.isdir("/output"):
        out = "/output/entry.png"
    else:
        out = os.path.join(".", "output", "entry.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as fh:
        fh.write(png)
    print("wrote", out, len(png), "bytes")


if __name__ == "__main__":
    main()
