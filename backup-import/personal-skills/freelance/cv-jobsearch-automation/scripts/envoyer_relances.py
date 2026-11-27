#!/usr/bin/env python3
"""ENVOIE les relances de candidatures validees (manuel, jamais auto).

Usage:
  python3 envoyer_relances.py          -> etat, n'envoie rien
  python3 envoyer_relances.py tout     -> envoie toutes les 'en attente'
  python3 envoyer_relances.py 1 3 5    -> envoie les relances #1 #3 #5

Chaque relance envoyee passe en status 'envoye' (plus jamais proposee).
FILL: EXP, PWD (app-password Gmail, meme que §9).
"""
import sys, json, smtplib, ssl, datetime
from email.message import EmailMessage

EXP = "FILL@gmail.com"
PWD = "FILL_APP_PASSWORD"
PENDING = "/root/linkedin_app/pending_relances.json"


def load():
    with open(PENDING) as f:
        return json.load(f)


def save(p):
    json.dump(p, open(PENDING, "w"), indent=2, ensure_ascii=False)


def envoyer_un(to, sujet, corps):
    msg = EmailMessage()
    msg["From"] = EXP
    msg["To"] = to
    msg["Subject"] = sujet
    msg.set_content(corps)
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
        s.login(EXP, PWD)
        s.send_message(msg)


def main():
    p = load()
    items = p.get("items", [])
    if len(sys.argv) < 2:
        attente = [it for it in items if it["status"] == "en attente"]
        envoye = [it for it in items if it["status"] == "envoye"]
        print(f"ETAT: {len(attente)} en attente | {len(envoye)} deja envoyees")
        for it in attente:
            print(f"  #{it['id']} -> {it['to']}  [{it['relance_sujet']}]")
        return

    if sys.argv[1].lower() == "tout":
        cibles = [it["id"] for it in items if it["status"] == "en attente"]
    else:
        cibles = [int(x) for x in sys.argv[1:] if x.isdigit()]

    by_id = {it["id"]: it for it in items}
    envoyes = 0
    for cid in cibles:
        it = by_id.get(cid)
        if not it or it["status"] != "en attente":
            print(f"# {cid}: ignore (deja envoye ou inconnu)")
            continue
        try:
            envoyer_un(it["to"], it["relance_sujet"], it["relance_corps"])
            it["status"] = "envoye"
            it["date_envoi"] = datetime.datetime.now().isoformat()
            envoyes += 1
            print(f"ENVOYE #{cid} -> {it['to']}")
        except Exception as e:
            print(f"ERREUR #{cid} -> {it['to']}: {e}")
    save(p)
    print(f"\n{envoyes} relance(s) envoyee(s).")


if __name__ == "__main__":
    main()
