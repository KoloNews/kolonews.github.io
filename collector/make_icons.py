#!/usr/bin/env python3
"""Малює іконки «Коло Новин» (кольорове кільце) у PNG без сторонніх бібліотек.
Запуск один раз: python3 collector/make_icons.py"""

import math
import struct
import zlib
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
STOPS = [(0.00, (79, 195, 255)), (0.25, (125, 92, 255)), (0.50, (255, 95, 138)), (0.75, (255, 179, 64)), (1.00, (79, 195, 255))]
BG = (12, 14, 18)


def ring_color(t):
    for (a, ca), (b, cb) in zip(STOPS, STOPS[1:]):
        if a <= t <= b:
            k = (t - a) / (b - a)
            return tuple(ca[i] + (cb[i] - ca[i]) * k for i in range(3))
    return STOPS[0][1]


def png(size, path):
    c = size / 2
    r_out, r_in = size * 0.34, size * 0.25
    dot_r = size * 0.055
    dot = (c + r_out * 0.98 * math.cos(-math.pi / 4), c + r_out * 0.98 * math.sin(-math.pi / 4))
    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            px, py = x + 0.5, y + 0.5
            d = math.hypot(px - c, py - c)
            a_ring = max(0.0, min(1.0, r_out - d + 0.5)) * max(0.0, min(1.0, d - r_in + 0.5))
            t = ((math.atan2(py - c, px - c) + math.pi / 2) / (2 * math.pi)) % 1.0
            col = ring_color(t)
            pix = [BG[i] * (1 - a_ring) + col[i] * a_ring for i in range(3)]
            dd = math.hypot(px - dot[0], py - dot[1])
            a_dot = max(0.0, min(1.0, dot_r - dd + 0.5))
            pix = [pix[i] * (1 - a_dot) + 255 * a_dot for i in range(3)]
            row += bytes(int(round(v)) for v in pix)
        rows.append(bytes(row))
    raw = zlib.compress(b"".join(rows), 9)

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)) + chunk(b"IDAT", raw) + chunk(b"IEND", b"")
    path.write_bytes(data)


if __name__ == "__main__":
    for s in (180, 192, 512):
        png(s, OUT / f"icon-{s}.png")
    print("Іконки готові:", OUT)
