import requests

# Vos clés API mémorisées
POLYGON_KEY = "RK23OMx4KO4Bku91FfHPRXI0VbchfGMD"
ALPHA_VANTAGE_KEY = "3HBNP1I3VVUBMY39"

# Actif à tester
ticker = "AAPL"

print(f"--- Lancement des tests pour l'actif : {ticker} ---\n")

# ==========================================
# TEST 1 : POLYGON.IO (Prix de clôture précédent)
# ==========================================
url_polygon = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?adjusted=true&apiKey={POLYGON_KEY}"

try:
    response_poly = requests.get(url_polygon)
    data_poly = response_poly.json()
    
    if response_poly.status_code == 200 and "results" in data_poly:
        # 'c' correspond au prix de clôture (Close price) dans l'API Polygon
        dernier_prix = data_poly["results"][0]["c"]
        print(f"[SUCCESS] Polygon.io fonctionne !")
        print(f" > Dernier prix de clôture pour {ticker} : {dernier_prix} USD\n")
    else:
        print(f"[ERREUR] Polygon.io : {data_poly.get('error', 'Erreur inconnue')}\n")
except Exception as e:
    print(f"[ERREUR] Connexion Polygon.io échouée : {e}\n")


# ==========================================
# TEST 2 : ALPHA VANTAGE (Données fondamentales)
# ==========================================
url_alpha = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_KEY}"

try:
    response_alpha = requests.get(url_alpha)
    data_alpha = response_alpha.json()
    
    # Vérification si l'API renvoie une erreur ou une limite de quota
    if "Note" in data_alpha:
        print("[INFO] Alpha Vantage : Limite de requêtes atteinte (25 par jour).")
        print(f" > Message de l'API : {data_alpha['Note']}\n")
    elif "Symbol" in data_alpha:
        nom_entreprise = data_alpha.get("Name", "Inconnu")
        ratio_pe = data_alpha.get("PERatio", "N/A")
        capitalisation = data_alpha.get("MarketCapitalization", "N/A")
        
        print(f"[SUCCESS] Alpha Vantage fonctionne !")
        print(f" > Nom de l'entreprise : {nom_entreprise}")
        print(f" > Ratio Cours/Bénéfice (P/E Ratio) : {ratio_pe}")
        print(f" > Capitalisation Boursière : {capitalisation} USD\n")
    else:
        print(f"[ERREUR] Alpha Vantage : Données non reçues. Vérifiez la clé.\n")
except Exception as e:
    print(f"[ERREUR] Connexion Alpha Vantage échouée : {e}\n")

print("--- Fin du test ---")

