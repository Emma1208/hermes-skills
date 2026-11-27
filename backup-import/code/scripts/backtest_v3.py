#!/usr/bin/env python3
"""
🧪 DERIV BACKTEST v3 — Version corrigée !!!
Les données contrat sont DANS proposal_open_contract, pas dans un champ "contract"
"""
import asyncio, json, websockets
from collections import deque
import sys

TOKEN = "syVTPuwjbZ5zaru"
WS_URL = "wss://ws.derivws.com/websockets/v3?app_id=1089"

# ---------- Stratégies ----------
def trend_5(ticks, price):
    """CALL si 4/5 haussiers, PUT si 4/5 baissiers"""
    if len(ticks) < 5: return None
    last5 = list(ticks)[-5:]
    up = sum(1 for i in range(4) if last5[i] < last5[i+1])
    down = sum(1 for i in range(4) if last5[i] > last5[i+1])
    if up >= 4: return ("CALL", {"contract_type":"CALL"})
    if down >= 4: return ("PUT", {"contract_type":"PUT"})
    return None

def rsi_reversal(ticks, price):
    """RSI: PUT >70, CALL <30"""
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

def ma_crossover(ticks, price):
    """MA5 vs MA20"""
    if len(ticks) < 20: return None
    p = list(ticks)[-20:]
    ma5 = sum(p[-5:]) / 5
    ma20 = sum(p) / 20
    if ma5 > ma20 * 1.001: return ("CALL", {"contract_type":"CALL"})
    if ma5 < ma20 * 0.999: return ("PUT", {"contract_type":"PUT"})
    return None

def digit_under(ticks, price):
    """DigitDiff: digit < 5% sur 100 ticks"""
    if len(ticks) < 100: return None
    curr = int(str(int(price))[-1])
    last100 = list(ticks)[-100:]
    for d in range(10):
        if (last100.count(d)/100)*100 < 5 and d != curr:
            return ("DIGITDIFF", {"contract_type":"DIGITDIFF", "barrier":str(d)})
    return None

# ---------- Testeur ----------
async def test_strat(name, signal_func, max_trades=5):
    print(f"\n{'='*50}", flush=True)
    print(f"🧪 {name}", flush=True)
    print(f"{'='*50}", flush=True)

    try:
        async with asyncio.timeout(120):
            async with websockets.connect(WS_URL, ping_interval=20) as ws:
                await ws.send(json.dumps({"authorize": TOKEN}))
                resp = json.loads(await ws.recv())
                if "error" in resp:
                    print(f"  ❌ Auth: {resp['error']['message']}", flush=True)
                    return None
                
                bal = resp.get("authorize", {}).get("balance", 0)
                print(f"  ✅ Solde: ${bal}", flush=True)
                await ws.send(json.dumps({"ticks": "R_100"}))
                
                ticks = deque(maxlen=200)
                trades = wins = profit = nosig = 0
                
                while trades < max_trades:
                    raw = await asyncio.wait_for(ws.recv(), timeout=15)
                    msg = json.loads(raw)
                    
                    if "tick" in msg and not trades < max_trades in [True]:  # always read ticks
                        price = msg["tick"]["quote"]
                        ticks.append(price)
                        
                        # Chercher signal (seulement si pas en trade)
                        sig = signal_func(ticks, price)
                        if sig is None:
                            nosig += 1
                            continue
                        nosig = 0
                        ctype, extra = sig
                        
                        # PROPOSAL
                        params = {"proposal":1,"amount":1.0,"basis":"stake",
                                  "contract_type":ctype,"currency":"USD",
                                  "duration":1,"duration_unit":"t","symbol":"R_100"}
                        params.update(extra)
                        await ws.send(json.dumps(params))
                        
                        pid = None
                        try:
                            while True:
                                m2 = json.loads(await ws.recv())
                                if m2.get("msg_type") == "proposal":
                                    if "error" not in m2:
                                        pid = m2["proposal"]["id"]
                                        await ws.send(json.dumps({"buy":pid,"price":1.0}))
                                    break
                        except:
                            break
                        
                        if not pid:
                            continue
                        
                        # ATTENDRE LE RÉSULTAT (les données sont directement dans poc)
                        try:
                            while True:
                                m3 = json.loads(await ws.recv())
                                if m3.get("msg_type") == "proposal_open_contract":
                                    poc = m3["proposal_open_contract"]
                                    # VERIFICATION CORRECTE: les champs sont directement dans poc
                                    is_sold = poc.get("status") == "sold" or poc.get("is_sold") or poc.get("is_expired")
                                    if is_sold:
                                        pf = poc.get("profit", 0)
                                        entry = poc.get("entry_spot", 0)
                                        exit_spot = poc.get("exit_spot", 0)
                                        trades += 1
                                        if pf > 0: wins += 1
                                        profit += pf
                                        icon = "✅" if pf > 0 else "❌"
                                        print(f"  {icon} #{trades}: {pf:+.2f}$ | {ctype} | E:{entry} S:{exit_spot}", flush=True)
                                        await asyncio.sleep(0.3)
                                        break  # sort pour prochain trade
                        except:
                            break
                
                wr = (wins/trades*100) if trades else 0
                print(f"\n📊 {name}: {trades}t WR={wr:.0f}% P&L={profit:+.2f}$", flush=True)
                return {"name":name,"trades":trades,"wins":wins,"wr":wr,"pnl":profit,
                        "start_balance": bal}
                
    except asyncio.TimeoutError:
        print("  ⏰ Timeout", flush=True)
        return None
    except Exception as e:
        print(f"  ❌ {type(e).__name__}: {e}", flush=True)
        return None


async def main():
    print("🧪 DERIV BACKTEST v3 — Contrats 1 tick R_100 (démo)", flush=True)
    
    strats = [
        ("Trend 5 ticks", trend_5),
        ("RSI Reversal (70/30)", rsi_reversal),
        ("MA Crossover", ma_crossover),
    ]
    
    results = []
    for name, func in strats:
        r = await test_strat(name, func)
        if r: results.append(r)
    
    if results:
        print(f"\n{'='*60}", flush=True)
        print(f"🏆 CLASSEMENT", flush=True)
        print(f"{'='*60}", flush=True)
        print(f"{'Stratégie':<30} {'T':<5} {'WR':<8} {'P&L':<10}", flush=True)
        print("-"*53, flush=True)
        for r in sorted(results, key=lambda x: x["pnl"], reverse=True):
            print(f"{r['name']:<30} {r['trades']:<5} {r['wr']:.0f}%{'':<5} {r['pnl']:+.2f}$", flush=True)
        best = sorted(results, key=lambda x: x["pnl"], reverse=True)[0]
        print(f"\n🥇 {best['name']} — {best['wr']:.0f}% | {best['pnl']:+.2f}$", flush=True)

asyncio.run(main())
