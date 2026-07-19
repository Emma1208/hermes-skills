# Strategy Pitfalls & Real Backtest Notes — Crypto Signal Bot

## 1. The contradictory trend filter (ZERO-signal bug)
**Symptom:** bot runs, fetches data fine, but `analyze()` never returns a signal.

**Cause:** combining RSI-oversold with "price above EMA50" in one AND:
- RSI < 35 ⇒ price just fell hard ⇒ price is BELOW EMA50, EMA20 BELOW EMA50.
- Requiring `price > EMA50` makes the condition impossible ⇒ 0 signals, forever.

**Fix (canonical):** define the trend by EMA *structure*, not by price-vs-EMA at the trigger candle:
```
BUY  = RSI oversold  AND price < EMA_slow AND EMA_fast >= EMA_slow
SELL = RSI overbought AND price > EMA_slow AND EMA_fast <= EMA_slow
```
After this fix, ~950 candles on BTC yielded 4 BUY + 1 SELL (rare but real, not noise).

**Rule:** the live bot and the backtest MUST call the same `signal_conditions()`. If they diverge, the backtest is meaningless.

## 2. Real backtest results (Binance, 15m, ~30d, HISTORY=3000)
| Pair   | Trades | Win rate |
|--------|--------|----------|
| BTC    | 3      | 33%      |
| ETH    | 9      | 22%      |
| SOL    | 8      | 75%      |

**Lesson:** the raw RSI(35/65)+EMA(20/50) filter is NOT viable as-is — it bleeds on BTC/ETH. Before monetizing you MUST:
- widen the test window (60–90d, multiple pairs),
- add a regime/volatility filter or multi-indicator confirmation (MACD cross),
- or optimize params (search RSI thresholds, TF, TP/SL) via a grid search.

## 3. Zero-dependency HTTP (urllib vs requests)
`pip install requests` can fail in minimal/PRoot/termux-like envs. Use stdlib:
```python
import urllib.request, urllib.parse
req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=15) as r:
    data = json.loads(r.read().decode())
```
Wrap calls in a 3× retry with 2s backoff — public APIs drop connections.

## 4. Tuning checklist before any paid launch
- Backtest ≥ 60 days, ≥ 3 pairs. Target WR > 55% with R:R ≥ 1.5.
- TP/SL: current 3%/1.5% (R:R=2). Tighten SL or widen TP if WR low.
- TF: 15m is noisy; test 1h/4h for fewer, higher-quality signals.
- Always keep the "Pas un conseil en investissement" disclaimer on every signal.
