#!/usr/bin/env python3
"""MODELE DE SIGNATURE - REFERENCE VIVANTE (KAKESA MUDIMBA DIEUDONNE).

Copie du module /root/linkedin_app/modele_signature.py, conservee dans le skill
comme reference. Signature manuscrite extraite d'une capture (bleue, fond transparent).
Standards VALIDES par l'utilisateur le 14/07/2026 :
  - hauteur signature : 16 mm (agrandie, lisible)
  - signature CENTREE horizontalement au-dessus du nom
  - nom tape en dessous, meme centre, en gras
  - zone de 75 mm a droite pour eviter que le nom soit coupe

Image de reference (source unique) : /root/linkedin_app/signature_kakesa_ref.png
"""
from PIL import Image
import os

SIG_REF = "/root/linkedin_app/signature_kakesa_ref.png"
NOM = "KAKESA MUDIMBA DIEUDONNE"
SIG_H_MM = 16
ZONE_MM = 75


def inserer_signature(pdf, zone_x, y, zone_w=ZONE_MM,
                      font_name="DJ", font_size=12, font_style="B",
                      nom=NOM, sig_h=SIG_H_MM):
    """Insere la signature (centree) puis le nom tape centre sous elle.

    zone_x, y : coin haut-gauche de la zone (mm, coord fpdf)
    zone_w    : largeur de la zone (mm)
    Renvoie le y apres le bloc signature.
    """
    if not os.path.exists(SIG_REF):
        raise SystemExit(f"Signature de reference manquante: {SIG_REF}")
    _iw, _ih = Image.open(SIG_REF).size
    s_h = sig_h
    s_w = s_h * _iw / _ih
    pdf.image(SIG_REF, x=zone_x + (zone_w - s_w) / 2, y=y, w=s_w)
    pdf.set_xy(zone_x, y + s_h + 1)
    pdf.set_font(font_name, font_style, font_size)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(zone_w, 6, nom, align="C", new_x="LMARGIN", new_y="NEXT")
    return y + s_h + 7
