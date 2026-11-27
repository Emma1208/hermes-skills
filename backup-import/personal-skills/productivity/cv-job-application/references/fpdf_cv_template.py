#!/usr/bin/env python3
"""TEMPLATE: French CV PDF with fpdf2 + DejaVu Unicode font.

Copy this and adapt the content. Hard rules from the user (Do NOT violate):
  * Keep accents (never strip é/è/à/ç — use the embedded Unicode font).
  * No "généré automatiquement" footer.
  * Keyword styling = BLACK, no bold (kw_bold=False, kw_color=DARK). The user
    first had them blue, then OVERRODE it. Only DATES stay bold+navy.
  * Body text size 13 minimum.
  * Structured label/value blocks for contact info AND references (same layout).
  * Header text = "Curriculum Vitæ" (NOT the name).
  * Section III title = "DOMAINES DE COMPÉTENCE À ÉVOLUER".
  * File naming (FINAL): general reference = CV_KAKESA_MUDIMBA.pdf (NO "Emmanuel");
    targeted CVs append the post: CV_KAKESA_MUDIMBA_Comptable.pdf, _HYGroup.pdf, etc.
  * This general CV is the LIVING reference — update it as experience grows, and
    derive targeted CVs FROM it (don't build them from scratch).

Requires DejaVuSans*.ttf in the working dir. On this host copy from:
  /data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans.ttf (and -Bold, -Oblique)
"""
import re
from fpdf import FPDF
from fpdf.enums import XPos, YPos

pdf = FPDF()
pdf.add_font("DJ", "", "/root/linkedin_app/DejaVuSans.ttf")
pdf.add_font("DJ", "B", "/root/linkedin_app/DejaVuSans-Bold.ttf")
pdf.add_font("DJ", "I", "/root/linkedin_app/DejaVuSans-Oblique.ttf")
pdf.set_auto_page_break(auto=True, margin=16)
pdf.add_page()

NAVY = (20, 40, 80)
GREY = (90, 90, 90)
DARK = (30, 30, 30)

KEYWORDS = {
    "comptabilité", "comptable", "financière", "financier", "finance", "audit",
    "contrôle", "gestion", "fiscalité", "ohada", "excel", "pack office",
    "enregistrement", "archivage", "rapports", "vérification", "pièces",
    "analyse", "analyse financière", "logistique", "stock", "reporting",
    "enseignement", "pédagogie", "risques", "décision",
}

def clean_w(w):
    return w.strip(".,;:()").lower()

def para(text, size=13, lh=6, keywords=None, bold_dates=True, x_indent=0,
         kw_bold=False, kw_color=DARK):
    """Enriched per-word renderer. dates: bold+navy (ONLY bold element);
    keywords: black, no bold by default (text NEVER altered)."""
    kw = keywords if keywords is not None else KEYWORDS
    x0 = pdf.l_margin + x_indent
    maxw = pdf.w - pdf.l_margin - pdf.r_margin - x_indent
    words = text.split()
    line = []
    def linewidth(wds):
        w = 0
        for wd in wds:
            pdf.set_font("DJ", style_of(wd), size)
            w += pdf.get_string_width(wd + " ")
        return w
    def style_of(wd):
        cw = clean_w(wd)
        is_kw = cw in kw
        is_date = bold_dates and (re.match(r'^\d{4}', wd) or
                  re.match(r'^(janvier|février|mars|avril|mai|juin|juillet|août|'
                           r'septembre|octobre|novembre|décembre)', wd, re.I) or
                  re.match(r'^(de|du|depuis|a|à|au|ce)', wd, re.I) and re.search(r'\d', wd))
        if is_kw:
            return "B" if kw_bold else ""
        if is_date:
            return "B"
        return ""
    def flush():
        pdf.set_x(x0)
        for wd in line:
            is_kw = clean_w(wd) in kw
            is_date = style_of(wd) == "B" and not is_kw
            style = "B" if (is_kw or is_date) else ""
            color = kw_color if is_kw else (NAVY if is_date else DARK)
            pdf.set_font("DJ", style, size)
            pdf.set_text_color(*color)
            pdf.cell(pdf.get_string_width(wd + " "), lh, wd + " ",
                     new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.ln(lh)
    for wd in words:
        trial = line + [wd]
        if linewidth(trial) > maxw and line:
            flush()
            line = [wd]
        else:
            line.append(wd)
    if line:
        flush()

def section(title):
    pdf.ln(1)
    pdf.set_x(pdf.l_margin)
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("DJ", "B", 13)
    pdf.cell(0, 8, "  " + title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L", fill=True)
    pdf.ln(1)

def bullet(text, size=13, lh=6):
    pdf.set_x(pdf.l_margin)
    pdf.set_font("DJ", "B", size); pdf.set_text_color(*NAVY)
    pdf.cell(6, lh, "—", new_x=XPos.RIGHT, new_y=YPos.TOP)
    para(text, size=size, lh=lh, x_indent=6)

def job_title(title):
    pdf.set_x(pdf.l_margin)
    pdf.set_font("DJ", "B", 13); pdf.set_text_color(*NAVY)
    pdf.multi_cell(0, 6, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    y = pdf.get_y()
    pdf.set_draw_color(*NAVY); pdf.set_line_width(0.4)
    pdf.line(pdf.l_margin, y, pdf.l_margin + 70, y)  # drawn underline (set_underline() missing)
    pdf.ln(1)

def field(label, value, multi=False):
    """Structured label/value block (blue-bold label, black value)."""
    pdf.set_font("DJ", "B", 13); pdf.set_text_color(*NAVY); pdf.set_x(pdf.l_margin)
    pdf.cell(45, 6, label, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font("DJ", "", 13); pdf.set_text_color(*DARK)
    if multi:
        pdf.multi_cell(0, 6, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.cell(0, 6, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

def ref(num, nom, role, contact):
    """Structured reference entry: navy num, bold name, black role, grey contact."""
    pdf.set_font("DJ", "B", 13); pdf.set_text_color(*NAVY); pdf.set_x(pdf.l_margin)
    pdf.cell(12, 6, num, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font("DJ", "B", 13); pdf.set_text_color(*DARK)
    pdf.multi_cell(0, 6, nom, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(pdf.l_margin + 12)
    pdf.set_font("DJ", "", 13); pdf.set_text_color(*DARK)
    pdf.multi_cell(0, 6, role, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(pdf.l_margin + 12)
    pdf.set_font("DJ", "", 13); pdf.set_text_color(*GREY)
    pdf.multi_cell(0, 6, contact, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)

# ---- Header (navy band, white text; NO footer) ----
pdf.set_fill_color(*NAVY)
pdf.rect(0, 0, 210, 28, "F")
pdf.set_xy(12, 8)
pdf.set_text_color(255, 255, 255)
pdf.set_font("DJ", "B", 17)
pdf.cell(0, 8, "Curriculum Vitæ", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_x(12); pdf.set_font("DJ", "", 11)
pdf.cell(0, 6, "Comptable / Gestion Financière / Audit / Enseignant",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(10)

# ---- I. Infos perso (structured) ----
section("I. INFORMATIONS PERSONNELLES")
field("Nom :", "KAKESA  |  Poste nom : MUDIMBA  |  Prénom : Dieudonné")
field("Sexe :", "Masculin  |  Né(e) à ITURI (BUNIA) le 12/08/1998")
field("État civil :", "Célibataire  |  Nationalité : Congolaise")
field("Adresse :", "N° 3, Avenue Tungila, Q/Bianda, C/Mont Ngafula, Kinshasa", multi=True)
field("Téléphone :", "(+243) 818 491 601", multi=True)
field("E-mail :", "kakesamudimba@gmail.com", multi=True)
pdf.ln(1)

# ---- II. Parcours ----
section("II. PARCOURS PROFESSIONNEL")
job_title("2024 à ce jour — Professeur des Comptabilités et cours à caractère commercial "
           "et délégué des professeurs au Complexe scolaire Sagesse 2.")
para("Enseignement de la comptabilité, des mathématiques et de la gestion ; encadrement "
      "à domicile en comptabilité et fiscalité ; délégué des professeurs : organisation "
      "et reporting.", keywords=set())  # detail after ";" forced black via empty kw set
pdf.ln(1)
job_title("Juillet 2025 — Agent de prospection, MARS SARL (mission de 2 semaines)")
para("Collecte de données d'entreprises, PME, écoles, ONG ; prospection terrain ; "
      "présentation des services ; identification des besoins.")
pdf.ln(1)
job_title("De 2019 à 2023 — Analyse des marchés financiers (Forex)")
para("Analyse technique et prise de décision en environnement incertain ; discipline et "
      "gestion du risque.")
pdf.ln(1)
job_title("Depuis novembre 2023 — Agent d'appui logistique au projet PUC MED de "
           "Médecins Sans Frontières")
para("Suivi de stock, gestion de la chaîne du froid, sécurité des locaux, reporting logistique.")
pdf.ln(1)
job_title("Août 2022 à février 2023 — Stage professionnel à la Direction de Réglementation "
           "et Qualité Comptable (DRQC) du Ministère des Finances")
para("Gestion et enregistrement des courriers entrants/sortants ; vérification des pièces "
      "comptables ; collaboration à l'archivage et à la préparation de rapports financiers.")
pdf.ln(1)

# ---- III. Compétences ----
section("III. DOMAINES DE COMPÉTENCE À ÉVOLUER")
for c in ["Analyse financière et prise de décision", "Audit, contrôle interne et gestion des risques",
          "Comptabilité financière et analytique", "Fiscalité et gestion d'entreprise",
          "Analyse de données et interprétation économique", "Pédagogie et transmission structurée",
          "Logistique et gestion opérationnelle"]:
    bullet(c)
pdf.ln(1)

# ---- IV. Études ----
section("IV. ÉTUDES FAITES")
para("2021-2022 : Licencié en Sciences économiques et de gestion, Option Gestion Financière "
      "à l'Université de Kinshasa")
para("2018-2020 : Gradué en science économique générale")
para("2012-2017 : Diplôme d'État en Littéraire au Collège Sainte Rita")
para("2004-2009 : Certificat d'études primaires à l'E.P 4 Présidence")
pdf.ln(1)

# ---- V. Formations ----
section("V. FORMATIONS ACADÉMIQUES")
bullet("Formation en comptabilité OHADA Révisée")
bullet("Formation en informatique (logiciels Word et Excel)")
pdf.ln(1)

# ---- VI. Langues ----
section("VI. LANGUES")
bullet("Français : Courant")
bullet("Anglais : lu, écrit, parlé (niveau moyen)")
bullet("Lingala : Bilingue")
pdf.ln(1)

# ---- VIII. Références (structured like contact block) ----
section("VIII. PERSONNES DE RÉFÉRENCE")
ref("1.", "MUTAMBWE TSHAMU Patrick",
    "Directeur des Ressources Humaines, MSF Belgique", "Tél : +243 824 983 499")
ref("2.", "TEDDY PULUMBA",
    "Encadrant, Chef de pool — Direction de Préparation de Réglementation Financière et Comptable",
    "E-mail : teddypulumba@gmail.com  |  Tél : +243 823 577 917")
ref("3.", "MFUNI INABANZA Ange",
    "Chef de bureau — Division de normalisation et Management comptable",
    "E-mail : angemiamas@gmail.com  |  Tél : +243 816 147 052")
ref("4.", "OMARI BATUKWA",
    "Pharmacien et logisticien, Médecins Sans Frontières",
    "E-mail : omaribatukwa@gmail.com  |  Tél : +243 814 363 400")
ref("5.", "DJIMY MAKENGO",
    "Directeur de discipline, Complexe scolaire Sagesse", "Tél : +243 821 994 204")
ref("6.", "MBELENGE Minga",
    "Promoteur et Préfet des études, Complexe scolaire Minga la Paix", "Tél : +243 820 073 629")

# File naming (FINAL convention): general reference = CV_KAKESA_MUDIMBA.pdf (NO "Emmanuel").
# Targeted CVs append the post: CV_KAKESA_MUDIMBA_Comptable.pdf, _HYGroup.pdf, etc.
pdf.output("/root/linkedin_app/CV_KAKESA_MUDIMBA.pdf")
print("PDF genere: CV_KAKESA_MUDIMBA.pdf")
