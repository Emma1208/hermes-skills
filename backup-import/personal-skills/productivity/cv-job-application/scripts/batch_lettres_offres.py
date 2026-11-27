#!/usr/bin/env python3
"""TEMPLATE — Batch motivation letters for multiple offers (KAKESA MUDIMBA).
Reusable: copy to your working dir (with modele_signature.py + DejaVuSerif*.ttf),
fill the OFFRES list, run. Each entry -> one 1-page official letter (100mm-block
layout) + living handwritten signature. The CV is generated separately as ONE master
CV reused for all offers (see generer_cv_master.py).

Usage:
  cp batch_lettres_offres.py /root/linkedin_app/
  # edit OFFRES below, then:
  python3 batch_lettres_offres.py
"""
import os
from datetime import date
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from modele_signature import inserer_signature   # ensure modele_signature.py is in working dir

LEFT = 25
RIGHT = 25
BLK = 100  # right column for destinataire / signature

EXPEDITEUR = [
    "KAKESA MUDIMBA DIEUDONNE",
    "N° 3, AV. TUNGILA, Q. BIANDA,",
    "C. MONT NGAFULA",
    "TEL : (+243) 818 491 601",
    "EMAIL : KAKESAMUDIMBA@GMAIL.COM",
]
DATE_LIEU = "KINSHASA, " + date.today().strftime("%d / %m / %Y")
FONT_DIR = "/root/linkedin_app"   # where DejaVuSerif*.ttf live
OUT_DIR = "/root/linkedin_app"

# ===== EDIT THIS LIST: one dict per offer =====
OFFRES = [
    dict(poste="Responsable Comptable (Grade B3)",
         structure="CICR — Comité International de la Croix-Rouge",
         loc="KINSHASA",
         url="https://...",
         corps=[
           "Par la présente, je vous soumets ma candidature au poste de ...",
           "Mon expérience (DRQC, MSF PUC MED) m'habilite à ce rôle.",
           "Je me tiens à votre disposition et vous prie de trouver ci-joint mon curriculum vitæ.",
         ]),
    # dict(poste="...", structure="...", loc="KINSHASA", url="...", corps=[...]),
]
# =============================================

def generer(o):
    pdf = FPDF(format="A4")
    pdf.add_font("SR", "", os.path.join(FONT_DIR, "DejaVuSerif.ttf"))
    pdf.add_font("SR", "B", os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf"))
    pdf.add_font("SR", "I", os.path.join(FONT_DIR, "DejaVuSerif-Italic.ttf"))
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.set_margins(LEFT, 25, RIGHT)
    pdf.add_page()

    def serif(size=11, style=""):
        pdf.set_font("SR", style, size)

    # expediteur (haut gauche)
    y = 25
    for line in EXPEDITEUR:
        pdf.set_xy(LEFT, y); serif(11, ""); pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 6, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT); y += 6
    # date (haut droite)
    pdf.set_xy(LEFT, 25); serif(11, "")
    pdf.cell(160, 6, DATE_LIEU, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    # objet (gauche, <=100mm)
    objet_y = y + 12
    pdf.set_xy(LEFT, objet_y); serif(11, "B"); pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(100, 6, "OBJET : CANDIDATURE AU POSTE DE " + o["poste"].upper(),
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    # destinataire (colonne droite 100mm)
    dest_y = objet_y + 11
    pdf.set_xy(BLK, dest_y); serif(11, "")
    pdf.multi_cell(85, 5, "A MONSIEUR LE DIRECTEUR\nDES RESSOURCES HUMAINES\nDE " + o["structure"].upper(),
                   new_x=XPos.RIGHT, new_y=YPos.NEXT, align="L", max_line_height=5)
    dy = pdf.get_y() + 1
    pdf.set_xy(BLK, dy)
    w = pdf.get_string_width(o["loc"])
    pdf.cell(w, 6, o["loc"], new_x=XPos.LMARGIN, new_y=YPos.TOP)
    y2 = pdf.get_y()
    pdf.set_draw_color(0, 0, 0); pdf.set_line_width(0.3)
    pdf.line(BLK, y2 + 6 + 1.5, BLK + w, y2 + 6 + 1.5)
    # formule d'appel
    formule_y = dy + 13
    pdf.set_xy(BLK, formule_y); serif(11, "")
    pdf.cell(0, 6, "Monsieur le Directeur,", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    # corps (justifie, pleine largeur)
    cy = formule_y + 9
    for p in o["corps"]:
        pdf.set_xy(LEFT, cy); serif(11, ""); pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(160, 5, p, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="J")
        cy = pdf.get_y() + 2
    # politesse
    pol_y = cy + 1
    pdf.set_xy(BLK, pol_y); serif(11, "")
    pdf.cell(0, 6, "Veuillez agréer, Monsieur le Directeur,", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_xy(LEFT, pdf.get_y() + 1)
    pdf.cell(0, 6, "l'assurance de ma considération distinguée.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    # signature vivante (droite)
    sig_y = pdf.get_y() + 8
    inserer_signature(pdf, BLK, sig_y, zone_w=75, font_name="SR", font_size=11, font_style="B")
    # nom de fichier
    slug = (o["structure"].split(" ")[0] + "_" + o["poste"].split(" ")[0]).replace("/", "-")
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in slug)
    out = os.path.join(OUT_DIR, f"Lettre_{safe}.pdf")
    pdf.output(out)
    return out

if __name__ == "__main__":
    for o in OFFRES:
        print("Genere:", generer(o))
