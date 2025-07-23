import dash
from dash import Output, Input, State, callback_context
import plotly.graph_objs as go
from data_utils import load_data_from_json, process_klines_data
from analysis_tools import find_resistance_levels, load_prices_from_json


def register_callbacks(app):
    @app.callback(
        [Output("historical-graph", "figure"),
         Output("popup-message", "style"),
         Output("popup-interval", "disabled"),
         Output("popup-interval", "n_intervals")],
        [Input("reload-button", "n_clicks"),
         Input("popup-interval", "n_intervals"),
         Input("toggle-resistances", "n_clicks")],  # Nouveau bouton
        [State("popup-message", "style")],
    )
    def update_graph_and_popup(n_clicks, n_intervals, resistance_clicks, current_style):
        ctx = callback_context

        # Charger les données
        klines = load_data_from_json()
        times, prices = process_klines_data(klines)

        # Figure de base
        fig = go.Figure(data=[
            go.Scatter(x=times, y=prices, mode="lines+markers", name="Prix")
        ])
        fig.update_layout(
            xaxis_title="Temps",
            yaxis_title="Prix (USDT)",
            template="plotly_white"
        )

        # Gestion des droites de résistances
        if resistance_clicks and resistance_clicks % 2 == 1:  # Clic impair -> afficher
            resistances = find_resistance_levels(prices, n=5, precision=10)
            for r in resistances:
                fig.add_shape(
                    type="line",
                    x0=times[0],
                    x1=times[-1],
                    y0=r,
                    y1=r,
                    line=dict(color="green", width=2, dash="dot"),
                )

        # Détection de l’événement déclencheur
        if not ctx.triggered:
            # Au chargement
            return fig, {"display": "none"}, True, 0

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if triggered_id == "reload-button" and n_clicks > 0:
            style_show = {
                "display": "block",
                "position": "fixed",
                "top": "20px",
                "right": "20px",
                "background-color": "lightgreen",
                "padding": "10px",
                "border-radius": "5px",
                "box-shadow": "0 0 5px #333",
                "zIndex": 1000,
            }
            return fig, style_show, False, 0

        elif triggered_id == "popup-interval" and n_intervals == 1:
            return fig, {"display": "none"}, True, 0

        else:
            return fig, current_style, dash.no_update, dash.no_update
