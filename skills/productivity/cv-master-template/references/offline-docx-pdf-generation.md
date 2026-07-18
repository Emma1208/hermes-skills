# Offline OOXML / PDF generation (Termux PRoot, Python 3.14, ARM musl)

Technique réutilisable pour produire des .docx et .pdf VALIDES sans les
bibliothèques standard (reportlab et python-docx échouent ici).

## Pourquoi on ne peut pas utiliser les libs standard
- **Pillow est CASSÉ** dans cet env (libc.musl manquant au runtime de _imaging).
  → reportlab importe PIL au chargement → crash.
  → python-docx importe lxml qui doit compiler libxml2/libxslt → échec build.
- Donc : pas de `pdf.image()` (fpdf2), pas de `Document()` (python-docx).

## DOCX : générer à la main (zip + XML OOXML)
Un .docx valide minimal = un zip contenant :
- `[Content_Types].xml` (Default rels/xml + Override document.xml)
- `_rels/.rels` (Relationship rId1 -> word/document.xml)
- `word/document.xml` (le corps)
- optionnel `word/media/photo.jpeg` + Relationship rId2 (image) si photo.
Voir scripts `make_docx_raw.py` (CV) et `make_lettre_docx.py` (lettre) -> code
canonique copiable. Points critiques :
- **JAMAIS de backslash dans une f-string Python 3.11+** (erreur de syntaxe).
  Construire les balises XML via variables/boucles, ex. `bold_navy = f'...'`.
- Photo = IMAGE FLOTTANTE (wp:anchor, positionH relativeFrom=page align=right,
  wrapSquare) pour qu'elle ne pousse pas le texte. Vérifier `wp:anchor` présent.
- Tableau 2 colonnes sans bordures : `<w:tblBorders>` tous `w:val="none"`.
- Valider en dézippant et en parsant tout XML avec `xml.dom.minidom.parseString`.

## PDF : fpdf2 + injection de photo sans Pillow
- fpdf2 fonctionne (installé). Police DejaVu système :
  `/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans.ttf` (+Bold/Oblique).
- Pour la PHOTO : ne PAS appeler `pdf.image()` (besoin de Pillow). À la place :
  1. générer le PDF sans image (make_pdf.py),
  2. injecter le JPEG via pypdf comme XObject :
     - lire le JPEG brut, créer `StreamObject` avec `/Filter /DCTDecode`,
       `/Width 234 /Height 312 /ColorSpace /DeviceRGB /BitsPerComponent 8`,
     - l'attacher à `/Resources /XObject /PhotoX`,
     - préfixer le content stream avec `q <w> 0 0 <h> <x> <y> cm /PhotoX Do Q`.
  Voir `scripts/inject_photo_pdf.py`.
- **Puce ⮚ (U+2BAC) absente de toutes les polices système** -> dans le PDF on
  utilise ► (U+25BA). Le DOCX et le LaTeX gardent la vraie ⮚ (rendue par Word/LaTeX).
  Pour ⮚ partout : installer une police type Segoe UI Symbol / Arial Unicode.

## Extraire une photo D'UN PDF source (sans Pillow)
pypdf ne décode pas l'image, mais peut en sortir le flux brut :
```python
from pypdf import PdfReader
obj = reader.pages[0]['/Resources']['/XObject'].get_object()['/Image30'].get_object()
data = obj.get_data()          # flux JPEG brut si /Filter /DCTDecode
open('photo.jpg','wb').write(data)
```

## Installations qui MARCHENT ici
- `pip install pypdf` (pur python) -> OK.
- `pip install fpdf2` -> OK (pas de PIL requis pour le texte).
- `pip install --only-binary :all: pillow` -> "already satisfied" mais runtime cassé.
- `pip install reportlab` / `pip install python-docx` -> ÉCHOUENT (lxml/libxml2).
