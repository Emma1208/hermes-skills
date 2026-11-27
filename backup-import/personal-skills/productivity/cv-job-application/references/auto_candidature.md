# Auto-candidature pack (multi-PJ)

Living scripts in `/root/linkedin_app/`:

## dossier_candidats.json
Manifest of candidates. Each entry: `nom, email, tel, documents:{key:path}`.
Current candidates: `dieudonne` (KAKESA MUDIMBA Dieudonné — CV + letters),
`bitota` (BITOTA MUDIMBA MAMITSHIO — letter only; no CV PDF yet, no email).

## candidature_auto.py
One-shot assembly + send for an offer.

Profiles (each maps to a CV generator + letter generator/output):
 general   -> CV_KAKESA_MUDIMBA.pdf            + Lettre_Motivation_Generale.pdf
 clientele -> generate_cv_clientele.py         + generer_lettre_clientele.py
 bsf       -> generate_cv_bsf.py               + generer_lettre_flash.py
 comptable -> generate_cv_comptable.py         + modele_lettre_generale.py

Usage:
  python3 candidature_auto.py --profil clientele --to recrutement@x.cd \
    --sujet "Candidature Chargé de clients" \
    --objet "Candidature au poste de Chargé de clients" \
    --structure "BANQUE X" --loc "KINSHASA / GOMBE" \
    --pj-supp diplome.pdf

- Regenerates the targeted CV + letter, then sends them (Gmail SMTP, App Password)
  as attachments. `--pj-supp` adds any extra files the site requires; the script
  adapts to N attachments (user requirement: "si un site demande plusieurs
  pièces jointes").
- Tested live 2026-07-14: sent 2 PJ (CV+lettre) to a control address, OK.
- Web-form (portal) upload not wired; add Playwright when a concrete offer exists.

## envoyer_candidature.py
Lower-level: send a fixed set of manifest document keys to an address.
  python3 envoyer_candidature.py --candidat dieudonne --to ADR \
    --sujet "..." --pj CV_Clientele Lettre_Clientele
