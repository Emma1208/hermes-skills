#!/usr/bin/env python3
"""Envoie un dossier de candidature par email Gmail (SMTP SSL 465) avec N pieces jointes
et une copie (Cc) optionnelle. Mode de soumission reel ("C" du pack de candidature).

Usage :
  python3 envoyer_candidature_pj.py --to recruteur@exemple.cd \
      --sujet "Candidature RESPONSABLE TECHNIQUE" \
      --cc kakesamudimba@gmail.com \
      --pj CV.pdf Lettre.pdf [diplome.pdf ...]

Credits : Gmail app-password (PAS le mot de passe du compte). Genere a
https://myaccount.google.com/security -> App passwords.
"""
import argparse, smtplib, ssl
from email.message import EmailMessage
from pathlib import Path

EXP = "kakesamudimba@gmail.com"      # expediteur (ton compte Gmail)
PWD = "APP_PASSWORD_ICI"              # remplacer par l'app-password valide


def envoyer(to, sujet, pj_cles, cc=None, corps=None):
    msg = EmailMessage()
    msg["From"] = EXP
    msg["To"] = to
    if cc:
        msg["Cc"] = cc
    msg["Subject"] = sujet
    if corps is None:
        corps = (
            "Madame, Monsieur,\n\n"
            f"Veuillez trouver ci-joint mon dossier de candidature "
            f"({len(pj_cles)} pièce(s) : CV et lettre de motivation).\n\n"
            "Cordialement,\nKAKESA MUDIMBA Dieudonné\n"
            "Tél : (+243) 818 491 601\nEmail : kakesamudimba@gmail.com"
        )
    msg.set_content(corps)

    for p in pj_cles:
        fp = Path(p)
        if not fp.exists():
            raise SystemExit(f"PJ manquante: {p}")
        with open(fp, "rb") as fh:
            msg.add_attachment(fh.read(), maintype="application",
                               subtype="pdf", filename=fp.name)

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
        s.login(EXP, PWD)
        s.send_message(msg)
    dest = f"{to}" + (f" (Cc: {cc})" if cc else "")
    print(f"ENVOYÉ OK -> {dest}  ({len(pj_cles)} PJ: {[Path(x).name for x in pj_cles]})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True)
    ap.add_argument("--sujet", required=True)
    ap.add_argument("--cc", default=None)
    ap.add_argument("--pj", nargs="+", required=True, help="chemins des PDF a joindre")
    ap.add_argument("--corps", default=None)
    a = ap.parse_args()
    envoyer(a.to, a.sujet, a.pj, cc=a.cc, corps=a.corps)
