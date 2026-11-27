---
name: rdc-admin-doc
description: Générer des documents administratifs officiels RDC (République Démocratique du Congo) au format A4 — procès-verbal / compte rendu de réunion, rapport d'activité / mission / mensuel / financier / inspection. Utiliser quand l'utilisateur demande un PV, compte rendu, rapport officiel, modèle RDC, document ministère/administration congolaise.
---

# rdc-admin-doc — Documents administratifs officiels RDC

Génère des PDF A4 officiels congolais (bandeau tricolore Bleu-Jaune-Rouge, en-tête
"RÉPUBLIQUE DÉMOCRATIQUE DU CONGO", devise "Paix - Justice - Travail", pied de page
réf + Page X/Y, sections numérotées, tableaux à double trait, blocs signatures/cachet).

## Prérequis (environnement déjà présent sur cette machine)
- `fpdf2` 2.8.7, `Pillow` 12.x, polices DejaVu dans `/root/linkedin_app/` (DejaVuSans*, DejaVuSerif*)
- Rendu/preview : `pdftoppm` (poppler) + `pdftotext` déjà installés
- IMPORTANT : accents FR corrects OBLIGATOIRES (jamais stripper é→e). fpdf2 + DejaVu gère l'UTF-8.

## Fichiers (déjà créés dans /root/linkedin_app/)
- `modele_administratif_rdc.py` = classe `DocumentAdministratifRDC(FPDF)` + helpers + `lire_config()`
- `generer_compte_rendu.py` = CLI procès-verbal / PV de réunion
- `generer_rapport.py` = CLI rapport (activité/mission/mensuel/financier/inspection)
- `exemple_compte_rendu.json`, `exemple_rapport.json` = configs de démo

## Usage CLI (le plus simple pour l'utilisateur)
```bash
cd /root/linkedin_app
python3 generer_compte_rendu.py config.json                 # -> PV_<ref>.pdf
python3 generer_compte_rendu.py config.json -o mon_pv.pdf
python3 generer_rapport.py config.json                      # -> RAPPORT_<ref>.pdf
python3 generer_rapport.py config.json -o mon_rapport.pdf
```
Config en JSON (ou YAML si PyYAML dispo). Tous champs optionnels sauf indiqué.

### Schéma compte rendu / PV (generer_compte_rendu.py)
```
entite, sous_entite, division, type_document, reference, lieu, date_texte,
heure_debut, heure_fin,
president:{nom,fonction},
participants:[{nom,fonction},...],
excusés:[...], ordre_du_jour:[...],
discussions:[{point,contenu},...],
decisions:[...], actions:[{action,responsable,echeance},...],
redacteur
```

### Schéma rapport (generer_rapport.py)
```
entite, sous_entite, division, type_document(DÉFAUT "RAPPORT D'ACTIVITE"),
reference, periode, lieu, date_texte,
destinataire, auteur:{nom,fonction},
resume, objectifs:[...], contexte,
activites:[{titre,description,indicateurs:[{indicateur,cible,realise}]},...],
resultats:[...], difficultes:[...],
tableau_synthese:{headers:[...],rows:[[...]]},   # optionnel
recommandations:[...], annexes:[...]
```

## Usage programmatique (DocumentAdministratifRDC)
```python
from modele_administratif_rdc import DocumentAdministratifRDC
doc = DocumentAdministratifRDC(entite="MINISTERE ...", type_document="PROCES-VERBAL",
                               reference="PV/2026/001", lieu="Kinshasa",
                               date_texte="Kinshasa, le 15 juillet 2026", serif=False)
doc.add_page(); doc.alias_nb_pages()
doc.section("IDENTIFICATION")          # niveau 1 = numérotation AUTO "1. ..."
doc.section("Sous-point", niveau=2)    # pas de numéro
doc.champ("Date", "...")               # libelle (gras) : valeur
doc.paragraphe("Texte justifié...")
doc.points([...])                      # puces
doc.numero_liste([...])
doc.tableau(headers, rows, col_widths=[...], align=[...])   # double trait + zebra
doc.bloc_signatures([{nom,fonction},...], colonnes=2)
doc.cachet_zone("Cachet et signature ...")   # carré en bas à droite
doc.output("f.pdf")
```
Helpers disponibles : `espace(mm)`, `champ`, `section`, `paragraphe`, `points`,
`numero_liste`, `tableau`, `bloc_signatures`, `cachet_zone`.

## PITFALLS (bugs résolus, à ne PAS refaire)
1. **Double numérotation des sections** : `section(titre, niveau=1)` incrémente
   automatiquement. Ne PAS passer déjà "1. TITRE" depuis le générateur — sinon
   numbering cassé (CONCLUSION ressort en "1."). `section()` est idempotent
   (détecte un titre déjà commençant par chiffre) MAIS la règle propre est :
   le GÉNÉRATEUR ne met JAMAIS de numéro, `section()` le fait.
2. **Référence qui chevauche le titre** dans `header()` : le `cell()` du titre
   doit utiliser `new_x=XPos.RIGHT` (pas `LMARGIN`) pour que la référence à
   droite se place à côté et non par-dessus.
3. **Tableaux multi-lignes** : utiliser `multi_cell(..., new_x=XPos.RIGHT,
   new_y=YPos.TOP)` et calculer la hauteur de ligne via split_only avant de
   dessiner, pour éviter le chevauchement des cellules. Gérer le saut de page
   manuellement (si y+rh > h-20 -> add_page + redessiner l'en-tête de tableau).
4. **Accents** : DejaVu gère l'UTF-8 ; ne rien encoder/stripper. Toujours
   `open(path, encoding="utf-8")` pour lire les configs JSON.

## VALIDATION (obligatoire avant de dire "fait")
L'utilisateur s'énerve si on corrige plusieurs fois la même mise en page. Donc :
1. Générer le PDF (python3 ...).
2. Rendre en PNG : `pdftoppm -r 110 -png f.pdf preview >/dev/null 2>&1`
3. Vérifier CHAQUE page avec `vision_analyze` (vision native) en demandant
   explicitement : chevauchements, débordements, numérotation, tableaux, signatures.
   (browser_vision ne marche PAS sur android-arm64 -> utiliser vision_analyze sur le PNG.)
4. Vérifier le texte extrait : `pdftotext f.pdf - | grep -E "^[0-9]+\. "`
5. Seulement après validation visuelle -> annoncer "fait" et livrer MEDIA:chemin.

## Extension rapide
Pour un nouveau type (ex: note de service, arrêté, circulaire) : ajouter une
fonction `build(cfg)` dans un nouveau `generer_xxx.py` qui réutilise
`DocumentAdministratifRDC` + ses helpers, et une config JSON exemple.
