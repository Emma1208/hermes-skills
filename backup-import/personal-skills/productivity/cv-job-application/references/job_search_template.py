#!/usr/bin/env python3
"""WORKING job-search template: DuckDuckGo HTML POST (GET returns empty page),
parse results, score by profile keywords, print + log. Copy into ~/.hermes/scripts/
for a cron."""
import urllib.request, urllib.parse, re, html, datetime, os

PROFILE_KEYWORDS = ["comptab", "financ", "audit", "contrôle de gestion", "fiscal",
                    "gestion", "professeur", "enseign", "econom"]
QUERIES = [
    "emploi comptabilite gestion financiere Kinshasa RDC",
    "emploi audit controle de gestion fiscalite Kinshasa",
    "assistant comptable Kinshasa RDC recrutement",
]
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

def ddg_search(query, limit=6):
    url = "https://html.duckduckgo.com/html/"
    data = urllib.parse.urlencode({"q": query}).encode()
    try:
        req = urllib.request.Request(url, data=data, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            page = r.read().decode("utf-8", "replace")
    except Exception as e:
        return [{"title": "ERREUR: " + str(e), "url": "", "snippet": ""}]
    items = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
                       r'.*?class="result__snippet"[^>]*>(.*?)</a>', page, re.S)
    out = []
    for href, title, snippet in items[:limit]:
        m = re.search(r'uddg=([^&]+)', href)
        if m: href = urllib.parse.unquote(m.group(1))
        out.append({"title": html.unescape(re.sub(r'<[^>]+>', '', title)),
                    "url": href, "snippet": html.unescape(re.sub(r'<[^>]+>', '', snippet))})
    return out

def score(r):
    t = (r["title"] + " " + r["snippet"]).lower()
    return sum(1 for k in PROFILE_KEYWORDS if k in t)

def main():
    out = ["=== RECHERCHE OFFRES (%s) ===" % datetime.date.today()]
    seen = set(); total = 0
    for q in QUERIES:
        out.append("--- " + q)
        res = ddg_search(q)
        if res and "ERREUR" in res[0].get("title", ""):
            out.append("  (echec: %s)" % res[0]["title"]); continue
        res.sort(key=score, reverse=True)
        for r in res:
            if not r["url"] or r["url"] in seen: continue
            seen.add(r["url"]); total += 1
            out.append("  * %s\n    %s" % (r["title"], r["url"]))
    out.append("Total: %d" % total)
    text = "\n".join(out); print(text)
    os.makedirs("/root/linkedin_app/logs", exist_ok=True)
    open("/root/linkedin_app/logs/jobs_%s.txt" % datetime.date.today(), "w").write(text)

if __name__ == "__main__":
    main()
