import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans

# === PARAMETRY ===
YEAR_START = 1977
YEAR_END = 2024
ROLLING_WINDOW = 10
LOG_SCALE = False

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
sns.set_style("whitegrid")
fig, axes = plt.subplots(3, 1, figsize=(14, 16))

# Wykres 1: CPI + USD
ax1 = axes[0]
ax1_twin = ax1.twinx()
ax1.plot(df_range["date"], df_range["cpi"], color="red", label="Inflacja CPI [%]", linewidth=1.5)
ax1_twin.plot(df_range["date"], df_range["usd"], color="blue", label="Kurs USD/PLN", linewidth=1.5)
if LOG_SCALE:
    ax1_twin.set_yscale("log")
ax1.set_ylabel("Inflacja CPI [%]", color="red")
ax1_twin.set_ylabel("USD/PLN", color="blue")
ax1.set_title(f"Inflacja CPI (PL) vs Kurs USD/PLN ({YEAR_START}-{YEAR_END})")
ax1.legend(loc="upper left")
ax1_twin.legend(loc="upper right")
ax1.grid(True, alpha=0.3)

# Wykres 2: Korelacja
axes[1].plot(df_range["date"], df_range["corr"], color="green", linewidth=1.5)
axes[1].axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.5)
axes[1].set_ylabel("Współczynnik korelacji")
axes[1].set_ylim(-1, 1)
axes[1].set_title(f"Korelacja krocząca ({ROLLING_WINDOW} lat)")
axes[1].grid(True, alpha=0.3)

# Wykres 3: Scatter
colors = ["#FF5733", "#33C3FF", "#33FF77"]
for cluster in sorted(df_seg["cluster"].unique()):
    seg = df_seg[df_seg["cluster"] == cluster]
    axes[2].scatter(seg["cpi"], seg["usd"], c=colors[cluster], label=f"Segment {cluster + 1}", 
                   alpha=0.7, s=50, edgecolors="black", linewidth=0.5)
if LOG_SCALE:
    axes[2].set_yscale("log")
axes[2].set_xlabel("Inflacja CPI [%]")
axes[2].set_ylabel("USD/PLN")
axes[2].set_title("Segmentacja: CPI vs USD")
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()

# === EKSPORT ===
plt.savefig("dashboard_02_pyplot_seaborn.png", dpi=300, bbox_inches="tight")
print("✓ Zapisano: dashboard_02_pyplot_seaborn.png")
plt.savefig("dashboard_02_pyplot_seaborn.pdf", bbox_inches="tight")
print("✓ Zapisano: dashboard_02_pyplot_seaborn.pdf")
plt.close()
