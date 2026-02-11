import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from sklearn.cluster import KMeans

# === PARAMETRY ===
YEAR_START = 1977
YEAR_END = 2024
ROLLING_WINDOW = 10  # lata
LOG_SCALE = "linear"  # lub "log"

# === WCZYTANIE I INTEGRACJA DANYCH ===
df_gus = pd.read_csv("data/gus/all.csv")
df_gus["date"] = pd.to_datetime(df_gus["date"])
df_gus = df_gus.sort_values("date")

df_nbp = pd.read_csv("data/nbp/all.csv")
df_nbp["date"] = pd.to_datetime(df_nbp["date"])
df_nbp = df_nbp.sort_values("date")

df = pd.merge_asof(
    df_gus.sort_values("date"),
    df_nbp.sort_values("date"),
    on="date",
    direction="nearest",
    tolerance=pd.Timedelta("30D")
)

df["year"] = df["date"].dt.year
df["cpi"] = df["cpi_avg_wiki"].fillna(df["cpi_avg_gus"])
df["usd"] = df["USD_PLN"]
df = df.dropna(subset=["cpi", "usd"])

# === FILTROWANIE ===
df_range = df[(df["year"] >= YEAR_START) & (df["year"] <= YEAR_END)].copy()

# Korelacja krocząca
window_days = int(ROLLING_WINDOW * 365)
df_range["corr"] = df_range["cpi"].rolling(window=window_days, min_periods=50).corr(df_range["usd"])

# Segmentacja
df_seg = df_range.dropna(subset=["cpi", "usd"]).copy()
if len(df_seg) >= 3:
    X = df_seg[["cpi", "usd"]].to_numpy()
    kmeans = KMeans(n_clusters=3, random_state=42, n_init="auto")
    df_seg["cluster"] = kmeans.fit_predict(X)
else:
    df_seg["cluster"] = 0

# === DASHBOARD Z 3 WYKRESAMI ===
fig = make_subplots(
    rows=3, cols=1,
    row_heights=[0.4, 0.3, 0.3],
    specs=[[{"secondary_y": True}], [{}], [{}]],
    subplot_titles=(
        "Inflacja CPI (PL) vs Kurs USD/PLN",
        f"Korelacja krocząca ({ROLLING_WINDOW} lat)",
        "Segmentacja: CPI vs USD"
    ),
    vertical_spacing=0.08
)

# Wykres 1: CPI + USD
fig.add_trace(go.Scatter(
    x=df_range["date"], y=df_range["cpi"],
    mode="lines", name="Inflacja CPI [%]",
    line=dict(color="red")
), row=1, col=1, secondary_y=False)

fig.add_trace(go.Scatter(
    x=df_range["date"], y=df_range["usd"],
    mode="lines", name="Kurs USD/PLN",
    line=dict(color="blue")
), row=1, col=1, secondary_y=True)

# Wykres 2: Korelacja
fig.add_trace(go.Scatter(
    x=df_range["date"], y=df_range["corr"],
    mode="lines", name="Korelacja",
    line=dict(color="green")
), row=2, col=1)

# Wykres 3: Scatter z segmentacją
colors = ["#FF5733", "#33C3FF", "#33FF77"]
for cluster in sorted(df_seg["cluster"].unique()):
    seg = df_seg[df_seg["cluster"] == cluster]
    fig.add_trace(go.Scatter(
        x=seg["cpi"], y=seg["usd"],
        mode="markers",
        name=f"Segment {cluster + 1}",
        marker=dict(size=8, color=colors[cluster % len(colors)], opacity=0.7),
        showlegend=True
    ), row=3, col=1)

# Layout
fig.update_yaxes(title_text="Inflacja CPI [%]", row=1, col=1, secondary_y=False)
fig.update_yaxes(title_text="USD/PLN", type=LOG_SCALE, row=1, col=1, secondary_y=True)
fig.update_yaxes(title_text="Korelacja", range=[-1, 1], row=2, col=1)
fig.update_yaxes(title_text="USD/PLN", type=LOG_SCALE, row=3, col=1)
fig.update_xaxes(title_text="Data", row=2, col=1)
fig.update_xaxes(title_text="Inflacja CPI [%]", row=3, col=1)

fig.update_layout(
    height=1600,
    title_text=f"Dashboard: Inflacja CPI vs USD/PLN ({YEAR_START}-{YEAR_END})",
    showlegend=True,
    legend=dict(x=1.05, y=1)
)

# === EKSPORT ===
fig.write_html("dashboard.html")
print("✓ Zapisano: dashboard.html")

# Dla PNG/PDF zainstaluj: pip install kaleido
try:
    fig.write_image("dashboard.png", width=1400, height=1600, scale=2)
    print("✓ Zapisano: dashboard.png")
    fig.write_image("dashboard.pdf", width=1400, height=1600)
    print("✓ Zapisano: dashboard.pdf")
except Exception as e:
    print(f"⚠ Aby zapisać PNG/PDF, zainstaluj: pip install kaleido")
    print(f"  Błąd: {e}")
