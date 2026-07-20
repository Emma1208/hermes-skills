# Worked case study — Crypto Signal Bot EMK (Termux deployment)

## What was built
- Python bot (urllib only, zero external deps) scanning Binance public klines.
- Strategy: RSI(14) [30/60], EMA(20/100), SL 2%, **RR 3:1**, pairs SOL/DOGE/LTC.
- Backtest (real Binance data, ~30d, 15m): SOL 83% WR, DOGE 63%, LTC 48% (BTC/ETH
  rejected — WR below 25% breakeven). Seuil de rentabilité = 1/(1+rr) = 25%.
- Telegram `@Cryptobotemkbot` (admin in a supergroup), signals sent in DM only to
  active subscribers (Mobile Money M-Pesa RDC monetization: 24 000 FC/mois).
- Files: crypto_signal_bot.py (engine), payments.py (subscribers store), run_bot.py
  (master: poll commands + scan loop + gated DM broadcast), backtest.py, optimizer.py,
  get_chat_id.py.

## Deployment gotchas hit (and fixed)
1. `git add -A` run in /root staged 3206 files incl. `.git-credentials`,
   `.hermes/auth.json` → commit created locally, push timed out (so not leaked).
   FIX: `rm -rf /root/.git`, re-clone/push only from a dedicated `crypto-bot/` subfolder
   with `.gitignore` (`.env`, `subscribers.json`). Repo made public (no secrets in it).
2. Token given to user as `883696...1` → user typed the placeholder literally, looping
   for ~20 messages. FIX: read exact token from local `.env`, paste full value;
   user edited via `nano .env` and verified with `cat .env`.
3. `getUpdates` returned HTTP 404 even with a valid token. Two fixes:
   - token `.strip()` after env read (kills trailing newline/space)
   - use GET with query string instead of POST `data=`:
     `f"{API}/getUpdates?offset={offset}&timeout=15"`
   After fix: `[bot] ecoute des commandes...` with no 404.

## Verification that worked
```
timeout 10 python3 run_bot.py
# -> [bot] ecoute des commandes...
# -> [bot] boucle de scan demarree
# -> [scan] SOLUSDT: aucun signal   (normal, no trade that minute)
# NO [poll err] 404
```

## Monetization flow (Mobile Money)
1. Prospect pays M-Pesa to bot owner's number.
2. Prospect sends `/pay <txn_ref>` to bot.
3. Admin (user_id in ADMIN_IDS) receives alert, replies `/approve <user_id>`.
4. Subscriber now receives signals in DM for 30 days.
Commands: user `/start /pay /status`; admin `/approve /deny /list /broadcast`.
