# -*- coding: utf-8 -*-
"""Inject a JPEG photo into an fpdf2-generated PDF WITHOUT Pillow.

Why: fpdf2.image() requires Pillow, which is broken on some Termux/ARM builds
(`dlopen failed: library "libc.musl-aarch64.so.1" not found`). So:
  1. build the TEXT pdf with fpdf2 (no image),
  2. run THIS on the result to add the JPEG as an XObject /DCTDecode and
     draw it with a `q ... cm /Name Do Q` op prepended to the page stream.

Usage:
  python inject_jpeg_pdf.py CV.pdf photo.jpg out.pdf --w 34 --h 45.3 \
      --x 150 --y 270 --name PhotoX
  (coordinates in PDF points; defaults place a ~34x45 mm photo top-right.)

The JPEG dimensions are read from its SOF marker (no Pillow needed) when
--w/--h are omitted.
"""
import argparse
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (NameObject, DictionaryObject, StreamObject,
                           NumberObject)


def jpeg_size(path):
    """Read JPEG w/h from the SOF marker without Pillow."""
    with open(path, "rb") as f:
        data = f.read()
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                      0xC9, 0xCA, 0xCB, 0xCD):
            h = int.from_bytes(data[i + 5:i + 7], "big")
            w = int.from_bytes(data[i + 7:i + 9], "big")
            return w, h
        seglen = int.from_bytes(data[i + 2:i + 4], "big")
        i += 2 + seglen
    raise ValueError("JPEG dimensions not found")


def inject(src_pdf, jpeg_path, out_pdf, x, y, w, h, name="/PhotoX",
           page_index=0):
    reader = PdfReader(src_pdf)
    page = reader.pages[page_index]
    jpeg = open(jpeg_path, "rb").read()
    jw, jh = jpeg_size(jpeg_path)
    if w is None:
        w = jw * (h / jh) if h else jw
    if h is None:
        h = jh * (w / jw) if w else jh

    # 1) XObject image (DCTDecode JPEG, no decode needed)
    img = StreamObject()
    img._data = jpeg
    img[NameObject("/Type")] = NameObject("/XObject")
    img[NameObject("/Subtype")] = NameObject("/Image")
    img[NameObject("/Filter")] = NameObject("/DCTDecode")
    img[NameObject("/Width")] = NumberObject(int(w) if w else jw)
    img[NameObject("/Height")] = NumberObject(int(h) if h else jh)
    img[NameObject("/ColorSpace")] = NameObject("/DeviceRGB")
    img[NameObject("/BitsPerComponent")] = NumberObject(8)

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
    xo[NameObject(name)] = img

    # 2) prepend draw op: q w 0 0 h x y cm /Name Do Q
    draw = (f"q\n{w:.2f} 0 0 {h:.2f} {x:.2f} {y:.2f} cm\n"
            f"{name} Do\nQ\n")
    contents = page.get_contents()
    if isinstance(contents, list):
        merged = b"".join(c.get_data() for c in contents)
    else:
        merged = contents.get_data()
    new_stream = StreamObject()
    new_stream.set_data(draw.encode("latin-1") + merged)
    page[NameObject("/Contents")] = new_stream

    writer = PdfWriter()
    writer.add_page(page)
    for p in reader.pages[1:]:
        writer.add_page(p)
    writer.write(out_pdf)
    print(f"Photo injectee dans {out_pdf} "
          f"(page {page_index+1}, x={x:.1f} y={y:.1f} w={w:.1f} h={h:.1f})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("jpeg")
    ap.add_argument("out")
    ap.add_argument("--x", type=float, default=None)
    ap.add_argument("--y", type=float, default=None)
    ap.add_argument("--w", type=float, default=None)
    ap.add_argument("--h", type=float, default=None)
    ap.add_argument("--name", default="/PhotoX")
    ap.add_argument("--page", type=int, default=0)
    args = ap.parse_args()

    PW_PT, PH_PT = 595.28, 841.89  # A4
    mm = 2.834645669
    if args.w is None:
        args.w = 34 * mm
    if args.h is None:
        args.h = 45.3 * mm
    if args.x is None:
        args.x = PW_PT - 18 * mm - args.w
    if args.y is None:
        args.y = PH_PT - 16 * mm - args.h

    inject(args.src, args.jpeg, args.out, args.x, args.y,
           args.w, args.h, args.name, args.page)


if __name__ == "__main__":
    main()
