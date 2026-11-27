# Official letter layout — literal coordinates
All in mm. A4 = 210 x 297. LEFT=25, RIGHT=25, top=25, bottom=25. BLK (100mm) = start of right blocks.
Right margin line = 185mm (210 - 25). Max width for right-aligned cell = 160 (185-25).

- Expéditeur: x=25 (LEFT), ALL CAPS, width capped 100mm (wrap long lines).
- Date: x=25, cell width=160, align="R" → text ends at 185mm. `KINSHASA, JJ / MM / AAAA`.
- Objet: y = 25 + (n_exp*6) + 25 - 6 ; x=25, ALL CAPS, width capped 100mm.
- Destinataire: x=25, cell width=160, align="R". Lines:
  `A MONSIEUR LE DIRECTEUR` / `DES RESSOURCES HUMAINES` / `DE [ORGANISATION]`
  then `KINSHASA / GOMBE` underlined BELOW: pdf.line(185-w, y2+6+1.5, 185, y2+6+1.5)
  where w = string width, y2 = cell top (new_y=YPos.TOP).
- Formule d'appel: formule_y = objet_y + 30 + 12 (=42mm under objet). x=25, w=160, align="R".
  Text: `Monsieur le Directeur,`
- Corps: para1 first line to right margin then LEFT; others justified. Interline 5mm to fit 1 page.
- Politesse: line1 RIGHT (`Veuillez agréer, Monsieur le [Titre],`), line2 LEFT (`l'assurance de ma considération distinguée.`)
- Signature: x=25, w=160, align="R", ALL CAPS `KAKESA MUDIMBA DIEUDONNE`.

Font: DejaVuSerif 11pt (add_font "SR"). Underline = manual line, never set_underline.

## CV layout notes
- Title `Curriculum Vitæ` (æ). Subtitle = poste visé.
- Sections I-VIII (skip VII). 
- Infos perso & Références: blue bold label + black value. Références numbered.
- Dates bold; job titles underlined via pdf.line. Keywords black, not bold.
- Honour clause italic at end + date.today().
- No photo, no "généré automatiquement" footer. Body font ≥13.
