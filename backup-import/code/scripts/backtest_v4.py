#!/usr/bin/env python3
"""🏆 DERIV BACKTEST v4 — Stratégies vs Baseline (CALL aléatoire)"""
import asyncio, json, websockets
from collections import deque
from _token import AK, WS
import random

async def run_trades(name, signal_func, n=10):
    """Exécute n trades selon la stratégie signal_func"""
    print(f"\n{'='*50}\n🧪 {name}\n{'='*50}", flush=True)
    
    try:
        async with asyncio.timeout(300):
            async with websockets.connect(WS, ping_interval=10) as ws:
                await ws.send(json.dumps({"authorize": AK}))
                r = json.loads(await ws.recv())
                if "error" in r: return None
                await ws.send(json.dumps({"ticks": "R_100"}))
                
                ticks = deque(maxlen=200)
                trades = wins = profit = 0
                
                while trades < n:
                    raw = await asyncio.wait_for(ws.recv(), timeout=30)
                    m = json.loads(raw)
                    if "tick" not in m: continue
                    
                    p = m["tick"]["quote"]
                    ticks.append(p)
                    
                    # Signal
                    if signal_func:
                        sig = signal_func(ticks, p)
                        if sig is None: continue
                        ctype, extra = sig
                    else:
                        # Baseline: CALL aléatoire
                        ctype = random.choice(["CALL", "PUT"])
                        extra = {"contract_type": ctype}
                    
                    # Proposal
                    params = {"proposal":1,"amount":1.0,"basis":"stake",
                              "contract_type":ctype,"currency":"USD",
                              "duration":1,"duration_unit":"t","symbol":"R_100"}
                    params.update(extra)
                    await ws.send(json.dumps(params))
                    
                    pid = None
                    while True:
                        m2 = json.loads(await ws.recv())
                        if m2.get("msg_type") == "proposal":
                            if "error" not in m2: pid = m2["proposal"]["id"]
                            break
                    if not pid: continue
                    
                    # Buy
                    await ws.send(json.dumps({"buy":pid,"price":1.0}))
                    cid = None
                    while True:
                        m3 = json.loads(await ws.recv())
                        if m3.get("msg_type") == "buy":
                            if "error" not in m3: cid = m3["buy"]["contract_id"]
                            break
                    if not cid: continue
                    
                    # Subscribe
                    await ws.send(json.dumps({"proposal_open_contract":1,"contract_id":cid,"subscribe":1}))
                    
                    # Wait result
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
                                print(f"  {icon} #{trades}: {pf:+.2f}$ | {ctype}", flush=True)
                                break
                
                wr = (wins/trades*100) if trades else 0
                print(f"\n📊 {name}: {trades}t WR={wr:.0f}% P&L={profit:+.2f}$", flush=True)
                return {"name":name,"t":trades,"w":wins,"wr":wr,"pnl":profit}
    
    except asyncio.TimeoutError:
        print(f"  ⏰ Timeout", flush=True)
        return None
    except Exception as e:
        print(f"  ❌ {type(e).__name__}: {e}", flush=True)
        return None


# Stratégies
def trend5(t, p):
    if len(t)<5: return None
    l5 = list(t)[-5:]
    u = sum(1 for i in range(4) if l5[i] < l5[i+1])
    d = sum(1 for i in range(4) if l5[i] > l5[i+1])
    if u>=4: return ("CALL", {})
    if d>=4: return ("PUT", {})
    return None

def rsi70(t, p):
    if len(t)<20: return None
    tl = list(t)[-20:]
    g=l=0
    for i in range(-14,0):
        d = tl[i]-tl[i-1]
        if d>0: g+=d
        elif d<0: l+=abs(d)
    r = 100-100/(1+g/(l or 0.0001))
    if r>70: return ("PUT", {})
    if r<30: return ("CALL", {})
    return None

def macross(t, p):
    if len(t)<20: return None
    tl = list(t)[-20:]
    m5 = sum(tl[-5:])/5
    m20 = sum(tl)/20
    if m5>m20*1.001: return ("CALL", {})
    if m5<m20*0.999: return ("PUT", {})
    return None


async def main():
    print("🏆 BACKTEST DERIV v4 — Stratégies vs Baseline", flush=True)
    
    tests = [
        ("🎲 Baseline (aléatoire)", None),
        ("📈 Trend 5 ticks", trend5),
        ("📊 RSI Reversal", rsi70),
        ("📉 MA Crossover", macross),
    ]
    
    results = []
    for name, func in tests:
        r = await run_trades(name, func, n=10)
        if r: results.append(r)
    
    print(f"\n{'='*60}", flush=True)
    print(f"🏆 CLASSEMENT", flush=True)
    print(f"{'='*60}", flush=True)
    print(f"{'Stratégie':<30} {'T':<4} {'WR':<8} {'P&L':<10}", flush=True)
    print("-"*52, flush=True)
    for r in sorted(results, key=lambda x: x["pnl"], reverse=True):
        b = "🎲" if "Baseline" in r["name"] else ""
        print(f"{r['name']:<30} {r['t']:<4} {r['wr']:.0f}%{'':<5} {r['pnl']:+.2f}$ {b}", flush=True)
    
    if len(results) >= 2:
        best = sorted(results, key=lambda x: x["pnl"], reverse=True)[0]
        base = [r for r in results if "Baseline" in r["name"]]
        if base:
            b = base[0]
            diff = best["pnl"] - b["pnl"]
            print(f"\n🥇 Meilleure: {best['name']} ({best['pnl']:+.2f}$)", flush=True)
            print(f"📊 vs Baseline: {diff:+.2f}$")
    
    print(f"\n💡 Mise: 1$ | Contrat: 1 tick | Symbole: R_100", flush=True)

asyncio.run(main())
