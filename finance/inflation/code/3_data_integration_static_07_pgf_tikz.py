import pandas as pd
import matplotlib.pyplot as plt
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

# === DASHBOARD Z PGF/TikZ ===
plt.rcParams.update({
    "pgf.texsystem": "pdflatex",
    "font.family": "serif",
    "text.usetex": True,
    "pgf.rcfonts": False,
})

fig, axes = plt.subplots(3, 1, figsize=(10, 12))

# Wykres 1
ax1 = axes[0]
ax1_twin = ax1.twinx()
ax1.plot(df_range["date"], df_range["cpi"], color="red", label="CPI", linewidth=1)
ax1_twin.plot(df_range["date"], df_range["usd"], color="blue", label="USD", linewidth=1)
ax1.set_ylabel("CPI [\\%]")
ax1_twin.set_ylabel("USD/PLN")
ax1.set_title("Inflacja CPI vs USD/PLN")

# Wykres 2
axes[1].plot(df_range["date"], df_range["corr"], color="green", linewidth=1)
axes[1].set_ylabel("Korelacja")
axes[1].set_title(f"Korelacja kroczaca ({ROLLING_WINDOW} lat)")

# Wykres 3
colors = ["#FF5733", "#33C3FF", "#33FF77"]
for cluster in sorted(df_seg["cluster"].unique()):
    seg = df_seg[df_seg["cluster"] == cluster]
    axes[2].scatter(seg["cpi"], seg["usd"], c=colors[cluster], s=20, alpha=0.7)
axes[2].set_xlabel("CPI [\\%]")
axes[2].set_ylabel("USD/PLN")
axes[2].set_title("Segmentacja")

plt.tight_layout()

# === EKSPORT ===
plt.savefig("dashboard_07_pgf_tikz.pgf")
print("✓ Zapisano: dashboard_07_pgf_tikz.pgf (dla LaTeX)")
plt.savefig("dashboard_07_pgf_tikz.pdf")
print("✓ Zapisano: dashboard_07_pgf_tikz.pdf")
plt.close()
