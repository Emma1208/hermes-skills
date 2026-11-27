#!/bin/bash
# Valide un index.html avant déploiement : présence de </html>, blocs JS valides,
# références PWA cohérentes. Usage: validate_html.sh <fichier.html>
set -e
F="${1:?Usage: validate_html.sh <fichier.html>}"
python3 - "$F" <<'PY'
import re, sys, subprocess, tempfile, os
path = sys.argv[1]
html = open(path, encoding="utf-8", errors="replace").read()
ok = True
print("Fichier:", path, "|", len(html), "octets")
if "</html>" in html:
    print("OK  balise </html> présente")
else:
    print("ERREUR fichier tronqué (pas de </html>) — demander la suite à l'utilisateur")
    ok = False
blocks = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', html, re.S)
print("Blocs JS inline:", len(blocks))
for i, b in enumerate(blocks):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(b); name = f.name
    r = subprocess.run(["node", "--check", name], capture_output=True, text=True)
    os.unlink(name)
    if r.returncode == 0:
        print(f"OK  bloc {i} ({len(b)} octets)")
    else:
        print(f"ERREUR bloc {i}: {r.stderr.strip()[:300]}")
        ok = False
for ref in ("manifest.json", "sw.js", "./index.html", "bdd.json"):
    if ref in html or ref.lstrip("./") in html:
        print("OK  référence:", ref)
print("RESULTAT:", "VALIDE" if ok else "INVALIDE")
sys.exit(0 if ok else 1)
PY
