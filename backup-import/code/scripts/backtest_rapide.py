#!/usr/bin/env python3
"""
🧪 DERIV BACKTEST RAPIDE — Contrats 1 tick (DIGITDIFF / DIGITMATCH)
Les trades durent 1 tick (~1s) — pas de timeout connexion.
"""
import asyncio, json, websockets
from collections import deque

TOKEN = "syVTPuwjbZ5zaru"
WS_URL = "wss://ws.derivws.com/websockets/v3?app_id=1089"

# ======== STRATÉGIES À TESTER ========

STRATEGIES = []

def strat_digit_under():
    """DigitDiff: acheter quand un digit est sous-représenté (< 5% sur 100 ticks)"""
    name = "DigitDiff (<5% sur 100)"
    async def signal(ticks, current_price):
        if len(ticks) < 100:
            return None
        current_digit = int(str(int(current_price))[-1])
        stats = {i: list(ticks)[-100:].count(i) for i in range(10)}
        for d, count in stats.items():
            if (count / 100) * 100 < 5 and d != current_digit:
                return ("DIGITDIFF", {"contract_type": "DIGITDIFF", "barrier": str(d)})
        return None
    return name, signal

def strat_digit_match():
    """DigitMatch: acheter quand un digit apparaît 2+ fois dans les 3 derniers ticks"""
    name = "DigitMatch (récent pattern)"
    async def signal(ticks, current_price):
        if len(ticks) < 5:
            return None
        recent = list(ticks)[-3:]
        current_digit = int(str(int(current_price))[-1])
        for d in range(10):
            if recent.count(d) >= 2 and d != current_digit:
                return ("DIGITMATCH", {"contract_type": "DIGITMATCH", "barrier": str(d)})
        return None
    return name, signal

def strat_digit_over_under():
    """Over/Under: jouer contre le digit le plus fréquent"""
    name = "Digit Over/Under (mean reversion)"
    async def signal(ticks, current_price):
        if len(ticks) < 100:
            return None
        stats = {i: list(ticks)[-100:].count(i) for i in range(10)}
        most_common = max(stats, key=stats.get)
        pct = (stats[most_common] / 100) * 100
        if pct > 15:  # Un digit > 15% → reversion attendue
            return ("DIGITDIFF", {"contract_type": "DIGITDIFF", "barrier": str(most_common)})
        return None
    return name, signal

def strat_rise_fall_trend():
    """Rise/Fall: CALL si 5 ticks haussiers, PUT si baissiers - contrat 1 tick"""
    name = "Rise/Fall Trend (5 ticks)"
    async def signal(ticks, current_price):
        if len(ticks) < 10:
            return None
        recent = list(ticks)[-5:]
        if all(recent[i] < recent[i+1] for i in range(4)):
            return ("CALL", {"contract_type": "CALL"})
        if all(recent[i] > recent[i+1] for i in range(4)):
            return ("PUT", {"contract_type": "PUT"})
        return None
    return name, signal

STRATEGIES = [
    strat_digit_under(),
    strat_digit_match(),
    strat_digit_over_under(),
    strat_rise_fall_trend()
]

# ======== TESTEUR ========

async def test_strategy(name, signal_func):
    print(f"\n{'='*50}", flush=True)
    print(f"🧪 Test: {name}", flush=True)
    print(f"{'='*50}", flush=True)
    
    async with asyncio.timeout(20):
        async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=15) as ws:
            await ws.send(json.dumps({"authorize": TOKEN}))
            resp = json.loads(await ws.recv())
        if "error" in resp:
            print(f"❌ Auth: {resp['error']['message']}", flush=True)
            return
        
        # Subscribe ticks
        await ws.send(json.dumps({"ticks": "R_100"}))
        
        ticks = deque(maxlen=200)
        trades_done = 0
        wins = 0
        total_profit = 0.0
        max_trades = 20
        no_signal_count = 0
        
        while trades_done < max_trades and no_signal_count < 200:
            raw = await asyncio.wait_for(ws.recv(), timeout=30)
            msg = json.loads(raw)
            
            if "tick" in msg:
                price = msg["tick"]["quote"]
                ticks.append(price)
                
                # Chercher un signal
                sig = await signal_func(ticks, price)
                if sig:
                    no_signal_count = 0
                    contract_type, extra_params = sig
                    
                    # Construction de la requête proposal
                    params = {
                        "proposal": 1, "amount": 1.0, "basis": "stake",
                        "contract_type": contract_type, "currency": "USD",
                        "duration": 1, "duration_unit": "t", "symbol": "R_100"
                    }
                    params.update(extra_params)
                    
                    await ws.send(json.dumps(params))
                    
                    # Attendre la réponse proposal
                    while True:
                        raw2 = await asyncio.wait_for(ws.recv(), timeout=10)
                        msg2 = json.loads(raw2)
                        if msg2.get("msg_type") == "proposal":
                            if "error" in msg2:
                                break
                            pid = msg2["proposal"]["id"]
                            await ws.send(json.dumps({"buy": pid, "price": 1.0}))
                            break
                    
                    # Attendre la réponse buy + résultat du contrat (1 tick = très rapide)
                    while True:
                        raw3 = await asyncio.wait_for(ws.recv(), timeout=10)
                        msg3 = json.loads(raw3)
                        
                        # Résultat du contrat
                        if "proposal_open_contract" in msg3:
                            poc = msg3["proposal_open_contract"]
                            if "contract" in poc:
                                c = poc["contract"]
                                if c.get("status") == "sold" or c.get("is_sold"):
                                    trades_done += 1
                                    profit = c.get("profit", 0)
                                    entry = c.get("entry_spot", 0)
                                    exit_spot = c.get("exit_spot", 0)
                                    
                                    if profit > 0:
                                        wins += 1
                                    total_profit += profit
                                    
                                    icon = "✅" if profit > 0 else "❌"
                                    print(f"  {icon} #{trades_done}: {profit:+.2f}$ | {contract_type}"
                                          f" | E:{entry} S:{exit_spot}", flush=True)
                                    
                                    # Petite pause
                                    await asyncio.sleep(0.5)
                                    break
                        
                        # Buy response (avant le résultat)
                        if msg3.get("msg_type") == "buy":
                            if "error" in msg3:
                                break
                else:
                    no_signal_count += 1
        
        wr = (wins / trades_done * 100) if trades_done else 0
        pf = (wins / max(1, trades_done - wins)) if trades_done > wins else float('inf')
        
        print(f"\n📊 {name}", flush=True)
        print(f"   Trades: {trades_done}", flush=True)
        print(f"   WR: {wr:.0f}% ({wins}/{trades_done})", flush=True)
        print(f"   P&L: {total_profit:+.2f}$", flush=True)
        print(f"   PF: {pf:.2f}", flush=True)
        print(f"   Rentable: {'✅ OUI' if total_profit > 0 else '❌ NON'}", flush=True)
        
        return {"name": name, "trades": trades_done, "wins": wins, 
                "wr": wr, "pnl": total_profit, "pf": pf}


async def main():
    print("""
╔══════════════════════════════════════════════╗
║  🧪 DERIV STRATEGY BACKTEST                 ║
║  Contrats 1 tick sur R_100                   ║
║  Compte démo | 20 trades par stratégie       ║
╚══════════════════════════════════════════════╝
    """, flush=True)
    
    results = []
    for name, signal_func in STRATEGIES:
        r = await test_strategy(name, signal_func)
        if r:
            results.append(r)
    
    # Classement
    print(f"\n{'='*60}", flush=True)
    print(f"🏆 CLASSEMENT FINAL", flush=True)
    print(f"{'='*60}", flush=True)
    print(f"{'Stratégie':<35} {'Trades':<8} {'WR':<8} {'P&L':<10} {'PF':<8}", flush=True)
    print("-"*68, flush=True)
    ranked = sorted(results, key=lambda r: r["pnl"], reverse=True)
    for r in ranked:
        print(f"{r['name']:<35} {r['trades']:<8} {r['wr']:.0f}%{'':<5} {r['pnl']:+.2f}${'':<6} {r['pf']:<8.2f}", flush=True)
    
    if ranked:
        best = ranked[0]
        print(f"\n🥇 MEILLEURE: {best['name']}", flush=True)
        print(f"   WR: {best['wr']:.0f}% | P&L: {best['pnl']:+.2f}$ | PF: {best['pf']:.2f}", flush=True)


asyncio.run(main())
