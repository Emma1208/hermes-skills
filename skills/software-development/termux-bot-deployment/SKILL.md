---
name: termux-bot-deployment
description: Run a long-lived Python Telegram/Discord bot (or the Hermes agent gateway itself) 24/7 on an Android phone via Termux (phone-as-server, no VPS). Covers the watchdog + termux-wake-lock pattern, the Hermes gateway self-watchdog, .env secret handling, the mobile one-command-at-a-time workflow, the Git secret-leak pitfall, and the Telegram getUpdates 404 fix.
---

# Termux Bot Deployment (phone as a server)

Use when the user wants to run a long-lived Python bot (Telegram signal bot, trading
bot, notifier, scraper) on their Android phone via Termux instead of paying for a VPS —
typically because they have no budget for a VPS.

## When this applies
- "use my phone as a server", "run the bot on Termux", "deploy on Android"
- Bot must stay alive 24/7, survive the app being closed, and not let the phone sleep
- User is typing commands on a mobile keyboard (high typo risk on long tokens / IDs)

## Prerequisites (tell the user up front)
- Install **Termux from F-Droid**, NOT Google Play (the Play build is stale/buggy).
- Optional: **Termux:Boot** for auto-start at device boot.

## Core pattern
1. **Dedicated folder.** Clone the project into its own dir (`~/mybot`). NEVER run git
   from `$HOME`/`/root`.
2. **Secrets in `.env`** (gitignored), loaded via `os.environ`. Never hardcode tokens in
   code that gets pushed.
3. **Watchdog** shell script relaunches the bot on crash + `termux-wake-lock` prevents sleep.
4. Launch: `termux-wake-lock && nohup bash watchdog.sh > bot.log 2>&1 &`.

See `templates/watchdog.sh`.

## Mobile workflow (CRITICAL — this is where sessions burn rounds)
Guide the user **ONE COMMAND AT A TIME**. After each command, wait for their "OK" or a
screenshot before sending the next. Mobile keyboards produce typos, especially on long
tokens and numeric IDs with similar digits (e.g. `8131589581` vs `81313589581`, or a
chat_id missing its final digit). Do NOT batch steps.

## Watchdog for the Hermes agent gateway itself
The same pattern works to keep **Hermes's own gateway** alive (it runs as a plain
`hermes gateway run` foreground process on Termux — no systemd). Use a watchdog that
`pgrep -f "hermes gateway"` and relaunches with `hermes gateway run --replace` (the
`--replace` flag clears any stale instance and avoids the "second dispatcher escapes
the service" refusal). See `templates/hermes-watchdog.sh`. For boot auto-start, use
`templates/termux-boot-hermes.sh` placed in `~/.termux/boot/` (Termux:Boot) — it
detaches with `setsid` so it lives OUTSIDE the gateway process tree and is never hit by
the gateway's self-protection (see pitfall below).

**Launching the watchdog:** use `terminal(background=true)` for the watchdog itself
(don't use `nohup ... & disown`/`setsid` from the agent's own shell — it's rejected).

**Testing the relaunch WITHOUT killing the live gateway:** you cannot `pkill -f "hermes
gateway"` or run `hermes gateway restart` from inside the gateway (the gateway blocks it
– SIGTERM would kill the command running in its own child). Instead, validate the
relaunch loop with an independent dummy process, kill THAT by PID, and confirm the
watchdog relaunches it. Detailed gotchas (BusyBox `exec -a` dummy failure, `pkill -f`
self-match, battery drain) are in `references/termux-watchdog-pitfalls.md`.

## Pitfalls

### 1. Git secret leak (HIGH RISK)
`git add -A` from `/root` or `$HOME` stages `.git-credentials`, `*.auth.json`,
`MEMORY.md` — everything. Even if `git push` times out, the secret is already in the
local commit and one retry will publish it.
- FIX: commit only from a dedicated project subfolder. Add a strict `.gitignore`
  (`.env`, `subscribers.json`, `__pycache__/`). After `git add -A` but BEFORE push, scan:
  `git ls-files | grep -E '\.env$|credentials|auth\.json|MEMORY'` → must be empty.
- If you already committed secrets: `rm -rf .git` in that folder (token never pushed),
  redo in a clean subfolder, and **rotate the leaked token** on the provider.

### 2. Truncated tokens handed to the user (wasted the most rounds in one session)
NEVER give the user a token as `883696...1` or `****`. A mobile user will type the
placeholder literally and you will loop for 20+ messages.
- FIX: read the EXACT token from the source file
  (`grep '^TELEGRAM_TOKEN=' .env | cut -d= -f2-`) and paste the FULL value.
- Prefer: have the user `nano .env`, paste the token there, then `cat .env` to verify
  byte-for-byte. If you must display it, split into short chunks to paste consecutively,
  and state exactly which characters are uppercase (positions), because `l` vs `I` vs `1`
  and `SLLi` vs `li` are easy to mistype.

### 3. Telegram getUpdates → HTTP 404
Two independent causes:
- (a) token has a stray newline/space → always `.strip()` it after reading from env.
- (b) sending `getUpdates` as a POST with `data=` fails on some Termux/Python setups →
  use **GET with a query string**: `f"{API}/getUpdates?offset={offset}&timeout=15"`.
Verify with: `python3 -c "import urllib.request;print(urllib.request.urlopen(f'{API}/getUpdates?offset=0&timeout=5').read())"`
→ should print JSON with `"ok":true`, not a 404.

### 4. Battery
`termux-wake-lock` stops the phone sleeping but drains the battery fast. Tell the user to
keep the phone on charge while the bot runs.

## Verification checklist
- `timeout 10 python3 run_bot.py` → expect `[bot] ecoute des commandes...` with NO
  `[poll err] 404` and scan lines printing.
- `cat .env` → 3 vars present, token is the FULL value (no `...`, no `****`).
- From another Telegram account, send `/start` to the bot → it must reply with the menu.

See `references/telegram-bot-pitfalls.md` for a full worked case study (crypto signal bot:
Binance RSI/EMA strategy, backtest, RR 3:1, Mobile Money M-Pesa monetization, the 404 fix).
