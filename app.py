import dash
from dash import dcc, html
from callbacks import register_callbacks
from analysis_tools import find_resistance_levels, load_prices_from_json


app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Historique des prix ETHUSDT sur la dernière journée"),
    html.Button("Recharger les données", id="reload-button", n_clicks=0),
    html.Button("Droites de résistances", id="toggle-resistances", n_clicks=0),
    dcc.Graph(id="historical-graph"),
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
