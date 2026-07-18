# GitHub Skills Backup — recette détaillée et vérifications

## 1. Créer le dépôt (si besoin)
```
export GITHUB_TOKEN='ghp_...'
curl -s -H "Authorization: token $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" \
  -d '{"name":"hermes-skills","description":"Backup skills Hermes","private":false,"auto_init":false}' \
  https://api.github.com/user/repos
```

## 2. Cloner + copier
```
git clone "https://Emma1208:${GITHUB_TOKEN}@github.com/Emma1208/<repo>.git" /root/<repo>-push
cp -r /root/.hermes/skills/. /root/<repo>-push/
# nettoyer caches
find /root/<repo>-push -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find /root/<repo>-push -name "*.pyc" -delete 2>/dev/null
```

## 3. Commit + push (BRANCHE = main)
```
cd /root/<repo>-push
git add -A
git -c user.name="KAKESA MUDIMBA Emmanuel-Dieudonne" -c user.email="kakesamudimba@gmail.com" \
  commit -m "Backup skills Hermes Agent - persistance inter-session"
git push -u origin main        # PAS master
unset GITHUB_TOKEN
```

## 4. Vérifier côté dépôt (ne pas se fier au seul push local)
```
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/Emma1208/<repo>/contents | python3 -c "import sys,json;[print(x['name']) for x in json.load(sys.stdin)]"
# vérifier un fichier précis (correction présente ?)
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://raw.githubusercontent.com/Emma1208/<repo>/main/<chemin>/fichier.py" | grep -c "mot_cle"
```

## 5. Alternative API (sans clone) — si clone bloqué
`PUT /repos/Emma1208/<repo>/contents/<path>` avec body JSON
`{"message":"...","content":"<base64>","sha":"<sha existant si update>"}`.
base64 : `content=$(base64 -w0 fichier)`.

## Pièges réels de la session
- `git push origin master` → erreur « src refspec master does not match ».
  Cause : branche par défaut = `main`. Corriger en `git push -u origin main`.
- `git clone` a expiré (gate d'approbation) la 1re fois ; relancé avec accord
  utilisateur a fonctionné. Ne pas rejouer aveuglément un clone bloqué.
- Le `git commit` peut échouer silencieusement si identité git absente ou si le
  working tree est « clean » alors que les fichiers n'ont pas été copiés (vérifier
  `ls` du dossier avant commit).
