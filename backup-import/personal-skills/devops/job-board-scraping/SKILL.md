---
name: job-board-scraping
description: Scrape job boards and search engines for job offers matching a user's CV/profile, filter by relevance, generate a PDF CV with fpdf2, and run a daily cron that delivers matches to Telegram. Built for Emmanuel (Kinshasa/RDC finance-compta-audit profile) but reusable for any profile + locale.
triggers:
  - user wants to search for jobs / offres d'emploi matching their CV
  - build a daily job-search monitor / cron that reports new offers
  - generate a clean PDF CV from a pasted text resume
  - scrape LinkedIn/Indeed/OptionCarriere/Emploi.cd when the API is blocked
---

# Job-board scraping & profile-matched job monitoring

## 1. The scraping engine — DuckDuckGo HTML (KEY PITFALL)
Most job-search scraping here uses DuckDuckGo's HTML endpoint as a search proxy because
LinkedIn/Indeed block direct bots.

**CRITICAL:** `https://html.duckduckgo.com/html/` returns an EMPTY results page on a plain
GET. You MUST send a **POST** with form body `q=<query>`. A GET silently yields 0 results
and looks like a "regex broken" bug — it is not.

Working call:
```python
import urllib.request, urllib.parse
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
data = urllib.parse.urlencode({"q": query}).encode()
req = urllib.request.Request("https://html.duckduckgo.com/html/", data=data, headers=UA)
page = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
```
Parse with regex (classes: `result__a` = title+link, `result__snippet` = snippet; links are
wrapped as `uddg=<urlencoded>` — extract with `re.search(r'uddg=([^&]+)', href)` then unquote).
See `references/ddg_scraper.py` for the proven, copy-paste script.

## 2. LinkedIn is API-blocked for this use case
The official LinkedIn API (OpenID Connect "Sign In with LinkedIn") returns ONLY
name / email / photo. It CANNOT read the full profile, edit it, or search jobs.
LinkedIn also blocks direct scraping (captcha + login wall). Real options:
- Browser automation (only if agent + browser share a machine — NOT on Android Termux,
  where browser tools fail with "Unsupported platform: android-arm64").
- Guided manual: user does it, agent dictates clicks.
- Scrape OTHER boards instead (below) — this is the reliable path.

## 3. RDC / French job boards that work (no login wall)
Prefer these as direct targets in addition to DDG search:
- https://www.optioncarriere.cd/emploi-comptabilite-et-gestion-financiere
- https://www.emploi.cd/
- https://www.emploiscongo.com/emplois/finance-et-comptabilite
- https://www.moncongojobs.com/
- https://cd.linkedin.com/jobs/ (public listings, may partial-render)
- https://www.mediacongo.net/emplois.html

## 4. Profile-match filter
Define `PROFILE_KEYWORDS` (lowercased substrings of the CV domain) and score each result by
count of keyword hits in title+snippet; sort descending; dedupe by URL. Keep it simple —
substring matching, no ML. Example keywords for a finance/compta profile:
`["comptab","financ","audit","controle de gestion","fiscal","gestion","professeur","enseign","econom"]`

## 5. PDF CV generation (fpdf2)
- `pip install fpdf2` (pure-python, installs cleanly).
- fpdf core fonts are latin-1 ONLY. Sanitize text: replace curly quotes/dashes
  (`\u2019 \u2013 \u2014 \u201c \u201d \u2022`) and `.encode("latin-1","replace").decode("latin-1")`.
- Use Helvetica (Arial maps to it with a deprecation warning). Avoid `ln=` param — use
  `new_x=XPos.LMARGIN, new_y=YPos.NEXT` (import `from fpdf.enums import XPos, YPos`).
- **multi_cell horizontal-space error:** after any `cell()` call, reset X with
  `pdf.set_x(pdf.l_margin)` before `multi_cell()`, or the cursor stays at the right margin
  and raises "Not enough horizontal space to render a single character". Safest: wrap every
  multi_cell in a helper that calls set_x first. See `references/cv_template.py`.

## 6. Visual preview (PNG) + the 13pt legibility rule
The user reviews the CV by EYE (sends "Regarde" screenshots), so a PNG preview is often
needed alongside the PDF. **Legibility rule (observed correction: "Les écrits sont petits
utiliser taille 13"):** body text MUST render at ~13pt minimum. In fpdf2 that is font size 13;
in a PIL A4-as-image preview use ~30px job titles and ~27px body text.

PNG preview paths, in order of preference:
- **Best:** `pdftoppm -r 110 CV.pdf cv_preview` or `pymupdf` (`fitz`) `page.get_pixmap(dpi=110)`.
  BUT these deps may be absent or network-blocked (pymupdf `pip install` timed out on a slow
  link in-session). Don't burn time retrying a slow install.
- **Reliable fallback (PROVEN in-session):** render the CV straight to PNG with **PIL**
  (Pillow is usually preinstalled). Draw a navy header band, section bars, and text via
  `ImageDraw`; wrap long lines manually with `d.textlength()`. Use DejaVuSans/LiberationSans
  TTFs (check `/usr/share/fonts/truetype/`). This avoids any PDF toolchain entirely and is the
  safe default when you just need the user to *see* the layout. See `references/cv_preview_pil.py`.

When the user supplies their OWN `.docx` resume, **mirror its section structure** (e.g.
"I. INFORMATIONS PERSONNELLES / II. PARCOURS PROFESSIONNEL / III. DOMAINES DE COMPETENCE …")
rather than inventing your own. Read the docx by unzipping `word/document.xml` and stripping
tags (no python-docx needed): `zipfile.ZipFile(fn).read('word/document.xml')` then
`re.sub(r'<[^>]+>',' ', xml)`. Filenames may contain spaces — glob `*.docx` instead of
passing a literal path with spaces.

## 7b. Sharing generated CVs as a LINK (user preference)
The user prefers receiving generated docs as a **web link**, not a Telegram attachment
(observed correction: "Envoyé moi ça en lien"). Upload via `tmpfiles.org` and paste the URL.
See `references/share_link.md` for the working call + hosts that are shut. Tell him links
expire (~24h).

### 7b-i. DELIVERY PITFALL — link alone may fail for him
Observed: after sending a tmpfiles.org link he replied "Je n'arrive pas à le télécharger
fait le pour moi" — he could not download the link on his phone. **Fix:** deliver the SAME
file through MULTIPLE channels: (1) re-send as a Telegram file attachment (MEDIA: path),
(2) re-paste the link, (3) offer PNG preview. Don't assume the link worked — confirm he
got it. When in doubt, attach the file directly; links are a nice-to-have, not the only path.

## 7c. Adding a PROFILE PHOTO to the CV (observed: user sent a portrait photo)
When the user supplies a photo (Telegram image attachment), embed it. Square-crop + resize
with PIL, then `pdf.image()` top-right. Full template in `references/cv_with_photo.py`.
Key points: crop to square `min(w,h)` centered; resize ~360px; in fpdf2 use
`pdf.image("photo_cv.jpg", x=158, y=8, w=40)` (A4=210mm wide, so x158+w40=198 leaves a
12mm margin); draw it AFTER the header text block. Also bake the photo into the PIL PNG
preview if he wants to eyeball layout. Don't generate a fake AI face — use his real photo.

## 7d. VERIFY THE OFFER IS STILL ACTIVE (pitfall)
Search engines surface STALE listings. Before tailoring a CV / telling the user to apply,
confirm the offer is open: fetch its page and check for "n'est plus d'actualité" / a past
deadline / "Postulez avant le <old-date>". Example hit this session: HY Group / AMT CONGO
comptable offer via ReKrute was **closed since 30/01/2022** but still ranked high in DDG.
Always pick an ACTIVE offer for the "apply" step, or say explicitly "cette offre est expirée"
and move to a live one.

## 7. Daily cron delivery to Telegram
- The cron `script` MUST live in `~/.hermes/scripts/` (absolute paths are rejected). Copy the
  scraper there; set `workdir` to where it reads/writes (e.g. `/root/linkedin_app`).
- `deliver: telegram:<chat_id>` pushes the script's stdout straight to the user's chat.
- Use `no_agent: true` style ONLY if the script itself prints the final message; otherwise
  give the cron a `prompt` that runs the script then summarizes (keeps the agent's voice).
- Schedule `0 9 * * *` for a 9am daily digest.

## 7. Secrets
LinkedIn client_id/secret (if used) go in a chmod-700 local config, never in memory plaintext.
