#!/usr/bin/env python3
"""🧪 DIGITDIFF STAT — Stratégie basée sur fréquence des chiffres
Vérifier si un digit apparait ≤4 fois sur 100 → DIGITDIFF dessus"""
import asyncio, json, websockets
from collections import deque
from _token import AK, WS

async def main():
    print("🔌 Connexion...", flush=True)
    async with websockets.connect(WS, ping_interval=10) as ws:
        await ws.send(json.dumps({"authorize": AK}))
        r = json.loads(await ws.recv())
        bal = r.get("authorize",{}).get("balance",0)
        print(f"✅ Solde: ${bal}", flush=True)
        await ws.send(json.dumps({"ticks": "R_100"}))
        
        digits = deque(maxlen=100)
        trades = wins = profit = 0
        MAX = 30
        
        # Phase 1 : collecter 100 digits
        print("📊 Collecte de 100 digits...", flush=True)
        while len(digits) < 100:
            raw = await ws.recv()
            m = json.loads(raw)
            if "tick" not in m: continue
            d = int(str(int(m["tick"]["quote"]))[-1])
            digits.append(d)
        
        print(f"   Distribution initiale:", flush=True)
        freq = {i: list(digits).count(i) for i in range(10)}
        for i in range(10):
            bar = "█" * freq[i]
            print(f"   {i}: {bar} ({freq[i]}%)", flush=True)
        
        # Phase 2 : trader
        while trades < MAX:
            raw = await ws.recv()
            m = json.loads(raw)
            if "tick" not in m: continue
            
            price = m["tick"]["quote"]
            curr_digit = int(str(int(price))[-1])
            prev_digit = digits[-1] if digits else curr_digit
            digits.append(curr_digit)
            
            if curr_digit == prev_digit:
                continue  # attendre un tick différent
            
            # Analyser la fréquence
            freq = {i: list(digits).count(i) for i in range(10)}
            
            # Chercher un digit avec fréquence ≤ 4%
            target = None
            for d in range(10):
                if freq[d] <= 4 and d != curr_digit:
                    target = d
                    break
            
            if target is None:
                continue
            
            # PROPOSAL DIGITDIFF
            params = {"proposal":1,"amount":1.0,"basis":"stake",
                      "contract_type":"DIGITDIFF","currency":"USD",
                      "duration":1,"duration_unit":"t","symbol":"R_100",
                      "barrier":str(target)}
            await ws.send(json.dumps(params))
            
            pid = None
            while True:
                m2 = json.loads(await ws.recv())
                if m2.get("msg_type") == "proposal":
                    if "error" not in m2:
                        pid = m2["proposal"]["id"]
                        ask = m2["proposal"]["ask_price"]
                        payout = m2["proposal"]["payout"]
                    break
            if not pid: continue
            
            # BUY
            await ws.send(json.dumps({"buy":pid,"price":1.0}))
            cid = None
            while True:
                m3 = json.loads(await ws.recv())
                if m3.get("msg_type") == "buy":
                    if "error" not in m3:
                        cid = m3["buy"]["contract_id"]
                    break
            if not cid: continue
            
            # SUBSCRIBE + WAIT
            await ws.send(json.dumps({"proposal_open_contract":1,"contract_id":cid,"subscribe":1}))
            while True:
                m4 = json.loads(await ws.recv())
                if m4.get("msg_type") == "proposal_open_contract":
                    poc = m4["proposal_open_contract"]
                    if poc.get("status")=="sold" or poc.get("is_sold"):
                        pf = poc.get("profit",0)
                        exit_digit = int(str(int(poc.get("exit_spot",0)))[-1]) if poc.get("exit_spot") else -1
                        trades += 1
                        if pf > 0: wins += 1
                        profit += pf
                        outcome = "✅" if pf > 0 else "❌"
                        print(f"  {outcome}#{trades}: {pf:+.4f}$ | target={target}({freq[target]}%) exit={exit_digit} | ask={ask} payout={payout}", flush=True)
                        break
        
        wr = (wins/trades*100) if trades else 0
        print(f"\n{'='*50}", flush=True)
        print(f"📊 DIGITDIFF STAT — {trades} trades", flush=True)
        print(f"   WR: {wr:.1f}% ({wins}/{trades})", flush=True)
        print(f"   P&L: {profit:+.2f}$", flush=True)
        print(f"   Gain moyen: {profit/trades:+.4f}$" if trades else "", flush=True)
        print(f"{'='*50}", flush=True)

asyncio.run(main())
