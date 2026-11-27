#!/usr/bin/env python3
"""GENERE (uniquement) les brouillons de relance des candidatures sans reponse (+7j).

Mode DRAFT-FIRST: n'envoie RIEN. Ecrit dans pending_relances.json (status
'en attente') et affiche les NOUVEAUX brouillons pour livraison Telegram.
L'envoi est fait a la main via envoyer_relances.py (l'utilisateur valide).

Logique:
  1. Lit [Gmail]/Messages envoyés (SINCE 10j) -> candidatures (To, Subj, Date).
  2. Pour chaque candidature de >=7j, verifie si le domaine a deja repondu via
     une recherche IMAP CIBLEE 'FROM @domaine' (PITFALL perf: jamais de scan
     complet de l'INBOX). Cache persistant .inbox_domain_history.json.
  3. Ignore si deja repondu OU deja dans pending (to, subj).
  4. Genere un brouillon francais poli, l'ajoute a pending_relances.json.
  5. Affiche UNIQUEMENT les nouveaux brouillons (stdout vide = rien a livrer).

FILL: EXP, PWD (app-password Gmail, meme que §9 SMTP).
"""
import imaplib, email, json, os, re
from email.header import decode_header
from datetime import datetime, timedelta

EXP = "FILL@gmail.com"
PWD = "FILL_APP_PASSWORD"
PENDING = "/root/linkedin_app/pending_relances.json"
HIST = "/root/linkedin_app/.inbox_domain_history.json"

BLOCKLIST = ("linkedin.com", "instagram.com", "facebook.com", "noreply@",
             "mail.", "info.n8n", "trade-ideas", "betibet", "promo@", "n8n.io")


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
    return m.group(1).lower().strip() if m else (s or "").strip().lower()


def domain(addr):
    return addr.split("@")[-1] if "@" in addr else ""


def parse_date(s):
    try:
        d = email.utils.parsedate_to_datetime(s)
        if d is None:
            return None
        if d.tzinfo is not None:
            d = d.astimezone().replace(tzinfo=None)  # PITFALL: offset-naive vs aware
        return d
    except Exception:
        return None


def fetch_sent_old():
    m = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    m.login(EXP, PWD)
    candidates = ['"[Gmail]/Messages envoy&AOk-s"',
                  '"[Gmail]/Sent Mail"', '"[Gmail]/Sent"', '"Sent"']
    box = None
    for c in candidates:
        try:
            m.select(c); box = c; break
        except Exception:
            continue
    if box is None:
        raise SystemExit("Dossier Messages envoyes introuvable")
    since = (datetime.now() - timedelta(days=10)).strftime("%d-%b-%Y")
    _, data = m.search(None, f"SINCE {since}")
    out = []
    for num in data[0].split():
        _, d = m.fetch(num, "(BODY.PEEK[HEADER])")
        msg = email.message_from_bytes(d[0][1])
        subj = decode(msg.get("Subject", ""))
        to = parse_addr(msg.get("To", ""))
        if "candidatur" in subj.lower() or "candidat" in subj.lower():
            out.append({"to": to, "subj": subj, "date": parse_date(msg.get("Date", ""))})
    m.logout()
    return out


def load_domain_history():
    if os.path.exists(HIST):
        try:
            return set(json.load(open(HIST)))
        except Exception:
            pass
    return set()


def save_domain_history(s):
    json.dump(list(s), open(HIST, "w"))


def domain_repondu(target_domains):
    """Renvoie le set des domaines cibles ayant repondu (recherche CIBLEE)."""
    hist = load_domain_history()
    m = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    m.login(EXP, PWD)
    m.select("INBOX")
    for dom in target_domains:
        if dom in hist:
            continue
        try:
            _, data = m.search(None, "FROM", f"@{dom}")
        except Exception:
            continue
        if data and data[0].strip():
            hist.add(dom)
    m.logout()
    save_domain_history(hist)
    return hist


def poste_from_subj(subj):
    s = re.sub(r"(?i)^candidature\s*[-:]\s*", "", subj)
    s = re.sub(r"(?i)^candidat\s*[-:]\s*", "", s)
    return s.strip() or subj


def make_draft(c):
    poste = poste_from_subj(c["subj"])
    date_env = c["date"].strftime("%d/%m/%Y") if c["date"] else "il y a quelques jours"
    sujet = f"Relance - {poste}"
    corps = (
        "Madame, Monsieur,\n\n"
        f"Je me permets de revenir vers vous concernant ma candidature "
        f"transmise le {date_env} pour le poste de {poste}.\n\n"
        "Toujours très intéressé par cette opportunité et motivé à contribuer "
        "à vos équipes, je souhaite m'assurer que mon dossier vous est bien "
        "parvenu et rester à votre disposition pour tout entretien ou "
        "complément d'information.\n\n"
        "Vous remerciant de votre attention, je vous prie d'agréer, "
        "Madame, Monsieur, mes salutations distinguées.\n\n"
        "KAKESA MUDIMBA Dieudonné\n"
        "Tél : (+243) 818 491 601\n"
        "Email : kakesamudimba@gmail.com"
    )
    return sujet, corps


def load_pending():
    if os.path.exists(PENDING):
        try:
            return json.load(open(PENDING))
        except Exception:
            pass
    return {"items": []}


def main():
    pending = load_pending()
    done = {(it["to"], it["subj"]) for it in pending["items"]}
    sent = fetch_sent_old()
    target_doms = {domain(c["to"]) for c in sent if domain(c["to"])}
    replied = domain_repondu(target_doms)
    new = []
    for c in sent:
        if c["date"] is None:
            continue
        age = (datetime.now() - c["date"]).days
        if age < 7:
            continue
        if domain(c["to"]) in replied:
            continue
        if (c["to"], c["subj"]) in done:
            continue
        sujet, corps = make_draft(c)
        rid = len(pending["items"]) + 1
        pending["items"].append({
            "id": rid, "to": c["to"], "subj": c["subj"],
            "relance_sujet": sujet, "relance_corps": corps,
            "status": "en attente", "date_gen": datetime.now().isoformat(),
        })
        new.append(rid)
    json.dump(pending, open(PENDING, "w"), indent=2, ensure_ascii=False)

    if new:
        lines = ["📋 BROUILLONS DE RELANCE À VALIDER (réponds « ENVOIE <id> » ou « envoie tout ») :\n"]
        for it in pending["items"]:
            if it["id"] in new:
                lines.append(
                    f"── Relance #{it['id']} → {it['to']} ──\n"
                    f"Sujet : {it['relance_sujet']}\n\n{it['relance_corps']}\n"
                )
        print("\n".join(lines))


if __name__ == "__main__":
    main()
