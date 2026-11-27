#!/usr/bin/env python3
"""MODELE GENERAL DE LETTRE DE MOTIVATION (base reusable) — KAKESA 2026-07-14.
Copier ce fichier, modifier UNIQUEMENT la zone CONFIG, lancer, livrer le PDF.
Mise en page validee (style Serge) : expediteur(commune separee), date droite,
objet limite au milieu, destinataire/formule/signature colonne droite (x=100mm),
corps justifie pleine largeur, 1 page, 11pt DejaVuSerif.
"""
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# =====================================================================
# CONFIG - ZONE A MODIFIER PAR OFFRE
# =====================================================================
EXPEDITEUR = [
    "KAKESA MUDIMBA DIEUDONNE",
    "N° 3, AV. TUNGILA, Q. BIANDA,",
    "C. MONT NGAFULA",
    "Tel : +243 81 849 16 01",
    "Email : kakesamudimba@gmail.com",
]
DATE_LIEU   = "Kinshasa, 14 / 07 / 2026"
OBJET_POSTE = "Candidature au poste de Responsable Technique"   # sans "Objet :"
STRUCTURE   = "FLASH SERVICES SARL"
LOCALISATION = "KINSHASA / GOMBE"
CORPS = [
    "Par la présente, je vous soumets ma candidature au poste de Responsable Technique au sein "
    "de FLASH SERVICES SARL. Titulaire d'une licence en Sciences Économiques et de Gestion, "
    "option Gestion Financière de l'Université de Kinshasa, je dispose d'une solide capacité "
    "d'analyse, de coordination et de suivi que je souhaite mettre au service de vos opérations.",
    "Mon expérience en tant qu'Agent d'appui logistique au projet PUC MED de Médecins Sans "
    "Frontières m'a permis de gérer le suivi de stock, la chaîne du froid et le reporting "
    "logistique, développant ainsi le sens de la rigueur, de l'organisation et du suivi des "
    "interventions. Par ailleurs, mon stage à la Direction de Réglementation et Qualité "
    "Comptable (DRQC) du Ministère des Finances m'a formé à la vérification des pièces et à la "
    "production de rapports, compétences directement transposables au suivi des achats, des "
    "dépenses et des opérations dans SAP.",
    "Rigoureux et doté d'une forte aptitude pour l'analyse de données, je suis en mesure "
    "d'analyser les consommations (carburant, énergie), les factures d'eau et d'électricité, "
    "ainsi que les rapports techniques, et d'en proposer des actions correctives ou préventives. "
    "Ma capacité à coordonner une équipe et à planifier le suivi des interventions s'accorde avec "
    "la mission de supervision des activités techniques confiée au Responsable Technique.",
    "Je suis persuadé que ma conscience professionnelle, mon sens de l'organisation et mon aptitude "
    "au travail en équipe constitueront un atout pour FLASH SERVICES. Je me tiens à votre entière "
    "disposition pour tout renseignement complémentaire et vous prie de trouver ci-joint mon "
    "curriculum vitæ pour de plus amples informations.",
]
SORTIE = "/root/linkedin_app/Lettre_Motivation_Generale.pdf"
# =====================================================================

LEFT = 25
RIGHT = 25
COL = 100  # colonne de droite (destinataire, formule, signature)

pdf = FPDF(format="A4")
pdf.add_font("SR", "", "/root/linkedin_app/DejaVuSerif.ttf")
pdf.add_font("SR", "B", "/root/linkedin_app/DejaVuSerif-Bold.ttf")
pdf.set_auto_page_break(auto=True, margin=25)
pdf.set_margins(LEFT, 25, RIGHT)
pdf.add_page()

def set_serif(size=11, style=""):
    pdf.set_font("SR", style, size)

# ---------- EXPEDITEUR (gauche, commune sur ligne separee) ----------
y = 25
set_serif(11, "")
for line in EXPEDITEUR:
    pdf.set_xy(LEFT, y)
    pdf.cell(0, 6, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    y += 6

# ---------- DATE (haut droite) ----------
pdf.set_xy(LEFT, 25)
set_serif(11, "")
pdf.cell(160, 6, DATE_LIEU, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# ---------- OBJET (limite au milieu, debordement dessous) ----------
objet_y = y + 12
pdf.set_xy(LEFT, objet_y)
set_serif(11, "B")
pdf.multi_cell(100, 6, "Objet : " + OBJET_POSTE, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")

# ---------- DESTINATAIRE (colonne droite) ----------
dest_y = objet_y + 11
pdf.set_xy(COL, dest_y)
set_serif(11, "")
pdf.multi_cell(85, 5, "A Monsieur le Responsable des Ressources Humaines de " + STRUCTURE,
               new_x=XPos.RIGHT, new_y=YPos.NEXT, align="L", max_line_height=5)
dy = pdf.get_y() + 1
pdf.set_xy(COL, dy)
w = pdf.get_string_width(LOCALISATION)
pdf.cell(w, 6, LOCALISATION, new_x=XPos.LMARGIN, new_y=YPos.TOP)
y2 = pdf.get_y()
pdf.set_draw_color(0, 0, 0); pdf.set_line_width(0.3)
pdf.line(COL, y2 + 6 + 1.5, COL + w, y2 + 6 + 1.5)

# ---------- FORMULE D'APPEL (colonne droite) ----------
formule_y = dy + 13
pdf.set_xy(COL, formule_y)
set_serif(11, "")
pdf.cell(0, 6, "Monsieur le Responsable,", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# ---------- CORPS (justifie, pleine largeur) ----------
cy = formule_y + 9
for p in CORPS:
    pdf.set_xy(LEFT, cy)
    set_serif(11, "")
    pdf.multi_cell(160, 5, p, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="J")
    cy = pdf.get_y() + 2

# ---------- POLITESSE / SIGNATURE (droite) ----------
sig_y = cy + 4
pdf.set_xy(COL, sig_y)
set_serif(11, "")
pdf.cell(85, 6, "Veuillez agréer, Monsieur le Responsable,", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_xy(COL, pdf.get_y() + 1)
set_serif(11, "B")
pdf.cell(85, 6, "KAKESA MUDIMBA DIEUDONNE", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

pdf.output(SORTIE)
print("PDF genere:", SORTIE)
