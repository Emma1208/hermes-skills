# ODT cover-letter recipe (odfpy) — 1 page, navy band, blue signature

Reusable boilerplate for a **LibreOffice-editable** cover letter (KAKESA target).
Derived from `/root/linkedin_app/generer_lettre_kpmg.py` (KPMG letter, validated 2026-07-17).

## Hard odfpy pitfalls (all hit this session)
1. **MasterPage MUST be named `"Standard"`** to become the default page.
   Any other name is silently ignored → your PageLayout margins never apply and the
   letter overflows to 2 pages.
   ```python
   mp = MasterPage(name="Standard", pagelayoutname="PL_x")
   doc.masterstyles.addElement(mp)   # NOT automaticstyles (→ IllegalChild)
   ```
   The `PageLayout` (margins) goes in `doc.automaticstyles.addElement(pl)`.
2. **Frame + Image come from `odf.draw`**: `from odf.draw import Frame, Image as ODImage`.
   (`odf.graphic` and `fpdf.drawing` do NOT exist here.)
   ```python
   fr = Frame(width="6cm", height="2.2cm", anchortype="paragraph")
   fr.addElement(ODImage(href=IMG, type="simple", show="embed", actuate="onLoad"))
   doc.text.addElement(fr)
   ```
   No `textalign` attr on `draw:frame` — right-align via the parent paragraph style.
3. **`Style` uses `setAttribute`, NOT `addAttribute`**:
   `s.setAttribute("parentstylename", kw["parent"])`. `addAttribute` → AttributeError.

## 1-page recipe (validated)
- PageLayout margins: left/right 1.6cm, top/bottom 1.4cm.
- `st_base`: `linespacing=0.26cm`, `marginbottom=0.25cm`, fontsize 12pt, justified.
- Navy band: a `Style` paragraph with `ParagraphProperties(backgroundcolor=NAVY)`
  + `TextProperties(color=FFFFFF, fontweight=bold, fontsize=16pt)`.
  NAVY = `"1F3350"`.
- Object line: bold navy 12pt.
- Drop any paragraph that duplicates the closing politesse line — the page break
  happens MID-PARAGRAPH, not at the end. Verify with
  `pdftotext -layout f.pdf -` : page 2 must be empty, not with stray text.
- Blue signature image bottom-right + typed name below (right-aligned style).

## Signature asset
Prefer `/root/Candidatures/Modèles/signature_seule.png` (cursive sig only, blue on
white, isolated from a clean "Signatures" app preview). Fallback:
`/root/Candidatures/Modèles/signature_kakesa.jpg` carries the printed name too —
see SKILL.md §4c refinement on isolating the cursive-only crop.

## Regenerate / verify
```bash
cd /root/linkedin_app && python3 generer_lettre_kpmg.py
cd /root/Candidatures/Modèles && \
  soffice --headless --convert-to pdf Lettre_KPMG_KAKESA.odt
pdfinfo Lettre_KPMG_KAKESA.pdf | grep Pages   # must be 1
pdftoppm -png -r 110 Lettre_KPMG_KAKESA.pdf /tmp/lettre
# then vision_analyze to confirm: nothing cut, name not truncated, sig clean
```
