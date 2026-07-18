# Mise en page canonique — Lettre de motivation RDC (validée)

Convention validée par l'utilisateur après MULTIPLES corrections. Ne pas
improviseer l'ordre ni l'alignement. ETAT FINAL ci-dessous (le plus récent
prime sur le reste).

## Ordre vertical (haut -> bas) et alignement
1. **LIGNE 1** (côte à côte, 2 minipages/cellules) :
   - GAUCHE : `expediteur.nom` (navy gras, nom COMPLET).
   - DROITE (aligné en haut, même ligne) : `date_lieu`.
   - ❌ La date ne va PAS sous le nom. ❌ Le destinataire ne va PAS sur cette ligne.
2. **Sous le nom, à GAUCHE** : adresse, tel, email de l'expéditeur (cellule
   gauche de la 2e ligne du tableau, ou minipage séparé).
3. **Destinataire** : EN-DESSOUS du bloc expéditeur, **bloc positionné à
   DROITE** (pas à gauche) MAIS **texte aligné à GAUCHE** (les lignes
   commencent à gauche du bloc, non collées au bord droit). Etat final validé.
   Lignes : ligne1 « A Monsieur le Directeur des Ressources »,
   ligne2 « Humaines de DELOITTE RDC », ligne3 « KINSHASA / GOMBE ».
   - Implémentation : PDF `multi_cell(80,5,...,align="L")` avec x placé à droite
     (`set_xy(w - MARGIN - 80, exp_bottom + 4)`) ; DOCX cellule droite SANS
     `<w:jc w:val="right"/>` ; LaTeX minipage `\hfill` SANS `\raggedleft`.
   - ❌ Destinataire à gauche = interdit. ❌ Texte du destinataire collé à
     droite = ancien état, remplacé par alignement gauche dans le bloc droit.
4. **Objet :** (navy gras, pleine largeur).
5. **Formule d'appel / salutation** (« Monsieur le Directeur, ») :
   AU-DESSUS du corps, DONC SOUS l'Objet. Ordre = Objet -> Salutation -> Corps.
   ❌ Ne jamais mettre la salutation au-dessus de l'Objet.
6. **Corps** (paragraphes), **formule de politesse** (2 lignes),
   **signature** (nom dactylographié, navy gras).
   - Convention signature FINALE validée (demande « tout le nom à droite ») :
     **TOUT le nom de la signature est aligné à DROITE** (pas seulement le
     post-nom). Rendu : `KAKESA MUDIMBA Emmanuel-Dieudonné` aligné à droite.
     Implémentation par format :
       * fpdf2 : `pdf.cell(0, 6, signature_nom, align="R", new_x="LMARGIN", new_y="NEXT")`.
       * DOCX : paragraphe `<w:jc w:val="right"/>` pour le nom signé.
       * LaTeX : `\raggedleft {\color{navy}\textbf{\NomExp}}`.
   - ⚠️ AMBIGUÏTÉ « le nom en dessous du corps » : l'utilisateur parle de la
     **SIGNATURE** (bas de lettre), JAMAIS du bloc expéditeur (haut). Ne pas
     modifier l'expéditeur pour ce type de demande. En cas de doute, clarifier.

## Points de contrôle fréquents
- Quand on remplace l'identité de l'expéditeur, changer AUSSI `signature_nom`
  (champ séparé). Vérifier en fin de génération qu'aucune trace de l'ancienne
  identité ne subsiste (ex. plus de « MBULU » dans le PDF/DOCX).
- Numéros de référence masqués « **** » dans une source doivent être remplacés
  par les vrais chiffres une fois connus.
- Orthographe/accents OBLIGATOIRES avant sauvegarde (voir SKILL.md).

## Coordonnées fpdf2 typiques (A4)
- Marges 18 mm. `y0 = 18` (pt) pour la 1re ligne.
- Nom : `set_xy(MARGIN, y0)`, date : `set_xy(w - MARGIN - 80, y0)`.
- Destinataire droite + texte à gauche :
  `set_xy(w - MARGIN - 80, exp_bottom + 4)`,
  `multi_cell(80, 5, ..., align="L")`.
