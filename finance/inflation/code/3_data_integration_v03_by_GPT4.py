import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display as ipython_display

# ------------------------------
# 1️⃣ Wczytanie danych
# ------------------------------
df_nbp = pd.read_csv("data/nbp/all.csv")
df_gus = pd.read_csv("data/gus/all.csv")

# ------------------------------
# 2️⃣ Konwersja dat
# ------------------------------
df_nbp["date"] = pd.to_datetime(df_nbp["date"], errors="coerce")
df_gus["date"] = pd.to_datetime(df_gus["date"], errors="coerce")

# ------------------------------
# 3️⃣ Merge danych
# ------------------------------
df = pd.merge(df_gus, df_nbp, on="date", how="left").sort_values("date")
df = df.set_index("date")

# ------------------------------
# 4️⃣ Filtrowanie od 1917 roku
# ------------------------------
df = df[df.index.year >= 1917]

# ------------------------------
# 5️⃣ Resample miesięczny / średnia dla płynności
# ------------------------------
df_monthly = df.resample("M").mean()

# ------------------------------
# 6️⃣ Wyświetlenie ostatnich wierszy
# ------------------------------
ipython_display(df_monthly.tail())

# ------------------------------
# 7️⃣ Wizualizacja z dwiema osiami Y
# ------------------------------
fig, ax1 = plt.subplots(figsize=(14,7))

# Oś Y1: inflacja
ax1.plot(df_monthly.index, df_monthly["cpi_mo2moyr_gus"], color="tab:red", label="Inflacja CPI (GUS)")
ax1.set_ylabel("Inflacja (%)", color="tab:red")
ax1.tick_params(axis="y", labelcolor="tab:red")

# Oś Y2: kurs USD/PLN
ax2 = ax1.twinx()
ax2.plot(df_monthly.index, df_monthly["USD_PLN"], color="tab:blue", label="USD/PLN", alpha=0.7)
ax2.set_ylabel("Kurs USD/PLN", color="tab:blue")
ax2.tick_params(axis="y", labelcolor="tab:blue")

# Tytuł, legenda, grid
fig.suptitle("Inflacja CPI vs Kurs USD/PLN (od 1917 roku)", fontsize=16)
ax1.grid(True, alpha=0.3)

# Połączenie legend z obu osi
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")

plt.tight_layout()
plt.show()


