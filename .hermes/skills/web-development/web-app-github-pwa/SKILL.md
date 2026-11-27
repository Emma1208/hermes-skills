---
name: web-app-github-pwa
description: "Déployer une application web statique (HTML/JS) sur GitHub avec une base de données JSON (bdd.json) synchronisée par PAT, GitHub Pages et installation PWA sur mobile."
version: 1.3.0
author: Hermes Agent (pour Emmanuel)
license: MIT
platforms: [linux, android, termux]
metadata:
  hermes:
    tags: [GitHub, Pages, PWA, JSON, PAT, mobile, static-app, Termux]
---

# Web App + GitHub JSON + PWA

Procédure éprouvée pour transformer un fichier HTML isolé en application installable sur téléphone, avec persistance des données dans un fichier JSON sur GitHub.

## Quand l'utiliser
- L'utilisateur envoie un `index.html` (app locale, often `localStorage`) et veut :
  1. le déployer sur GitHub ;
  2. que les données soient partagées entre navigateurs/appareils via un `bdd.json` ;
  3. l'installer sur Android en PWA.

## Étapes

### 1. Vérifier le HTML reçu
- Les messages WhatsApp coupent souvent les longs fichiers (~20 000 caractères). Comparer la fin du fichier reçu : chercher `</html>`. Si absent, demander la suite en plusieurs messages.
- Extraire les blocs `<script>` inline et valider avec `node --check` :
  ```python
  import re
  blocks = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', html, re.S)
  ```
- Vérifier les références de fichiers (ex. `manifest.json` pointant vers `compta-syscohada-v2.html` alors que le fichier s'appelle `index.html`) et les harmoniser.

### 2. Créer le dépôt et les fichiers via l'API GitHub
Toujours passer par un **script fichier** (`write_file` puis `bash`) pour ne jamais exposer le PAT dans la ligne de commande (le scan de sécurité bloque sinon).
- Créer le dépôt : `POST https://api.github.com/user/repos` avec `{"name":..., "private":false, "auto_init":true}`.
- Upload : `PUT /repos/<owner>/<repo>/contents/<file>` avec `{"message":..., "content":"<base64>"}`. Pour une mise à jour, inclure le `sha` existant (GET préalable).
- `bdd.json` : structurer exactement comme l'objet `state` de l'app + métadonnées `app`, `version`, `cle_localStorage`, `ts`.

### 3. Ajouter le pont GitHub BDD dans le HTML
- Exposer l'état : `window.__gcState = () => state;` et `window.__gcSetState = value => {...; init();}`.
- Modifier `save()` pour appeler `window.GitHubBDD.schedulePush()` après le `localStorage`.
- **Apps à plusieurs états `localStorage`** : repérer TOUTES les clés (`grep localStorage.getItem|setItem`) — ex. un éditeur CV (`cv-kakesa-index-v1`) + un module offres/lettres (`dossier-candidatures-v1`). Exposer `window.__appState = () => ({...})` avec un accesseur par état, appeler `schedulePush()` dans **chaque** fonction de persistance, et stocker les deux objets dans `bdd.json` avec les noms de clés.
- Pont `GitHubBDD` :
  - `pull()` : GET `/contents/bdd.json`, décoder `atob` + `decodeURIComponent(escape(...))`, comparer `ts` local/distant (le plus récent gagne), `sha` mémorisé.
  - `push()` : PUT avec `{message, content, sha}` ; file d'attente `pending` si sync en cours.
  - config (owner/repo/path/token) dans `localStorage`, panneau modal + boutons Charger/Envoyer.
  - sync auto toutes les 120 s.
- **Anti-perte de données (OBLIGATOIRE — voir `references/sync-data-loss.md`)** : quatre bugs classiques détruisent les saisies, à corriger dès la création du pont :
  1. `push()` doit **aligner le `ts` local** sur celui envoyé (`lastLocalTs = ts` + `state.ts = ts` via `__gcSetTs`). Sinon le `pull()` auto voit « distant plus récent » et écrase les saisies non envoyées.
  2. Un drapeau `dirty` doit empêcher `pull()` de remplacer l'état local tant qu'une modification n'est pas poussée.
  3. `schedulePush()` ne doit **pas** faire `clearTimeout` à chaque frappe : garder le premier timer (`if (timer) return`) sinon rien n'est jamais envoyé.
  4. En cas d'échec réseau, garder les données locales et l'indiquer dans le message de statut.
- `api.github.com` renvoie `Access-Control-Allow-Origin: *` → fonctionne depuis `file://` et depuis Pages. Ne jamais mettre le PAT en dur dans le HTML.

### 4. PWA (installation mobile)
- `manifest.json` : `name`, `short_name`, `start_url:"./index.html"`, `display:"standalone"`, `theme_color`, icônes 192/512/maskable.
- `sw.js` : cache first pour les ressources statiques, **toujours `fetch` pour `api.github.com`** (jamais de cache des données). `skipWaiting()` + `clients.claim()`.
- Icônes PNG sans dépendance : générer en Python pur avec `zlib` + `struct` (IHDR/IDAT/IEND, RGB). Vérifier la signature `\x89PNG\r\n\x1a\n`.
- Injecter dans `<head>` : `<link rel="manifest">`, `<link rel="apple-touch-icon">`, `<meta name="theme-color">`, `<meta name="apple-mobile-web-app-capable" content="yes">`. Enregistrer le SW avant `</body>`.
- **Proposer l'installation depuis la page** : capturer `beforeinstallprompt` (`preventDefault()` + mémoriser l'événement), afficher une bannière avec un bouton qui appelle `deferred.prompt()` dans le geste utilisateur, gérer `appinstalled` et un bouton ✕ mémorisé. Prévoir un repli `alert` pour iOS/Safari où l'événement n'existe pas. Template : `templates/install-prompt.html`; détails et piège d'ancrage HTML : `references/install-prompt.md`.

### 4b. Upgrade PWA d'une app déjà déployée
Quand l'utilisateur renvoie une version modifiée d'une app déjà en ligne :
- **Inspecter d'abord l'existant** : lister les fichiers du dépôt et lire `manifest.json` / `sw.js`. Ils référencent souvent l'ancien nom de fichier (`compta-syscohada-v2.html`) ou des icônes CDN distantes.
- Vérifier que le HTML envoyé contient bien `<link rel="manifest">`, `<link rel="apple-touch-icon">`, `<meta name="theme-color">` et l'enregistrement du SW. Ajouter `apple-touch-icon` s'il manque (cas réel).
- Ne pas supprimer les données existantes : voir `references/pwa-upgrade-existing-app.md`.

### 5. GitHub Pages — PIÈGE CRITIQUE
- Activer : `POST /repos/<owner>/<repo>/pages` avec `{"source":{"branch":"main","path":"/"}}`. Un 409 « already enabled » est normal.
- **Toujours créer un fichier `.nojekyll` vide à la racine** (contenu base64 `""`). Sans lui, le build passe en `errored` dès qu'on ajoute des fichiers PNG/manifest/sw : les fichiers restent 404 alors que `bdd.json` (déjà publié) répond 200.
- Attendre le build (`GET /pages` → `status: built`), puis vérifier chaque URL avec `curl -w "HTTP %{http_code} | %{content_type}"`.
- URL finale : `https://<owner>.github.io/<repo>/` — c'est cette URL qu'il faut ouvrir dans Chrome (pas le lien `/blob/main/...` qui affiche le code source).

### 6. Vérification finale
- Tester réellement GET/PUT `bdd.json` avec le PAT, avec le `sha`, puis restaurer le fichier à son état initial.
- Confirmer : CORS `*`, titre distant correct, tous les fichiers PWA en HTTP 200 avec le bon MIME.

## Fichiers de support (linked_files)

- `scripts/validate_html.sh <fichier.html>` — vérifie `</html>`, valide chaque bloc JS avec `node --check`, contrôle les références.
- `scripts/make_icons.py [dossier]` — génère les 3 icônes PNG sans dépendance (zlib + struct).
- `scripts/deploy_files.sh <owner> <repo> <local:remote> ...` — upload via API avec `GITHUB_TOKEN` en variable d'environnement (jamais en argument), gère le SHA des mises à jour. **Ne jamais passer le base64 en argument de `python3 -c`** : un HTML de ~600 Ko déclenche `Argument list too long` ; le script lit le fichier lui-même. Lancer `bash -n` après toute modification de script : une apostrophe dans un `python3 -c "..."` a provoqué `unexpected EOF while looking for matching quote`.
- `scripts/setup_pages.sh <owner> <repo> [fichiers...]` — active Pages, crée `.nojekyll`, attend le build, vérifie les URLs.
- `templates/manifest.json`, `templates/sw.js`, `templates/bdd.json`, `templates/install-prompt.html` — modèles à copier/adapter (remplacer `APP-NAME` / `APP_NAME` / `APP_PREFIX`).
- `references/install-prompt.md` — événement `beforeinstallprompt`, repli iOS, et piège du point d'ancrage HTML (nav générée par JS).
- `references/sync-data-loss.md` — pourquoi un pont « simple » perd des données (ts local non aligné, drapeau dirty, clearTimeout) et le correctif exact, étape par étape.
- `references/troubleshooting.md` — erreurs fréquentes et leurs solutions.
- `references/repo-consolidation.md` — fusionner un dépôt backup dans le dépôt « cerveau » (audit croisé, transfert idempotent par lots, vérification, suppression sécurisée).
- `references/pwa-upgrade-existing-app.md` — migrer une app déjà déployée vers `bdd.json` et une PWA complète sans perdre les données (casse, fusion de BDD parasite, vérification).

## Pièges rencontrés
- **Casse des noms de fichiers** : GitHub est sensible à la casse. Une app envoyée pointait vers `BDD.json` alors que le dépôt contenait `bdd.json` → l'app aurait créé un second fichier et perdu la synchro. Harmoniser TOUJOURS les références (`grep -o 'BDD.json'`) vers le nom réel du fichier avant déploiement. Si un fichier parasite existe déjà et contient de vraies données, les **fusionner** dans le fichier canonique avant de corriger les références, et garder le parasite comme copie de sécurité.
- **Patch de `push()` : surveiller le `try {`** — un remplacement de bloc peut avaler le `try` d'origine ; `node --check` donne alors `SyntaxError: Unexpected token 'catch'`. Voir `references/sync-data-loss.md`.
- **Point d'ancrage pour patcher le HTML** : ne jamais chercher un élément généré par JS (ex. `<nav id="nav"></nav>` rempli par `$("#nav").innerHTML=...`). Cibler du HTML statique (`<main class="wrap">`, `</body>`). Un script Python qui échoue avant `write()` laisse le fichier intact — corriger l'ancrage et relancer.
- Messages WhatsApp tronqués → demander la fin en plusieurs messages.
- `grep -qw "ma-compta-syscohada"` correspond aussi à `compta-syscohada` (sous-chaîne) → comparer les noms exacts avec `echo " $KEEP " | grep -q " $REPO "`.
- Token exposé dans une commande → blocage du scan ; passer par un fichier script.
- Chrome headless sur Termux/PRoot : `udev_watcher` → SIGTRAP, NETLINK indisponible. Ne pas insister ; tester l'API directement avec curl à la place.
- Org GitHub via `POST /user/organizations` → 404 définitif (route dépréciée) : un « domaine » GitHub gratuit passe par `<user>.github.io` ou une organisation créée manuellement avec compte vérifié.

## Préférences utilisateur ( vérifiées en session )
- Répondre en français, de façon concise et actionnable, sans long récit de processus.
- Si l'utilisateur dit « stop / donne moi juste ces informations » : arrêter immédiatement les outils et ne donner que les valeurs concrètes.
- L'utilisateur accorde des approbations globales (« toujours approuvé ») : ne pas redemander à chaque fois ; regrouper le travail dans des scripts et rapporter à la fin. Respecter toute interruption explicite.

## Sécurité
- PAT saisi par l'utilisateur dans le navigateur, stocké dans `localStorage` (à ressaisir par appareil).
- Rappeler de révoquer/régénérer les tokens collés en clair dans une conversation : https://github.com/settings/tokens
