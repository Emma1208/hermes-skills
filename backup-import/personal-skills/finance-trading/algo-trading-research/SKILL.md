---
name: algo-trading-research
description: How to research, backtest, and validate automated trading strategies for Emmanuel — edge-first on REAL market data, Deriv excluded, modular Python framework, with the empirical findings from the 2026-07 session.
triggers:
  - Emmanuel asks for a trading strategy, bot, or an idea that works
  - building or backtesting an auto-trading bot (Deriv, BTC, gold, forex)
  - validating whether a strategy has an edge before risking money
  - the "fait ce qui est idéal" directive applied to trading
---

# Algo Trading Research (edge-first)

Emmanuel is an active trader/automatizer (capital 10k$, 50$ virtual for crypto bot,
1% risk/trade, 5x max leverage, swing 3-10 days, strict SL/BE/trailing). The ONLY
correct way to serve him here is to **prove an edge on real data before any code
touches real money**. He disengages from theory — he wants a working, tested thing.

## Core principle: EDGE-FIRST, never trust a backtest photo
1. Write the strategy as a PURE signal module (no money management mixed in).
2. Backtest on REAL candles (Binance public klines — no account needed, see references/framework_recipe.md).
3. Report the **ONE-LINE verdict first** ("gagne / perd / edge confirmé"),
   then the table as backup. Never lead with a table.
4. Walk-forward: re-test on periods the code NEVER saw. If positive in-sample but
   negative OOS, the edge is fake. Require PF > 1.2 on OOS to consider real money.
5. Only THEN build a virtual (simulated) bot, run it live for weeks, then 50$ real.

## What markets have an edge (empirical, 2026-07 session)
See references/empirical_findings.md for full numbers. Summary:
- **Deriv (R_100, DIGITDIFF, CALL/PUT): NO EDGE POSSIBLE** — it is a house game,
  payouts are pre-set so EV ≤ 0 by construction. Do not waste time. If he insists on
  Deriv, treat it as entertainment with fixed 0.5% stake, no martingale, stop after 3 SL.
- **Gold / PAXG (Binance tokenized gold) daily + MM200 trend filter + PER10 breakout:
  STRONGEST EDGE FOUND** — +17.3%, PF 2.25, DD < 4%, all filter configs positive.
  This is the recommended candidate.
- **BTC 4h breakout: unstable** — +8% in-sample but negative OOS (2022 bear -5.3%).
  Not reliable enough for real money.
- **BTC weekly breakout: positive but too slow** (+3.8% over 9y, ~6 trades).
- **EURUSD daily breakout: flat** (PF ~1.0). No edge.
- **Naive trend follower (SMA50+MACD) BTC 4h: ~0** even in a +43% bull — too simple.

## Modular framework (reusable skeleton)
Split into 4 independent modules so strategy can be backtested alone and risk changed
without touching the signal:
- `data/feed.py` — synthetic ticks + CSV loader (real ticks)
- `data/candles.py` — Binance public klines fetch (symbol/interval/limit + startMs/endMs)
- `strategy/base.py` — Strategy base; signal() returns {action, payout} or None
- `strategy/range_breakout.py` — Donchian breakout WITH optional MM200 filter
- `risk/manager.py` — capped martingale (max 4 levels) + kill-switch (daily loss 3%, 3 consec SL)
- `backtest/engine.py` — tick-level EV/WR/drawdown simulator
- `backtest/candle_engine.py` — candle-level with ATR SL (1.5-2x) + trailing stop (2-3x ATR)
- `execution/virtual_bot.py` — SIMULATED live bot (no real money), prints equity/DD/wins

Keep strategy signal-only; money management lives in risk/. This separation is what
let us swap strategies and re-test in minutes.

## Support files in this skill
- `references/termux-watchdog.md` — proven 24/7 watchdog + launcher scripts (Termux+Debian).
- `scripts/watchdog_template.sh` — reusable generic watchdog (edit BOT_CMD, then nohup it).
- `references/empirical_findings.md` — full backtest numbers per market.
- `references/framework_recipe.md` — how to scaffold the 4-module framework.

## Delivering to Emmanuel (collaboration)
- Lead with the verdict, not the table. Offer the next step as lettered choices (A/B/C/D),
  let him reply with one word.
- When he says "propose moi une idée qui fonctionne", give ONE concrete actionable
  strategy (e.g. "cassure de range sur l'or, filtre MM200, daily"), not a lecture.
- He validates by running it on his phone + sending a screenshot. Diagnose FROM the
  image, fix, re-deliver. Never claim success without real run output.
- Build + actually RUN the backtest/code in-session and paste REAL output before
  telling him it works.

## 24/7 deployment (watchdog + launcher) — for the virtual/live bot
Once the edge is validated, run the bot continuously on his phone:
1. The bot MUST print a **heartbeat line every loop** (price/equity/DD/wins), even when
   FLAT. The watchdog detects a hung bot by heartbeat staleness, not by process life.
   (Bug we hit: VirtualBot.run() only printed on a non-None return -> silent when FLAT ->
   watchdog could not tell alive from dead. Fix: print state every loop unconditionally.)
2. `watchdog.sh` (runs INSIDE the bot's env via `proot-distro login debian -- bash -c "$BOT_CMD"`):
   - restarts if the process dies (exit code)
   - restarts if `bot.out` mtime is older than STALE sec (default 300) -> kills + relaunches
   - crash-loop cap (MAX_RESTARTS, default 20) so it stops instead of looping forever
3. `start-bot-24-7.sh` (run from Termux, NOT Debian): `termux-wake-lock` + `nohup bash watchdog.sh &`
4. `stop-bot-24-7.sh`: `pkill -f watchdog.sh`, pkill the bot, `termux-wake-unlock`
See references/termux-watchdog.md for the proven scripts; scripts/watchdog_template.sh is a
reusable generic version (set BOT_CMD). Test the watchdog with a mock bot that crashes after
3 heartbeats — confirm `exited, restart` appears in the log, then a fresh `starting`.

## Pitfalls (learned the hard way)
- A backtest that is positive is NOT proof — always walk-forward on unseen data.
- Binance spot has NO forex pairs. For "gold/euro" use PAXGUSDT (gold) / EURUSDT (euro);
  XAUUSDT is NOT listed (HTTP 400). XAUTUSDT exists but has too few candles (0 trades).
- fetch() without a User-Agent header can be blocked; send `User-Agent: Mozilla/5.0`.
- RangeBreakout.signal() with use_filter=False must treat `long_ok/short_ok = True`,
  NOT `trend = price` (that made price>trend always false -> 0 trades, silent bug).
- Virtual bot MUST emit a heartbeat every loop (see 24/7 section) or the watchdog is blind.
- Test the watchdog logic with a crashing mock bot BEFORE trusting it on the real bot.
