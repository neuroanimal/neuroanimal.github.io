import pandas as pd
import altair as alt
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
df_seg["cluster"] = df_seg["cluster"].astype(str)

# === DASHBOARD ===
alt.data_transformers.disable_max_rows()

chart1_cpi = alt.Chart(df_range).mark_line(color="red").encode(
    x=alt.X("date:T", title="Data"),
    y=alt.Y("cpi:Q", title="Inflacja CPI [%]", scale=alt.Scale(zero=False))
).properties(width=800, height=250, title="Inflacja CPI")

chart1_usd = alt.Chart(df_range).mark_line(color="blue").encode(
    x=alt.X("date:T", title="Data"),
    y=alt.Y("usd:Q", title="USD/PLN", scale=alt.Scale(zero=False))
).properties(width=800, height=250, title="Kurs USD/PLN")

chart2 = alt.Chart(df_range).mark_line(color="green").encode(
    x=alt.X("date:T", title="Data"),
    y=alt.Y("corr:Q", title="Korelacja", scale=alt.Scale(domain=[-1, 1]))
).properties(width=800, height=200, title=f"Korelacja krocząca ({ROLLING_WINDOW} lat)")

chart3 = alt.Chart(df_seg).mark_circle(size=60, opacity=0.7).encode(
    x=alt.X("cpi:Q", title="Inflacja CPI [%]"),
    y=alt.Y("usd:Q", title="USD/PLN"),
    color=alt.Color("cluster:N", scale=alt.Scale(range=["#FF5733", "#33C3FF", "#33FF77"]), 
                    legend=alt.Legend(title="Segment"))
).properties(width=800, height=300, title="Segmentacja: CPI vs USD")

dashboard = alt.vconcat(chart1_cpi, chart1_usd, chart2, chart3).properties(
    title=f"Dashboard: Inflacja CPI vs USD/PLN ({YEAR_START}-{YEAR_END})"
)

# === EKSPORT ===
dashboard.save("dashboard_03_altair.html")
print("✓ Zapisano: dashboard_03_altair.html")

try:
    dashboard.save("dashboard_03_altair.png", scale_factor=2.0)
    print("✓ Zapisano: dashboard_03_altair.png")
except Exception as e:
    print(f"⚠ PNG wymaga: npm install -g vega-lite vega-cli canvas")
    print(f"  Lub użyj: dashboard.save('dashboard_03_altair.svg')")
