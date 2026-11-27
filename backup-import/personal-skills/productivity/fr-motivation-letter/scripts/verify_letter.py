#!/usr/bin/env python3
"""verify_letter.py — coordinate-based check for the fr-motivation-letter layout.
Usage: python3 verify_letter.py <pdf_path>
Prints page count and flags right-column blocks whose x0 deviates from ~286pt.
Right-column blocks (destinataire, formule d'appel, signature) MUST have x0 ~ 286.
Trust coordinates over vision_analyze, which misreports right-aligned as left-aligned.
"""
import sys, fitz

path = sys.argv[1] if len(sys.argv) > 1 else "/root/linkedin_app/Lettre_Motivation_Generale.pdf"
d = fitz.open(path)
print("PAGES:", d.page_count)
if d.page_count != 1:
    print("WARN: letter should be 1 page")
p = d[0]
words = p.get_text("words")
print("--- RIGHT-COLUMN words (x0 should be ~286 for dest/formule/signature) ---")
for w in sorted(words, key=lambda w:(round(w[1]), w[0])):
    x0,y0,x1,y1,txt,*_ = w
    if x0 < 250:
        continue
    if y0 < 95:
        continue
    flag = "" if 270 <= x0 <= 300 else "  <-- CHECK (not ~286)"
    print(round(y0,1), round(x0,1), repr(txt), flag)
