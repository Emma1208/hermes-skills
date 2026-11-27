#!/usr/bin/env python3
"""Proven fpdf2 CV generator. Key fixes baked in:
- latin-1 sanitize (curly quotes/dashes) before any text
- Helvetica font (Arial -> deprecation warning)
- XPos/YPos enums instead of ln=
- set_x(l_margin) before every multi_cell to avoid 'Not enough horizontal space'
Copy, then fill the content blocks for the user's CV."""
from fpdf import FPDF
from fpdf.enums import XPos, YPos

def clean(t):
    return (t.replace("\u2019", "'").replace("\u2013", "-").replace("\u2014", "-")
             .replace("\u201c", '"').replace("\u201d", '"').replace("\u2022", "-")
             .encode("latin-1", "replace").decode("latin-1"))

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=18)
pdf.add_page()
LM = pdf.l_margin

def mc(w, h, txt, font=("Helvetica", "", 9.5), color=(30, 30, 30)):
    pdf.set_x(LM)
    pdf.set_font(*font)
    pdf.set_text_color(*color)
    pdf.multi_cell(w, h, clean(txt), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

def section(title):
    pdf.set_x(LM)
    pdf.set_fill_color(20, 40, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "  " + clean(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
    pdf.ln(1)

# --- build content with mc()/section()/pdf.cell() calls ---
# header band:
pdf.set_fill_color(20, 40, 80)
pdf.rect(0, 0, 210, 26, "F")
pdf.set_xy(12, 6)
pdf.set_text_color(255, 255, 255)
pdf.set_font("Helvetica", "B", 16)
pdf.cell(0, 8, "NOM PRENOM", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_x(12)
pdf.set_font("Helvetica", "", 10)
pdf.cell(0, 6, "Titre du poste vise", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(10)

section("EXPERIENCE PROFESSIONNELLE")
mc(0, 5, "Poste", font=("Helvetica", "B", 10), color=(20, 40, 80))
mc(0, 4.5, "Employeur | Dates", font=("Helvetica", "I", 9), color=(90, 90, 90))
mc(0, 4.8, "- Mission clé")
pdf.ln(1.5)

pdf.output("/root/linkedin_app/CV_genere.pdf")
print("OK")
