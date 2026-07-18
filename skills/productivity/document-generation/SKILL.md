---
name: document-generation
description: Generate CVs / résumés / structured documents in PDF + DOCX + LaTeX from one data source, on environments where python-docx, reportlab, and PyMuPDF fail to install. Pure-Python fpdf2 for PDF, hand-built OOXML for DOCX, shipped .tex for LaTeX.
---

# document-generation

Generate professional documents — CV / résumé, cover letter, structured forms — in **PDF + DOCX + LaTeX** from a single structured data source. Built for environments where Office, a LaTeX toolchain, or the commonly-recommended Python libs (`python-docx`, `reportlab`, `PyMuPDF`) are unavailable or fail to install.

## When to use
- "Make me a CV / résumé", "create a resume", "generate my CV as PDF and Word"
- "Recreate this document in 3 formats" (PDF / DOCX / LaTeX)
- Any request to produce a formatted document where the user may not have Word / LibreOffice / LaTeX
- When `python-docx`, `reportlab`, or `PyMuPDF` fail to import / install

## User communication preference (observed)
This user writes in **French** and expects replies / in-document text in French.
Keep conversation replies in French for this user; keep generated document
content in French too (names, section titles, signature).

## Core approach: one data source → three renderers
Keep all content in a single Python module (e.g. `cv_data.py`) as plain dicts / lists. Write three thin generators that read it. The user edits data once and regenerates everything. Reusable generators live in `scripts/`.

## 1. PDF — use `fpdf2` (pure Python, no PIL needed for text)
`pip install fpdf2` installs where `reportlab` fails (`reportlab` pulls Pillow, which is broken on some Termux / ARM builds → `dlopen failed: library "libc.musl-aarch64.so.1"`).
- Register a Unicode TTF **before** any non-Latin-1 text:
  `pdf.add_font("DJ","", "/path/DejaVuSans.ttf")` plus the `"B"` and `"I"` variants separately.
- DejaVu paths: Termux → `/data/data/com.termux/files/usr/share/fonts/TTF/`; desktop → `fc-list | grep DejaVu` or `/usr/share/fonts/truetype/dejavu/`.
- Wrap lines with `multi_cell(0, h, text, new_x="LMARGIN", new_y="NEXT")`.
- PITFALL: a glyph present in the **regular** face of a font may be **missing in its bold face**. If you see `Font ... is missing the following glyphs`, render that glyph (e.g. a bullet/arrow) in the regular style, not bold.
- PITFALL: `fpdf2` raises `FPDFUnicodeEncodingException` for any char outside Latin-1 when using built-in core fonts (`helvetica`). Always `add_font` a TTF for accented / Unicode text.

## 2. DOCX — build a minimal valid .docx by hand (no python-docx)
`python-docx` fails to install when its `lxml` dependency can't build (needs system `libxml2` / `libxslt` dev packages: `Error: Please make sure the libxml2 and libxslt development packages are installed`). A `.docx` is just a zip of OOXML — write a valid one with stdlib `zipfile` + a small XML template. `scripts/docx_minimal.py` is a zero-dependency builder that produces a real Word file (sections, navy bold labels, bullets). Word / LibreOffice open it correctly.

## 3. LaTeX — ship a ready template
Give the user a `.tex` they can compile themselves with `pdflatex` (they may have TeX even when you don't). Use `xcolor` + custom `\sectioncv` / `\puce` / `\ligne` macros for the navy-sectioned look. Keep it self-contained (no exotic packages). See `templates/cv_template.tex`.

## Unicode glyph gotcha (shared)
The arrow `⮚` (U+2BAC) used as a bullet in many Francophone CV templates is **absent from DejaVu and most system fonts**. DOCX and LaTeX render it natively, but fpdf2 / DejaVu cannot. Substitute `►` (U+25BA, BLACK RIGHT-POINTING POINTER) in the PDF only, and tell the user. To keep the exact `⮚` everywhere, the user must install a font containing it (e.g. Segoe UI Symbol / Arial Unicode) and pass its TTF to `add_font`.

## PDF text extraction (reading their source)
When the user hands you a PDF to "recreate the template": `pip install pypdf` (pure Python, installs fast). `PyMuPDF` (`fitz`) compiles slowly from source; `pdfminer.six` / `pdfplumber` need `cryptography`, which often fails to build. `pypdf`'s `PdfReader(path).pages[i].extract_text()` is the reliable choice for text-only PDFs. (Sends image extraction to the `pillow` warning — ignore; see below for the no-Pillow way.)

## Pulling an embedded photo OUT of the source PDF (no Pillow)
If the original CV already contains the candidate's photo, reuse it. `pypdf`
needs Pillow for `page.images`, so read the **raw XObject** instead:
```python
from pypdf import PdfReader
page = PdfReader(src).pages[0]
xo = page["/Resources"]["/XObject"].get_object()
for name, ref in xo.items():
    o = ref.get_object()
    if o.get("/Subtype") == "/Image" and o.get("/Filter") == "/DCTDecode":
        open("photo.jpg", "wb").write(o.get_data())  # raw JPEG bytes
```
`/DCTDecode` = JPEG, so `get_data()` is a ready `.jpg` — no decode, no Pillow.

## Adding a photo INTO the PDF without Pillow (fpdf2 workaround)
`fpdf2.image()` requires Pillow (broken here). Instead: build the **text** PDF
with fpdf2 (no image), then inject the JPEG as a `/XObject /Image /DCTDecode`
and prepend a `q w 0 0 h x y cm /Name Do Q` op to the page content stream.
Reusable, runnable script: `scripts/inject_jpeg_pdf.py`
(`python inject_jpeg_pdf.py CV.pdf photo.jpg out.pdf`). It also reads JPEG
dimensions from the SOF marker without Pillow.

## Photo placement vs. content (layout lesson)
If the photo is top-right and you push the title DOWN under it, the left side
of the header looks empty. Better: keep the photo as a **floating / absolute**
element and start the title + ALL body content at a fixed top margin (e.g.
25 mm). In the PDF, narrow the right text column only over the photo's vertical
span (`set_right_margin(margin + pic_w + gap)` while `get_y() < photo_bottom`,
then restore) so text never overlaps the image. In DOCX use a floating
`wp:anchor` (positionH `right` / positionV `page`), not an inline `wp:inline`
(which pushes text down). In LaTeX, use
`\tikz[overlay,remember picture]{\node[anchor=north east] at ([xshift=-16mm,
yshift=-16mm]current page.north east){...};}` and set geometry `top=25mm`.

## Verification
- DOCX: re-open the zip and parse each XML part with `xml.dom.minidom.parseString` to confirm well-formedness; grep extracted `<w:t>` runs for key strings. If a photo is used, confirm `word/media/photo.jpeg` is in the zip and that `wp:inline`/`wp:anchor` is present.
- PDF: `pypdf` `extract_text()` and assert expected sections / strings are present; check `len(PdfReader(path).pages)`; for a photo, confirm the `/XObject` dict contains your image name and that the page content stream contains `<name> Do`.
- LaTeX: usually can't compile here — ship it and note the compile command (`pdflatex file.tex`).

## Files in this skill
- `templates/cv_template.tex` — sectioned CV LaTeX template (I → VIII style, navy rules)
- `scripts/docx_minimal.py` — zero-dependency DOCX builder (zip + OOXML)
- `scripts/pdf_fpdf2_cv.py` — fpdf2 Unicode PDF generator with DejaVu
- `scripts/inject_jpeg_pdf.py` — add a JPEG photo to an fpdf2 PDF without Pillow
