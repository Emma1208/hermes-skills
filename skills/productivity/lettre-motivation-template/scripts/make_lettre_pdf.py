# -*- coding: utf-8 -*-
"""Génère une LETTRE DE MOTIVATION en PDF (fpdf2 + DejaVu, Unicode).
Identité visuelle du CV (palette navy).
Mise en page :
  - LIGNE 1 : Expéditeur (nom) à GAUCHE  |  Date à DROITE (même ligne).
  - Sous le nom : adresse, tél, email (gauche).
  - DESTINATAIRE : EN-DESSOUS de l'expéditeur, aligné à DROITE.
  - Objet, puis FORMULE D'APPEL (salutation), puis CORPS, formule de
    politesse, signature.
"""
from fpdf import FPDF
import lettre_data as L

FDIR = "/data/data/com.termux/files/usr/share/fonts/TTF"
NAVY = (31, 51, 100)
BLACK = (0, 0, 0)
MARGIN = 18

class LPDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("DJ", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Page {self.page_no()}/{{nb}}", align="C")

pdf = LPDF(format="A4")
pdf.add_font("DJ", "", f"{FDIR}/DejaVuSans.ttf")
pdf.add_font("DJ", "B", f"{FDIR}/DejaVuSans-Bold.ttf")
pdf.set_auto_page_break(auto=True, margin=18)
pdf.set_margins(MARGIN, 18, MARGIN)
pdf.add_page()
pdf.alias_nb_pages()

e = L.LETTRE["expediteur"]
d = L.LETTRE["destinataire"]

# ---------- LIGNE 1 : nom expéditeur (gauche) + date (droite) ----------
y0 = 18
pdf.set_xy(MARGIN, y0)
pdf.set_font("DJ", "B", 11)
pdf.set_text_color(*NAVY)
pdf.cell(95, 5.5, e["nom"], new_x="LMARGIN", new_y="TOP")

pdf.set_xy(pdf.w - MARGIN - 80, y0)
pdf.set_font("DJ", "", 10)
pdf.set_text_color(*BLACK)
pdf.cell(80, 5.5, L.LETTRE["date_lieu"], align="R", new_x="LMARGIN", new_y="NEXT")

# ---------- Sous le nom : adresse, tél, email (gauche) ----------
pdf.set_xy(MARGIN, y0 + 6)
pdf.set_font("DJ", "", 10)
pdf.multi_cell(95, 5, e["adresse"], new_x="LMARGIN", new_y="NEXT")
pdf.multi_cell(95, 5, e["tel"], new_x="LMARGIN", new_y="NEXT")
pdf.multi_cell(95, 5, e["email"], new_x="LMARGIN", new_y="NEXT")
exp_bottom = pdf.get_y()

# ---------- Destinataire : EN-DESSOUS de l'expéditeur, à DROITE, aligné à GAUCHE ----------
pdf.set_xy(pdf.w - MARGIN - 80, exp_bottom + 4)
pdf.set_font("DJ", "", 10)
pdf.multi_cell(80, 5, d["ligne1"], align="L", new_x="LMARGIN", new_y="NEXT")
pdf.set_x(pdf.w - MARGIN - 80)
pdf.multi_cell(80, 5, d["ligne2"], align="L", new_x="LMARGIN", new_y="NEXT")
pdf.set_x(pdf.w - MARGIN - 80)
pdf.multi_cell(80, 5, d["ligne3"], align="L", new_x="LMARGIN", new_y="NEXT")

# ---------- Photo (optionnelle, coin haut-droite) ----------
ph = L.LETTRE["photo"]
if ph:
    PW, PH_ = 28, 37.3
    px = pdf.w - MARGIN - PW
    py = 18
    try:
        pdf.image(ph, x=px, y=py, w=PW, h=PH_)
    except Exception:
        pass

# ---------- Saut avant corps ----------
pdf.set_y(max(pdf.get_y(), exp_bottom + 4 + 22))
pdf.ln(10)

# ---------- Concerne (multi_cell largeur = bloc expéditeur 95mm, retour auto) ----------
pdf.set_font("DJ", "B", 11)
pdf.set_text_color(*NAVY)
pdf.multi_cell(95, 6, "Concerne : " + L.LETTRE["objet"], new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(*BLACK)
pdf.ln(4)

# ---------- Formule d'appel (au-dessus du corps, sous l'Objet) ----------
pdf.set_font("DJ", "", 11)
pdf.cell(0, 6, L.LETTRE["salutation"], new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)

# ---------- Corps ----------
pdf.set_font("DJ", "", 11)
for para in L.LETTRE["corps"]:
    pdf.multi_cell(0, 5.5, para, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

# ---------- Formule de politesse ----------
pdf.ln(2)
pdf.set_font("DJ", "", 11)
for line in L.LETTRE["formule"]:
    pdf.cell(0, 5.5, line, new_x="LMARGIN", new_y="NEXT")

# ---------- Signature (tout le nom à droite) ----------
pdf.ln(10)
sig_img = L.LETTRE["signature_image"]
if sig_img:
    try:
        pdf.image(sig_img, x=pdf.l_margin, y=pdf.get_y(), w=45)
        pdf.ln(18)
    except Exception:
        pass
pdf.set_font("DJ", "B", 11)
pdf.set_text_color(*NAVY)
pdf.cell(0, 6, L.LETTRE["signature_nom"], align="R", new_x="LMARGIN", new_y="NEXT")

OUT = "/root/lettre_motivation/LETTRE_MOTIVATION.pdf"
pdf.output(OUT)
print("PDF généré:", OUT)
