import dash
from dash import dcc, html
from callbacks import register_callbacks
import pandas as pd
from analysis_tools import load_prices_from_json, calculate_macd, create_macd_figure
from dash.dependencies import Input, Output
from dash import dcc
from dash import html



app = dash.Dash(__name__)

app.layout = html.Div([# Div contenant les boutons et les éléments pricipaux du HUD
    
    html.Div(  #Zone d'affichage du MACD
    id="macd-status",
    children="Chargement MACD...",
    style={
        "textAlign": "center",
        "fontSize": "20px",
        "marginTop": "10px",
        "color": "gray",
        "fontStyle": "italic"}),
    html.H2("Historique des prix ETHUSDT sur la dernière journée"),
    html.Div([
        html.Button("Recharger les données", id="reload-button", n_clicks=0),
        html.Button("Droites de résistances", id="toggle-resistances", n_clicks=0),
        html.Div(id="macd-status", style={
            "textAlign": "center",
            "fontWeight": "bold",
            "fontSize": "20px",
            "marginTop": "10px",
            "height": "30px",
            "color": "green", }),  #Couleur si avantageux

    ], style={"margin-bottom": "10px"}),

    # Div contenant les sliders (les sliders sont cachés par défaut et seront affichés au clic du bouton)
    html.Div(
        id="resistance-sliders-container",
        children=[
            html.Label("Nombre de droites (1-20)"),
            html.Div(
                dcc.Slider(
                    id="num-resistances-slider",
                    min=1,
                    max=20,
                    step=1,
                    value=5,
                    marks={i: str(i) for i in range(1, 21)},
                ),
                style={"width": "400px", "margin-bottom": "20px"}
            ),

            html.Label("Précision (1-50)"),
            html.Div(
                dcc.Slider(
                    id="precision-slider",
                    min=1,
                    max=20,
                    step=1,
                    value=10,
                    marks={i: str(i) for i in range(1, 21, 1)},
                ),
                style={"width": "400px", "margin-bottom": "20px"}
            ),
        ],
        style={"display": "none", "margin-top": "10px"}
    ),

    dcc.Graph(id="historical-graph"),  #Graphe des prix
    dcc.Graph(id="macd-graph"),        #Graphe des MACD
    dcc.Interval(                      #Update automatique du graphe toutes les 60 secondes
        id='interval-component',
        interval=60*1000,              # 60 000 ms = 60 secondes
        n_intervals=0,
        max_intervals=-1               # par défaut infini
),
    html.Div("Valeurs mises à jour !", id="popup-message", style={
        "display": "none",
        "position": "fixed",
        "top": "20px",
        "right": "20px",
        "background-color": "lightgreen",
        "padding": "10px",
        "border-radius": "5px",
        "box-shadow": "0 0 5px #333",
        "zIndex": 1000,
    }),
    dcc.Interval(id="popup-interval", interval=2000, n_intervals=0, max_intervals=1, disabled=True),
])

register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
