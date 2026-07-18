# Candidature ciblée — dériver une variante sans écraser le template

Quand l'utilisateur veut un CV/lettre pour un poste précis (ex. enseignant,
comptable, logisticien), partir du template validé et en dériver une version
ciblée. RECETTE TESTÉE (session "enseignant") :

## Principe
- Garder le template de BASE intact (fichiers `cv_data.py` / `lettre_data.py`).
- Créer des fichiers séparés suffixés `_enseignant` (ou `_<poste>`).
- Ne FILTRE/REORDONNE que le réel (jamais inventer de données).

## Étapes (lettre)
1. `cp lettre_data.py lettre_data_enseignant.py` puis éditer (destinataire,
   objet, corps axés sur le poste ; garder la structure validée).
2. `sed 's/^import lettre_data as L$/import lettre_data_enseignant as L/' \
      make_lettre_pdf.py > make_lettre_pdf_enseignant.py`
   (idem pour make_lettre_docx.py)
3. Changer la ligne `OUT = "..."` dans les 2 variantes pour suffixer le nom
   (`..._ENSEIGNANT.pdf` / `..._ENSEIGNANT.docx`) -> SINON on écrase le PDF de base.
4. `python3 make_lettre_pdf_enseignant.py && python3 make_lettre_docx_enseignant.py`

## Étapes (CV)
1. `cp cv_data.py cv_data_enseignant.py` puis réordonner `parcours`/`competences`
   pour mettre l'expérience la plus pertinente en tête (ex. enseignement 1er).
2. `sed 's/^import cv_data as D$/import cv_data_enseignant as D/' \
      make_pdf.py > make_pdf_enseignant.py`
3. Changer `OUT` -> `CV_KAKESA_MUDIMBA_ENSEIGNANT.pdf`.
4. `python3 make_pdf_enseignant.py` (génère SANS photo).
5. `cp inject_photo_pdf.py inject_photo_pdf_enseignant.py` puis dans la copie
   remplacer `src` et `out` par `..._ENSEIGNANT.pdf` -> `python3 inject_photo_pdf_enseignant.py`.
   ⚠️ L'injecteur d'origine écrase le CV de base si on ne change pas src/out.

## Vérifications
- PDF : `pypdf` -> texte contient le nouvel objet ; photo présente si attendue
  (`'/PhotoX' in open(path,'rb').read().decode('latin1','ignore')`).
- DOCX : parser document.xml + rels avec xml.dom.minidom -> doit passer.
- PLUS AUCUNE trace de l'identité/objet de base dans la variante.
