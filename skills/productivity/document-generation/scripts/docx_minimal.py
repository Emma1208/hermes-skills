# -*- coding: utf-8 -*-
"""Zero-dependency DOCX builder (zip + minimal OOXML).
Use when python-docx refuses to install (lxml build failure: needs libxml2/libxslt dev).
Word / LibreOffice open the output correctly.

Usage:
    from docx_minimal import DocxBuilder
    b = DocxBuilder(title="CURRICULUM VITAE")
    b.section("I. INFORMATIONS PERSONNELLES")
    b.bullet("KAKESA", label="Nom")          # navy bold "⮚ Nom : KAKESA"
    b.bullet("Some free text")               # navy bold "⮚ Some free text"
    b.section("VIII. PERSONNES DE REFERENCE")
    b.bullet("+243 ...", label="NOM.")
    b.signature("Fait a Kinshasa, le 01 Juin 2026", "KAKESA MUDIMBA Emmanuel-Dieudonne")
    b.save("CV.docx")
"""
import zipfile
import html

NAVY = "1F3364"


class DocxBuilder:
    def __init__(self, title="CURRICULUM VITAE"):
        self._body = []
        self._title = title

    def _esc(self, t):
        return html.escape(t, quote=True)

    def _run(self, text, bold=False, italic=False, color=None):
        rpr = []
        if bold:
            rpr.append("<w:b/>")
        if italic:
            rpr.append("<w:i/>")
        if color:
            rpr.append(f'<w:color w:val="{color}"/>')
        rpr_xml = f"<w:rPr>{''.join(rpr)}</w:rPr>" if rpr else ""
        return (f'<w:r>{rpr_xml}'
                f'<w:t xml:space="preserve">{self._esc(text)}</w:t></w:r>')

    def section(self, title):
        self._body.append(
            '<w:p><w:pPr><w:spacing w:before="120" w:after="40"/>'
            f'<w:pBdr><w:bottom w:val="single" w:sz="6" w:space="2" w:color="{NAVY}"/></w:pBdr>'
            '</w:pPr>'
            + self._run(title, bold=True, color=NAVY) + '</w:p>'
        )

    def bullet(self, value, label=None):
        parts = [self._run("⮚ ", bold=True, color=NAVY)]
        if label:
            parts.append(self._run(f"{label} : ", bold=True, color=NAVY))
        parts.append(self._run(value))
        self._body.append(
            '<w:p><w:pPr><w:spacing w:after="60"/></w:pPr>'
            + "".join(parts) + '</w:p>'
        )

    def signature(self, lieu_date, nom):
        self._body.append('<w:p><w:pPr><w:spacing w:before="240"/></w:pPr></w:p>')
        self._body.append(
            '<w:p><w:pPr><w:jc w:val="right"/></w:pPr>'
            + self._run(lieu_date, italic=True) + '</w:p>')
        self._body.append(
            '<w:p><w:pPr><w:jc w:val="right"/></w:pPr>'
            + self._run(nom, bold=True) + '</w:p>')

    def save(self, path):
        title_run = (
            '<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:after="120"/></w:pPr>'
            + self._run(self._title, bold=True, color=NAVY).replace(
                "<w:rPr>", '<w:rPr><w:sz w:val="36"/>') + '</w:p>')
        document_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:body>' + title_run + "".join(self._body)
            + '<w:sectPr>'
              '<w:pgSz w:w="11906" w:h="16838"/>'
              '<w:pgMar w:top="1020" w:right="1134" w:bottom="1020" w:left="1134" '
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
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", content_types)
            z.writestr("_rels/.rels", rels)
            z.writestr("word/document.xml", document_xml)
        return path


if __name__ == "__main__":
    b = DocxBuilder()
    b.section("I. INFORMATIONS PERSONNELLES")
    b.bullet("KAKESA", label="Nom")
    b.bullet("MUDIMBA", label="Poste nom")
    b.signature("Fait a Kinshasa, le 01 Juin 2026", "KAKESA MUDIMBA Emmanuel-Dieudonne")
    print("saved", b.save("CV_example.docx"))
