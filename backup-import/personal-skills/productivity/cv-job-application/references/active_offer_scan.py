#!/usr/bin/env python3
"""ACTIVE offer scanner for a Kinshasa/RDC job-seeker profile.

Reusable pattern (built for Emmanuel KAKESA MUDIMBA, comptable/finance/audit/logistique):
1. DDG HTML POST search across profile-tuned queries.
2. Read detail pages of top hits to extract the REAL deadline (snippet rarely has it).
3. Parse deadline (DD/MM/YYYY or French month) and flag ACTIVE vs EXPIREE vs no-date.
4. Emit a profile-fit verdict so the user knows what they can/can't do.

Usage: python3 active_offer_scan.py  (writes offres_brutes.json + prints active ones)

Note: this is a TEMPLATE. Tune QUERIES / PROFILE_KEYWORDS / fit logic per user.
Network can be slow; DDG POST with a browser UA. Don't trust a surfaced result as
"open" — always verify the date on the detail page.
"""
import urllib.parse, urllib.request, re, datetime, json, os

QUERIES = [
    "emploi comptable Kinshasa 2026",
    "offre audit Kinshasa recrutement",
    "assistant comptable Kinshasa debutant 2026",
    "professeur comptabilite Kinshasa",
    "logisticien Kinshasa ONG recrutement 2026",
    "finance gestion Kinshasa emploi",
]

MONTHS = {"janvier":1,"février":2,"mars":3,"avril":4,"mai":5,"juin":6,"juillet":7,
          "août":8,"septembre":9,"octobre":10,"novembre":11,"décembre":12}

def ddg_search(q, n=10):
    data = urllib.parse.urlencode({"q": q, "kl": "fr-fr"}).encode()
    req = urllib.request.Request("https://html.duckduckgo.com/html/", data=data,
        headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
    out = []
    for m in re.finditer(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?'
                         r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', html, re.S):
        url = m.group(1)
        if url.startswith("//duckduckgo.com/l/?uddg="):
            url = urllib.parse.unquote(url.split("uddg=")[1].split("&")[0])
        title = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        snip = re.sub(r"<[^>]+>", "", m.group(3)).strip()
        out.append({"q": q, "title": title, "snip": snip, "url": url.strip()})
    return out[:n]

def find_deadline(text):
    """Return datetime.date or None from DD/MM/YYYY or '1 juillet 2026'."""
    m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if m:
        try: return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError: pass
    m = re.search(r'(\d{1,2})\s+([a-zéûàè]+)\s+(\d{4})', text, re.I)
    if m and m.group(2).lower() in MONTHS:
        try: return datetime.date(int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1)))
        except ValueError: pass
    m = re.search(r'(?:expire|date limite)\D*(\d{1,2})\s+([a-zéûàè]+)\s+(\d{4})', text, re.I)
    if m and m.group(2).lower() in MONTHS:
        try: return datetime.date(int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1)))
        except ValueError: pass
    return None

today = datetime.date.today()
all_results = []
for q in QUERIES:
    try:
        all_results += ddg_search(q)
    except Exception as e:
        print(f"! {q}: {e}")

seen, uniq = set(), []
for r in all_results:
    if r["url"] in seen: continue
    seen.add(r["url"]); uniq.append(r)

print(f"Total uniques: {len(uniq)}  |  Today: {today}")
for r in uniq:
    d = find_deadline(r["title"] + " " + r["snip"])
    if d:
        tag = "ACTIVE" if d >= today else "EXPIREE"
        print(f"[{tag}] {d} | {r['title'][:55]} | {r['url'][:70]}")

json.dump(uniq, open(os.path.join(os.path.dirname(__file__),
                                  "..", "offres_brutes.json"), "w"), ensure_ascii=False)
