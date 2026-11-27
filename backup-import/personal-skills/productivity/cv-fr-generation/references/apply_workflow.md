# Automated-apply workflow — multiple attachments
User question (2026-07-14): "si un site d'offre demande plusieurs pièces jointes comme tu fairas pour l'envoi automatique" — i.e. how do we send CV + letter + any other docs automatically when a posting wants several files.

## Decision tree (choose per posting)
| Case | Mechanism | Notes |
|------|-----------|-------|
| Posting gives an **email address** (e.g. `recrutement@x.com`) | ONE email, loop `add_attachment` over all files | Simplest, most reliable. Subject = "Candidature - [poste] - [NOM]". |
| Posting is an **online form** (makesense, job board, ATS) | Pilot a browser, fill fields, drop each file in its correct upload slot | Multiple upload fields are fine. Map CV→CV slot, letter→letter slot. |
| Unknown | Inspect the site, auto-pick A or B | User does nothing. |
| Posting demands **email + imposed filename convention + a mandatory web-form validation** (e.g. KPMG RDC: "Envoyez votre CV à CD-Recrutement@kpmg.com nommé CV_Nom&Prénom_AD Audit" AND "Assurez-vous d'avoir validé le formulaire de renseignement") | Do ALL THREE: (a) one email with all attachments, (b) rename each PJ to the imposed name at `add_attachment` time (keep source files untouched on disk), (c) tell the user to also validate the site form — email alone is rejected | Hybrid case. CC the candidate's Gmail. Flag the form step + deadline prominently; email is necessary but NOT sufficient. |

## Preferred setup
1. Build a "dossier type" on disk first: `CV_KAKESA_MUDIMBA_[offre].pdf`, `Lettre_Motivation_[offre].pdf`, plus any extras (diplômes, certificats).
2. The send/apply step lists those files and attaches/updates all of them — never hand-type per file.

## Email multi-attach snippet (extends gmail_smtp.md)
```python
files = [
    ("/root/linkedin_app/CV_KAKESA_MUDIMBA.pdf", "CV_KAKESA_MUDIMBA.pdf"),
    ("/root/linkedin_app/Lettre_Motivation_X.pdf", "Lettre_Motivation_X.pdf"),
    # add任意 extras:
    # ("/root/linkedin_app/diplome.pdf", "diplome.pdf"),
]
for f, name in files:
    with open(f, "rb") as fh:
        msg.add_attachment(fh.read(), maintype="application", subtype="pdf", filename=name)
```
PWD = app password with spaces STRIPPED (see gmail_smtp.md).

## Caveats
- LinkedIn scraping/postulate is BLOCKED (captcha). Email + form-fill on other sites is fine — do NOT claim "browser piloting impossible" (that old note was wrong; corrected 2026-07-14).
- For forms, confirm each upload field landed the right file before submitting; screenshot-verify if unsure.
