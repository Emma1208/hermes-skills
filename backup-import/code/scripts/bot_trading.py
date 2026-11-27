#!/usr/bin/env python3
"""
🤖 BOT TRADING DERIV — API Telegram directe
Pas de conflit getUpdates. Menu interactif + trading auto.
"""
import asyncio, json, aiohttp, time, threading, signal
from collections import deque, Counter
from _token import AK, WS
from _tg import TG_CHAT
from _tg_trading import TG_TRADING as TG_BOT

BASE = f"https://api.telegram.org/bot{TG_BOT}"
WS_URL = WS
LAST_UPDATE = 0

# ===== STATE =====
STATE = {
    "running": False, "mode": None, "balance": 0,
    "trades": 0, "wins": 0, "profit": 0.0,
    "stake": 1.0, "base_stake": 1.0,
    "loss_streak": 0, "max_streak": 0,
    "martingale": True, "freq_threshold": 2.0,
    "digit_history": deque(maxlen=100), "task": None,
}

# ===== TELEGRAM API =====
async def tg_call(method, data=None):
    """Appelle l'API Telegram"""
    url = f"{BASE}/{method}"
    async with aiohttp.ClientSession() as s:
        if data:
            async with s.post(url, json=data) as r:
                return await r.json()
        else:
            async with s.get(url) as r:
                return await r.json()

async def tg_send_to(chat_id, text, keyboard=None):
    """Envoie un message à un chat spécifique"""
    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if keyboard:
        data["reply_markup"] = keyboard
    return await tg_call("sendMessage", data)

async def tg_send(text, keyboard=None):
    return await tg_send_to(TG_CHAT, text, keyboard)

async def tg_edit(chat_id, msg_id, text, keyboard=None):
    """Édite un message"""
    data = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": "Markdown"}
    if keyboard:
        data["reply_markup"] = keyboard
    return await tg_call("editMessageText", data)

async def tg_get_updates():
    """Récupère les updates Telegram"""
    global LAST_UPDATE
    r = await tg_call(f"getUpdates?offset={LAST_UPDATE+1}&timeout=30")
    if r.get("ok") and r["result"]:
        for u in r["result"]:
            LAST_UPDATE = u["update_id"]
        return r["result"]
    return []

# ===== KEYBOARD =====
def main_keyboard():
    r = STATE["running"]
    return {
        "inline_keyboard": [
            [{"text": "▶️ DÉMARRER" if not r else "⏸️ STOP", "callback_data": "start" if not r else "stop"}],
            [
                {"text": "📊 DIGITDIFF 2%", "callback_data": "mode_digitdiff"},
                {"text": "🎯 CALL/PUT Mart.", "callback_data": "mode_callput"},
            ],
            [
                {"text": "💰 1$", "callback_data": "stake_1"},
                {"text": "💰 5$", "callback_data": "stake_5"},
                {"text": "💰 10$", "callback_data": "stake_10"},
            ],
            [
                {"text": "🔄 Mart: " + ("ON" if STATE["martingale"] else "OFF"), "callback_data": "toggle_mart"},
                {"text": "📊 Rapport", "callback_data": "report"},
            ],
        ]
    }

def status_text():
    wr = (STATE["wins"]/STATE["trades"]*100) if STATE["trades"] else 0
    return f"""🤖 **Bot Trading Deriv**

📊 **État**
• Mode: {'▶️ Actif' if STATE['running'] else '⏸️ Arrêté'}
• Stratégie: {'DIGITDIFF 2%' if STATE['mode']=='digitdiff' else 'CALL/PUT Mart.' if STATE['mode']=='callput' else 'Aucune'}
• Solde: ${STATE['balance']:.2f}

📈 **Performance**
• Trades: {STATE['trades']}
• Gains: {STATE['wins']} | WR: {wr:.1f}%
• P&L: {STATE['profit']:+.2f}$
• Streak: {STATE['loss_streak']} (max: {STATE['max_streak']})
• Stake: ${STATE['base_stake']:.0f} | Mart.: {'✅' if STATE['martingale'] else '❌'}"""

# ===== DERIV =====
async def deriv_ws_connect():
    """Connect via aiohttp WebSocket"""
    session = aiohttp.ClientSession()
    ws = await session.ws_connect(WS_URL)
    await ws.send_json({"authorize": AK})
    r = await ws.receive_json()
    STATE["balance"] = float(r.get("authorize", {}).get("balance", 0))
    await ws.send_json({"ticks": "R_100"})
    return ws, session

async def deriv_buy(ws, contract_type, amount, duration=1, unit="t"):
    """Achète un contrat Deriv"""
    await ws.send_json({
        "proposal": 1, "amount": amount, "basis": "stake",
        "contract_type": contract_type, "currency": "USD",
        "duration": duration, "duration_unit": unit, "symbol": "R_100"
    })
    while True:
        m = await ws.receive_json()
        if m.get("msg_type") == "proposal":
            if "error" in m: return None
            pid = m["proposal"]["id"]
            break
    await ws.send_json({"buy": pid, "price": amount})
    while True:
        m = await ws.receive_json()
        if m.get("msg_type") == "buy":
            if "error" in m: return None
            cid = m["buy"]["contract_id"]
            break
    await ws.send_json({"proposal_open_contract": 1, "contract_id": cid, "subscribe": 1})
    while True:
        m = await ws.receive_json()
        if m.get("msg_type") == "proposal_open_contract":
            poc = m["proposal_open_contract"]
            if poc.get("status") == "sold" or poc.get("is_sold"):
                return {"profit": poc.get("profit", 0), "entry": poc.get("entry_spot", 0), "exit": poc.get("exit_spot", 0)}
    return None

async def strategy_digitdiff(update_msg_id):
    """DIGITDIFF fréquence 2%"""
    ws, session = await deriv_ws_connect()
    STATE["running"] = True
    STATE["digit_history"].clear()
    
    while STATE["running"]:
        try:
            m = await asyncio.wait_for(ws.receive_json(), timeout=25)
        except asyncio.TimeoutError:
            await ws.send_json({"ping": 1})
            try: await asyncio.wait_for(ws.receive_json(), timeout=5)
            except: pass
            continue
        
        if "tick" not in m: continue
        
        prix = m["tick"]["quote"]
        digit = str(int(float(prix)))[-1] if type(prix) in (float, int) else str(prix)[-1]
        STATE["digit_history"].append(digit)
        
        if len(STATE["digit_history"]) < 50: continue
        
        counts = Counter(STATE["digit_history"])
        total = len(STATE["digit_history"])
        
        rare = None
        for d in "0123456789":
            if counts.get(d, 0)/total*100 <= STATE["freq_threshold"] and d != digit:
                rare = d; break
        
        if not rare: continue
        
        stake = STATE["base_stake"] * (2 ** STATE["loss_streak"]) if STATE["martingale"] else STATE["base_stake"]
        result = await deriv_buy(ws, "DIGITDIFF", min(stake, 100), 1, "t")
        
        if result:
            STATE["trades"] += 1
            if result["profit"] > 0:
                STATE["wins"] += 1; STATE["loss_streak"] = 0
            else:
                STATE["loss_streak"] += 1
                STATE["max_streak"] = max(STATE["max_streak"], STATE["loss_streak"])
            STATE["profit"] += result["profit"]
        
        await asyncio.sleep(0.3)
    
    await ws.close(); await session.close()

async def strategy_callput(update_msg_id):
    """CALL/PUT martingale"""
    ws, session = await deriv_ws_connect()
    STATE["running"] = True
    
    while STATE["running"]:
        try:
            m = await asyncio.wait_for(ws.receive_json(), timeout=25)
        except asyncio.TimeoutError:
            await ws.send_json({"ping": 1})
            try: await asyncio.wait_for(ws.receive_json(), timeout=5)
            except: pass
            continue
        
        if "tick" not in m: continue
        
        prix = m["tick"]["quote"]
        digit = str(int(float(prix)))[-1] if type(prix) in (float, int) else str(prix)[-1]
        STATE["digit_history"].append(digit)
        
        if len(STATE["digit_history"]) < 50: continue
        
        counts = Counter(STATE["digit_history"])
        total = len(STATE["digit_history"])
        
        rare = None
        for d in "0123456789":
            if counts.get(d, 0)/total*100 <= STATE["freq_threshold"] and d != digit:
                rare = d; break
        
        if not rare: continue
        
        direction = "CALL" if int(rare) > int(digit) else "PUT"
        stake = STATE["base_stake"] * (2 ** STATE["loss_streak"]) if STATE["martingale"] else STATE["base_stake"]
        result = await deriv_buy(ws, direction, min(stake, 100), 1, "t")
        
        if result:
            STATE["trades"] += 1
            if result["profit"] > 0:
                STATE["wins"] += 1; STATE["loss_streak"] = 0
            else:
                STATE["loss_streak"] += 1
                STATE["max_streak"] = max(STATE["max_streak"], STATE["loss_streak"])
            STATE["profit"] += result["profit"]
        
        await asyncio.sleep(0.3)
    
    await ws.close(); await session.close()

# ===== MAIN BOT LOOP =====
async def process_callback(data, msg_id, chat_id):
    """Traite un callback de bouton"""
    d = data
    
    if d == "start":
        if not STATE["mode"]:
            await tg_send("⚠️ Choisis d'abord une stratégie !")
            return
        if STATE["running"]:
            await tg_send("⚠️ Déjà en cours !")
            return
        STATE["trades"] = STATE["wins"] = 0
        STATE["profit"] = STATE["loss_streak"] = STATE["max_streak"] = 0
        if STATE["mode"] == "digitdiff":
            STATE["task"] = asyncio.create_task(strategy_digitdiff(msg_id))
        else:
            STATE["task"] = asyncio.create_task(strategy_callput(msg_id))
        await tg_send("🚀 Bot démarré !", main_keyboard())
    
    elif d == "stop":
        STATE["running"] = False
        if STATE["task"]: STATE["task"].cancel()
        await tg_send("⏸️ Bot arrêté.", main_keyboard())
    
    elif d == "mode_digitdiff":
        if STATE["running"]: await tg_send("⚠️ Arrête le bot d'abord !"); return
        STATE["mode"] = "digitdiff"
        await tg_send("📊 Mode: DIGITDIFF 2%\n⚠️ Stake fixe recommandé (Martingale inefficace)", main_keyboard())
    
    elif d == "mode_callput":
        if STATE["running"]: await tg_send("⚠️ Arrête le bot d'abord !"); return
        STATE["mode"] = "callput"
        await tg_send("🎯 Mode: CALL/PUT Martingale\n✅ Payout 1.92 — Martingale viable !", main_keyboard())
    
    elif d.startswith("stake_"):
        STATE["base_stake"] = float(d.split("_")[1])
        await tg_send(f"💰 Stake: ${STATE['base_stake']:.0f}", main_keyboard())
    
    elif d == "toggle_mart":
        STATE["martingale"] = not STATE["martingale"]
        await tg_send(f"🔄 Martingale: {'✅ ON' if STATE['martingale'] else '❌ OFF'}", main_keyboard())
    
    elif d == "report":
        await tg_send(status_text(), main_keyboard())

async def bot_loop():
    """Boucle principale du bot"""
    print("🤖 Bot Trading Deriv — en attente de /start", flush=True)
    
    chat_id = None
    msg_id = None
    
    while True:
        try:
            updates = await tg_get_updates()
            for u in updates:
                # Capture chat_id from first message
                msg = u.get("message") or u.get("callback_query", {}).get("message", {})
                if "chat" in msg:
                    chat_id = str(msg["chat"]["id"])
                
                if "callback_query" in u:
                    cq = u["callback_query"]
                    # Update chat_id from callback
                    if "message" in cq and "chat" in cq["message"]:
                        chat_id = str(cq["message"]["chat"]["id"])
                    await tg_call("answerCallbackQuery", {"callback_query_id": cq["id"]})
                    if msg_id:
                        await process_callback(cq["data"], msg_id, chat_id)
                        try:
                            await tg_edit(chat_id, msg_id, status_text(), main_keyboard())
                        except:
                            pass
                
                elif "message" in u:
                    msg = u["message"]
                    text = msg.get("text", "")
                    chat_id = str(msg["chat"]["id"])
                    if text == "/start":
                        # Send initial menu
                        r = await tg_send_to(chat_id, status_text(), main_keyboard())
                        if r.get("ok"):
                            msg_id = r["result"]["message_id"]
                            print(f"✅ Menu envoyé à {chat_id}", flush=True)
        
        except Exception as e:
            print(f"Bot loop error: {e}", flush=True)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(bot_loop())
