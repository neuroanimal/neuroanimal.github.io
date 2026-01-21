import pandas as pd
import numpy as np
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from scipy.stats import linregress

# === 1. Wczytanie danych ===
df_gus = pd.read_csv("data/gus/all.csv", parse_dates=["date"])
df_nbp = pd.read_csv("data/nbp/all.csv", parse_dates=["date"])

# Kolumna CPI z Wikipedii
df_gus["cpi"] = df_gus.get("cpi_avg_wiki")

# Scalanie po dacie (outer, bo różne częstotliwości)
df = pd.merge(df_gus[["date", "cpi"]], df_nbp[["date", "USD_PLN"]], on="date", how="outer")
df = df.sort_values("date").set_index("date")

# Przydatny "czysty" DF bez NaN w obu seriach do analiz korelacyjnych
df_clean = df.dropna(subset=["cpi", "USD_PLN"])

# Jeśli nie ma danych, ustaw rozsądne domyślne lata
min_year = 1917
max_year = int(df.index.max().year) if not df.index.empty else 2025

# === 2. Dash App ===
app = Dash(__name__)
app.title = "Inflacja CPI a Kurs USD/PLN - Poprawiona korelacja krocząca"

app.layout = html.Div([
    html.H2("Inflacja CPI a Kurs USD/PLN (Polska, 1917–2025)",
            style={"textAlign": "center", "marginTop": "20px"}),

    html.Div(id="corr-info", style={"textAlign": "center", "fontWeight": "bold", "marginBottom": "10px"}),

    dcc.Graph(id="cpi-usd-graph", style={"height": "60vh"}),
    dcc.Graph(id="scatter-graph", style={"height": "25vh"}),
    dcc.Graph(id="rolling-corr", style={"height": "25vh"}),

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
     Output("rolling-corr", "figure"),
     Output("corr-info", "children")],
    Input("year-slider", "value")
)
def update_graph(year_range):
    start_year, end_year = year_range
    # wybieramy zakres na podstawie roku (uwaga: indeks to datetime)
    # uwzględniamy pełne lata, od 1 stycznia start do 31 grudnia end
    start_ts = f"{start_year}-01-01"
    end_ts = f"{end_year}-12-31"
    df_range_all = df.loc[start_ts:end_ts]            # może zawierać NaNy
    df_range = df_clean.loc[start_ts:end_ts]          # tylko wiersze z obydwoma wartościami

    # Jeśli brak danych do rysunku
    if df_range_all.empty and df_range.empty:
        return go.Figure(), go.Figure(), go.Figure(), "Brak danych w wybranym zakresie."

    # --- Czasowy wykres (wykorzystujemy df_range_all aby pokazać luki) ---
    fig_time = go.Figure()
    if not df_range_all["cpi"].isna().all():
        fig_time.add_trace(go.Scatter(
            x=df_range_all.index, y=df_range_all["cpi"],
            mode="lines", name="Inflacja CPI", line=dict(color="red", width=2)
        ))
    if not df_range_all["USD_PLN"].isna().all():
        fig_time.add_trace(go.Scatter(
            x=df_range_all.index, y=df_range_all["USD_PLN"],
            mode="lines", name="USD/PLN", line=dict(color="blue", width=2),
            yaxis="y2"
        ))
    fig_time.update_layout(
        yaxis=dict(title="Inflacja (%)", color="red"),
        yaxis2=dict(title="Kurs USD/PLN", overlaying="y", side="right", color="blue"),
        xaxis_title="Data",
        legend=dict(x=0, y=1.05, orientation="h"),
        margin=dict(l=60, r=60, t=40, b=40),
        height=500,
        template="plotly_white",
        hovermode="x unified"
    )

    # --- Scatter + linia regresji (używamy df_range czyli par bez NaN) ---
    fig_scatter = go.Figure()
    if not df_range.empty:
        fig_scatter.add_trace(go.Scatter(
            x=df_range["USD_PLN"], y=df_range["cpi"],
            mode="markers", name="Punkty (CPI vs USD/PLN)",
            marker=dict(size=6, color="purple", opacity=0.6)
        ))

        # regresja liniowa CPI ~ USD
        slope, intercept, r_value, p_value, std_err = linregress(df_range["USD_PLN"], df_range["cpi"])
        x_vals = np.linspace(df_range["USD_PLN"].min(), df_range["USD_PLN"].max(), 100)
        y_vals = slope * x_vals + intercept
        fig_scatter.add_trace(go.Scatter(
            x=x_vals, y=y_vals, mode="lines", name="Linia trendu (regresja)",
            line=dict(color="green", dash="dot")
        ))
        corr_text = f"Korelacja Pearsona (CPI ↔ USD/PLN): {df_range['cpi'].corr(df_range['USD_PLN']):.3f}"
        corr_text += f"  |  Trend: CPI = {slope:.2f}·USD + {intercept:.2f} (r={r_value:.3f})"
    else:
        corr_text = "Brak wystarczających par (CPI, USD) w wybranym zakresie."
    fig_scatter.update_layout(
        xaxis_title="Kurs USD/PLN", yaxis_title="Inflacja CPI (%)",
        title="Wykres rozrzutu (CPI vs USD/PLN)",
        margin=dict(l=60, r=60, t=40, b=40),
        height=300,
        template="plotly_white"
    )

    # --- Rolling correlation (time-based window 10 lat = '3650D') ---
    # Używamy df_range_all[['cpi','USD_PLN']] i obliczamy korelację czasową
    fig_corr = go.Figure()
    rolling_corr_series = pd.Series(dtype=float)
    try:
        # wybieramy kolumny i usuwamy całkowicie puste daty (aby rolling('3650D') miało sens)
        df_for_roll = df_range_all[["cpi", "USD_PLN"]].copy()
        # compute rolling correlation (time-based window)
        # result of .rolling(...).corr(other) is aligned with index
        rolling_corr_series = df_for_roll["cpi"].rolling(window="3650D", min_periods=20).corr(df_for_roll["USD_PLN"])
        # Drop NaNs for plotting
        rolling_corr_series = rolling_corr_series.dropna()
        if not rolling_corr_series.empty:
            fig_corr.add_trace(go.Scatter(
                x=rolling_corr_series.index, y=rolling_corr_series.values,
                mode="lines", name="Korelacja krocząca (10 lat)", line=dict(color="orange", width=2)
            ))
            fig_corr.add_hline(y=0, line_dash="dot", line_color="gray")
        else:
            # empty series -> no trace
            pass
    except Exception as e:
        # Bez krytycznego błędu — zamiast crashu wyświetlamy pusty wykres i komunikat w tekście korelacji
        rolling_corr_series = pd.Series(dtype=float)

    fig_corr.update_layout(
        title="Korelacja krocząca CPI↔USD (okno 10 lat, time-based)",
        yaxis_title="Współczynnik korelacji",
        xaxis_title="Data",
        margin=dict(l=60, r=60, t=40, b=40),
        height=250,
        template="plotly_white"
    )

    return fig_time, fig_scatter, fig_corr, corr_text


if __name__ == "__main__":
    app.run(debug=True)


