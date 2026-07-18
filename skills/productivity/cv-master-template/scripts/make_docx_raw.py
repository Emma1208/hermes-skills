# -*- coding: utf-8 -*-
"""Génère un .docx VALIDE sans dépendance externe (zip + XML minimal).
Template CV (sections I -> VIII, puces ⮚) + photo flottante coin haut-droite.
Marge haute = 25 mm ; titre + contenu démarrent à 25 mm (photo flottante,
ne pousse pas le texte)."""
import zipfile, os, html
import cv_data as D

OUT = "/root/cv_kakesa/CV_KAKESA_MUDIMBA.docx"
PHOTO = "/root/cv_kakesa/photo_kakesa.jpg"
NAVY = "1F3364"

# 3.4 cm de large ~ 1 223 905 EMU ; hauteur proportionnelle 312/234
PIC_W_EMU = 1223905
PIC_H_EMU = int(PIC_W_EMU * 312 / 234)
TOP_MARGIN_EMU = 1417   # 25 mm (1 mm = 56.6929 EMU)

def esc(t):
    return html.escape(t, quote=True)

def runs_bullet(label, value):
    parts = []
    parts.append(f'<w:r><w:rPr><w:b/><w:color w:val="{NAVY}"/></w:rPr>'
                 f'<w:t xml:space="preserve">&#x2BAC; </w:t></w:r>')
    if label:
        parts.append(f'<w:r><w:rPr><w:b/><w:color w:val="{NAVY}"/></w:rPr>'
                     f'<w:t xml:space="preserve">{esc(label)} : </w:t></w:r>')
    parts.append(f'<w:r><w:t xml:space="preserve">{esc(value)}</w:t></w:r>')
    return ('<w:p><w:pPr><w:spacing w:after="60"/></w:pPr>' +
            "".join(parts) + '</w:p>')

def section_para(title):
    return (
        '<w:p><w:pPr><w:spacing w:before="120" w:after="40"/>'
        f'<w:pBdr><w:bottom w:val="single" w:sz="6" w:space="2" w:color="{NAVY}"/></w:pBdr>'
        '</w:pPr>'
        f'<w:r><w:rPr><w:b/><w:color w:val="{NAVY}"/></w:rPr>'
        f'<w:t xml:space="preserve">{esc(title)}</w:t></w:r></w:p>'
    )

def photo_para():
    """Image flottante (anchor) coin haut-droite, habillage carré."""
    return (
        '<w:p><w:pPr><w:spacing w:before="0" w:after="0"/></w:pPr>'
        '<w:r>'
        '<w:drawing>'
        '<wp:anchor distT="0" distB="0" distL="0" distR="0" simplePos="0" '
        'relativeHeight="251658240" behindDoc="0" locked="0" layoutInCell="1" allowOverlap="1">'
        '<wp:simplePos x="0" y="0"/>'
        '<wp:positionH relativeFrom="page"><wp:align>right</wp:align></wp:positionH>'
        '<wp:positionV relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionV>'
        f'<wp:extent cx="{PIC_W_EMU}" cy="{PIC_H_EMU}"/>'
        '<wp:effectExtent l="0" t="0" r="0" b="0"/>'
        '<wp:wrapSquare wrapText="bothSides"/>'
        '<wp:docPr id="1" name="PhotoCV"/>'
        '<wp:cNvGraphicFramePr><a:graphicFrameLocks '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>'
        '</wp:cNvGraphicFramePr>'
        '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:nvPicPr><pic:cNvPr id="0" name="photo.jpeg"/><pic:cNvPicPr/></pic:nvPicPr>'
        '<pic:blipFill><a:blip r:embed="rId2"/>'
        '<a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        '<pic:spPr>'
        '<a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        f'<a:ln w="12700"><a:solidFill><a:srgbClr val="{NAVY}"/></a:solidFill></a:ln>'
        '</pic:spPr>'
        '</pic:pic>'
        '</a:graphicData>'
        '</a:graphic>'
        '</wp:anchor>'
        '</w:drawing>'
        '</w:r></w:p>'
    ) % (PIC_W_EMU, PIC_H_EMU)

def build_body():
    b = []
    b.append(photo_para())
    b.append(
        '<w:p><w:pPr><w:spacing w:before="0" w:after="120"/>'
        f'<w:jc w:val="center"/></w:pPr>'
        f'<w:r><w:rPr><w:b/><w:sz w:val="36"/><w:color w:val="{NAVY}"/></w:rPr>'
        f'<w:t xml:space="preserve">{esc(D.CV["titre"])}</w:t></w:r></w:p>'
    )
    b.append(section_para("I. INFORMATIONS PERSONNELLES"))
    for label, val in D.CV["infos_perso"]:
        b.append(runs_bullet(label, val))
    b.append(section_para("II. PARCOURS PROFESSIONNEL"))
    for item in D.CV["parcours"]:
        b.append(runs_bullet(None, item))
    b.append(section_para("III. DOMAINES DE COMPETENCE"))
    b.append(runs_bullet(None, " ; ".join(D.CV["competences"]) + "."))
    b.append(section_para("IV. ETUDES FAITES"))
    for item in D.CV["etudes"]:
        b.append(runs_bullet(None, item))
    b.append(section_para("V. FORMATIONS ACADÉMIQUE"))
    for item in D.CV["formations"]:
        b.append(runs_bullet(None, item))
    b.append(section_para("VI. LANGUES"))
    for langue, niveau in D.CV["langues"]:
        b.append(runs_bullet(langue, niveau))
    b.append(section_para("VIII. PERSONNES DE REFERENCE"))
    for nom, detail in D.CV["references"]:
        b.append(runs_bullet(nom + ".", detail))
    b.append('<w:p><w:pPr><w:spacing w:before="240"/></w:pPr></w:p>')
    b.append('<w:p><w:pPr><w:jc w:val="right"/></w:pPr>'
             f'<w:r><w:rPr><w:i/></w:rPr>'
             f'<w:t xml:space="preserve">{esc(D.CV["signature"]["lieu_date"])}</w:t></w:r></w:p>')
    b.append('<w:p><w:pPr><w:jc w:val="right"/></w:pPr>'
             f'<w:r><w:rPr><w:b/></w:rPr>'
             f'<w:t xml:space="preserve">{esc(D.CV["signature"]["nom"])}</w:t></w:r></w:p>')
    return "".join(b)

document_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
    '<w:body>'
    + build_body()
    + '<w:sectPr>'
      '<w:pgSz w:w="11906" w:h="16838"/>'
      f'<w:pgMar w:top="{TOP_MARGIN_EMU}" w:right="1134" w:bottom="1020" w:left="1134" '
               'w:header="708" w:footer="708" w:gutter="0"/>'
    '</w:sectPr>'
    '</w:body></w:document>'
)

content_types = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Default Extension="jpeg" ContentType="image/jpeg"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '</Types>'
)

rels = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/photo.jpeg"/>'
    '</Relationships>'
)

os.makedirs("/root/cv_kakesa", exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", content_types)
    z.writestr("_rels/.rels", rels)
    z.writestr("word/document.xml", document_xml)
    with open(PHOTO, "rb") as fh:
        z.writestr("word/media/photo.jpeg", fh.read())

print("DOCX généré:", OUT, os.path.getsize(OUT), "bytes")
