#!/usr/bin/env python3
"""🏆 STRATÉGIE 5 MINUTES — RSI + EMA + MACD sur R_100
Bougies 1 minute construites à partir des ticks
Signaux sur nouvelle bougie → trade 5 min CALL/PUT (payout ~1.92)"""
import asyncio, json, websockets
from collections import deque
from _token import AK, WS
import time, math, traceback

N_TRADES = 10
TIMEOUT = 7200  # 2h max

class Bougie:
    """Bougie OHLC 1 minute"""
    def __init__(self, ts, prix):
        self.ts = ts
        self.open = self.high = self.low = self.close = prix
    def update(self, prix):
        self.high = max(self.high, prix)
        self.low = min(self.low, prix)
        self.close = prix

class Analyse:
    """Analyse technique sur bougies 1 min"""
    def __init__(self):
        self.bougies = deque(maxlen=100)  # Bougies 1 min
    
    def add_tick(self, ts, prix):
        """Ajoute un tick, crée/met à jour la bougie courante"""
        minute = int(ts // 60)  # Timestamp en minutes
        if not self.bougies or self.bougies[-1].ts != minute:
            self.bougies.append(Bougie(minute, prix))
        else:
            self.bougies[-1].update(prix)
    
    def rsi(self, period=7):
        """RSI sur les closes des bougies"""
        if len(self.bougies) < period + 1: return None
        closes = [b.close for b in list(self.bougies)[-(period+1):]]
        gains = losses = 0
        for i in range(1, len(closes)):
            d = closes[i] - closes[i-1]
            if d > 0: gains += d
            else: losses += abs(d)
        if losses == 0: return 100
        rs = gains / losses
        return 100 - 100 / (1 + rs)
    
    def ema(self, period=20):
        """EMA sur les closes"""
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
            for i in range(-period, 0):
                ema = data[i] * k + ema * (1 - k)
            return ema
        
        ema12 = calc_ema(closes, 12)
        ema26 = calc_ema(closes, 26)
        macd_line = ema12 - ema26
        
        # Signal line (EMA 9 of MACD)
        macd_values = []
        for i in range(-26, 0):
            e12 = calc_ema(closes[:i] if i < 0 else closes, 12)
            e26 = calc_ema(closes[:i] if i < 0 else closes, 26)
            macd_values.append(e12 - e26)
        
        if len(macd_values) < 9: return macd_line, None
        signal = calc_ema(macd_values, 9)
        return macd_line, signal

async def recv_with_ping(ws, timeout=25):
    """Receive with timeout — sends ping if idle to keep connection alive"""
    try:
        return await asyncio.wait_for(ws.recv(), timeout=timeout)
    except asyncio.TimeoutError:
        await ws.send(json.dumps({"ping": 1}))
        # Drain the pong silently
        try:
            await asyncio.wait_for(ws.recv(), timeout=5)
        except:
            pass
        return None

async def recv_until(ws, check_fn, timeout=30):
    """Receive messages until check_fn returns non-None, with keep-alive pings"""
    start = time.time()
    while time.time() - start < timeout:
        raw = await recv_with_ping(ws, timeout=10)
        if raw is None:
            continue
        try:
            m = json.loads(raw)
            if check_fn(m):
                return m
        except:
            pass
    return None

async def connect_and_auth():
    """Connect to Deriv and authenticate, returns websocket"""
    ws = await websockets.connect(WS, ping_interval=30, ping_timeout=30, max_size=2**20)
    await ws.send(json.dumps({"authorize": AK}))
    auth = await recv_until(ws, lambda m: "authorize" in m)
    if not auth:
        raise Exception("Échec authentification")
    bal = auth["authorize"].get("balance", 0)
    print(f"✅ Connecté — Solde: ${bal}", flush=True)
    await ws.send(json.dumps({"ticks": "R_100"}))
    return ws, bal

async def execute_trade(ws, signal):
    """Execute a trade on the connected websocket, returns result or None"""
    await ws.send(json.dumps({"proposal": 1, "amount": 1.0, "basis": "stake",
        "contract_type": signal, "currency": "USD",
        "duration": 5, "duration_unit": "m", "symbol": "R_100"}))
    
    prop = await recv_until(ws, lambda m: m.get("msg_type") == "proposal")
    if not prop or "error" in prop:
        return None
    pid = prop["proposal"]["id"]
    ask = prop["proposal"]["ask_price"]
    payout = prop["proposal"]["payout"]
    print(f"    💰 Prix: {ask} | Payout: {payout}", flush=True)
    
    await ws.send(json.dumps({"buy": pid, "price": 1.0}))
    buy = await recv_until(ws, lambda m: m.get("msg_type") == "buy")
    if not buy or "error" in buy:
        return None
    cid = buy["buy"]["contract_id"]
    print(f"    ✅ Trade ouvert #{cid} — attente 5 min...", flush=True)
    
    # Subscribe
    await ws.send(json.dumps({"proposal_open_contract": 1, "contract_id": cid, "subscribe": 1}))
    
    # Wait for result (with keep-alive)
    result = await recv_until(ws, lambda m: (
        m.get("msg_type") == "proposal_open_contract" and
        (m["proposal_open_contract"].get("status") == "sold" or m["proposal_open_contract"].get("is_sold"))
    ), timeout=360)
    
    if not result:
        return None
    
    poc = result["proposal_open_contract"]
    return {
        "profit": poc.get("profit", 0),
        "entry": poc.get("entry_spot", 0),
        "exit": poc.get("exit_spot", 0)
    }

async def main():
    print(f"""
╔═══════════════════════════════════════════════════╗
║  🏆 STRATÉGIE 5 MINUTES v3                       ║
║  Bougies 1 min | RSI(7) + EMA(20) + MACD         ║
║  Contrats CALL/PUT 5 min | R_100                 ║
║  {N_TRADES} trades | Ping + Reconnect auto        ║
╚═══════════════════════════════════════════════════╝
    """, flush=True)
    
    analyse = Analyse()
    trades = wins = profit = 0
    in_trade = False
    dernier_signal = None
    collect_start = time.time()
    start_time = time.time()
    
    # Connect and auth
    ws, bal = await connect_and_auth()
    
    print(f"📊 Collecte initiale pour indicateurs...", flush=True)
    
    while trades < N_TRADES and time.time() - start_time < TIMEOUT:
        try:
            raw = await recv_with_ping(ws, timeout=20)
            if raw is None:
                continue
            
            try:
                m = json.loads(raw)
            except:
                continue
            
            if "tick" not in m:
                continue
            
            now = time.time()
            prix = m["tick"]["quote"]
            analyse.add_tick(now, prix)
            
            if in_trade:
                if m.get("msg_type") == "proposal_open_contract":
                    poc = m["proposal_open_contract"]
                    if poc.get("status") == "sold" or poc.get("is_sold"):
                        pf = poc.get("profit", 0)
                        entry = poc.get("entry_spot", 0)
                        exit_spot = poc.get("exit_spot", 0)
                        trades += 1
                        if pf > 0: wins += 1
                        profit += pf
                        icon = "✅" if pf > 0 else "❌"
                        print(f"  {icon} #{trades}: {pf:+.2f}$ | {dernier_signal} | E:{entry:.2f}→S:{exit_spot:.2f}", flush=True)
                        in_trade = False
                        collect_start = time.time()
                continue
            
            if len(analyse.bougies) < 8:
                if int(now) % 30 <= 1:
                    print(f"  ⏳ Collecte... {len(analyse.bougies)} bougies", flush=True)
                continue
            
            current_min = int(now // 60)
            current_bougie = analyse.bougies[-1]
            
            if current_min == current_bougie.ts:
                continue
            
            rsi = analyse.rsi(7)
            ema20 = analyse.ema(20)
            macd_line, macd_signal = analyse.macd()
            
            if rsi is None or ema20 is None:
                continue
            
            prix_actuel = current_bougie.close
            
            signal = None
            raisons = []
            
            if rsi > 55 and prix_actuel > ema20:
                signal = "CALL"
                raisons.append(f"RSI={rsi:.0f}>55")
                raisons.append(f"Prix>{ema20:.2f}")
                if macd_line is not None and macd_signal is not None and macd_line > macd_signal:
                    raisons.append("MACD>signal")
            elif rsi < 45 and prix_actuel < ema20:
                signal = "PUT"
                raisons.append(f"RSI={rsi:.0f}<45")
                raisons.append(f"Prix<{ema20:.2f}")
                if macd_line is not None and macd_signal is not None and macd_line < macd_signal:
                    raisons.append("MACD<signal")
            
            if not signal:
                continue
            
            dernier_signal = signal
            temps_attente = time.time() - collect_start
            print(f"  🎯 Signal #{trades+1}: {signal} | {' | '.join(raisons)} | ⏱{temps_attente:.0f}s", flush=True)
            
            in_trade = True
            result = await execute_trade(ws, signal)
            
            if result:
                trades += 1
                if result["profit"] > 0:
                    wins += 1
                profit += result["profit"]
                icon = "✅" if result["profit"] > 0 else "❌"
                print(f"  {icon} #{trades}: {result['profit']:+.2f}$ | {signal} | E:{result['entry']:.2f}→S:{result['exit']:.2f}", flush=True)
            else:
                print(f"  ❌ #{trades+1}: Trade échoué", flush=True)
                trades += 1
            
            in_trade = False
            collect_start = time.time()
            
            if trades % 3 == 0:
                wr = (wins/trades*100) if trades > 0 else 0
                print(f"  📊 [{trades}/{N_TRADES}] WR={wr:.0f}% | P&L={profit:+.2f}$", flush=True)
        
        except (websockets.exceptions.ConnectionClosed, ConnectionResetError, OSError) as e:
            print(f"  🔌 Déconnecté — reconnexion...", flush=True)
            try:
                await ws.close()
            except:
                pass
            for retry in range(5):
                await asyncio.sleep(5)
                try:
                    ws, bal = await connect_and_auth()
                    print(f"  ✅ Reconnecté (tentative {retry+1}) — {len(analyse.bougies)} bougies conservées", flush=True)
                    break
                except Exception as ce:
                    print(f"  ⚠️ Tentative {retry+1}/5 échouée: {ce}", flush=True)
            else:
                print(f"  ❌ Échec reconnexion après 5 tentatives — abandon", flush=True)
                break
    
    try:
        await ws.close()
    except:
        pass
    
    # FINAL REPORT
    wr = (wins/trades*100) if trades > 0 else 0
    ev = (wins*0.92 - (trades-wins)*1.0)/trades if trades > 0 else 0
    print(f"\n{'='*55}", flush=True)
    print(f"🏁 STRATÉGIE 5 MIN — {trades} trades", flush=True)
    print(f"{'='*55}", flush=True)
    print(f"   WR: {wr:.1f}% ({wins}/{trades})", flush=True)
    print(f"   P&L: {profit:+.2f}$", flush=True)
    print(f"   EV/trade: {ev:+.4f}$", flush=True)
    print(f"   {'✅ RENTABLE' if profit>0 else '❌ NON RENTABLE'}", flush=True)
    print(f"{'='*55}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
