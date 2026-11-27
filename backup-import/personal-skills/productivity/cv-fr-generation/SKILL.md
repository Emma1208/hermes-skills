---
name: cv-fr-generation
description: Generate French CV and official motivation letters as PDF with fpdf2 for user KAKESA MUDIMBA Dieudonné. Covers DejaVu font setup, the exact official letter spatial spec (25mm margins, 100mm blocks, right-aligned date/destinataire, majuscules, single underlined destination), the CV structure (I-VIII, no VII), the living-reference naming convention, and the Gmail SMTP app-password pitfall. Use whenever the user asks for a CV, a lettre de motivation, or to apply to a job.
---

# CV & Lettre de Motivation — Génération FR (fpdf2)

Workflow for producing this user's job documents. The user is **KAKESA MUDIMBA Dieudonné** (Congolais, Kinshasa). Communicate in French, be concise, send the PDF back as MEDIA each time you regenerate.

## 0. Environment / fonts (CRITICAL)
fpdf2's built-in Helvetica does NOT render French accents (é è à ê ç æ). Always use **DejaVu** TTFs.
- Source on this box: `/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans.ttf` (+ `-Bold`, `-Oblique`) and `DejaVuSerif.ttf` (+ `-Bold`, `-Italic`).
- Copy them into the working dir first:
  `cp /data/data/com.termux/files/usr/share/fonts/TTF/DejaVu*.ttf /root/linkedin_app/`
- Register: `pdf.add_font("DJ","", "DejaVuSans.ttf")` etc. Use "DJ" for sans (CV) and "SR" for serif (letter, ≈ Times).
- pypdf is available for extracting/verifying generated PDF text: `pip install pypdf` if missing.

## 1. Naming convention (living reference)
- General reference (always updated as experience accrues, base for everything):
  `CV_KAKESA_MUDIMBA.pdf` and `Lettre_Motivation_Generale.pdf`
- **LIVING BASE TEMPLATE (the canonical source for ALL letters, incl. family members'):**
  `/root/linkedin_app/modele_lettre_generale.py` → regenerates `Lettre_Motivation_Generale.pdf`.
  It has a `CONFIG` block at the TOP (EXPEDITEUR list / DATE_LIEU / OBJET_POSTE / STRUCTURE / LOCALISATION / CORPS list / SORTIE path).
  **ONLY ever edit the CONFIG block** — the layout code below it is frozen (user: "sauvegarde cette format de lettre motivation générale ça servira de base"). For a new offer, copy this file to `generer_lettre_<offre>.py` and change CONFIG only. Same pattern for a sibling's letter (copy, swap identity + CORPS).
- Targeted per offer: `CV_KAKESA_MUDIMBA_[Offre].pdf` (e.g. `_BSF`, `_Clientele`) and `Lettre_Motivation_[Offre].pdf`.
- Keep a generator script per document: `generate_cv.py` (general), `generate_cv_<offre>.py` (copy+adapt), `generer_lettre_officielle.py` (general letter), `generer_lettre_<offre>.py`, `generer_lettre_bitota.py` (sibling example).
- The general docs are the SOURCE — derive targeted ones by filling the bracket placeholders, never rebuild from scratch.

## 2. CV structure (generate_cv.py)
- Header: big `Curriculum Vitæ` (use the æ glyph), subtitle = poste visé (e.g. "Candidat au poste de Chargé de clientèle").
- Sections: **I. Informations personnelles**, **II. Parcours**, **III. DOMAINES DE COMPÉTENCE À ÉVOLUER**, **IV. Études faites**, **V. Formations**, **VI. Langues**, **VIII. Références** (NO VII).
- Infos perso & Références: render as label (blue, bold) + value (black). Références numbered 1..N with name (bold black), role (black), contact (grey, indented).
- Dates in **bold**; job titles **underlined** by drawing a line (`pdf.line`) because fpdf2 has no set_underline for this version.
- Keywords: black, NOT bold.
- End with honour declaration (italic): "Je jure sur mon honneur que les informations ci-dessus sont vraies et exactes." + "Fait à Kinshasa, le JJ/MM/AAAA" (use `datetime.date.today()`).
- **NO photo** by default, NO "généré automatiquement" footer.
- **PHOTO EXCEPTION (KPMG-class offers)**: if the offer text EXPLICITLY demands a photo (e.g. KPMG RDC: "Votre dossier doit impérativement contenir : [...] un Curriculum Vitae (CV) avec photo"), ADD a photo to the TARGETED CV. Place it top-right INSIDE the navy header band (height ~26mm, right margin 4mm, y=2mm) so it never collides with the left-aligned title. Reuse an available photo file (`/root/linkedin_app/photo_docx.png`, 150×200 RGB; or `ref_photo.png`). This is the ONLY case a photo goes on the CV — the general CV stays photo-free. (Verified 2026-07-15: 2-page KPMG CV with header photo rendered clean, vision-confirmed no collision.)
- Font size: user wants ≥13 for readability in the CV body.
- Reference data (verified): MSF PUC MED (logistique), Min. Finances DRQC (audit/vérification pièces), prof compta Sagesse 2 + Minga la Paix; Licence Gestion Financière Univ. Kinshasa 2021-2022. Références: MUTAMBWE TSHAMU Patrick (DRH MSF +243 824 983 499), TEDDY PULUMBA, DJIMY MAKENGO (Directeur discipline Sagesse +243 821 994 204), MBELENGE Minga (Promoteur/Préfet Minga la Paix +243 820 073 629).

## 3. Official letter spec (generer_lettre_officielle.py) — EXACT
Margins 25mm all sides. Page A4. Serif 11pt.
- **Expéditeur**: top-LEFT, ALL CAPS, width capped at **100mm** (wrap if longer, e.g. address "N° 3, AV. TUNGILA, Q. BIANDA, C. MONT NGAFULA" wraps). Do NOT exceed page middle.
- **Date**: top-RIGHT, RIGHT-aligned to the 25mm right margin (cell x=LEFT width=160, align="R" → ends at 185mm). Format `KINSHASA, JJ / MM / AAAA`.
- **Objet**: 25mm below expéditeur, LEFT, ALL CAPS, width capped 100mm (wrap). `OBJET : CANDIDATURE AU POSTE DE [POSTE]`.
- **Destinataire**: RIGHT BLOCK, all lines START at x=100mm/BLK, left-aligned within the block (NOT right-aligned — user: "ils doivent commencer au même colonne"). Three lines `A MONSIEUR LE DIRECTEUR` / `DES RESSOURCES HUMAINES` (own line, below) / `DE [ORGANISATION]`, each via `pdf.set_xy(BLK,dy); pdf.cell(0,6,line)`. Then `KINSHASA / [COMMUNE]` UNDERLINED — underline drawn BELOW the text (`pdf.line(BLK, y+6+1.5, BLK+w, y+6+1.5)`), not above.
- **Formule d'appel**: `Monsieur le Directeur,` RIGHT-aligned, at `objet_y + 30 + 12` mm below objet (user pushed it down cumulatively; 42mm total).
- **Corps**: para 1 → first line runs to right margin, remainder continues at LEFT; other paragraphs JUSTIFIED. Width = 160 (ends x=185) so right edge matches the destinataire block ("doivent se limiter là où le corps se limite").
- **Politesse finale**: line 1 (`Veuillez agréer, Monsieur le [Titre],`) RIGHT-aligned (BLK block, ends 185); line 2 (`l'assurance de ma considération distinguée.`) at LEFT.
- **Signature**: RIGHT-aligned at BLK=x=100mm start, align="R", ALL CAPS (`KAKESA MUDIMBA DIEUDONNE`).
- MAJUSCULES for: Expéditeur, Objet, Organisation, Ville destinataire, Signature. Underline ONLY the destination ville/quartier.
- Keep whole letter on ONE page (tighten interline to 5mm if signature spills to p2).
- Bracket placeholders to fill per offer: `[POSTE]`, `[NOM ORGANISATION]`, `[COMMUNE]`, `[Titre]`, date.

## 4. Iterative layout-correction workflow (how this user works)
User gives tiny nudges, one at a time: "Encore 4mm", "serre à droite limite à 25mm de la marge", "la ligne noir doit être dessous", "descendre Monsieur le Directeur de 2mm". 
- Apply the single change, regenerate, re-send the PDF. Do NOT batch unrelated changes or over-explain.
- When user says "comme tu as fait pour la date" → they mean RIGHT-aligned (the date is right-aligned). If you misread as left, correct immediately.
- Always verify with pypdf text extraction that the change took effect.

## 4b. VERIFY BY RENDERING — NOT BY GUESSING (critical, learned the hard way)
`pypdf` text extraction does NOT reveal layout bugs: overlapping/colliding text, wrong alignment, things spilling to page 2 still read as "normal" text. Blind-guessing spacing from text extraction wasted ~10 turns on one letter. Instead:
1. `pip install pymupdf` (gives the `fitz` module). Then render each page to PNG:
   ```python
   import fitz
   d = fitz.open("Lettre_Motivation_X.pdf")
   for i,p in enumerate(d):
       p.get_pixmap(dpi=110).save(f"page{i+1}.png")
   ```
2. Inspect with `vision_analyze(image_url=".../page1.png", question="...")` — ask specifically: "Tient-il sur 1 page ? L'objet et la date sont-ils bien séparés (pas collés) ? Le texte est-il lisible et bien aligné ? Signale tout problème." The vision model catches collisions/overlaps/legibility that text extraction hides.
3. Only after the render looks correct, send the PDF. This cut a 10-turn loop to 1.

## 4c. LEGIBILITY IS NON-NEGOTIABLE — NEVER SHRINK FONT TO FIT
To force a letter onto one page, do NOT drop below **11pt** or below ~4.8mm interline. A 10.5pt / 3.9mm version was produced to fit a page and the user rejected it hard ("tu as fait n'importe quoi"). Fit one page via GEOMETRY instead: shrink gaps between blocks (objet→destinataire, formule→corps), reduce body block width, tighten `cy +=` increments by 0.3–1.5mm. Keep 11pt serif, 5mm body interline minimum. If it still overflows, that's acceptable feedback to ask the user — never ship an illegible doc.
- If user sends a *reference* letter (e.g. "Lettre Serge Mbulu") and says "suis l'entièreté de cette lettre", they mean REUSE THE CONTENT/STRUCTURE, NOT copy its left-aligned layout. This user's preferred official layout is the right-aligned format in §3. They reverted a left-aligned "Serge style" copy with "Non remet ma lettre d'avant" — so keep §3, only borrow prose.

## 4d. VERIFY ALIGNMENT WITH WORD COORDINATES — vision misreads alignment
When the user cares about *where* a block sits (right column vs left, "aligné avec le corps"), the vision model is unreliable — it reported the Serge clone's destinataire as "left/centered" when it was actually at x≈286pt (the right column). Confirm coordinates programmatically instead of trusting the render:
```python
import fitz
d = fitz.open("Lettre_Motivation_X.pdf")
for b in d[0].get_text("words"):
    x0, y0, x1, y1, txt = b[0], b[1], b[2], b[3], b[4]
    if txt in ("A","Monsieur","KAKESA","Objet") or "STRUCTURE" in txt:
        print(round(x0,1), repr(txt))
```
On A4 (210mm = 595pt), LEFT=25mm≈71pt, COL=100mm≈283pt. So a block at x0≈283–286 is the right column; x0≈71 is the left margin. Use this to confirm destinataire/formule/signature share the same column before declaring success. Combine with the §4b render+vision check for legibility/overlap; use §4d specifically for *position* claims.

## 4e. SIBLING / FAMILY LETTERS — same template, swap identity + CORPS
The user will ask you to write letters for family members (e.g. his sister BITOTA MUDIMBA MAMITSHIO, agent d'entretien) using the SAME living template. Procedure:
1. Copy `modele_lettre_generale.py` → `generer_lettre_<prenom>.py`.
2. Swap EXPEDITEUR (their identity from their CV), DATE_LIEU, OBJET_POSTE, STRUCTURE, LOCALISATION, CORPS, SORTIE.
3. Keep ALL layout code frozen. Follow the same pitfall rules below.
Identity facts captured for siblings live in memory (USER.md), not here. For BITOTA: name BITOTA MUDIMBA MAMITSHIO, 4 Av. Tungila Q. Masanga-Mbila C. Mont-Ngafula, tel 0892966888, NO email in CV (ask if needed), poste "agent d'entretien", experience MSF pool d'entretien + écoles/ONG ménagère.

### CRITICAL PITFALL — "formule d'appel" vs "bloc destinataire" are DIFFERENT blocks
The user corrects these as SEPARATE elements. When he says "à la formule d'appel supprimer X" he means ONLY the `Monsieur le Responsable,` line — do NOT touch the destinataire block above it. When he says "au bloc destinataire supprimer X" he means ONLY the `A Monsieur le Responsable des Ressources Humaines` / `KINSHASA / GOMBE` block.
- Session error (2026-07-14): user said "à la formule d'appel, supprimer madame et des ressources humaines"; assistant wrongly ALSO edited the destinataire block. User: "Tu ne m'a pas compris j'ai dit au formule d'appel et non au coordonnées du destinataire." → FIX: edit formule line only, regenerate, verify with word coords (§4d) that destinataire still reads full original text.
- Then: "au bloc destinataire supprimer madame" → edit destinataire line only (remove "Madame,"), keep formule as-is.
- Then: "le bloc du destinataire doivent être fini au même colonne que le corps" → move destinataire block to LEFT (x=LEFT, width 160) while formule + signature STAY RIGHT. Then user said "A droite" → move destinataire back to COL=100. Net rule: ask/confirm which block + which column per nudge; never assume both blocks move together.
- This user gives ONE tiny nudge at a time and expects you to apply JUST that. Do not batch the destinataire+formule edits.
> NOTE: the FINAL accepted Serge-clone letter layout (right-column destinataire/formule/signature,
> living CONFIG template, verify_letter.py coordinate check) now lives in its own skill
> **`fr-motivation-letter`** — load that for any cover-letter task. This §7 is kept as the
> reverted-attempts record only; do not rebuild the layout from here, it's frozen there.
All of these were tried and the user said "Échec met comme avant" / "Non remet ma lettre d'avant". Do NOT redo them:
- **Objet and Destinataire on the SAME line** (objet left at x=LEFT, destinataire at x=BLK starting at the same Y). User reverted. Keep Objet left, then Destinataire BELOW at BLK (objet_y + 8).
- **Expéditeur address on one line** (`N° 3, AV. TUNGILA, Q. BIANDA, C. MONT NGAFULA`). User wanted the commune split onto its OWN line below the avenue line: line1 = `N° 3, AV. TUNGILA, Q. BIANDA,` then line2 = `C. MONT NGAFULA`. Applies to BOTH the §3 official letter and the §7 Serge clone. User: "la commune doit être au dessous du numéro 3 de l'avenue".
- **Left-aligned "Serge Mbulu style"** letter (objet left, destinataire left, formule left, corps indented right at BLK, signature left). User prefers the §3 official right-block format. Only the prose may come from references.
- **One-pager fit for the left-aligned "Serge" style** (geometry captured in case it's ever requested): body 10.5pt, first line `cell(0,4.0,...)`, continuation `multi_cell(85,3.9,align="L")` at x=BLK(100); gaps `formule_y=dy+9`, `cy=formule_y+6`, `cy+=0.3`, `pol_y=cy+2`, `sig_y=get_y()+3`. Generator `generer_lettre_serge.py` → `Lettre_Motivation_Serge_Clone.pdf`. Reverted to §3 but geometry kept for reuse.
- **The FINAL accepted Serge clone** (legible, 1 page) — CORRECTED: user explicitly wants **destinataire + formule d'appel + signature ALL RIGHT-aligned on the SAME right column** (COL=100mm → text starts ~x=283pt on A4), matching the reference Serge letter where "A Monsieur le Directeur...", "Monsieur le Directeur," and the signature all sit in that right column. An earlier capture wrongly said left-aligned — that was rejected. If the user says "regarde bien la lettre de référence Serge, observe comment le destinataire est aligné avec le corps et la formule d'appel", they mean this right-column alignment. Working geometry at 11pt serif (verified 1 page): `LEFT=25, RIGHT=25, COL=100`; Expéditeur top-LEFT (5 lines: name / `N° 3, AV. TUNGILA, Q. BIANDA,` / `C. MONT NGAFULA` on its OWN line / Tel / Email); Date `cell(160,6,"Kinshasa, 14 / 07 / 2026",align="R")` top-right; Objet LEFT at `objet_y=y+12`; Destinataire `multi_cell(85,5,text, new_x=XPos.RIGHT, new_y=YPos.NEXT, align="L")` at `set_xy(COL,dest_y)` — **`new_x=XPos.RIGHT` keeps the cursor in the right column so a too-long line WRAPS to the next line in the SAME right column, NOT back to the left margin** (User: "la structure et destinataire doivent être une suite même s'il y a plus d'espace là ça continue sur l'autre ligne"). Using `new_x=XPos.LMARGIN` is the WRONG behavior (jumps to far left); localisation `KINSHASA / [COMMUNE]` underlined below; Formule `Monsieur le Directeur,` at `set_xy(COL,formule_y)`; **Corps = full-width justified** `multi_cell(160,5,align="J")` from LEFT (NOT an 85mm indented block — that forced the illegible 10.5pt/3.9mm version rejected with "tu as fait n'importe quoi"); Politesse line1 right-block / line2 LEFT; Signature `cell(85,6,"KAKESA MUDIMBA DIEUDONNE",align="R")` at COL. Generator `generer_lettre_serge.py` → `Lettre_Motivation_Serge_Clone.pdf`.

## 8. Editable .odt workflow (odfpy + LibreOffice) — 'opérateur de saisie' use case
When the user wants to FILL/EDIT the doc himself (his framing: 'opérateur de saisie' building his
candidacy dossier), deliver an **editable LibreOffice .odt** AND a PDF export, not a PDF-only.

- Build with `odfpy` (`pip install odfpy`). Use a `mk_para_style(name, color, fontsize, bold=False, bg=None, sp=None)`
  helper that adds ParagraphProperties + TextProperties to `doc.styles`. Reference families:
  navy header band (`backgroundcolor="#142850"`, white text, bold) for the title + each section band;
  black body 10–10.5pt; navy bold for job titles; right-aligned block for the closing.
- **RIGHT ALIGN**: define a dedicated style with `ParagraphProperties(textalign="right", ...)` and pass its
  name string to `P(stylename=...)`. odfpy has no `set_alignment` on P — the style is the only way.
- **BOLD**: `TextProperties(fontweight="bold")`. Verify in the saved .odt by unzipping:
  `unzip -p file.odt styles.xml | grep -o 'name="CVSerment"[^/]*fo:font-weight="bold"'`. The vision model
  MISREADS a long right-aligned serment as 'centered' — confirm with the XML + a 150-dpi render, not by eye alone.
- **IMPORT GOTCHA**: `TextProperties` lives in `odf.style`, NOT `odf.text` (ImportError if wrong).
- Save: `doc.save("file.odt")`. Export to PDF: `soffice --headless --convert-to pdf file.odt`.
  Check page count: `pdfinfo file.pdf | grep Pages` (target 2 for CVs — see CV page-count note).
- **VERIFY by render** (§4b): `pdftoppm -png -r 150 file.pdf /tmp/p` then `vision_analyze` on each page:
  ask specifically "serment à gauche ? Fait à Kinshasa à droite ? 2 pages, rien tronqué ?". Cross-check
  truncated text with `pdftotext -layout file.pdf - | grep <pattern>`.
- Deliver BOTH `CV_modele_vierge.odt` (bracket fields `[à remplir]` the user fills) AND
  `CV_KAKESA_MUDIMBA_rempli.odt/.pdf` (data from the living reference). Working generators on this box:
  `/root/linkedin_app/generer_cv_modele_vierge.py` and `/root/linkedin_app/generer_cv_rempli.py`.
- Canonical CV ending (matches `CV_KAKESA_MUDIMBA.pdf` = living reference): honour serment EN GRAS, LEFT;
  `Fait à Kinshasa, le JJ/MM/AAAA` RIGHT; **NO** "Signature :" line and NO typed name unless the user
  explicitly asks for the §7 handwritten-signature block. (2026-07-16: user said "toujours mettre la
  signature référence vivante" → meant match the living reference, which has no signature block — when
  checked, `CV_KAKESA_MUDIMBA.pdf` ends serment+Fait only. Remove any "Signature :"/name you added.)

## 5. Sending by email (Gmail SMTP) — PITFALL
- Normal Gmail password FAILS: `SMTPAuthenticationError 534 ... Application-specific password required`.
- Fix: user must create an **App Password** at https://myaccount.google.com/apppasswords (name it e.g. "Hermes"), give the 16-char code.
- **GOTCHA**: the code arrives WITH SPACES (e.g. `hhrz ujtk nfvz kpkk`) — strip them: `PWD = code.replace(" ","")` before `login()`. Passing it with spaces fails auth. Verified: stripped variant sent `ENVOYÉ OK -> mbombomudimba@gmail.com`.
- Send via `smtplib.SMTP_SSL("smtp.gmail.com", 465)` with `login(email, APP_PASSWORD)`, `EmailMessage`, attach PDFs via `msg.add_attachment(..., maintype="application", subtype="pdf", filename=...)`.
- See `references/gmail_smtp.md` for the working script.
- NOTE: APPLY WORKFLOW (user asked 2026-07-14 "si un site d'offre demande plusieurs pièces jointes comme tu fairas pour l'envoi automatique"): you CAN attach as many files as the site asks.
  • If the posting gives an email address → send ONE email with all attachments (CV + letter + any others) via the script above (loop the `add_attachment` list).
  • If the posting is an ONLINE FORM (makesense, job board) → pilot a browser to fill fields and drop each file in its correct upload slot (CV here, letter there). Multiple upload fields are fine.
  • Preferred approach: prepare a "dossier type" (CV + letter + any docs) on disk first, then the send step picks from it per offer. Decide A (email) vs B (form) per site automatically.
  • Do NOT claim browser piloting is impossible — it works for form-based apply. Only blocked case is LinkedIn scraping (captcha).
  • **REUTILISABLE SCRIPT** `scripts/candidature_auto.py` (in this skill dir): profile-dispatched auto-apply pack. Add a profile = add one line to PROFILS dict (`cv_gen`, `cv_out`, `let_gen`, `let_out`). Run: `python3 candidature_auto.py --profil flash --to rh@flash.one --sujet "Candidature RESPONSABLE TECHNIQUE" [--pj-supp diplome.pdf ...]`. It regenerates the targeted CV+letter then emails ALL attachments (adapts to however many the site asks for). Strip spaces from the app password inside the script. Reusable as-is for any new offer — just add a PROFILS line.
  • **CC / copie**: the script accepts `--cc kakesamudimba@gmail.com` to send a copy to the candidate's Gmail (user asked 2026-07-14 "Envoyer mais avec un cc à mon Gmail"). It sets `msg["Cc"] = cc` and prints the copy in the confirmation. Use it whenever the user wants a copy of the sent application.
  • **HYBRID APPLY (email + imposed naming + mandatory form)** — KPMG RDC case (2026-07-15): a posting can require ALL THREE at once: (a) send CV+letter by EMAIL to a given address; (b) RENAME the attachments to an imposed convention (`CV_Nom&Prénom_AD Audit.pdf`, etc.) — do the rename at `add_attachment` time, NOT on disk; (c) ALSO **validate a web form** on the same site ("Assurez-vous d'avoir validé le formulaire de renseignement afin qu'il soit pris en compte"). Email alone is NOT sufficient — flag the form step to the user and tell them to click through/Suivant→valider. Deadline (e.g. 27/07/2026) also goes in the reminder. Working send script: `/root/linkedin_app/envoyer_kpmg.py` (IMPLEMENTED, sent OK: TO `CD-Recrutement@kpmg.com`, CC Gmail, two renamed PDFs). Reuse its shape for any offer with an imposed filename convention.

## 7. Adding a handwritten signature (image + typed name)
User asked 2026-07-14 to add his signature to BOTH the CV and the letter: a manuscript-style image ABOVE + the typed name BELOW. **FINAL VALIDATED STANDARD (user: "Très bon sauvegarde notre modèle de signature référence vivante", 2026-07-14):**

### 7a. Living-reference signature — SINGLE SOURCE, use for every doc
- Reference image (bleue extraite d'une capture, fond transparent) : `/root/linkedin_app/signature_kakesa_ref.png`.
- Reusable module : `/root/linkedin_app/modele_signature.py` → `inserer_signature(pdf, zone_x, y, zone_w=75, font_name="DJ", font_size=12, font_style="B", nom="KAKESA MUDIMBA DIEUDONNE", sig_h=16)`. A copy lives in `references/signature_reference.py`.
- Standards VALIDÉS : **hauteur signature 16 mm**, **CENTRÉE horizontalement au-dessus du nom** (même axe central), nom tapé en gras dessous, **zone de 75 mm**. Jamais recréer la signature : si l'utilisateur change de signature, remplacer UNIQUEMENT `signature_kakesa_ref.png`.
- Apply on a new doc by calling `inserer_signature()` with the zone top-left (zone_x, y), zone_w=75.
  - Letter right column (COL=100, width 85): center the 75mm zone → `zone_x = COL + (85-75)/2`.
  - CV bottom-right: `zone_x = pdf.w - pdf.r_margin - 75`.

### 7b. If user only has a name (no image) — generate one
Generate the signature PNG from the name with a cursive font + PIL: `scripts/faire_signature.py` (fonts in `fonts/`, google/fonts raw: `GreatVibes-Regular.ttf`, `Parisienne-Regular.ttf`, `Sacramento-Regular.ttf`, `Allura-Regular.ttf`). Then save it as `signature_kakesa_ref.png` to become the living reference. PITFALL: draw with ~30px left offset + ~40px height/60px width margin, else Great Vibes ascenders/descenders get clipped.

### 7c. If the user provides a SIGNATURE PHOTO / SCREENSHOT — extract it
Workflow that worked (2026-07-14, screenshot from a mobile signature app):
1. Locate the mark by colour: scan pixels, detect the ink (e.g. blue: `b>120 and b-r>40 and b-g>40`). Compute bbox, crop with a margin → `sig_raw_crop.png`.
2. Make background transparent: open RGBA, set any near-white pixel (`r>200 and g>200 and b>200`) to alpha 0.
3. Save as `/root/linkedin_app/signature_kakesa_ref.png` (the living reference). Verify with vision_analyze that it's clean (no parasitic text) and not clipped.
4. Insert via `modele_signature.inserer_signature()` (§7a). Reusable extractor: `scripts/extraire_signature.py`.

### 7d. Sizing & 1-page pitfalls
- **SIZE BY HEIGHT, NOT WIDTH**: a fixed `sig_w=60`mm is fine for a wide *generated* name (~1016×118) but OVERFLOWS for a near-square *extracted* mark (~90×69px → 60mm wide = ~46mm tall, alone forces page 2). Always set a target height and derive width: `sig_h = 16; sig_w = sig_h * iw / ih`.
- **CENTER, don't right-align** (SUPERSEDES old `align="R"` name): validated layout centers the signature over the name (same axis).
- **1-PAGE OVERFLOW (letter)**: the signature block can push p2. Fix WITHOUT shrinking below 11pt (§4c): tighten body interline `multi_cell(160,5,..)`→`(160,4.8,..)`, reduce gaps (`cy=formule_y+8`, `cy+=1.5`, `sig_y=get_y()+3`). 16mm sig + 75mm zone kept the Flash letter at 1 page. Always `fitz.open(f).page_count` check after.
- Verify via §4b render+vision: signature not clipped, name directly under, same center.

See `scripts/faire_signature.py` for the name-based generator; `references/signature_reference.py` + `/root/linkedin_app/signature_kakesa_ref.png` for the living-reference insertion; `scripts/extraire_signature.py` for screenshot extraction.

### CV page-count compression PITFALL (learned 2026-07-14, Flash CV; DEFAULT REVISED 2026-07-16)
A CV may run up to **2 pages** — that is now the user's DEFAULT (2026-07-16: "Non ma préférence
est deux pages maximum par défaut"). Do NOT silently compress a 2-page CV to 1 page. Only compress
GEOMETRY when a 2-page CV threatens a 3rd page, and never below 13pt in the CV body. Compress GEOMETRY instead:
- `pdf.set_margins(14,14,14)` + `pdf.set_auto_page_break(auto=True, margin=14)` (tighter margins).
- Drop body `para`/`bullet` default to `size=12, lh=5.5` (still ≥12, readable). Keep identity block at 13 if desired.
- **CRITICAL**: `pdf.add_page()` does NOT accept a `margin=` kwarg — it raises `TypeError: add_page() got an unexpected keyword argument 'margin'`. Set margins via `set_margins()` BEFORE `add_page()`, then call `add_page()` with no args.
- Condense the références section (6 detailed numbered blocks → 3 one-line bullets `• Name — role — contact`) to shave a trailing 3rd page.
- Verify with `fitz.open(f).page_count` after regenerating. Target = 2 pages (NOT 3). One page only if explicitly requested or content is short.

## 6. Job search / active offers
- Scan multiple sources (Médiacongo, TonJob, eGoZola, Congoquotidien, makesense) for offers matching: comptable / gestion financière / audit / enseignement / logistique, Kinshasa + remote FR.
- KEEP ONLY offers with a non-expired deadline. Many listings are stale republications — verify the date in the body before presenting.
- Present as a compact table (offre / employeur / lieu / deadline / adéquation) + A/B/C/D next step. This user prefers A/B/C/D choices and result-first.

See `references/layout_spec.md` for the literal coordinate values, `references/gmail_smtp.md` for the send script, `references/lettre_template_config.md` for the living base template CONFIG block, `references/apply_workflow.md` for the multi-attachment automated-apply flow, `references/signature_reference.py` + `/root/linkedin_app/signature_kakesa_ref.png` for the living-reference signature module, `scripts/candidature_auto.py` for the reusable profile-dispatched auto-apply pack, `scripts/faire_signature.py` for the name-based handwritten-signature generator (§7b), and `scripts/extraire_signature.py` for screenshot/photo signature extraction (§7c).
