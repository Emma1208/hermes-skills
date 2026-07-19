#!/usr/bin/env python3
"""
optimizer.py - Grid-search parameter optimizer for crypto_signal_bot
====================================================================
Telecharge l'historique une fois par (paire, timeframe), teste un GRID de
parametres et ne garde que les configs rentables (WR >= breakeven) avec un
echantillon statistiquement valide (>= MIN_TRADES).

Usage : python3 optimizer.py
Depend de : crypto_signal_bot.py (rsi, ema, BINANCE_KLINES, CONFIG)
"""
import json
import time
import urllib.request
import urllib.parse
import itertools

import crypto_signal_bot as bot

BINANCE_KLINES = bot.BINANCE_KLINES
HISTORY = 3000
MAX_HOLD_15 = 96
MAX_HOLD_1H = 24 * 7
MIN_TRADES = 20

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT", "LTCUSDT"]
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
            last = e
            time.sleep(2)
    raise last


def backtest_on(data, p):
    closes = [float(r[4]) for r in data]
    highs = [float(r[2]) for r in data]
    lows = [float(r[3]) for r in data]
    eff_hold = MAX_HOLD_15 if p["interval"] == "15m" else MAX_HOLD_1H
    rv = bot.rsi(closes, p["rsi_period"])
    ef = bot.ema(closes, p["ema_fast"])
    es = bot.ema(closes, p["ema_slow"])
    n = len(closes)
    start = max(p["ema_slow"], p["rsi_period"])
    trades = []
    for i in range(start, n - eff_hold):
        pr = closes[i]; rn = rv[i]; af = ef[i]; aS = es[i]
        if rn is None:
            continue
        sig = None
        if rn < p["rsi_oversold"] and pr < aS and af >= aS:
            sig = "BUY"
        elif rn > p["rsi_overbought"] and pr > aS and af <= aS:
            sig = "SELL"
        if not sig:
            continue
        sl = pr * (1 + p["sl_pct"]) if sig == "SELL" else pr * (1 - p["sl_pct"])
        tp = pr * (1 - p["sl_pct"] * p["rr"]) if sig == "SELL" else pr * (1 + p["sl_pct"] * p["rr"])
        out = "EXP"; ex = None
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
    print("Chargement historiques (une fois)...")
    cache = {}
    for sym in SYMBOLS:
        for inter in INTERVALS:
            cache[(sym, inter)] = fetch_history(sym, inter, HISTORY)
            print(f"  {sym} {inter} OK")
    print()

    keys = list(GRID.keys())
    combos = list(itertools.product(*[GRID[k] for k in keys]))
    print(f"Combinaisons testees : {len(combos)} x {len(SYMBOLS)} paires x {len(INTERVALS)} TF\n")

    results = []
    for sym in SYMBOLS:
        for inter in INTERVALS:
            data = cache[(sym, inter)]
            for combo in combos:
                p = dict(zip(keys, combo)); p["interval"] = inter
                trades = backtest_on(data, p)
                tot = len(trades)
                if tot < MIN_TRADES:
                    continue
                wins = sum(1 for t in trades if t == "TP")
                wr = wins / tot * 100
                breakeven = 1 / (1 + p["rr"]) * 100
                cap = 100.0
                for t in trades:
                    cap *= (1 + p["sl_pct"] * p["rr"] * 0.01) if t == "TP" else (1 - p["sl_pct"] * 0.01)
                net = cap - 100
                if wr >= breakeven and net > 0:
                    results.append({"sym": sym, "inter": inter, "wr": round(wr, 1), "trades": tot,
                                    "net": round(net, 2), "rsi_p": p["rsi_period"], "rsi_lo": p["rsi_oversold"],
                                    "rsi_hi": p["rsi_overbought"], "ef": p["ema_fast"], "es": p["ema_slow"],
                                    "sl": p["sl_pct"], "rr": p["rr"]})

    results.sort(key=lambda r: r["net"], reverse=True)
    print("=" * 80)
    print(f"CONFIGS RENTABLES (WR >= breakeven ET net > 0) : {len(results)}")
    print("=" * 80)
    if not results:
        print("Aucune config rentable. Elargir la grille ou assouplir MIN_TRADES.")
        return
    print(f"{'Sym':8} {'TF':4} {'WR%':6} {'Tr':4} {'Net%':7} | params")
    for r in results[:15]:
        print(f"{r['sym']:8} {r['inter']:4} {r['wr']:<6} {r['trades']:<4} {r['net']:<7} | "
              f"RSI{r['rsi_p']} lo{r['rsi_lo']} hi{r['rsi_hi']} EMA{r['ef']}/{r['es']} SL{r['sl']} RR{r['rr']}")
    best = results[0]
    print("\n>>> MEILLEURE CONFIG (copier dans crypto_signal_bot.py CONFIG) :")
    print(f"    'symbols': ['{best['sym']}'],")
    print(f"    'interval': '{best['inter']}',")
    print(f"    'rsi_period': {best['rsi_p']}, 'rsi_oversold': {best['rsi_lo']}, 'rsi_overbought': {best['rsi_hi']},")
    print(f"    'ema_fast': {best['ef']}, 'ema_slow': {best['es']}, 'sl_pct': {best['sl']}, 'rr': {best['rr']}")


if __name__ == "__main__":
    t0 = time.time()
    main()
    print(f"\nTemps total : {time.time()-t0:.1f}s")
