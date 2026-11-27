#!/usr/bin/env python3
"""
🧪 STRATEGY TESTER v3 — Robuste, messages debug, cycle trade complet
"""
import asyncio, json, time, websockets
from collections import deque

TOKEN = "syVTPuwjbZ5zaru"
APP_ID = 1089
WS_URL = f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}"

class Trade:
    """Représente un trade et suit son cycle de vie"""
    def __init__(self, ws):
        self.ws = ws
        self.state = "IDLE"  # IDLE → PROPOSING → BUYING → IN_TRADE → DONE
        self.signal_type = None
        self.proposal_id = None
        self.contract_id = None
        self.profit = 0
        self.entry_spot = 0
        self.exit_spot = 0
        self.result = None

    async def propose(self, params):
        """Demande un prix pour un contrat"""
        self.signal_type = params.get("contract_type")
        self.state = "PROPOSING"
        await self.ws.send(json.dumps(params))

    async def buy(self, proposal_id, price):
        """Achète le contrat proposé"""
        self.proposal_id = proposal_id
        self.state = "BUYING"
        await self.ws.send(json.dumps({"buy": proposal_id, "price": price}))

    async def subscribe(self, contract_id):
        """S'abonne au contrat ouvert"""
        self.contract_id = contract_id
        self.state = "IN_TRADE"
        await self.ws.send(json.dumps({
            "proposal_open_contract": 1, "contract_id": contract_id, "subscribe": 1
        }))

    def handle_buy_response(self, msg):
        """Traite la réponse de buy"""
        if "error" in msg:
            print(f"    ❌ Buy refusé: {msg['error']['message']}")
            self.state = "IDLE"
            return False
        cid = msg["buy"]["contract_id"]
        price = msg["buy"]["buy_price"]
        print(f"    ✅ Acheté! Contract #{cid} à ${price}")
        return True

    def handle_contract_update(self, msg):
        """Traite une mise à jour du contrat ouvert"""
        poc = msg["proposal_open_contract"]
        if "contract" not in poc:
            return None
        
        c = poc["contract"]
        status = c.get("status", "")
        self.profit = c.get("profit", 0)
        self.entry_spot = c.get("entry_spot", 0)
        self.exit_spot = c.get("exit_spot", 0)
        
        if status == "sold" or c.get("is_sold") or c.get("is_expired"):
            self.result = "win" if self.profit > 0 else "loss"
            self.state = "DONE"
            return self.result
        
        return None


async def run_strategy_test(name, proposal_params_func):
    """Teste une stratégie: laisse tourner jusqu'à obtenir un trade complet"""
    print(f"\n{'='*55}")
    print(f"🧪 Test: {name}")
    print(f"{'='*55}")
    
    async with websockets.connect(WS_URL, ping_interval=20) as ws:
        # Auth
        await ws.send(json.dumps({"authorize": TOKEN}))
        resp = json.loads(await ws.recv())
        if "error" in resp:
            print(f"❌ Auth: {resp['error']['message']}")
            return None
        
        balance = resp.get("authorize", {}).get("balance", 0)
        print(f"✅ Connecté | Solde: ${balance}")
        
        # Subscribe ticks
        await ws.send(json.dumps({"ticks": "R_100"}))
        
        trade = Trade(ws)
        waiting_for_signal = True
        ticks_buffer = deque(maxlen=100)
        trade_count = 0
        wins = 0
        total_profit = 0.0
        max_trades = 5
        
        while trade_count < max_trades:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=60)
            except asyncio.TimeoutError:
                print("⏰ Timeout: pas de message reçu pendant 60s")
                break
            
            msg = json.loads(raw)
            
            # --- GESTION DES TICKS ---
            if "tick" in msg:
                tick = msg["tick"]
                ticks_buffer.append(tick["quote"])
                
                if waiting_for_signal and len(ticks_buffer) >= 30:
                    prices = list(ticks_buffer)
                    
                    # CALCUL DES INDICATEURS
                    ma5 = sum(prices[-5:]) / 5
                    ma20 = sum(prices[-20:]) / 20
                    
                    # RSI
                    g, l = 0, 0
                    for i in range(-14, 0):
                        d = prices[i] - prices[i-1]
                        if d > 0: g += d
                        else: l += abs(d)
                    rsi = 100 - (100 / (1 + g/l)) if l > 0 else 100
                    
                    # ANALYSE: priorité RSI extrême, sinon MA
                    signal = None
                    if rsi > 75:
                        signal = "PUT", f"RSI={rsi:.0f} (surachat)"
                    elif rsi < 25:
                        signal = "CALL", f"RSI={rsi:.0f} (survente)"
                    elif ma5 > ma20 * 1.0005:
                        signal = "CALL", f"MA5={ma5:.2f} > MA20={ma20:.2f}"
                    elif ma5 < ma20 * 0.9995:
                        signal = "PUT", f"MA5={ma5:.2f} < MA20={ma20:.2f}"
                    
                    if signal:
                        contract_type, reason = signal
                        print(f"\n🎯 Signal #{trade_count+1}: {contract_type} | {reason}")
                        await trade.propose(proposal_params_func(contract_type))
                        waiting_for_signal = False
            
            # --- GESTION PROPOSAL ---
            if trade.state == "PROPOSING" and "proposal" in msg:
                if "error" in msg:
                    print(f"    ❌ Proposal: {msg['error']['message']}")
                    trade.state = "IDLE"
                    waiting_for_signal = True
                    continue
                pid = msg["proposal"]["id"]
                ask = msg["proposal"]["ask_price"]
                payout = msg["proposal"]["payout"]
                print(f"    💰 Prix: {ask} | Payout: {payout}")
                await trade.buy(pid, 1.0)
            
            # --- GESTION BUY RESPONSE ---
            if trade.state == "BUYING" and "buy" in msg:
                if trade.handle_buy_response(msg):
                    cid = msg["buy"]["contract_id"]
                    await trade.subscribe(cid)
                else:
                    waiting_for_signal = True
            
            # --- SUIVI CONTRAT ---
            if trade.state == "IN_TRADE" and "proposal_open_contract" in msg:
                result = trade.handle_contract_update(msg)
                if result == "win":
                    trade_count += 1
                    wins += 1
                    total_profit += trade.profit
                    print(f"    ✅ Trade #{trade_count} GAGNÉ: {trade.profit:+.2f}$ (entrée: {trade.entry_spot}, sortie: {trade.exit_spot})")
                    trade = Trade(ws)
                    waiting_for_signal = True
                    await asyncio.sleep(1)
                elif result == "loss":
                    trade_count += 1
                    total_profit += trade.profit
                    print(f"    ❌ Trade #{trade_count} PERDU: {trade.profit:+.2f}$ (entrée: {trade.entry_spot}, sortie: {trade.exit_spot})")
                    trade = Trade(ws)
                    waiting_for_signal = True
                    await asyncio.sleep(1)
                elif result is None:
                    # Contrat toujours en cours
                    if "tick" in msg:  # seulement si tick aussi présent (message combiné)
                        pass
        
        return {
            "name": name,
            "trades": trade_count,
            "wins": wins,
            "losses": trade_count - wins,
            "win_rate": (wins / trade_count * 100) if trade_count else 0,
            "profit": total_profit
        }


async def main():
    print("""
╔══════════════════════════════════════════╗
║  🧪 DERIV STRATEGY TESTER v3             ║
║  Test simple: signaux RSI + MA           ║
║  Compte démo R_100 | Contrats 1 minute   ║
╚══════════════════════════════════════════╝
""")
    
    def params_1m(signal):
        return {"proposal": 1, "amount": 1.0, "basis": "stake",
                "contract_type": signal, "currency": "USD",
                "duration": 1, "duration_unit": "m", "symbol": "R_100"}
    
    result = await run_strategy_test("RSI+MA Combo (1 min CALL/PUT)", params_1m)
    
    if result:
        print(f"\n{'='*55}")
        print(f"📊 RÉSULTATS FINAUX")
        print(f"{'='*55}")
        print(f"  Stratégie: {result['name']}")
        print(f"  Trades: {result['trades']}")
        print(f"  Win Rate: {result['win_rate']:.1f}%")
        print(f"  P&L: {result['profit']:+.2f}$")
        print(f"  Score: {'✅ RENTABLE' if result['profit'] > 0 else '❌ NON RENTABLE'}")

if __name__ == "__main__":
    asyncio.run(main())
