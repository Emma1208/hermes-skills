---
name: attestation-modele-generation
description: Generate branded A4 attestations, diplomas, training certificates, or membership/ID-style cards (MODELES VIERGES) for Emmanuel with Pillow + fpdf2 at 300 DPI, French accents via DejaVu, plus the HARD guardrail against reproducing real official state documents (CENI voter card, passport, national ID, a real institution's genuine diploma). Use when Emmanuel asks to make, create, or clone an attestation, diploma, certificat, carte, or any document model.
triggers:
  - "fais moi une attestation, diplome, certificat, ou carte"
  - "crée une attestation de formation, fin de service, ou travail"
  - "clone ou copie ce document ou cette carte (with a PDF or image attached)"
  - any request implying reproduction of an existing official-looking document
---

# Attestation / Modèle document generation (Emmanuel)

Generate clean, creative, branded **modèles vierges** (blank, fill-in-the-blank documents)
for Emmanuel's own use / PAO. The edition of real official state documents is OFF-LIMITS —
see Guardrail below.

## Environment note (one-time setup, NOT a constraint)
On this Ubuntu 26.04 aarch64 box the doc/imaging stack is installed via apt:
`gimp inkscape imagemagick poppler-utils ghostscript fonts-dejavu fonts-liberation`
and Python libs via pip: `fpdf2 pillow reportlab pikepdf pdf2image`.
DejaVu fonts live at `/usr/share/fonts/truetype/dejavu/` and carry correct French accents
(use `DejaVuSans.ttf`, `DejaVuSans-Bold.ttf`, `DejaVuSerif-Bold.ttf`).
`apt-get` can intermittently hit the 180s foreground clamp — run big installs with
`terminal(background=true, notify_on_complete=true)`; a prior interrupted run may leave
dpkg locked — resolve with `dpkg --configure -a` then re-run (it is idempotent).

## GUARDRAIL — non-negotiable (FIRST-CLASS, learned 2026-07-14)
Emmanuel may hand you a photo/PDF of a REAL official document and say "clone / copie ça".
Distinguish the two cases and act accordingly:

- **REAL official state identity / credential — DO NOT REPRODUCE.** Examples seen:
  RDC **CENI carte d'électeur** (serial number, QR code, RDC flag, CENI signature),
  passport, national ID card, a real university/state diploma presented as authentic.
  Recreating these — even with his own real name — is counterfeiting an official document
  and is illegal in the RDC and most jurisdictions. The CENI alone issues voter cards.
  → Refuse plainly (no lecture), then offer the legitimate alternative below.
- **Legitimate alternative you CAN build:** a **modèle with his OWN branding**
  (e.g. "KPGR"), no state logo / no official QR / no real serial / clearly labelled
  "Modèle d'attestation". Filling a blank modèle with his own name for his own records
  is normal PAO. A blank diploma/cert with a fictional or his-own-org name is fine as a
  *modèle*; do NOT make a fake diploma that impersonates a real institution to deceive an
  employer.

Plain refusal script (French, direct, no moralizing):
"Je ne clone pas / ne reproduis pas ta vraie carte d'électeur CENI — c'est un document
d'identité d'État protégé (numéro de série, QR, drapeau, signature CENI) ; le refaire =
contrefaçon, illégal même avec ton nom. Par contre je peux te faire une carte / attestation
MODÈLE avec ton propre en-tête KPGR, vierge à remplir." Then give A/B/C/D choices.

## Workflow (autonomous — Emmanuel wants the artifact, not a tutorial)
1. Generate with Pillow at **A4 2480×3508 px @ 300 DPI** (or card ratio 595×1319 pts).
   Build the layout in code (see `templates/attestation_a4_kpgr.py` — copy & modify).
2. Save PNG (300 dpi) AND PDF (`img.convert("RGB").save(out, "PDF", dpi=(300,300))`).
3. **Verify visually** with `vision_analyze` on the PNG: check alignment, overlaps,
   overflow, accent correctness. Fix and re-run until clean.
4. **Deliver**: he prefers a **shareable web link** over a Telegram file.
   `curl -s -F "file=@X.pdf" https://tmpfiles.org/api/v1/upload` → returns a ~24h URL
   (tmpfiles.org is the only host that worked; 0x0.st/litterbox/file.io/transfer.sh FAILED).
   Tell him links expire. Attach the PDF/PNG as fallback if the link doesn't reach him.
5. Keep the generator script in `/root/` so he can ask for tweaks (colors, text, batch).

## Design conventions that worked (KPGR attestation example)
- Identity: emblem = colored disc + monogram + a relevant icon (cross humanitaire + cube
  logistique for a logistics cert). Two-color palette (bleu + orange), double decorative
  frame, DejaVu Serif for titles, DejaVu Sans for body.
- Structure: en-tête (logo+org) → titre centré → corps paragraph → champs vierges
  (Nom, Référence, Période, Durée, Lieu) as label + grey fill-in line → mentions légales
  → signatures (2 blocks) → decorative sceau "CERTIFIÉ" + "Modèle d'attestation" footer.
- Body text ≥ readable size (he complained about "petits" text before → keep ≥ ~40px on a
  2480px-wide A4, i.e. ≈ 13pt+). Accents MUST be correct (never strip é→e).

## Pitfalls
- Don't label a branded modèle as an official state document or add real seals/QR of a
  real authority — that crosses the guardrail.
- Don't send only a Telegram attachment if he asked for a link; prefer tmpfiles.org.
- Don't over-explain the refusal — one line + A/B/C/D choices, then build what he picks.
- When he sends a sample doc/image to "clone", READ it first (pdf2image → PNG, vision_analyze)
  to extract layout before reproducing the *style* as a clean modèle.
- **BRAND LOGO reproduction boundary (learned 2026-07-15):** reproducing a recognizable
  company/NGO LOGO is NOT the same as counterfeiting a state ID. Two sub-rules:
  (a) **Employer / NGO logo for the applicant's OWN genuine application is OK.** When Emmanuel
  is actually applying to that org (e.g. he asked to reproduce the MSF red-cross logo to put on
  his own MSF application pack), drawing a clean PNG of that logo (transparent background, his own
  use) is legitimate PAO — do it. Verify the result with `getpixel` alpha check (corner alpha=0 =
  transparent) + vision_analyze.
  (b) **Do NOT reproduce a real COMMERCIAL company's brand/mark to impersonate it** (e.g. a
  French "alternance" training-site brand handed as a style sample). Reproduce the *visual style*
  (palette, monogram shape, layout) as a NEUTRAL "Centre de formation professionnelle" header,
  clearly a modèle — never paste the real trademarked name/logo. Explain in one line, then build
  the neutral version. Impersonating a real company to deceive an employer is the line not to cross.
- **PITFALL — transparent PNG verification:** when generating a logo/icon on a transparent
  canvas (RGBA), the vision model shows it on a WHITE background and may report "fond blanc" while
  the file is actually transparent. Always confirm transparency programmatically:
  `python3 -c "from PIL import Image; im=Image.open(f); print(im.getpixel((5,5))[-1])"` → expect 0
  (transparent) at a corner and 255 at a logo pixel. State clearly to the user the file IS
  transparent even though vision shows white.
