# Strategy & Backtest Notes — Crypto Signal Bot

## The RSI/EMA contradiction bug (the part that bit us)
Original (BROKEN) filter for a BUY:
```
RSI < oversold  AND  price > EMA_slow  AND  EMA_fast >= EMA_slow
```
When RSI is oversold the recent candle closed *down hard*, so price is **below**
EMA_slow and EMA_fast is **below** EMA_slow. The `price > EMA_slow` clause can never
be true at the same time → **0 signals, ever**. The bot "worked" (fetched data, no
errors) but never fired. Diagnosed by counting how many bars satisfied each clause
individually; only the combined clause was 0.

Corrected (dip-buy in uptrend):
- UPTREND := EMA_fast >= EMA_slow  (trend structure, ignores where price wiggles)
- BUY  := RSI < oversold  AND price < EMA_slow AND EMA_fast >= EMA_slow
- SELL := RSI > overbought AND price > EMA_slow AND EMA_fast <= EMA_slow

## Risk/Reward derivation
- Fixed `sl_pct` (e.g. 0.02). TP is derived: `tp = entry * (1 ± sl_pct * rr)`.
- Breakeven win-rate = `1 / (1 + rr)`.
  - rr=2.5 → need 28.6% WR
  - rr=3.0 → need 25.0% WR
- Implication: with RR≥3 you can be "wrong" 75% of the time and still net positive,
  so the engineering effort shifts to *filter quality* (fewer false signals), not hit-rate.

## Backtest methodology (real history, not fabricated)
1. `klines(sym, tf, N)` once per (pair, tf) — reuse the live fetch call.
2. Bar-by-bar: compute signal with the SAME `analyze()` logic.
3. For each signal, walk forward up to `max_hold` candles; first touch of TP or SL wins.
   If neither hit, resolve at `max_hold` by direction.
4. Metrics: win-rate, cumulative %, and compare WR to breakeven. Require ≥ ~20 trades.
5. Search a GRID of params (`itertools.product`) to find profitable configs; keep only
   those with WR ≥ breakeven AND net > 0 AND enough trades.

## Validated config (Binance, ~30d, 15m, RSI14/EMA20-100/SL2%/RR3)
| Pair   | Trades | WR   | Net (1%/trade) |
|--------|--------|------|----------------|
| SOL    | 29     | 83%  | +1.35%         |
| DOGE   | 27     | 63%  | +0.82%         |
| LTC    | 27     | 48%  | +0.50%         |
| BTC    | 27     | 37%  | +0.26% (neutral) |
| ETH    | 22     | 27%  | +0.04% (neutral) |
| ADA    | 23     | 22%  | −0.06% (negative) |

Lesson: the SAME strategy is great on SOL/DOGE and loses on ADA. Ship only validated
pairs; do not assume one filter fits all symbols. "DAT" is not a Binance symbol (HTTP 400).
