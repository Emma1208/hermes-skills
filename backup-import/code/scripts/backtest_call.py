#!/usr/bin/env python3
"""📊 BACKTEST CALL-ONLY — RSI≥80 + Prix>EMA20 | Contrats 5 min"""
import asyncio, json, websockets, time
from collections import deque
from _token import AK, WS

N_TRADES = 50

class Bougie:
    def __init__(self, ts, prix):
        self.ts, self.open, self.high, self.low, self.close = ts, prix, prix, prix, prix
    def update(self, prix):
        self.high, self.low = max(self.high,prix), min(self.low,prix); self.close = prix

class Analyse:
    def __init__(self):
        self.bougies = deque(maxlen=100)
    def add_candle(self, ts, o):
        b = Bougie(ts, o["open"]); b.high, b.low, b.close = o["high"], o["low"], o["close"]
        self.bougies.append(b)
    def rsi(self, period=7):
        if len(self.bougies) < period+1: return None
        c = [b.close for b in list(self.bougies)[-(period+1):]]
        g = sum(max(c[i]-c[i-1],0) for i in range(1,len(c)))
        l = sum(max(c[i-1]-c[i],0) for i in range(1,len(c)))
        return 100 if l==0 else 100-100/(1+g/l)
    def ema(self, period=20):
        if len(self.bougies) < period: return None
        c = [b.close for b in self.bougies]
        k = 2/(period+1); e = sum(c[-period:])/period
        for v in c[-period+1:]: e = v*k + e*(1-k)
        return e

async def fetch_candles():
    async with websockets.connect(WS, max_size=2**20) as ws:
        await ws.send(json.dumps({"authorize": AK}))
        await ws.recv()
        all_ticks, now = [], int(time.time())
        for b in range(180):  # 3h de données
            await ws.send(json.dumps({"ticks_history":"R_100","end":now-b*60,"count":5000,"style":"ticks","adjust_start_time":1}))
            while True:
                m = json.loads(await ws.recv())
                if m.get("msg_type")=="history":
                    h = m["history"]
                    for t,p in zip(h.get("times",[]),h.get("prices",[])): all_ticks.append((t,p))
                    break
                elif m.get("msg_type")=="error": break
            await asyncio.sleep(0.03)
        all_ticks.sort(key=lambda x:x[0])
        candles, cur = [], None
        for ts,prix in all_ticks:
            mn = ts//60
            if cur is None or cur.ts != mn:
                if cur: candles.append({"ts":cur.ts,"open":cur.open,"high":cur.high,"low":cur.low,"close":cur.close})
                cur = Bougie(mn, prix)
            else: cur.update(prix)
        if cur: candles.append({"ts":cur.ts,"open":cur.open,"high":cur.high,"low":cur.low,"close":cur.close})
        return candles

def backtest_call(candles):
    ana = Analyse()
    trades = wins = profit = 0
    last_ts = 0
    results = []
    for i, c in enumerate(candles):
        ana.add_candle(c["ts"], c)
        if len(ana.bougies) < 20: continue
        if c["ts"] - last_ts < 5: continue
        rsi = ana.rsi(7); ema20 = ana.ema(20)
        if rsi is None or ema20 is None: continue
        prix = c["close"]
        if not (rsi >= 80 and prix > ema20): continue
        # CALL: prix doit monter dans 5 min
        target_ts = c["ts"] + 5
        fp = None
        for j in range(i+1, len(candles)):
            if candles[j]["ts"] >= target_ts:
                fp = candles[j]["open"]; break
        if fp is None: continue
        won = fp > prix
        pf = 0.92 if won else -1.0
        trades += 1
        if won: wins += 1
        profit += pf
        last_ts = c["ts"]
        icon = "✅" if won else "❌"
        results.append({"t":trades,"i":icon,"p":pf,"r":rsi,"e":prix,"s":fp})
        print(f"  {icon} #{trades}: {pf:+.2f}$ | RSI={rsi:.0f} | E:{prix:.2f}→S:{fp:.2f}", flush=True)
        if trades >= N_TRADES: break
    return trades, wins, profit, results

async def main():
    print(f"""
╔═══════════════════════════════════════════════════╗
║  📊 BACKTEST CALL-ONLY — RSI≥80                  ║
║  CALL 5 min | {N_TRADES} trades | Payout 1.92     ║
╚═══════════════════════════════════════════════════╝""", flush=True)
    print("📡 Fetch 3h de ticks (180 batches)...", flush=True)
    candles = await fetch_candles()
    print(f"✅ {len(candles)} bougies\n", flush=True)
    trades, wins, profit, results = backtest_call(candles)
    wr = (wins/trades*100) if trades else 0
    ev = profit/trades if trades else 0
    print(f"\n{'='*55}")
    print(f"🏁 CALL-ONLY RSI≥80 | {trades} trades")
    print(f"{'='*55}")
    print(f"   WR: {wr:.1f}% ({wins}/{trades})")
    print(f"   P&L: {profit:+.2f}$")
    print(f"   EV/trade: {ev:+.4f}$")
    print(f"   {'✅ RENTABLE' if profit>0 else '❌ NON RENTABLE'}")
    print(f"{'='*55}")

asyncio.run(main())
