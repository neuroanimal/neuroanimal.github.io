import pandas as pd
import numpy as np
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from scipy.stats import linregress

# === 1. Wczytanie danych ===
df_gus = pd.read_csv("data/gus/all.csv", parse_dates=["date"])
df_nbp = pd.read_csv("data/nbp/all.csv", parse_dates=["date"])

# CPI z Wikipedii (1917–...)
df_gus["cpi"] = df_gus["cpi_avg_wiki"]

# Scalanie po dacie
df = pd.merge(df_gus[["date", "cpi"]], df_nbp[["date", "USD_PLN"]], on="date", how="outer")
df = df.sort_values("date").set_index("date")

# Usuwamy NaN-y do analizy korelacji
df_clean = df.dropna(subset=["cpi", "USD_PLN"])

# Zakres lat
min_year, max_year = int(df_clean.index.min().year), int(df_clean.index.max().year)


# === 2. Dash App ===
app = Dash(__name__)
app.title = "Inflacja CPI a Kurs USD/PLN"

app.layout = html.Div([
    html.H2("Inflacja CPI a Kurs USD/PLN (Polska, 1917–2025)",
            style={"textAlign": "center", "marginTop": "20px"}),

    html.Div(id="corr-info", style={"textAlign": "center", "fontWeight": "bold", "marginBottom": "10px"}),

    dcc.Graph(id="cpi-usd-graph", style={"height": "70vh"}),
    dcc.Graph(id="scatter-graph", style={"height": "30vh"}),

    html.Label("Zakres lat:", style={"marginTop": "15px"}),
    dcc.RangeSlider(
        id="year-slider",
        min=min_year,
        max=max_year,
        step=1,
        value=[1977, max_year],
        marks={y: str(y) for y in range(min_year, max_year + 1, 10)},
        tooltip={"placement": "bottom", "always_visible": True}
    )
])


# === 3. Callback ===
@app.callback(
    [Output("cpi-usd-graph", "figure"),
     Output("scatter-graph", "figure"),
     Output("corr-info", "children")],
    Input("year-slider", "value")
)
def update_graph(year_range):
    start_year, end_year = year_range
    df_range = df_clean.loc[str(start_year):str(end_year)]

    if df_range.empty or df_range["cpi"].isna().all() or df_range["USD_PLN"].isna().all():
        return go.Figure(), go.Figure(), "Brak danych w wybranym zakresie."

    # Oblicz korelację Pearsona i linię regresji
    corr = df_range["cpi"].corr(df_range["USD_PLN"])
    slope, intercept, _, _, _ = linregress(df_range["USD_PLN"], df_range["cpi"])

    trend_line = slope * df_range["USD_PLN"] + intercept

    # === Główny wykres (czasowy) ===
    fig_time = go.Figure()

    fig_time.add_trace(go.Scatter(
        x=df_range.index, y=df_range["cpi"],
        mode="lines", name="Inflacja CPI", line=dict(color="red", width=2)
    ))

    fig_time.add_trace(go.Scatter(
        x=df_range.index, y=df_range["USD_PLN"],
        mode="lines", name="USD/PLN", line=dict(color="blue", width=2),
        yaxis="y2"
    ))

    fig_time.update_layout(
        yaxis=dict(title="Inflacja (%)", color="red"),
        yaxis2=dict(title="Kurs USD/PLN", overlaying="y", side="right", color="blue"),
        xaxis_title="Data",
        legend=dict(x=0, y=1.1, orientation="h"),
        margin=dict(l=60, r=60, t=40, b=40),
        height=600
    )

    # === Scatter CPI vs USD/PLN ===
    fig_scatter = go.Figure()
    fig_scatter.add_trace(go.Scatter(
        x=df_range["USD_PLN"], y=df_range["cpi"],
        mode="markers", name="Punkty (CPI vs USD/PLN)",
        marker=dict(size=6, color="purple", opacity=0.6)
    ))
    fig_scatter.add_trace(go.Scatter(
        x=df_range["USD_PLN"], y=trend_line,
        mode="lines", name="Linia trendu (regresja)",
        line=dict(color="green", dash="dot")
    ))

    fig_scatter.update_layout(
        xaxis_title="Kurs USD/PLN",
        yaxis_title="Inflacja CPI (%)",
        title="Wykres rozrzutu (CPI vs USD/PLN)",
        margin=dict(l=60, r=60, t=40, b=40),
        height=300
    )

    # === Opis korelacji ===
    info_text = f"Korelacja Pearsona (CPI ↔ USD/PLN): {corr:.3f} | Trend: CPI = {slope:.2f}·USD + {intercept:.2f}"

    return fig_time, fig_scatter, info_text


if __name__ == "__main__":
    app.run(debug=True)


