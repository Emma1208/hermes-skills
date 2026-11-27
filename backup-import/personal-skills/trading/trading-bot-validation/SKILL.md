---
name: trading-bot-validation
description: Edge-first methodology for building and validating automated trading bots (Deriv, crypto, forex). Always backtest on REAL market data before automating. Deriv binary instruments are house games with EV <= 0 by construction. Honest EV reporting is mandatory for this user.
tags: [trading, backtest, crypto, forex, deriv, quant, automation, ev, edge]
triggers:
  - build or automate a trading bot
  - trading automatique or trading bot request
  - backtest a strategy or validate an edge
  - Deriv R_100 DIGITDIFF CALL_PUT binary options
  - propose a trading strategy that works
  - walk-forward drawdown or kill-switch setup
---

# Trading Bot Validation (edge-first)

Emmanuel (cap 10k$, 50$ virtual bot sandbox, 1% risk/trade, 5x max leverage, swing 3-10j, SL/BE/trail). Cardinal rule for THIS user: **never automate a strategy you have not proven has positive EV on real data** -- he will burn capital on house games otherwise.

## Core principle: edge-first
1. **Backtest BEFORE you build an executor.** A backtester that returns "NO EDGE" did its job -- it saved the coding hours AND the capital.
2. A negative backtest is a SUCCESSFUL filter, not a failure. Report it honestly, do not soften it.
3. Never trust a synthetic-only result. Test on REAL market data, across multiple regimes (bull AND bear). One bearish window proving negative is not conclusive; one bullish window near-zero is not an edge either.

## The Deriv trap (critical domain knowledge)
Deriv instruments are **house games**: payout is pre-computed so EV <= 0 by construction. Backtest evidence (20k synthetic ticks + real data, see references/backtest-evidence.md):
- **DIGITDIFF**: 89-95% WR but payout ~1.09 -> EV negative. High WR is the trap.
- **CALL/PUT martingale**: payout ~1.92; needs >52.1% net WR to break even; martingale risks ruin on 6-7 consecutive losses -> cap at 4 levels, reset after.
- **R_100 (Volatility 100)**: ~50% WR even-odds -> EV ~0, pure noise.
-> **Do NOT present Deriv binaries as edge.** If Emmanuel insists, sandbox at 50$ virtual and show him the EV math.

## FIRST REAL EDGE FOUND — gold (PAXG) range-breakout + MM200 (2026-07-12)
After rejecting Deriv (house), BTC 4h trend follower (0 edge), BTC 4h range-breakout
(intermittent, 2/4 OOS positive), and BTC weekly (positive but ~3% in 9y = too slow),
the **first genuinely tradable edge** surfaced on **gold**:
- **PAXGUSDT (tokenized gold), Daily, range-breakout Donchian PER10 + MM200 trend filter,
  ATR(14) SL 2x + trailing 3x, 1% risk/trade.** Result over ~1000 daily candles (2021→):
  **+17.3% (PF 2.25, DD 3.6%)** and ALL MM200 configs (PER10/20/50) positive (+14 to +17%,
  PF 2.25–2.82). XAUTUSDT had too few candles (109, 0 trades). EURUSDT daily = flat (PF 1.0).
- Why gold works where BTC didn't: gold has a structural multi-year uptrend (inflation /
  safe-haven) the MM200 filter rides. The MM200 filter HURT BTC but HELPED gold.
- Caveat for honesty: PAXG only ~1000 daily candles since 2021 → few trades (19–31). Confirm
  with more data before real capital. This is the candidate to paper-trade 2wk then 50$ real.

## 24/7 deployment pattern (deployed for Emmanuel this session)
To run a virtual/sim bot 24/7 on Termux+proot-Debian:
- `watchdog.sh` (run INSIDE `proot-distro login debian -- bash -c`): launches the bot,
  polls every 30s, RESTARTS if (a) process dies OR (b) output file mtime stale > 300s
  (heartbeat = bot prints a status line every loop). Caps at 20 restarts then exits
  (anti crash-loop). PROVEN: simulated crash -> log showed `exited, restart` -> `starting
  (restart 1)`.
- `start-bot-24-7.sh` (run from Termux, NOT inside Debian): `termux-wake-lock` + `nohup
  bash watchdog.sh`. Keeps phone awake with screen off.
- `stop-bot-24-7.sh`: `pkill` watchdog + bot + `termux-wake-unlock`.
- Bot MUST print a heartbeat line every poll loop or the watchdog kills it as "silent".

## Telegram signal alerts — chat_id GOTCHA (cost 1 debug round this session)
- Bot alerts via `https://api.telegram.org/bot<TOKEN>/sendMessage`. Token from @BotFather.
- **chat_id is NOT the user's chat with Hermes.** It is the chat id between the USER and the
  NEW bot. To get it: user must FIRST send a message to the new bot, THEN
  `GET https://api.telegram.org/bot<TOKEN>/getUpdates` → read `"chat":{"id":<number>}`.
  400 Bad Request = wrong chat_id (user pasted Hermes chat id). `getMe` validates the token.
- Use a SEPARATE bot token from @BotFather — NEVER the Hermes gateway token (hard rule).
- If Telegram unconfigured, bot must fail SILENT (still runs, just no alerts) — do not crash.

## Framework architecture (reusable)
Separate modules so strategy backtests independently of execution:
```
data/        feed (synthetic + CSV), candles (real Binance klines), collector (live WS)
strategy/    signal ONLY -- no money management mixed in (digit_diff, call_put, r100, trend_follower)
risk/        position sizing, capped martingale, kill-switches (daily loss%, consec SL)
backtest/    tick-level EV/WR/drawdown; candle-level ATR SL + trailing stop
```
Run order: backtest -> walk-forward (train != test window) -> paper trade 2wk (50$ virtual) -> 50$ real ONLY if EV>0 over 100+ trades.

## Trend follower template
`templates/trading_framework.py` -- standalone runnable: SMA(50)+MACD(12,26,9) entry, ATR(14) SL (1.5x) + trailing stop (2-3x), 1% risk/trade, Binance public klines (no account). **Naive version has NO edge on BTC 4h** (best PF 1.00 even on +43% rally -- see references). To get edge: add regime filter (trade only when price > SMA200 / bullish regime), test on Daily/Weekly, or other markets. Sweep SMA/SL/trail params before concluding.

## Real data source (no account needed)
Binance public klines: `https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=4h&limit=1000` (optional `&startTime=`/`&endTime=` ms). Returns OHLC arrays. No API key required.

## Reporting rule (this user)
Be brutally honest. If EV <= 0, print "NO EDGE, do not trade" -- do NOT invent or flatter an edge. Emmanuel values real validation over reassurance.

## Verification checklist
- Backtester runs on synthetic ticks AND real Binance candles with no import errors.
- Every strategy prints: WR, EV/trade, total return, max drawdown, profit factor, kill reason.
- Walk-forward uses a different window than training.
- Kill-switch (daily loss 3%, 3 consec SL) actually triggers in negative runs.
