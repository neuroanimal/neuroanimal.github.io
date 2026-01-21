import pandas as pd
import plotly.graph_objects as go

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
# 3️⃣ Merge po dacie
# ------------------------------
df = pd.merge(df_gus, df_nbp, on="date", how="left").sort_values("date")
df = df.set_index("date")

# ------------------------------
# 4️⃣ Filtrowanie od 1917
# ------------------------------
df = df[df.index.year >= 1917]

# ------------------------------
# 5️⃣ Resample miesięczny dla płynności
# ------------------------------
df_monthly = df.resample("M").mean()

# ------------------------------
# 6️⃣ Tworzenie wykresu interaktywnego
# ------------------------------
fig = go.Figure()

# Inflacja CPI (lewa oś Y)
fig.add_trace(go.Scatter(
    x=df_monthly.index,
    y=df_monthly["cpi_mo2moyr_gus"],
    mode='lines',
    name="Inflacja CPI (GUS)",
    line=dict(color='red'),
    yaxis="y1"
))

# Kurs USD/PLN (prawa oś Y)
fig.add_trace(go.Scatter(
    x=df_monthly.index,
    y=df_monthly["USD_PLN"],
    mode='lines',
    name="USD/PLN",
    line=dict(color='blue'),
    yaxis="y2"
))

# ------------------------------
# 7️⃣ Konfiguracja osi i layout
# ------------------------------
fig.update_layout(
    title="Inflacja CPI vs Kurs USD/PLN (od 1917 roku)",
    xaxis_title="Data",
    yaxis=dict(
        title=dict(
            text="Inflacja (%)",
            font=dict(color="red")
        ),
        tickfont=dict(color="red"),
    ),
    yaxis2=dict(
        title=dict(
            text="Kurs USD/PLN",
            font=dict(color="blue")
        ),
        tickfont=dict(color="blue"),
        overlaying="y",
        side="right"
    ),
    legend=dict(x=0.01, y=0.99),
    template="plotly_white",
    hovermode="x unified"
)

# ------------------------------
# 8️⃣ Wyświetlenie
# ------------------------------
fig.show()


