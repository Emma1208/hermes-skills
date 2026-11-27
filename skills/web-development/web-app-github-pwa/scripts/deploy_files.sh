#!/bin/bash
# Déploie des fichiers sur GitHub via l'API sans exposer le PAT dans la ligne de commande.
# Le token est lu depuis la variable d'environnement GITHUB_TOKEN.
# Usage: GITHUB_TOKEN=ghp_xxx ./deploy_files.sh <owner> <repo> <fichier:chemin distant> [...]
set -e
: "${GITHUB_TOKEN:?Définir GITHUB_TOKEN dans l'environnement}"
OWNER="${1:?owner manquant}"; REPO="${2:?repo manquant}"; shift 2
API="https://api.github.com/repos/$OWNER/$REPO/contents"
H=(-H "Authorization: token $GITHUB_TOKEN" -H "Accept: application/vnd.github+json")

for PAIR in "$@"; do
  LOCAL="${PAIR%%:*}"; REMOTE="${PAIR#*:}"
  [ -f "$LOCAL" ] || { echo "FICHIER MANQUANT: $LOCAL"; continue; }
  SHA=$(curl -s -m 20 "${H[@]}" "$API/$REMOTE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('sha',''))" 2>/dev/null || echo "")
  B64=$(base64 -w 0 "$LOCAL")
  if [ -n "$SHA" ]; then
    PAYLOAD=$(python3 -c "import json,sys; print(json.dumps({'message':'Mise à jour $REMOTE','content':sys.argv[1],'sha':sys.argv[2]}))" "$B64" "$SHA")
  else
    PAYLOAD=$(python3 -c "import json,sys; print(json.dumps({'message':'Ajout $REMOTE','content':sys.argv[1]}))" "$B64")
  fi
  curl -s -m 30 -X PUT "${H[@]}" "$API/$REMOTE" -d "$PAYLOAD" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(('OK  ' if d.get('content') else 'ECHEC ')+'$REMOTE '+str(d.get('message','')))"
done
