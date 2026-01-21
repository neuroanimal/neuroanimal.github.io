import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display as ipython_display

# ------------------------------
# 1️⃣ Wczytanie danych
# ------------------------------
df_nbp_pln_usd = pd.read_csv("data/nbp/all.csv")
df_gus_cpi_hicp = pd.read_csv("data/gus/all.csv")

# ------------------------------
# 2️⃣ Normalizacja kolumn daty
# ------------------------------
df_nbp_pln_usd["date"] = pd.to_datetime(df_nbp_pln_usd["date"], errors="coerce")
df_gus_cpi_hicp["date"] = pd.to_datetime(df_gus_cpi_hicp["date"], errors="coerce")

# ------------------------------
# 3️⃣ Scalanie po dacie
# ------------------------------
df = pd.merge(df_gus_cpi_hicp, df_nbp_pln_usd, on="date", how="outer").sort_values("date")
df = df.set_index("date")

# ------------------------------
# 4️⃣ Redukcja liczby punktów (opcjonalna)
# ------------------------------
# Gęste dane możemy uśrednić np. miesięcznie, by wykres był czytelny i szybki
df_monthly = df.resample("M").mean()

# ------------------------------
# 5️⃣ Podgląd danych
# ------------------------------
ipython_display(df_monthly.tail())

# ------------------------------
# 6️⃣ Wizualizacja
# ------------------------------
plt.figure(figsize=(14, 7))

plt.plot(df_monthly.index, df_monthly["cpi_mo2moyr_gus"], label="Inflacja (CPI, GUS)")
plt.plot(df_monthly.index, df_monthly["USD_PLN"], label="USD/PLN", alpha=0.7)

plt.legend()
plt.title("Inflacja CPI vs Kurs USD/PLN (uśrednione miesięcznie)")
plt.xlabel("Data")
plt.ylabel("Wartość")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

