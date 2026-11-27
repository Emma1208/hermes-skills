#!/usr/bin/env python3
"""Reusable Gmail SMTP sender for the job-application dossier.

USAGE:
  python3 references/email_send.py <TARGET_EMAIL> <OFFER_TAG>
    <TARGET_EMAIL> : recipient HR address
    <OFFER_TAG>    : suffix used in filenames, e.g. Clientele, BSF, Comptable
  The script reads APP_PASSWORD from the APP_PWD env var (NOT hardcoded).
  It attaches:
    /root/linkedin_app/CV_KAKESA_MUDIMBA_<OFFER_TAG>.pdf
    /root/linkedin_app/Lettre_Motivation_<OFFER_TAG>.pdf

GMAIL NOTE: PWD must be a 16-char App Password from
https://myaccount.google.com/apppasswords — the normal account password FAILS
with SMTPAuthenticationError 534 (2FA on). Do not retry the real password.
"""
import os, sys, smtplib, ssl
from email.message import EmailMessage

EXP = "kakesamudimba@gmail.com"
PWD = os.environ.get("APP_PWD", "")
if not PWD:
    sys.exit("Set APP_PWD env var to the Gmail App Password (16 chars).")

if len(sys.argv) < 3:
    sys.exit("Usage: python3 email_send.py <TARGET_EMAIL> <OFFER_TAG>")
TO, TAG = sys.argv[1], sys.argv[2]

base = "/root/linkedin_app"
cv = f"{base}/CV_KAKESA_MUDIMBA_{TAG}.pdf"
lettre = f"{base}/Lettre_Motivation_{TAG}.pdf"
for p in (cv, lettre):
    if not os.path.exists(p):
        sys.exit(f"Missing file: {p}")

msg = EmailMessage()
msg["From"], msg["To"] = EXP, TO
msg["Subject"] = f"Candidature - {TAG} - KAKESA MUDIMBA Dieudonné"
msg.set_content(
    "Madame, Monsieur,\n\n"
    f"Veuillez trouver ci-joint mon CV et ma lettre de motivation pour le poste de {TAG}.\n\n"
    "Cordialement,\nKAKESA MUDIMBA Dieudonné\nTél : (+243) 818 491 601\n"
    "Email : kakesamudimba@gmail.com"
)
for f, n in [(cv, f"CV_KAKESA_MUDIMBA_{TAG}.pdf"),
             (lettre, f"Lettre_Motivation_{TAG}.pdf")]:
    with open(f, "rb") as fh:
        msg.add_attachment(fh.read(), maintype="application", subtype="pdf", filename=n)

ctx = ssl.create_default_context()
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
        s.login(EXP, PWD)
        s.send_message(msg)
    print(f"ENVOYÉ OK -> {TO}")
except Exception as e:
    print("ERREUR:", repr(e))
