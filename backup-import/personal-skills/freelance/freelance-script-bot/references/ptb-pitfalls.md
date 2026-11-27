# Python-Telegram-Bot (PTB) 22.x — Pitfalls & Fixes (Emmanuel's bots)

## 1. Timeout kwargs go on the BUILDER, not run_polling()
`run_polling()` in PTB 22.x does NOT accept `read_timeout`/`connect_timeout`/`pool_timeout`.
Passing them raises: `TypeError: Application.run_polling() got an unexpected keyword argument 'read_timeout'`.

WRONG:
```python
app = Application.builder().token(TOKEN).build()
app.run_polling(allowed_updates=Update.ALL_TYPES, read_timeout=30)
```

RIGHT (set on the builder):
```python
app = (
    Application.builder()
    .token(TOKEN)
    .connect_timeout(30)
    .read_timeout(30)
    .pool_timeout(30)
    .build()
)
app.run_polling(allowed_updates=Update.ALL_TYPES)
```
Use this on slow networks (e.g. sandboxed envs where getUpdates takes >5s) to avoid
`telegram.error.TimedOut`.

## 2. Token guard — never run a client bot with the Hermes-exclusive token
Tokens starting with `820389` belong to Hermes' Telegram gateway. Launching a client bot with it
causes HTTP 409 and kills the Hermes gateway. Add a startup guard:
```python
if not TOKEN or TOKEN.startswith("820389"):
    raise SystemExit("⛔ TOKEN = Hermes-exclusive (820389...). Use a @BotFather token.")
```
Also: a single token may be polled by ONLY ONE process — `pgrep -af python` before relaunch.

## 3. Chat-not-found when testing
You cannot `sendMessage` to a chat_id that never started the bot → `400 Bad Request: chat not found`.
The bot must receive a `/start` from the user first. To validate end-to-end, ask the user to open the
bot and send `/start`, then drive it from the real chat (or use `getUpdates` to confirm polling alive).

## 4. Always run in a DEDICATED venv, never inside ~/.hermes/hermes-agent/venv
```bash
python3 -m venv /path/to/bot/venv
/path/to/bot/venv/bin/pip install python-telegram-bot==22.6 python-dotenv
/path/to/bot/venv/bin/python bot.py
```
Accidentally inheriting the Hermes venv mixes the bot process with the agent — avoid.

## 5. Reliable deps (Termux / sandboxed)
- `python-telegram-bot==22.6` (22.8 also fine on Termux Py3.14; 21.x crashes).
- `python-dotenv` for `.env` token loading.
- Avoid `parsel`/`lxml` without `libxml2`/`libxslt-dev`.
