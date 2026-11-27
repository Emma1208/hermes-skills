---
name: cv-lettre-generation
description: Generate French CV and cover letters (lettre de motivation) as PDF + editable ODT for user KAKESA MUDIMBA Dieudonné (Emmanuel-Dieudonné). Reuse HIS exact model structure (never invent a layout), embed his handwritten signature, and verify the render. Use when the user asks for a CV, a lettre de motivation, or to apply to a job — including rebuilding from his model PDFs.
---

# CV & Lettre de motivation — KAKESA

## When to use
The user asks for a CV, a lettre de motivation, or to apply to a job. He supplies his own model files (usually PDF) which you MUST reuse **exactly in structure** — you only adapt the wording/content to the target offer. This session started from scratch after all prior models/skills were deleted, so always confirm you have his current models in `~/Candidatures/Modèles/` before generating.

## Hard rules (from past corrections — he gets angry if violated)
1. **NEVER invent a new layout.** A prior session used a fresh HTML layout instead of his retained model and the user was furious ("je crois que te vraiment un fou"). Reuse his model's section order and headings verbatim; fill only the text.
2. **No photo in the CV** (stated preference).
3. **Accents must be correct** — never strip é→e. Output is French.
4. **Signature is mandatory.** He will call you out ("Tu oublies la signature"). Always embed it.
5. **Do NOT send the application.** Prepare and show the docs only. Wait for an explicit "envoie" before any submission (form fill, email, portal).

## Layout preferences (HARD — confirmed this session)
- **Signature ABOVE the typed name, BOTH right-aligned** (image first, name just below, same right edge). This is the user's explicit correction ("La signature doit être vraiment au dessus de nom").
- **Letter "Objet" is LEFT-aligned**, separate from the right-aligned recipient/date block ("L'object est à gauche").
- CV target **2 pages max** by default.
- Full name forms: `KAKESA MUDIMBA Emmanuel-Dieudonné`; split Nom=KAKESA / Poste nom=MUDIMBA / Prénom=Emmanuel-Dieudonné. Born 12/08/1998 at Bunia (Ituri). Tel +243 818 491 601, email kakesamudimba@gmail.com.

## The reliable rendering pipeline (KEY TECHNIQUE — learned the hard way)
**ODT image embedding is UNRELIABLE with `soffice --headless --convert-to pdf`.** Across a long debug session we confirmed: even with a correct `<draw:frame>`, a defined `FrSig` graphic style in `styles.xml`, the `Pictures/...png` manifest entry, and the `draw:`/`svg:`/`xlink:` namespaces all present, LibreOffice **silently drops the embedded image at render time**. The frame is in the XML; the pixels are not in the PDF. Do not waste time on ODT image frames.

**Use HTML → PDF instead (works every time):**
- Build the document as one HTML file with an inline `<style>` block (A4 `@page { size: A4; margin: ... }`).
- Embed the signature as a **base64 data URI**: `<img src="data:image/png;base64,....">`. No external path, no ODT frame — this is the reliable fix.
- Convert to PDF: `soffice --headless --convert-to pdf --outdir <dir> <file>.html`
- Also produce an editable ODT: `soffice --headless --convert-to odt --outdir <dir> <file>.html` (the base64 img survives into the ODT too, so it stays editable AND renders).
- Inject the base64 string via `sed "s|__SIG__|data:image/png;base64,$B64|g"` from a text file, or inline in the HTML.

### Signature acquisition (recurring blocker)
The user keeps his signature in a phone "Signatures" app. **A screenshot of that app is NOT usable** (UI chrome around it, low quality, can't isolate). To get the real file:
- Ask him to **EXPORT/SHARE the signature as a PNG** from the app (share / save-image → Downloads or Images), then send that `.png` file (not a screenshot).
- Fallback: handwritten signature on white paper, photo on a white background in good light — then isolate/clean it.
- If a previous session left a `signature_seule.png`, reuse it (but it may have been deleted on a "clean slate" request).

## His model structures (re-confirm against the actual file each time — they can change)
CV model (`CV_KAKESA_MUDIMBA_modele.pdf`): I. Infos perso · II. Parcours pro · III. Domaines de compétence · IV. Études · V. Formations · VI. Langues · **(NO VII — jumps straight to)** · VIII. Personnes de référence · + déclaration d'honneur + signature line. Prénom is **Emmanuel-Dieudonné** (not just "Dieudonné").
Letter model (`Lettre_Modele_KAKESA.pdf`, the "Serge Mbulu" layout): sender block top-left (name / address / tel / email), date top-right ("Kinshasa, le JJ / MM / AAAA"), recipient block top-right ("A Monsieur/Madame le…", "Objet : …", city), 4 body paragraphs, closing formule, signature (name) bottom-right.

## Workflow
1. Receive the model files; save to `~/Candidatures/Modèles/`.
2. Extract structure with `pdftotext -layout <model>.pdf -` (pdftotext is available).
3. Build `cv_base.html` and `lettre_base.html` from `templates/`, filling content for the target offer but keeping his section order/headings.
4. Read signature PNG → base64 → inject into both `__SIG__` slots.
5. `soffice --headless --convert-to pdf` and `--convert-to odt` into `~/Candidatures/Brouillons/`, renaming to clear names (e.g. `CV_<OFFRE>_KAKESA.pdf`).
6. **Verify visually**: `pdftoppm -png -r 110 <file>.pdf /tmp/check.png` then `vision_analyze` the bottom region — confirm the signature pixels actually render. XML presence is NOT proof of render.
7. Show the user the PDFs. Do not send.

## Pitfalls
- **Right-aligning a signature image in soffice is unreliable.** `text-align:right` on a block `<img>` and `float:right` BOTH render inconsistently — the signature ends up centered while the name is right-aligned (confirmed this session across multiple regenerations). **Use a `<table>` with a 62% spacer cell + 38% right cell holding the image then the name; set the image `display:block; margin-left:auto`.** See `templates/cv_base.html` / `templates/lettre_base.html` for the working pattern.
- Don't trust "the frame/image is in the XML" as proof it renders — always render and vision-check the bottom of the page.
- Avoid external `file:///` image paths in HTML for headless conversion; base64 is safe.
- `soffice` convert may exit code 2 on first PDF render for multi-page docs; re-run or render pages separately with `pdftoppm` — not a real failure.
- The vision auxiliary model is unreliable for fine alignment questions (gave contradictory "centered" vs "left" on the same render). Trust the CSS; ask the user to confirm on their screen.
- The user may ask to "delete everything and restart from zero" — that includes his model PDFs AND the skills. Recreate models from what he re-sends; recreate this skill's knowledge from the conversation.

## References
- `references/modeles.md` — extracted text of his CV and letter models (section-by-section), for quick structural check.
- `templates/cv_base.html` — known-good HTML skeleton (A4, blue section headers, `__SIG__` base64 slot). Copy and fill.
- `templates/lettre_base.html` — known-good letter skeleton (Serge Mbulu layout, `__SIG__` slot).
