#!/bin/bash
# Active GitHub Pages, crée .nojekyll (obligatoire), attend le build et vérifie les URLs.
# Usage: GITHUB_TOKEN=ghp_xxx ./setup_pages.sh <owner> <repo> [fichier1 fichier2 ...]
set -e
: "${GITHUB_TOKEN:?Définir GITHUB_TOKEN dans l'environnement}"
OWNER="${1:?owner}"; REPO="${2:?repo}"; shift 2 || true
BASE="https://api.github.com/repos/$OWNER/$REPO"
H=(-H "Authorization: token $GITHUB_TOKEN" -H "Accept: application/vnd.github+json")

echo "== activation Pages =="
curl -s -m 30 -X POST "${H[@]}" "$BASE/pages" \
  -d '{"source":{"branch":"main","path":"/"}}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('  ',d.get('html_url') or d.get('message'))"

echo "== .nojekyll (évite le build errored) =="
SHA=$(curl -s -m 20 "${H[@]}" "$BASE/contents/.nojekyll" | python3 -c "import sys,json; print(json.load(sys.stdin).get('sha',''))" 2>/dev/null || echo "")
if [ -z "$SHA" ]; then
  curl -s -m 30 -X PUT "${H[@]}" "$BASE/contents/.nojekyll" \
    -d '{"message":"Désactivation de Jekyll","content":""}' -o /dev/null -w "  HTTP %{http_code}\n"
else
  echo "  déjà présent"
fi

echo "== attente du build =="
for i in 1 2 3 4 5 6 7 8; do
  sleep 10
  ST=$(curl -s -m 20 "${H[@]}" "$BASE/pages" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status'))")
  echo "  tentative $i: $ST"
  [ "$ST" = "built" ] && break
done

echo "== vérification des URLs =="
for f in "" "$@"; do
  u="https://$OWNER.github.io/$REPO/$f"
  printf "  %-24s " "${f:-index racine}"
  curl -s -m 20 -o /dev/null -w "HTTP %{http_code} | %{content_type}\n" "$u"
done
