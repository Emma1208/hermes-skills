---
name: docx-pdf-no-deps
description: "Use when generating DOCX/PDF documents without external dependencies (no python-docx, no Pillow). Create DOCX via raw OOXML + zipfile, inject JPEG images into PDFs via DCTDecode XObjects, and render PDFs with fpdf2 + system fonts."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [docx, pdf, ooxml, no-deps, fpdf2, python, documents]
    related_skills: [pdf, docx, ocr-and-documents]
---

# DOCX/PDF Generation Without External Dependencies

## Overview

Generate professional DOCX and PDF documents using only Python's standard library plus `fpdf2` (for PDF) and `pypdf` (for PDF manipulation). No `python-docx`, no `Pillow`, no `reportlab`. Ideal for constrained environments like Termux PRoot where some packages are unavailable.

## When to Use

- **DOCX**: When you need to generate a Word document but `python-docx` is unavailable or you want zero dependencies.
- **PDF**: When `Pillow` is unavailable but you need to embed JPEG images in a PDF.
- **Termux/Constrained environments**: When working in PRoot environments where binary packages fail to install.
- **Template-driven documents**: When you have structured data (dict) and want to render it into multiple formats (PDF + DOCX) from the same source.

## DOCX: Raw OOXML Generation

A `.docx` is a ZIP archive containing XML files. You can create a valid DOCX by writing the XML manually and zipping it.

### Minimal DOCX Structure

```
document.docx
├── [Content_Types].xml
├── _rels/.rels
└── word/
    ├── document.xml
    ├── _rels/document.xml.rels
    └── media/
        └── image1.jpeg
```

### [Content_Types].xml
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="jpeg" ContentType="image/jpeg"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
```

### _rels/.rels
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
```

### word/document.xml (minimal)
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>Hello World</w:t></w:r></w:p>
  </w:body>
</w:document>
```

### Python: Create DOCX from raw XML
```python
import zipfile, os, html

def create_docx(output_path, document_xml, image_files=None):
    """Create a valid .docx from raw XML content."""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z:
        # Content types
        z.writestr('[Content_Types].xml', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="jpeg" ContentType="image/jpeg"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>''')
        
        # Root relationships
        z.writestr('_rels/.rels', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>''')
        
        # Document XML
        z.writestr('word/document.xml', document_xml)
        
        # Images (if any)
        if image_files:
            for i, (img_path, img_name) in enumerate(image_files):
                z.write(img_path, f'word/media/{img_name}')

def esc(t):
    """Escape XML special characters."""
    return html.escape(t, quote=True)

# Example: build document.xml with styled paragraphs
NAVY = "1F3364"
def bullet(text, label=None):
    parts = []
    parts.append(f'<w:r><w:rPr><w:b/><w:color w:val="{NAVY}"/></w:rPr>'
                 f'<w:t xml:space="preserve">&#x2BAC; </w:t></w:r>')
    if label:
        parts.append(f'<w:r><w:rPr><w:b/><w:color w:val="{NAVY}"/></w:rPr>'
                     f'<w:t xml:space="preserve">{esc(label)} : </w:t></w:r>')
    parts.append(f'<w:r><w:t xml:space="preserve">{esc(text)}</w:t></w:r>')
    return ('<w:p><w:pPr><w:spacing w:after="60"/></w:pPr>' +
            "".join(parts) + '</w:p>')

document_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {bullet("KAKESA MUDIMBA Emmanuel-Dieudonné", "Nom")}
    {bullet("(+243) 818 491 601", "Téléphone")}
  </w:body>
</w:document>'''

create_docx("output.docx", document_xml)
```

### Floating Image in DOCX (anchored)
```python
def photo_para(photo_path, width_emu=1223905, height_emu=None):
    """Create an anchored (floating) image in the top-right corner."""
    if height_emu is None:
        height_emu = int(width_emu * 312 / 234)  # maintain aspect ratio
    
    return f'''<w:p><w:pPr><w:spacing w:before="0" w:after="0"/></w:pPr>
<w:r>
<w:drawing>
<wp:inline distT="0" distB="0" distL="0" distR="0" simplePos="0" 
  relativeHeight="251658240" behindDoc="0" locked="0" layoutInCell="1" allowOverlap="1">
<wp:simplePos x="0" y="0"/>
<wp:positionH relativeFrom="page"><wp:align>right</wp:align></wp:positionH>
<wp:positionV relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionV>
<wp:extent cx="{width_emu}" cy="{height_emu}"/>
<wp:docPr id="1" name="PhotoCV"/>
<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:blipFill><a:blip r:embed="rIdImg1"/></pic:blipFill>
<pic:spPr><a:xfrm><a:ext cx="{width_emu}" cy="{height_emu}"/></a:xfrm></pic:spPr>
</pic:pic>
</a:graphicData>
</a:graphic>
</wp:inline>
</w:drawing>
</w:r>
</w:p>'''
```

## PDF: JPEG Injection Without Pillow

Inject a JPEG image into an existing PDF by adding a DCTDecode XObject and drawing it with a content stream operation.

### Python: Inject JPEG into PDF
```python
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (NameObject, DictionaryObject, StreamObject,
                           ArrayObject, NumberObject)

def inject_jpeg_into_pdf(pdf_path, jpeg_path, output_path, x_mm=16, y_mm=16, width_mm=34):
    """
    Inject a JPEG image into the first page of a PDF.
    Position is relative to bottom-left, in millimeters.
    """
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    
    # Convert mm to points (1 mm = 2.834645669 pt)
    MM_TO_PT = 2.834645669
    PW = float(page.mediabox.width)
    PH = float(page.mediabox.height)
    
    margin_pt = 18 * MM_TO_PT
    top_pt = y_mm * MM_TO_PT
    pic_w_pt = width_mm * MM_TO_PT
    # Maintain aspect ratio (234x312 for the reference image)
    ratio = 312 / 234
    pic_h_pt = pic_w_pt * ratio
    
    x = PW - margin_pt - pic_w_pt
    y = PH - top_pt - pic_h_pt
    
    # Read JPEG data
    jpeg_data = open(jpeg_path, "rb").read()
    
    # Create XObject for the image
    img = StreamObject()
    img._data = jpeg_data
    img[NameObject("/Type")] = NameObject("/XObject")
    img[NameObject("/Subtype")] = NameObject("/Image")
    img[NameObject("/Filter")] = NameObject("/DCTDecode")
    img[NameObject("/Width")] = NumberObject(234)  # JPEG width in pixels
    img[NameObject("/Height")] = NumberObject(312)  # JPEG height in pixels
    img[NameObject("/ColorSpace")] = NameObject("/DeviceRGB")
    img[NameObject("/BitsPerComponent")] = NumberObject(8)
    
    # Link XObject to page resources
    res = page.get("/Resources")
    if res is None:
        res = DictionaryObject()
        page[NameObject("/Resources")] = res
    res = res.get_object()
    xo = res.get("/XObject")
    if xo is None:
        xo = DictionaryObject()
        res[NameObject("/XObject")] = xo
    xo = xo.get_object()
    xo[NameObject("/PhotoX")] = img
    
    # Prepend drawing operation to content stream
    draw = f"q\n{pic_w_pt:.2f} 0 0 {pic_h_pt:.2f} {x:.2f} {y:.2f} cm\n/PhotoX Do\nQ\n"
    
    contents = page.get_contents()
    if isinstance(contents, list):
        merged = b"".join(c.get_data() for c in contents)
    else:
        merged = contents.get_data()
    new_data = draw.encode("latin-1") + merged
    
    new_stream = StreamObject()
    new_stream.set_data(new_data)
    page[NameObject("/Contents")] = new_stream
    
    # Write output
    writer = PdfWriter()
    writer.add_page(page)
    for p in reader.pages[1:]:
        writer.add_page(p)
    writer.write(output_path)
    print(f"PDF mis à jour avec photo: {output_path}")
```

## PDF: Generate with fpdf2 + System Fonts

When Pillow is unavailable, use `fpdf2` with system-installed DejaVu fonts for Unicode support.

```python
from fpdf import FPDF

# Locate system fonts (Termux path)
FDIR = "/data/data/com.termux/files/usr/share/fonts/TTF"
NAVY = (31, 51, 100)
BLACK = (0, 0, 0)

class CVPDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("DJ", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Page {self.page_no()}/{{nb}}", align="C")

pdf = CVPDF(format="A4")
pdf.add_font("DJ", "", f"{FDIR}/DejaVuSans.ttf")
pdf.add_font("DJ", "B", f"{FDIR}/DejaVuSans-Bold.ttf")
pdf.add_font("DJ", "I", f"{FDIR}/DejaVuSans-Oblique.ttf")
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_margins(18, 16, 18)
pdf.add_page()
pdf.alias_nb_pages()

# Photo in top-right
PIC_W, PIC_H = 34, 45.3  # mm
TOP_MM = 16
pic_x = pdf.w - pdf.r_margin - PIC_W
pic_y = TOP_MM
PHOTO_BOTTOM_MM = TOP_MM + PIC_H
RIGHT_FULL = 18
RIGHT_NARROW = RIGHT_FULL + PIC_W + 4

try:
    pdf.image("photo.jpg", x=pic_x, y=pic_y, w=PIC_W, h=PIC_H)
    pdf.set_draw_color(*NAVY)
    pdf.set_line_width(0.5)
    pdf.rect(pic_x, pic_y, PIC_W, PIC_H)
except Exception as e:
    print("Photo non intégrée:", e)

def content_margin():
    """Narrow right margin when text overlaps photo zone."""
    if pdf.get_y() < PHOTO_BOTTOM_MM:
        pdf.set_right_margin(RIGHT_NARROW)
    else:
        pdf.set_right_margin(RIGHT_FULL)

def section(title):
    content_margin()
    pdf.ln(2)
    pdf.set_font("DJ", "B", 12)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
    y = pdf.get_y()
    pdf.set_draw_color(*NAVY)
    pdf.set_line_width(0.4)
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
    pdf.ln(2)

def bullet(text, label=None):
    content_margin()
    pdf.set_font("DJ", "", 11)
    pdf.set_text_color(*NAVY)
    pdf.cell(7, 5.5, "►")
    pdf.set_text_color(*BLACK)
    if label:
        pdf.set_font("DJ", "B", 11)
        pdf.set_text_color(*NAVY)
        pdf.write(5.5, f" {label} : ")
        pdf.set_font("DJ", "", 11)
        pdf.set_text_color(*BLACK)
    else:
        pdf.set_font("DJ", "", 11)
    pdf.multi_cell(0, 5.5, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.5)

# Build document
pdf.set_right_margin(RIGHT_FULL)
pdf.set_y(25)
pdf.set_font("DJ", "B", 18)
pdf.set_text_color(*NAVY)
pdf.cell(0, 10, "CURRICULUM VITAE", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)

section("I. INFORMATIONS PERSONNELLES")
bullet("KAKESA", label="Nom")
bullet("MUDIMBA", label="Poste nom")
bullet("Emmanuel-Dieudonné", label="Prénom")

pdf.output("cv.pdf")
```

## Common Pitfalls

1. **XML escaping**: Always escape `&`, `<`, `>` in text content with `html.escape()`.
2. **Namespace prefixes**: Don't use `xml.etree.ElementTree` for OOXML — it rewrites namespace prefixes and corrupts the file. Use string templates.
3. **Zip order**: Write `[Content_Types].xml` first in the ZIP (some readers are strict about this).
4. **JPEG dimensions**: The `/Width` and `/Height` in the DCTDecode XObject must match the actual JPEG pixel dimensions, not the display size.
5. **Font paths**: In Termux PRoot, fonts are at `/data/data/com.termux/files/usr/share/fonts/TTF/`. Check with `find / -name "DejaVuSans.ttf"` if the path differs.
6. **Color values**: Use RGB tuples (0-255) for fpdf2, hex strings for OOXML.
7. **Bullet characters**: Use `►` (U+25BA) for PDF bullets and `⮚` (U+2B9A) for DOCX/LaTeX — they render reliably in DejaVu fonts.

## Verification

1. **DOCX**: Open with `python -c "from docx import Document; d=Document('out.docx'); print(len(d.paragraphs))"` or render to PDF with LibreOffice: `libreoffice --headless --convert-to pdf out.docx`
2. **PDF**: Check page count: `python -c "from pypdf import PdfReader; print(len(PdfReader('out.pdf').pages))"`. Render to images: `pdftoppm -jpeg -r 100 out.pdf page` and inspect with `vision_analyze`.
3. **JPEG injection**: Verify the image appears in the correct position by rendering the first page to an image and checking visually.

## Related skills

`pdf` (PDF creation/manipulation with full dependency stack), `docx` (DOCX with python-docx), `ocr-and-documents` (text extraction from scanned PDFs), `nano-pdf` (natural-language PDF text editing).
