#!/usr/bin/env python3
"""
Clone a retained .odt template and edit its TEXT IN PLACE (no layout change).

WHY: the user keeps canonical editable CV/letter templates in
~/Candidatures/Modèles/ (CV_KAKESA_MUDIMBA_rempli.odt, Lettre_Modele_KAKESA.odt).
When tailoring for an offer he may say "use the model we retained" — that means
EDIT THE EXISTING .odt, NOT author a brand-new HTML/CSS layout. A fresh layout is
rejected ("pourquoi est-ce que tu fais des choses sans réfléchir ?").

HOW: an .odt is a zip. We edit content.xml by replacing exact <text:span> strings.
The structure / styles / page setup stay 100% untouched (that's the whole point).

USAGE:
  python3 edit_odt_template.py --src MODELE.odt --out CIBLE.odt --map rempl.json
  # OR inline (handy for 1-2 edits):
  python3 edit_odt_template.py --src MODELE.odt --out CIBLE.odt \
      --replace "ancien texte||nouveau texte" --replace "autre||autre"

rempl.json shape: { "exact old text": "new text", ... }
  - Both keys and values may contain & < > : write them NATURALLY, the script
    XML-escapes them (& -> &amp; etc.) so they match/insert correctly in content.xml.
  - Use EXACT substrings as they appear in the rendered doc (no regex).
  - If a search string is not found, the script WARNS and skips it (does not crash)
    so you can fix the mapping instead of silently shipping the old text.

After running, convert to PDF to verify:
  soffice --headless --convert-to pdf --outdir <DIR> CIBLE.odt
  pdftoppm -png -r 90 CIBLE.pdf p.png && vision_analyze p-1.png "..."
"""
import argparse, json, os, re, shutil, sys, zipfile

def xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="retained .odt template")
    ap.add_argument("--out", required=True, help="output .odt (cloned + edited)")
    ap.add_argument("--map", help="JSON file {old: new}")
    ap.add_argument("--replace", action="append", default=[],
                    help='"old||new" pair, repeatable')
    args = ap.parse_args()

    repl = {}
    if args.map:
        with open(args.map, encoding="utf-8") as f:
            repl.update(json.load(f))
    for pair in args.replace:
        if "||" not in pair:
            sys.exit("ERROR --replace needs 'old||new'")
        old, new = pair.split("||", 1)
        repl[old] = new
    if not repl:
        sys.exit("ERROR: nothing to replace (use --map or --replace)")

    work = "/tmp/odt_edit_" + str(os.getpid())
    if os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(work)
    with zipfile.ZipFile(args.src) as z:
        z.extractall(work)

    xml_path = os.path.join(work, "content.xml")
    with open(xml_path, encoding="utf-8") as f:
        xml = f.read()

    for old, new in repl.items():
        o, n = xml_escape(old), xml_escape(new)
        if o not in xml:
            print("  [WARN] search string NOT FOUND, skipped:", repr(old[:60]))
            continue
        xml = xml.replace(o, n, 1)
        print("  [ok] replaced:", repr(old[:50]), "->", repr(new[:50]))

    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml)

    if os.path.exists(args.out):
        os.remove(args.out)
    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(work):
            for fn in files:
                fp = os.path.join(root, fn)
                z.write(fp, os.path.relpath(fp, work))

    shutil.rmtree(work)
    print("EDITED ->", args.out)

if __name__ == "__main__":
    main()
