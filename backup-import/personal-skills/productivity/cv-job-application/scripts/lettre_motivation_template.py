#!/usr/bin/env python3
"""TEMPLATE DE LETTRE DE MOTIVATION (mise en page + style VALIDÉS par KAKESA).
Dérivé de /root/linkedin_app/generer_lettre_kpmg.py (lettre KPMG approuvée 2026-07-17).

Reproduit EXACTEMENT la mise en page et le style validés :
  - expéditeur GAUCHE, date DROITE (tableau sans bordure 60/40)
  - destinataire EN DESSOUS à droite
  - objet en gras navy
  - corps justifié
  - formule de politesse + signature image (reference vivante) à droite + nom tapé

POUR RÉUTILISER : éditer le bloc CONFIG (expéditeur, destinataire, objet, corps)
et lancer :  python3 lettre_motivation_template.py
Sortie : ODT éditable + PDF converti.

ATTENTION (pitfall environnement) : soffice PERD l'image de signature en
conversion ODT->PDF ici. Pour une lettre avec signature image garantie dans le
PDF, utiliser la variante fpdf2 (voir references/lettre_kpmg_validee.md).
"""
from odf.opendocument import OpenDocumentText
from odf.style import (Style, ParagraphProperties, TextProperties,
                       PageLayout, PageLayoutProperties, MasterPage,
                       TableProperties, TableCellProperties, TableColumnProperties)
from odf.text import P
from odf.draw import Frame, Image as ODImage
from odf.table import Table, TableRow, TableCell, TableColumn
from datetime import date

# ====================== CONFIG (éditer ici) ======================
EXP_NOM = "KAKESA MUDIMBA Dieudonné"
EXP_ADR = "N° 3, Avenue Tungila, Q/Bianda, C/Mont Ngafula, Kinshasa"
EXP_TEL = "Tél : (+243) 818 491 601  |  E-mail : kakesamudimba@gmail.com"

DEST_1 = "À l'attention de la Direction des Ressources Humaines"
DEST_2 = "Orange RDC — Service de Recrutement"
DEST_3 = "recrutement.ordc@orange.com"

OBJET = "Objet : Candidature au poste de Chef de Département Data Factory & IA — Orange RDC"

CORPS = [
    "Madame, Monsieur,",
    "C'est avec un vif intérêt que je vous adresse ma candidature pour le poste de "
    "Chef de Département Data Factory & IA au sein d'Orange RDC. La donnée est "
    "aujourd'hui le carburant de la transformation digitale : or la comptabilité, la "
    "finance et l'audit en sont, au fond, la gestion, la qualité et la valorisation. "
    "J'ai donc une lecture concrète et opérationnelle de la donnée, que je souhaite "
    "mettre au service de vos équipes.",
    "Mon parcours m'a amené à piloter, contrôler et restituer des flux d'informations "
    "fiables : vérification des pièces comptables et reporting financier à la Direction "
    "de Réglementation et Qualité Comptable (DRQC) du Ministère des Finances, suivi et "
    "contrôle logistique chez Médecins Sans Frontières (projet PUC MED), et analyse de "
    "données de marché (Forex) orientée décision. Cette maîtrise de la donnée, doublée "
    "d'une culture de la gouvernance et de la conformité (OHADA, IFRS), constitue un "
    "socle solide pour diriger une Data Factory.",
    "À ce socle s'ajoutent des aptitudes de direction : délégué des professeurs et "
    "encadrant, je sais structurer, planifier et faire monter les compétences d'une "
    "équipe. Rigoureux, analytique et à l'aise avec les outils informatiques (Excel, "
    "Word), je parle couramment le français, l'anglais (en progression) et le lingala, "
    "autant d'atouts pour animer une fonction data au cœur d'Orange RDC.",
    "Animé par la volonté de contribuer à l'accélération de la transformation digitale "
    "de votre entreprise, je me tiens à votre entière disposition pour un entretien.",
]

POLITESSE = "Veillez agréer, Madame, Monsieur, l'expression de mes salutations distinguées."

OUT_ODT = "/root/Candidatures/Modèles/Lettre_Modele_KAKESA.odt"
SIGNATURE_IMG = "/root/Candidatures/Modèles/signature_seule.png"
# ================================================================

doc = OpenDocumentText()

pl = PageLayout(name="PL_Lettre")
plp = PageLayoutProperties()
plp.setAttribute("marginleft", "1.6cm")
plp.setAttribute("marginright", "1.6cm")
plp.setAttribute("margintop", "1.4cm")
plp.setAttribute("marginbottom", "1.4cm")
pl.addElement(plp)
doc.automaticstyles.addElement(pl)
mp = MasterPage(name="Standard", pagelayoutname="PL_Lettre")
doc.masterstyles.addElement(mp)

NAVY = "1F3350"

def style(name, **kw):
    s = Style(name=name, family="paragraph")
    if "parent" in kw:
        s.setAttribute("parentstylename", kw["parent"])
    p = ParagraphProperties()
    for k, v in kw.get("para", {}).items():
        p.setAttribute(k, v)
    if kw.get("para"):
        s.addElement(p)
    t = TextProperties()
    for k, v in kw.get("text", {}).items():
        t.setAttribute(k, v)
    if kw.get("text"):
        s.addElement(t)
    doc.styles.addElement(s)
    return name

st_base = style("st_base", para={"textalign": "justify", "marginbottom": "0.25cm",
                                   "linespacing": "0.26cm"},
                text={"fontname": "DejaVu Sans", "fontsize": "12pt",
                       "language": "fr", "country": "FR"})
st_obj = style("st_obj", parent="st_base",
               para={"marginbottom": "0.5cm", "textalign": "left"},
               text={"fontweight": "bold", "color": NAVY, "fontsize": "12pt"})
st_coord = style("st_coord", parent="st_base",
                 para={"textalign": "left", "marginbottom": "0.1cm"},
                 text={"fontsize": "11pt"})
st_dest = style("st_dest", parent="st_base",
                para={"textalign": "right", "marginbottom": "0.15cm"},
                text={"fontsize": "11pt"})
st_date = style("st_date", parent="st_base",
                para={"textalign": "right", "marginbottom": "0.4cm", "margintop": "0.2cm"},
                text={"fontsize": "11pt"})
st_pol = style("st_pol", parent="st_base",
               para={"textalign": "left", "marginbottom": "0.3cm", "margintop": "0.3cm"},
               text={"fontweight": "bold", "fontsize": "12pt"})
st_right = style("st_right", parent="st_base",
                 para={"textalign": "right", "marginbottom": "0.1cm"},
                 text={"fontsize": "12pt"})
st_blank = style("st_blank", parent="st_base",
                 para={"textalign": "left", "marginbottom": "0.2cm"},
                 text={"fontsize": "6pt"})

def para(text, st=st_base):
    p = P(stylename=st)
    p.addText(text)
    doc.text.addElement(p)

# ---------- COORDONNEES + DATE (tableau sans bordure) ----------
st_tbl = Style(name="Tbl_Entete", family="table")
stp = TableProperties(); stp.setAttribute("width", "100%"); st_tbl.addElement(stp)
doc.styles.addElement(st_tbl)

st_cell = Style(name="Cell_Entete", family="table-cell")
scp = TableCellProperties(); scp.setAttribute("border", "none"); st_cell.addElement(scp)
doc.styles.addElement(st_cell)

csg = Style(name="Col_G", family="table-column")
cgp = TableColumnProperties(); cgp.setAttribute("columnwidth", "60%"); csg.addElement(cgp)
doc.styles.addElement(csg)
csd = Style(name="Col_D", family="table-column")
cdp = TableColumnProperties(); cdp.setAttribute("columnwidth", "40%"); csd.addElement(cdp)
doc.styles.addElement(csd)

tbl = Table(name="Entete", stylename="Tbl_Entete")
tc1 = TableColumn(numbercolumnsrepeated=1); tc1.setAttribute("stylename", "Col_G"); tbl.addElement(tc1)
tc2 = TableColumn(numbercolumnsrepeated=1); tc2.setAttribute("stylename", "Col_D"); tbl.addElement(tc2)
tr = TableRow()
c1 = TableCell(stylename="Cell_Entete")
c1.addElement(P(stylename=st_coord, text=EXP_NOM))
c1.addElement(P(stylename=st_coord, text=EXP_ADR))
c1.addElement(P(stylename=st_coord, text=EXP_TEL))
tr.addElement(c1)
c2 = TableCell(stylename="Cell_Entete")
c2.addElement(P(stylename=st_date, text="Kinshasa, le " + date.today().strftime("%d/%m/%Y")))
tr.addElement(c2)
tbl.addElement(tr)
doc.text.addElement(tbl)

para("", st_blank)

d = P(stylename=st_dest); d.addText(DEST_1); doc.text.addElement(d)
d2 = P(stylename=st_dest); d2.addText(DEST_2); doc.text.addElement(d2)
d3 = P(stylename=st_dest); d3.addText(DEST_3); doc.text.addElement(d3)
para("", st_blank)
para(OBJET, st_obj)
para("", st_blank)

for c in CORPS:
    para(c)

para("", st_blank)
pol = P(stylename=st_pol); pol.addText(POLITESSE); doc.text.addElement(pol)

fr = Frame(width="6cm", height="2.2cm", anchortype="paragraph")
fr.addElement(ODImage(href=SIGNATURE_IMG, type="simple", show="embed", actuate="onLoad"))
doc.text.addElement(fr)
para(EXP_NOM, st_right)

doc.save(OUT_ODT)
print("ODT genere:", OUT_ODT)
