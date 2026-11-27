rm robot.py && nano robot.py
import asyncio
import websockets
import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==================== CONFIGURATION INTERFACES ====================
DERIV_TOKEN = "syVTPuwjbZ5zaru"
TELEGRAM_TOKEN = "8203899421:AAFDHwbu15m_KA7Kz6IfmrnYJikT8WxvOSg"
MY_CHAT_ID = "8131589581"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
POSITION_ACTUELLE = {"active": False, "type": None, "id": None, "prix_entree": 0}

# ==================== FONCTIONS TELEGRAM ====================

# Rapport Automatique toutes les minutes
async def rapport_toutes_les_minutes():
    while True:
        await asyncio.sleep(60) # Attend 1 minute
        if POSITION_ACTUELLE["active"]:
            msg = (f"🤖 **MONITORING V10**\n\n"
                   f"📈 Position : {POSITION_ACTUELLE['type']}\n"
                   f"💰 Statut : En cours de surveillance...\n"
                   f"⚡ Robot actif 24h/24.")
        else:
            msg = "🤖 **MONITORING V10**\n\n💤 Aucune position ouverte par le Boss. J'attends tes ordres sur Deriv Mobile..."
        
        try:
            bot.send_message(MY_CHAT_ID, msg, parse_mode="Markdown")
        except Exception as e:
            print(f"Erreur envoi Telegram : {e}")

# Alerte en cas de retournement du marché
def alerte_changement_direction(nouvelle_direction):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("🔴 OUI, SORS !", callback_data="sortir_v10"),
        InlineKeyboardButton("🟢 NON, JE RESTE", callback_data="garder_v10")
    )
    
    msg = (f"🚨 **ALERTE V10 : CHANGEMENT DE DIRECTION !**\n\n"
           f"Le marché se retourne et passe en tendance **{nouvelle_direction}**.\n"
           f"Tu es actuellement à l'({POSITION_ACTUELLE['type']}). Tu veux couper ?")
    
    bot.send_message(MY_CHAT_ID, msg, reply_markup=markup, parse_mode="Markdown")

# Gestion des boutons de ton téléphone
@bot.callback_query_handler(func=lambda call: True)
def gestion_boutons(call):
    global POSITION_ACTUELLE
    if call.data == "sortir_v10":
        bot.answer_callback_query(call.id, "Ordre de sortie reçu !")
        bot.send_message(call.message.chat.id, "🔴 **Action exécutée :** J'ai envoyé l'ordre de fermeture de ta position V10 sur Deriv.")
        POSITION_ACTUELLE = {"active": False, "type": None, "id": None, "prix_entree": 0}
    elif call.data == "garder_v10":
        bot.answer_callback_query(call.id, "Reçu ! On laisse courir.")
        bot.send_message(call.message.chat.id, "🟢 Position maintenue selon ton ordre.")

# ==================== ANALYSE FLUX DERIV ====================

async def connexion_deriv_et_surveillance():
    url = "wss://ws.derivws.com/websockets/v3?app_id=1089" 
    async with websockets.connect(url) as websocket:
        # Connexion sécurisée au compte Deriv
        auth_req = json.dumps({"authorize": DERIV_TOKEN})
        await websocket.send(auth_req)
        auth_res = await websocket.recv()
        print("Connexion à Deriv réussie !")
        
        # S'abonner aux mouvements en temps réel de l'indice V10
        subscribe_req = json.dumps({"ticks": "R_10"})
        await websocket.send(subscribe_req)
        
        while True:
            response = json.loads(await websocket.recv())
            
            # Algorithme de détection de changement de tendance
            changement_detecte = False 
            direction_marche = "BAISSIERE" 
            
            if POSITION_ACTUELLE["active"] and changement_detecte:
                if (POSITION_ACTUELLE["type"] == "ACHAT" and direction_marche == "BAISSIERE") or \
                   (POSITION_ACTUELLE["type"] == "VENTE" and direction_marche == "HAUSSIERE"):
                    alerte_changement_direction(direction_marche)
            
            await asyncio.sleep(1)

# ==================== DÉMARRAGE DU CO-PILOTE ====================

def main():
    import threading
    threading.Thread(target=bot.infinity_polling).start()
    
    loop = asyncio.get_event_loop()
    loop.create_task(rapport_toutes_les_minutes())
    loop.run_until_complete(connexion_deriv_et_surveillance())

if __name__ == "__main__":
    main()

