import pandas as pd
from great_tables import GT
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

# === AGREGACJA DANYCH ===
summary = df_range.groupby("year").agg({
    "cpi": ["mean", "min", "max"],
    "usd": ["mean", "min", "max"],
    "corr": "mean"
}).round(2)
summary.columns = ["CPI_avg", "CPI_min", "CPI_max", "USD_avg", "USD_min", "USD_max", "Corr"]
summary = summary.reset_index()

seg_stats = df_seg.groupby("cluster").agg({
    "cpi": ["mean", "std"],
    "usd": ["mean", "std"],
    "date": "count"
}).round(2)
seg_stats.columns = ["CPI_mean", "CPI_std", "USD_mean", "USD_std", "Count"]
seg_stats = seg_stats.reset_index()
seg_stats["cluster"] = seg_stats["cluster"] + 1

# === DASHBOARD ===
gt_summary = (
    GT(summary.tail(20).reset_index(drop=True))
    .tab_header(
        title=f"Dashboard: Inflacja CPI vs USD/PLN ({YEAR_START}-{YEAR_END})",
        subtitle="Podsumowanie roczne (ostatnie 20 lat)"
    )
    .fmt_number(columns=["CPI_avg", "CPI_min", "CPI_max", "USD_avg", "USD_min", "USD_max", "Corr"], decimals=2)
    .data_color(columns=["Corr"], palette=["red", "white", "green"], domain=[-1, 1])
)

gt_segments = (
    GT(seg_stats)
    .tab_header(
        title="Segmentacja klastrów",
        subtitle=f"K-means (k=3) na danych CPI vs USD"
    )
    .fmt_number(columns=["CPI_mean", "CPI_std", "USD_mean", "USD_std"], decimals=2)
)

# === EKSPORT ===
with open("dashboard_05_great_tables_summary.html", "w") as f:
    f.write(gt_summary.as_raw_html())
print("✓ Zapisano: dashboard_05_great_tables_summary.html")

with open("dashboard_05_great_tables_segments.html", "w") as f:
    f.write(gt_segments.as_raw_html())
print("✓ Zapisano: dashboard_05_great_tables_segments.html")

try:
    gt_summary.save("dashboard_05_great_tables_summary.png")
    print("✓ Zapisano: dashboard_05_great_tables_summary.png")
except:
    print("⚠ PNG wymaga selenium + webdriver")

print("⚠ Great Tables jest zoptymalizowane dla tabel, nie wykresów")
