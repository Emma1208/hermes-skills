#!/usr/bin/env python3
"""Capture the Telegram chat_id by listening to getUpdates.
1) Add the bot to the group AND promote to admin.
2) Send any message in that group.
3) Run: python3 get_chat_id.py   (listens ~40s)
Group IDs look like -100..., a DM is type 'private'.
"""
import json, time, urllib.request, urllib.parse

TOK = "8836960951:AAGJxe6cjyoE2DFMPHSLli-liaeBahETn6M"

def api(method, params=None, timeout=15):
    url = f"https://api.telegram.org/bot{TOK}/{method}"
    data = urllib.parse.urlencode(params or {}).encode()
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

try:
    api("deleteWebhook", {"drop_pending_updates": True})
except Exception:
    pass

print("Ecoute des messages... (envoie un msg dans le groupe avec le bot en admin)")
found = set(); deadline = time.time() + 40; offset = 0
while time.time() < deadline:
    try:
        upd = api("getUpdates", {"offset": offset, "timeout": 10}, timeout=12)
        for u in upd.get("result", []):
            offset = u["update_id"] + 1
            msg = u.get("message") or u.get("my_chat_member") or u.get("channel_post")
            if msg:
                cid = msg.get("chat", {}).get("id")
                ctype = msg.get("chat", {}).get("type")
                title = msg.get("chat", {}).get("title") or msg.get("chat", {}).get("username") or "?"
                if cid and cid not in found:
                    found.add(cid)
                    print(f"  -> chat_id: {cid}  (type={ctype}, titre={title})")
    except Exception as e:
        print("  (attente)", e)
    time.sleep(1)
print("\nCopie le chat_id dans crypto_signal_bot.py -> 'telegram_chat_id'" if found
      else "AUCUN chat_id. Verifie : bot admin du groupe + 1 message envoye.")
