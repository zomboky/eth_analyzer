import json
from collections import Counter
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def load_prices_from_json(filename):
    """
    Charge une liste de prix à partir d'un fichier JSON.
    Le fichier JSON doit être une liste d'objets avec les clés "time" et "price".
    
    Args:
        filename (str): chemin vers le fichier JSON
    
    Returns:
        List[float]: liste des prix extraits
    """
    with open(filename, "r") as f:
        data = json.load(f)
    # Extraire la valeur float du champ "price" dans chaque entrée
    return [float(entry["price"]) for entry in data]

def find_resistance_levels(prices, n=5, precision=10):
    """
    Estime les niveaux de résistance sur une liste de prix.
    Les prix sont arrondis à une certaine précision pour regrouper les valeurs proches,
    puis on sélectionne les n valeurs les plus fréquentes comme résistances.
    
    Args:
        prices (List[float]): liste des prix
        n (int): nombre de niveaux de résistance à extraire (par défaut 5)
        precision (int or float): précision pour arrondir les prix (ex: 10 signifie arrondir à la dizaine)
        
    Returns:
        List[float]: niveaux de résistance estimés (arrondis)
    """
    # Arrondi des prix à la précision donnée pour regrouper les niveaux proches
    rounded_prices = [round(price / precision) * precision for price in prices]
    
    # Compte les occurrences de chaque niveau arrondi
    counter = Counter(rounded_prices)
    
    # Récupère les n niveaux les plus fréquents (niveau, nombre d'occurrences)
    most_common = counter.most_common(n)
    
    # Retourne uniquement les niveaux (sans les comptes)
    return [level for level, _ in most_common]

def calculate_macd(df, fast=12, slow=26, signal=9):
    """
    Calcule les indicateurs MACD à partir d'un DataFrame contenant une colonne 'price'.
    
    Args:
        df (pd.DataFrame): DataFrame avec une colonne "price"
        fast (int): période de la moyenne mobile exponentielle rapide (par défaut 12)
        slow (int): période de la moyenne mobile exponentielle lente (par défaut 26)
        signal (int): période pour la moyenne mobile exponentielle du signal (par défaut 9)
    
    Returns:
        pd.DataFrame: DataFrame enrichi avec les colonnes MACD (diff), DEA (signal) et Histogramme
    """
    # Calcul EMA rapide (fast)
    df["EMA_fast"] = df["price"].ewm(span=fast, adjust=False).mean()
    # Calcul EMA lente (slow)
    df["EMA_slow"] = df["price"].ewm(span=slow, adjust=False).mean()
    
    # Différence entre EMA rapide et lente = MACD (DIF)
    df["macd_diff"] = df["EMA_fast"] - df["EMA_slow"]
    # Moyenne mobile exponentielle du MACD, appelée signal ou DEA
    df["macd_dea"] = df["macd_diff"].ewm(span=signal, adjust=False).mean()
    # Histogramme = différence entre MACD et signal (DEA)
    df["Histogram"] = df["macd_diff"] - df["macd_dea"]

    df["price_diff"] = df["price"].diff() # La méthode Pandas "diff" calcule la différence entre une valeur et la précédente

    df["trend"] = df["price_diff"].apply( # Création d'une colonne "trend" dans le df pour catégoriser la tendance
        lambda x: "up" if x > 0 else ("down" if x < 0 else "flat"))
    
    return df

def create_macd_figure(df):
    """
    Crée une figure Plotly pour afficher le MACD avec DIF et DEA.
    
    Args:
        df (pd.DataFrame): DataFrame contenant les colonnes "time", "macd_diff", "macd_dea"
        
    Returns:
        plotly.graph_objs._figure.Figure: figure interactive Plotly
    """
    # Création d'un subplot simple
    fig = make_subplots(
        rows=1, cols=1, shared_xaxes=True,
        subplot_titles=("MACD",)
    )

    # Trace la courbe DIF (MACD)
    fig.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["macd_diff"],
            mode="lines",
            name="DIF (MACD)",
            line=dict(color="purple")
        ),
        row=1, col=1
    )
    
    # Trace la courbe DEA (signal)
    fig.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["macd_dea"],
            mode="lines",
            name="DEA (Signal)",
            line=dict(color="deeppink")
        ),
        row=1, col=1
    )

    # Mise en forme générale du graphique avec conservation du zoom
    fig.update_layout(
        height=400,
        template="plotly_white",
        title="Indicateur MACD (DIF & DEA)",
        margin=dict(t=40, b=40, l=40, r=40),
        legend=dict(orientation="h", y=-0.2),
        uirevision="macd-zoom"  # <- Ceci permet de garder le zoom/pan
    )
    fig.update_yaxes(title_text="MACD / Signal", row=1, col=1)

    return fig


# Note : L'exemple d'utilisation (chargement des prix, calcul des résistances, affichage des résultats)
# doit être placé dans un script principal, pas dans ce module, pour garder la modularité.

def classify_support_resistance(df, levels, seuil=0.03):
    close_prices = df['price'].values
    level_classification = {}

    for level in levels:
        support_count = 0
        resistance_count = 0
        neutral_count = 0

        for i in range(1, len(close_prices)-1):
            if abs(close_prices[i] - level) / level <= seuil:
                prev = close_prices[i - 1]
                curr = close_prices[i]
                nxt = close_prices[i + 1]

                if prev > level and nxt > level:
                    support_count += 1
                elif prev < level and nxt < level:
                    resistance_count += 1
                else:
                    neutral_count += 1

        if support_count > resistance_count and support_count > neutral_count:
            level_classification[level] = 'support'
        elif resistance_count > support_count and resistance_count > neutral_count:
            level_classification[level] = 'resistance'
        else:
            level_classification[level] = 'neutral'

    return level_classification


