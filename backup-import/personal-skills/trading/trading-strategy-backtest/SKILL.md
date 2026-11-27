---
name: trading-strategy-backtest
description: Build and validate automated trading strategies with edge-first discipline — modular backtest framework, real-market data via public APIs, and honest walk-forward/OOS verification. For crypto/forex strategy research, NOT Deriv house games.
triggers:
  - user asks for a trading bot, trading strategy, or "idée de trading"
  - backtest / walk-forward / EV / profit factor / drawdown mentions
  - Deriv, R_100, DIGITDIFF, CALL/PUT, crypto auto-trading, automated trading
  - "propose moi une idée de trading qui fonctionne"
---

# Trading Strategy Backtest (edge-first)

Emmanuel is a trader who wants AUTOMATED trading. Cardinal rule: **never code an
executor before the edge is proven by backtest on real data.** A positive backtest
is a hypothesis; walk-forward on unseen data is the test.

## Methodology
1. Separate concerns into 4 modules:
   - `data/` (synthetic feed + real collector)
   - `strategy/` (signal ONLY, no money management)
   - `risk/` (sizing + kill-switch)
   - `backtest/` (engine)
2. **Backtest on REAL market data**, never only synthetic. Binance public klines need
   NO account:
   `https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=4h&limit=1000`
   Supports `startTime`/`endTime` (unix ms) for walk-forward windows.
3. Candle engine simulates REAL PnL: ATR(14) stop-loss (1.5–2×), trailing stop
   (2–3× ATR), risk 1% equity/trade, size = equity*risk / risk_per_unit.
4. **Walk-forward / out-of-sample (OOS) test is MANDATORY.** A good in-sample result
   is just a photo. Split history; the code must NEVER see the test window while tuning.

## Key findings from BTC research (2021–2024)
- **Deriv house games have EV ≤ 0 BY CONSTRUCTION.** The house sets the payout so you
  cannot win long-term. Proven: DIGITDIFF 89% WR but payout 1.09 → negative EV;
  CALL/PUT martingale → ruin risk; R_100 50% WR → pure noise. Do NOT automate Deriv.
  Tell the user plainly — do not pretend an edge exists.
- **Naive trend-following (SMA50 + MACD) on BTC 4h:** ~0 edge (PF ~1.0 even in a +43% bull).
- **XAUUSD spot via Yahoo Finance (2026-07-17):** raw symbols `XAUUSD` and
  `XAUUSD=X` return 404 on Yahoo. Use the COMEX futures proxy **`GC=F`** (USD/oz,
  tracks spot ~1:1). `yfinance` returns MultiIndex columns → call `.squeeze()` on
  the Close. Ready long/short engine + 5y multi-window findings in
  `references/xauusd_yahoo_backtest.md`.
- **GOLD IS THE FIRST REAL EDGE (2026-07-12).** On PAXGUSDT (tokenized gold) Daily,
  range-breakout Donchian PER10 + MM200 trend filter, ATR(14) SL 2× + trail 3×, 1% risk:
  **+17.3% (PF 2.25, DD 3.6%)** and ALL MM200 configs positive (+14–17%, PF 2.25–2.82).
  XAUTUSDT had too few candles (109); EURUSDT daily flat (PF 1.0). The MM200 filter HURT
  BTC but HELPED gold — gold's structural uptrend is what makes the filter work. Caveat:
  PAXG only ~1000 daily candles → few trades (19–31); confirm with more data before real $.

## 24/7 deployment (deployed this session, Termux + proot-Debian)
Backtest → walk-forward → THEN paper-trade live. For 24/7 paper bot: `watchdog.sh` (inside
`proot-distro login debian -- bash -c`) polls 30s, restarts on death OR stale output
(>300s = "silent", bot must print heartbeat each loop), caps 20 restarts. `start-bot-24-7.sh`
(from Termux, NOT Debian) does `termux-wake-lock` + `nohup bash watchdog.sh`. `stop-bot-24-7.sh`
pkills + `termux-wake-unlock`. Telegram alerts: SEPARATE @BotFather token (never Hermes
token); chat_id = user's chat WITH THE NEW BOT (send msg first, then getUpdates) — NOT the
Hermes chat id (400 Bad Request if wrong).
- Lesson: a strategy that looks great on one window usually disappoints OOS. Require
  PF > 1.3 on MULTIPLE OOS windows before recommending live capital.

## Architecture / reusable patterns
- Strategy class exposes `signal(series, i) -> {'action':..., 'payout':...}` or None.
  No position sizing inside the strategy.
- Risk manager: capped martingale (max 4 levels: ×1→×2→×4→×8→RESET; never keep doubling
  → ruin protection) + kill-switch (stop if daily loss > 3% or 3 consecutive SL).
- Binance fetch wrapper: `urllib.request` + `User-Agent` header (avoids 403), parse
  klines `[o,h,l,c,...]`.

## Pitfalls
- **XAUUSD / spot-forex data gotcha:** Yahoo 404s on `XAUUSD` / `XAUUSD=X`; use
  `GC=F` (gold futures proxy). See `references/xauusd_yahoo_backtest.md`.
- **pandas 3.0 removed `DataFrame.last("6mo")`** → AttributeError. Slice by date:
  `sub = df.loc[df.index[-1] - pd.DateOffset(months=6):]`.
- **Single-window backtest is a trap.** A strategy that wins on one regime (e.g.
  MACD shorting a 6mo bear XAUUSD window, -1.6% vs -16.6% B&H) can be the WORST
  over full history (MACD lost all 5 windows over 5y because gold's secular uptrend
  punishes persistent shorting). ALWAYS run MULTI-WINDOW (6mo/1y/2y/3y/5y, different
  start dates) before naming a "best" strategy. The robust XAUUSD winner was
  SMA10/30 trend-follow WITH extreme-RSI cut (long if RSI>70 cut, short if RSI<30
  cut): +14.4% avg, best Sharpe, 4/5 windows positive.
- **Python `nonlocal` helper functions must be NESTED inside the function that uses
  them**, not module-level — else `SyntaxError: no binding for nonlocal 'x'`. Define
  `book(pnl)` INSIDE `run()`.
- Keep entry/exit logic and the final `return` dict in the correct scope; a misplaced
  `return` inside the entry block terminates the loop early (silent logic break).
- Synthetic ticks are for framework self-test only; never validate an edge on them.

## Verification
`python3 run_breakout_backtest.py` then `python3 run_walkforward.py` — BOTH must show
POSITIVE on ≥ multiple OOS windows before recommending live.
