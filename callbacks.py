import dash
from dash import Output, Input, State, callback_context
import plotly.graph_objs as go
from data_utils import load_data_from_json, process_klines_data
from analysis_tools import find_resistance_levels, calculate_macd, create_macd_figure, classify_support_resistance
import pandas as pd
import json
from dash.dependencies import Input, Output, State
from dash import html

def register_callbacks(app):
    @app.callback(
        Output("historical-graph", "figure"),
        Output("macd-graph", "figure"),
        Output("popup-message", "style"),
        Output("popup-interval", "disabled"),
        Output("popup-interval", "n_intervals"),
        Output("resistance-sliders-container", "style"),
        Output("macd-status", "children"),
        Output("macd-status", "style"),
        Output("macd-trend-text", "children"),
        Input("reload-button", "n_clicks"),
        Input("popup-interval", "n_intervals"),
        Input("toggle-resistances", "n_clicks"),
        Input("num-resistances-slider", "value"),
        Input("precision-slider", "value"),
        State("popup-message", "style"),
        State("resistance-sliders-container", "style"),
    )
    def update_graph_and_popup(n_clicks, n_intervals, resistance_clicks,
                                num_resistances, precision,
                                current_style, current_slider_style):
        ctx = callback_context

        # --- Charger les données ---
        klines = load_data_from_json()
        times, prices = process_klines_data(klines)

        # Construire DataFrame avec time et price pour MACD
        df = pd.DataFrame({
            "time": times,
            "price": prices
        })

        # Calcul MACD
        df = calculate_macd(df)

        # Renommer les colonnes si nécessaire
        df = df.rename(columns={
            "MACD": "macd_diff",
            "Signal": "macd_dea"
        })

        # Sécurité si colonne absente
        if "macd_diff" not in df or "macd_dea" not in df:
            macd_status = "MACD indisponible"
            macd_status_style = {
                "color": "gray",
                "fontStyle": "italic",
                "textAlign": "center",
                "fontSize": "20px",
                "marginTop": "10px"
            }
        else:
            macd_diff = df["macd_diff"].iloc[-1]
            macd_dea = df["macd_dea"].iloc[-1]

            if macd_dea > macd_diff:
                macd_status = "MACD"
                macd_status_style = {
                    "color": "green",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "fontSize": "20px",
                    "marginTop": "10px"
                }
            else:
                macd_status = "MACD"
                macd_status_style = {
                    "color": "red",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "fontSize": "20px",
                    "marginTop": "10px"
                }

        # Création de la figure de prix
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times,
            y=prices,
            mode="lines",
            name="Prix",
            line=dict(color="blue", width=2)
        ))


        # Vérification de la tendance actuelle
        # Calcul du DEA_diff et de la tendance actuelle
        dea_diff = df["macd_dea"].iloc[-1] - df["macd_dea"].iloc[-2]
        if abs(dea_diff) < 1e-6:
            last_trend = "flat"
        elif dea_diff > 0:
            last_trend = "up"
        else:
            last_trend = "down"

        trend_color = {
            "up": "green",
            "down": "red",
            "flat": "yellow"
        }[last_trend]

        macd_trend_text = f"Tendance actuelle : {last_trend}"

        fig.update_layout(
            xaxis_title="Temps",
            yaxis_title="Prix (USDT)",
            template="plotly_white",
            uirevision="prix"  # <-- c'est cette ligne qui fixe le zoom/pan
        )

        macd_fig = create_macd_figure(df)  # Figure MACD

        # Si pas d’événement déclencheur
        if not ctx.triggered:
            empty_macd_fig = go.Figure()
            return fig, empty_macd_fig, {"display": "none"}, True, 0, {"display": "none"}, macd_status, macd_status_style, html.Span(macd_trend_text, style={"color": trend_color}),


        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        sliders_visible = current_slider_style.get("display") == "block"

        # Gestion des résistances
        if triggered_id == "toggle-resistances":
            if sliders_visible:
                return fig, macd_fig, current_style, True, 0, {"display": "none"}, macd_status, macd_status_style, html.Span(macd_trend_text, style={"color": trend_color}),

            else:
                resistances = find_resistance_levels(prices, n=num_resistances, precision=precision)

                # Classification des niveaux
                levels_classification = classify_support_resistance(df, resistances, seuil=0.001)
                levels_colors = {
                    "support": "green",
                    "resistance": "red",
                    "neutral": "yellow"
                }

                for r in resistances:
                    classification = levels_classification.get(r, "neutral")
                    # Ajouter une ligne visuelle
                    fig.add_shape(
                        type="line",
                        x0=times[0],
                        x1=times[-1],
                        y0=r,
                        y1=r,
                        line=dict(color=levels_colors[classification], width=2, dash="dot"),
                        layer="below",
                    )

                    # Ajouter la valeur de la droite de résistance lorsque qu'on passe la souris dessus
                    fig.add_trace(go.Scatter(
                        x=[times[-1]],
                        y=[r],
                        mode="markers",
                        marker=dict(color=levels_colors[classification], size=8, opacity=0),
                        showlegend=False,
                        hoverinfo="text",
                        hovertext=f"{classification.capitalize()} : {r:.2f} USDT"
                    ))


                return fig, macd_fig, current_style, True, 0, {"display": "block"}, macd_status, macd_status_style, html.Span(macd_trend_text, style={"color": trend_color}),


        elif triggered_id in ["num-resistances-slider", "precision-slider"]:
            if sliders_visible:
                resistances = find_resistance_levels(prices, n=num_resistances, precision=precision)

                # Classification des niveaux
                levels_classification = classify_support_resistance(df, resistances, seuil=0.001)
                levels_colors = {
                    "support": "green",
                    "resistance": "red",
                    "neutral": "yellow"
                }

                for r in resistances:
                    classification = levels_classification.get(r, "neutral")
                    # Ajouter une ligne visuelle
                    fig.add_shape(
                        type="line",
                        x0=times[0],
                        x1=times[-1],
                        y0=r,
                        y1=r,
                        line=dict(color=levels_colors[classification], width=2, dash="dot"),
                        layer="below",
                    )

                    # Ajouter la valeur de la droite de résistance lorsque qu'on passe la souris dessus
                    fig.add_trace(go.Scatter(
                        x=[times[-1]],
                        y=[r],
                        mode="markers",
                        marker=dict(color=levels_colors[classification], size=8, opacity=0),
                        showlegend=False,
                        hoverinfo="text",
                        hovertext=f"{classification.capitalize()} : {r:.2f} USDT"
                    ))


                return fig, macd_fig, current_style, True, 0, current_slider_style, macd_status, macd_status_style,  html.Span(macd_trend_text, style={"color": trend_color}),

            else:
                return fig, macd_fig, current_style, True, 0, current_slider_style, macd_status, macd_status_style,  html.Span(macd_trend_text, style={"color": trend_color}),


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
            return fig, macd_fig, style_show, False, 0, {"display": "none"}, macd_status, macd_status_style,  html.Span(macd_trend_text, style={"color": trend_color}),


        elif triggered_id == "popup-interval" and n_intervals >= 1:
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
            return fig, macd_fig, style_show, False, 0, {"display": "none"}, macd_status, macd_status_style, html.Span(macd_trend_text, style={"color": trend_color}),


        else:
            return fig, macd_fig, current_style, dash.no_update, dash.no_update, current_slider_style, macd_status, macd_status_style, html.Span(macd_trend_text, style={"color": trend_color}),
