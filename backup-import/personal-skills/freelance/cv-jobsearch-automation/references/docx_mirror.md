# Mirroring Emmanuel's own .docx for CV generation

When Emmanuel sends a `.docx` as the layout/photo reference, do not impose a new
structure. Extract and reuse HIS content order, headings, and embedded photo.

## 1. Extract text (shell + Python)
```bash
unzip -p "CV KAKESA MUDIMBA .docx" word/document.xml > doc.xml
python3 - <<'PY'
import re
xml = open('doc.xml', encoding='utf-8', errors='replace').read()
txt = re.sub(r'<[^>]+>', ' ', xml)
txt = re.sub(r'\s+', ' ', txt)
print(txt[:3000])
PY
```
Note: filenames with spaces / accents break the shell glob. In Python, list the
dir and pick the `.docx` by `f.endswith('.docx')` rather than typing the path.

## 2. Extract HIS photo from the docx
The photo is bundled in `word/media/image1.png` (name may vary).
```python
import zipfile
fn = [f for f in __import__('os').listdir('.') if f.endswith('.docx')][0]
z = zipfile.ZipFile(fn)
media = [n for n in z.namelist() if 'media' in n.lower()]
data = z.read(media[0])
open('ref_photo.png', 'wb').write(data)
```
Then crop to a portrait and resize for the PDF:
```python
from PIL import Image
im = Image.open('ref_photo.png').convert('RGB')
w, h = im.size
top = 0 if h <= w*1.33 else (h - int(w*1.33))//2
im = im.crop((0, top, w, top + int(w*1.33)))
im = im.resize((150, 200))   # ~34mm wide at 72dpi when placed in fpdf
im.save('photo_docx.png')
```

## 3. Place photo where HIS doc had it
Emmanuel's doc places the photo inside "I. INFORMATIONS PERSONNELNELLES / COORDONNEES"
(next to the contact lines), NOT in the header band. Use:
```python
pdf.image("/root/linkedin_app/photo_docx.png", x=168, y=34, w=34)
```
embedded right after the section heading and before the `mc(...)` contact block.

## 4. His known section order (do not reorder)
I. INFORMATIONS PERSONNELLES
II. PARCOURS PROFESSIONNEL
III. DOMAINES DE COMPETENCE (possedant une base solide a evoluer)
IV. ETUDES FAITES
V. FORMATIONS ACADEMIQUES
VI. LANGUES
VIII. PERSONNES DE REFERENCE   (note: no "VII")

## 5. Pitfalls observed
- He added a photo, then "supprimer la photo" -> remove in ONE patch; grep for
  `pdf.image` to confirm 0 remain. A prior dual-placement (header + section) left
  a stray header photo he noticed.
- He rejected the auto footer "CV genere automatiquement" -> never stamp the
  deliverable. Either omit the footer class or strip it before output.
