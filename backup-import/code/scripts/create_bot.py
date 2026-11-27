#!/usr/bin/env python3
"""Crée un nouveau bot Telegram via @BotFather"""
import asyncio, aiohttp, json, re
from _tg import TG_BOT

BASE = f"https://api.telegram.org/bot{TG_BOT}"
BOTFATHER = "@BotFather"

async def send_message(text, reply_to=None):
    """Envoie un message à BotFather"""
    data = {"chat_id": BOTFATHER, "text": text}
    async with aiohttp.ClientSession() as s:
        async with s.post(f"{BASE}/sendMessage", json=data) as r:
            return await r.json()

async def get_updates(offset=0, timeout=30):
    """Récupère les messages de BotFather"""
    import time
    start = time.time()
    while time.time() - start < 60:
        url = f"{BASE}/getUpdates?offset={offset}&timeout={timeout}&allowed_updates=[\"message\"]"
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                data = await r.json()
                if data.get("ok") and data["result"]:
                    return data["result"]
        await asyncio.sleep(0.5)
    return None

async def create_bot():
    print("📡 Connexion à @BotFather...", flush=True)
    
    # Get initial offset
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{BASE}/getUpdates?offset=-1") as r:
            data = await r.json()
            if data.get("ok") and data["result"]:
                last_id = data["result"][-1]["update_id"]
            else:
                last_id = 0
    
    # Step 1: /newbot
    print("📤 Envoi /newbot...", flush=True)
    await send_message("/newbot")
    await asyncio.sleep(2)
    
    updates = await get_updates(last_id + 1)
    if updates:
        for u in updates:
            last_id = max(last_id, u["update_id"])
            msg = u.get("message", {})
            text = msg.get("text", "")
            if "Alright" in text or "name" in text.lower():
                print(f"✅ BotFather: {text[:100]}...", flush=True)
    
    # Step 2: Bot name
    bot_name = "Mudimba Trading Bot"
    print(f"📤 Envoi nom: {bot_name}", flush=True)
    await send_message(bot_name)
    await asyncio.sleep(2)
    
    updates = await get_updates(last_id + 1)
    if updates:
        for u in updates:
            last_id = max(last_id, u["update_id"])
            msg = u.get("message", {})
            text = msg.get("text", "")
            if "username" in text.lower() or "choose" in text.lower():
                print(f"✅ BotFather: {text[:100]}...", flush=True)
    
    # Step 3: Bot username
    bot_username = "mudimba_trading_bot"
    print(f"📤 Envoi username: {bot_username}", flush=True)
    await send_message(bot_username)
    await asyncio.sleep(3)
    
    updates = await get_updates(last_id + 1)
    token = None
    if updates:
        for u in updates:
            last_id = max(last_id, u["update_id"])
            msg = u.get("message", {})
            text = msg.get("text", "")
            print(f"📥 Response: {text[:200]}", flush=True)
            # Extract token
            m = re.search(r'(\d{8,10}:[A-Za-z0-9_-]{30,45})', text)
            if m:
                token = m.group(1)
    
    if token:
        print(f"\n🎉 BOT CRÉÉ !")
        print(f"Token: {token}")
        print(f"Username: @{bot_username}")
        # Save to file
        with open("_tg_trading.py", "w") as f:
            f.write(f'TG_TRADING="{token}"\n')
        print(f"✅ Token sauvegardé dans _tg_trading.py")
    else:
        print("❌ Impossible d'extraire le token")
        # Dump all updates for debugging
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{BASE}/getUpdates?offset={last_id-5}&limit=10") as r:
                data = await r.json()
                if data.get("ok"):
                    for u in data["result"]:
                        print(f"  Update: {json.dumps(u, indent=2)[:300]}")

asyncio.run(create_bot())
