# Telegram Bot Deploy — PTB (Termux / Linux)

Recette concrète + pièges rencontrés en déployant `@Gestionadresseemkbot` (gestion clients).

## 1. Isolation venv (CRITIQUE)
Ne JAMAIS lancer un bot client dans le venv Hermes (`/root/hermes_agent/venv` ou `~/.hermes/hermes-agent/venv`).
Créer un venv dédié à côté du bot :
```bash
cd /root/freelance-clients-bot
python3 -m venv venv
venv/bin/pip install python-telegram-bot==22.6 python-dotenv
venv/bin/python bot_clients.py
```
Lancer dans le venv Hermes a provoqué `TimedOut` + collisions de modules.

## 2. Timeouts PTB 22.6 (réseau lent)
`run_polling()` N'accepte PAS `read_timeout`/`connect_timeout`/`pool_timeout` (→ `TypeError`).
Les mettre sur le builder :
```python
app = (Application.builder().token(TOKEN)
       .connect_timeout(30).read_timeout(30).pool_timeout(30).build())
app.run_polling(allowed_updates=Update.ALL_TYPES)
```
Sans ça, sur lien Telegram lent (5s+ de latence) → `telegram.error.TimedOut`.

## 3. Garde-fou plage de token
Token Hermes = plage `820389...` (EXCLUSIF). Un bot client doit utiliser un token DIFFÉRENT de @BotFather
(ex : `895028...`). Ajouter au démarrage :
```python
if not TOKEN or TOKEN.startswith("820389"):
    raise SystemExit("⛔ refus token Hermes (conflit 409)")
```
Utiliser le token `820389` pour un bot client → HTTP 409 → coupe la passerelle Hermes.

## 4. Exclusivité du polling (getUpdates vole la file)
Un bot en long-polling est le SEUL propriétaire de la file d'updates de son token.
Un `curl .../getUpdates` manuel (même pour diagnostiquer) consomme les updates en attente
→ le bot « reçoit mais ne répond pas » (double checkmarks, pas de réponse).
NE JAMAIS appeler getUpdates sur un token qu'un bot poll déjà.
Pour vider une file bloquée : `getUpdates?offset=<dernier_update_id+1>&timeout=1` UNE fois, puis laisser le bot reprendre.

## 5. Handlers de debug (échecs silencieux)
Sans ça, une exception dans un handler se traduit par « message lu, pas de réponse » sans rien logger :
```python
import logging
logging.basicConfig(level=logging.INFO)
async def err_handler(update, ctx):
    logging.getLogger("bot").error("ERR %s", ctx.error, exc_info=ctx.error)
async def log_update(update, ctx):
    if update.message:
        logging.getLogger("bot").info("recv %s", update.message.text)
app.add_error_handler(err_handler)
app.add_handler(MessageHandler(filters.ALL, log_update), group=99)
```
