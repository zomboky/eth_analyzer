import dash
from dash import Output, Input, State, callback_context
import plotly.graph_objs as go
from data_utils import load_data_from_json, process_klines_data
from analysis_tools import find_resistance_levels, calculate_macd, create_macd_figure
import pandas as pd
import json

def register_callbacks(app):
    @app.callback(
        [Output("historical-graph", "figure"),
         Output("macd-graph", "figure"),                 # ** Nouveau Output pour le MACD **
         Output("popup-message", "style"),
         Output("popup-interval", "disabled"),
         Output("popup-interval", "n_intervals"),
         Output("resistance-sliders-container", "style")],
        [Input("reload-button", "n_clicks"),
         Input("popup-interval", "n_intervals"),
         Input("toggle-resistances", "n_clicks"),
         Input("num-resistances-slider", "value"),
         Input("precision-slider", "value")],
        [State("popup-message", "style"),
         State("resistance-sliders-container", "style")]
    )
    def update_graph_and_popup(n_clicks, n_intervals, resistance_clicks,
                              num_resistances, precision,
                              current_style, current_slider_style):
        ctx = callback_context

        # --- Charger les données ---
        klines = load_data_from_json()
        times, prices = process_klines_data(klines)

        # Construire DataFrame avec time et price pour MACD
        # Ici, on suppose load_data_from_json charge la même source que les JSON prix historiques
        # Sinon tu peux adapter en ouvrant directement le fichier JSON :
        # with open("prices_history/2025-07-24.json", "r") as f:
        #     raw_data = json.load(f)
        # df = pd.DataFrame(raw_data)

        df = pd.DataFrame({
            "time": times,
            "price": prices
        })

        # Calcul MACD
        df = calculate_macd(df)

        # Création des figures
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times,
            y=prices,
            mode="lines",
            name="Prix",
            line=dict(color="blue", width=2)
        ))

        fig.update_layout(
            xaxis_title="Temps",
            yaxis_title="Prix (USDT)",
            template="plotly_white"
        )

        
        macd_fig = create_macd_figure(df)  # Figure MACD

        # Si pas d'événement déclencheur => initialisation avec graph seul, MACD vide
        if not ctx.triggered:
            empty_macd_fig = go.Figure()
            return fig, empty_macd_fig, {"display": "none"}, True, 0, {"display": "none"}

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        sliders_visible = current_slider_style.get("display") == "block"

        # Gestion toggles résistances
        if triggered_id == "toggle-resistances":
            if sliders_visible:
                return fig, macd_fig, current_style, True, 0, {"display": "none"}
            else:
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
                return fig, macd_fig, current_style, True, 0, {"display": "block"}

        elif triggered_id in ["num-resistances-slider", "precision-slider"]:
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
                return fig, macd_fig, current_style, True, 0, current_slider_style
            else:
                return fig, macd_fig, current_style, True, 0, current_slider_style

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
            return fig, macd_fig, style_show, False, 0, {"display": "none"}

        elif triggered_id == "popup-interval" and n_intervals == 1:
            return fig, macd_fig, {"display": "none"}, True, 0, current_slider_style

        else:
            return fig, macd_fig, current_style, dash.no_update, dash.no_update, current_slider_style
