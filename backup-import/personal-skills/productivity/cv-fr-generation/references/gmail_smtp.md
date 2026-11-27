# Gmail SMTP send (works) — pitfall + working script

## Pitfall
Normal Gmail password → `SMTPAuthenticationError(534, b'5.7.9 Application-specific password required...')`
Gmail blocks basic-auth SMTP when 2FA is on. The password "DIEUDONNE" / any account password will NOT work.

## Fix
User creates an App Password: https://myaccount.google.com/apppasswords (name e.g. "Hermes") →
gets a 16-char code like `abcd efgh ijkl mnop`. Use that as PWD, not the account password.

## GOTCHA: the code ARRIVES WITH SPACES — strip them
The user types/pastes the code in 4-char chunks WITH spaces, e.g. `hhrz ujtk nfvz kpkk`.
You MUST concatenate to a single 16-char string before `login()`:
```python
PWD = "hhrz ujtk nfvz kpkk".replace(" ", "")   # -> "hhrzujtknfvzkpkk"
```
If you pass it WITH spaces, login fails with SMTPAuthenticationError. Verified working:
strip-spaces variant sent `ENVOYÉ OK -> mbombomudimba@gmail.com` on the first try.

## Working script (envoyer_test.py, /root/linkedin_app)
```python
import smtplib, ssl
from email.message import EmailMessage

EXP = "kakesamudimba@gmail.com"
PWD = "XXXX XXXX XXXX XXXX"   # APP PASSWORD, not account password
TO  = "mbombomudimba@gmail.com"

msg = EmailMessage()
msg["From"] = EXP
msg["To"] = TO
msg["Subject"] = "Candidature - Chargé de clientèle - KAKESA MUDIMBA Dieudonné"
msg.set_content("Madame, Monsieur,\n\nVeuillez trouver ci-joint mon CV et ma lettre de "
                "motivation.\n\nCordialement,\nKAKESA MUDIMBA Dieudonné\nTél : (+243) 818 491 601")

for f, name in [
    ("/root/linkedin_app/CV_KAKESA_MUDIMBA_Clientele.pdf", "CV_KAKESA_MUDIMBA_Clientele.pdf"),
    ("/root/linkedin_app/Lettre_Motivation_Clientele.pdf", "Lettre_Motivation_Clientele.pdf"),
]:
    with open(f, "rb") as fh:
        msg.add_attachment(fh.read(), maintype="application", subtype="pdf", filename=name)

ctx = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
    s.login(EXP, PWD)
    s.send_message(msg)
print("ENVOYÉ OK ->", TO)
```
Note: do NOT store credentials in memory or skill as plaintext beyond what's needed; use only for the live send.
