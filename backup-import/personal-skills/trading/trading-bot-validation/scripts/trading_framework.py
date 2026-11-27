#!/usr/bin/env python3
"""Self-contained trading-bot validation scaffold (edge-first).
Run: python3 trading_framework.py
Fetches REAL Binance BTC 4h candles (no account) and backtests a trend follower
with ATR SL + trailing stop across parameter combos. Prints honest EV/WR/PF.
"""
import json, urllib.request


def fetch(symbol="BTCUSDT", interval="4h", limit=1000, start_ms=None, end_ms=None):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    if start_ms: url += f"&startTime={int(start_ms)}"
    if end_ms: url += f"&endTime={int(end_ms)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = json.load(r)
    return [{"open": float(k[1]), "high": float(k[2]), "low": float(k[3]), "close": float(k[4])} for k in raw]


def sma(v, p):
    return None if len(v) < p else sum(v[-p:]) / p


def macd_hist(closes, i, st):
    if st.get("e12") is None:
        st["e12"] = st["e26"] = st["sig"] = closes[i]
    else:
        k12, k26, k9 = 2/13, 2/27, 2/10
        st["e12"] = closes[i]*k12 + st["e12"]*(1-k12)
        st["e26"] = closes[i]*k26 + st["e26"]*(1-k26)
        macd = st["e12"] - st["e26"]
        st["sig"] = macd*k9 + st["sig"]*(1-k9)
    return (st["e12"] - st["e26"]) - st["sig"]


def atr(h, l, c, i, p=14):
    if i < p: return None
    trs = [max(h[j]-l[j], abs(h[j]-c[j-1]), abs(l[j]-c[j-1])) for j in range(i-p+1, i+1)]
    return sum(trs) / p


def backtest(candles, sma_p=50, sl_m=1.5, tr_m=2.0, equity=1000.0, risk=0.01):
    h = [c["high"] for c in candles]; l = [c["low"] for c in candles]; c = [c["close"] for c in candles]
    n = len(c); trades = wins = 0; gw = gl = 0.0; eq = equity; peak = equity; mdd = 0.0; pos = None; st = {}
    def book(pnl):
        nonlocal trades, wins, gl, gw
        trades += 1
        if pnl >= 0: wins += 1; gw += pnl
        else: gl += -pnl
    for i in range(n):
        if pos:
            a = atr(h, l, c, i) or pos["atr"]; flip = signal(c, i, sma_p, st)
            ex = None
            if pos["side"] == "LONG":
                pos["trail"] = max(pos["trail"], h[i]-tr_m*a)
                if l[i] <= pos["trail"]: ex = pos["trail"]
                elif flip and flip == "SHORT": ex = c[i]
            else:
                pos["trail"] = min(pos["trail"], l[i]+tr_m*a)
                if h[i] >= pos["trail"]: ex = pos["trail"]
                elif flip and flip == "LONG": ex = c[i]
            if ex:
                pnl = pos["units"]*(ex-pos["entry"]) if pos["side"]=="LONG" else pos["units"]*(pos["entry"]-ex)
                eq += pnl; book(pnl); pos = None
        eq_curve = eq; peak = max(peak, eq); mdd = max(mdd, (peak-eq)/peak)
        if not pos:
            sig = signal(c, i, sma_p, st); a = atr(h, l, c, i)
            if sig and a:
                e = c[i]; sl = e-a*sl_m if sig=="LONG" else e+a*sl_m
                rpu = abs(e-sl)
                if rpu <= 0: continue
                pos = {"side": sig, "entry": e, "trail": sl, "units": equity*risk/rpu, "atr": a}
    ret = (eq-1000.0)/1000.0*100
    return dict(trades=trades, wr=wins/trades if trades else 0, ret=ret, mdd=mdd*100, pf=gw/gl if gl else float("inf"))


def signal(closes, i, sma_p, st):
    if i < sma_p: return None
    m = sma(closes[:i+1], sma_p)
    hh = macd_hist(closes, i, st)
    if closes[i] > m and hh > 0: return "LONG"
    if closes[i] < m and hh < 0: return "SHORT"
    return None


def main():
    cd = fetch("BTCUSDT", "4h", 1000)
    print(f"BTC {cd[0]['close']:.0f} -> {cd[-1]['close']:.0f} "
          f"({'UP' if cd[-1]['close']>cd[0]['close'] else 'DOWN'})\n")
    rows = []
    for sp in (30, 50, 100):
        for sl in (1.5, 2.0):
            for tr in (2.0, 3.0):
                r = backtest(cd, sp, sl, tr)
                rows.append((sp, sl, tr, r))
    rows.sort(key=lambda x: x[3]["ret"], reverse=True)
    print(f"{'SMA':>4} {'SL':>4} {'TR':>4} {'trades':>6} {'WR%':>5} {'ret%':>8} {'DD%':>6} {'PF':>5}")
    for sp, sl, tr, r in rows:
        print(f"{sp:>4} {sl:>4} {tr:>4} {r['trades']:>6} {r['wr']*100:>5.1f} "
              f"{r['ret']:>+8.1f} {r['mdd']:>6.1f} {r['pf']:>5.2f}")


if __name__ == "__main__":
    main()
