#!/usr/bin/env python3
"""Backtest the signal strategy on REAL Binance history.
Reports win-rate (WR), avg win/loss, R/R, and simulated capital at 1% risk/trade.
Usage: python3 backtest.py
"""
import json, time, urllib.request, urllib.parse
import crypto_signal_bot as bot

SYMBOL = "SOLUSDT"
INTERVAL = "15m"
HISTORY = 3000            # ~30d of 15m candles (96/day)
MAX_HOLD = 96             # max candles before expiry (1 day)
RR = bot.CONFIG["rr"]
SL_PCT = bot.CONFIG["sl_pct"]

def fetch_history(symbol, interval, limit, retries=3):
    params = urllib.parse.urlencode({"symbol": symbol, "interval": interval, "limit": limit})
    url = f"{bot.BINANCE_KLINES}?{params}"
    last = None
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            last = e; time.sleep(2)
    raise last

def backtest(symbol, interval, history, max_hold):
    raw = fetch_history(symbol, interval, history)
    closes = [float(r[4]) for r in raw]; highs = [float(r[2]) for r in raw]; lows = [float(r[3]) for r in raw]
    rsi_v = bot.rsi(closes, bot.CONFIG["rsi_period"])
    ef = bot.ema(closes, bot.CONFIG["ema_fast"]); es = bot.ema(closes, bot.CONFIG["ema_slow"])
    trades = []
    start = max(bot.CONFIG["ema_slow"], bot.CONFIG["rsi_period"])
    for i in range(start, len(closes) - max_hold):
        price = closes[i]; rsi_n = rsi_v[i]; ema_f = ef[i]; ema_s = es[i]
        if rsi_n is None: continue
        signal = None
        if rsi_n < bot.CONFIG["rsi_oversold"] and price < ema_s and ema_f >= ema_s:
            signal = "BUY"
        elif rsi_n > bot.CONFIG["rsi_overbought"] and price > ema_s and ema_f <= ema_s:
            signal = "SELL"
        if not signal: continue
        if signal == "BUY":
            tp, sl = price * (1 + SL_PCT * RR), price * (1 - SL_PCT)
        else:
            tp, sl = price * (1 - SL_PCT * RR), price * (1 + SL_PCT)
        outcome = "EXPIRE"
        for j in range(i + 1, min(i + 1 + max_hold, len(closes))):
            if signal == "BUY":
                if highs[j] >= tp: outcome, ex = "TP", tp; break
                if lows[j] <= sl: outcome, ex = "SL", sl; break
            else:
                if lows[j] <= tp: outcome, ex = "TP", tp; break
                if highs[j] >= sl: outcome, ex = "SL", sl; break
        if outcome == "EXPIRE":
            ex = closes[min(i + max_hold, len(closes) - 1)]
            outcome = "TP" if (ex > price and signal == "BUY") or (ex < price and signal == "SELL") else "SL"
        pnl = (ex - price) / price * 100 * (1 if signal == "BUY" else -1)
        trades.append({"side": signal, "entry": price, "exit": ex, "outcome": outcome, "pnl_pct": pnl})
    return trades

def report(trades):
    if not trades:
        print("Aucun trade genere."); return
    n = len(trades)
    wins = [t for t in trades if t["outcome"] == "TP"]
    losses = [t for t in trades if t["outcome"] == "SL"]
    wr = len(wins) / n * 100
    total = sum(t["pnl_pct"] for t in trades)
    avg_win = sum(t["pnl_pct"] for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t["pnl_pct"] for t in losses) / len(losses) if losses else 0
    cap = 100.0
    for t in trades:
        cap *= (1 + (t["pnl_pct"] / 100) * 0.01 * 100)
    print("=" * 50)
    print(f"BACKTEST {SYMBOL} TF={INTERVAL} ({n} trades)")
    print("=" * 50)
    print(f"Taux reussite    : {wr:.1f}%  ({len(wins)} TP / {len(losses)} SL)")
    print(f"Gain cumule      : {total:+.2f}%")
    print(f"Gain moyen (TP)  : {avg_win:+.2f}%   Perte moy (SL) : {avg_loss:+.2f}%")
    print(f"Ratio G/P        : {(abs(avg_win/avg_loss)) if avg_loss else 0:.2f}")
    print(f"Capital simule 1%/trade : 100 -> {cap:.2f}")
    print("=" * 50)

if __name__ == "__main__":
    print(f"Recuperation historique {SYMBOL} ({HISTORY} bougies)...")
    t0 = time.time()
    tr = backtest(SYMBOL, INTERVAL, HISTORY, MAX_HOLD)
    print(f"Fait en {time.time()-t0:.1f}s\n")
    report(tr)
