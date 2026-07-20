# Telegram + Mobile Money Recipes — Crypto Signal Bot

All calls use `urllib` (stdlib only). `requests` was unavailable on the host.

## Bot setup
1. Talk to @BotFather → /newbot → copy the token.
2. To send to a group the bot MUST be **added as a member AND promoted admin**
   (otherwise `sendMessage`/`getChat` return HTTP 400).
3. `deleteWebhook?drop_pending_updates=true` before using `getUpdates` polling
   (a webhook blocks long-polling).

## urllib helpers
```python
import json, urllib.request, urllib.parse
TOK = "...."
def api(method, params=None, timeout=15):
    url = f"https://api.telegram.org/bot{TOK}/{method}"
    data = urllib.parse.urlencode(params or {}).encode()
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

api("getMe")                                   # validate token
api("getChatMember", {"chat_id": CH, "user_id": BOT_ID})["result"]["status"]  # expect "administrator"
api("sendMessage", {"chat_id": CH, "text": msg})
```

## Capturing a chat_id
Run a listener ~40s; send any message in the target chat; read `update.message.chat.id`.
- Private DM → positive int (e.g. 8131589581)
- Supergroup → `-100NNNNNNNNNN`

## Polling loop (commands)
```
offset = 0
while True:
    upd = api("getUpdates", {"offset": offset, "timeout": 15})
    for u in upd["result"]:
        offset = u["update_id"] + 1
        msg = u.get("message")
        if msg and msg.get("text","").startswith("/"):
            handle(msg["from"]["id"], msg["text"], msg["from"].get("first_name",""))
```

## Mobile-Money-gated monetization (RDC)
State: `subscribers.json` = `{"subscribers": {}, "pending": {}}`.
- User command `/pay <txn_ref>` → `pending[uid] = {mm_reference, requested_at}` + alert admin.
- Admin command `/approve <uid>` → move to `subscribers[uid]` with `paid_until = today+30d`.
- `is_active(uid)` → True only if status active AND `paid_until` not past.
- On each signal: `for uid in list_active(): send(int(uid), signal)` (private DM, not the group).
Commands: user `/start` (menu+MM info), `/pay`, `/status`; admin `/approve`, `/deny`, `/list`, `/broadcast`.

### M-Pesa (DRC) specifics used
- Operator: M-Pesa. Number shown to users: `+243818491601` (use the operator's assigned
  business number, not a personal one if possible).
- Price: 24 000 FC / month; discovery offer 5 000 FC / 7 days.
- Approval is MANUAL (admin types `/approve`). Automate later via Flutterwave webhook if scale demands.

## Pitfall: token in chat
The bot token is a secret. It must be written into the script config to function, but
warn the user never to paste it publicly and to rotate via @BotFather if leaked.

## Pitfall: leaking secrets when PUSHING this bot to GitHub (real near-miss)
Never run `git init` / `git add -A` inside `/root` or `~`. A live session did exactly
that and staged **3206 files including `.git-credentials` (GitHub token),
`.hermes/auth.json`, `nous_auth.json`, and `MEMORY.md`** — only a push *timeout*
prevented the leak; the bad `.git` had to be `rm -rf`'d and the repo rebuilt scoped to
a subfolder. Rules: (1) copy only the project files into a clean subfolder
(e.g. `crypto-bot/`) and `git init` there; (2) commit a strict `.gitignore` first
(`.env`, `subscribers.json`, `__pycache__/`, `*.pyc`); (3) before commit run
`git ls-files | grep -E '\.env$|credentials|auth\.json|MEMORY'` — if anything matches,
`rm -rf .git` and restart; (4) commit `.env.example` (placeholders) never the real
`.env`; (5) prefer a PRIVATE repo. Load real secrets at runtime from a git-ignored `.env`.
