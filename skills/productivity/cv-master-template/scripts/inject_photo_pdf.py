# -*- coding: utf-8 -*-
"""Injecte le JPEG de la photo dans le PDF généré par fpdf2,
sans Pillow : on ajoute un XObject /DCTDecode et une opération 'Do'."""
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (NameObject, DictionaryObject, StreamObject,
                           ArrayObject, NumberObject)

src = "/root/cv_kakesa/CV_KAKESA_MUDIMBA.pdf"
photo = "/root/cv_kakesa/photo_kakesa.jpg"
out = "/root/cv_kakesa/CV_KAKESA_MUDIMBA.pdf"

reader = PdfReader(src)
page = reader.pages[0]

# dimensions A4 en points
PW, PH = float(page.mediabox.width), float(page.mediabox.height)
margin = 18 * 2.834645669  # 18 mm -> pt
top = 16 * 2.834645669      # 16 mm -> pt
pic_w = 34 * 2.834645669    # 34 mm -> pt
# conserver le ratio 234x312
ratio = 312 / 234
pic_h = pic_w * ratio

x = PW - margin - pic_w
y = PH - top - pic_h

# --- Créer l'XObject image ---
jpeg = open(photo, "rb").read()
img = StreamObject()
img._data = jpeg
img[NameObject("/Type")] = NameObject("/XObject")
img[NameObject("/Subtype")] = NameObject("/Image")
img[NameObject("/Filter")] = NameObject("/DCTDecode")
img[NameObject("/Width")] = NumberObject(234)
img[NameObject("/Height")] = NumberObject(312)
img[NameObject("/ColorSpace")] = NameObject("/DeviceRGB")
img[NameObject("/BitsPerComponent")] = NumberObject(8)

# --- Lier l'XObject aux ressources de la page ---
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

# --- Préparer le dessin dans le content stream ---
draw = (
    f"q\n{pic_w:.2f} 0 0 {pic_h:.2f} {x:.2f} {y:.2f} cm\n"
    "/PhotoX Do\nQ\n"
)

contents = page.get_contents()
if isinstance(contents, list):
    merged = b"".join(c.get_data() for c in contents)
else:
    merged = contents.get_data()
new_data = draw.encode("latin-1") + merged

new_stream = StreamObject()
new_stream.set_data(new_data)
page[NameObject("/Contents")] = new_stream

writer = PdfWriter()
writer.add_page(page)
# copier les autres pages
for p in reader.pages[1:]:
    writer.add_page(p)
writer.write(out)
print("PDF mis à jour avec photo:", out)
