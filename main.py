#!/usr/bin/env python3
"""THE DAY IN ONE IMAGE - 24 November 2026 world news summary.
Stdlib only, deterministic. Writes a 1024x1024 PNG.
"""
import os
import struct
import zlib

W = 1024
H = 1024

# Colours (R, G, B)
PAPER = (247, 243, 233)
INK = (18, 18, 18)
ACCENT = (164, 22, 22)
RULE = (18, 18, 18)
TILE_BG = (255, 254, 248)
GREY = (92, 88, 80)

# 5x7 bitmap font. Each glyph: 7 rows of 5 chars, '#' = on.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '/': ("....#", "...#.", "...#.", "..#..", "..#..", ".#...", "#...."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '%': ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"),
    '$': ("..#..", ".####", "#....", ".###.", "....#", "####.", "..#.."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
}


def blank_image():
    return bytearray(bytes(PAPER) * (W * H))


def fill_rect(img, x0, y0, w, h, col):
    for y in range(y0, y0 + h):
        if y < 0 or y >= H:
            continue
        base = (y * W) * 3
        for x in range(x0, x0 + w):
            if 0 <= x < W:
                i = base + x * 3
                img[i] = col[0]
                img[i + 1] = col[1]
                img[i + 2] = col[2]


def draw_char(img, ch, x, y, scale, col, bold=False):
    glyph = FONT.get(ch, FONT['?'])
    for r in range(7):
        row = glyph[r]
        for c in range(5):
            if row[c] == '#':
                fill_rect(img, x + c * scale, y + r * scale, scale, scale, col)
                if bold:
                    fill_rect(img, x + c * scale + 1, y + r * scale,
                              scale, scale, col)
    return 6 * scale + (1 if bold else 0)


def text_width(text, scale, bold=False):
    if not text:
        return 0
    adv = 6 * scale + (1 if bold else 0)
    return adv * len(text) - scale


def draw_text(img, text, x, y, scale, col, bold=False):
    cx = x
    for ch in text.upper():
        cx += draw_char(img, ch, cx, y, scale, col, bold)
    return cx


def draw_text_centered(img, text, y, scale, col, bold=False):
    tw = text_width(text, scale, bold)
    x = (W - tw) // 2
    draw_text(img, text, x, y, scale, col, bold)
    return x


def wrap_text(text, scale, max_w, bold=False):
    words = text.upper().split()
    lines = []
    cur = ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_width(trial, scale, bold) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            while text_width(wd, scale, bold) > max_w and len(wd) > 1:
                n = 1
                while n < len(wd) and text_width(wd[:n + 1], scale, bold) <= max_w:
                    n += 1
                lines.append(wd[:n])
                wd = wd[n:]
            cur = wd
    if cur:
        lines.append(cur)
    return lines


STORIES = [
    ("1", "MEDVEDEV FLOATS PREVENTIVE NUCLEAR STRIKE",
     "In a journal article, Russia's Dmitry Medvedev says Ukraine and NATO "
     "crossed lines that could justify a first nuclear strike. "
     "The decision, he writes, rests with Putin."),
    ("2", "NVIDIA BRINGS BACK JENSEN HUANG AS CEO",
     "The board reinstates Nvidia's co-founder 11 days after he resigned. "
     "Trump publicly backed his return, and the shares jump about 30%."),
    ("3", "SANOFI TO BUY INSMED FOR $41 BILLION",
     "France's Sanofi will pay $175 a share in cash for the US biotech, "
     "the biggest biotech deal in nearly three years. "
     "It should close in the first half of 2027."),
    ("4", "UK RECOGNISES ROHINGYA GENOCIDE",
     "After the ICJ ruled Myanmar committed genocide, Britain sanctions "
     "five senior Myanmar officers and plans a ban on jet fuel. "
     "Fourteen countries back the ruling."),
    ("5", "TWO US STATES SUE MUSK'S SPACEX OVER GROK",
     "Virginia and Oregon say Grok's spicy mode produced sexualised "
     "images, including of children, and that safeguards were stripped "
     "out. First state lawsuits of their kind."),
    ("6", "LEAKED RECORDS: 490,000 RUSSIAN WAR DEAD",
     "Mediazona and Meduza analysed leaked Russian registry data: about "
     "490,000 military deaths registered, the true total modelled above "
     "700,000. Rosstat denies any leak."),
]


def render():
    img = blank_image()

    # Masthead
    fill_rect(img, 0, 0, W, 124, INK)
    draw_text_centered(img, "THE DAY IN ONE IMAGE", 12, 8, PAPER, bold=True)
    fill_rect(img, 262, 78, 500, 4, ACCENT)
    draw_text_centered(img, "TUESDAY 24 NOVEMBER 2026", 88, 3, PAPER)
    draw_text_centered(img, "WORLD NEWS - SIX STORIES THAT MATTER", 136, 2, GREY)

    # Tiles: 2 columns x 3 rows
    margin = 24
    gap = 16
    top = 164
    tile_w = (W - margin * 2 - gap) // 2
    tile_h = 256
    head_scale = 3
    body_scale = 2

    for idx, (num, head, body) in enumerate(STORIES):
        col_i = idx % 2
        row_i = idx // 2
        tx = margin + col_i * (tile_w + gap)
        ty = top + row_i * (tile_h + gap)
        fill_rect(img, tx, ty, tile_w, tile_h, TILE_BG)
        fill_rect(img, tx, ty, tile_w, 4, ACCENT)
        fill_rect(img, tx, ty, 4, tile_h, RULE)
        fill_rect(img, tx + tile_w - 4, ty, 4, tile_h, RULE)
        fill_rect(img, tx, ty + tile_h - 4, tile_w, 4, RULE)

        inner_x = tx + 18
        inner_w = tile_w - 36
        fill_rect(img, inner_x, ty + 16, 34, 34, ACCENT)
        draw_text(img, num, inner_x + 10, ty + 21, 3, PAPER, bold=True)

        hy = ty + 58
        for line in wrap_text(head, head_scale, inner_w, bold=True):
            draw_text(img, line, inner_x, hy, head_scale, INK, bold=True)
            hy += 7 * head_scale + 6

        fill_rect(img, inner_x, hy + 1, inner_w, 2, GREY)
        by = hy + 9
        for line in wrap_text(body, body_scale, inner_w):
            draw_text(img, line, inner_x, by, body_scale, INK)
            by += 7 * body_scale + 4

    # Footer
    fy = top + 3 * tile_h + 2 * gap + 14
    fill_rect(img, margin, fy, W - margin * 2, 3, RULE)
    draw_text_centered(img, "SOURCES: REUTERS - AP - WSJ - SCMP - MEDIAZONA",
                       fy + 14, 3, INK, bold=True)
    return bytes(img)


def png_bytes(rgb):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw.extend(rgb[y * stride:(y + 1) * stride])

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(raw), 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def main():
    data = png_bytes(render())
    if os.path.isdir("/output"):
        out_dir = "/output"
    else:
        out_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote", path, len(data), "bytes")


if __name__ == "__main__":
    main()
