#!/usr/bin/env python3
"""🧪 DIGITDIFF STAT v2 — Stratégie fréquence des chiffres sur R_100
Le digit = dernier chiffre de la partie entière du prix.
Ex: 270.85 → int=270 → dernier="0" → digit=0
Le prix bouge de ~0.1-0.5 par tick, donc le digit change rarement.
DIGITDIFF sur un digit lointain = quasi sûr de gagner.
"""
import asyncio, json, websockets
from collections import deque
from _token import AK, WS

async def run_test(max_trades=30):
    print("🔌 Connexion...", flush=True)
    async with websockets.connect(WS, ping_interval=10) as ws:
        await ws.send(json.dumps({"authorize": AK}))
        r = json.loads(await ws.recv())
        bal = r.get("authorize",{}).get("balance",0)
        print(f"✅ Solde: ${bal}", flush=True)
        await ws.send(json.dumps({"ticks": "R_100"}))
        
        digits = deque(maxlen=100)
        trades = wins = profit = 0
        
        # Collecter les 100 premiers ticks
        print("📊 Collecte initiale...", flush=True)
        while len(digits) < 100:
            raw = await ws.recv()
            m = json.loads(raw)
            if "tick" not in m: continue
            price = m["tick"]["quote"]
            digit = int(str(int(price))[-1])
            digits.append(digit)
        
        freq = {i: list(digits).count(i) for i in range(10)}
        current_range = f"{int(price)}"  # ex: "270", le dernier char = digit actuel
        print(f"   Prix ≈ {price:.2f} | Digit actuel: {current_range[-1]}", flush=True)
        print(f"   Distribution: {freq}", flush=True)
        
        # Trading loop
        while trades < max_trades:
            raw = await ws.recv()
            m = json.loads(raw)
            if "tick" not in m: continue
            
            price = m["tick"]["quote"]
            curr_digit = int(str(int(price))[-1])
            digits.append(curr_digit)
            
            # Mise à jour fréquence
            freq = {i: list(digits).count(i) for i in range(10)}
            
            # Chercher un digit ≤4% ET différent du digit actuel
            target = None
            for d in range(10):
                if freq[d] <= 4 and d != curr_digit:
                    target = d
                    break
            
            if target is None:
                continue  # pas de target, attendre
            
            # PROPOSAL DIGITDIFF
            params = {"proposal":1,"amount":1.0,"basis":"stake",
                      "contract_type":"DIGITDIFF","currency":"USD",
                      "duration":1,"duration_unit":"t","symbol":"R_100",
                      "barrier":str(target)}
            await ws.send(json.dumps(params))
            
            pid = ask = payout = None
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
                        # Récupérer le digit de sortie
                        exit_val = poc.get("exit_tick_display_value") or poc.get("sell_spot_display_value") or 0
                        exit_digit = int(str(int(float(exit_val)))[-1]) if exit_val else -1
                        
                        trades += 1
                        if pf > 0: wins += 1
                        profit += pf
                        icon = "✅" if pf > 0 else "❌"
                        print(f"  {icon}#{trades}: {pf:+.4f}$ | target={target}({freq[target]}%) | "
                              f"curr={curr_digit} exit={exit_digit} | profit={payout-1:.3f}$", flush=True)
                        break
        
        wr = (wins/trades*100) if trades else 0
        print(f"\n{'='*50}", flush=True)
        print(f"📊 DIGITDIFF STAT — {trades} trades", flush=True)
        print(f"   WR: {wr:.1f}% ({wins}/{trades})", flush=True)
        print(f"   P&L: {profit:+.2f}$", flush=True)
        print(f"   Gain moyen: {profit/trades:+.4f}$" if trades else "", flush=True)
        print(f"   Meilleur payout observé: ~{payout if payout else '?'}", flush=True)
        print(f"{'='*50}", flush=True)
        
        return {"trades": trades, "wins": wins, "profit": profit, "wr": wr}

if __name__ == "__main__":
    asyncio.run(run_test(30))
