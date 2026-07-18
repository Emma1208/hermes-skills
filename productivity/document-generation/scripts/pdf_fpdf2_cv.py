# -*- coding: utf-8 -*-
"""fpdf2 CV PDF generator with DejaVu Unicode font.
Use when reportlab fails (Pillow broken on Termux/ARM) and you need Unicode.

pip install fpdf2
Find DejaVu:  Termux -> /data/data/com.termux/files/usr/share/fonts/TTF/
              desktop -> fc-list | grep DejaVu  (or /usr/share/fonts/truetype/dejavu/)

NOTE: arrow char U+2BAC (⮚) is absent from DejaVu and most system fonts.
      Substitute U+25BA (►) for the bullet, OR register a font that has it.

Run: python3 pdf_fpdf2_cv.py
"""
from fpdf import FPDF

FDIR = "/data/data/com.termux/files/usr/share/fonts/TTF"   # EDIT for desktop
NAVY = (31, 51, 100)
BLACK = (0, 0, 0)

# data source would be imported here; inline example:
DATA = {
    "titre": "CURRICULUM VITAE",
    "infos": [("Nom", "KAKESA"), ("Poste nom", "MUDIMBA")],
    "refs": [("NOM", "+243 ...")],
    "signature": ("Fait a Kinshasa, le 01 Juin 2026", "KAKESA MUDIMBA Emmanuel-Dieudonne"),
}


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


def section(title):
    pdf.ln(2)
    pdf.set_font("DJ", "B", 12)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
    y = pdf.get_y()
    pdf.set_draw_color(*NAVY)
    pdf.set_line_width(0.4)
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
    pdf.ln(2)


def bullet(text, label=None, bullet_glyph="►"):
    pdf.set_font("DJ", "", 11)
    pdf.set_text_color(*NAVY)
    pdf.cell(7, 5.5, bullet_glyph)         # regular face (bold may miss glyph)
    pdf.set_text_color(*BLACK)
    if label:
        pdf.set_font("DJ", "B", 11)
        pdf.set_text_color(*NAVY)
        pdf.write(5.5, f" {label} : ")
        pdf.set_font("DJ", "", 11)
        pdf.set_text_color(*BLACK)
    pdf.multi_cell(0, 5.5, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.5)


pdf.ln(2)
pdf.set_font("DJ", "B", 18)
pdf.set_text_color(*NAVY)
pdf.cell(0, 10, DATA["titre"], align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)

section("I. INFORMATIONS PERSONNELLES")
for label, val in DATA["infos"]:
    bullet(val, label=label)

section("VIII. PERSONNES DE REFERENCE")
for nom, detail in DATA["refs"]:
    bullet(detail, label=nom + ".")

pdf.ln(8)
pdf.set_font("DJ", "I", 11)
pdf.set_text_color(*BLACK)
pdf.cell(0, 6, DATA["signature"][0], align="R", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("DJ", "B", 11)
pdf.cell(0, 6, DATA["signature"][1], align="R", new_x="LMARGIN", new_y="NEXT")

pdf.output("CV_KAKESA_MUDIMBA.pdf")
print("PDF généré")
