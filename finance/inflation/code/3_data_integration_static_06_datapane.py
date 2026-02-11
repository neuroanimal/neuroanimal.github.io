import pandas as pd
import plotly.graph_objs as go
from sklearn.cluster import KMeans

# === PARAMETRY ===
YEAR_START = 1977
YEAR_END = 2024
ROLLING_WINDOW = 10

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

window_days = int(ROLLING_WINDOW * 365)
df_range["corr"] = df_range["cpi"].rolling(window=window_days, min_periods=50).corr(df_range["usd"])

df_seg = df_range.dropna(subset=["cpi", "usd"]).copy()
if len(df_seg) >= 3:
    X = df_seg[["cpi", "usd"]].to_numpy()
    kmeans = KMeans(n_clusters=3, random_state=42, n_init="auto")
    df_seg["cluster"] = kmeans.fit_predict(X)
else:
    df_seg["cluster"] = 0

# === WYKRESY ===
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=df_range["date"], y=df_range["cpi"], mode="lines", name="CPI", line=dict(color="red")))
fig1.update_layout(title="Inflacja CPI", height=300)

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df_range["date"], y=df_range["usd"], mode="lines", name="USD", line=dict(color="blue")))
fig2.update_layout(title="Kurs USD/PLN", height=300)

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=df_range["date"], y=df_range["corr"], mode="lines", line=dict(color="green")))
fig3.update_layout(title=f"Korelacja ({ROLLING_WINDOW} lat)", height=250)

# === EKSPORT Z DATAPANE ===
try:
    import datapane as dp
    
    report = dp.Report(
        dp.Text(f"# Dashboard: Inflacja CPI vs USD/PLN ({YEAR_START}-{YEAR_END})"),
        dp.Plot(fig1),
        dp.Plot(fig2),
        dp.Plot(fig3),
        dp.DataTable(df_range[["date", "cpi", "usd", "corr"]].tail(50))
    )
    
    report.save("dashboard_06_datapane.html")
    print("✓ Zapisano: dashboard_06_datapane.html")
except ImportError:
    print("⚠ Zainstaluj: pip install datapane")
except Exception as e:
    print(f"⚠ Błąd Datapane: {e}")
