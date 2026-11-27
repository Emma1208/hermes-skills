#!/usr/bin/env python3
"""PACK CLE EN MAIN - candidature automatique multi-pieces (mode C, email).
REUTILISABLE : pour une offre, genere le CV cible + la lettre cible (depuis les
modeles existants) puis envoie le tout par email avec AUTANT de PJ que demande le site.

PRINCIPE :
  - PROFILS = dict qui mappe chaque profil -> (generateur CV, sortie CV,
    generateur lettre, sortie lettre). Ajoute un profil = ajoute une ligne.
  - Genere d'abord (subprocess) puis envoie (smtp gmail app-password).
  - --pj-supp permet d'ajouter N fichiers (diplome, certificat...) : le script
    s'adapte au nombre de PJ demande par le site.

USAGE :
  python3 candidature_auto.py --profil flash --to rh@flash.one \
      --sujet "Candidature RESPONSABLE TECHNIQUE" \
      --pj-supp diplome.pdf

CREDENTIALS : EXP = email Gmail, PWD = app-password SANS espaces.
"""
import argparse, subprocess, smtplib, ssl
from email.message import EmailMessage
from pathlib import Path

EXP = "kakesamudimba@gmail.com"
PWD = "hhrzujtknfvzkpkk"  # app password Gmail (16 chars, SANS espaces)

BASE = "/root/linkedin_app"

# >>> PROFILS : ajouter une ligne pour chaque offre ciblee <<<
PROFILS = {
    "general":   {"cv_gen": None, "cv_out": f"{BASE}/CV_KAKESA_MUDIMBA.pdf",
                  "let_gen": f"{BASE}/modele_lettre_generale.py",
                  "let_out": f"{BASE}/Lettre_Motivation_Generale.pdf"},
    "clientele": {"cv_gen": f"{BASE}/generate_cv_clientele.py", "cv_out": f"{BASE}/CV_KAKESA_MUDIMBA_Clientele.pdf",
                  "let_gen": f"{BASE}/generer_lettre_clientele.py",
                  "let_out": f"{BASE}/Lettre_Motivation_Clientele.pdf"},
    "bsf":       {"cv_gen": f"{BASE}/generate_cv_bsf.py", "cv_out": f"{BASE}/CV_KAKESA_MUDIMBA_BSF.pdf",
                  "let_gen": f"{BASE}/generer_lettre_flash.py",
                  "let_out": f"{BASE}/Lettre_Motivation_Flash.pdf"},
    "flash":     {"cv_gen": f"{BASE}/generate_cv_flash.py", "cv_out": f"{BASE}/CV_KAKESA_MUDIMBA_Flash.pdf",
                  "let_gen": f"{BASE}/generer_lettre_flash.py",
                  "let_out": f"{BASE}/Lettre_Motivation_Flash.pdf"},
    "comptable": {"cv_gen": f"{BASE}/generate_cv_comptable.py", "cv_out": f"{BASE}/CV_KAKESA_MUDIMBA_Comptable.pdf",
                  "let_gen": f"{BASE}/modele_lettre_generale.py",
                  "let_out": f"{BASE}/Lettre_Motivation_Generale.pdf"},
}


def generer(profil, objet, structure, loc):
    p = PROFILS[profil]
    if p["cv_gen"]:
        subprocess.run(["python3", p["cv_gen"]], check=True, cwd=BASE)
    if Path(p["let_gen"]).exists():
        subprocess.run(["python3", p["let_gen"]], check=True, cwd=BASE)
    return p["cv_out"], p["let_out"]


def envoyer(to, sujet, pjs, corps):
    msg = EmailMessage()
    msg["From"] = EXP
    msg["To"] = to
    msg["Subject"] = sujet
    msg.set_content(corps)
    for f in pjs:
        fp = Path(f)
        if not fp.exists():
            raise SystemExit(f"PJ manquante: {f}")
        with open(fp, "rb") as fh:
            msg.add_attachment(fh.read(), maintype="application", subtype="pdf", filename=fp.name)
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
        s.login(EXP, PWD)
        s.send_message(msg)
    print(f"ENVOYE OK -> {to}  ({len(pjs)} PJ: {[Path(x).name for x in pjs]})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--profil", required=True, choices=list(PROFILS))
    ap.add_argument("--to", required=True)
    ap.add_argument("--sujet", required=True)
    ap.add_argument("--objet", default="")
    ap.add_argument("--structure", default="")
    ap.add_argument("--loc", default="KINSHASA / GOMBE")
    ap.add_argument("--pj-supp", nargs="*", default=[], help="PJ supplementaires (chemins)")
    ap.add_argument("--corps", default=None)
    a = ap.parse_args()

    cv, lettre = generer(a.profil, a.objet, a.structure, a.loc)
    pjs = [cv, lettre] + a.pj_supp

    if a.corps is None:
        a.corps = (
            "Madame, Monsieur,\n\n"
            f"Veuillez trouver ci-joint mon dossier de candidature "
            f"({len(pjs)} piece(s) : CV et lettre de motivation"
            f"{', plus documents complementaires' if a.pj_supp else ''}).\n\n"
            "Cordialement,\nKAKESA MUDIMBA Dieudonne\n"
            "Tel : (+243) 818 491 601\nEmail : kakesamudimba@gmail.com"
        )
    envoyer(a.to, a.sujet, pjs, a.corps)
