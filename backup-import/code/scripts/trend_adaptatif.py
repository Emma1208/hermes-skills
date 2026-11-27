#!/usr/bin/env python3
"""🏆 TREND ADAPTATIF — Filtre de tendance + Trend 4/5
Mode = direction de MA50 (haussière→CALL, baissière→PUT)
Signal = 4/5 ticks dans la direction du mode
Contrat CALL/PUT 1-tick | Payout 1.92"""
import asyncio, json, websockets
from collections import deque
from _token import AK, WS

N_TRADES = 30
TIMEOUT = 600

async def main():
    print(f"🏆 TREND ADAPTATIF — {N_TRADES} trades sur R_100", flush=True)
    
    async with asyncio.timeout(TIMEOUT):
        async with websockets.connect(WS, ping_interval=10) as ws:
            await ws.send(json.dumps({"authorize": AK}))
            r = json.loads(await ws.recv())
            bal_start = r.get("authorize",{}).get("balance",0)
            print(f"✅ Solde: ${bal_start}", flush=True)
            await ws.send(json.dumps({"ticks": "R_100"}))
            
            ticks = deque(maxlen=200)
            trades = wins = profit = 0
            mode = "NEUTRE"  # HAUSSIER/BAISSIER
            
            while len(ticks) < 50:
                raw = await ws.recv()
                m = json.loads(raw)
                if "tick" not in m: continue
                ticks.append(m["tick"]["quote"])
            
            print(f"📊 Collecte initiale: 50 ticks ✓", flush=True)
            
            while trades < N_TRADES:
                raw = await ws.recv()
                m = json.loads(raw)
                if "tick" not in m: continue
                
                p = m["tick"]["quote"]
                ticks.append(p)
                
                # Mise à jour du MODE (tous les 5 ticks)
                if len(ticks) >= 55 and len(ticks) % 5 == 0:
                    prices = list(ticks)[-50:]
                    first_third = sum(prices[:17])/17
                    last_third = sum(prices[-17:])/17
                    slope = (last_third - first_third) / first_third
                    
                    if slope > 0.0005:  # Hausse significative
                        new_mode = "HAUSSIER"
                    elif slope < -0.0005:  # Baisse significative
                        new_mode = "BAISSIER"
                    else:
                        new_mode = "NEUTRE"
                    
                    if new_mode != mode:
                        mode = new_mode
                        print(f"  🔄 Mode: {mode} (slope={slope:+.6f})", flush=True)
                
                if mode == "NEUTRE":
                    continue  # Ne pas trader en mode neutre
                
                # Signal Trend 5 ticks dans la direction du mode
                if len(ticks) >= 5:
                    l5 = list(ticks)[-5:]
                    up = sum(1 for i in range(4) if l5[i] < l5[i+1])
                    down = sum(1 for i in range(4) if l5[i] > l5[i+1])
                    
                    if mode == "HAUSSIER" and up >= 3:
                        signal = "CALL"
                    elif mode == "BAISSIER" and down >= 3:
                        signal = "PUT"
                    else:
                        continue
                else:
                    continue
                
                # --- PROPOSAL ---
                await ws.send(json.dumps({"proposal":1,"amount":1.0,"basis":"stake",
                    "contract_type":signal,"currency":"USD",
                    "duration":1,"duration_unit":"t","symbol":"R_100"}))
                
                pid = None
                while True:
                    m2 = json.loads(await ws.recv())
                    if m2.get("msg_type") == "proposal":
                        if "error" not in m2: pid = m2["proposal"]["id"]
                        break
                if not pid: continue
                
                # --- BUY ---
                await ws.send(json.dumps({"buy":pid,"price":1.0}))
                cid = None
                while True:
                    m3 = json.loads(await ws.recv())
                    if m3.get("msg_type") == "buy":
                        if "error" not in m3: cid = m3["buy"]["contract_id"]
                        break
                if not cid: continue
                
                # --- SUBSCRIBE ---
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
                            
                            # Résumé périodique
                            if trades % 5 == 0:
                                wr = (wins/trades*100)
                                print(f"  📊 [{trades}/{N_TRADES}] {icon} {pf:+.2f}$ | {signal} ({mode}) | WR={wr:.0f}% P&L={profit:+.2f}$", flush=True)
                            else:
                                print(f"  {icon}#{trades}: {pf:+.2f}$ | {signal} ({mode})", flush=True)
                            break
        
        # FINAL
        wr = (wins/trades*100) if trades else 0
        ev = (wins*0.92 - (trades-wins)*1.0)/trades if trades else 0
        bal_end = bal_start + profit
        
        print(f"\n{'='*55}", flush=True)
        print(f"🏁 TREND ADAPTATIF — {trades} trades", flush=True)
        print(f"{'='*55}", flush=True)
        print(f"   WR: {wr:.1f}% ({wins}/{trades})", flush=True)
        print(f"   P&L: {profit:+.2f}$", flush=True)
        print(f"   EV/trade: {ev:+.4f}$", flush=True)
        print(f"   Solde: ${bal_start:.2f} → ${bal_end:.2f}", flush=True)
        print(f"   {'✅ RENTABLE' if profit>0 else '❌ NON RENTABLE'}", flush=True)
        print(f"{'='*55}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
