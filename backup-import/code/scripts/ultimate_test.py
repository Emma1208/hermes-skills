#!/usr/bin/env python3
"""🏆 SMA FILTER ULTIMATE — Test 2 approches: Trend vs Reversion
Filtre: SMA(50) = tendance longue
Strategy A: Trader DANS la direction de SMA (trend)
Strategy B: Trader CONTRE la direction de SMA (reversion)
Signal: 3/5 ticks dans la direction visée
Contrat CALL/PUT 1-tick"""
import asyncio, json, websockets
from collections import deque
from _token import AK, WS
import time

N = 15
TIMEOUT = 300

async def test_strat(name, direction, reversion=False):
    """direction='CALL' ou 'PUT', reversion=True → trader contre la tendance"""
    print(f"\n{'='*50}\n🧪 {name}\n{'='*50}", flush=True)
    
    try:
        async with asyncio.timeout(TIMEOUT):
            async with websockets.connect(WS, ping_interval=10) as ws:
                await ws.send(json.dumps({"authorize": AK}))
                r = json.loads(await ws.recv())
                bal = r.get("authorize",{}).get("balance",0)
                await ws.send(json.dumps({"ticks": "R_100"}))
                
                ticks = deque(maxlen=200)
                trades = wins = profit = 0
                
                # Collecte initiale
                while len(ticks) < 50:
                    raw = await ws.recv()
                    m = json.loads(raw)
                    if "tick" not in m: continue
                    ticks.append(m["tick"]["quote"])
                
                print(f"  ✅ Collecté 50 ticks", flush=True)
                
                while trades < N:
                    raw = await ws.recv()
                    m = json.loads(raw)
                    if "tick" not in m: continue
                    p = m["tick"]["quote"]
                    ticks.append(p)
                    
                    # SMA 50
                    sma50 = sum(list(ticks)[-50:]) / 50
                    above_sma = p > sma50
                    
                    # Direction totale: SMA déterminée ou fixe?
                    if direction == "AUTO":
                        # Automatique: suivre SMA
                        target = "CALL" if (above_sma != reversion) else "PUT"
                    else:
                        target = direction
                    
                    # Signal d'entrée: 3/5 dans la direction
                    l5 = list(ticks)[-5:]
                    u = sum(1 for i in range(4) if l5[i] < l5[i+1])
                    d = sum(1 for i in range(4) if l5[i] > l5[i+1])
                    
                    if target == "CALL" and u < 3: continue
                    if target == "PUT" and d < 3: continue
                    
                    # PROPOSAL + BUY + RESULT
                    await ws.send(json.dumps({"proposal":1,"amount":1.0,"basis":"stake",
                        "contract_type":target,"currency":"USD",
                        "duration":1,"duration_unit":"t","symbol":"R_100"}))
                    pid = None
                    while True:
                        m2 = json.loads(await ws.recv())
                        if m2.get("msg_type") == "proposal":
                            if "error" not in m2: pid = m2["proposal"]["id"]
                            break
                    if not pid: continue
                    
                    await ws.send(json.dumps({"buy":pid,"price":1.0}))
                    cid = None
                    while True:
                        m3 = json.loads(await ws.recv())
                        if m3.get("msg_type") == "buy":
                            if "error" not in m3: cid = m3["buy"]["contract_id"]
                            break
                    if not cid: continue
                    
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
                                sma_dir = "HAUT" if above_sma else "BAS"
                                print(f"  {icon}#{trades}: {pf:+.2f}$ | {target} (SMA={sma_dir})", flush=True)
                                if trades % 5 == 0:
                                    wr = wins/trades*100
                                    print(f"  📊 [{trades}/{N}] WR={wr:.0f}% P&L={profit:+.2f}$", flush=True)
                                break
                
                wr = (wins/trades*100) if trades else 0
                ev = (wins*0.92 - (trades-wins)*1.0)/trades if trades else 0
                print(f"\n📊 {name}: {trades}t | WR={wr:.1f}% | P&L={profit:+.2f}$ | EV={ev:+.4f}$", flush=True)
                return {"name":name,"t":trades,"w":wins,"wr":wr,"pnl":profit,"ev":ev}
    except: return None

async def main():
    print("""
╔══════════════════════════════════════════════════╗
║  🏆 ULTIMATE COMPARISON                         ║
║  SMA(50) filtre + Trend 3/5                     ║
║  CALL/PUT 1-tick | Payout 1.92                 ║
╚══════════════════════════════════════════════════╝
    """, flush=True)
    
    tests = [
        ("📈 Trend CALL-only (fixe)", "CALL", False),
        ("📉 Trend PUT-only (fixe)", "PUT", False),
        ("🔄 SMA Trend (dans direction SMA)", "AUTO", False),
        ("🔄 SMA Reversion (contre SMA)", "AUTO", True),
    ]
    
    results = []
    for name, dir, rev in tests:
        r = await test_strat(name, dir, rev)
        if r: results.append(r)
    
    if results:
        print(f"\n{'='*60}", flush=True)
        print(f"🏆 CLASSEMENT FINAL", flush=True)
        print(f"{'='*60}", flush=True)
        print(f"{'Stratégie':<35} {'T':<4} {'WR':<8} {'P&L':<10}", flush=True)
        print("-"*57, flush=True)
        for r in sorted(results, key=lambda x: x["pnl"], reverse=True):
            rent = "✅" if r["pnl"] > 0 else "❌"
            print(f"{r['name']:<35} {r['t']:<4} {r['wr']:.0f}%{'':<5} {r['pnl']:+.2f}$", flush=True)
        
        best = sorted(results, key=lambda x: x["pnl"], reverse=True)[0]
        print(f"\n🥇 GAGNANTE: {best['name']}", flush=True)
        
        rentables = [r for r in results if r["pnl"] > 0]
        if rentables:
            print(f"\n✅ Stratégies rentables:", flush=True)
            for r in rentables:
                print(f"   • {r['name']}: {r['wr']:.0f}% WR | {r['pnl']:+.2f}$ | EV={r['ev']:+.4f}$/trade", flush=True)

asyncio.run(main())
