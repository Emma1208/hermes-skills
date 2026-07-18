# -*- coding: utf-8 -*-
"""Génère le CV en PDF avec fpdf2 + police DejaVu (Unicode complet, puce ►).
Photo en haut à droite (coin à 16 mm). Titre + contenu commencent à 25 mm du haut.
La colonne de texte est rétrécie à droite tant qu'elle chevauche verticalement
la zone de la photo, pour éviter tout recouvrement."""
from fpdf import FPDF
import cv_data as D

FDIR = "/data/data/com.termux/files/usr/share/fonts/TTF"
NAVY = (31, 51, 100)
BLACK = (0, 0, 0)

MM = 2.834645669  # mm -> pt (informations internes)

class CVPDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("DJ", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Page {self.page_no()}/{{nb}}", align="C")

pdf = CVPDF(format="A4")
pdf.add_font("DJ", "", f"{FDIR}/DejaVuSans.ttf")
pdf.add_font("DJ", "B", f"{FDIR}/DejaVuSans-Bold.ttf")
pdf.add_font("DJ", "I", f"{FDIR}/DejaVuSans-Oblique.ttf")
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_margins(18, 16, 18)
pdf.add_page()
pdf.alias_nb_pages()

# ---- Photo en-tête (haut droite, coin à 16 mm) ----
PHOTO = "/root/cv_kakesa/photo_kakesa.jpg"
PIC_W, PIC_H = 34, 45.3
TOP_MM = 16
pic_x = pdf.w - pdf.r_margin - PIC_W
pic_y = TOP_MM
PHOTO_BOTTOM_MM = TOP_MM + PIC_H          # 61.3 mm
RIGHT_FULL = 18                            # marge droite normale (mm)
RIGHT_NARROW = RIGHT_FULL + PIC_W + 4      # laisse la place à la photo (mm)
try:
    pdf.image(PHOTO, x=pic_x, y=pic_y, w=PIC_W, h=PIC_H)
    pdf.set_draw_color(*NAVY)
    pdf.set_line_width(0.5)
    pdf.rect(pic_x, pic_y, PIC_W, PIC_H)
except Exception as e:
    print("Photo non intégrée:", e)

def content_margin():
    """Rétrécit la colonne de droite tant qu'on est dans la bande de la photo."""
    if pdf.get_y() < PHOTO_BOTTOM_MM:
        pdf.set_right_margin(RIGHT_NARROW)
    else:
        pdf.set_right_margin(RIGHT_FULL)

def section(title):
    content_margin()
    pdf.ln(2)
    pdf.set_font("DJ", "B", 12)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
    y = pdf.get_y()
    pdf.set_draw_color(*NAVY)
    pdf.set_line_width(0.4)
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
    pdf.ln(2)

def bullet(text, label=None):
    content_margin()
    pdf.set_font("DJ", "", 11)
    pdf.set_text_color(*NAVY)
    pdf.cell(7, 5.5, "►")
    pdf.set_text_color(*BLACK)
    if label:
        pdf.set_font("DJ", "B", 11)
        pdf.set_text_color(*NAVY)
        pdf.write(5.5, f" {label} : ")
        pdf.set_font("DJ", "", 11)
        pdf.set_text_color(*BLACK)
    else:
        pdf.set_font("DJ", "", 11)
    pdf.multi_cell(0, 5.5, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.5)

# ---- Titre : centré sur toute la page, à 25 mm du haut ----
pdf.set_right_margin(RIGHT_FULL)
pdf.set_y(25)
pdf.set_font("DJ", "B", 18)
pdf.set_text_color(*NAVY)
pdf.cell(0, 10, D.CV["titre"], align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)

section("I. INFORMATIONS PERSONNELLES")
for label, val in D.CV["infos_perso"]:
    bullet(val, label=label)

section("II. PARCOURS PROFESSIONNEL")
for item in D.CV["parcours"]:
    bullet(item)

section("III. DOMAINES DE COMPETENCE")
bullet(" ; ".join(D.CV["competences"]) + ".")

section("IV. ETUDES FAITES")
for item in D.CV["etudes"]:
    bullet(item)

section("V. FORMATIONS ACADÉMIQUE")
for item in D.CV["formations"]:
    bullet(item)

section("VI. LANGUES")
for langue, niveau in D.CV["langues"]:
    bullet(niveau, label=langue)

section("VIII. PERSONNES DE REFERENCE")
for nom, detail in D.CV["references"]:
    bullet(detail, label=nom + ".")

# ---- Signature (pleine largeur) ----
pdf.set_right_margin(RIGHT_FULL)
pdf.ln(8)
pdf.set_font("DJ", "I", 11)
pdf.set_text_color(*BLACK)
pdf.cell(0, 6, D.CV["signature"]["lieu_date"], align="R", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("DJ", "B", 11)
pdf.cell(0, 6, D.CV["signature"]["nom"], align="R", new_x="LMARGIN", new_y="NEXT")

OUT = "/root/cv_kakesa/CV_KAKESA_MUDIMBA.pdf"
pdf.output(OUT)
print("PDF généré:", OUT)
