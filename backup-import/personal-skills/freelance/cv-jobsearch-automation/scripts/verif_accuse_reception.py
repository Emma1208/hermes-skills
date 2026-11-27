#!/usr/bin/env python3
"""Watchdog : verifie les accuse de reception des candidatures envoyees.

Concu pour tourner en cron (no_agent=True) : il affiche UNIQUEMENT quand
un nouvel accuse est trouve. Stdout vide = silence (rien n'est livre au user),
c'est le comportement watchdog attendu.

PIEGES Gmail/IMAP resolus (cf SKILL.md §10) :
  - Le dossier "Messages envoyes" porte un accent -> son nom IMAP est deja
    en UTF-7 modifie ([Gmail]/Messages envoy&AOk-s). NE PAS le re-encoder.
  - Le '/' dans le nom casse le parsing IMAP -> il faut QUOTER le nom.
  - fetch RFC822 par mail = timeout sur 1294 msgs. Utiliser
    (BODY.PEEK[HEADER]) + fenetre 14j.
"""
import imaplib, email, json, os, re
from email.header import decode_header
from datetime import datetime, timedelta

# ===================== CONFIG =====================
EXP = "kakesamudimba@gmail.com"
PWD = "APP_PASSWORD_HERE"          # app-password Gmail (cf candidature_auto.py)
STATE = "/root/linkedin_app/.accuse_state.json"   # fichier d'etat des deja-vus
WINDOW_DAYS = 14
# ==================================================

# Expediateurs a ignorer (spam / promo / alertes)
BLOCKLIST = ("linkedin.com", "instagram.com", "facebook.com", "noreply@",
             "mail.", "info.n8n", "trade-ideas", "betibet", "promo@", "n8n.io")

# Mots-cles d'accuse de reception
ACK_KEYWORDS = ["accusé", "accuse", "réception", "reception",
                "avons reçu", "avons recu", "bien reçu", "bien recu"]


def decode(s):
    if s is None:
        return ""
    out = []
    for b, enc in decode_header(s):
        if isinstance(b, bytes):
            out.append(b.decode(enc or "utf-8", "ignore"))
        else:
            out.append(str(b))
    return " ".join(out)


def parse_addr(s):
    m = re.search(r"<([^>]+)>", s or "")
    if m:
        return m.group(1).lower().strip()
    return (s or "").strip().lower()


def domain(addr):
    return addr.split("@")[-1] if "@" in addr else ""


def company_name(fromhdr):
    name = decode(fromhdr)
    addr = parse_addr(fromhdr)
    disp = name.replace(f"<{addr}>", "").strip().strip('"').strip()
    if disp and "@" not in disp:
        return disp
    return domain(addr)


def fetch_sent():
    m = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    m.login(EXP, PWD)
    # Noms deja en UTF-7 modifie ; le '/' casse le parsing -> on QUOTE.
    candidates = ['"[Gmail]/Messages envoy&AOk-s"',
                  '"[Gmail]/Sent Mail"', '"[Gmail]/Sent"', '"Sent"']
    box = None
    for c in candidates:
        try:
            m.select(c)
            box = c
            break
        except Exception:
            continue
    if box is None:
        raise SystemExit("Dossier Messages envoyes introuvable")
    since = (datetime.now() - timedelta(days=WINDOW_DAYS)).strftime("%d-%b-%Y")
    _, data = m.search(None, f"SINCE {since}")
    sent_domains = set()
    for num in data[0].split():
        _, d = m.fetch(num, "(BODY.PEEK[HEADER])")
        msg = email.message_from_bytes(d[0][1])
        subj = decode(msg.get("Subject", ""))
        to = parse_addr(msg.get("To", ""))
        if "candidatur" in subj.lower() or "candidat" in subj.lower():
            sent_domains.add(domain(to))
    m.logout()
    return sent_domains


def fetch_inbox():
    m = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    m.login(EXP, PWD)
    m.select("INBOX")
    since = (datetime.now() - timedelta(days=WINDOW_DAYS)).strftime("%d-%b-%Y")
    _, data = m.search(None, f"SINCE {since}")
    msgs = []
    for num in data[0].split():
        _, d = m.fetch(num, "(BODY.PEEK[HEADER])")
        msg = email.message_from_bytes(d[0][1])
        msgs.append({
            "from": decode(msg.get("From", "")),
            "subj": decode(msg.get("Subject", "")),
            "date": decode(msg.get("Date", "")),
        })
    m.logout()
    return msgs


def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE))
        except Exception:
            pass
    return {"seen": []}


def main():
    st = load_state()
    seen = set(st["seen"])
    sent_domains = fetch_sent()
    inbox = fetch_inbox()
    found = []
    for mm in inbox:
        addr = parse_addr(mm["from"])
        dom = domain(addr)
        if addr == EXP or dom in BLOCKLIST or dom == "gmail.com":
            continue
        is_ack = dom in sent_domains
        kw = any(k in (mm["subj"] + mm["from"]).lower() for k in ACK_KEYWORDS)
        if not (is_ack or kw):
            continue
        key = f"{addr}|{mm['subj']}|{mm['date']}"
        if key in seen:
            continue
        seen.add(key)
        found.append((company_name(mm["from"]), mm["subj"], mm["date"], addr))

    if found:
        lines = []
        for comp, subj, date, addr in found:
            lines.append(
                f"📨 ACCUSÉ RÉCEPTION DE {comp}\n"
                f"   Sujet : {subj}\n"
                f"   Expéditeur : {addr}\n"
                f"   Reçu le : {date}"
            )
        print("\n\n".join(lines))

    json.dump({"seen": list(seen)}, open(STATE, "w"))


if __name__ == "__main__":
    main()
