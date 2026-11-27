# Modèle CV vierge ÉDITABLE (.odt via odfpy)

## Quand l'utiliser
Le générateur PDF fpdf2 produit un CV *figé* (rempli, non éditable). Quand
l'utilisateur veut un **modèle vierge à remplir lui-même** (profil "opérateur
de saisie", ou pour produire des variantes à la main), génère un `.odt`
LibreOffice avec des champs `[à remplir]`. Il ouvre le fichier et tape dedans.

## Install
`pip install odfpy` (dispo sur le venv après install). DejaVu Sans est rendu
par LibreOffice à l'ouverture (pas besoin d'embed le TTF dans l'odt).

## Deux PIÈGES odfpy (toutes les deux levées en session)
1. **`page-width`/`page-height` NE SONT PAS autorisés sur `doc.text`.**
   `doc.text.setAttribute("page-width","21cm")` → `AttributeError: Attribute
   page-width is not allowed in <office:text>`. FIX : ne pas les poser ; la
   taille de page vient de la page-layout par défaut du document ODF. On les
   omet simplement.
2. **`spacebefore` / `spaceafter` NE SONT PAS des attributs valides de
   `ParagraphProperties`.** → `AttributeError ... not allowed in
   <style:paragraph-properties>`. FIX : les retirer. Pour l'espacement, on
   utilise `marginleft`/`marginright` (valides) + le `padding` du bloc coloré.
   Les attributs QUI MARCHENT : `backgroundcolor`, `padding`, `marginleft`,
   `marginright` (ParagraphProperties) ; `color`, `fontsize`, `fontweight`,
   `fontfamily` (TextProperties).

## Style retenu (identique à la référence fpdf2)
- Bandeau bleu marine (NAVY="#142850") en header + sur chaque titre de section
  (texte blanc). Sections I→VII.
- Corps 12pt noir (#1E1E1E), titres de section 13pt gras blanc.
- Champs placeholder en `[CROCHETS]` majuscules pour guider la saisie.
- Pas de photo (cohérent avec la règle CV), accents corrects (DejaVu via LO).

## Vérification (règle utilisateur : valider visuellement AVANT de dire « fait »)
1. Convertir en PDF pour rendu :
   `soffice --headless --convert-to pdf fichier.odt` (depuis le dossier du .odt)
2. `pdftoppm -png -r 100 fichier.pdf /tmp/apercu`
3. `vision_analyze` sur `/tmp/apercu-1.png` : bandeaux présents, champs
   visibles, aucun texte tronqué/chevauché, lisibilité OK.
4. **Check troncature de fin de ligne** (voir §4) avec `pdftotext -layout`.

## Générateur réutilisable
`scripts/generer_cv_modele_vierge.py`. Usage :
`python3 generer_cv_modele_vierge.py [chemin_sortie.odt]`.

## 3. PIÈGE — alignement à droite (textalign="right" marche… presque)
Pour aligner à droite, créer un style avec `ParagraphProperties(textalign="right")`
(et TextProperties pour couleur/taille). Cela FONCTIONNE pour les lignes courtes
("Fait à Kinshasa…", "Signature :", "KAKESA MUDIMBA Dieudonné" collent bien à la
marge droite). MAIS une ligne LONGUE alignée à droite commence vers le milieu de la
page (elle occupe presque toute la largeur) → le modèle de vision la lit comme
« centrée ». C'est une FAUSSE ALARME : elle est bien à droite.
→ Convention retenue (CV rempli, 2026-07-16) : le **serment** « Je jure sur mon
honneur… » reste à **GAUCHE** (style left) ; seuls **« Fait à Kinshasa, le
JJ/MM/AAAA » + « Signature : » + « KAKESA MUDIMBA Dieudonné »** vont à **DROITE**.
C'est exactement ce que l'utilisateur a demandé (« Fait à Kinshasa+date, signature,
nom à droite »). Ne pas tout mettre à droite.
→ Pour AJOUTER un style right-align, le helper `mk_para_style` ne prend pas
textalign : créer le style à la main :
```python
from odf.style import ParagraphProperties as _PP, Style as _S, TextProperties as _TP
_r = _S(name="CVRightA", family="paragraph")
_r.addElement(_PP(textalign="right", marginleft="0cm", marginright="0cm"))
_r.addElement(_TP(color=DARK, fontsize="10.5pt", fontfamily="DejaVu Sans"))
doc.styles.addElement(_r)
st_right = "CVRightA"   # passer cette chaîne à P(stylename=...)
```
NOTE : `TextProperties` vient de `odf.style`, PAS de `odf.text` (import error sinon).

## 4. PIÈGE — troncature de la queue d'une ligne longue dans le PDF
Une entrée de référence mise sur UNE SEULE ligne trop longue (ex. « 4. OMARI BATUKWA
— Pharmacien logisticien, MSF — omaribatukwa@gmail.com / +243 814 363 400 ») perd SA
FIN dans le PDF : la vision montre « …363 » et le « 400 » est coupé à la marge droite.
`pdftotext -layout` confirme la perte (« …814 363 » sans 400). FIX : scinder en une
ligne `Tél :` à part :
```python
("4. OMARI BATUKWA — Pharmacien logisticien, MSF — omaribatukwa@gmail.com",),
("     Tél : +243 814 363 400",),
```
→ RÈGLE : après génération d'un .odt rempli, vérifier la queue des lignes avec
`pdftotext -layout fichier.pdf - | grep -i "omari\|363 400"` (ou le motif pertinent),
EN PLUS du check visuel vision. Ne pas se fier à la vision seule pour la troncature
de fin de ligne (elle peut la rater ou la surligner).

## 5. Convention CV rempli livré (référence vivante du format éditable)
`generer_cv_rempli.py` → `/root/Candidatures/Modèles/CV_KAKESA_MUDIMBA_rempli.odt`
(+ `.pdf`). Format : bandeaux bleu marine identiques à la référence fpdf2, sections
I→VII (INFOS PERSO, PARCOURS remis en ordre chronologique, COMPÉTENCES, ÉTUDES,
FORMATIONS, LANGUES, RÉFÉRENCES 6 contacts en lignes compactes), serment à gauche,
bloc signature à droite, **2 pages max** (défaut utilisateur 2026-07-16). Le .odt est
ÉDITABLE : l'utilisateur peut le rouvrir et le modifier.
