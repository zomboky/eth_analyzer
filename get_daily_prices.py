import requests
from datetime import datetime
import json
import os

def get_daily_prices(symbol="ETHUSDC", interval="1m", limit=1440):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()

    prices = []
    for candle in data:
        timestamp = datetime.fromtimestamp(candle[0] / 1000)  # ouverture du chandelier
        close_price = float(candle[4])  # prix de clôture
        prices.append({"time": timestamp.isoformat(), "price": close_price})

    # Crée le dossier prices_history s'il n'existe pas
    os.makedirs("prices_history", exist_ok=True)

    # Nom du fichier basé sur la date du jour
    today = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join("prices_history", f"{today}.json")

    # Sauvegarde dans le fichier JSON
    with open(filename, "w") as f:
        json.dump(prices, f, indent=4)

    return prices


get_daily_prices(symbol="ETHUSDC", interval="1m", limit=1440)  # Exemple d'appel de la fonction