#!/usr/bin/env python3
"""🏆 DIGITDIFF FINAL — Test 100 trades, seuil 2%"""
import asyncio, json, websockets
from collections import deque
from _token import AK, WS
import time

THRESHOLD = 2  # %
MAX_TRADES = 100
TIMEOUT = 600  # 10 min max

async def main():
    print(f"🏆 DIGITDIFF FINAL — {MAX_TRADES} trades | Seuil: {THRESHOLD}%", flush=True)
    start = time.time()
    
    async with websockets.connect(WS, ping_interval=10) as ws:
        await ws.send(json.dumps({"authorize": AK}))
        r = json.loads(await ws.recv())
        bal_start = r.get("authorize",{}).get("balance",0)
        print(f"✅ Solde: ${bal_start}", flush=True)
        await ws.send(json.dumps({"ticks": "R_100"}))
        
        digits = deque(maxlen=100)
        trades = wins = profit = 0
        
        # Collecte initiale
        print("📊 Collecte initiale 100 ticks...", flush=True)
        while len(digits) < 100:
            raw = await ws.recv()
            m = json.loads(raw)
            if "tick" not in m: continue
            d = int(str(int(m["tick"]["quote"]))[-1])
            digits.append(d)
        
        freq = {i: list(digits).count(i) for i in range(10)}
        print(f"   Distribution: {freq}", flush=True)
        
        # Trading
        while trades < MAX_TRADES:
            raw = await ws.recv()
            m = json.loads(raw)
            if "tick" not in m: continue
            
            price = m["tick"]["quote"]
            curr_digit = int(str(int(price))[-1])
            digits.append(curr_digit)
            freq = {i: list(digits).count(i) for i in range(10)}
            
            # Chercher digit ≤ THRESHOLD% ET ≠ digit actuel
            target = None
            for d in range(10):
                if freq[d] <= THRESHOLD and d != curr_digit:
                    target = d
                    break
            if target is None: continue
            
            # PROPOSAL
            await ws.send(json.dumps({"proposal":1,"amount":1.0,"basis":"stake",
                "contract_type":"DIGITDIFF","currency":"USD",
                "duration":1,"duration_unit":"t","symbol":"R_100","barrier":str(target)}))
            
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
                        
                        # Résumé périodique
                        if trades % 10 == 0:
                            wr = (wins/trades*100)
                            rate = trades / (time.time() - start)
                            print(f"  📊 [{trades}/{MAX_TRADES}] WR={wr:.0f}% P&L={profit:+.2f}$ | {rate:.1f}t/min", flush=True)
                        break
        
        # Rapport final
        elapsed = time.time() - start
        wr = (wins/trades*100) if trades else 0
        bal_end = bal_start + profit
        print(f"\n{'='*55}", flush=True)
        print(f"🏁 RAPPORT FINAL — {trades} trades en {elapsed:.0f}s", flush=True)
        print(f"{'='*55}", flush=True)
        print(f"   WR: {wr:.1f}% ({wins}/{trades})", flush=True)
        print(f"   P&L: {profit:+.2f}$", flush=True)
        print(f"   Gain moyen: {profit/trades:+.4f}$", flush=True)
        print(f"   Rythme: {trades/elapsed*60:.1f} trades/min", flush=True)
        print(f"   Solde: ${bal_start:.2f} → ${bal_end:.2f}", flush=True)
        print(f"   Rendement: {profit/bal_start*100:.2f}%", flush=True)
        print(f"   {'✅ RENTABLE' if profit > 0 else '❌ NON RENTABLE'}", flush=True)
        print(f"{'='*55}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
