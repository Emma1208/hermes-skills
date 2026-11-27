---
name: pdf-document-generation
description: Generate formatted PDF documents (CVs, résumés, cover letters, invoices, reports) with ZERO external dependencies using a pure-Python stdlib PDF writer. Trigger when (a) the environment lacks chromium/wkhtmltopdf and weasyprint/fpdf2/reportlab fail to install (native build deps missing, Pillow won't compile, no venv module — common in restricted sandboxes), (b) you must avoid installing anything, or (c) you want deterministic, dependency-free PDF output. Also encodes the deliver-draft-then-validate workflow for document requests.
---

# PDF Document Generation (zero-dependency)

## When to use
- User asks for a PDF (CV, résumé, cover letter, letter, report) and no PDF toolchain is available.
- `which chromium wkhtmltopdf pdftoppm` returns nothing AND `pip install weasyprint` / `fpdf2` fails (Pillow can't build wheels, no `python3 -m venv`, timeout on native compile).
- You want a deterministic output with no network/install step.

## Do NOT do
- Do **not** conclude "PDF generation is impossible" just because weasyprint/fpdf2 failed. Fall back to the pure-stdlib writer below. That failure is an environment state, not a permanent constraint — the fix is the stdlib engine.
- Do not hand-roll PDF xref offsets incorrectly — reuse the proven engine in `scripts/generate_pdf.py`.

## Workflow for document requests (user preference)
1. Create a dedicated folder for the deliverable (e.g. `~/dossier_candidature/`).
2. Generate **both** an HTML version (native accents, easy visual check, print-to-PDF capable) and a PDF via the stdlib engine.
3. Deliver the PDF (and HTML) and explicitly mark it as a **draft to validate** — ask for confirmation/adjustments BEFORE finalizing. User's stated pattern: "create the folder, put the template, I will validate, then we adjust."
4. Iterate on feedback, then finalize.

## The pure-stdlib PDF technique (key facts)
- PDF is plain text: objects (`N 0 obj ... endobj`), a `/Pages` tree, `/Page` objects each referencing a content stream, then an `xref` table + `trailer` with `startxref`.
- Coordinates: origin is **bottom-left**. A4 = 595.28 × 841.89 pt. Track a cursor `y` from the top; convert to PDF space with `py = PAGE_H - y`.
- Fonts: the 14 standard Type1 fonts need no embedding — use `/Helvetica`, `/Helvetica-Bold`, `/Helvetica-Oblique`. Declare `/Encoding /WinAnsiEncoding`.
- **Accents / non-ASCII:** encode every text byte as **latin-1** (`s.encode('latin-1','replace')`). WinAnsiEncoding maps Latin-1 code points, so French é/è/à/ç/ô/ù etc. render correctly. Never put raw UTF-8 in content streams (it won't display). If a glyph is outside Latin-1, `replace` with its base letter as a last resort and tell the user.
- Text wrapping: AFM advance widths for Helvetica are public; approximate accented letters with their base-letter width (error <1%). See `char_w` in the engine.
- Content-stream text op: `BT /F size Tf r g b rg 1 0 0 1 x y Tm (text) Tj ET`. Escape `(`, `)`, `\`.
- Rules/bars: stroke with `rg w x1 y1 m x2 y2 l S`; fills with `g x y w h re f`.
- Multi-page: when the cursor drops below the bottom margin, start a new `/Page` object and continue.

## Pitfalls
- Missing `%PDF-1.4` header or `%%EOF` → file won't open.
- Wrong xref offsets (must be 10-digit zero-padded, followed by ` 00000 n ` or ` 65535 f `). Compute each offset as you append bytes.
- Mixing `str` and `bytes` while assembling → encode every object body to latin-1 before concatenation.
- Lines too wide → wrap with approximate widths and keep max width < usable width (page width − 2×margin).

## Reusable engine
`scripts/generate_pdf.py` — a self-contained PDF writer class (`PDF`) with `header()`, `heading()`, `para()` (supports bullets), `text()`, plus helpers, and a CV example in the `CONTENT` block at the bottom. Copy it, replace the `CONTENT` section with the target document, run `python3 generate_pdf.py`. No pip, no venv.

## References
- `references/pdf-format-notes.md` — minimal PDF structure cheat-sheet and the Latin-1 / WinAnsiEncoding mapping notes.

## Overlap note
Complements `nano-pdf` (edits existing PDFs via CLI) and `powerpoint` (pptx). This skill is specifically about *generating* PDFs from scratch with no dependencies; it does not overlap their territory.
