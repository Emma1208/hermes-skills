import asyncio
import requests
import telebot

# ==================== CONFIGURATION SYNCHRONISÉE ====================
TELEGRAM_TOKEN = "8203899421:AAFDHwbu15m_KA7Kz6IfmrnYJikT8WxvOSg"
MY_CHAT_ID = "8131589581"

META_API_TOKEN = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2MTUxYTdmYzkwNTllNDYwYzFjMjNhMWZmNjc1MjE0MSIsImFjY2Vzc1J1bGVzIjpbeyJpZCI6InRyYWRpbmctYWNjb3VudC1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFhcGktcmVzdC1hcGkiLCJtZXRob2RzIjpbIm1ldGFhcGktYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFhcGktcnBjLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFhcGktcmVhbC10aW1lLXN0cmVhbWluZy1hcGkiLCJtZXRob2RzIjpbIm1ldGFhcGktYXBpOndzOnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtZXRhc3RhdHMtYXBpIiwibWV0aG9kcyI6WyJtZXRhc3RhdHMtYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6InJpc2stbWFuYWdlbWVudC1hcGkiLCJtZXRob2RzIjpbInJpc2stbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoiY29weWZhY3RvcnktYXBpIiwibWV0aG9kcyI6WyJjb3B5ZmFjdG9yeS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibXQtbWFuYWdlci1hcGkiLCJtZXRob2RzIjpbIm10LW1hbmFnZXItYXBpOnJlc3Q6zGVhbGluZzoqOioiLCJtdC1tYW5hZ2VyLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJiaWxsaW5nLWFwaSIsIm1ldGhvZHMiOlsiYmlsbGluZy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfV0sImlnbm9yZVJhdGVMaW1pdHMiOmZhbHNlLCJ0b2tlbklkIjoiMjAyMTAyMTMiLCJpbXBlcnNvbmF0ZWQiOmZhbHNlLCJyZWFsVXNlcklkIjoiNjE1MWE3ZmM5MDU5ZTQ2MGMxYzIzYTFmZjY3NTIxNDEiLCJpYXQiOjE3ODAxOTcyNTF9.HTTdwMmcLg9aJhIITtsvmC0Riuz3x4C2OuSUBQTFDO3X_BO89g9uDKpLZPi9gO7cctEbu4DlK_ufXUV3ApwJi4hdfy3BPtLkgnjxbIlK9LmtnlsDxWMiD6W40x-AvyEiWS2ltd8OOFRzxTEUO0Xaf2joRp5l1GN7kDYnnjuDY3y7ZCWFLDdIo-MYV-oEaLvx3AanXfzsIQqlU098gpBkAwE2BIM2jekbXXzOdzI0264DpxJ6z54ffN4aGWN0fm0jAhpFQyEr066D3KktRd2yajlkIuRENAhxkzmv46_-_MPRglTe3bDEgTvCZlhgtrbJfjYeGZJ0IL1dObvJxwaemwEUeipJvCR2CHXYuDZoPtKzJYRT8RKuZO9JQ1VeZIRAqO3XCWmbg3mY7w-h_yp_u0F4e5wj5525I4suaHiSEalqnraWM87VvKOz2LebGJ9v34wVOfxMFySF6mAdEPzvqtA0GVtt9FERGYYbM9GIOppfjmwKTJUZ2BP59hIU3LKuGLlYwbWQp3Y-EyrPzcIgo2AKNHqNtAArxXY6QgFrVhtn0G732XM27MRPGcuxdL1y_A1F1lUNgM1YohEi99hcI7rUHcvtXjg3n_4hIIYKp0io5zSl8ARdYQDxpdJ9C3VESPUxVaPgEG3K34YsksSzbPTjdCXK__cjZW5eonFYuGA"
META_ACCOUNT_ID = "6151a7fc9059e460c1c23a1ff6752141"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
LISTE_POSITIONS = []

# RETOUR SUR LE SERVEUR RECOMMANDÉ (NEW YORK / REST API STANDARD)
URL_API = f"https://mt-client-api-v1.new-york.agiliumtrade.ai/users/current/accounts/{META_ACCOUNT_ID}/positions"
HEADERS = {
    "auth-token": META_API_TOKEN,
    "Accept": "application/json"
}

def verifier_positions_xm():
    global LISTE_POSITIONS
    try:
        reponse = requests.get(URL_API, headers=HEADERS, timeout=15)
        print(f"📡 Analyse Flux VPN (NY) -> Statut : {reponse.status_code}")
        
        if reponse.status_code == 200:
            positions = reponse.json()
            LISTE_POSITIONS = []
            for p in positions:
                LISTE_POSITIONS.append({
                    "symbol": p.get("symbol", "Inconnu"),
                    "ticket": p.get("id", "N/A"),
                    "type": "ACHAT (Buy) 🍏" if p.get("type") == "POSITION_TYPE_BUY" else "VENTE (Sell) 🍎",
                    "profit": round(p.get("profit", 0.0), 2),
                    "lots": p.get("volume", 0.0)
                })
            print(f"📊 Trades actifs détectés : {len(LISTE_POSITIONS)}")
        else:
            print(f"⚠️ Code serveur : {reponse.status_code}")
    except Exception as e:
        print(f"❌ Échec de la liaison : {e}")

async def boucle_suivi_telegram():
    try:
        bot.send_message(MY_CHAT_ID, "🚀 **Copilote XM synchronisé sur la bonne région !**\n\nSurveillance opérationnelle en arrière-plan...")
    except:
        pass

    while True:
        verifier_positions_xm()
        
        if len(LISTE_POSITIONS) > 0:
            msg = "📈 **RAPPORT EN DIRECT (XM MT5)**\n\n"
            for pos in LISTE_POSITIONS:
                msg += (f"📊 Actif : *{pos['symbol']}*\n"
                        f"⚙️ Action : {pos['type']}\n"
                        f"🎚️ Lots : `{pos['lots']}`\n"
                        f"💰 Profit : *{pos['profit']}$*\n"
                        f"-------------------------\n")
        else:
            msg = "🤖 **RAPPORT MONITORING XM**\n\n💤 Aucun trade en cours détecté."
            
        try:
            bot.send_message(MY_CHAT_ID, msg, parse_mode="Markdown")
        except Exception as e:
            print(f"Erreur Telegram : {e}")
            
        await asyncio.sleep(60)

def main():
    print("Lancement final du moniteur XM...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(boucle_suivi_telegram())

if __name__ == "__main__":
    main()

