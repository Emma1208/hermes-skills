---
name: fr-motivation-letter
description: >-
  Generate French motivation/cover letters (lettres de motivation) as PDF with fpdf2 +
  DejaVuSerif, following Emmanuel KAKESA's VALIDATED "Serge Mbulu" layout and the reusable
  living-template (CONFIG block) pattern. Use for ANY job-application cover letter for Emmanuel
  or a family member; adapt ONLY the CONFIG block per offer. Layout rules are strict and were
  signed off 2026-07-14 — do not improvise spacing or fonts.
---

# French Motivation Letter (Lettre de Motivation) — validated layout

## When to use
- User asks for a `lettre de motivation` / cover letter for a job offer (their own or a relative's).
- Always reuse the living template `modele_lettre_generale.py` (see `templates/`). Only the
  CONFIG block at the top changes per offer; the page layout NEVER changes.
- If the user sends a rough draft + identity (CV), rewrite it INTO this format, fixing grammar
  and keeping their facts.

## Prerequisites
- `fpdf2` installed (`pip install fpdf2`).
- Fonts present in the working dir: `DejaVuSerif.ttf` and `DejaVuSerif-Bold.ttf`
  (serif ≈ Times, required — the user rejected sans-serif for letters).
- Always 11pt minimum for letters (user: "JAMAIS < 11pt", legibility rule).

## The validated layout ("Serge Mbulu" style) — DO NOT DEVIATE
Exact rules confirmed by the user on 2026-07-14:

> **Override rule:** this layout is the DEFAULT, not absolute. When the user gives an explicit
> per-letter layout instruction that deviates, FOLLOW IT — explicit user instruction beats the
> frozen code. But be warned: the closing/polite formula is the single most-moved element (see
> PITFALL — moveable politeness phrase below). Always implement the COMPLETE sentence at the ONE
> requested location and verify with coordinates BEFORE declaring done.
- **Page:** A4, margins 25mm, `set_auto_page_break(margin=25)`, 1 page only.
- **Expéditeur (left):** name, then address with the **commune on its own line** under the
  street number, e.g.:
  ```
  KAKESA MUDIMBA DIEUDONNE
  N° 3, AV. TUNGILA, Q. BIANDA,
  C. MONT NGAFULA
  Tel : +243 81 849 16 01
  Email : kakesamudimba@gmail.com
  ```
- **Date (top right):** `cell(160, 6, "Kinshasa, 14 / 07 / 2026", align="R")`.
- **Objet (left, under expediteur):** bold, limited to ~100mm width so it stops at the
  MIDDLE of the page; if it overflows it wraps BELOW in the same left column.
  `multi_cell(100, 6, "Objet : " + OBJET_POSTE, ...)`.
- **Destinataire / Formule d'appel / Signature (RIGHT column, x=100mm):**
  `COL = 100`; always `set_xy(COL, y)` before these blocks. They must be aligned on the same
  right column (verified coordinate x0 ≈ 286pt).
- **Corps (body):** justified, FULL width (`multi_cell(160, 5, p, align="J")`), starts under
  the formule d'appel.
- **Politesse + Signature (right):** "Votre employée," / name in bold, right-aligned.

## Support files in this skill
- `templates/modele_lettre_generale.py` — copy this, edit only the CONFIG block, run.
- `scripts/verify_letter.py <pdf>` — prints page count + right-column x0 coords; run after
  generating to confirm right-column blocks sit at x0≈286 (trust this over vision_analyze).

## The living-template pattern (KEY technique)
`templates/modele_lettre_generale.py` separates ALL variable content into a `CONFIG` block at
the top (EXPEDITEUR, DATE_LIEU, OBJET_POSTE, STRUCTURE, LOCALISATION, CORPS, SORTIE). For a
new offer: copy the file, edit only CONFIG, run, deliver PDF. The layout code below CONFIG is
frozen. This is what the user meant by "sauvegarde comme base".

## Per-offer workflow
1. Copy `modele_lettre_generale.py` → `generer_lettre_<offre>.py`.
2. Fill CONFIG from the offer + the candidate's CV/identity.
3. Run, render to PNG (`fitz`/PyMuPDF `get_pixmap(dpi=110)`), verify.

## Verification loop (IMPORTANT — vision can lie)
- Use `vision_analyze` on the rendered PNG for a quick human-style check.
- BUT cross-check alignment with real coordinates: `page.get_text("words")` and inspect `x0`.
  Right-column blocks must have x0 ≈ 286. The vision model has repeatedly MISREPORTED
  right-aligned blocks as left-aligned — trust the coordinates over the vision text.
- Only deliver when BOTH say clean and the page count == 1.

## Pitfalls
- **Formule d'appel symmetry:** the phrase "Madame, Monsieur le Responsable des Ressources
  Humaines" appears in BOTH the destinataire block (top right) AND the formule d'appel line.
  If the user says "supprime madame et des ressources humaines", fix BOTH occurrences, else
  they'll be inconsistent (happened with Bitota's letter).
- **Right-column overflow:** to make a multi_cell wrap onto the NEXT LINE in the SAME right
  column (not snap back to the left margin), use
  `multi_cell(85, 5, txt, new_x=XPos.RIGHT, new_y=YPos.NEXT, align="L", max_line_height=5)`.
  `new_x=XPos.RIGHT` is what keeps subsequent lines in the column.
- **Never compress below 11pt** to fit — the user rejected that ("Tu as fait n'importe quoi").
  Instead shorten the body text or use justified full-width.
- **Accents mandatory** — never strip é→e in French letters.
- **No "généré automatiquement" footer** on user-facing docs.
- Keep the candidate's REAL facts from their CV; only fix grammar/orthography of a rough draft.
- **Signature image**: the user wants "signature manuscrite + nom tapé dessous" (official style).
  Two ways to get the image:
  1. **Generated** from the name: use `scripts/faire_signature.py` helper (in `cv-fr-generation`
     skill) with a script font (GreatVibes/Parisienne/Sacramento/Allura) — output a transparent PNG.
     Add generous margin when cropping the rendered text so the font's descenders/ascenders
     (e.g. K, a tails in GreatVibes) are NOT clipped — offset x by ~30px, y by ~10px, and pad
     width/height by 40-60px before saving.
  2. **Extracted from a screenshot/photo** (preferred when the user already has a signature in a
     phone app): use `scripts/extraire_signature.py` (in `cv-jobsearch-automation` skill) — it
     crops the colored stroke, makes the light background transparent, keeps the real handwritten
     mark. Feed it the screenshot; it auto-detects the blue stroke by default (tune for other hues).
  Insert above the typed name in the right column:
  `pdf.image(SIG, x=COL+(85-sig_w), y=get_y()+3, w=sig_w)` then `cell(85,6,name,align="R")`.
- **PITFALL — size the signature by HEIGHT, not width.** A fixed `w=60` (mm) on a near-square
  extracted signature (~90×69 px) becomes ~46 mm TALL and pushes the letter to a 2nd page. ALWAYS
  set a target height and derive width: `sig_h = 12  # mm`; `sig_w = sig_h * iw / ih`; then
  `pdf.image(SIG, x=..., y=..., w=sig_w)`. This keeps it compact (~12 mm tall) and 1-page-safe.
- **PITFALL — 1-page overflow after adding the image:** even with height sizing, tighten the body
  interline to 4.8 mm (NEVER below 11pt) so the letter stays on one page. Verify page count == 1
  after adding the signature.
- **PITFALL — moveable politeness phrase:** the user relocates the polite formula a LOT. FINAL
  VALIDATED layout for the MSF "Agent d'entretien" / RH letter (2026-07-15, after a 6-turn loop):
  (1) the formule d'appel "Madame, Monsieur le Responsable," sits in the RIGHT column, directly
  under the destinataire block (x=COL ≈ 286pt, y just below destinataire);
  (2) the COMPLETE closing sentence "Veuillez agréer, Madame, Monsieur le Responsable, l'assurance
  de ma considération distinguée." sits at the END of the body, in the LEFT column (x=LEFT, same
  column as "Disponible / conscience / curriculum"), as the LAST multi_cell before the signature.
  NEVER split the sentence, NEVER drop the "Veuillez agréer, Madame, Monsieur le" opener, NEVER
  leave a fragment in the right column. Honor explicit placement over the frozen layout.
- **PITFALL — duplicate destinataire phrase:** when the user wants the block to read
  "A Madame, Monsieur le Responsable des Ressources Humaines" (no trailing "+ STRUCTURE"), do NOT
  append STRUCTURE, else it reads "...des Ressources Humaines de RESSOURCES HUMAINES" (double). Set
  the destinataire string literally and keep LOCALISATION ("KINSHASA / GOMBE") as the underlined line.
  This happened 2026-07-15 with the Agent d'entretien letter.
- **PITFALL — verify phrase relocation with COORDINATES, not vision, before declaring done.**
  The polite formula is the most-moved element and the user will correct you several times
  (2026-07-15: a 6-turn loop on "Veuillez agréer, Madame, Monsieur le Responsable, l'assurance de
  ma considération distinguée."). The ACTUAL journey: he first said the phrase should OPEN the body
  (left column), then corrected "à la fin du corps" (END of body, left column), then caught that I
  had DROPPED the "Veuillez agréer, Madame, Monsieur le" opener, then finally wanted BOTH: the
  formule d'appel "Madame, Monsieur le Responsable," in the RIGHT column (under destinataire) AND
  the COMPLETE closing sentence at the END of the body's LEFT column. FINAL RESOLVED LAYOUT = the
  one described in the moveable-politeness-phrase pitfall above. When he asks to move a phrase:
  (1) implement the COMPLETE sentence at the ONE requested location — never split it or leave a
  fragment elsewhere; (2) immediately dump `page.get_text("words")` and check x0/y0 of BOTH the
  formule d'appel (right column, x0≈286) and the closing sentence (left column, end of body);
  (3) confirm each phrase is present exactly ONCE and at the right x; (4) only then say it's done.
  Do NOT rely on vision_analyze, which misreads right/left alignment. Skipping the coordinate check
  is what triggered "tu n'as pas toutes ta tête".
