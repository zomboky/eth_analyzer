# === Import des modules nécessaires ===
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Import des fonctions internes du projet
from callbacks import register_callbacks  # Pour enregistrer les interactions
from analysis_tools import load_prices_from_json, calculate_macd, create_macd_figure

# === Initialisation de l'application Dash ===
app = dash.Dash(__name__)

# === Définition du layout principal de l'application ===
app.layout = html.Div([

    # ✅ 1. Statut MACD (affiché au-dessus des graphes)
    html.Div(
        id="macd-status",
        style={
            "textAlign": "center",
            "fontSize": "20px",
            "marginTop": "10px",
            "color": "gray",
            "fontStyle": "italic"
        }
    ),

    html.H2("Historique des prix ETHUSDT sur la dernière journée"),

    # ✅ 2. Boutons d'action
    html.Div([
        html.Button("Recharger les données", id="reload-button", n_clicks=0),
        html.Button("Droites de résistances", id="toggle-resistances", n_clicks=0),
    ], style={"margin-bottom": "10px"}),

    # ✅ 3. Conteneur des sliders (pour configurer l'analyse des résistances)
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

            html.Label("Précision (1-20)"),
            html.Div(
                dcc.Slider(
                    id="precision-slider",
                    min=1,
                    max=20,
                    step=1,
                    value=10,
                    marks={i: str(i) for i in range(1, 21)},
                ),
                style={"width": "400px", "margin-bottom": "20px"}
            ),
        ],
        style={"display": "none", "margin-top": "10px"}  # Caché par défaut
    ),

    # ✅ 4. Graphiques (historique des prix et indicateur MACD)
    dcc.Graph(id="historical-graph"),  # Graphe principal des prix
    dcc.Graph(id="macd-graph"),        # Graphe MACD

    # ✅ 5. Intervalle automatique de mise à jour (toutes les 60 secondes)
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000,  # 60 secondes
        n_intervals=0,
        max_intervals=-1     # Infini
    ),

    # ✅ 6. Popup de confirmation (apparaît brièvement après mise à jour)
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

    # ✅ 7. Intervalle pour masquer le popup après 2 secondes
    dcc.Interval(
        id="popup-interval",
        interval=2000,
        n_intervals=0,
        max_intervals=1,
        disabled=True
    ),
])

# === Enregistrement des callbacks (interactions) dans l'app ===
register_callbacks(app)

# === Lancement de l'application (uniquement si ce fichier est exécuté directement) ===
if __name__ == "__main__":
    app.run(debug=True)
