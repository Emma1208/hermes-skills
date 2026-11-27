#!/usr/bin/env python3
"""Render a CV to PNG with PIL (no PDF toolchain / no network install needed).
Proven fallback when pdftoppm/pymupdf are absent or `pip install` is blocked by a slow link.
Body text ~27px (~13pt at 150dpi). Mirror the user's own section structure if they gave a .docx.
"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1240, 2600
NAVY=(20,40,80); WHITE=(255,255,255); GREY=(90,90,90); DARK=(30,30,30)
img=Image.new("RGB",(W,H),WHITE); d=ImageDraw.Draw(img)

def font(sz,bold=False):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]:
        if os.path.exists(p): return ImageFont.truetype(p,sz)
    return ImageFont.load_default()

f_name=font(42,True); f_role=font(24); f_sec=font(32,True); f_job=font(30,True)
f_body=font(27); f_foot=font(20,True)
y=0
d.rectangle([0,0,W,148],fill=NAVY)
d.text((40,34),"KAKESA MUDIMBA Emmanuel-Dieudonne",font=f_name,fill=WHITE)
d.text((40,92),"Comptable / Gestion Financiere / Audit / Enseignant",font=f_role,fill=WHITE)
y=165

def sec(t):
    global y
    d.rectangle([0,y,W,y+44],fill=NAVY)
    d.text((16,y+8),t,font=f_sec,fill=WHITE); y+=58

def wrap(t,fnt,mw):
    lines,cur=[],""
    for w in t.split():
        s=(cur+" "+w).strip()
        if d.textlength(s,font=fnt)<=mw: cur=s
        else: lines.append(cur); cur=w
    if cur: lines.append(cur)
    return lines

def block(lines,fnt,color,gap=32):
    global y
    for ln in lines:
        d.text((40,y),ln,font=fnt,fill=color); y+=gap
    y+=6

def bullet(t,fnt,color):
    global y
    for i,ln in enumerate(wrap(t,fnt,W-100)):
        d.text((52,y),("- " if i==0 else "  ")+ln,font=fnt,fill=color); y+=30
    y+=4

# --- duplicate the same text blocks you put in the PDF here ---
sec("I. INFORMATIONS PERSONNELLES")
block(["Nom : KAKESA  |  Poste nom : MUDIMBA  |  Prenom : Emmanuel-Dieudonne",
       "Sexe : Masculin  |  Ne(e) a ITURI (BUNIA) le 12/08/1998",
       "Etat civil : Celibataire  |  Nationalite : Congolaise",
       "Adresse : N° 3, Avenue Tungila, Q/Bianda, C/Mont Ngafula, Kinshasa",
       "Telephone : (+243) 818 491 601  |  E-mail : kakesamudimba@gmail.com"],
      f_body,DARK,gap=30); y+=4
sec("II. PARCOURS PROFESSIONNEL")
block(["2024 a ce jour - Professeur des Comptabilites ... au Complexe scolaire Sagesse 2 ..."],
      f_body,(20,40,80))
# ... add remaining sections to match the PDF ...
sec("VIII. PERSONNES DE REFERENCE")
block(["1. MUTAMBWE TSHAMU Patrick - DRH MSF Belgique : +243 824 983 499"],f_body,DARK,gap=30)
d.text((40,H-50),"CV genere automatiquement - KAKESA MUDIMBA Emmanuel-Dieudonne",font=f_foot,fill=GREY)
img.save("/root/linkedin_app/CV_KAKESA_Emmanuel.png")
print("PNG genere")
