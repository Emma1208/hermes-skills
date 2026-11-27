#!/usr/bin/env python3
"""REFERENCE cover-letter generator — FINAL layout (reproduces Serge Mbulu sample).
FINAL (user instruction "suis l'entièreté de cette lettre" 2026-07-13):
EVERYTHING LEFT-aligned EXCEPT the DATE which is RIGHT-aligned at the right margin.
The earlier 100mm-right-block spec (destinataire/formule/signature at x=100mm) was
an INTERMEDIATE state the user OVERRIDED — do not reproduce it.

Serif (DejaVuSerif) 11pt, margins 25mm. Copy DejaVuSerif*.ttf into working dir first.
Branched per offer: generer_lettre_<OFFER>.py -> fill [POSTE]/[ORG]/[COMMUNE]/[Titre].
"""
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import date

LEFT, RIGHT, TOP, BOT = 25, 25, 25, 25
MAXW = 100  # aucun bloc entete ne depasse le milieu de la page (sinon collision date)

pdf = FPDF(format="A4")
pdf.add_font("SR", "", "/root/linkedin_app/DejaVuSerif.ttf")
pdf.add_font("SR", "B", "/root/linkedin_app/DejaVuSerif-Bold.ttf")
pdf.add_font("SR", "I", "/root/linkedin_app/DejaVuSerif-Italic.ttf")
pdf.set_auto_page_break(auto=True, margin=BOT)
pdf.set_margins(LEFT, TOP, RIGHT)
pdf.add_page()

def set_serif(size=11, style=""):
    pdf.set_font("SR", style, size)

# ---------- EXPEDITEUR (haut gauche, MAJUSCULES, <=100mm) ----------
exp = [
    "KAKESA MUDIMBA DIEUDONNE",
    "N° 3, AV. TUNGILA, Q. BIANDA, C. MONT NGAFULA",
    "TEL : (+243) 818 491 601",
    "EMAIL : KAKESAMUDIMBA@GMAIL.COM",
]
y = 25
set_serif(11, "")
for line in exp:
    pdf.set_xy(LEFT, y)
    pdf.set_text_color(0, 0, 0)
    if pdf.get_string_width(line) > MAXW:
        words = line.split(); l1 = ""
        for wd in words:
            trial = l1 + (" " if l1 else "") + wd
            if pdf.get_string_width(trial) > MAXW:
                break
            l1 = trial
        reste = line[len(l1):].strip()
        pdf.cell(0, 6, l1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        y = pdf.get_y(); pdf.set_xy(LEFT, y)
        pdf.cell(0, 6, reste, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        y = pdf.get_y()
    else:
        pdf.cell(0, 6, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        y += 6

# ---------- DATE (haut droite, ALIGNEE A DROITE marge droite) ----------
pdf.set_xy(LEFT, 25)
set_serif(11, "")
pdf.cell(160, 6, "KINSHASA, " + date.today().strftime("%d / %m / %Y"), align="R",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# ---------- OBJET (gauche, 25mm sous expediteur, Title case) ----------
objet_y = 25 + len(exp)*6 + 25 - 6
pdf.set_xy(LEFT, objet_y)
set_serif(11, "")
pdf.set_text_color(0, 0, 0)
pdf.cell(0, 6, "Objet : Candidature au poste de [POSTE]", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# ---------- DESTINATAIRE (gauche, une ligne style Serge) ----------
dest_y = pdf.get_y() + 2
pdf.set_xy(LEFT, dest_y)
set_serif(11, "")
pdf.cell(0, 6, "A Monsieur le Directeur des Ressources Humaines de [ORG]",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
dy = pdf.get_y()
pdf.set_xy(LEFT, dy)
loc = "KINSHASA / [COMMUNE]"
w = pdf.get_string_width(loc)
pdf.cell(w, 6, loc, new_x=XPos.LMARGIN, new_y=YPos.TOP)
y2 = pdf.get_y()
pdf.set_draw_color(0, 0, 0); pdf.set_line_width(0.3)
pdf.line(LEFT, y2 + 6 + 1.5, LEFT + w, y2 + 6 + 1.5)  # souligne SOUS le texte

# ---------- FORMULE D'APPEL (gauche, ~42mm sous objet) ----------
formule_y = objet_y + 30 + 12
pdf.set_xy(LEFT, formule_y)
set_serif(11, "")
pdf.cell(0, 6, "Monsieur le Directeur,", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# ---------- CORPS (pleine largeur justifiee pour tenir 1 page) ----------
corps = [
    "Par la presente, je vous soumets ma candidature au poste ci-haut emmarge. "
    "En effet, je detiens une licence en Sciences Economiques et de Gestion, option "
    "Gestion Financiere de l'Universite de Kinshasa. Je suis particulierement interesse "
    "par les domaines de la Finance, de la Comptabilite et de l'Audit qui sont des "
    "instruments majeurs de bonne gestion.",
    "J'ai deja eu l'opportunite de me familiariser avec les principes de la Comptabilite, "
    "du Controle interne et de l'Audit grace a mes etudes et a mon stage a la Direction "
    "de Reglementation et Qualite Comptable (DRQC) du Ministere des Finances, ou j'ai "
    "assure la verification des pieces comptables et la production de rapports financiers. "
    "Par ailleurs, en tant qu'Agent d'appui logistique au projet PUC MED de Medecins Sans "
    "Frontieres, j'ai gere le suivi de stock, la chaine du froid et le reporting logistique.",
    "Je suis persuade que mes competences et ma conscience professionnelles me permettront "
    "de reussir dans ce role. Je souhaiterais vivement integrer votre structure et contribuer "
    "a l'atteinte de ses objectifs. Etant un travailleur acharne, determine et capable de "
    "travailler en equipe, je peux offrir une contribution significative a votre organisation.",
    "Je vous remercie de prendre en consideration ma candidature et je me tiens a votre "
    "disposition pour tout renseignement complementaire. Veuillez trouver ci-joint mon "
    "curriculum vitae pour des amples informations.",
]
cy = formule_y + 8
for p in corps:
    pdf.set_xy(LEFT, cy)
    set_serif(11, ""); pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(170, 4.6, p, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="J")
    cy = pdf.get_y() + 1.5

# ---------- POLITESSE FINALE (gauche) ----------
pol_y = cy + 2
pdf.set_xy(LEFT, pol_y)
set_serif(11, "")
pdf.cell(0, 6, "Veuillez agreer, Monsieur le [Titre],", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_x(LEFT)
pdf.cell(0, 6, "l'assurance de ma consideration distinguee.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# ---------- SIGNATURE (gauche, MAJUSCULES) ----------
sig_y = pdf.get_y() + 6
pdf.set_xy(LEFT, sig_y)
set_serif(11, "B")
pdf.cell(0, 6, "KAKESA MUDIMBA DIEUDONNE", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

pdf.output("/root/linkedin_app/Lettre_Motivation_Generale.pdf")
print("PDF genere: /root/linkedin_app/Lettre_Motivation_Generale.pdf")
