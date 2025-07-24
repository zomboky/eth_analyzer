import json
from datetime import datetime
from get_daily_prices import get_daily_prices  # Import de la fonction qui récupère et sauvegarde les prix

# Définir le nom du fichier JSON basé sur la date du jour au moment du lancement du script
today = datetime.now().strftime("%Y-%m-%d")
HISTORIC_JSON_FILE = f"prices_history/{today}.json"

def load_data_from_json(filename=HISTORIC_JSON_FILE):
    """
    Charge les données des prix depuis un fichier JSON. 
    
    Avant de charger, lance la récupération et sauvegarde des données actuelles via l'API Binance.

    Args:
        filename (str): Chemin du fichier JSON contenant les données.

    Returns:
        list of dict: Liste de dictionnaires {"time": str ISO, "price": float} extraites du fichier JSON.
    """
    # Mise à jour des données du jour dans le fichier JSON
    get_daily_prices(symbol="ETHUSDC", interval="1m", limit=1440)
    
    # Ouvre et charge le fichier JSON avec les prix enregistrés
    with open(filename, "r") as f:
        return json.load(f)


def process_klines_data(klines):
    """
    Transforme la liste de données brutes (dictionnaires {"time", "price"}) en listes séparées.

    Args:
        klines (list of dict): Liste d'éléments contenant "time" en ISO string et "price" float.

    Returns:
        tuple: (times, prices)
            times (list of datetime): liste des timestamps convertis en datetime objets.
            prices (list of float): liste des prix correspondants.
    """
    times = []
    prices = []
    for k in klines:
        # Convertir la chaîne ISO en datetime
        dt = datetime.fromisoformat(k["time"])
        # Convertir le prix en float (au cas où)
        price = float(k["price"])
        times.append(dt)
        prices.append(price)
    return times, prices


# Ancienne version sans récupération automatique, conservée en commentaire au cas où
# def load_data_from_json(filename=HISTORIC_JSON_FILE):
#     with open(filename, "r") as f:
#         return json.load(f)
