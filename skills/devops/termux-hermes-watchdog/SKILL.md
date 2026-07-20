---
name: termux-hermes-watchdog
description: Installer un watchdog qui surveille et relance automatiquement le "hermes gateway" sur Termux (Android, phone-as-server) — utile quand Hermes tourne 24/7 sur un téléphone sans VPS ni systemd fiable. Couvre le script de surveillance, termux-wake-lock, le lancement complètement détaché (setsid) pour survivre à un crash du gateway, l'auto-démarrage via Termux:Boot, et les pièges (BusyBox exec -a, blocage "ne pas tuer le gateway depuis le chat", pkill auto-match).
---

# Watchdog Hermes Agent sur Termux

Sur Termux il n'y a pas de systemd fiable. Quand Hermes tourne en `hermes gateway run`
(en foreground, lancé manuellement), il meurt si Termux passe en arrière-plan, OOM, ou
crash Python. Ce skill pose une boucle de surveillance qui le relance + `termux-wake-lock`
pour empêcher le téléphone de dormir.

## Quand ça s'applique
- "mets un watchdog sur Hermes", "fais tourner Hermes 24/7 sur mon téléphone"
- Le gateway tourne en manuel (`hermes gateway status` → "Running manually, not as a system service")
- Pas de VPS, Termux sur Android

## Prérequis
- Termux depuis F-Droid (pas Google Play). Optionnel : Termux:Boot pour l'auto-démarrage.
- `termux-wake-lock` présent (natif). Vérifier : `command -v termux-wake-lock`.
- Le binaire Hermes : `/usr/local/lib/hermes-agent/venv/bin/hermes` (ou `hermes` dans PATH).

## Étapes

1. **Créer le dossier dédié** (jamais dans /root direct pour éviter les fuites git) :
   `/root/hermes-guard/`

2. **Écrire le watchdog** (voir `templates/watchdog.sh`). Points clés :
   - `termux-wake-lock` en haut.
   - Boucle `while true` qui relance `hermes gateway run --replace` si le process
     `hermes gateway` n'est plus là. Le `--replace` nettoie toute instance fantôme
     résiduelle (évite l'erreur "second dispatcher escapes the service").
   - `sleep 15` entre les checks ; `sleep 5` après un relance pour laisser init.
   - Log horodaté dans `hermes-watchdog.log`.
   - Optionnel : `termux-notification` (faible priorité) pour signaler un redémarrage.

3. **Lancer DÉTACHÉ** pour qu'il survive à la session :
   - Soit via `terminal(background=true)` de Hermes (trace le process).
   - Soit en shell : `setsid nohup bash /root/hermes-guard/watchdog.sh >/dev/null 2>&1 &`
   - ⚠️ NE PAS lancer avec `nohup ... & disown` dans un `terminal()` normal de Hermes :
     le wrapper shell est refusé. Utiliser `background=true` ou `setsid`.

4. **Auto-démarrage au boot** : écrire `/root/.termux/boot/start-hermes-watchdog.sh`
   (voir template) qui fait `termux-wake-lock` puis `setsid nohup bash ...watchdog.sh &`.
   Termux:Boot exécute `~/.termux/boot/*.sh` au démarrage du téléphone.

## Vérification (SANS tuer le vrai gateway)
Tu ne peux PAS tuer le vrai `hermes gateway` depuis le chat Hermes : le terminal
tourne *dans* le gateway, donc le tuer tuerait ta propre commande (bloqué par sécurité
« cannot restart or stop the gateway from inside the gateway process »).

À la place, valide le *mécanisme de relance* avec un leurre :
- `is_running(){ pgrep -f "MARK"; }` puis `launch(){ nohup python3 -c "import time;time.sleep(1000)" ... & }`
- Tuer le leurre par PID exact (`kill -9 $(cat pidfile)`) → le watchdog doit écrire
  "dummy absent -> RELANCE" et relancer un nouveau PID.
- Nettoyer : `pkill -f "MARK"; rm -f /tmp/wdtest.*`

Vérifier ensuite l'état :
- `pgrep -af "hermes-guard/watchdog.sh"` → doit lister le watchdog.
- Gateway vivant : `P=$(python3 -c "import json;print(json.load(open('/root/.hermes/gateway.pid'))['pid'])"); kill -0 "$P" && echo VIT`
  (utiliser `kill -0` + lecture du PID file, PAS `hermes gateway status` depuis le chat).

## Pièges
1. **BusyBox `exec -a NAME sleep infinity` échoue** sur Termux : « applet not found »,
   car BusyBox lit argv[0] pour choisir l'applet. Pour un leurre de test, utiliser
   `python3 -c "import time;time.sleep(1000)"` (vrai binaire), pas un applet BusyBox.
2. **`pkill -f "dummy_wd_test"` s'auto-matche** : la chaîne figure dans la cmd du
   `pkill` lui-même → il se tue (exit -15). Toujours tuer par PID exact (`kill $(cat pidfile)`),
   ou filtrer avec `pgrep -x` (nom de comm exact) et/ou exclure le script.
3. **Ne pas tuer le gateway depuis le chat** (voir Vérification).
4. **Batterie** : `termux-wake-lock` draine vite → téléphone en charge.
5. **Coexistence** : un autre watchdog (ex. bot crypto dans `~/.termux/boot/watchdog.sh`)
   peut tourner en parallèle sans conflit, tant qu'il ne matche pas `hermes gateway`.

## Pour arrêter le watchdog Hermes
`pkill -f hermes-guard/watchdog.sh` (le gateway restera en l'air jusqu'à un kill manuel).
