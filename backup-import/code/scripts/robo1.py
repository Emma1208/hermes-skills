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

# Variables de suivi en temps réel
POSITION_REELLE = {"active": False, "id": None, "type": None, "profit": 0.0}
historique_prix = []
derniere_tendance = "NEUTRE"

# ==================== FONCTIONS TELEGRAM ====================

# Rapport minute basé sur tes VRAIES positions ouvertes
async def rapport_toutes_les_minutes():
    while True:
        await asyncio.sleep(60)
        if POSITION_REELLE["active"]:
            msg = (f"🤖 **RAPPORT PORTEFEUILLE V10**\n\n"
                   f"📈 Position détectée : *{POSITION_REELLE['type']}*\n"
                   f"🆔 ID Contrat : `{POSITION_REELLE['id']}`\n"
                   f"💰 Gains/Pertes en direct : *{POSITION_REELLE['profit']}$*\n"
                   f"⚡ Statut : Je surveille le marché 24h/24...")
        else:
            msg = "🤖 **RAPPORT PORTEFEUILLE V10**\n\n💤 Aucune position active détectée sur ton compte Deriv. J'attends que tu passes un ordre sur ton mobile !"
        
        try:
            bot.send_message(MY_CHAT_ID, msg, parse_mode="Markdown")
        except Exception as e:
            print(f"Erreur envoi Telegram : {e}")

# Alerte si le marché se retourne contre ta position ouverte
def alerte_changement_direction(nouvelle_direction):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("🔴 COUPER LE TRADE MAINTENANT", callback_data=f"fermer_{POSITION_REELLE['id']}"))
    
    msg = (f"🚨 **ATTENTION BOSS ! CHANGEMENT DE DIRECTION !**\n\n"
           f"Tu as un trade de **{POSITION_REELLE['type']}** en cours.\n"
           f"Mais le marché V10 vient de se retourner et passe : **{nouvelle_direction}** 📉\n\n"
           f"Gains actuels : {POSITION_REELLE['profit']}$\n"
           f"Tu veux que je ferme la position ?")
    
    try:
        bot.send_message(MY_CHAT_ID, msg, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        print(f"Erreur envoi alerte : {e}")

# Gestion du bouton de fermeture d'urgence
@bot.callback_query_handler(func=lambda call: True)
def gestion_boutons(call):
    if "fermer_" in call.data:
        contract_id = call.data.split("_")[1]
        bot.answer_callback_query(call.id, "Demande de fermeture envoyée...")
        # L'ordre de fermeture sera envoyé via la boucle principale
        asyncio.run_coroutine_threadsafe(fermer_position_deriv(contract_id), loop_principal)

async def fermer_position_deriv(contract_id):
    url = "wss://ws.derivws.com/websockets/v3?app_id=1089"
    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps({"authorize": DERIV_TOKEN}))
        await websocket.recv()
        # Envoyer l'ordre de vente (sell) du contrat ouvert
        await websocket.send(json.dumps({"sell": int(contract_id), "price": 0}))
        response = json.loads(await websocket.recv())
        if "error" in response:
            bot.send_message(MY_CHAT_ID, f"❌ Erreur lors de la fermeture : {response['error']['message']}")
        else:
            bot.send_message(MY_CHAT_ID, "🔴 **Position fermée avec succès !**")

# ==================== STRATÉGIE ET SYNCHRONISATION DERIV ====================

def analyser_tendance(prix_actuel):
    global historique_prix, derniere_tendance
    historique_prix.append(prix_actuel)
    if len(historique_prix) > 30:
        historique_prix.pop(0)
    if len(historique_prix) < 15:
        return "NEUTRE"
        
    moyenne_rapide = sum(historique_prix[-5:]) / 5
    moyenne_lente = sum(historique_prix[-15:]) / 15
    
    if moyenne_rapide > moyenne_lente:
        return "HAUSSIERE"
    elif moyenne_rapide < moyenne_lente:
        return "BAISSIERE"
    return "NEUTRE"

async def connexion_deriv_et_surveillance():
    global POSITION_REELLE
    url = "wss://ws.derivws.com/websockets/v3?app_id=1089"
    
    async with websockets.connect(url) as websocket:
        # Connexion au compte
        await websocket.send(json.dumps({"authorize": DERIV_TOKEN}))
        await websocket.recv()
        
        # S'abonner aux mouvements du V10
        await websocket.send(json.dumps({"ticks": "R_10"}))
        
        # S'abonner aux contrats/positions ouverts sur le compte en temps réel
        await websocket.send(json.dumps({"proposal_open_contract": 1, "subscribe": 1}))
        
        bot.send_message(MY_CHAT_ID, "🤖 **Copilote V10 Connecté !**\n\nOuvre un trade quand tu veux sur ton application Deriv Mobile, je vais le détecter immédiatement.")
        
        while True:
            msg = json.loads(await websocket.recv())
            
            # 1. Gestion et synchronisation des positions réelles (Multiplicateurs compris)
            if "proposal_open_contract" in msg and "contract" in msg["proposal_open_contract"]:
                contract_info = msg["proposal_open_contract"]["contract"]
                
                # Si le contrat est encore ouvert
                if contract_info["status"] == "open":
                    POSITION_REELLE["active"] = True
                    POSITION_REELLE["id"] = contract_info["contract_id"]
                    POSITION_REELLE["type"] = "ACHAT (Call)" if contract_info["contract_type"] == "CALL" else "VENTE (Put)"
                    POSITION_REELLE["profit"] = contract_info["profit"]
                else:
                    # Si le contrat vient de se fermer (par toi ou par un stop loss/take profit)
                    POSITION_REELLE = {"active": False, "id": None, "type": None, "profit": 0.0}
            
            # 2. Analyse des prix et détection du retournement
            if "tick" in msg:
                prix_actuel = msg["tick"]["quote"]
                tendance_actuelle = analyser_tendance(prix_actuel)
                
                # Alerte de sortie intelligente si la tendance change
                if POSITION_REELLE["active"]:
                    if (POSITION_REELLE["type"] == "ACHAT (Call)" and tendance_actuelle == "BAISSIERE") or \
                       (POSITION_REELLE["type"] == "VENTE" and tendance_actuelle == "HAUSSIERE"):
                        if derniere_tendance != tendance_actuelle:
                            alerte_changement_direction(tendance_actuelle)
                
                derniere_tendance = tendance_actuelle
                
            await asyncio.sleep(0.1)

# ==================== DÉMARRAGE ====================

def main():
    global loop_principal
    import threading
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    
    loop_principal = asyncio.get_event_loop()
    loop_principal.create_task(rapport_toutes_les_minutes())
    loop_principal.run_until_complete(connexion_deriv_et_surveillance())

if __name__ == "__main__":
    main()

