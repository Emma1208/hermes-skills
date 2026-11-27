#!/usr/bin/env python3
"""
🏆 DERIV STRATEGY BACKTEST — Version finale
Teste les stratégies Trend 5, RSI, MA Crossover
Chaque stratégie exécute des trades réels sur compte démo R_100
"""
import asyncio, json, websockets
from collections import deque
from _token import AK, WS

# ==================== STRATÉGIES ====================

def trend_5(ticks, price):
    """4/5 ticks dans la même direction"""
    if len(ticks) < 5: return None
    last5 = list(ticks)[-5:]
    up = sum(1 for i in range(4) if last5[i] < last5[i+1])
    down = sum(1 for i in range(4) if last5[i] > last5[i+1])
    if up >= 4: return ("CALL", {"contract_type":"CALL"})
    if down >= 4: return ("PUT", {"contract_type":"PUT"})
    return None

def rsi_70(ticks, price):
    """RSI 14: PUT >70, CALL <30"""
    if len(ticks) < 20: return None
    p = list(ticks)[-20:]
    g = l = 0
    for i in range(-14, 0):
        d = p[i] - p[i-1]
        if d > 0: g += d
        elif d < 0: l += abs(d)
    rsi = 100 - 100/(1+g/(l or 0.0001))
    if rsi > 70: return ("PUT", {"contract_type":"PUT"})
    if rsi < 30: return ("CALL", {"contract_type":"CALL"})
    return None

def ma_cross(ticks, price):
    """MA5 vs MA20 avec spread 0.1%"""
    if len(ticks) < 20: return None
    p = list(ticks)[-20:]
    ma5 = sum(p[-5:]) / 5
    ma20 = sum(p) / 20
    if ma5 > ma20 * 1.001: return ("CALL", {"contract_type":"CALL"})
    if ma5 < ma20 * 0.999: return ("PUT", {"contract_type":"PUT"})
    return None

# ==================== EXÉCUTEUR ====================

async def run_strat(name, signal_func, max_trades=15):
    print(f"\n{'='*50}", flush=True)
    print(f"🧪 {name}", flush=True)
    print(f"{'='*50}", flush=True)
    
    try:
        async with asyncio.timeout(180):
            async with websockets.connect(WS, ping_interval=20) as ws:
                await ws.send(json.dumps({"authorize": AK}))
                r = json.loads(await ws.recv())
                if "error" in r:
                    print(f"  ❌ Auth: {r['error']['message']}", flush=True)
                    return None
                
                bal = r.get("authorize",{}).get("balance",0)
                await ws.send(json.dumps({"ticks": "R_100"}))
                
                ticks = deque(maxlen=200)
                trades = wins = profit = 0
                
                while trades < max_trades:
                    raw = await ws.recv()
                    m = json.loads(raw)
                    if "tick" not in m: continue
                    
                    p = m["tick"]["quote"]
                    ticks.append(p)
                    
                    sig = signal_func(ticks, p)
                    if sig is None: continue
                    
                    ctype, extra = sig
                    
                    # --- PROPOSAL ---
                    params = {"proposal":1,"amount":1.0,"basis":"stake",
                              "contract_type":ctype,"currency":"USD",
                              "duration":1,"duration_unit":"t","symbol":"R_100"}
                    params.update(extra)
                    await ws.send(json.dumps(params))
                    
                    pid = None
                    while True:
                        m2 = json.loads(await ws.recv())
                        if m2.get("msg_type") == "proposal":
                            if "error" not in m2:
                                pid = m2["proposal"]["id"]
                            break
                    
                    if not pid: continue
                    
                    # --- BUY ---
                    await ws.send(json.dumps({"buy":pid,"price":1.0}))
                    
                    cid = None
                    while True:
                        m3 = json.loads(await ws.recv())
                        if m3.get("msg_type") == "buy":
                            if "error" not in m3:
                                cid = m3["buy"]["contract_id"]
                            break
                    
                    if not cid: continue
                    
                    # --- SUBSCRIBE ---
                    await ws.send(json.dumps({
                        "proposal_open_contract":1,"contract_id":cid,"subscribe":1
                    }))
                    
                    # --- WAIT RESULT ---
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
                                print(f"  {icon} #{trades}: {pf:+.2f}$", flush=True)
                                break
                
                wr = (wins/trades*100) if trades else 0
                print(f"\n📊 {name}: {trades}t WR={wr:.0f}% P&L={profit:+.2f}$", flush=True)
                return {"name":name,"trades":trades,"wins":wins,"wr":wr,"pnl":profit,
                        "start_bal":bal}
    
    except asyncio.TimeoutError:
        print(f"  ⏰ Timeout", flush=True)
        return None
    except Exception as e:
        print(f"  ❌ {type(e).__name__}: {e}", flush=True)
        return None

async def main():
    print("""
╔═══════════════════════════════════════════╗
║  🏆 DERIV STRATEGY BACKTEST               ║
║  Contrats 1 tick sur R_100 (compte démo)  ║
║  15 trades par stratégie | Mise: 1$       ║
╚═══════════════════════════════════════════╝
    """, flush=True)
    
    strats = [
        ("Trend 5 ticks (4/5)", trend_5),
        ("RSI Reversal (70/30)", rsi_70),
        ("MA Crossover (0.1%)", ma_cross),
    ]
    
    results = []
    for name, func in strats:
        r = await run_strat(name, func)
        if r: results.append(r)
    
    # Classement
    if results:
        print(f"\n{'='*60}", flush=True)
        print(f"🏆 CLASSEMENT FINAL", flush=True)
        print(f"{'='*60}", flush=True)
        print(f"{'Stratégie':<30} {'T':<5} {'WR':<8} {'P&L':<10}", flush=True)
        print("-"*53, flush=True)
        ranked = sorted(results, key=lambda x: x["pnl"], reverse=True)
        for r in ranked:
            print(f"{r['name']:<30} {r['trades']:<5} {r['wr']:.0f}%{'':<5} {r['pnl']:+.2f}$", flush=True)
        
        best = ranked[0]
        print(f"\n🥇 GAGNANTE: {best['name']}", flush=True)
        print(f"   WR: {best['wr']:.0f}% | P&L: {best['pnl']:+.2f}$ | {best['trades']} trades", flush=True)
        
        worst = ranked[-1]
        if worst['pnl'] < 0:
            print(f"⚠️  Perdante: {worst['name']} ({worst['pnl']:+.2f}$)", flush=True)

asyncio.run(main())
