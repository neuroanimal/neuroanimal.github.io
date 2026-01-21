import dash
from dash import dcc, html, Input, Output
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from sklearn.cluster import KMeans

# === WCZYTANIE I INTEGRACJA DANYCH ===
# Dane inflacji (GUS/Wikipedia)
df_gus = pd.read_csv("data/gus/all.csv")
df_gus["date"] = pd.to_datetime(df_gus["date"])
df_gus = df_gus.sort_values("date")

# Dane kursu USD (NBP)
df_nbp = pd.read_csv("data/nbp/all.csv")
df_nbp["date"] = pd.to_datetime(df_nbp["date"])
df_nbp = df_nbp.sort_values("date")

# Scalanie danych po dacie (inner join)
df = pd.merge_asof(
    df_gus.sort_values("date"),
    df_nbp.sort_values("date"),
    on="date",
    direction="nearest",
    tolerance=pd.Timedelta("30D")  # dopasuj jeśli chcesz szerszy margines
)

# Wybór istotnych kolumn
df["year"] = df["date"].dt.year
df["cpi"] = df["cpi_avg_wiki"].fillna(df["cpi_avg_gus"])  # preferuj dane z Wikipedii
df["usd"] = df["USD_PLN"]

# Filtrujemy tylko rekordy z obydwoma wartościami
df = df.dropna(subset=["cpi", "usd"])

# === APLIKACJA DASH ===
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Inflacja CPI (PL) vs Kurs USD/PLN z korelacją kroczącą"),
    html.Div([
        html.Label("Zakres lat:"),
        dcc.RangeSlider(
            id="year-range",
            min=int(df["year"].min()),
            max=int(df["year"].max()),
            step=1,
            value=[1977, int(df["year"].max())],
            marks={int(y): str(y) for y in range(1917, 2025, 10)},
            tooltip={"placement": "bottom", "always_visible": False}
        ),
    ], style={"margin": "20px"}),

    html.Div([
        html.Label("Okno kroczące (lata):"),
        dcc.Slider(
            id="rolling-window",
            min=1, max=20, step=1, value=10,
            marks={i: f"{i}" for i in range(1, 21)},
            tooltip={"placement": "bottom", "always_visible": False}
        ),
    ], style={"margin": "20px"}),

    html.Div([
        html.Label("Skala logarytmiczna dla kursu USD:"),
        dcc.RadioItems(
            id="log-scale",
            options=[
                {"label": "Linear", "value": "linear"},
                {"label": "Log", "value": "log"}
            ],
            value="linear",
            inline=True
        ),
    ], style={"margin": "20px"}),

    dcc.Graph(id="cpi-usd-graph", style={"height": "1000px"}),
    dcc.Graph(id="corr-graph", style={"height": "600px"}),
    dcc.Graph(id="scatter-graph", style={"height": "600px"}),
])

# === CALLBACK ===
@app.callback(
    [Output("cpi-usd-graph", "figure"),
     Output("corr-graph", "figure"),
     Output("scatter-graph", "figure")],
    [Input("year-range", "value"),
     Input("rolling-window", "value"),
     Input("log-scale", "value")]
)
def update_graph(year_range, rolling_window, log_scale):
    df_range = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])].copy()

    # Korelacja krocząca
    window_days = int(rolling_window * 365)
    df_range["corr"] = df_range["cpi"].rolling(window=window_days, min_periods=50).corr(df_range["usd"])

    # Segmentacja (scatter plot)
    df_seg = df_range.dropna(subset=["cpi", "usd"]).copy()
    if len(df_seg) >= 3:
        X = df_seg[["cpi", "usd"]].to_numpy()
        kmeans = KMeans(n_clusters=3, random_state=42, n_init="auto")
        df_seg["cluster"] = kmeans.fit_predict(X)
    else:
        df_seg["cluster"] = 0

    # === WYKRES GŁÓWNY ===
    fig_main = go.Figure()
    fig_main.add_trace(go.Scatter(
        x=df_range["date"], y=df_range["cpi"],
        mode="lines", name="Inflacja CPI [%]",
        yaxis="y1", line=dict(color="red")
    ))
    fig_main.add_trace(go.Scatter(
        x=df_range["date"], y=df_range["usd"],
        mode="lines", name="Kurs USD/PLN",
        yaxis="y2", line=dict(color="blue")
    ))
    fig_main.update_layout(
        yaxis=dict(title="Inflacja CPI [%]", domain=[0, 0.8], anchor="x"),
        yaxis2=dict(
            title="USD/PLN",
            overlaying="y",
            side="right",
            type=log_scale,
            showgrid=False
        ),
        height=1000,
        legend=dict(x=0.01, y=0.99),
        margin=dict(l=60, r=60, t=60, b=60)
    )

    # === WYKRES KORELACJI ===
    fig_corr = go.Figure()
    fig_corr.add_trace(go.Scatter(
        x=df_range["date"], y=df_range["corr"],
        mode="lines", name=f"Korelacja krocząca ({rolling_window} lat)",
        line=dict(color="green")
    ))
    fig_corr.update_layout(
        yaxis=dict(title="Współczynnik korelacji", range=[-1, 1]),
        height=600,
        margin=dict(l=60, r=60, t=60, b=60)
    )

    # === SCATTER PLOT ===
    colors = ["#FF5733", "#33C3FF", "#33FF77"]
    fig_scatter = go.Figure()
    for cluster in sorted(df_seg["cluster"].unique()):
        seg = df_seg[df_seg["cluster"] == cluster]
        fig_scatter.add_trace(go.Scatter(
            x=seg["cpi"], y=seg["usd"],
            mode="markers",
            name=f"Segment {cluster + 1}",
            marker=dict(size=10, color=colors[cluster % len(colors)], opacity=0.7),
        ))

    fig_scatter.update_layout(
        xaxis=dict(title="Inflacja CPI [%]"),
        yaxis=dict(title="Kurs USD/PLN", type=log_scale),
        height=600,
        margin=dict(l=60, r=60, t=60, b=60),
        legend=dict(x=0.01, y=0.99)
    )

    return fig_main, fig_corr, fig_scatter


if __name__ == "__main__":
    app.run(debug=True)


