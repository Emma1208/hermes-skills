---
name: cv-master-template
description: Génère un CV multi-format (PDF, DOCX, LaTeX) à partir d'un template de base réutilisable, en réutilisant les données d'un CV existant comme socle pour des candidatures ciblées. À utiliser quand l'utilisateur veut créer/recréer un CV, partir d'un CV existant comme base, ou produire un CV dans plusieurs formats (PDF/DOCX/LaTeX).
---

# CV Master Template (base KAKESA)

Template de CV congolais structuré (sections I→VIII), généré en 3 formats à partir
d'une source de données unique. Conçu pour servir de BASE réutilisable : on part de
ce CV "complet" et on en dérive des versions ciblées (ex. professeur, comptable,
logisticien) en filtrant/réordonnant les expériences.

## Emplacement de travail
Tous les fichiers vivent dans `/root/cv_kakesa/` :
- `cv_data.py`   → source unique des données (dict `CV`). MODIFIER CECI d'abord.
- `make_pdf.py`  → génère le PDF via fpdf2 (police DejaVu, Unicode).
- `make_docx_raw.py` → génère un .docx VALIDE sans python-docx (zip+XML).
- `inject_photo_pdf.py` → injecte le JPEG de la photo dans le PDF (contourne Pillow cassé).
- `CV_KAKESA_MUDIMBA.tex` → template LaTeX (compiler avec pdflatex).
- `photo_kakesa.jpg` → photo extraite du CV source.

## Mise en page canonique (validée par l'utilisateur)
- Photo EN HAUT A DROITE (coin à 16 mm), cadre navy. Elle reste visible.
- Titre + tout le contenu commencent à 25 mm du haut (marge haute = 25 mm).
- Pour éviter le recouvrement : la colonne de texte est automatiquement rétrécie
  à droite tant qu'elle chevauche verticalement la zone de la photo, puis repasse
  pleine largeur en dessous.
- DOCX : photo en IMAGE FLOTTANTE (ancre, coin haut-droit) -> ne pousse pas le
  titre ; texte à gauche, habillage autour.
- LaTeX : photo en position absolue (TikZ overlay/remember picture, anchor north
  east à 16 mm du coin), marge haute top=2.5cm.
- Conseil utilisateur : numéros de référence masqués (****) dans le CV source
  doivent être remplacés par les vrais chiffres quand connus (corrigé : TEDDY
  PULUMBA +243 823 577 917, MFUNI INABANZA +243 816 147 052).

## Structure du template (sections)
I. Informations personnelles | II. Parcours professionnel | III. Domaines de compétence
IV. Études faites | V. Formations académique | VI. Langues | VIII. Personnes de référence
+ signature (lieu/date + nom). NOTE: l'original saute la section VII (à conserver tel quel
ou à corriger selon demande).

## Variante ciblée « enseignant » (RETENUE par l'utilisateur)
Recette éprouvée pour dériver une version ciblée sans écraser le template de base :
- Copier `cv_data.py` -> `cv_data_enseignant.py`, réordonner `parcours` pour mettre
  l'expérience clé en tête (ex. enseignement avant MSF/Forex), réordonner
  `competences` (pédagogie en tête). Garder études/langues/références/signature.
- `sed 's/^import cv_data as D$/import cv_data_enseignant as D/' make_pdf.py > make_pdf_enseignant.py`
- Changer `OUT = "...CV_KAKESA_MUDIMBA.pdf"` -> `"...CV_KAKESA_MUDIMBA_ENSEIGNANT.pdf"`
  dans make_pdf_enseignant.py (SINON écrase le PDF de base).
- `sed` du même genre pour `inject_photo_pdf.py` : mettre src=out=`..._ENSEIGNANT.pdf`.
- Résultat : `CV_KAKESA_MUDIMBA_ENSEIGNANT.pdf` (2 pages, photo, enseignement en tête).
- ⚠️ L'injecteur `inject_photo_pdf.py` écrase le PDF de base (src=out) : pour une
  variante, copier le script et changer `src`/`out` vers `..._ENSEIGNANT.pdf`.

## Flux de travail
1. **Modifier les données** dans `cv_data.py` (éditer le dict `CV`). Pour une candidature
   ciblée, filtrer les entrées `parcours`/`competences` ou réordonner.
2. **Régénérer le PDF** :
   `cd /root/cv_kakesa && python3 make_pdf.py && python3 inject_photo_pdf.py`
3. **Régénérer le DOCX** :
   `cd /root/cv_kakesa && python3 make_docx_raw.py`
4. Le .tex est prêt ; compiler côté utilisateur avec `pdflatex CV_KAKESA_MUDIMBA.tex`.

## Pièges / environnement (Termux PRoot, Python 3.14, ARM musl)
Technique complète (DOCX à la main, injection photo PDF sans Pillow, puce ⮚,
extraction photo d'un PDF source) dans `references/offline-docx-pdf-generation.md`.
Résumé : Pillow cassé → reportlab & python-docx inutilisables ; fpdf2 OK (DejaVu
système) ; puce ⮚ absente des polices → ► dans le PDF ; photo injectée via pypdf
XObject /DCTDecode. Marges : haut = 25 mm (titre+contenu), photo flottante coin
haut-droit à 16 mm, colonne texte rétrécie à droite sous la photo (pas de recouvrement).

## Sauvegarde / GitHub (Token hygiene)
- Compte GitHub = `Emma1208`. Depot public de reference : `cv-lettre-templates`
  (contient cv-master-template + lettre-motivation-template + variante-enseignant).
- SOURCE DE VÉRITÉ = `/root/cv_kakesa/` et `/root/lettre_motivation/`, PAS
  `~/.hermes/skills/*` (copies). Après correction, copier vers le skill AVANT push.
- TOKEN : `export GITHUB_TOKEN=...` dans le shell, `unset` après push ; jamais en
  fichier commité ni en mémoire Hermes.

## Vérification attendue après génération
- PDF : `pypdf` → XObject /Image présent, texte extrait contient "CURRICULUM VITAE" et
  les sections, PAS de '****' dans les numéros de référence.
- DOCX : dézipper, parser tout XML (document.xml + rels) avec xml.dom.minidom → doit passer ;
  vérifier `word/media/photo.jpeg` présent et `wp:anchor` (photo flottante).
