#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODELE VIERGE — Attestation de formation (A4, 300 DPI).
Copie/modifie ce script pour tout modèle d'attestation / diplôme / certificat.
Identité KPGR (logistique humanitaire). Aucun logo d'État, aucun QR officiel.
Usage: python3 attestation_a4_kpgr.py  ->  genere attestation_kpgr.png + .pdf
"""
from PIL import Image, ImageDraw, ImageFont
import os

A4_W, A4_H = 2480, 3508
OUT_PNG = "/root/attestation_kpgr.png"
OUT_PDF = "/root/attestation_kpgr.pdf"

BG, INK   = (253, 251, 247), (34, 34, 34)
BLUE, BLUE_D = (11, 61, 145), (8, 42, 102)
AMBER, GREY = (232, 119, 34), (120, 120, 120)
WHITE = (255, 255, 255)

FD = "/usr/share/fonts/truetype/dejavu"
def font(p, s): return ImageFont.truetype(os.path.join(FD, p), s)

def tcenter(d, xy, txt, fnt, fill, anchor="mm"):
    d.text(xy, txt, font=fnt, fill=fill, anchor=anchor)

def draw_emblem(d, cx, cy, r):
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=BLUE, outline=WHITE, width=8)
    d.ellipse([cx-r+14, cy-r+14, cx+r-14, cy+r-14], outline=AMBER, width=5)
    cw, cl = int(r*0.16), int(r*0.34); ccy = cy-int(r*0.42)
    d.rectangle([cx-cw//2, ccy-cl, cx+cw//2, ccy+cl], fill=WHITE)
    d.rectangle([cx-cl, ccy-cw//2, cx+cl, ccy+cw//2], fill=WHITE)
    s = int(r*0.30); bx, by = cx, cy+int(r*0.30)
    d.rectangle([bx-s, by-s, bx+s, by+s], outline=WHITE, width=6)
    d.line([bx-s, by-s, bx, by-s-int(s*0.7)], fill=WHITE, width=6)
    d.line([bx+s, by-s, bx, by-s-int(s*0.7)], fill=WHITE, width=6)
    tcenter(d, (cx, cy+int(r*0.02)), "KPGR", font("DejaVuSerif-Bold.ttf", int(r*0.34)), WHITE)

def field_line(d, x1, x2, y, label):
    d.text((x1, y-30), label, font=font("DejaVuSans-Bold.ttf", 44), fill=BLUE)
    d.line([x1, y+44, x2, y+44], fill=GREY, width=3)

def wrap(d, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur+" "+w).strip()
        if d.textlength(t, font=fnt) <= max_w: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

img = Image.new("RGB", (A4_W, A4_H), BG)
d = ImageDraw.Draw(img)

# cadre
m = 70
d.rectangle([m, m, A4_W-m, A4_H-m], outline=BLUE, width=6)
d.rectangle([m+22, m+22, A4_W-m-22, A4_H-m-22], outline=AMBER, width=3)

# en-tête
Y = 200
draw_emblem(d, 400, Y+230, 200)
tcenter(d, (760, Y+150), "KPGR", font("DejaVuSerif-Bold.ttf", 96), BLUE_D, "lm")
tcenter(d, (762, Y+270), "KINSHASA · HUMANITARIAN LOGISTICS", font("DejaVuSans-Bold.ttf", 44), AMBER, "lm")
tcenter(d, (762, Y+330), "Relief · Supply Chain · Formation", font("DejaVuSans-Oblique.ttf", 38), GREY, "lm")
d.line([160, Y+470, A4_W-160, Y+470], fill=BLUE, width=4)
d.line([160, Y+480, A4_W-160, Y+480], fill=AMBER, width=3)

# titre
TY = 980
tcenter(d, (A4_W//2, TY), "ATTESTATION DE FORMATION", font("DejaVuSerif-Bold.ttf", 110), BLUE_D)
tcenter(d, (A4_W//2, TY+130), "EN LOGISTIQUE HUMANITAIRE", font("DejaVuSans-Bold.ttf", 70), AMBER)
d.polygon([(A4_W//2-40, TY+210),(A4_W//2, TY+250),(A4_W//2+40, TY+210),(A4_W//2, TY+170)], fill=BLUE)

# corps
para = ("La présente attestation certifie que le participant ci-dessous a suivi "
        "avec assiduité et réussite le programme de formation en logistique "
        "humanitaire dispensé par KPGR, portant sur la gestion des chaînes "
        "d'approvisionnement, le stockage, le transport et la distribution "
        "d'aide humanitaire.")
b = font("DejaVuSans.ttf", 52); yy = 1560
for ln in wrap(d, para, b, A4_W-520):
    tcenter(d, (A4_W//2, yy), ln, b, INK, "ma"); yy += 70
yy += 50
for lab in ["NOM & PRÉNOM DU PARTICIPANT", "RÉFÉRENCE DE LA FORMATION",
            "PÉRIODE (DU — AU)", "DURÉE TOTALE", "LIEU DE FORMATION"]:
    field_line(d, 360, A4_W-360, yy, lab); yy += 150
d.text((360, yy+30), "Cette attestation est délivrée pour servir et valoir ce que de droit.",
       font=font("DejaVuSans-Oblique.ttf", 40), fill=GREY)

# signatures
SY = A4_H-720
d.line([360, SY, 1120, SY], fill=GREY, width=3)
d.line([A4_W-1120, SY, A4_W-360, SY], fill=GREY, width=3)
tcenter(d, (740, SY+50), "LE FORMATEUR", font("DejaVuSans-Bold.ttf", 42), BLUE_D)
tcenter(d, (A4_W-740, SY+50), "LE DIRECTEUR KPGR", font("DejaVuSans-Bold.ttf", 42), BLUE_D)

# sceau + footer
sx, sy, sr = A4_W-420, A4_H-360, 190
d.ellipse([sx-sr, sy-sr, sx+sr, sy+sr], outline=AMBER, width=10)
d.ellipse([sx-sr+16, sy-sr+16, sx+sr-16, sy+sr-16], outline=AMBER, width=4)
tcenter(d, (sx, sy-40), "KPGR", font("DejaVuSans-Bold.ttf", 40), AMBER)
tcenter(d, (sx, sy+10), "CERTIFIÉ", font("DejaVuSans-Bold.ttf", 34), AMBER)
tcenter(d, (sx, sy+55), "2026", font("DejaVuSans.ttf", 32), AMBER)
tcenter(d, (A4_W//2, A4_H-150),
        "KPGR — Kinshasa, République Démocratique du Congo · Modèle d'attestation",
        font("DejaVuSans-Oblique.ttf", 34), GREY)

img.save(OUT_PNG, "PNG", dpi=(300, 300))
img.convert("RGB").save(OUT_PDF, "PDF", dpi=(300, 300), resolution=300.0)
print("PNG:", OUT_PNG, img.size, "| PDF:", OUT_PDF)
