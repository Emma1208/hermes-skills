# Signature recipe (KAKESA)

## 1. Source asset
`~/Candidatures/Modèles/signature_seule.png` — transparent-bg PNG of his blue handwritten
signature. If missing, the user can export it from his phone "Signatures" app (share/export → PNG)
or write it on paper and photo it; then run the extraction below.

## 2. Extract signature from a phone screenshot/photo (PIL only, numpy NOT available)
The user sends the bare signature image (white/light bg, blue scribble). Strip white → transparent,
crop to bounding box:

```python
from PIL import Image
img = Image.open('signature_source.jpg').convert('RGBA')
W,H = img.size
data = img.getdata()
new = []; minx,miny,maxx,maxy = W,H,0,0
for i,(r,g,b,a) in enumerate(data):
    if r>235 and g>235 and b>235:
        new.append((r,g,b,0))
    else:
        new.append((r,g,b,255)); x=i%W; y=i//W
        minx=min(minx,x); maxx=max(maxx,x); miny=min(miny,y); maxy=max(maxy,y)
img.putdata(new)
pad=8
img.crop((max(0,minx-pad),max(0,miny-pad),min(W-1,maxx+pad),min(H-1,maxy+pad))).save('signature_seule.png')
```

## 3. Embed in HTML (the ONLY method that renders in LibreOffice)
Do NOT rebuild ODT frames. Put a base64 data URI in the `<img>`:

```html
<img src="data:image/png;base64,__SIG__" style="height:46px;width:auto">
```

Then:
```bash
B64=$(base64 -w0 ~/Candidatures/Modèles/signature_seule.png)
sed "s|__SIG__|data:image/png;base64,$B64|g" doc.html > doc_b64.html
soffice --headless --convert-to pdf --outdir <out> doc_b64.html
soffice --headless --convert-to odt --outdir <out> doc_b64.html   # editable copy
```

## 4. WHY this and not ODT
Reassembling the ODT (`<draw:frame>` + `style:name="FrSig"` in styles.xml + image in
`Pictures/` + manifest entry) renders NOTHING in soffice — the frame is silently dropped even
when XML validates and the PNG is a valid 120x99 RGBA. Base64-in-HTML is bulletproof.
