#!/usr/bin/env python3
"""Extrait une signature manuscrite COLOREE d'une capture d'ecran et rend le fond transparent.
Usage : python3 extraire_signature.py <screenshot.jpg> [--hue blue|black|red]
Sortie : signature_extraite.png (PNG transparent, crop serre autour du trace).

Fonctionne pour une signature dans un app (barre claire, trace colore). Detecte le trace par
teinte, calcule la bounding box, recadre avec marge, puis passe le fond clair en alpha=0.
"""
import argparse
from PIL import Image

HUES = {
    "blue":  lambda r,g,b: b > 120 and (b - r) > 40 and (b - g) > 40,
    "black": lambda r,g,b: r < 80 and g < 80 and b < 80,
    "red":   lambda r,g,b: r > 140 and (r - g) > 40 and (r - b) > 40,
}

def is_bg(r, g, b):
    # fond blanc/gris clair -> transparent
    return r > 200 and g > 200 and b > 200

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--hue", default="blue", choices=list(HUES))
    ap.add_argument("--margin", type=int, default=15)
    ap.add_argument("--out", default="signature_extraite.png")
    a = ap.parse_args()

    im = Image.open(a.image).convert("RGBA")
    W, H = im.size
    px = im.load()
    test = HUES[a.hue]

    minx, maxx, miny, maxy = W, 0, H, 0
    found = False
    for y in range(H):
        for x in range(W):
            r, g, b, _ = px[x, y]
            if test(r, g, b):
                found = True
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
    if not found:
        raise SystemExit("Aucun trace de couleur '%s' trouve." % a.hue)

    m = a.margin
    crop = im.crop((max(0, minx - m), max(0, miny - m),
                   min(W, maxx + m), min(H, maxy + m)))
    cp = crop.load()
    cw, ch = crop.size
    for y in range(ch):
        for x in range(cw):
            r, g, b, _ = cp[x, y]
            if is_bg(r, g, b):
                cp[x, y] = (255, 255, 255, 0)
            else:
                cp[x, y] = (r, g, b, 255)
    crop.save(a.out)
    print("Signature extraite ->", a.out, "taille", crop.size)

if __name__ == "__main__":
    main()
