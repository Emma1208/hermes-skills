#!/usr/bin/env python3
"""
Add a profile photo to a CV PDF (fpdf2) + square-crop a portrait phone photo with PIL.
Reusable template -- copy and modify for any CV generator.

Usage:
  1. Place the user's photo (any portrait, e.g. phone selfie) as photo.jpg in the work dir.
  2. Crop to a square and resize (PIL, no network deps):
"""
from PIL import Image

im = Image.open("photo.jpg").convert("RGB")
w, h = im.size
s = min(w, h)
left = (w - s) // 2
top = (h - s) // 2
im = im.crop((left, top, left + s, top + s)).resize((360, 360))
im.save("photo_cv.jpg")

# 3. In the fpdf2 PDF builder, after drawing the header band and BEFORE writing
#    the first section, embed the photo top-right:
#
# from fpdf import FPDF
# from fpdf.enums import XPos, YPos
# pdf = FPDF()
# pdf.add_page()
# # ... draw navy header rect + name text ...
# try:
#     pdf.image("photo_cv.jpg", x=158, y=8, w=40)   # x/y/w in mm, A4 = 210x297
# except Exception as e:
#     print("Photo non inseree:", e)
# pdf.ln(10)
#
# NOTES:
# - A4 page width is 210mm. x=158 + w=40 = 198mm, leaving a 12mm right margin. Good.
# - pdf.image() accepts .jpg/.png. If the source is a huge phone image, crop+resize
#   first (above) or the PDF bloats and may render slowly.
# - Keep the photo OUT of the multi_cell text flow: draw it with absolute x/y AFTER
#   the header text but the header text used new_x=LMARGIN so it sits on the left --
#   they don't overlap.
# - The user reviews the CV by eye, so ALSO generate a PNG preview (see cv_preview_pil.py)
#   with the same photo embedded (Image.paste onto the PIL canvas) if he wants to "see" it.
