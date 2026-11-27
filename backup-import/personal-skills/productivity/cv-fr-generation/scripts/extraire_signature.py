#!/usr/bin/env python3
"""Extrait une signature MANUSCRITE d'une PHOTO / CAPTURE d'ecran et la rend
transparente pour servir de reference vivante (signature_kakesa_ref.png).

Usage :
  python3 extraire_signature.py CHEMIN_IMAGE [--couleur blue] [--out signature_kakesa_ref.png]

Etapes :
  1. Detecte l'encre par couleur (bleu par defaut : b>120 and b-r>40 and b-g>40 ;
     pour noir : r<80 and g<80 and b<80).
  2. Calcule la bbox, crop avec marge.
  3. Fond blanc/gris clair -> alpha 0 (transparent).
  4. Sauvegarde l'image de reference.
Verifiez ensuite avec vision_analyze que le rendu est propre (pas de texte
parasite, pas coupe) avant de l'inserer via modele_signature.inserer_signature().
"""
import argparse
from PIL import Image


def is_ink(r, g, b, color):
    if color == "blue":
        return b > 120 and (b - r) > 40 and (b - g) > 40
    if color == "black":
        return r < 90 and g < 90 and b < 90
    # generic dark ink
    return (r + g + b) / 3 < 110


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--couleur", default="blue", choices=["blue", "black", "dark"])
    ap.add_argument("--out", default="signature_kakesa_ref.png")
    ap.add_argument("--marge", type=int, default=15)
    a = ap.parse_args()

    im = Image.open(a.image).convert("RGB")
    W, H = im.size
    px = im.load()

    minx, maxx, miny, maxy = W, 0, H, 0
    found = False
    for y in range(H):
        for x in range(W):
            r, g, b = px[x, y]
            if is_ink(r, g, b, a.couleur):
                found = True
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
    if not found:
        raise SystemExit("Aucune encre detectee avec la couleur demandee.")

    m = a.marge
    crop = im.crop((max(0, minx - m), max(0, miny - m),
                    min(W, maxx + m), min(H, maxy + m)))

    crop = crop.convert("RGBA")
    pxa = crop.load()
    cw, ch = crop.size
    for y in range(ch):
        for x in range(cw):
            r, g, b, al = pxa[x, y]
            if r > 200 and g > 200 and b > 200:
                pxa[x, y] = (255, 255, 255, 0)
            else:
                pxa[x, y] = (r, g, b, 255)
    crop.save(a.out)
    print(f"Signature extraite -> {a.out}  (bbox x[{minx},{maxx}] y[{miny},{maxy}], "
          f"crop {crop.size})")


if __name__ == "__main__":
    main()
