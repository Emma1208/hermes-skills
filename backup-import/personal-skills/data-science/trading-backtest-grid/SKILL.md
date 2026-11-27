---
name: trading-backtest-grid
description: "Use when backtesting trading strategies with grid search optimization. Build a parameter optimizer that downloads historical data once, tests a grid of parameter combinations, filters for statistically valid profitable configs (WR >= breakeven, min trades), and outputs the best configuration."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [trading, backtest, grid-search, optimization, python, finance, rsi, ema]
    related_skills: [jupyter-live-kernel, evaluating-llms-harness]
---

# Trading Strategy Backtest with Grid Search Optimization

## Overview

Backtest a trading strategy (RSI + EMA crossover) with automated parameter optimization. The optimizer downloads historical data once per (symbol, timeframe), tests a grid of parameter combinations, and keeps only configs that are both statistically valid (≥ MIN_TRADES) and profitable (win rate ≥ breakeven, net PnL > 0). Designed for crypto markets using Binance public API (no API key required).

## When to Use

- **Backtesting**: When you need to validate a trading strategy against historical data.
- **Parameter optimization**: When you want to find the best RSI/EMA/SL/RR parameters automatically.
- **Strategy development**: When building or refining a trading bot and need to tune parameters.
- **Zero-dependency environments**: The core bot uses only Python stdlib (urllib, json, time) — no external packages needed for the signal engine.

## Architecture

```
crypto_signal_bot.py    # Core: data fetch, indicators, signal generation
optimizer.py            # Grid search backtest optimizer
backtest.py             # Historical backtest (optional)
get_chat_id.py          # Telegram chat_id capture utility
run_bot.py              # Master bot: subscribers, payments, signal broadcast
```

## Core Strategy: RSI + EMA Crossover

### Indicators
- **RSI(14)**: Overbought > 60, Oversold < 30 (configurable)
- **EMA(20/100)**: Fast EMA crosses slow EMA for trend confirmation
- **Risk/Reward**: 3:1 (TP = +3%, SL = -2%)

### Signal Logic
```python
# BUY signal: RSI < oversold AND price < EMA_slow AND EMA_fast >= EMA_slow
if rsi < rsi_oversold and price < ema_slow and ema_fast >= ema_slow:
    signal = "BUY"

# SELL signal: RSI > overbought AND price > EMA_slow AND EMA_fast <= EMA_slow
elif rsi > rsi_overbought and price > ema_slow and ema_fast <= ema_slow:
    signal = "SELL"
```

### Position Sizing
- **Stop Loss**: `entry_price * (1 - sl_pct)` for BUY, `entry_price * (1 + sl_pct)` for SELL
- **Take Profit**: `entry_price * (1 + sl_pct * rr)` for BUY, `entry_price * (1 - sl_pct * rr)` for SELL
- **Breakeven win rate**: `1 / (1 + rr) * 100` (e.g., RR=3 → 25% minimum WR)

## Data Fetching (Binance Public API)

```python
import json, time, urllib.request, urllib.parse

BINANCE_KLINES = "https://api.binance.com/api/v3/klines"

def fetch_history(symbol, interval, limit=3000, retries=3):
    """Fetch historical klines from Binance public API."""
    params = urllib.parse.urlencode({
        "symbol": symbol, "interval": interval, "limit": limit
    })
    url = f"{BINANCE_KLINES}?{params}"
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            time.sleep(2)
    raise e
```

## Indicators (From Scratch)

### RSI (Relative Strength Index)
```python
def rsi(closes, period=14):
    """Calculate RSI. Returns list with None for first `period` values."""
    if len(closes) < period + 1:
        return [None] * len(closes)
    
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    # Wilder's smoothing
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    result = [None] * period  # First `period` values are None
    
    for i in range(period, len(closes)):
        if i > period:
            avg_gain = (avg_gain * (period - 1) + gains[i-1]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i-1]) / period
        
        if avg_loss == 0:
            result.append(100.0)
        else:
            rs = avg_gain / avg_loss
            result.append(100 - (100 / (1 + rs)))
    
    return result
```

### EMA (Exponential Moving Average)
```python
def ema(closes, period):
    """Calculate EMA. Returns list with None for first `period-1` values."""
    if len(closes) < period:
        return [None] * len(closes)
    
    multiplier = 2 / (period + 1)
    result = [None] * (period - 1)
    
    # Seed with SMA
    sma = sum(closes[:period]) / period
    result.append(sma)
    
    for i in range(period, len(closes)):
        ema_val = (closes[i] - result[-1]) * multiplier + result[-1]
        result.append(ema_val)
    
    return result
```

## Grid Search Optimizer

### Key Design Decisions

1. **Download once**: Cache historical data per (symbol, interval) to avoid re-downloading.
2. **Statistical validity**: Require ≥ MIN_TRADES (default 20) for statistical significance.
3. **Profitability filter**: Keep only configs where WR ≥ breakeven AND net PnL > 0.
4. **Capital simulation**: Track simulated capital (start 100, risk 1% per trade).

### Python Implementation
```python
import itertools, time, json, urllib.request, urllib.parse

BINANCE_KLINES = "https://api.binance.com/api/v3/klines"
HISTORY = 3000
MAX_HOLD_15 = 96       # 1 day in 15m candles
MAX_HOLD_1H = 24 * 7   # 1 week in 1h candles
MIN_TRADES = 20

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
INTERVALS = ["15m", "1h"]

GRID = {
    "rsi_period": [14, 21],
    "rsi_oversold": [30, 35, 40],
    "rsi_overbought": [60, 65, 70],
    "ema_fast": [10, 20],
    "ema_slow": [50, 100],
    "sl_pct": [0.01, 0.015, 0.02],
    "rr": [2.0, 2.5, 3.0],
}

def backtest_on(data, params):
    """Backtest a single parameter combination on historical data."""
    closes = [float(r[4]) for r in data]
    highs = [float(r[2]) for r in data]
    lows = [float(r[3]) for r in data]
    eff_hold = MAX_HOLD_15 if params["interval"] == "15m" else MAX_HOLD_1H
    
    rv = rsi(closes, params["rsi_period"])
    ef = ema(closes, params["ema_fast"])
    es = ema(closes, params["ema_slow"])
    n = len(closes)
    start = max(params["ema_slow"], params["rsi_period"])
    trades = []
    
    for i in range(start, n - eff_hold):
        pr = closes[i]
        rn = rv[i]
        af = ef[i]
        aS = es[i]
        if rn is None:
            continue
        
        sig = None
        if rn < params["rsi_oversold"] and pr < aS and af >= aS:
            sig = "BUY"
        elif rn > params["rsi_overbought"] and pr > aS and af <= aS:
            sig = "SELL"
        
        if not sig:
            continue
        
        # Calculate SL/TP
        sl = pr * (1 + params["sl_pct"]) if sig == "SELL" else pr * (1 - params["sl_pct"])
        tp = pr * (1 - params["sl_pct"] * params["rr"]) if sig == "SELL" else pr * (1 + params["sl_pct"] * params["rr"])
        
        # Simulate trade exit
        out = "EXP"
        ex = None
        for j in range(i + 1, min(i + 1 + eff_hold, n)):
            if sig == "BUY":
                if highs[j] >= tp: out, ex = "TP", tp; break
                if lows[j] <= sl: out, ex = "SL", sl; break
            else:
                if lows[j] <= tp: out, ex = "TP", tp; break
                if highs[j] >= sl: out, ex = "SL", sl; break
        
        if out == "EXP":
            ex = closes[min(i + eff_hold, n - 1)]
            out = "TP" if (ex > pr and sig == "BUY") or (ex < pr and sig == "SELL") else "SL"
        
        trades.append(out)
    
    return trades

def main():
    print("Chargement historiques (une fois)...")
    cache = {}
    for sym in SYMBOLS:
        for inter in INTERVALS:
            cache[(sym, inter)] = fetch_history(sym, inter, HISTORY)
            print(f"  {sym} {inter} OK")
    
    keys = list(GRID.keys())
    combos = list(itertools.product(*[GRID[k] for k in keys]))
    print(f"\nCombinaisons testées : {len(combos)} x {len(SYMBOLS)} paires x {len(INTERVALS)} TF\n")
    
    results = []
    for sym in SYMBOLS:
        for inter in INTERVALS:
            data = cache[(sym, inter)]
            for combo in combos:
                p = dict(zip(keys, combo))
                p["interval"] = inter
                trades = backtest_on(data, p)
                tot = len(trades)
                if tot < MIN_TRADES:
                    continue
                
                wins = sum(1 for t in trades if t == "TP")
                wr = wins / tot * 100
                breakeven = 1 / (1 + p["rr"]) * 100
                
                # Simulate capital (1% risk per trade)
                cap = 100.0
                for t in trades:
                    if t == "TP":
                        cap *= (1 + p["sl_pct"] * p["rr"] * 0.01)
                    else:
                        cap *= (1 - p["sl_pct"] * 0.01)
                net = cap - 100
                
                if wr >= breakeven and net > 0:
                    results.append({
                        "sym": sym, "inter": inter, "wr": round(wr, 1),
                        "trades": tot, "net": round(net, 2),
                        "params": p
                    })
    
    results.sort(key=lambda r: r["net"], reverse=True)
    print("=" * 80)
    print(f"CONFIGS RENTABLES (WR >= breakeven ET net > 0) : {len(results)}")
    print("=" * 80)
    
    for r in results[:15]:
        p = r["params"]
        print(f"{r['sym']:8} {r['inter']:4} WR:{r['wr']}% Tr:{r['trades']} Net:{r['net']}% | "
              f"RSI{p['rsi_period']} lo{p['rsi_oversold']} hi{p['rsi_overbought']} "
              f"EMA{p['ema_fast']}/{p['ema_slow']} SL{p['sl_pct']} RR{p['rr']}")
    
    if results:
        best = results[0]
        p = best["params"]
        print(f"\n>>> MEILLEURE CONFIG :")
        print(f"    'symbols': ['{best['sym']}']")
        print(f"    'interval': '{best['inter']}'")
        print(f"    'rsi_period': {p['rsi_period']}, 'rsi_oversold': {p['rsi_oversold']}, 'rsi_overbought': {p['rsi_overbought']}")
        print(f"    'ema_fast': {p['ema_fast']}, 'ema_slow': {p['ema_slow']}, 'sl_pct': {p['sl_pct']}, 'rr': {p['rr']}")

if __name__ == "__main__":
    t0 = time.time()
    main()
    print(f"\nTemps total : {time.time()-t0:.1f}s")
```

## Telegram Bot Integration

### Chat ID Capture
```python
import json, time, urllib.request, urllib.parse

def get_chat_id(token, timeout=40):
    """Capture chat_id by listening for messages (bot must be admin in group)."""
    url = f"https://api.telegram.org/bot{token}/"
    
    # Remove webhook
    try:
        urllib.request.urlopen(f"{url}deleteWebhook?drop_pending_updates=True")
    except: pass
    
    found = set()
    deadline = time.time() + timeout
    offset = 0
    
    while time.time() < deadline:
        try:
            params = urllib.parse.urlencode({"offset": offset, "timeout": 10})
            with urllib.request.urlopen(f"{url}getUpdates?{params}", timeout=12) as r:
                upd = json.loads(r.read().decode())
            
            for u in upd.get("result", []):
                offset = u["update_id"] + 1
                msg = u.get("message") or u.get("channel_post")
                if msg:
                    cid = msg.get("chat", {}).get("id")
                    if cid and cid not in found:
                        found.add(cid)
                        print(f"  -> chat_id TROUVE: {cid}")
        except Exception as e:
            print(f"  (attente) {e}")
        time.sleep(1)
    
    return found
```

### Signal Broadcasting
```python
def send_telegram_signal(token, chat_id, signal_data):
    """Send a trading signal to Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    msg = f"""
📊 *Crypto Signal*
Pair: {signal_data['symbol']}
Signal: {signal_data['signal']}
Price: {signal_data['price']}
TP: {signal_data['tp']} ({signal_data['rr']}:1 RR)
SL: {signal_data['sl']}
"""
    data = urllib.parse.urlencode({
        "chat_id": chat_id, "text": msg, "parse_mode": "Markdown"
    }).encode()
    req = urllib.request.Request(url, data=data)
    urllib.request.urlopen(req)
```

## Mobile Money Monetization (RDC)

### Subscription Model
- Users pay via Mobile Money (M-Pesa RDC)
- Payment verified by reference number
- Admin approves subscriptions via Telegram command
- Active subscribers receive signals in DM

### Commands
- `/start` — Menu + subscription info
- `/pay <reference>` — Request subscription after payment
- `/status` — Check subscription status
- Admin: `/approve <user_id>`, `/deny <user_id>`, `/broadcast <msg>`

## Common Pitfalls

1. **Look-ahead bias**: Never use future data in backtest. Ensure indicators are calculated only from data available at that point in time.
2. **Survivorship bias**: Use historical data that includes delisted pairs. Binance klines API returns current pairs only.
3. **Overfitting**: Grid search can find spurious profitable configs. Always validate on out-of-sample data.
4. **Transaction costs**: This backtest ignores fees. Real trading has 0.1% fee per trade on Binance.
5. **Slippage**: Market orders may not fill at exact TP/SL prices, especially in volatile markets.
6. **RSI divergence**: RSI can stay overbought/oversold for extended periods in strong trends.
7. **EMA lag**: EMAs lag price, so signals may come late in fast-moving markets.

## Verification

1. **Run backtest**: `python3 optimizer.py` — should complete in < 5 minutes for 3 pairs × 2 timeframes × ~2000 combos.
2. **Check statistical validity**: Ensure MIN_TRADES ≥ 20 for each result.
3. **Validate on out-of-sample**: Test best config on a different time period.
4. **Forward test**: Run the bot in dry-run mode (`python3 crypto_signal_bot.py`) for at least 1 week.
5. **Compare with buy-and-hold**: Ensure the strategy outperforms simply holding the asset.

## Related skills

`jupyter-live-kernel` (interactive Python analysis), `evaluating-llms-harness` (grid search optimization patterns), `hermes-agent` (agent spawning for parallel backtests).
