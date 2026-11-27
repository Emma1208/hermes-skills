#!/usr/bin/env python3
"""Genere une image de signature manuscrite stylisee (PNG transparent)
a partir du nom, avec une police 'ecriture a la main'.
Usage : python3 faire_signature.py [--nom "KAKESA MUDIMBA"] [--out signature_kakesa.png]
Les polices script doivent se trouver dans ../fonts/ (ou le meme dossier que ce script).
Polices a recuperer (google/fonts raw) si absentes :
  GreatVibes-Regular.ttf, Parisienne-Regular.ttf, Sacramento-Regular.ttf, Allura-Regular.ttf
PITFALL : laisser une marge gauche ~30px et ajouter ~40px hauteur / ~60px largeur,
sinon les jambages decoratifs (1re/derniere lettre, ex Great Vibes 'K' et 'a') sont coupes.
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE / "signature_kakesa.png"

POLICES = [
    "GreatVibes-Regular.ttf",
    "Parisienne-Regular.ttf",
    "Sacramento-Regular.ttf",
    "Allura-Regular.ttf",
]
SIZE = 72  # taille police


def find_font():
    search_dirs = [HERE, HERE.parent / "fonts", HERE / "fonts", Path("/root/linkedin_app/fonts")]
    for d in search_dirs:
        if not d.exists():
            continue
        for name in POLICES:
            p = d / name
            if p.exists():
                try:
                    ImageFont.truetype(str(p), SIZE)
                    return str(p)
                except Exception:
                    continue
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nom", default="KAKESA MUDIMBA")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--police", default=None, help="force un nom de police parmi POLICES")
    a = ap.parse_args()

    chosen = a.police or find_font()
    if not chosen:
        raise SystemExit("Aucune police script trouvee. Place les .ttf dans fonts/")

    f = ImageFont.truetype(chosen, SIZE)
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)
    bbox = d.textbbox((0, 0), a.nom, font=f)
    w = bbox[2] - bbox[0] + 60
    h = bbox[3] - bbox[1] + 40

    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    # decalage pour eviter de couper les jambages (monter de 10px, gauche 30px)
    draw.text((30, 10), a.nom, font=f, fill=(0, 0, 0, 255))

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print("Signature generee:", out, "taille", img.size,
          "police", Path(chosen).name)


if __name__ == "__main__":
    main()
