import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

# ===========================================
# 1️⃣ Wczytanie danych
# ===========================================

# Dane GUS/Wiki (inflacja)
df_gus = pd.read_csv("data/gus/all.csv", parse_dates=["date"])
df_gus = df_gus.rename(columns={"cpi_avg_wiki": "cpi"})
df_gus = df_gus.set_index("date")

# Dane NBP (kurs USD/PLN)
df_nbp = pd.read_csv("data/nbp/all.csv", parse_dates=["date"])
df_nbp = df_nbp.set_index("date")

# Połączenie danych po dacie (outer join)
df = pd.merge(df_gus[["cpi"]], df_nbp[["USD_PLN"]], left_index=True, right_index=True, how="outer")
df = df.sort_index()

# ===========================================
# 2️⃣ Funkcja do agregacji (dzienna/miesięczna/roczna)
# ===========================================

def aggregate_dynamic(df):
    """Agreguje dane w zależności od długości przedziału czasowego."""
    total_years = df.index.year.max() - df.index.year.min()
    if total_years > 50:
        return df.resample("YE").mean()  # dane roczne
    elif total_years > 10:
        return df.resample("ME").mean()  # dane miesięczne
    else:
        return df.resample("D").mean()   # dane dzienne


# ===========================================
# 3️⃣ Konfiguracja aplikacji Dash
# ===========================================

app = Dash(__name__)
app.title = "Inflacja CPI vs Kurs USD/PLN"

# Zakres suwaka lat
year_min = int(df.index.year.min())
year_max = int(df.index.year.max())

# ===========================================
# 4️⃣ Layout aplikacji
# ===========================================

app.layout = html.Div([
    html.H1("Inflacja CPI a Kurs USD/PLN (Polska, 1917–2025)", style={"textAlign": "center"}),

    html.Div(id="correlation-output", style={"textAlign": "center", "fontSize": "20px", "marginBottom": "10px"}),

    dcc.Graph(id="cpi-usd-graph", style={"height": "800px"}),

    html.Label("Zakres lat:", style={"fontWeight": "bold"}),
    dcc.RangeSlider(
        id="year-range-slider",
        min=year_min,
        max=year_max,
        value=[1977, year_max],
        marks={y: str(y) for y in range(year_min, year_max + 1, 10)},
        step=1,
        tooltip={"placement": "bottom", "always_visible": False}
    ),

    html.Div([
        html.Label("Wybór serii danych:", style={"fontWeight": "bold"}),
        dcc.Checklist(
            id="line-toggle",
            options=[
                {"label": "Inflacja CPI", "value": "CPI"},
                {"label": "Kurs USD/PLN", "value": "USD"},
            ],
            value=["CPI", "USD"],
            inline=True
        ),
    ], style={"marginTop": "20px"}),
])

# ===========================================
# 5️⃣ Callback - aktualizacja wykresu
# ===========================================

@app.callback(
    [Output("cpi-usd-graph", "figure"),
     Output("correlation-output", "children")],
    [Input("year-range-slider", "value"),
     Input("line-toggle", "value")]
)
def update_graph(year_range, selected_lines):
    start_year, end_year = year_range
    df_filtered = df[(df.index.year >= start_year) & (df.index.year <= end_year)]
    df_agg = aggregate_dynamic(df_filtered)

    fig = go.Figure()

    # CPI
    if "CPI" in selected_lines:
        fig.add_trace(go.Scatter(
            x=df_agg.index, y=df_agg["cpi"],
            mode="lines+markers",
            name="Inflacja CPI",
            line=dict(color="red"),
            marker=dict(size=4),
            yaxis="y1",
            hovertemplate="Data: %{x|%Y-%m-%d}<br>CPI: %{y:.2f}%<extra></extra>"
        ))

    # USD/PLN
    if "USD" in selected_lines:
        fig.add_trace(go.Scatter(
            x=df_agg.index, y=df_agg["USD_PLN"],
            mode="lines+markers",
            name="USD/PLN",
            line=dict(color="blue"),
            marker=dict(size=4),
            yaxis="y2",
            hovertemplate="Data: %{x|%Y-%m-%d}<br>USD/PLN: %{y:.2f}<extra></extra>"
        ))

    # 🧠 Dynamiczne wyliczanie zakresu osi
    cpi_min, cpi_max = df_agg["cpi"].min(), df_agg["cpi"].max()
    usd_min, usd_max = df_agg["USD_PLN"].min(), df_agg["USD_PLN"].max()

    if pd.isna(cpi_min) or pd.isna(cpi_max):
        y1_range = [0, 1]
    else:
        padding = (cpi_max - cpi_min) * 0.1
        y1_range = [max(0, cpi_min - padding), cpi_max + padding]

    if pd.isna(usd_min) or pd.isna(usd_max):
        y2_range = [0, 1]
    else:
        usd_padding = (usd_max - usd_min) * 0.1
        y2_range = [max(0, usd_min - usd_padding), usd_max + usd_padding]

    # 🧮 Korelacja Pearson
    corr_text = "Brak wystarczających danych do obliczenia korelacji."
    if df_agg["cpi"].notna().sum() > 2 and df_agg["USD_PLN"].notna().sum() > 2:
        corr_value = df_agg["cpi"].corr(df_agg["USD_PLN"], method="pearson")
        if not np.isnan(corr_value):
            corr_text = f"📊 Korelacja (Pearson) CPI ↔ USD/PLN: {corr_value:.2f}"

    # Layout
    fig.update_layout(
        height=800,
        xaxis_title="Data",
        yaxis=dict(
            title=dict(text="Inflacja (%)", font=dict(color="red")),
            tickfont=dict(color="red"),
            range=y1_range,
        ),
        yaxis2=dict(
            title=dict(text="Kurs USD/PLN", font=dict(color="blue")),
            tickfont=dict(color="blue"),
            overlaying="y", side="right",
            range=y2_range,
        ),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(x=0.01, y=0.99)
    )

    return fig, corr_text


# ===========================================
# 6️⃣ Uruchomienie aplikacji
# ===========================================

if __name__ == "__main__":
    app.run(debug=True)


