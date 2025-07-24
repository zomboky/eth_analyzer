import requests  # Pour faire des requêtes HTTP vers l'API Binance
from datetime import datetime
import json
import os  # Pour gérer la création de dossiers

def get_daily_prices(symbol="ETHUSDC", interval="1m", limit=1440):
    """
    Récupère les prix historiques d'une crypto depuis Binance pour une journée complète en intervalles de 1 minute.

    Args:
        symbol (str): Le symbole du marché à interroger (ex: "ETHUSDC").
        interval (str): Intervalle de temps des bougies (ex: "1m").
        limit (int): Nombre de bougies à récupérer (max 1440 = 1 jour en 1 minute).

    Returns:
        list of dict: Liste de dictionnaires avec 'time' (ISO string) et 'price' (float).
    """
    
    # Construire l'URL pour la requête API Binance avec les paramètres donnés
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    
    # Envoyer la requête GET
    response = requests.get(url)
    response.raise_for_status()  # S'assurer que la requête a réussi (lève une erreur sinon)
    
    data = response.json()  # Récupérer la réponse au format JSON (liste de bougies)

    prices = []
    for candle in data:
        # candle est une liste avec plusieurs infos : [open_time, open, high, low, close, volume, ...]
        timestamp_ms = candle[0]  # Temps d'ouverture en millisecondes depuis epoch
        close_price_str = candle[4]  # Prix de clôture en string
        
        # Convertir timestamp en objet datetime
        timestamp = datetime.fromtimestamp(timestamp_ms / 1000)
        
        # Convertir le prix de clôture en float
        close_price = float(close_price_str)
        
        # Construire un dictionnaire simplifié avec heure ISO et prix
        prices.append({
            "time": timestamp.isoformat(),
            "price": close_price
        })

    # Créer le dossier 'prices_history' si il n'existe pas déjà (pour stocker les fichiers JSON)
    os.makedirs("prices_history", exist_ok=True)

    # Nommer le fichier selon la date du jour (ex: 2025-07-24.json)
    today = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join("prices_history", f"{today}.json")

    # Sauvegarder les prix dans ce fichier JSON, formaté pour être lisible
    with open(filename, "w") as f:
        json.dump(prices, f, indent=4)

    # Retourner la liste des prix pour un usage ultérieur dans le programme
    return prices

# Note : l'appel direct à la fonction est commenté pour éviter un appel automatique à l'import
# get_daily_prices(symbol="ETHUSDC", interval="1m", limit=1440)
