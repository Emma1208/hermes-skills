#!/usr/bin/env python3
"""📊 BACKTEST 5 MINUTES — sur données historiques (ticks_history)
Évite le problème de connexion persistante
"""
import asyncio, json, websockets, time
from collections import deque
from _token import AK, WS

N_TRADES = 30
CANDLE_COUNT = 120  # Bougies 1 min (2h de données)

class Bougie:
    def __init__(self, ts, prix):
        self.ts = ts
        self.open = self.high = self.low = self.close = prix
    def update(self, prix):
        self.high = max(self.high, prix)
        self.low = min(self.low, prix)
        self.close = prix

class Analyse:
    def __init__(self):
        self.bougies = deque(maxlen=100)
    
    def add_candle(self, ts, ohlc):
        b = Bougie(ts, ohlc["open"])
        b.high = ohlc["high"]
        b.low = ohlc["low"]
        b.close = ohlc["close"]
        self.bougies.append(b)
    
    def rsi(self, period=7):
        if len(self.bougies) < period + 1: return None
        closes = [b.close for b in list(self.bougies)[-(period+1):]]
        gains = losses = 0
        for i in range(1, len(closes)):
            d = closes[i] - closes[i-1]
            if d > 0: gains += d
            else: losses += abs(d)
        if losses == 0: return 100
        return 100 - 100 / (1 + gains/losses)
    
    def ema(self, period=20):
        if len(self.bougies) < period: return None
        closes = [b.close for b in self.bougies]
        k = 2 / (period + 1)
        ema_val = sum(closes[-period:]) / period
        for i in range(-period, 0):
            ema_val = closes[i] * k + ema_val * (1 - k)
        return ema_val
    
    def macd(self):
        """MACD (12, 26, 9)"""
        if len(self.bougies) < 35: return None, None
        closes = [b.close for b in self.bougies]
        
        def calc_ema(data, period):
            k = 2 / (period + 1)
            ema = sum(data[-period:]) / period
            for val in data[-period+1:]:
                ema = val * k + ema * (1 - k)
            return ema
        
        ema12 = calc_ema(closes, 12)
        ema26 = calc_ema(closes, 26)
        macd_line = ema12 - ema26
        
        # Signal line (EMA 9 of past MACD values)
        macd_values = []
        for i in range(len(closes) - 26, len(closes)):
            if i < 12: continue
            window = closes[:i+1]
            e12 = calc_ema(window, 12)
            e26 = calc_ema(window, 26)
            macd_values.append(e12 - e26)
        
        if len(macd_values) < 9: return macd_line, None
        signal = calc_ema(macd_values, 9)
        return macd_line, signal

async def fetch_candles():
    """Récupère les ticks et construit des bougies 1 min"""
    async with websockets.connect(WS, ping_interval=15, max_size=2**20) as ws:
        await ws.send(json.dumps({"authorize": AK}))
        auth = json.loads(await ws.recv())
        print(f"✅ Auth: ${auth.get('authorize',{}).get('balance','?')}", flush=True)
        
        now = int(time.time())
        # Demander les ticks des 2 dernières heures par lots de 1 min
        all_ticks = []
        for batch_min in range(60):  # 60 minutes de données
            end = now - batch_min * 60
            await ws.send(json.dumps({
                "ticks_history": "R_100",
                "end": end,
                "count": 5000,
                "style": "ticks",
                "adjust_start_time": 1
            }))
            
            while True:
                m = json.loads(await ws.recv())
                if m.get("msg_type") == "history":
                    history = m.get("history", {})
                    times = history.get("times", [])
                    prices = history.get("prices", [])
                    for i, (t, p) in enumerate(zip(times, prices)):
                        all_ticks.append((t, p))
                    break
                elif m.get("msg_type") == "error":
                    print(f"  ⚠️ Erreur batch {batch_min}: {m['error'].get('message','?')}", flush=True)
                    break
            await asyncio.sleep(0.1)  # Rate limit
        
        # Trier par timestamp
        all_ticks.sort(key=lambda x: x[0])
        
        # Construire les bougies 1 min
        candles = []
        current_candle = None
        for ts, prix in all_ticks:
            minute = ts // 60
            if current_candle is None or current_candle.ts != minute:
                if current_candle is not None:
                    candles.append({
                        "ts": current_candle.ts,
                        "open": current_candle.open,
                        "high": current_candle.high,
                        "low": current_candle.low,
                        "close": current_candle.close
                    })
                current_candle = Bougie(minute, prix)
            else:
                current_candle.update(prix)
        
        if current_candle is not None:
            candles.append({
                "ts": current_candle.ts,
                "open": current_candle.open,
                "high": current_candle.high,
                "low": current_candle.low,
                "close": current_candle.close
            })
        
        return candles

def backtest(candles):
    """Simule la stratégie sur les bougies historiques"""
    analyse = Analyse()
    trades = wins = profit = 0
    last_trade_ts = 0
    results = []
    
    for i, c in enumerate(candles):
        analyse.add_candle(c["ts"], c)
        
        # Attendre assez de bougies
        if len(analyse.bougies) < 20:  # EMA(20) a besoin de 20
            continue
        
        # Un trade à la fois, séparés d'au moins 5 min
        if c["ts"] - last_trade_ts < 5:
            continue
        
        rsi = analyse.rsi(7)
        ema20 = analyse.ema(20)
        
        if rsi is None or ema20 is None:
            continue
        
        prix = c["close"]
        signal = None
        raisons = []
        
        if rsi >= 80 and prix > ema20:
            signal = "CALL"
            raisons.append(f"RSI={rsi:.0f}≥80")
            raisons.append(f"Prix={prix:.2f}>{ema20:.2f}")
        elif rsi <= 20 and prix < ema20:
            signal = "PUT"
            raisons.append(f"RSI={rsi:.0f}≤20")
            raisons.append(f"Prix={prix:.2f}<{ema20:.2f}")
        
        if not signal:
            continue
        
        # Simuler le trade: regarder le prix 5 min plus tard
        target_ts = c["ts"] + 5  # ts est en minutes
        future_price = None
        for j in range(i+1, len(candles)):
            if candles[j]["ts"] >= target_ts:
                future_price = candles[j]["open"]  # Prix au début de la bougie
                break
        
        if future_price is None:
            continue  # Pas assez de données futures
        
        # Payout: 1.92, risque: 1.0
        if signal == "CALL":
            won = future_price > prix
        else:
            won = future_price < prix
        
        pf = 0.92 if won else -1.0
        trades += 1
        if won: wins += 1
        profit += pf
        last_trade_ts = c["ts"]
        
        # Vérifier qu'il y a assez de bougies restantes pour le prochain trade
        remaining = len(candles) - i - 1
        results.append({
            "trade": trades, "signal": signal, "entry": prix,
            "exit": future_price, "profit": pf,
            "raisons": raisons, "ts": c["ts"]
        })
        icon = "✅" if won else "❌"
        print(f"  {icon} #{trades}: {pf:+.2f}$ | {signal} | E:{prix:.2f}→S:{future_price:.2f} | {'|'.join(raisons)}", flush=True)
        
        if trades >= N_TRADES:
            break
    
    return trades, wins, profit, results

async def main():
    print(f"""
╔═══════════════════════════════════════════════════╗
║  📊 BACKTEST 5 MIN — Historique                  ║
║  RSI≥80/≤20+EMA(20) | {N_TRADES} trades simulés ║
╚═══════════════════════════════════════════════════╝
    """, flush=True)
    
    print("📡 Récupération des ticks historiques (2h)...", flush=True)
    candles = await fetch_candles()
    print(f"✅ {len(candles)} bougies 1 min chargées", flush=True)
    
    print(f"\n🧪 Simulation de la stratégie...\n", flush=True)
    trades, wins, profit, results = backtest(candles)
    
    print(f"\n{'='*55}", flush=True)
    print(f"🏁 BACKTEST 5 MIN | {candles[0]['ts']} → {candles[-1]['ts']}", flush=True)
    print(f"{'='*55}", flush=True)
    print(f"   Bougies: {len(candles)}", flush=True)
    print(f"   Trades: {trades}", flush=True)
    wr = (wins/trades*100) if trades else 0
    print(f"   WR: {wr:.1f}% ({wins}/{trades})", flush=True)
    print(f"   P&L: {profit:+.2f}$", flush=True)
    ev = profit/trades if trades else 0
    print(f"   EV/trade: {ev:+.4f}$", flush=True)
    print(f"   {'✅ RENTABLE' if profit>0 else '❌ NON RENTABLE'}", flush=True)
    print(f"{'='*55}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
