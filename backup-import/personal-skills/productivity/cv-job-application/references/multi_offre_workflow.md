# Multi-offer batch workflow (CV master + N letters)

Pattern validated 2026-07-15: user asked "prépare CV et lettres pour toutes ces offres"
(≈11 concrete offers from one cron run). Result: 1 master CV + 11 personalized 1-page
letters, all generated from a single batch script.

## Why a batch script (not N copied templates)
The skill's default letter flow is "copy `modele_lettre_generale.py` → change CONFIG →
regenerate" per offer. That is fine for 1 offer, but for N offers it means N files to
maintain and N runs. Prefer ONE script:
- `OFFRES = [dict(poste, structure, loc, url, corps), ...]`
- a `generer(o)` function that builds the §1b official layout + `inserer_signature`
- a loop that writes `Lettre_<SLUG>.pdf` for each.
Live example: `/root/linkedin_app/generer_lettres_batch.py` (11 entries). Reusable template:
`scripts/batch_lettres_offres.py`.

## 1) Source the offers
Daily cron writes to:
- `/root/linkedin_app/offres_brutes.json` — list of `{q,title,snip,url}`. HTML entities
  are encoded (`&#x27;` = ', `&amp;` = &). Decode before printing.
- `/root/linkedin_app/logs/jobs_YYYY-MM-DD.txt` — human-readable grouped by query.

## 2) Filter (CRITICAL — most entries are noise)
From ~60 JSON entries, keep only CONCRETE postings:
- DROP aggregator/portal pages: Optioncarriere, EgoZola (except a real `jobService.php?slug=`
  offer), Congojob, Emploi.cd, UNjobs, Jooble, AfricaWork, CarriereOS, Wikipedia/teacher
  profiles, Facebook pages, PDFs.
- DROP duplicates (same offer appears 2-3×).
- DROP EXPIRED: read the body for `Date limite` / `au plus tard le JJ/MM/AAAA`; compare to
  today. On 2026-07-15 these were already dead: VillageReach (10/07), DRC GOLD (08/05),
  Equity BCDC Finance Manager (15/06).
Survivors on 2026-07-15 (→ 11 letters):
CICR Responsable Comptable (B3) · Equity BCDC Auditeur Senior · BSF Responsable Support
(Admin/Fin/Log/RH) · ONEM Auditeur Interne Assistant · ONEM Responsable de l'Audit Interne ·
ADPI-RDC Comptable (projet énergétique) · eGoZola #40671 Comptable · AMI-RDC/BAfD
Assistante-Comptable PTA-RDC · L'Elite Agency Directeur Audit Interne · Julisha/PwC
Comptable Senior · COREF Consultant International (audit INS RDC).

## 3) Build the master CV (once)
`generer_cv_master.py` → `CV_KAKESA_MUDIMBA_MASTER.pdf`, 1 page, accents OK, signature
vivante, no photo, no footer. Reused for every offer (no per-offer CV needed unless the
user wants a targeted one).

## 4) Per-offer letter body (corps)
Keep the SAME skeleton (par 1 = candidature + formation; par 2 = DRQC vérification pièces +
MSF PUC MED reporting/conformité; par 3 = disponibilité + CV ci-joint). Swap only the
POSTE / STRUCTURE / LOC and re-tailor par 2-3 keywords to the offer (audit vs comptable vs
support). Full bodies live in `generer_lettres_batch.py`.

## 5) Verify (render + crop + vision)
`pypdf` text extraction hides layout bugs (overflow to p2, overlap). Render with `pdftoppm`
or `fitz`, THEN check. For dense 1-page docs, CROP the render into zones (top/header,
body, signature bottom-right, footer) and `vision_analyze` each zone separately — a single
full-page vision call can return a truncated/oversized response (seen: 107 KB repetition
bug). Ask specifically: "1 page ? accents corrects ? signature bleue au-dessus du nom en
gras ? pas de photo ? pas de footer 'généré automatiquement' ? texte non coupé ?"
Confirm page count with `pdfinfo <f> | grep Pages` or `fitz.open(f).page_count`.

## 6) Deliver / send
Send per-offre with `candidature_auto.py` (Gmail SMTP App Password, `--cc` to his Gmail).
Or just hand back the PDFs as MEDIA. CV master is shared; attach it with each letter.
