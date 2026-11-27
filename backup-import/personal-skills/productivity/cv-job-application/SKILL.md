---
name: cv-job-application
description: Generate professional CV/resume PDFs (French, accents, fpdf2), connect to LinkedIn OpenID API, and run daily job-search crons matched to a user profile. Use when the user wants a CV built/edited, a LinkedIn connection, or automated job hunting.
---

# CV & Job Application Toolkit

Covers three linked tasks for a job-seeking user: (1) building/editing a CV PDF,
(2) connecting to LinkedIn via the official API, (3) running automated job-search
crons filtered to the user's profile.

## 1. CV PDF generation with fpdf2 (Python)

### CRITICAL user corrections (do NOT repeat these mistakes)
- **Never strip accents.** fpdf2 core fonts (Helvetica/Arial) are latin-1 only, so
  a naive `clean()` that maps é→e, è→e corrupts French text. ALWAYS embed a Unicode
  TTF (DejaVuSans) instead and keep the real accents. The user explicitly rejected
  the accent-stripped version.
- **No "généré automatiquement" footer.** User found it unprofessional. Remove the
  footer or make it neutral.
- **Photo: only if the user explicitly wants it, placed where THEY show in their
  reference doc.** Default is NO photo. When added, place it to match the user's
  existing .docx (e.g. beside contact block), not a generic top-right badge.
  - **EXCEPTION — offer MANDATES a photo:** if the job posting explicitly requires
    "CV avec photo" (KPMG RDC forms.office.com offer, 2026-07-16: "Votre dossier doit
    impérativement contenir ... un Curriculum Vitae (CV) avec photo"), ADD the photo
    EVEN THOUGH the user's default is no-photo. User confirmed this override live
    ("Non il faut que il ai de photos"). Photo asset: `/root/linkedin_app/photo_docx.png`
    (150x200 portrait). Place it TOP-RIGHT INSIDE the navy header band (recipe):
    ```python
    from PIL import Image as _PIL
    sig = "/root/linkedin_app/photo_docx.png"
    _iw, _ih = _PIL.open(sig).size
    H = 30  # header height (mm)
    ph = H - 4; pw = ph * _iw / _ih
    pdf.image(sig, x=210 - pw - 4, y=2, w=pw, h=ph)
    ```
    Keep header text on the LEFT so it does not overlap the photo. (This is the only
    standing exception to the no-photo rule — never add a photo otherwise.)
- **Legibility:** body text size 13 minimum. User rejected small text.
- **File naming (FINAL convention):** the general/reference CV is
  `CV_KAKESA_MUDIMBA.pdf` (NO "Emmanuel", NO lowercase). Targeted CVs append the
  post/offer: `CV_KAKESA_MUDIMBA_Comptable.pdf`, `CV_KAKESA_MUDIMBA_HYGroup.pdf`.
  Keep the `pdf.output(...)` path in each generator script in sync with this convention.
- **Living reference CV (workflow rule):** `CV_KAKESA_MUDIMBA.pdf` is the user's
  LIVING reference. Update it whenever new experience appears, and always DERIVE
  targeted CVs FROM it.

### Unicode font setup
Core fonts can't render é/è/à/ç. Embed DejaVuSans:
```python
pdf.add_font("DJ","","/path/DejaVuSans.ttf")
pdf.add_font("DJ","B","/path/DejaVuSans-Bold.ttf")
pdf.add_font("DJ","I","/path/DejaVuSans-Oblique.ttf")
```
DejaVu lives in Termux: `/data/data/com.termux/files/usr/share/fonts/TTF/`
(copy to your working dir first). Use "DJ" family for ALL text.

### Rich formatting (user chose option "C": highlight, keep keyword text UNCHANGED)
- Dates in bold + navy (NAVY=(20,40,80)). Detect with regex `^\d{4}` or French
  month names. This is the ONE element that stays bold.
- Job titles: bold navy + a drawn underline line (`pdf.line(x1, y, x2, y)`) — because
  `set_underline()` does NOT exist in this fpdf2 version.
- Bullets: dash ("—") in accent/navy color, text indented + aligned.
  - **TypeError pitfall (2026-07-16):** `bullet()` has signature `bullet(text, size=13, lh=6)`
    and does NOT accept a `keywords=` kwarg. Calling `bullet("...", keywords=set())` raises
    `TypeError: bullet() got an unexpected keyword argument 'keywords'`. To force plain-black
    text inside a bullet, either drop the kwarg (default `KEYWORDS` set renders keywords
    black anyway via kw_bold=False) or use `para(text, keywords=set(), x_indent=6)` instead.
    (Contrast: `para()` DOES accept `keywords=set()`.)
- **fpdf2 image insertion — NO `fpdf.drawing` import (2026-07-16):** `from fpdf.drawing
  import Frame, DrawImage` raises `ImportError: cannot import name 'Frame' from 'fpdf.drawing'`
  in this fpdf2 version. Insert an image with `pdf.image(path, x=..., y=..., w=...)` directly
  (size by WIDTH; height auto-scales from aspect ratio). Do NOT wrap in Frame/DrawImage.
  To right-align an image: compute `x = pdf.w - pdf.r_margin - width_mm`. Used for both the
  KPMG photo (top-right in header) and the handwritten signature (bottom-right).
- **Keyword styling — FINAL:** keywords render in BLACK, no bold (kw_bold=False,
  kw_color=DARK). Default in template is black/no-bold; only dates emphasized.
- **Header text = "Curriculum Vitæ"** (NOT the user's name).
- **Section III title = "DOMAINES DE COMPÉTENCE À ÉVOLUER"**.
- **Prénom display:** user wants ONLY "Dieudonné" in the Infos perso Prénom field.
### End-of-CV honor declaration + signature (FINAL fpdf2 CV convention, validated 2026-07-16)
After the last section (Références) on the **fpdf2 targeted CV**:
- serment italic LEFT; "Fait à Kinshasa, le JJ/MM/AAAA" RIGHT; signature = the user's
  HANDWRITTEN IMAGE (référence vivante) placed bottom-RIGHT; typed name below, RIGHT.
- **NO "Signature :" prefix line** on the fpdf2 CV (user: "Supprimer : signature : remplacer
  le signature référence vivante"). The name sits directly under the image.
- Recipe that fits in 2 pages (tighten spacing BEFORE the block, see orphan-word pitfall):
  ```python
  from datetime import date
  pdf.ln(0.5)
  pdf.set_x(pdf.l_margin); pdf.set_font("DJ","I",12); pdf.set_text_color(*DARK)
  pdf.multi_cell(0,6,"Je jure sur mon honneur que les informations ci-dessus sont vraies et exactes.",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
  pdf.set_font("DJ","",12)
  pdf.multi_cell(0,5,"Fait à Kinshasa, le "+date.today().strftime("%d/%m/%Y"),
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
  pdf.ln(0.5)
  SIG="/root/Candidatures/Modèles/signature_kakesa.jpg"   # handwritten ref image
  pdf.image(SIG, x=pdf.w - pdf.r_margin - 42, w=42)      # bottom-right, ~21mm tall
  pdf.ln(0.5)
  pdf.set_font("DJ","B",13)
  pdf.multi_cell(0,5,"KAKESA MUDIMBA Dieudonné", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
  ```
- **DISTINGUISH — the ODT editable CV (§1d) uses the TYPED "Signature :" + name block, NOT
  the image.** The fpdf2 CV uses the IMAGE. Do NOT cross-contaminate the two.
- Asset: `/root/Candidatures/Modèles/signature_kakesa.jpg` (blue handwritten sig extracted
  from a phone screenshot). Keep it saved there; reuse for every fpdf2 CV/letter.

### Building a TARGETED CV from the reference (procedure — used for BSF/Flash)
1. `cp generate_cv.py generate_cv_<OFFER>.py` (e.g. `generate_cv_flash.py`).
2. Change the header subtitle to the target post:
   `pdf.cell(0,6,"Candidat au poste de <INTITULÉ> — <EMPLOYEUR>", ...)`
   Keep "Curriculum Vitæ" as the title line above it.
3. Add an **Adéquation au poste** section mapping real experiences to the offer's
   stated requirements. Each para with `keywords=set()` so it renders black.
4. Change `pdf.output(...)` to `CV_KAKESA_MUDIMBA_<OFFER>.pdf`.
5. **CV page count — 2 PAGES MAX by default (CORRECTED 2026-07-16).** The user's standing
rule is now: a CV may run up to **2 pages**; produce ONE page only if he explicitly asks for it
or the content is genuinely short. He explicitly rejected a silent compress-to-1-page attempt
with "Non ma préférence est deux pages maximum par défaut". **Do NOT silently compress a 2-page
CV to 1 page.** When a 2-page CV threatens a 3rd page, compress GEOMETRY first (margins, gaps,
condense références to one-line bullets), never below 13pt for the master fpdf2 CV. The old
"1 page A4, NOT 2" rule is REVOKED — treat 2 pages as the norm. (Historical note: the MSF
*Agent d'entretien* 2-page request of 2026-07-15 was an early signal of this preference.)
The official letter (§1b) stays ONE page — that rule is unchanged.
If a 1-page IS explicitly requested and it overflows:
   compress GEOMETRY first, never below 13pt body: tighten header (rect h≈19-22mm),
   section gaps to ~0.3-0.5mm, body line-height ~4.8, margins 14mm, condense références
   to 3-4 one-line entries (name — role — contact), merge small sections (Formations +
   Langues). Hit this: the master CV needed 3 passes (2 pages → compress → 1 page) using
   LH=4.8, size=13, margins 14/10/14, header rect 19mm. Verify with `pdfinfo`/`fitz`
   page_count == 1. Legibility (>=13pt) is non-negotiable.
- **Orphan-word / page-break pitfall (2026-07-16):** when a 2-page CV spills one LAST WORD
  of a paragraph onto a 3rd page (e.g. "rapports" ends page 1, "financiers." alone on page 3),
  do NOT trust vision alone — it may show the word as "cut off at the bottom edge" but the
  real defect is a paragraph-split across pages. Verify with `pdftotext -layout f.pdf -` and
  look for a `\f` splitting one word ("...préparation de rapports" then "financiers."). FIX by
  tightening spacing so the whole paragraph stays on the previous page: reduce `para(..., lh=6)`
  → `lh=5.5` on the parcours entries, shrink `pdf.ln(1)` gaps → `pdf.ln(0.5)`, and reduce
  `ref()` line-height from 6→5. Gain a few mm; the last word pulls back onto page 2. Re-check
  `pdftotext` shows the full sentence ending page 1 and the next section starting page 2.
  Never let a CV run to 3 pages when 2 is the cap.

   ### 1d. Modèle CV vierge ÉDITABLE (.odt via odfpy) — pour remplissage manuel
   Le générateur fpdf2 (§1) produit un PDF *figé*. Quand l'utilisateur veut un **modèle
   vierge qu'il remplit lui-même** (poste "opérateur de saisie", variantes à la main),
   génère un `.odt` LibreOffice éditable avec champs `[à remplir]`.
   - Script réutilisable : `scripts/generer_cv_modele_vierge.py`
   (`python3 generer_cv_modele_vierge.py [sortie.odt]`). `pip install odfpy` requis.
   - Style identique à la référence : bandeaux bleu marine (NAVY="#142850"), sections I→VII,
   corps 12pt, champs placeholder en `[CROCHETS]`. Pas de photo, accents OK (DejaVu via LO).
   - **Deux PIÈGES odfpy** (déjà levées) : (1) `page-width`/`page-height` INTERDITS sur
   `doc.text` → on les omet ; (2) `spacebefore`/`spaceafter` INTERDITS dans
   `ParagraphProperties` → on utilise `marginleft`/`marginright` + `padding`. Attributs
   valides : `backgroundcolor, padding, marginleft, marginright` (para) ; `color, fontsize,
   fontweight, fontfamily` (texte). Détail + vérif visuelle : `references/odt_blank_template.md`.
   - Vérification obligatoire (règle utilisateur) : `soffice --headless --convert-to pdf`,
   `pdftoppm`, puis `vision_analyze` avant de dire « fait ».
   - **Signature tapée (mode basique, 2026-07-16) :** quand l'utilisateur demande
   "ajouter la signature et mon nom en bas" sur le .odt rempli, ajoute sous le serment :
   une ligne `Signature :`, une ligne vide, puis une ligne `KAKESA MUDIMBA Dieudonné`
   (corps 12pt, navy ou noir). C'est le bloc signature *typé* (pas l'image manuscrite §4c) —
   approprié pour un doc qu'il remplit/imprime lui-même. Garde le doc sur ≤2 pages (§5).
   - **ALIGNEMENT DU BLOC SIGNATURE (convention validée 2026-07-16) :** le serment
   « Je jure sur mon honneur… » reste à **GAUCHE** ; seuls **« Fait à Kinshasa, le
   JJ/MM/AAAA » + « Signature : » + « KAKESA MUDIMBA Dieudonné »** vont à **DROITE**
   (utilisateur : « Fait à Kinshasa+date, signature, nom doivent être à droite »).
   Pour le style right-align → `references/odt_blank_template.md` §3 (helper + piège
   « ligne longue lue comme centrée »). Vérif troncature de fin de ligne → §4.
   - Le modèle rempli livré cette session : `/root/Candidatures/Modèles/CV_KAKESA_MUDIMBA_rempli.odt`
   + `.pdf` (2 pages, signature tapée en bas — référence vivante du format éditable).

   #### 1e. Lettre de demande d'emploi ÉDITABLE (.odt via odfpy) — ciblée offre
   Quand l'utilisateur veut la LETTRE (pas le CV) en .odt LibreOffice éditable +
   PDF, génère-la avec odfpy (même esprit que §1d). Générateur réel livré :
   `/root/linkedin_app/generer_lettre_kpmg.py` →
   `/root/Candidatures/Modèles/Lettre_KPMG_KAKESA.odt` + `.pdf`.
   Boilerplate réutilisable + recette 1 page : `references/odt_lettre_recipe.md`
   (pitfalls MasterPage="Standard", odf.draw, setAttribute + verify avec pdftotext).
   **3 pièges odfpy OBLIGATOIRES (tous heurtés 2026-07-17) :**
   - **MasterPage DOIT s'appeler `"Standard"`** pour être la page par défaut. Un autre
     nom ("MP_Lettre") est ignoré → les marges ne s'appliquent pas et la lettre
     déborde en 2 pages. `mp = MasterPage(name="Standard", pagelayoutname="PL_x")` puis
     `doc.masterstyles.addElement(mp)` (PAS `automaticstyles` → `IllegalChild`).
     Le `PageLayout` (marges) va lui dans `doc.automaticstyles.addElement(pl)`.
   - **Frame + Image viennent de `odf.draw`** : `from odf.draw import Frame, Image as
     ODImage`. `odf.graphic` et `fpdf.drawing` n'existent pas ici. Pour insérer la
     signature : `fr = Frame(width="6cm", height="2.2cm", anchortype="paragraph")` puis
     `fr.addElement(ODImage(href=IMG, type="simple", show="embed", actuate="onLoad"))`
     puis `doc.text.addElement(fr)`. PAS d'attribut `textalign` sur `draw:frame`
     (le droit se gère via le paragraphe parent, style `textalign="right"`).
   - **`Style` utilise `setAttribute`, pas `addAttribute`** : `s.setAttribute(
     "parentstylename", kw["parent"])`. `addAttribute` lève `AttributeError`.
   - **Recette 1 page (validée) :** marges 1.6/1.4cm via PageLayout ; `st_base`
     `linespacing=0.26cm`, `marginbottom=0.25cm`, fontsize 12pt ; bandeau bleu
     (ParagraphProperties `backgroundcolor` NAVY, texte blanc gras) ; supprimer tout
     paragraphe redondant avec la formule de politesse (le saut de page se fait AU
     MILIEU d'un paragraphe → vérifier avec `pdftotext -layout` que la page 2 est
     vide, pas avec la vision seule). Signature image en bas à droite + nom tapé dessous.
   - **EN-TÊTE : expéditeur GAUCHE + DATE DROITE (même ligne)** — recette validée
     2026-07-17 (offre KPMG). Le bloc destinataire va EN DESSOUS à droite. Pour
     aligner la date à droite SUR LA MÊME LIGNE que l'expéditeur, un `Table` 1 ligne ×
     2 colonnes SANS BORDURE est la méthode fiable (un paragraphe `align="right"`
     séparé tombe sous l'expéditeur, pas à côté). Recette :
     ```python
     from odf.table import Table, TableRow, TableCell, TableColumn
     from odf.style import TableProperties, TableCellProperties, TableColumnProperties
     from odf.text import P as OP
     # style tableau sans bordure
     st_tbl = Style(name="Tbl_Ent", family="table")
     stp = TableProperties(); stp.setAttribute("width","100%"); st_tbl.addElement(stp)
     doc.styles.addElement(st_tbl)
     # style cellule sans bordure (border VA sur table-cell, PAS sur table)
     st_cell = Style(name="Cell_Ent", family="table-cell")
     scp = TableCellProperties(); scp.setAttribute("border","none"); st_cell.addElement(scp)
     doc.styles.addElement(st_cell)
     # COLONNES : SANS ça, la 2e cellule (date) NE REND PAS (silencieux)
     csg = Style(name="Col_G", family="table-column")
     cgp = TableColumnProperties(); cgp.setAttribute("columnwidth","60%"); csg.addElement(cgp)
     doc.styles.addElement(csg)
     csd = Style(name="Col_D", family="table-column")
     cdp = TableColumnProperties(); cdp.setAttribute("columnwidth","40%"); csd.addElement(cdp)
     doc.styles.addElement(csd)
     tbl = Table(name="Entete", stylename="Tbl_Ent")
     tc1 = TableColumn(numbercolumnsrepeated=1); tc1.setAttribute("stylename","Col_G"); tbl.addElement(tc1)
     tc2 = TableColumn(numbercolumnsrepeated=1); tc2.setAttribute("stylename","Col_D"); tbl.addElement(tc2)
     tr = TableRow()
     c1 = TableCell(stylename="Cell_Ent")
     c1.addElement(OP(stylename=st_coord, text="KAKESA MUDIMBA Dieudonné"))
     c1.addElement(OP(stylename=st_coord, text="N° 3, Avenue Tungila, ..."))  # adresse/tel sous le nom (gauche)
     tr.addElement(c1)
     c2 = TableCell(stylename="Cell_Ent")
     c2.addElement(OP(stylename=st_date, text="Kinshasa, le "+date.today().strftime("%d/%m/%Y")))  # droite
     tr.addElement(c2)
     tbl.addElement(tr); doc.text.addElement(tbl)
     # destinataire EN DESSOUS, style st_dest textalign="right"
     ```
   - **PITFALLS odfpy Table (tous heurtés 2026-07-17) :**
     * `TableProperties` N'ACCEPTE PAS `border` → `AttributeError: border not allowed in
       <style:table-properties>`. Le bordure se règle via `TableCellProperties` avec
       `border="none"` sur un style `family="table-cell"` appliqué aux cellules.
     * **SANS `TableColumn` + `TableColumnProperties` `columnwidth`, la 2e cellule
       (date) NE REND PAS** — le PDF montre seulement l'expéditeur à gauche et
       aucune date. Toujours déclarer les 2 colonnes (largeurs 60/40).
     * `Table`/`TableRow`/`TableCell` viennent de `odf.table` ; `TableProperties`/
       `TableCellProperties`/`TableColumnProperties` de `odf.style`.
     * Vérifier le rendu avec `pdftotext -layout` (la date doit apparaître à droite
       de la 1re ligne), pas seulement la vision.
   - **KPMG RDC offre (2026-07-16/17) — conventions figées :** email
     `CD-Recrutement@kpmg.com` ; nom de fichier CV IMPOSÉ
     `CV_KAKESA_MUDIMBA_AD Audit.pdf` (renommer avant envoi) ; lettre + CV
     requis ; photo OBLIGATOIRE (« CV avec photo ») ; date limite **27/07/2026**.
     Letter KPMG livrée : `/root/Candidatures/Modèles/Lettre_KPMG_KAKESA.odt`+`.pdf`
     (générateur `/root/linkedin_app/generer_lettre_kpmg.py`). CV KPMG :
     `/root/linkedin_app/CV_KAKESA_MUDIMBA_KPMG.pdf` (générateur
     `/root/linkedin_app/generer_cv_kpmg_cible.py`, 2 pages, photo + signature image).
   - **Style cohérent CV** : bandeaux bleu marine, objet en gras navy, corps justifié.

   #### 1f. HTML → LibreOffice headless (one-shot ODT éditable + PDF) — ALTERNATIVE la plus robuste
   Quand l'utilisateur veut un CV/lettre ÉDITABLE `.odt` + PDF (profil « opérateur de saisie »),
   l'approche **HTML → soffice** est PLUS SÛRE que odfpy (§1d/§1e) : elle évite TOUTES les
   trappes odfpy (MasterPage doit être « Standard », `TableColumn` obligatoire sinon la 2e cellule
   ne rend pas, `Frame`/`odf.draw`, `setAttribute` vs `addAttribute`). **Un seul fichier HTML source
   produit .odt + .pdf en une passe**, et l'ODT reste pleinement éditable dans LibreOffice.
   - **Recette validée (session COOPI Nutritionniste terrain, 2026-07-17) :**
     1. Écrire un `.html` autonome, UTF-8, avec `<style>` inline (marges via `@page`,
        corps ≥13px pour le CV / ≥12px pour la lettre, accents tels quels). Modèle réutilisable :
        `templates/cv_html_to_odt_template.html` (copier → remplir les zones `/* À REMPLIR */`).
     2. Convertir (deux appels) :
        ```bash
        soffice --headless --convert-to odt --outdir <DIR> fichier.html
        soffice --headless --convert-to pdf --outdir <DIR> fichier.html
        ```
     3. **VÉRIFIER le rendu (règle utilisateur) :** `pdftoppm -png -r 90 f.pdf p.png` puis
        `vision_analyze` (lisibilité, accents corrects, aucun chevauchement, page-break propre).
        This session : la vision a signalé « affection visée » → corriger en « affection » dans le HTML.
   - **AVANTAGES vs odfpy :** pas de XML fragile ; alignement « expéditeur GAUCHE + date DROITE »
     géré nativement par CSS (`display:table` / `float` / `text-align:right`) ; saut de page via
     `page-break-before: always` en CSS (fiable, contrairement au saut odfpy au milieu d'un paragraphe).
   - **PIÈGES :**
     * soffice convertit en filtre « Writer/Web » (`writerweb8_writer`) — NORMAL, l'ODT reste éditable.
     * Ne PAS injecter de footer « généré automatiquement » (règle utilisateur).
     * Accents : écrire le HTML en UTF-8 (`<meta charset="utf-8">`) — ils passent intacts (vérifié).
     * Pour l'alignement droite/gauche, préférer **flux normal + tableau CSS** plutôt que
       `position:absolute` (fragile à la conversion). Ex. bloc destinataire : `<table>` 1 ligne ×
       2 colonnes sans bordure (expéditeur gauche, date droite `text-align:right`).
     * Si débordement de page : ajuster `margin` `@page` + tailles dans le CSS, relancer la conversion
       (pas de refonte du générateur). Garder ≥13px (CV) / ≥12px (lettre) — lisibilité non négociable.
   - **Nommage :** `CV_KAKESA_MUDIMBA_<OFFRE>.{html,odt,pdf}` ;
     `Lettre_<OFFRE>_KAKESA.{html,odt,pdf}`. Garder le `.html` comme source « vivant » (modifiable +
     régénérable), produire .odt/.pdf à la demande.
   - **PIVOT hors-profil** : cette voie a été utilisée pour COOPI Nutritionniste terrain (poste
     nutrition, profil comptable/finance) — voir « Hors-profil pivot » ci-dessous pour le contenu
     (expérience MSF PUC MED EN TÊTE, section « COMPÉTENCES TRANSFÉRABLES AU POSTE », jamais inventer
     de diplôme non possédé). Même HTML/CSS, seul le corps change.

   #### 1g. RÈGLE ABSOLUE — éditer le MODÈLE RETENU en place (PAS de nouveau layout)
   Quand l'utilisateur parle du « modèle que nous avons retenu » / « modèles des CV, références
   vivantes », il désigne LES `.odt` canoniques DÉJÀ VALIDÉS dans `~/Candidatures/Modèles/`
   (`CV_KAKESA_MUDIMBA_rempli.odt`, `Lettre_Modele_KAKESA.odt` — sous-titre « Comptable /
   Gestion Financière / Audit / Enseignant », sections I→VII, mêmes références). LE CONTRAT :
   garder CETTE mise en page à l'identique et ne changer QUE le texte dedans.
   - **NE JAMAIS** générer un nouveau layout (HTML/CSS maison, fpdf2 from scratch, odfpy neuf)
     pour une offre « normale » — l'utilisateur a rejeté violemment un CV refait de zéro
     (« pourquoi est-ce que tu fais des choses sans réfléchir ? »). Même la voie HTML→ODT (§1f)
     ne sert QUE si le modèle retenu N'EXISTE PAS encore ; sinon, ÉDITER le retenu en place.
   - **Méthode validée (session COOPI Nutritionniste terrain, 2026-07-17) — édition IN PLACE :**
     1. Copier le modèle retenu dans le dossier de travail (ex `/root/Candidatures/Brouillons/`).
     2. `unzip -p MODELE.odt content.xml | sed 's/<[^>]*>/ /g'` pour lire le texte réel — les
        chaînes à remplacer sont dans des `<text:span>...</text:span>` ; styles/sections/serment
        NE bougent pas.
     3. Remplacer les `<text:span>` EXACTS par le texte ciblé (échapper `& < >` en
        `&amp; &lt; &gt;` dans le XML). Garder titres de section, styles, références INTACTS.
     4. Re-zipper (même arbo que le .odt d'origine) → .odt édité.
     5. `soffice --headless --convert-to pdf` puis `pdftoppm` + `vision_analyze` pour vérifier
        (lisible, accents OK, structure I→VII préservée).
   - **Script réutilisable** : `scripts/edit_odt_template.py` fait clonage + remplacement in-place
     en une passe (JSON `--map` ou paires `--replace "ancien||nouveau"`). Il WARN (sans planter)
     si une chaîne est introuvable — corrige le mapping au lieu de livrer l'ancien texte. Ex. COOPI :
     ```bash
     python3 scripts/edit_odt_template.py \
       --src /root/Candidatures/Modèles/CV_KAKESA_MUDIMBA_rempli.odt \
       --out /root/Candidatures/Brouillons/CV_COOPI_Nutritionniste_KAKESA.odt \
       --replace "Comptable / Gestion Financière / Audit / Enseignant||Candidature — Nutritionniste terrain · Avis COOPI RDC N° 001/JUILLET 2026" \
       --replace "— Analyse financière et prise de décision  |  Audit, contrôle interne et gestion des risques||— Logistique & suivi de stock (exp. MSF)  |  Gestion de la chaîne du froid et distribution de matériel"
     ```
   - **Cas « hors-profil » (ex nutrition avec profil compta) :** on garde AUSSI le modèle retenu,
     on ne change QUE le texte (sous-titre + section compétences reformulée vers le poste, +
     paragraphe « compétences transférables » dans la lettre). On n'invente AUCUN diplôme non
     possédé — on met en avant l'expérience MSF PUC MED (logistique/stock) et l'ancrage local
     (originaire d'Ituri/Bunia = zone d'affectation, Lingala bilingue).

   #### Hors-profil pivot (offer in a DIFFERENT job family)
When the offer does NOT match the user's core profile (e.g. comptable applying to
MSF **Cuisinier·ère Réserviste**), DO NOT force-finance the CV. Pivot on the ONE bridge:
shared employer / transferable experience. Concrete recipe that worked (MSF Cuisinier, 15/07/2026):
- Put the **shared-employer experience FIRST** in the parcours (here: `Agent d'appui logistique,
  projet PUC MED de MSF` moved ABOVE the comptable roles) and reframe it in the offer's vocabulary
  (suivi de stock → contrôle des stocks alimentaires; chaîne du froid → denrées; hygiène/conformité).
- Add a dedicated **"ATOUTS POUR LE POSTE DE <INTITULÉ>"** section (bold keyword-styled bullets,
  keywords=set()) mapping transferable skills to the offer's stated responsabilités:
  hygiène/sécurité, contrôle de stock/inventaire, ponctualité/rigueur, langues (FR/Lingala →
  menus selon différences culturelles), connaissance de l'employeur, esprit d'équipe/réserviste.
- Keep an MSF reference (here DRH MSF Belgique) — it reinforces the shared-employer bridge.
- Letter: same pivot — open with attachment to MSF values, lead body with the PUC MED/MSF
  experience reframed for the kitchen/logistics-alimentaire mission, close on flexibilité/réserviste.
- Keep 1 page, accents, 13pt min, signature vivante — all UNCHANGED from the master spec.
File examples: `/root/linkedin_app/generate_cv_cuisinier.py`, `generer_lettre_cuisinier.py`
(branch FROM the master/lettre-generale templates, edit only CONFIG + the pivot sections).
See `references/targeted_cv_procedure.md` for the full BSF example.

## 1b. Official cover-letter (FORMAT OFFICIEL / administrative)

The standing FINAL spec is the **100mm-block official format**. Anchor BLK=100mm.
Right edge of every right-placed block is x=185mm (25mm margin).

- **Marges** 25mm. **Expéditeur** (haut gauche, <=100mm, commune on its OWN line).
- **Date** (haut droite): RIGHT-ALIGNED to right margin. `KINSHASA, JJ / MM / AAAA`.
- **Objet** (LEFT, width <=100mm via `multi_cell(100,6,...,new_x=LMARGIN)`,
  overflow continues BELOW same column).
- **Destinataire** (RIGHT BLOCK, all lines START at x=100mm, left-aligned within block):
  `A MONSIEUR LE DIRECTEUR` / `DES RESSOURCES HUMAINES` / `DE [ORG]`, then
  `KINSHASA / [COMMUNE]` UNDERLINED below the text (draw line at `y2 + 6 + 1.5`,
  NOT `y2 + 1.5`).
- **Formule d'appel** (RIGHT-aligned, ends at 185mm): `Monsieur le Directeur,`.
- **Corps**: justified, full width (160mm → ends x=185). ONE page (tighten to 5/4.8
  line-height if needed).
- **Politesse finale**: line 1 right-aligned, line 2 at LEFT.
- **Signature** (RIGHT block at x=100mm, ALL CAPS): `KAKESA MUDIMBA DIEUDONNE`.
- **Typo**: serif (DejaVuSerif TTF), 11pt. CAPS for Expéditeur + Objets + Organisation +
  Ville + Signature.

### Living reference letter
Validated base (`modele_lettre_generale.py`, working dir `/root/linkedin_app/`) with a
CONFIG block at top. For each offer/person: COPY it → `generer_lettre_<OFFER>.py`, edit
ONLY the CONFIG, regenerate. Branch, never build from scratch.

### PITFALL — minimal targeted edit (FIRST-CLASS)
When the user asks to change ONE element, change ONLY that element. If you must touch a
sibling block for consistency, ASK or do it as a SEPARATE explicit step — never silently
cascade. Example: user said "à la formule d'appel, supprimer madame" — do NOT also edit
the destinataire block.

## 1c. Batch generation — one master CV + N personalized letters (MULTI-OFFER)
When the user says "prépare CV et lettres pour toutes ces offres" / wants to apply to
several offers from a single cron run, do NOT copy the letter template N times. Use ONE
script with an OFFRES list and a `generer(o)` function:
- Build **one master CV** (reusable `generer_cv_master.py` → `CV_KAKESA_MUDIMBA_MASTER.pdf`)
  and **N letters** from a list of dicts. The CV is shared; only the letter body is per-offer.
- OFFRES dict shape: `{poste, structure, loc, url, corps:[...]}`. Loop `generer(o)` →
  `Lettre_<SLUG>.pdf`. Slug = first word of structure + first word of poste, sanitized.
- Reuse the §1b official 100mm-block layout + `inserer_signature` inside `generer()`.
- Full working example: `/root/linkedin_app/generer_lettres_batch.py` (11 offers, all 1 page).
- Reusable template: `scripts/batch_lettres_offres.py` in this skill dir (copy → fill OFFRES).
See `references/multi_offre_workflow.md` for offer-sourcing + filtering detail + verification.

### Offer sourcing & filtering (BEFORE generating)
The daily cron dumps matches to `/root/linkedin_app/offres_brutes.json` (60+ entries) and
`logs/jobs_YYYY-MM-DD.txt`. Most entries are AGGREGATOR pages (Optioncarriere, EgoZola,
Congojob, Emploi.cd, UNjobs) or DUPLICATES — not real offers. Extract only CONCRETE postings
(named post + employer, ideally with a deadline). Then drop EXPIRED ones by reading the body
for `Date limite` / `au plus tard le` dates. Example on 2026-07-15 expired: VillageReach
(10/07), DRC GOLD (08/05), Equity BCDC Finance Manager (15/06). Concrete live offers that day:
CICR Responsable Comptable, Equity BCDC Auditeur Senior, BSF Responsable Support,
ONEM Auditeur Interne Assistant + Responsable Audit Interne, ADPI-RDC Comptable,
eGoZola #40671 Comptable, AMI-RDC/BAfD Assistante-Comptable, L'Elite Directeur Audit Interne,
Julisha/PwC Comptable Senior, COREF Consultant INS RDC. → 11 letters generated from 1 script.

## 2. LinkedIn OpenID Connect connection
- Create app at linkedin.com/developers; need a Company Page.
- Add product "Sign In with LinkedIn using OpenID Connect" (free, no validation).
- Redirect URI must be added; Scope `openid profile email`. `/v2/userinfo` returns ONLY
  basic profile (name, email, picture) — NOT experiences/contacts/job search.
- Manual OAuth mode needed from a phone (print auth URL, user pastes `code=`).
- Browser automation of LinkedIn is BLOCKED on Android.
- Store Client ID/Secret in local config.json, never plaintext memory.

## 2b. LinkedIn profile read (user API connection LIVE)
Credentials in `/root/linkedin_app/config.json`. Token valid ~60 days; re-auth if expired.
`/v2/userinfo` returns basic profile only.

## 3. Daily job-search cron
- LinkedIn/Indeed BLOCK scraping. Use **DuckDuckGo HTML POST**
  (`https://html.duckduckgo.com/html/` with `urllib.parse.urlencode({'q':...})` as POST).
- Filter by profile keywords; score/sort by match count.
- Cron script in `~/.hermes/scripts/`; set `workdir`; `deliver` to target chat.
- A/B/C/D summaries, result-first, French, no tables (user preference).

### Filtering ACTIVE offers
Most surfaced offers are EXPIRED. Read the detail page for `Date limite`; parse
`(\d{1,2})/(\d{1,2})/(\d{4})` or French month; compare to today. Build a profile-fit
grid (✅/⚠️/❌) and a one-line verdict. Lead with eligibility.

## 4. Sending the dossier by email (Gmail SMTP)

> **🚨 RÈGLE ABSOLUE — VALIDATION AVANT ENVOI (utilisateur, 2026-07-17).**
> Tu PREPARES toujours CV + lettre, tu les PRÉSENTES (extrait texte + vision du PDF),
> et tu ATTENDS son « OK, envoie » EXPLICITE. **JAMAIS d'envoi automatique à son nom**
> — même si `candidature_auto.py` le permet, ne lance pas l'envoi sans accord préalable.
> L'utilisateur a été TRÈS IRRITÉ qu'une candidature Orange parte sans sa validation.
> Le CC Gmail (kakesamudimba@gmail.com) reste requis QUAND il valide l'envoi.
> Workflow correct : générer → montrer le contenu → attendre accord → envoyer avec `--cc`.
> Cette règle est une PRÉFÉRENCE UTILISATEUR durable, pas un détail de session.

```python
import smtplib, ssl
from email.message import EmailMessage
EXP, PWD, TO = "kakesamudimba@gmail.com", APP_PASSWORD, "TARGET@gmail.com"
msg = EmailMessage()
msg["From"], msg["To"] = EXP, TO
msg["Subject"] = "Candidature - <POSTE> - KAKESA MUDIMBA Dieudonné"
# optional CC (user wanted a copy to his own Gmail): msg["Cc"] = "kakesamudimba@gmail.com"
msg.set_content("Madame, Monsieur,\n\nVeuillez trouver ci-joint mon CV et ma "
                "lettre de motivation pour le poste de <POSTE>.\n\nCordialement,\n"
                "KAKESA MUDIMBA Dieudonné\nTél : (+243) 818 491 601")
for f, n in [(CV,"CV_KAKESA_MUDIMBA_<OFFER>.pdf"),
             (LETTRE,"Lettre_Motivation_<OFFER>.pdf")]:
    with open(f,"rb") as fh: msg.add_attachment(fh.read(),
        maintype="application", subtype="pdf", filename=n)
ctx = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
    s.login(EXP, PWD); s.send_message(msg)
```

### CRITICAL pitfall — Gmail App Password
A normal Gmail password does NOT work with SMTP when 2FA is on
(`SMTPAuthenticationError(534, '5.7.9 Application-specific password required')`).
Ask the user to generate a 16-char **App Password** at
https://myaccount.google.com/apppasswords. Never store it in memory or config.

### AUTO-CANDIDATURE PACK (multi-PJ, per-offer assembly)
In `/root/linkedin_app/`:
- `dossier_candidats.json`: manifest mapping candidate → {nom, email, tel,
  documents:{key:path}}. Profils: `general`, `clientele`, `bsf`, `flash`, `comptable`,
  each pointing to a CV generator + letter generator/output.
- `candidature_auto.py`: for `--profil X --to ADR --sujet "..."`, it (1) regenerates the
  targeted CV, (2) regenerates the targeted letter, (3) sends BOTH as attachments via
  Gmail SMTP App Password. Add `--pj-supp f1.pdf f2.pdf ...` for extra pieces (adapts to
  N attachments). Add `--cc kakesamudimba@gmail.com` to ALSO send the user a copy
  (user requirement: "envoie mais avec un cc à mon Gmail"). Tested live 2026-07-14:
  sent 2 PJ to rh@flash.one with CC to his Gmail, signature included.
- Mode C web-form upload (Playwright) NOT yet wired — only email multi-PJ is live.
  See `references/auto_candidature.md`.

### 4c. Handwritten signature (extracted from a screenshot + inserted)
User requirement (locked 2026-07-14): extract his REAL signature from a phone
signature-app screenshot, ENLARGE it (~16mm), and CENTER it directly above the typed
name `KAKESA MUDIMBA DIEUDONNE` (same vertical axis), on BOTH the CV and the letter.

**Extract (PIL):** the screenshot is a phone UI (colored header "Signatures", a light
strip with the blue handwritten sig, white body).
```python
from PIL import Image
im = Image.open(path).convert("RGB"); px = im.load(); W,H = im.size
minx=W; maxx=0; miny=H; maxy=0
for y in range(150,260):
    for x in range(W):
        r,g,b = px[x,y]
        if b>120 and b-r>40 and b-g>40:   # blue signature pixels
            minx=min(minx,x); maxx=max(maxx,x); miny=min(miny,y); maxy=max(maxy,y)
crop = im.crop((max(0,minx-15), max(0,miny-15), min(W,maxx+15), min(H,maxy+15)))
# make background transparent
c = crop.convert("RGBA"); p = c.load()
for y in range(c.size[1]):
    for x in range(c.size[0]):
        r,g,b,a = p[x,y]
        if r>200 and g>200 and b>200: p[x,y]=(255,255,255,0)
        else: p[x,y]=(r,g,b,255)
c.save("signature_extraite.png")
```
Vision-check the crop (isolated? clean? not cut?).

**Insert (fpdf2) — SIZE BY HEIGHT, CENTER ON THE NAME:**
```python
SIG = "/root/linkedin_app/signature_extraite.png"
from PIL import Image as _PILImage
_iw, _ih = _PILImage.open(SIG).size
sig_h = 16   # mm — size by HEIGHT not width (see pitfall)
sig_w = sig_h * _iw / _ih
ZONE = 75    # mm — wide zone so the typed name is NOT truncated at the right edge
# letter: COL=100, center the 75mm zone inside the 85mm right column
zone_x = COL + (85 - ZONE) / 2
pdf.image(SIG, x=zone_x + (ZONE - sig_w) / 2, y=sig_y, w=sig_w)   # center img in zone
pdf.set_xy(zone_x, sig_y + sig_h + 1)
pdf.cell(ZONE, 6, "KAKESA MUDIMBA DIEUDONNE", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
```
CV (no fixed COL): `zone_x = pdf.w - pdf.r_margin - ZONE`.

**Pitfalls (all hit & fixed this session):**
- `add_page(margin=...)` is INVALID — raises `TypeError: add_page() got an unexpected
  keyword argument 'margin'`. Set margins via `pdf.set_margins(l,t,r)` +
  `pdf.set_auto_page_break(auto=True, margin=...)`.
- Size by HEIGHT not width. A near-square sig at `sig_w=60mm` becomes ~46mm tall and
  shoves the letter onto a 2nd page. `sig_h=16 → sig_w≈21mm` keeps it compact; drop to
  14mm if it still splits.
- Keep the LETTER on ONE page. After adding the image tighten: body `multi_cell(160,5.0,
  ...) → 4.8`, paragraph gap `cy = get_y()+2 → +1.5`, `sig_y = get_y()+3`.
- Wide-enough name ZONE (75mm). `cell(sig_w, ...)` truncates "DIEUDONNE" at the right
  edge — the typed name must sit in the same 75mm zone the image is centered in.
- Verify with pymupdf + vision: render last page, confirm signature centered over name,
  not cut, doc still 1 page (letter) / 2 pages (CV).

**Generated fallback (no screenshot):** `faire_signature.py` renders the name with a
script TTF (GreatVibes/Parisienne/Sacramento/Allura, `curl` from github google/fonts) to
a transparent PNG. Prefer the extracted real signature when the user supplies a screenshot.

**REFINEMENT — screenshot qui contient SIG + NOM IMPRIMÉ (2026-07-17) :** la 1re image
de signature fournie (`/root/.hermes/cache/images/img_4a068b6b80ad.jpg` →
`signature_kakesa.jpg`) portait ENSEMBLE la signature cursive ET le nom « KAKESA MUDIMBA »
en lettres de bloc séparées en dessous. La recette bbox-pixels-bleus (§4c) a extrait les
DEUX. Pour isoler LA SIGNATURE SEULE dans ce cas :
- **Couper par DENSITÉ D'ENCRE PAR LIGNE** (`row_ink(y)` = fraction de pixels sombres
  sur la ligne), pas par bbox globale. La signature cursive finit vers y≈187 ; le nom en
  bloc commence ~y≈188 (chute nette de densité). `crop((0, top, W, 186))` isole la
  cursive. La vision seule est INSUFFISANTE pour juger (elle « lit » le nom même après
  crop car une partie du script épelle KAKESA) — vérifier la coupure sur le profil de
  densité ligne par ligne.
- **Source la plus propre** : si l'utilisateur fournit un aperçu « Signatures » d'une app
  (ex `img_1d3e3ed83a0f.jpg`) ne montrant QUE le tracé cursif, la recette bbox-bleue
  §4c suffit et donne `/root/Candidatures/Modèles/signature_seule.png` (isolé, bleu sur
  blanc) — C'EST cet asset qui a été retenu pour le CV/lettre KPMG. Préférer toujours
  une source ne contenant que la signature ; ne découper que si le nom est mélangé.
- **PITFALL** : ne PAS laisser la ligne « Signature : » sur le CV fpdf2 (§4c) — l'utilisateur
  a demandé « Supprimer : signature : remplacer le signature référence vivante » → image
  seule + nom tapé dessous. Sur l'ODT (§1e) en revanche, garde le nom tapé (pas d'image
  imprimée dans l'image).

### Workflow for "postule pour moi"
1. Build CV_KAKESA_MUDIMBA_<OFFER>.pdf + Lettre_Motivation_<OFFER>.pdf (branch from refs).
2. If an HR email is available → send via Gmail SMTP with App Password (+ `--cc` for copy).
3. If only a portal → deliver files + the apply link; user clicks Postuler.
