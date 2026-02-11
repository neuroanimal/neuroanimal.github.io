import pandas as pd
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import column
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

# === DASHBOARD ===
output_file("dashboard_04_bokeh.html")

p1 = figure(width=900, height=300, x_axis_type="datetime", title="Inflacja CPI [%]")
p1.line(df_range["date"], df_range["cpi"], color="red", line_width=2, legend_label="CPI")
p1.yaxis.axis_label = "Inflacja CPI [%]"

p2 = figure(width=900, height=300, x_axis_type="datetime", title="Kurs USD/PLN")
p2.line(df_range["date"], df_range["usd"], color="blue", line_width=2, legend_label="USD/PLN")
p2.yaxis.axis_label = "USD/PLN"

p3 = figure(width=900, height=250, x_axis_type="datetime", title=f"Korelacja krocząca ({ROLLING_WINDOW} lat)")
p3.line(df_range["date"], df_range["corr"], color="green", line_width=2)
p3.yaxis.axis_label = "Korelacja"

p4 = figure(width=900, height=350, title="Segmentacja: CPI vs USD")
colors_map = {0: "#FF5733", 1: "#33C3FF", 2: "#33FF77"}
for cluster in sorted(df_seg["cluster"].unique()):
    seg = df_seg[df_seg["cluster"] == cluster]
    p4.circle(seg["cpi"], seg["usd"], size=8, color=colors_map.get(cluster, "gray"),
             alpha=0.7, legend_label=f"Segment {cluster + 1}")
p4.xaxis.axis_label = "Inflacja CPI [%]"
p4.yaxis.axis_label = "USD/PLN"

dashboard = column(p1, p2, p3, p4)

# === EKSPORT ===
save(dashboard)
print("✓ Zapisano: dashboard_04_bokeh.html")
print("⚠ Bokeh nie wspiera natywnego eksportu do PNG/PDF")
