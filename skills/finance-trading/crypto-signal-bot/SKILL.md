---
name: crypto-signal-bot
description: Build, backtest, and optimize an automated crypto trading-signal bot (Telegram delivery) in pure Python stdlib — no requests/pandas. Use when the user wants to build a trading signal service, backtest a crypto strategy, or tune RSI/EMA parameters against real Binance data.
---

# Crypto Signal Bot (pure-stdlib)

Build an automated crypto signal generator + backtester + parameter optimizer using
ONLY the Python standard library (`urllib`, `json`, no `requests`/`pandas`). This avoids
the broken-Pillow / missing-`requests` problems common on Termux/musl and keeps the bot
deployable on any VPS with stock Python 3.

## When to use
- User asks to build a trading signal bot, crypto alerts service, or "business automatique" around signals.
- User wants to backtest a strategy or optimize RSI/EMA/TP-SL parameters on real data.
- User is an ex-Forex analyst / wants a subscription signal product (see Monetization below).

## Hard constraints & environment notes
- **No third-party deps.** Binance market data is PUBLIC — no API key needed. Use
  `urllib.request` + `urllib.parse`, NOT `requests` (often missing on Termux/musl).
- This user expects **all replies and generated document/content in French**. Code/comments
  may stay English, but user-facing messages, signal text, and reports must be French.
- Add a **retry loop** around every `urlopen` — Binance public endpoints drop connections
  intermittently (saw `read operation timed out`); 3 retries with 2s sleep fixes it.

## Workflow (proven sequence from a real build)
1. **Prototype the bot** — fetch klines, compute RSI(Wilder)+EMA, detect signal, format, send.
   Start in `dry_run` (console) mode; verify live before wiring Telegram.
2. **Backtest on REAL history** — replay strategy on `klines` and simulate TP/SL hit candle-by-candle.
   Report: #trades, win rate (WR), cumulative %, breakeven WR, best/worst trade.
3. **Optimize** — grid-search parameters; keep only configs with WR ≥ breakeven AND ≥20 trades
   (small samples are not statistically valid).
4. **Pick winning pairs** — test multiple symbols; a strategy that wins on SOL may lose on BTC.
   Launch on validated pairs only.
5. **Monetize (separate step)** — Telegram delivery + subscription + Mobile Money gating.
   See `references/telegram_mobilemoney.md` for the urllib recipes (getMe, sendMessage,
   getChatMember, getUpdates polling, deleteWebhook) and the **Mobile-Money-gated** flow
   that shipped in this project: prospect pays M-Pesa → `/pay <txn_ref>` → admin
   `/approve <user_id>` → signals delivered to that user's private DM only (gated by
   `subscribers.json`). Manual approval is fine to start; automate with Flutterwave later.

## ⚠️ PUSHING TO GITHUB — DO NOT LEAK SECRETS (real near-miss this project)
When saving the bot to GitHub, a `git add -A` run inside `/root` staged **3206 files
including `.git-credentials` (GitHub token), `.hermes/auth.json`, `nous_auth.json`, and
`MEMORY.md`**. Only a push *timeout* prevented the leak; the bad `.git` had to be
`rm -rf`'d and the repo rebuilt. Hard rules:
- **Never `git init` / `git add -A` in `/root` or `~`.** Copy only the project files into
  a clean subfolder (e.g. `/root/crypto-bot/`) and `git init` there.
- **Commit a strict `.gitignore` first**: `.env`, `subscribers.json`, `__pycache__/`, `*.pyc`.
- **Before commit, verify**: `git ls-files | grep -E '\\.env$|credentials|auth\\.json|MEMORY'`.
  If anything matches → `rm -rf .git` and restart scoped. (In this project a `git add -A`
  in `/root` actually staged `.git-credentials` + Hermes auth; only a push timeout
  saved us. The fix was `rm -rf /root/.git` and a clean `/root/crypto-bot/` re-init.)
- **Never commit a real `.env`.** Commit `.env.example` (placeholders only); load real
  secrets at runtime from a git-ignored local `.env`. Prefer a PRIVATE repo.

## ⚠️ NEVER HAND THE USER AN ABBREVIATED SECRET (real mistake this project)
When the user needs a Telegram token / chat_id / admin_id to paste into their
`.env`, give the **FULL** value. An abbreviated form like `883696...1` will be
typed verbatim by the user and **will not work** — this cost ~10 wasted turns in
the real session and the user explicitly said "c'est toi qui commet tout ces
erreurs." Instead: read the full secret from the real source file (e.g. `/root/.env`)
and paste it whole, or have the user open `nano .env` and paste it themselves.
Do NOT ask them to retype a long value character-by-character on a phone keyboard.

## Deploying on Android (Termux) — free 24/7 server
When the user has no VPS budget, run the bot on their phone via Termux. Watchdog +
`termux-wake-lock` recipe, battery warning, `nano` for secrets, and the fact that
the agent CANNOT SSH into the phone (private LAN IP) are all in
`references/termux_deploy.md`. Key takeaways: install Termux from F-Droid (not
Play Store); use a watchdog+nohup so it survives app close; plug the phone in
(wake-lock drains battery); and have the user TYPE commands themselves — you
cannot reach the phone over SSH.

## ⚠️ CRITICAL STRATEGY PITFALL (easy to get backwards)
The naive "buy when RSI oversold AND price above EMA_slow" is **self-contradictory**:
when RSI is oversold, price is *below* EMA_slow. The original build had this bug → 0 signals,
a real wasted cycle. Correct logic = **buy the dip inside an uptrend**:
- BUY:  `rsi < rsi_oversold` AND `price < ema_slow` AND `ema_fast >= ema_slow`
- SELL: `rsi > rsi_overbought` AND `price > ema_slow` AND `ema_fast <= ema_slow`
Trend is judged by EMA structure (`ema_fast >= ema_slow`), NOT by `price > ema_slow`.

## Risk/Reward math
- Derive TP from SL: `tp = entry * (1 ± sl_pct * rr)` (BUY +, SELL −). Do NOT use a fixed tp_pct.
- **Breakeven win rate = `1 / (1 + rr)`**. With rr=3.0 you only need **25% WR** to be profitable.
- This means leverage is on *signal quality* (filter noise), not on hitting 50% WR.

## Backtest core loop (TP/SL hit simulation)
```
for each candle i where indicators valid:
    if signal: entry, sl, tp computed
    for j in i+1 .. i+MAX_HOLD:
        if BUY and highs[j] >= tp: outcome=TP; break
        if BUY and lows[j]  <= sl: outcome=SL; break
        (mirror for SELL)
    if none hit within MAX_HOLD: mark EXPIRE -> compare final close vs entry
```
`MAX_HOLD` ~ 96 candles for 15m (1 day), ~168 for 1h (1 week).

## Compliance (do not skip)
- Always include "⚠️ Pas un conseil en investissement. DYOR." in signal text.
- Never promise a guaranteed return — legally risky and reputationally fatal.

## Files in this skill
- `templates/crypto_signal_bot.py` — full working bot (dry_run + Telegram), validated live on Binance. Copy and edit CONFIG.
- `scripts/optimizer.py` — grid-search optimizer; prints only rentable configs (WR≥breakeven, ≥20 trades). Run: `python3 optimizer.py`.
- Backtest module: reconstruct from the "Backtest core loop" above (or copy from a prior session); it is small.
- `references/strategy_backtest_notes.md` — domain notes: the RSI/EMA contradiction bug, RR derivation, backtest recipe, and the VALIDATED config from this build (SOL 83% / DOGE 63% / LTC 48% WR on ~30d 15m; BTC/ETH neutral; ADA negative).
- `references/telegram_mobilemoney.md` — urllib Telegram recipes (validate token, send, capture chat_id, poll commands) + the M-Pesa (DRC) gated-subscription flow.
- `references/termux_deploy.md` — run the bot 24/7 on the user's Android via Termux: watchdog + wake-lock, battery warning, `nano .env` for long secrets, WHY the agent cannot SSH into the phone, and clone/typo/overwrite pitfalls.
