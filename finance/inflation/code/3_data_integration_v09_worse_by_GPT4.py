import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
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
# 4️⃣ Filtrowanie danych CPI od 1917
# ------------------------------
# Nowa kolumna z danymi z Wikipedii
df["cpi"] = df["cpi_avg_wiki"]

# ------------------------------
# 5️⃣ Resample miesięczny (dla NBP) i roczny dla CPI z wiki
# ------------------------------
df_nbp_monthly = df_nbp.set_index("date").resample("ME").mean()
df_cpi_yearly = df["cpi"].resample("Y").mean()

# ------------------------------
# 6️⃣ Połączenie danych w jeden DataFrame
# ------------------------------
df_combined = pd.concat([df_cpi_yearly, df_nbp_monthly["USD_PLN"]], axis=1)

# ------------------------------
# 7️⃣ Tworzenie aplikacji Dash
# ------------------------------
app = Dash(__name__)
app.title = "Inflacja CPI vs USD/PLN"

# ------------------------------
# 8️⃣ Layout Dash
# ------------------------------
app.layout = html.Div([
    html.H1("Inflacja CPI vs Kurs USD/PLN", style={'textAlign': 'center'}),
    
    html.Div([
        html.Label("Zakres lat:"),
        dcc.RangeSlider(
            id='year-range-slider',
            min=df_combined.index.year.min(),
            max=df_combined.index.year.max(),
            value=[1977, df_combined.index.year.max()],  # domyślnie od 1977
            marks={year: str(year) for year in range(df_combined.index.year.min(), df_combined.index.year.max()+1, 10)},
            step=1
        ),
    ], style={'margin': '20px'}),

    html.Div([
        dcc.Checklist(
            id='line-toggle',
            options=[
                {'label': 'Inflacja CPI', 'value': 'CPI'},
                {'label': 'USD/PLN', 'value': 'USD'}
            ],
            value=['CPI', 'USD'],
            inline=True
        )
    ], style={'margin': '20px'}),

    dcc.Graph(id='cpi-usd-graph')
])

# ------------------------------
# 9️⃣ Callback do interaktywnego wykresu
# ------------------------------
@app.callback(
    Output('cpi-usd-graph', 'figure'),
    [Input('year-range-slider', 'value'),
     Input('line-toggle', 'value')]
)
def update_graph(year_range, selected_lines):
    start_year, end_year = year_range
    df_filtered = df_combined[(df_combined.index.year >= start_year) & (df_combined.index.year <= end_year)]
    
    fig = go.Figure()
    
    if 'CPI' in selected_lines:
        fig.add_trace(go.Scatter(
            x=df_filtered.index,
            y=df_filtered["cpi"],
            mode='lines',
            name="Inflacja CPI (Wiki)",
            line=dict(color='red'),
            yaxis="y1"
        ))
    
    if 'USD' in selected_lines:
        fig.add_trace(go.Scatter(
            x=df_filtered.index,
            y=df_filtered["USD_PLN"],
            mode='lines',
            name="USD/PLN",
            line=dict(color='blue'),
            yaxis="y2"
        ))
    
    fig.update_layout(
        xaxis_title="Data",
        yaxis=dict(
            title=dict(text="Inflacja (%)", font=dict(color="red")),
            tickfont=dict(color="red"),
            range=[0, df_filtered["cpi"].max()*2]  # dwukrotnie większa skala osi Y
        ),
        yaxis2=dict(
            title=dict(text="Kurs USD/PLN", font=dict(color="blue")),
            tickfont=dict(color="blue"),
            overlaying="y",
            side="right",
            range=[0, df_filtered["USD_PLN"].max()*2]  # dwukrotnie większa skala osi Y
        ),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig

# ------------------------------
# 10️⃣ Uruchomienie serwera (Dash 3.x+)
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)


