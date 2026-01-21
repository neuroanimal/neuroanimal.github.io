import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output  # ✅ poprawny import
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
# 5️⃣ Resample miesięczny (ME zamiast M)
# ------------------------------
df_monthly = df.resample("ME").mean()

# ------------------------------
# 6️⃣ Tworzenie aplikacji Dash
# ------------------------------
app = Dash(__name__)
app.title = "Inflacja CPI vs USD/PLN"

# ------------------------------
# 7️⃣ Layout Dash
# ------------------------------
app.layout = html.Div([
    html.H1("Inflacja CPI vs Kurs USD/PLN", style={'textAlign': 'center'}),
    
    html.Div([
        html.Label("Zakres lat:"),
        dcc.RangeSlider(
            id='year-range-slider',
            min=df_monthly.index.year.min(),
            max=df_monthly.index.year.max(),
            value=[df_monthly.index.year.min(), df_monthly.index.year.max()],
            marks={year: str(year) for year in range(df_monthly.index.year.min(), df_monthly.index.year.max()+1, 10)},
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
# 8️⃣ Callback do interaktywnego wykresu
# ------------------------------
@app.callback(
    Output('cpi-usd-graph', 'figure'),
    [Input('year-range-slider', 'value'),
     Input('line-toggle', 'value')]
)
def update_graph(year_range, selected_lines):
    start_year, end_year = year_range
    df_filtered = df_monthly[(df_monthly.index.year >= start_year) & (df_monthly.index.year <= end_year)]
    
    fig = go.Figure()
    
    if 'CPI' in selected_lines:
        fig.add_trace(go.Scatter(
            x=df_filtered.index,
            y=df_filtered["cpi_mo2moyr_gus"],
            mode='lines',
            name="Inflacja CPI (GUS)",
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
            tickfont=dict(color="red")
        ),
        yaxis2=dict(
            title=dict(text="Kurs USD/PLN", font=dict(color="blue")),
            tickfont=dict(color="blue"),
            overlaying="y",
            side="right"
        ),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig

# ------------------------------
# 9️⃣ Uruchomienie serwera
# ------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)


