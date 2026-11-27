#!/usr/bin/env python3
"""CV modele VIERGE editable LibreOffice (odt) - style identique a la reference
KAKESA MUDIMBA (bleu marine, sections numerotees). Champs a remplir en [crochets].

Usage: python3 generer_cv_modele_vierge.py [chemin_sortie.odt]
Prerequis: pip install odfpy
Sert a produire un modele qu'on OUVRE dans LibreOffice et qu'on REMPLIT
(contrairement au generateur fpdf2 qui produit un PDF fige/non editable).
"""
import sys
from odf.opendocument import OpenDocumentText
from odf.style import Style, ParagraphProperties, TextProperties
from odf.text import P, Span

NAVY = "#142850"
WHITE = "#FFFFFF"
DARK = "#1E1E1E"

out = sys.argv[1] if len(sys.argv) > 1 else "/root/Candidatures/Modèles/CV_modele_vierge.odt"

doc = OpenDocumentText()

# NOTE pitfall: page-width/page-height NE vont PAS sur doc.text -> omis.

def mk_para_style(name, color, fontsize, bold=False, bg=None):
    s = Style(name=name, family="paragraph")
    pp = dict(marginleft="0cm", marginright="0cm")
    if bg:
        pp["backgroundcolor"] = bg
        pp["padding"] = "0.15cm 0.3cm"
    s.addElement(ParagraphProperties(**pp))
    tp = dict(color=color, fontsize=fontsize, fontfamily="DejaVu Sans")
    if bold:
        tp["fontweight"] = "bold"
    s.addElement(TextProperties(**tp))
    doc.styles.addElement(s)
    return name

# NOTE pitfall: spacebefore/spaceafter NE sont PAS valides dans ParagraphProperties -> omis.
st_title = mk_para_style("CVTitle", WHITE, "18pt", bold=True, bg=NAVY)
st_sub   = mk_para_style("CVSub", WHITE, "11pt", bg=NAVY)
st_sec   = mk_para_style("CVSec", WHITE, "13pt", bold=True, bg=NAVY)
st_body  = mk_para_style("CVBody", DARK, "12pt")
st_ital  = mk_para_style("CVItal", DARK, "11pt")

def para(stylename, text, label=None):
    p = P(stylename=stylename)
    if label:
        ls = Span(); ls.addText(label); p.addElement(ls)
    t = Span(); t.addText(text); p.addElement(t)
    doc.text.addElement(p)

# HEADER
para(st_title, "Curriculum Vitæ")
para(st_sub, "[Métier 1] / [Métier 2] / [Métier 3] / [Métier 4]")

# I. INFOS PERSO
para(st_sec, "I. INFORMATIONS PERSONNELLES")
para(st_body, "  |  Poste nom : [POSTE NOM]  |  Prénom : [PRÉNOM]", label="Nom : ")
para(st_body, "  |  Né(e) à [VILLE] le [JJ/MM/AAAA]", label="Sexe : ")
para(st_body, "  |  Nationalité : [Nationalité]", label="État civil : ")
para(st_body, "[N°, Avenue, Quartier, Commune, Ville]", label="Adresse : ")
para(st_body, "[+243 ...]", label="Téléphone : ")
para(st_body, "[email@exemple.com]", label="E-mail : ")

# II. PARCOURS (ordre chronologique inverse, corrigé)
para(st_sec, "II. PARCOURS PROFESSIONNEL")
para(st_body, "[Depuis MMAAAA — Intitulé du poste, Nom de l'entreprise]")
para(st_body, "— [Description de la mission : actions clés, résultats, compétences utilisées.]")
para(st_body, "")
para(st_body, "[MMAAAA à MMAAAA — Intitulé du poste, Nom de l'entreprise]")
para(st_body, "— [Description de la mission.]")
para(st_body, "")
para(st_body, "[MMAAAA à MMAAAA — Intitulé du poste, Nom de l'entreprise]")
para(st_body, "— [Description de la mission.]")

# III. COMPETENCES
para(st_sec, "III. DOMAINES DE COMPÉTENCE")
para(st_body, "— [Compétence 1, ex : Comptabilité financière et analytique]")
para(st_body, "— [Compétence 2, ex : Audit et contrôle interne]")
para(st_body, "— [Compétence 3]")
para(st_body, "— [Compétence 4]")

# IV. ETUDES
para(st_sec, "IV. ÉTUDES FAITES")
para(st_body, "[AAAA-AAAA : Diplôme, Établissement]")
para(st_body, "[AAAA-AAAA : Diplôme, Établissement]")
para(st_body, "[AAAA-AAAA : Diplôme, Établissement]")

# V. FORMATIONS
para(st_sec, "V. FORMATIONS ACADÉMIQUES")
para(st_body, "— [Formation, ex : Comptabilité OHADA Révisée]")
para(st_body, "— [Formation, ex : Informatique (Word, Excel)]")

# VI. LANGUES
para(st_sec, "VI. LANGUES")
para(st_body, "— Français : [Courant / Moyen / Débutant]")
para(st_body, "— Anglais : [lu, écrit, parlé (niveau)]")
para(st_body, "— [Langue 3] : [Niveau]")

# VII. REFERENCES
para(st_sec, "VII. PERSONNES DE RÉFÉRENCE")
para(st_body, "1. [NOM Prénom]")
para(st_body, "    [Fonction, Organisation]")
para(st_body, "    Tél : [+243 ...]  |  E-mail : [email]")
para(st_body, "2. [NOM Prénom]")
para(st_body, "    [Fonction, Organisation]")
para(st_body, "    Tél : [+243 ...]  |  E-mail : [email]")

# SERMENT
para(st_ital, "Je jure sur mon honneur que les informations ci-dessus sont vraies et exactes.")
para(st_ital, "Fait à [Ville], le [JJ/MM/AAAA]")

doc.save(out)
print("Modele genere:", out)
