import dash
from dash import Output, Input, State, callback_context
import plotly.graph_objs as go
from data_utils import load_data_from_json, process_klines_data
from analysis_tools import find_resistance_levels

def register_callbacks(app):
    @app.callback(
        [Output("historical-graph", "figure"),
         Output("popup-message", "style"),
         Output("popup-interval", "disabled"),
         Output("popup-interval", "n_intervals"),
         Output("resistance-sliders-container", "style")],  # ajout du style des sliders
        [Input("reload-button", "n_clicks"),
         Input("popup-interval", "n_intervals"),
         Input("toggle-resistances", "n_clicks"),
         Input("num-resistances-slider", "value"),
         Input("precision-slider", "value")],  # ajout des sliders en entrée
        [State("popup-message", "style"),
         State("resistance-sliders-container", "style")]  # état actuel du conteneur sliders
    )
    def update_graph_and_popup(n_clicks, n_intervals, resistance_clicks,
                              num_resistances, precision,
                              current_style, current_slider_style):
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

        # Détection de l’événement déclencheur
        if not ctx.triggered:
            # Au chargement, sliders cachés
            return fig, {"display": "none"}, True, 0, {"display": "none"}

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Booléen pour savoir si sliders visibles
        sliders_visible = current_slider_style.get("display") == "block"

        # Gestion des droites de résistances + sliders
        if triggered_id == "toggle-resistances":
            # Toggle affichage sliders
            if sliders_visible:
                # Cacher sliders et ne pas afficher les droites
                return fig, current_style, True, 0, {"display": "none"}
            else:
                # Afficher sliders + droites avec valeurs courantes
                resistances = find_resistance_levels(prices, n=num_resistances, precision=precision)
                for r in resistances:
                    fig.add_shape(
                        type="line",
                        x0=times[0],
                        x1=times[-1],
                        y0=r,
                        y1=r,
                        line=dict(color="green", width=2, dash="dot"),
                    )
                return fig, current_style, True, 0, {"display": "block"}

        elif triggered_id in ["num-resistances-slider", "precision-slider"]:
            # Si sliders visibles, mettre à jour les droites quand sliders bougent
            if sliders_visible:
                resistances = find_resistance_levels(prices, n=num_resistances, precision=precision)
                for r in resistances:
                    fig.add_shape(
                        type="line",
                        x0=times[0],
                        x1=times[-1],
                        y0=r,
                        y1=r,
                        line=dict(color="green", width=2, dash="dot"),
                    )
                return fig, current_style, True, 0, current_slider_style
            else:
                # Si sliders cachés, ne rien changer (juste renvoyer)
                return fig, current_style, True, 0, current_slider_style

        elif triggered_id == "reload-button" and n_clicks > 0:
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
            # garder sliders cachés au rechargement
            return fig, style_show, False, 0, {"display": "none"}

        elif triggered_id == "popup-interval" and n_intervals == 1:
            return fig, {"display": "none"}, True, 0, current_slider_style

        else:
            return fig, current_style, dash.no_update, dash.no_update, current_slider_style
