#!/usr/bin/env python3
"""🏆 MULTI-STRATEGY COMPARISON — Test 6 stratégies sur R_100
Compare CALL/PUT 1-tick avec payout 1.92
Seuil de rentabilité: 52.1% WR"""
import asyncio, json, websockets
from collections import deque
from _token import AK, WS
import time

N_TRADES = 10  # trades par stratégie
TIMEOUT = 240  # 4 min par stratégie

# ==================== STRATÉGIES ====================

def s_trend_put(ticks, price):
    """PUT-only: 4/5 ticks baissiers"""
    if len(ticks) < 5: return None
    l5 = list(ticks)[-5:]
    d = sum(1 for i in range(4) if l5[i] > l5[i+1])
    if d >= 4: return ("PUT", {})
    return None

def s_trend_call(ticks, price):
    """CALL-only: 4/5 ticks haussiers"""
    if len(ticks) < 5: return None
    l5 = list(ticks)[-5:]
    u = sum(1 for i in range(4) if l5[i] < l5[i+1])
    if u >= 4: return ("CALL", {})
    return None

def s_rsi_put(ticks, price):
    """PUT si RSI > 75 (surachat) — mean reversion"""
    if len(ticks) < 20: return None
    p = list(ticks)[-20:]
    g = l = 0
    for i in range(-14, 0):
        d = p[i] - p[i-1]
        if d > 0: g += d
        elif d < 0: l += abs(d)
    rsi = 100 - 100/(1+g/(l or 0.001))
    if rsi > 75: return ("PUT", {})
    return None

def s_rsi_call(ticks, price):
    """CALL si RSI < 25 (survente) — mean reversion"""
    if len(ticks) < 20: return None
    p = list(ticks)[-20:]
    g = l = 0
    for i in range(-14, 0):
        d = p[i] - p[i-1]
        if d > 0: g += d
        elif d < 0: l += abs(d)
    rsi = 100 - 100/(1+g/(l or 0.001))
    if rsi < 25: return ("CALL", {})
    return None

def s_ma_trend(ticks, price):
    """MA5 vs MA20: CALL si haussier, PUT si baissier"""
    if len(ticks) < 20: return None
    p = list(ticks)[-20:]
    ma5 = sum(p[-5:])/5
    ma20 = sum(p)/20
    if ma5 > ma20 * 1.0005: return ("CALL", {})
    if ma5 < ma20 * 0.9995: return ("PUT", {})
    return None

def s_bb_revert(ticks, price):
    """Bollinger Bands reversion: CALL near lower, PUT near upper"""
    if len(ticks) < 20: return None
    p = list(ticks)[-20:]
    mean = sum(p)/20
    var = sum((x-mean)**2 for x in p)/20
    std = var**0.5
    upper = mean + 2*std
    lower = mean - 2*std
    curr = p[-1]
    if curr >= upper: return ("PUT", {})
    if curr <= lower: return ("CALL", {})
    return None

def s_combo_put(ticks, price):
    """PUT seulement si RSI surachat + trend baissier MA"""
    if len(ticks) < 20: return None
    p = list(ticks)[-20:]
    # RSI
    g = l = 0
    for i in range(-14, 0):
        d = p[i] - p[i-1]
        if d > 0: g += d
        elif d < 0: l += abs(d)
    rsi = 100 - 100/(1+g/(l or 0.001))
    # MA
    ma5 = sum(p[-5:])/5
    ma20 = sum(p)/20
    # Trend 5
    l5 = list(ticks)[-5:]
    trend_down = sum(1 for i in range(4) if l5[i] > l5[i+1]) >= 3
    
    if rsi > 70 and ma5 < ma20 and trend_down:
        return ("PUT", {})
    if rsi < 30 and ma5 > ma20:
        return ("CALL", {})
    return None

STRATS = [
    ("🎯 PUT-only (Trend 4/5)", s_trend_put),
    ("🎯 CALL-only (Trend 4/5)", s_trend_call),
    ("📉 RSI>75 → PUT", s_rsi_put),
    ("📈 RSI<25 → CALL", s_rsi_call),
    ("📊 MA Crossover", s_ma_trend),
    ("📐 Bollinger revert", s_bb_revert),
    ("🔬 Combo RSI+MA+Trend", s_combo_put),
]

# ==================== TESTEUR ====================

async def test_strat(name, signal_func):
    print(f"\n{'='*50}", flush=True)
    print(f"🧪 {name}", flush=True)
    print(f"{'='*50}", flush=True)
    
    t0 = time.time()
    try:
        async with asyncio.timeout(TIMEOUT):
            async with websockets.connect(WS, ping_interval=10) as ws:
                await ws.send(json.dumps({"authorize": AK}))
                r = json.loads(await ws.recv())
                if "error" in r: return None
                bal = r.get("authorize",{}).get("balance",0)
                await ws.send(json.dumps({"ticks": "R_100"}))
                
                ticks = deque(maxlen=200)
                trades = wins = profit = 0
                
                while trades < N_TRADES:
                    raw = await ws.recv()
                    m = json.loads(raw)
                    if "tick" not in m: continue
                    p = m["tick"]["quote"]
                    ticks.append(p)
                    
                    sig = signal_func(ticks, p)
                    if not sig: continue
                    ctype, _ = sig
                    
                    # PROPOSAL
                    await ws.send(json.dumps({"proposal":1,"amount":1.0,"basis":"stake",
                        "contract_type":ctype,"currency":"USD",
                        "duration":1,"duration_unit":"t","symbol":"R_100"}))
                    pid = None
                    while True:
                        m2 = json.loads(await ws.recv())
                        if m2.get("msg_type") == "proposal":
                            if "error" not in m2: pid = m2["proposal"]["id"]
                            break
                    if not pid: continue
                    
                    # BUY
                    await ws.send(json.dumps({"buy":pid,"price":1.0}))
                    cid = None
                    while True:
                        m3 = json.loads(await ws.recv())
                        if m3.get("msg_type") == "buy":
                            if "error" not in m3: cid = m3["buy"]["contract_id"]
                            break
                    if not cid: continue
                    
                    # SUBSCRIBE
                    await ws.send(json.dumps({"proposal_open_contract":1,"contract_id":cid,"subscribe":1}))
                    while True:
                        m4 = json.loads(await ws.recv())
                        if m4.get("msg_type") == "proposal_open_contract":
                            poc = m4["proposal_open_contract"]
                            if poc.get("status")=="sold" or poc.get("is_sold"):
                                pf = poc.get("profit",0)
                                trades += 1
                                if pf > 0: wins += 1
                                profit += pf
                                icon = "✅" if pf > 0 else "❌"
                                print(f"  {icon}#{trades}: {pf:+.2f}$ | {ctype}", flush=True)
                                break
                
                elapsed = time.time() - t0
                wr = (wins/trades*100) if trades else 0
                ev = (wins*0.92 - (trades-wins)*1.0)/trades if trades else 0
                
                print(f"\n📊 {name}: {trades}t | WR={wr:.0f}% | P&L={profit:+.2f}$ | EV={ev:+.4f}$ | ⏱{elapsed:.0f}s", flush=True)
                return {"name":name,"t":trades,"w":wins,"wr":wr,"pnl":profit,"ev":ev}
    
    except asyncio.TimeoutError:
        print(f"  ⏰ Timeout", flush=True)
        return None
    except Exception as e:
        print(f"  ❌ {type(e).__name__}: {e}", flush=True)
        return None


async def main():
    print("""
╔══════════════════════════════════════════╗
║  🏆 MULTI-STRATEGY COMPARISON            ║
║  7 stratégies × 15 trades sur R_100      ║
║  CALL/PUT 1-tick | Payout 1.92          ║
║  Seuil rentabilité: WR > 52.1%          ║
╚══════════════════════════════════════════╝
    """, flush=True)
    
    results = []
    for name, func in STRATS:
        r = await test_strat(name, func)
        if r: results.append(r)
    
    # CLASSEMENT
    if results:
        print(f"\n{'='*65}", flush=True)
        print(f"🏆 CLASSEMENT FINAL", flush=True)
        print(f"{'='*65}", flush=True)
        print(f"{'Stratégie':<35} {'T':<4} {'WR':<8} {'P&L':<10} {'EV/trade':<10}", flush=True)
        print("-"*65, flush=True)
        ranked = sorted(results, key=lambda x: x["pnl"], reverse=True)
        for r in ranked:
            rent = "✅" if r["pnl"] > 0 else "❌"
            be = r["ev"] * r["t"]
            print(f"{r['name']:<35} {r['t']:<4} {r['wr']:.0f}%{'':<5} {r['pnl']:+.2f}$ {'':<3} {r['ev']:+.4f}$", flush=True)
        
        best = ranked[0]
        print(f"\n🥇 GAGNANTE: {best['name']}", flush=True)
        print(f"   WR: {best['wr']:.0f}% | P&L: {best['pnl']:+.2f}$ | EV: {best['ev']:+.4f}$/trade", flush=True)
        
        # Seuils
        rentables = [r for r in ranked if r["pnl"] > 0]
        if rentables:
            print(f"\n✅ Stratégies rentables ({len(rentables)}):", flush=True)
            for r in rentables:
                print(f"   • {r['name']}: {r['wr']:.0f}% WR, {r['pnl']:+.2f}$", flush=True)

asyncio.run(main())
