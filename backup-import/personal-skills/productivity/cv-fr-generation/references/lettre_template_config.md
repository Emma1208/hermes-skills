# Living base letter template — CONFIG block
File: `/root/linkedin_app/modele_lettre_generale.py` → regenerates `Lettre_Motivation_Generale.pdf`.
User saved this on 2026-07-14 as the "base" for ALL future letters (his + family).
**Only the CONFIG block at the top is ever edited.** Layout code below is frozen.

```python
# ===== CONFIG — ZONE A MODIFIER PAR OFFRE =====
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
CORPS = [ "para1", "para2", "para3", "para4" ]
SORTIE = "/root/linkedin_app/Lettre_Motivation_Generale.pdf"
# =============================================

LEFT = 25; RIGHT = 25; COL = 100
pdf = FPDF(format="A4")
pdf.add_font("SR","","/root/linkedin_app/DejaVuSerif.ttf")
pdf.add_font("SR","B","/root/linkedin_app/DejaVuSerif-Bold.ttf")
pdf.set_auto_page_break(auto=True, margin=25); pdf.set_margins(LEFT,25,RIGHT); pdf.add_page()
# Expéditeur top-LEFT (commune on its OWN line), Date top-RIGHT cell(160,6,...,align="R")
# Objet LEFT multi_cell(100,6,"Objet : "+OBJET_POSTE) at objet_y=y+12
# Destinataire RIGHT: multi_cell(85,5,"A Monsieur le Directeur des Ressources Humaines de "+STRUCTURE, new_x=XPos.RIGHT,...) at COL
# LOCALISATION underlined below (pdf.line at COL..COL+w)
# Formule RIGHT: cell(0,6,"Monsieur le Directeur,") at COL
# Corps LEFT multi_cell(160,5,...,align="J")
# Politesse RIGHT then LEFT; Signature RIGHT cell(85,6,NAME,align="R") at COL
```

## Sibling-letter recipe (verified with BITOTA letter)
1. `cp modele_lettre_generale.py generer_lettre_<prenom>.py`
2. In CONFIG: swap EXPEDITEUR (their identity), DATE_LIEU, OBJET_POSTE, STRUCTURE, LOCALISATION, CORPS, SORTIE.
3. For "agent d'entretien" type letters, the formule/signature living convention:
   - destinataire line: `A Monsieur le Responsable des Ressources Humaines` (Madame removed per user)
   - formule: `Monsieur le Responsable,` (Madame + "des ressources humaines" removed per user)
   - signature: `Votre employée,` + name in bold caps (feminine register for sister)
4. Regenerate, verify 1 page + word coords (§4d), send MEDIA.
