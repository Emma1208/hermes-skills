#!/usr/bin/env python3
"""Grid-search parameter optimizer. Downloads history once per (pair,TF), tests a grid,
keeps only PROFITABLE configs (WR >= breakeven AND net>0) with >= MIN_TRADES samples.
Usage: python3 optimizer.py
"""
import json, time, urllib.request, urllib.parse, itertools
import crypto_signal_bot as bot

BINANCE_KLINES = bot.BINANCE_KLINES
HISTORY = 3000
MAX_HOLD_15 = 96
MAX_HOLD_1H = 24 * 7
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

def fetch_history(symbol, interval, limit, retries=3):
    params = urllib.parse.urlencode({"symbol": symbol, "interval": interval, "limit": limit})
    url = f"{BINANCE_KLINES}?{params}"
    last = None
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            last = e; time.sleep(2)
    raise last

def backtest_on(data, p):
    closes = [float(r[4]) for r in data]; highs = [float(r[2]) for r in data]; lows = [float(r[3]) for r in data]
    eff_hold = MAX_HOLD_15 if p["interval"] == "15m" else MAX_HOLD_1H
    rv = bot.rsi(closes, p["rsi_period"]); ef = bot.ema(closes, p["ema_fast"]); es = bot.ema(closes, p["ema_slow"])
    n = len(closes); start = max(p["ema_slow"], p["rsi_period"]); trades = []
    for i in range(start, n - eff_hold):
        pr = closes[i]; rn = rv[i]; af = ef[i]; aS = es[i]
        if rn is None: continue
        sig = None
        if rn < p["rsi_oversold"] and pr < aS and af >= aS: sig = "BUY"
        elif rn > p["rsi_overbought"] and pr > aS and af <= aS: sig = "SELL"
        if not sig: continue
        sl = pr * (1 + p["sl_pct"]) if sig == "SELL" else pr * (1 - p["sl_pct"])
        tp = pr * (1 - p["sl_pct"] * p["rr"]) if sig == "SELL" else pr * (1 + p["sl_pct"] * p["rr"])
        out = "EXP"
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
        trades.append(out if out in ("TP", "SL") else "SL")
    return trades

def main():
    print("Chargement historiques...")
    cache = {}
    for sym in SYMBOLS:
        for inter in INTERVALS:
            cache[(sym, inter)] = fetch_history(sym, inter, HISTORY)
            print(f"  {sym} {inter} OK")
    keys = list(GRID.keys()); combos = list(itertools.product(*[GRID[k] for k in keys]))
    print(f"\nCombinaisons : {len(combos)} x {len(SYMBOLS)} x {len(INTERVALS)}")
    results = []
    for sym in SYMBOLS:
        for inter in INTERVALS:
            data = cache[(sym, inter)]
            for combo in combos:
                p = dict(zip(keys, combo)); p["interval"] = inter
                trades = backtest_on(data, p)
                tot = len(trades)
                if tot < MIN_TRADES: continue
                wins = sum(1 for t in trades if t == "TP"); wr = wins / tot * 100
                be = 1 / (1 + p["rr"]) * 100
                cap = 100.0
                for t in trades:
                    cap *= (1 + p["sl_pct"] * p["rr"] * 0.01) if t == "TP" else (1 - p["sl_pct"] * 0.01)
                net = cap - 100
                if wr >= be and net > 0:
                    results.append({**{k: p[k] for k in keys}, "sym": sym, "inter": inter,
                                    "wr": round(wr, 1), "trades": tot, "net": round(net, 2)})
    results.sort(key=lambda r: r["net"], reverse=True)
    print(f"\nCONFIGS RENTABLES : {len(results)}")
    for r in results[:15]:
        print(f"{r['sym']:8} {r['inter']:4} WR{r['wr']:<6} {r['trades']:<4} net{r['net']:<7} | "
              f"RSI{r['rsi_period']} lo{r['rsi_oversold']} hi{r['rsi_overbought']} EMA{r['ema_fast']}/{r['ema_slow']} SL{r['sl_pct']} RR{r['rr']}")

if __name__ == "__main__":
    t0 = time.time(); main(); print(f"\nTemps : {time.time()-t0:.1f}s")
