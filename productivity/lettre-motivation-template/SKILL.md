---
name: lettre-motivation-template
description: Genere une lettre de motivation multi-format (PDF, DOCX, LaTeX) selon le modele RDC canonique (expediteur+nom a gauche avec date meme ligne a droite, destinataire en-dessous a droite mais aligne a gauche, Concerne, salutation, corps, formule de politesse 1 ligne, signature toute alignee a droite). Reutilisable, on remplit les champs dans lettre_data.py puis on regenere. A utiliser pour creer/recréer une lettre de motivation ou partir d'un modele comme base de candidature.
---

# Lettre de Motivation — Template RDC reutilisable

Modele de lettre de motivation conforme au style congolais courant (vu dans WPS Office),
pensee pour assortir au CV (cv-master-template) : meme palette navy, memes polices.

## Mise en page canonique (RDC) — RESPECTER STRICTEMENT
C'est LA convention validee par l'utilisateur (plusieurs corrections successives). Ne pas
l'improviseer. Detail des coordonnees et points de controle dans
`references/rdc-letter-layout.md`. Ordre vertical du haut vers le bas :
1. **LIGNE 1** : `expediteur.nom` a GAUCHE | `date_lieu` a DROITE (MEME ligne,
   alignee en haut). Utiliser deux cellules/minipages cote a cote, PAS l'une
   sous l'autre.
2. **Sous le nom** (toujours a gauche) : adresse, tel, email de l'expediteur.
3. **Destinataire** : EN-DESSOUS du bloc expediteur, **bloc positionné à DROITE**
   (pas à gauche, pas sur la meme ligne que la date) MAIS le **texte aligné à
   GAUCHE** (les lignes ligne1/2/3 commencent à gauche du bloc, non collées au
   bord droit). Etat final valide par l'utilisateur.
4. **Concerne :** (navy gras, ÉCRIT « Concerne : » et NON « Objet : ») : largeur
   **LIMITÉE à celle du bloc expéditeur (95 mm)** via `multi_cell` (retour à la
   ligne automatique si le texte est long, sans déborder au-delà de la moitié de
   page). Convention FINALISÉE validée par l'utilisateur.
5. **Formule d'appel** (salutation, ex. « Monsieur le Directeur, ») : AU-DESSUS du
   corps, DONC SOUS le Concerne. ORDRE = Concerne -> Salutation -> Corps. Ne JAMAIS
   mettre la salutation au-dessus du Concerne.
6. **Corps** (paragraphes), **formule de politesse**, **signature** (nom dactylographie, navy gras).
   - Formule de politesse : **SUR UNE SEULE LIGNE** (convention FINALISÉE) :
     `Je vous prie d'agreer, Monsieur le Directeur, l'assurance de ma
     consideration distinguee.` — AUCUN saut de ligne après la virgule, la suite
     suit directement. Dans les donnees : `formule` = liste a 1 element.
       * PDF  : `pdf.cell(0, 5.5, line, ...)` ou `multi_cell` par element.
       * DOCX : `para(formule[0], ...)` (1 seul paragraphe).
       * LaTeX : une seule commande `\Formule` (pas `\FormuleA`+`\FormuleB`).
   - Convention signature validée (FINALE) : **TOUT le nom de la signature est
     aligné à DROITE** (pas seulement le post-nom). Bloc positionné en bas de
     lettre, sous le corps. Dans les 3 formats :
       * PDF  : `pdf.cell(0, 6, signature_nom, align="R", ...)`
       * DOCX : paragraphe `<w:jc w:val="right"/>` pour le nom signé.
       * LaTeX : `\raggedleft {\color{navy}\textbf{\NomExp}}`.
   - ⚠️ AMBIGUÏTÉ FRÉQUENTE : si l'utilisateur parle de « le nom en dessous du
     corps de la lettre » ou « le nom en bas », il désigne la **SIGNATURE**, PAS
     le bloc expéditeur en haut. Ne pas toucher au bloc expéditeur pour ce type
     de demande. (Correction réelle : j'avais modifié l'expéditeur au lieu de la
     signature -> « tu m'a pas compris ».) En cas de doute, confirmer avant de
     modifier l'un ou l'autre.
   - ⚠️ Quand l'utilisateur dit « l'Objet doit se limiter au bloc expéditeur /
     ne pas depasser la moitie de la page » : il veut la largeur de `Concerne`
     bornée à 95 mm (comme le bloc expéditeur) + retour à la ligne auto.

PITFALLS (erreurs deja faites, a ne plus reproduire) :
- ❌ Date sous le nom / destinataire sur la meme ligne que l'expediteur.
- ❌ Salutation placee au-dessus du Concerne (ordre Salut->Concerne->Corps).
- ❌ Destinataire a gauche. Le BLOC destinataire reste a DROITE (mais le texte
  dedans est aligné a GAUCHE — nuance finale validée).
- ❌ Ecrire « Objet : » au lieu de « Concerne : » (libellé finalisé de l'utilisateur).
- ❌ Formule de politesse sur 2 lignes (saut après la virgule) — doit être 1 ligne.
- ❌ Concerne en `cell(0,...)` pleine largeur — doit être `multi_cell(95,...)` pour
  limiter à la largeur du bloc expéditeur.
- ❌ Oublier de changer `signature_nom` en meme temps que `expediteur` quand on
  remplace l'identite : la signature est un champ SEPARE (verif : plus aucune
  trace de l'ancienne identite dans le PDF/DOCX apres generation).
- ❌ Variantes ciblées qui écrasent le template de base : quand on crée une
  version ciblée (ex. enseignant), utiliser des fichiers séparés
  (`*_enseignant.py` + sortie `..._ENSEIGNANT.pdf/.docx`) et pointer le champ
  `OUT`/l'import dessus, SINON `make_*` réécrit le PDF de base. Voir
  `references/candidature-ciblee.md`.

## Orthographe & accents (OBLIGATOIRE avant sauvegarde)
Le corps de lettre doit toujours être en français correct, AVEC accents :
présente, susmentionné, économiques, Financière, Université, intérêt, effectué,
Contrôle, appréhender, Comptabilité, maîtrise, compétences, acharné, déterminé,
équipe, caractérise, particulièrement, accordée, entière, agréer, considération,
distinguée. Le fichier `lettre_data.py` est la source : le corriger AVANT de
générer. Vérifier après génération (pypdf -> tous les mots accentués présents).
Le LaTeX utilise déjà les bons accents (et `\'` pour l'apostrophe accentuée).

## Emplacement de travail
Tous les fichiers vivent dans `/root/lettre_motivation/` :
- `lettre_data.py`         -> source unique (dict LETTRE). REMPLIR CECI d'abord.
- `make_lettre_pdf.py`     -> PDF via fpdf2 (DejaVu, Unicode).
- `make_lettre_docx.py`    -> .docx VALIDE (zip+XML OOXML, tableau 2 colonnes sans bordures).
- `LETTRE_MOTIVATION.tex`  -> template LaTeX (champs \newcommand en haut).

## Flux de travail
1. Editer `lettre_data.py` (dict LETTRE) : expediteur, date_lieu, destinataire
   (ligne1/2/3), salutation, objet, corps (liste de paragraphes),
   formule (1 SEUL élément = la ligne complète), signature_nom. Champs optionnels :
   `signature_image` (png signature manuscrite), `photo` (jpg, coin haut-droite).
   - Pour une variante ciblée (ex. enseignant) SANS écraser le template :
     voir `references/candidature-ciblee.md`.
2. `cd /root/lettre_motivation && python3 make_lettre_pdf.py`
3. `cd /root/lettre_motivation && python3 make_lettre_docx.py`
4. Le .tex se compile cote utilisateur : `pdflatex LETTRE_MOTIVATION.tex`.

## Pieges / environnement (Termux PRoot, Python 3.14, ARM musl) — voir cv-master-template
Technique complete (DOCX a la main, photo PDF sans Pillow, puce ⮚) dans
`references/offline-docx-pdf-generation.md` du skill cv-master-template.
Résumé : Pillow cassé -> reportlab & python-docx (lxml) inutilisables ; fpdf2 OK
(DejaVu systeme) ; puce ⮚ absente -> ► dans le PDF ; DOCX : pas de backslash dans
les f-string (erreur Python 3.11+), preferer variables/boucles pour l'XML.

## Sauvegarde / GitHub (Token hygiene)
- Compte GitHub = `Emma1208`. Depot public de reference : `cv-lettre-templates`
  (contient cv-master-template + lettre-motivation-template + variante-enseignant).
- ⚠️ SOURCE DE VÉRITÉ = `/root/lettre_motivation/` et `/root/cv_kakesa/`, PAS
  `~/.hermes/skills/*`. Les skills sont des COPIES ; après une correction, copier
  les fichiers de `/root/...` vers `skill/.../scripts/` AVANT de pousser, sinon le
  dépôt GitHub reste obsolète. Réflexe : `cp /root/lettre_motivation/lettre_data.py
  skill/.../scripts/` etc. juste avant `git add`.
- ⚠️ TOKEN : ne jamais l'écrire dans un fichier relu/commité ; le passer via
  `export GITHUB_TOKEN=...` dans le shell, puis `unset GITHUB_TOKEN` apres le push.
  Ne jamais le stocker en memoire Hermes ni dans un fichier du dépôt.

## Verification attendue
- PDF : `pypdf` -> 1 page typique, texte contient Nom expediteur, Destinataire,
  « Concerne : », et la formule de politesse SUR UNE LIGNE. Verifier aussi :
  date MEME ligne que le nom ; destinataire APRES l'expediteur dans le flux ;
  Concerne AVANT la salutation ; Concerne ne depasse pas la moitie de page.
- DOCX : dezipper, parser document.xml + rels avec xml.dom.minidom -> doit passer.
