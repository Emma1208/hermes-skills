---
name: kakesa-cv-letter
description: Generate CV + cover letter (lettre de motivation) PDFs/ODTs for Emmanuel-Dieudonné KAKESA MUDIMBA (Kinshasa/RDC, compta-finance-audit profile). Covers his EXACT retained model structures, the reliable signature-embedding method (HTML+base64, NOT ODT frame reassembly), signature extraction from a phone JPG, output locations, and the never-auto-send rule. Use whenever he asks for a CV, a lettre de motivation, or to apply to a job.
---

# KAKESA — CV & Lettre de motivation

## Trigger
User asks for a CV, a lettre de motivation, or to apply to a job (for himself: Emmanuel-Dieudonné KAKESA MUDIMBA). Profile: comptable / gestion financière / audit / enseignant, Kinshasa.

## HARD RULE 1 — Respect the EXACT model structure (do NOT invent a layout)
The user gets upset ("tu es fou") if you generate a fresh/new layout. He has **retained model files** that MUST be used as the structural template; you only adapt the *content*.

Current model files (in `~/Candidatures/Modèles/`):
- `CV_KAKESA_MUDIMBA_modele.pdf` — CV structure:
  - **I. INFORMATIONS PERSONNELLES** (Nom/Poste nom/Prénom/Sexe/Lieu+date nais./État civil/Nationalité/Adresse/Tél/Email)
  - **II. PARCOURS PROFESSIONNEL**
  - **III. DOMAINES DE COMPÉTENCE**
  - **IV. ÉTUDES FAITES**
  - **V. FORMATIONS ACADÉMIQUE**
  - **VI. LANGUES**
  - *(NO VII — the model skips from VI to VIII)*
  - **VIII. PERSONNES DE RÉFÉRENCE**
  - End: "Je jure sur l'honneur..." + "Fait à Kinshasa, le ..." + signature.
  - Prénom is **Emmanuel-Dieudonné** (keep both parts).
- `Lettre_Modele_KAKESA.pdf` — "Serge Mbulu" letter layout:
  - Expéditeur block (left): Nom, adresse, Tel, Email
  - Date (right): "Kinshasa, le JJ/MM/AAAA"
  - Destinataire (right): "À Monsieur/Madame le…", "Objet : …", ville
  - Body: 4 paragraphs (soumission candidature / diplôme+intérêt / expérience+qualités+motivation / remerciement+"Veuillez trouver ci-joint mon CV")
  - Formule: "Veuillez agréer, … l'assurance de ma considération distinguée."
  - Signature (right): typed name.

Workflow when a job offer arrives: read the offer, adapt the SAME sections, put the new job title/ref in the CV header line and the letter destinataire/objet. Keep accents correct (É, è, ô, æ in "vitæ"). CV = 2 pages is fine.

## HARD RULE 2 — Signature embedding: use HTML + base64, NEVER ODT frame reassembly
The user's original ODT models referenced the signature by an EXTERNAL path (`/root/Candidatures/Modèles/signature_seule.png`) that was never embedded — so the signature never rendered, even in his own model. Attempts to fix by rebuilding the ODT (adding `<draw:frame>` + defining `FrSig` style in styles.xml + adding the image to META-INF/manifest.xml + embedding the PNG in Pictures/) ALL FAILED: LibreOffice silently refuses to render the reassembled frame.

**Reliable method (this is what works):**
1. Build the document as HTML (any clean HTML/CSS, A4 `@page` margins).
2. Embed the signature as a **base64 data URI** in the `<img src="data:image/png;base64,....">` — no external path, no ODT.
3. Convert with `soffice --headless --convert-to pdf --outdir <dir> file.html` (and optionally `... --convert-to odt` for an editable copy).
4. Verify the rendered PDF bottom with vision_analyze to confirm the blue signature shows.

Signature asset: `~/Candidatures/Modèles/signature_seule.png` (transparent-bg PNG of his blue handwritten signature). See `references/signature_recipe.md` for the exact base64-embed HTML snippet and the PIL extraction script.

## HARD RULE 3 — Never auto-send
Prepare and SHOW documents only. Do NOT submit to any form/portal/email unless the user explicitly says "envoie"/"OK envoie". Past incident: agent applied to Orange RDC solo after a simple "A". Also: when sending email on his behalf, CC his Gmail (kakesamudimba@gmail.com) — but that only applies if/when he actually requests sending.

## Output locations
- Generated docs → `~/Candidatures/Brouillons/` (e.g. `CV_COOPI_Nutritionniste_KAKESA.pdf` + `.odt`, `Lettre_...`).
- Models → `~/Candidatures/Modèles/`.
- Dossier convention (from memory): `~/Candidatures/{Modèles,Envoi,Brouillons,Archives}`.

## Communication style for this user
Result-first, offer A/B/C/D choices, minimal technical detail. He has said "je ne comprends rien" when over-explained. Lead with the deliverable, then a short option list.

## Verification
After generating, render the PDF to PNG (`pdftoppm -png -r 100 file.pdf /tmp/x.png`) and vision_check: (a) all model sections present, (b) accents correct, (c) signature visible at bottom. Only then show the user.
