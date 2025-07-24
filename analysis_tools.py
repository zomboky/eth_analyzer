import json
import numpy as np
from collections import Counter

import pandas as pd
import matplotlib.pyplot as plt

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




# Calcul du MACD
def calculate_macd(df, fast=12, slow=26, signal=9):
    df["EMA_fast"] = df["price"].ewm(span=fast, adjust=False).mean()
    df["EMA_slow"] = df["price"].ewm(span=slow, adjust=False).mean()
    df["macd_diff"] = df["EMA_fast"] - df["EMA_slow"]  # DIF
    df["macd_dea"] = df["macd_diff"].ewm(span=signal, adjust=False).mean()  # DEA
    df["Histogram"] = df["macd_diff"] - df["macd_dea"]
    return df


import plotly.graph_objs as go
from plotly.subplots import make_subplots

def create_macd_figure(df):
    fig = make_subplots(
        rows=1, cols=1, shared_xaxes=True,
        subplot_titles=("MACD",)
    )

    # Courbes DIF et DEA
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

    fig.update_layout(
        height=400,
        template="plotly_white",
        title="Indicateur MACD (DIF & DEA)",
        margin=dict(t=40, b=40, l=40, r=40),
        legend=dict(orientation="h", y=-0.2)
    )
    fig.update_yaxes(title_text="MACD / Signal", row=1, col=1)

    return fig
