---
name: auto-trading-signals
description: Build, validate, and deploy an automated crypto/Forex trading-signal service (the user's recurring business). Covers live-data bot, RSI/EMA strategy with correct pullback logic, backtesting, parameter optimization, Telegram delivery, and the monetization path. Use whenever the user wants to build/improve a signal bot, trading service, or "business automatique" in trading.
---

# Auto Trading Signals (crypto/Forex)

Build a **working, live-validated** trading-signal bot, then backtest + optimize before
monetizing. The user (ex-Forex analyst, Kinshasa) runs this as a business: sell signals
by subscription. Validate with REAL exchange data before claiming anything works.

## Pipeline (in order)
1. **Fetch** live/historical candles (Binance public REST, no API key needed).
2. **Indicators** RSI + EMA fast/slow + trend filter (pure Python, no pandas).
3. **Signal logic** — see CRITICAL pitfall below (the contradiction bug).
4. **Deliver** to Telegram (BotFather bot → channel/group).
5. **Backtest** on real history; require ≥20 trades for statistical validity.
6. **Optimize** a parameter grid; keep only configs with WR ≥ breakeven AND net > 0.
7. **Monetize** (subscription + Mobile Money/Flutterwave) — see references/telegram-integration.md.

## Constraints / environment
- **No `requests` library** on this box (pip install fails). Use `urllib.request` +
  `urllib.parse` (stdlib) with a `User-Agent` header and a retry loop. See scripts/.
- Binance public endpoints: `https://api.binance.com/api/v3/klines`
  (params: symbol, interval, limit). No auth required for market data.

## CRITICAL — RSI/EMA pullback logic (the bug that silently kills the bot)
When RSI is **oversold**, price has JUST dropped → price is **BELOW** the slow EMA, and
fast EMA is **BELOW** slow EMA. A naive filter `price > EMA_slow AND RSI < oversold`
yields **ZERO possible signals** (verified: 0 trades on BTC over 950 candles).

Correct "buy the dip in an uptrend" logic:
```
uptrend   = ema_fast >= ema_slow          # structure, not price vs EMA
BUY  if rsi < rsi_oversold AND price < ema_slow AND ema_fast >= ema_slow
SELL if rsi > rsi_overbought AND price > ema_slow AND ema_fast <= ema_slow
```
This produces rare-but-real signals (≈1/day on SOL 15m).

## Risk/Reward derivation
- `SL` is the fixed stop; `TP = SL × RR` (not two independent values).
- Breakeven win-rate = `1 / (1 + RR)`. With RR=3 you only need **≥25% WR** to be profitable.
- Validated config (backtested ~30d, 15m, real data):
  RSI period 14, oversold 30, overbought 60, EMA 20/100, SL 2%, RR 3.0.

## Validated pair performance (real data, ~30d, 15m, config above)
| Pair  | Trades | WR   | Verdict |
|-------|--------|------|---------|
| SOL   | 29     | 83%  | ★★★ launch pair |
| DOGE  | 27     | 63%  | ★★ solid |
| LTC   | 27     | 48%  | positive but weak |
| BTC   | 27     | 37%  | neutral |
| ETH   | 22     | 27%  | neutral |
| DOT   | 16     | 31%  | neutral |
| ADA   | 23     | 22%  | NEGATIVE |
- **Recommendation:** run bot on `["SOLUSDT","DOGEUSDT","LTCUSDT"]` only. Exclude BTC/ETH/ADA.
- Symbol typos → Binance returns HTTP 400. "DAT" does not exist; user likely meant DOT/ADA.

## Telegram delivery (see references/telegram-integration.md)
- Validate token: `GET https://api.telegram.org/bot<TOKEN>/getMe`.
- `deleteWebhook` before using `getUpdates` (they conflict).
- Capture target `chat_id` by listening to `getUpdates` after the user posts in the group
  where the bot is **admin**. Group IDs look like `-100...`; a DM is type `private`.

## Compliance (RDC / generic)
- Always include "⚠️ Pas un conseil en investissement. DYOR." in signals.
- Never promise a guaranteed gain. Backtest proof builds credibility, not promises.

## Support files
- `scripts/crypto_signal_bot.py` — full working bot (urllib, RSI/EMA, Telegram, RR3).
- `scripts/backtest.py` — historical backtest, reports WR + simulated capital.
- `scripts/optimizer.py` — grid search over params, keeps profitable configs.
- `scripts/get_chat_id.py` — listener that captures the Telegram chat_id.
- `references/strategy-and-backtest-notes.md` — math, gotchas, dataset notes.
- `references/telegram-integration.md` — BotFather + paiement RDC setup.
