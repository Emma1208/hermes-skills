# Strategy & Backtest Notes — Crypto Signal Bot

## Math recap
- EMA(k): `out[i] = out[i-1] + (2/(k+1)) * (price - out[i-1])`. Seed = SMA of first k.
- RSI (Wilder): avg_gain/avg_loss smoothed; `RSI = 100 - 100/(1+RS)`. Guard avg_loss==0 -> RS=100.
- Breakeven WR = `1/(1+RR)`. RR=2.5 -> 28%; RR=3.0 -> 25%. So you need FAR less than 50% WR to profit.
- Simulated capital: per trade at `risk%` of capital:
  `cap *= (1 + sl_pct*rr*risk)` on TP, `cap *= (1 - sl_pct*risk)` on SL.

## The contradiction bug (CRITICAL)
Naive spec: "buy when RSI oversold AND price above EMA_slow AND uptrend".
Reality when RSI is oversold: a sharp drop just happened, so price is BELOW EMA_slow
and fast EMA is BELOW slow EMA. Condition `price > EMA_slow` is therefore NEVER true
together with RSI<oversold. Result: 0 signals (observed on BTC, 950 candles).
Fix = trade the PULLBACK in the trend using EMA structure, NOT price-vs-EMA:
  BUY  if RSI<oversold AND price<EMA_slow AND EMA_fast>=EMA_slow
  SELL if RSI>overbought AND price>EMA_slow AND EMA_fast<=EMA_slow
This yields ~1 signal/day on SOL 15m — rare but real, which is the point (no noise).

## Dataset facts (Binance public klines)
- URL `https://api.binance.com/api/v3/klines?symbol=SOLUSDT&interval=15m&limit=3000`
- Row layout: [open_time, open, high, low, close, volume, ...]. Index 4 = close.
- No API key. Symbol typos -> HTTP 400. Check symbol exists before looping.
- 15m -> 96 candles/day. 3000 candles ~= 31 days. 1h -> 24 candles/day.

## Why backtest before selling
Without the backtest the user would have shipped a strategy losing on BTC/ETH and only
winning on SOL. Backtest on >=20 trades per pair; report WR vs breakeven, not just WR.
Net simulated capital (1% risk/trade) is the honest profitability metric.

## Validated config (do not re-derive blindly each session)
RSI period=14, oversold=30, overbought=60, EMA fast=20/slow=100, SL=2%, RR=3.0, TF=15m.
Launch pairs: SOLUSDT, DOGEUSDT, LTCUSDT. Exclude BTC/ETH/ADA/DOT (weak/negative).
