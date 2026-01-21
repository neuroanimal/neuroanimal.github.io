import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display as ipython_display

df_nbp_pln_usd = pd.read_csv("data/nbp/all.csv", date_format="%Y-%m-%d")
df_gus_cpi_hicp = pd.read_csv("data/gus/all.csv", date_format="%Y-%m-%d")

df = df_gus_cpi_hicp.merge(df_nbp_pln_usd, on="date", how="outer")
ipython_display(df)

plt.figure(figsize=(12,6))
plt.plot(df['date'], df['cpi_mo2moyr_gus'], label="Inflacja (CPI)")
plt.plot(df['date'], df['USD_PLN'], label="USD/PLN", alpha=0.7)
plt.legend()
plt.title("Inflacja CPI vs Kurs EUR/PLN")
plt.show()


