#!/usr/bin/env python3
"""Génère des icônes PWA PNG (192, 512, maskable) sans dépendance externe.

Usage: python3 make_icons.py [dossier_sortie]
Sortie: icon-192.png, icon-512.png, icon-maskable.png
"""
import os
import struct
import sys
import zlib


def png_chunk(typ, data):
    c = typ + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)


def make_icon(size, path, maskable=False):
    bg = (20, 74, 133)       # #144a85
    paper = (255, 255, 255)
    line = (200, 220, 240)
    mx0, mx1 = 0.18, (0.78 if maskable else 0.82)
    my0, my1 = 0.16, (0.78 if maskable else 0.84)
    rows = []
    for y in range(size):
        row = bytearray()
        ry = y / size
        for x in range(size):
            rx = x / size
            r, g, b = bg
            if mx0 <= rx <= mx1 and my0 <= ry <= my1:
                r, g, b = paper
                for i in (0.32, 0.46, 0.60, 0.74):
                    if abs(ry - i) < 0.008 and mx0 + 0.06 < rx < mx1 - 0.05:
                        r, g, b = line
                if abs(rx - (mx0 + 0.035)) < 0.012:
                    r, g, b = bg
            row += bytes((r, g, b))
        rows.append(bytes(row))
    raw = b"".join(b"\x00" + r for r in rows)
    data = (b"\x89PNG\r\n\x1a\n"
            + png_chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + png_chunk(b"IDAT", zlib.compress(raw, 9))
            + png_chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "signature PNG invalide"
    print(f"  {path}: {len(data)} octets ({size}x{size})")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    make_icon(192, os.path.join(out, "icon-192.png"))
    make_icon(512, os.path.join(out, "icon-512.png"))
    make_icon(512, os.path.join(out, "icon-maskable.png"), maskable=True)


if __name__ == "__main__":
    main()
