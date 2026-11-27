#!/usr/bin/env python3
"""
🤖 TREND BOT DERIV — Stratégie Trend 5 ticks
Trade automatique sur R_100, contrat 1 tick, mise 1$
Envoie rapport Telegram à chaque session
"""
import asyncio, json, websockets
from collections import deque
from datetime import datetime
from _token import AK as DERIV_TOKEN
from _tg import TG_BOT as BOT_TOKEN, TG_CHAT as CHAT_ID

# ==================== CONFIG ====================
SYMBOL = "R_100"
STAKE = 1.0
MAX_TRADES = 25
TIMEOUT = 360
WS_URL = "wss://ws.derivws.com/websockets/v3?app_id=1089"

# ==================== STRATÉGIE ====================
def signal(ticks, price):
    if len(ticks) < 5: return None
    last5 = list(ticks)[-5:]
    up = sum(1 for i in range(4) if last5[i] < last5[i+1])
    down = sum(1 for i in range(4) if last5[i] > last5[i+1])
    if up >= 4: return "CALL"
    if down >= 4: return "PUT"
    return None

# ==================== TELEGRAM ====================
async def tg(msg):
    try:
        import urllib.request
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = json.dumps({"chat_id": CHAT_ID, "text": msg}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"  TG: {e}", flush=True)

# ==================== TRADE ====================
async def do_trade(ws, ticks, n):
    while True:
        raw = await ws.recv()
        m = json.loads(raw)
        if "tick" not in m: continue
        p = m["tick"]["quote"]
        ticks.append(p)
        sig = signal(ticks, p)
        if not sig: continue
        
        # Proposal
        await ws.send(json.dumps({"proposal":1,"amount":STAKE,"basis":"stake",
            "contract_type":sig,"currency":"USD","duration":1,"duration_unit":"t","symbol":SYMBOL}))
        pid = None
        while True:
            m2 = json.loads(await ws.recv())
            if m2.get("msg_type") == "proposal":
                if "error" not in m2: pid = m2["proposal"]["id"]
                break
        if not pid: continue
        
        # Buy
        await ws.send(json.dumps({"buy":pid,"price":STAKE}))
        cid = None
        while True:
            m3 = json.loads(await ws.recv())
            if m3.get("msg_type") == "buy":
                if "error" not in m3: cid = m3["buy"]["contract_id"]
                break
        if not cid: continue
        
        # Subscribe + wait result
        await ws.send(json.dumps({"proposal_open_contract":1,"contract_id":cid,"subscribe":1}))
        while True:
            m4 = json.loads(await ws.recv())
            if m4.get("msg_type") == "proposal_open_contract":
                poc = m4["proposal_open_contract"]
                if poc.get("status")=="sold" or poc.get("is_sold"):
                    pf = poc.get("profit",0)
                    return {"n":n,"type":sig,"profit":pf,"result":"win" if pf>0 else "loss"}

# ==================== SESSION ====================
async def session():
    print(f"\n{'='*50}", flush=True)
    print(f"🤖 TREND BOT — {datetime.now().strftime('%Y-%m-%d %H:%M')}", flush=True)
    print(f"{'='*50}", flush=True)
    
    try:
        async with asyncio.timeout(TIMEOUT):
            async with websockets.connect(WS_URL, ping_interval=10) as ws:
                await ws.send(json.dumps({"authorize": DERIV_TOKEN}))
                r = json.loads(await ws.recv())
                if "error" in r:
                    await tg(f"❌ *TREND BOT* — Auth: {r['error']['message']}")
                    return
                
                bal_start = r.get("authorize",{}).get("balance",0)
                login = r.get("authorize",{}).get("loginid","?")
                print(f"✅ {login} ${bal_start}", flush=True)
                await ws.send(json.dumps({"ticks": SYMBOL}))
                
                ticks = deque(maxlen=200)
                done = []
                
                while len(done) < MAX_TRADES:
                    r = await do_trade(ws, ticks, len(done)+1)
                    if r:
                        done.append(r)
                        icon = "✅" if r["result"]=="win" else "❌"
                        print(f"  {icon}#{r['n']}: {r['profit']:+.2f}$ {r['type']}", flush=True)
                
                wins = sum(1 for t in done if t["result"]=="win")
                total = sum(t["profit"] for t in done)
                wr = wins/len(done)*100
                
                calls = [t for t in done if t["type"]=="CALL"]
                puts = [t for t in done if t["type"]=="PUT"]
                
                report = (
                    f"🤖 *TREND BOT — Session*\n"
                    f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                    f"📈 {SYMBOL} | 1 tick | ${STAKE}\n\n"
                    f"📊 *{len(done)} trades* | WR: *{wr:.0f}%*\n"
                    f"✅ {wins}W | ❌ {len(done)-wins}L\n"
                    f"💰 P&L: *{total:+.2f}$*\n"
                    f"📈 CALL: {len(calls)}t ({sum(1 for t in calls if t['result']=='win')/len(calls)*100 if calls else 0:.0f}%) | {sum(t['profit'] for t in calls):+.2f}$\n"
                    f"📉 PUT: {len(puts)}t ({sum(1 for t in puts if t['result']=='win')/len(puts)*100 if puts else 0:.0f}%) | {sum(t['profit'] for t in puts):+.2f}$\n"
                    f"💳 ${bal_start:.2f} → ${bal_start+total:.2f}\n"
                    f"{'✅ RENTABLE' if total>0 else '❌ NON RENTABLE'}"
                )
                
                print(f"\n{report}", flush=True)
                await tg(report)
    
    except asyncio.TimeoutError:
        await tg(f"⏰ *TREND BOT* — Timeout ({TIMEOUT}s)")
    except Exception as e:
        await tg(f"❌ *TREND BOT* — {type(e).__name__}: {e}")

async def main():
    await tg(f"🚀 *TREND BOT* — Lancement\n{MAX_TRADES} trades | ${STAKE} | {SYMBOL}")
    await session()
    print("🏁 Terminé", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
