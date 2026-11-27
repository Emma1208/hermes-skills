# Style & mise en page de la LETTRE (validés par KAKESA, 2026-07-17)

Référence vivante : la lettre KPMG que l'utilisateur a approuvée
(`/root/linkedin_app/generer_lettre_kpmg.py` -> `Lettre_KPMG_KAKESA.odt/.pdf`)
et le template reproductible
`scripts/lettre_motivation_template.py`.

## GRILLE DE MISE EN PAGE (structure exacte)
1. **Expéditeur** : bloc en HAUT GAUCHE (nom, adresse, tel/email).
   Nom en gras ; reste en 11pt.
2. **Date** : en HAUT DROITE, SUR LA MÊME LIGNE que l'expéditeur.
   Réalisé via un `Table` 1 ligne × 2 colonnes SANS BORDURE
   (largeurs 60% / 40%). Un paragraphe `align=right` séparé tomberait
   SOUS l'expéditeur — le tableau est la méthode fiable.
3. **Destinataire** : EN DESSOUS, aligné à DROITE (3 lignes :
   attention DRH / structure / email).
4. **Objet** : à GAUCHE, gras navy, sur ~100mm de largeur.
5. **Corps** : justifié, pleine largeur. Interligne 0.26cm, fontsize 12pt.
6. **Formule de politesse** : en gras, à GAUCHE.
7. **Signature** : image manuscrite (référence vivante) en bas à DROITE,
   + nom tapé dessous (aligné à droite).

## STYLE (valeurs figées)
- Police : **DejaVu Sans** (odfpy) — garantit les accents fr.
- Corps : 12pt, justifié, `linespacing=0.26cm`, `marginbottom=0.25cm`.
- Expéditeur / destinataire : 11pt.
- Objet : 12pt **gras**, couleur NAVY = `#1F3350`.
- Formule de politesse : 12pt gras.
- Marges page : gauche/droite **1.6cm**, haut/bas **1.4cm**.
- 1 page MAX (jamais 2).

## COULEURS
- NAVY (titres/objet/signature tapée) : `#1F3350`
- Texte courant : noir `(30,30,30)`
- Signature image : bleue sur blanc (asset `assets/signature_seule.png`)

## ASSETS
- Signature : `/root/.hermes/skills/productivity/cv-job-application/assets/signature_seule.png`
  (copie miroir : `/root/Candidatures/Modèles/signature_seule.png`)
- Générateur KPMG validé : `/root/linkedin_app/generer_lettre_kpmg.py`
- Template réutilisable : `scripts/lettre_motivation_template.py`
  (modifier le bloc CONFIG en haut, lancer -> ODT + convertir en PDF)

## PITFALL (environnement actuel)
La conversion `soffice --headless --convert-to pdf` de l'ODT PERD l'image
de signature (0 image dans le PDF final). Donc :
- L'ODT éditable est correct (signature présente dans LibreOffice).
- Pour un PDF avec signature visible et garantie, générer la lettre en
  PDF DIRECT via fpdf2 (cf. `generer_lettre_orange_pdf.py`, et
  `references/lettre_kpmg_validee.md`).
- Ne JAMAIS affirmer « la signature est là » sur la seule vision :
  vérifier `fitz.open(pdf)[0].get_images(full=True)` (doit être >=1).
