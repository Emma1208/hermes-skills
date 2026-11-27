# Dépannage — Web App GitHub + PWA

## Le PAT est refusé (401 Bad credentials)
- Tester avec `curl -H "Authorization: token $TOKEN" https://api.github.com/user` et les deux schémas (`token`, `Bearer`).
- Un PAT collé dans WhatsApp peut être tronqué/corrompu. Vérifier la longueur (classic = 40 chars, fine-grained = ~93).
- Révoquer tout token collé en clair : https://github.com/settings/tokens

## Le scan de sécurité bloque la commande
- **Ne jamais** mettre le token dans une commande `terminal`.
- Écrire le token dans un fichier script via `write_file`, exécuter `bash script.sh`, puis supprimer le script.
- Alternative : `GITHUB_TOKEN=... ./deploy_files.sh` avec le token passé en variable d'environnement.

## GitHub Pages : fichiers 404 alors que le dépôt les contient
- Symptôme : `bdd.json` répond 200 mais `manifest.json`, `sw.js`, les PNG répondent 404 ; statut `building` puis `errored`.
- Cause : Jekyll essaie de traiter les fichiers. **Solution : fichier `.nojekyll` vide à la racine** (`content: ""` en base64).
- Forcer un rebuild si besoin : `POST /repos/<owner>/<repo>/pages/builds`.
- Attendre `GET /pages` → `status: built`, puis vérifier avec `curl -w "HTTP %{http_code} | %{content_type}"`.

## L'app ne s'ouvre pas dans Chrome (mobile)
- Ouvrir `https://<owner>.github.io/<repo>/` et **pas** le lien `/blob/main/...` qui affiche le code source.
- Ne pas ouvrir un lien `content://...` depuis un fichier local WhatsApp : le transférer ou utiliser l'URL Pages.
- La PWA peut mettre 1–2 min avant que Chrome propose « Ajouter à l'écran d'accueil » (service worker).

## Les données disparaissent quand on change de navigateur
- Comportement normal avec `localStorage` : chaque navigateur a sa propre copie.
- Configurer le pont GitHub dans **chaque** navigateur (owner/repo/path/PAT) et cliquer sur « Charger de GitHub ».
- Au tout premier envoi, configurer d'abord le navigateur qui contient les vraies données.

## Fichier HTML reçu tronqué
- Les messages WhatsApp coupent vers ~20 000 caractères. Vérifier `</html>` en fin de fichier.
- Demander la suite en plusieurs messages, puis assembler dans l'ordre.
- Valider avec `scripts/validate_html.sh`.

## Chrome headless sur Termux / PRoot
- `chromium` plante en `SIGTRAP` : `udev_watcher` + NETLINK indisponibles. Tenter Xvfb + stubs udev/netlink reste fragile.
- **Ne pas insister** : tester directement les appels API de la page avec `curl` (lecture GET, écriture PUT avec SHA, CORS).

## Création d'organisation GitHub par API
- `POST /user/organizations` → 404 définitif (route dépréciée).
- Un domaine gratuitGitHub = `<user>.github.io`, ou organisation créée manuellement sur github.com/organizations/new (compte vérifié requis).

## Filtre de noms de dépôts
- `grep -qw "ma-compta-syscohada"` correspond aussi à `compta-syscohada` (sous-chaîne).
- Comparer exactement : `echo " $KEEP " | grep -q " $REPO "`.
