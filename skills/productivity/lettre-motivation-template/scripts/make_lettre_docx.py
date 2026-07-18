# -*- coding: utf-8 -*-
"""Génère une LETTRE DE MOTIVATION en .docx VALIDE (zip + XML minimal).
Mise en page :
  - LIGNE 1 : nom expéditeur (gauche) | date (droite), sur la même ligne.
  - Sous le nom : adresse/tél/email (gauche).
  - Destinataire EN-DESSOUS, aligné à droite.
  - Objet, salutation, corps, formule de politesse.
  - SIGNATURE en bas : dernier nom à droite.
"""
import zipfile, os, html
import lettre_data as L

OUT = "/root/lettre_motivation/LETTRE_MOTIVATION.docx"
NAVY = "1F3364"

def esc(t):
    return html.escape(t, quote=True)

def para(text, bold=False, color=None, size=22, after=80, align=None):
    rpr = ""
    if bold:
        rpr += "<w:b/>"
    if color:
        rpr += f'<w:color w:val="{color}"/>'
    rpr += f'<w:sz w:val="{size}"/>'
    jc = f'<w:jc w:val="{align}"/>' if align else ""
    return (
        f'<w:p><w:pPr>{jc}<w:spacing w:after="{after}"/></w:pPr>'
        f'<w:r><w:rPr>{rpr}</w:rPr>'
        f'<w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>'
    )

e = L.LETTRE["expediteur"]
d = L.LETTRE["destinataire"]
bold_navy = f'<w:b/><w:color w:val="{NAVY}"/>'

# Cellule gauche : nom (plein, gauche) + adresse/tel/email
cell_g = (
    '<w:p><w:pPr><w:spacing w:after="20"/></w:pPr>'
    f'<w:r><w:rPr><w:sz w:val="22"/>{bold_navy}</w:rPr>'
    f'<w:t xml:space="preserve">{esc(e["nom"])}</w:t></w:r></w:p>'
)
for t in [e["adresse"], e["tel"], e["email"]]:
    cell_g += ('<w:p><w:pPr><w:spacing w:after="20"/></w:pPr>'
               f'<w:r><w:rPr><w:sz w:val="20"/></w:rPr>'
               f'<w:t xml:space="preserve">{esc(t)}</w:t></w:r></w:p>')

# Cellule date (droite, meme ligne que le nom)
cell_date = (
    '<w:p><w:pPr><w:jc w:val="right"/><w:spacing w:after="20"/></w:pPr>'
    f'<w:r><w:rPr><w:sz w:val="20"/></w:rPr>'
    f'<w:t xml:space="preserve">{esc(L.LETTRE["date_lieu"])}</w:t></w:r></w:p>'
)

# Cellule destinataire (droite, mais alignee a GAUCHE)
cell_dest = ""
for t in [d["ligne1"], d["ligne2"], d["ligne3"]]:
    cell_dest += ('<w:p><w:pPr><w:spacing w:after="20"/></w:pPr>'
                  f'<w:r><w:rPr><w:sz w:val="20"/></w:rPr>'
                  f'<w:t xml:space="preserve">{esc(t)}</w:t></w:r></w:p>')

# Signature : tout le nom a droite
sig = L.LETTRE["signature_nom"]
sig_xml = (
    '<w:p><w:pPr><w:jc w:val="right"/><w:spacing w:after="0"/></w:pPr>'
    f'<w:r><w:rPr><w:sz w:val="22"/>{bold_navy}</w:rPr>'
    f'<w:t xml:space="preserve">{esc(sig)}</w:t></w:r></w:p>'
)

def build_body():
    b = []
    b.append(
        '<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/>'
        '<w:tblBorders>'
        '<w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '</w:tblBorders></w:tblPr>'
        '<w:tblGrid><w:gridCol w:w="4252"/><w:gridCol w:w="4252"/></w:tblGrid>'
        '<w:tr>'
        f'<w:tc><w:tcPr><w:tcW w:w="4252" w:type="dxa"/><w:vAlign w:val="top"/></w:tcPr>{cell_g}</w:tc>'
        f'<w:tc><w:tcPr><w:tcW w:w="4252" w:type="dxa"/><w:vAlign w:val="top"/></w:tcPr>{cell_date}</w:tc>'
        '</w:tr>'
        '<w:tr>'
        '<w:tc><w:tcPr><w:tcW w:w="4252" w:type="dxa"/><w:vAlign w:val="top"/></w:tcPr></w:tc>'
        f'<w:tc><w:tcPr><w:tcW w:w="4252" w:type="dxa"/><w:vAlign w:val="top"/></w:tcPr>{cell_dest}</w:tc>'
        '</w:tr></w:tbl>'
    )
    b.append(para("Concerne : " + L.LETTRE["objet"], bold=True, color=NAVY, after=160))
    b.append(para(L.LETTRE["salutation"], after=120))
    for p in L.LETTRE["corps"]:
        b.append(para(p, after=160))
    b.append('<w:p><w:pPr><w:spacing w:before="120" w:after="40"/></w:pPr></w:p>')
    for line in L.LETTRE["formule"]:
        b.append(para(line, after=0))
    b.append('<w:p><w:pPr><w:spacing w:before="240" w:after="0"/></w:pPr></w:p>')
    if L.LETTRE["signature_image"]:
        pass
    b.append(sig_xml)
    return "".join(b)

document_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:body>'
    + build_body()
    + '<w:sectPr>'
      '<w:pgSz w:w="11906" w:h="16838"/>'
      '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" '
               'w:header="708" w:footer="708" w:gutter="0"/>'
    '</w:sectPr>'
    '</w:body></w:document>'
)

content_types = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '</Types>'
)

rels = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
    '</Relationships>'
)

os.makedirs("/root/lettre_motivation", exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", content_types)
    z.writestr("_rels/.rels", rels)
    z.writestr("word/document.xml", document_xml)

print("DOCX généré:", OUT, os.path.getsize(OUT), "bytes")
