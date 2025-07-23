import json
import numpy as np
from collections import Counter


def load_prices_from_json(filename):
    """Charge une liste de prix à partir d'un fichier JSON (format [{time, price}])"""
    with open(filename, "r") as f:
        data = json.load(f)
    return [float(entry["price"]) for entry in data]

def find_resistance_levels(prices, n=5, precision=10):

    # Arrondir les prix pour regrouper les valeurs proches
    rounded_prices = [round(price / precision) * precision for price in prices]
    
    # Compter les occurrences
    counter = Counter(rounded_prices)
    
    # Extraire les n prix les plus fréquents
    most_common = counter.most_common(n)
    return [level for level, _ in most_common]

prices = load_prices_from_json("prices_history/2025-07-23.json")
resistances = find_resistance_levels(prices, n=10, precision=1)
print("Niveaux de résistance estimés:", resistances)

