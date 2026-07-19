#!/usr/bin/env python3
"""Backtest harness for the crypto signal bot.

Replays signal_conditions() on REAL Binance history and measures:
  - number of trades, win rate (TP hit before SL)
  - cumulative PnL (%) and simulated capital

Run: python3 backtest.py
Edit SYMBOL / INTERVAL / HISTORY at the top to widen the test window.
"""
import time, json, urllib.request, urllib.parse
import crypto_signal_bot as bot

SYMBOL = "BTCUSDT"
INTERVAL = "15m"
HISTORY = 3000          # ~30 days of 15m candles (96/day)
MAX_HOLD = 96           # max candles a trade stays open (~1 day) before expiry


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
            last = e
            time.sleep(2)
    raise last


def backtest(symbol, interval, history, max_hold):
    raw = fetch_history(symbol, interval, history)
    closes = [float(r[4]) for r in raw]
    highs = [float(r[2]) for r in raw]
    lows = [float(r[3]) for r in raw]
    rv = bot.rsi(closes, bot.CONFIG["rsi_period"])
    ef = bot.ema(closes, bot.CONFIG["ema_fast"])
    es = bot.ema(closes, bot.CONFIG["ema_slow"])

    trades = []
    start = bot.CONFIG["ema_slow"]
    for i in range(start, len(closes) - max_hold):
        price = closes[i]
        rn = rv[i]
        af = ef[i]
        aS = es[i]
        side = bot.signal_conditions(price, rn, af, aS)
        if not side:
            continue
        entry = price
        if side == "BUY":
            tp, sl = entry * (1 + bot.CONFIG["tp_pct"]), entry * (1 - bot.CONFIG["sl_pct"])
        else:
            tp, sl = entry * (1 - bot.CONFIG["tp_pct"]), entry * (1 + bot.CONFIG["sl_pct"])

        outcome = "EXPIRE"
        exit_price = None
        for j in range(i + 1, min(i + 1 + max_hold, len(closes))):
            h, l = highs[j], lows[j]
            if side == "BUY":
                if h >= tp:
                    outcome, exit_price = "TP", tp; break
                if l <= sl:
                    outcome, exit_price = "SL", sl; break
            else:
                if l <= tp:
                    outcome, exit_price = "TP", tp; break
                if h >= sl:
                    outcome, exit_price = "SL", sl; break
        if outcome == "EXPIRE":
            exit_price = closes[min(i + max_hold, len(closes) - 1)]
            outcome = "TP" if (exit_price > entry and side == "BUY") or (exit_price < entry and side == "SELL") else "SL"

        pnl = (exit_price - entry) / entry * 100 * (1 if side == "BUY" else -1)
        trades.append({"side": side, "entry": entry, "exit": exit_price,
                       "outcome": outcome, "pnl_pct": pnl})
    return trades


def report(trades):
    if not trades:
        print("Aucun trade genere sur la periode.")
        return
    n = len(trades)
    wins = [t for t in trades if t["outcome"] == "TP"]
    losses = [t for t in trades if t["outcome"] == "SL"]
    wr = len(wins) / n * 100
    total = sum(t["pnl_pct"] for t in trades)
    aw = sum(t["pnl_pct"] for t in wins) / len(wins) if wins else 0
    al = sum(t["pnl_pct"] for t in losses) / len(losses) if losses else 0
    print("=" * 50)
    print(f"BACKTEST  {SYMBOL}  TF={INTERVAL}  ({n} trades)")
    print("=" * 50)
    print(f"Win rate            : {wr:.1f}%  ({len(wins)} TP / {len(losses)} SL)")
    print(f"PnL cumule (somme) : {total:+.2f}%")
    print(f"Gain moyen (TP)     : {aw:+.2f}%")
    print(f"Perte moyenne (SL)  : {al:+.2f}%")
    print(f"Ratio gain/perte   : {(abs(aw / al)) if al else 0:.2f}")
    cap = 100.0
    for t in trades:
        cap *= (1 + t["pnl_pct"] / 100)
    print(f"Capital simule     : 100 -> {cap:.2f}")
    print("=" * 50)
    print("\nDerniers trades :")
    for t in trades[-10:]:
        print(f"  {t['side']:4} entree {t['entry']:.0f} -> {t['outcome']:2} {t['pnl_pct']:+.2f}%")


if __name__ == "__main__":
    print(f"Recuperation de l'historique {SYMBOL} ({HISTORY} bougies {INTERVAL})...")
    t0 = time.time()
    tr = backtest(SYMBOL, INTERVAL, HISTORY, MAX_HOLD)
    print(f"Fait en {time.time() - t0:.1f}s\n")
    report(tr)
