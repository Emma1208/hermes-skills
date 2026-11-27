# Reusable trading-research framework recipe (Binance public data, no account)

## 1. Fetch real candles (no API key)
```python
import json, urllib.request
def fetch(symbol="PAXGUSDT", interval="1d", limit=1000, start_ms=None, end_ms=None):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    if start_ms is not None: url += f"&startTime={int(start_ms)}"
    if end_ms is not None: url += f"&endTime={int(end_ms)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = json.load(r)
    return [{"open":float(k[1]),"high":float(k[2]),"low":float(k[3]),"close":float(k[4])} for k in raw]
```

## 2. Range-breakout signal (Donchian + optional MM200 filter)
```python
def _sma(v, p):
    return sum(v[-p:])/p if len(v) >= p else None

class RangeBreakout:
    def __init__(self, params=None):
        self.params = params or {}
        self.n = self.params.get("period", 10)
        self.trend_p = self.params.get("trend_period", 200)
        self.use_filter = self.params.get("use_filter", True)
    def signal(self, closes, i):
        if i < max(self.n, self.trend_p): return None
        wh = max(closes[i-self.n:i]); wl = min(closes[i-self.n:i]); price = closes[i]
        if self.use_filter:
            t = _sma(closes[:i+1], self.trend_p)
            if t is None: return None
            long_ok, short_ok = price > t, price < t
        else:
            long_ok = short_ok = True
        if price > wh and long_ok: return {"action":"LONG","payout":1.0}
        if price < wl and short_ok: return {"action":"SHORT","payout":1.0}
        return None
```

## 3. Backtest with ATR SL + trailing stop (candle-level, key bits)
- entry: units = (equity * 0.01) / risk_per_unit, risk_per_unit = sl_mult*ATR
- LONG SL = entry - 1.5*ATR; trail starts at SL, ratchets up to high - 2*ATR
- exit LONG when low <= trail, or signal flips to SHORT
- mirror for SHORT
- track equity curve, max drawdown = (peak-equity)/peak, profit factor = gross_win/gross_loss

## 4. Workflow
1. strategy signal-only 2. backtest in-sample 3. walk-forward OOS (unseen dates)
4. PF>1.2 OOS -> virtual bot (execution/virtual_bot.py) 5. run weeks -> 50$ real

## Notes
- Binance spot has no forex. Gold = PAXGUSDT (XAUUSDT 400, XAUTUSDT too few candles).
- Always send User-Agent or request may be blocked.
