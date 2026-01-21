import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np

# ------------------------------
# 1️⃣ Wczytanie danych
# ------------------------------
df_nbp = pd.read_csv("data/nbp/all.csv")
df_gus = pd.read_csv("data/gus/all.csv")

df_nbp["date"] = pd.to_datetime(df_nbp["date"], errors="coerce")
df_gus["date"] = pd.to_datetime(df_gus["date"], errors="coerce")

# ------------------------------
# 2️⃣ Przygotowanie danych
# ------------------------------
df_gus["cpi"] = df_gus["cpi_avg_wiki"]
df = pd.merge(df_gus[["cpi"]], df_nbp[["date","USD_PLN"]], left_index=True, right_on="date", how="outer")
df = df.set_index("date").sort_index()

# ------------------------------
# 3️⃣ Funkcja dynamicznej agregacji
# ------------------------------
def aggregate_dynamic(df_subset, max_points=1000):
    n = len(df_subset)
    if n <= max_points:
        return df_subset
    # automatyczne wybranie interwału
    if n > max_points*4:
        return df_subset.resample("Y").mean()
    elif n > max_points*2:
        return df_subset.resample("Q").mean()
    else:
        return df_subset.resample("ME").mean()

# ------------------------------
# 4️⃣ Tworzenie aplikacji Dash
# ------------------------------
app = Dash(__name__)
app.title = "Inflacja CPI vs USD/PLN - Dynamic Zoom"

app.layout = html.Div([
    html.H1("Inflacja CPI vs Kurs USD/PLN", style={'textAlign': 'center'}),
    
    html.Div([
        html.Label("Zakres lat:"),
        dcc.RangeSlider(
            id='year-range-slider',
            min=df.index.year.min(),
            max=df.index.year.max(),
            value=[1977, df.index.year.max()],
            marks={year: str(year) for year in range(df.index.year.min(), df.index.year.max()+1, 10)},
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

    dcc.Graph(
        id='cpi-usd-graph',
        config={'displayModeBar': True, 'scrollZoom': True}
    )
])

# ------------------------------
# 5️⃣ Callback do interaktywnego wykresu
# ------------------------------
@app.callback(
    Output('cpi-usd-graph', 'figure'),
    [Input('year-range-slider', 'value'),
     Input('line-toggle', 'value')]
)
def update_graph(year_range, selected_lines):
    start_year, end_year = year_range
    df_filtered = df[(df.index.year >= start_year) & (df.index.year <= end_year)]
    
    # dynamiczna agregacja
    df_agg = aggregate_dynamic(df_filtered)
    
    fig = go.Figure()
    
    if 'CPI' in selected_lines:
        fig.add_trace(go.Scatter(
            x=df_agg.index,
            y=df_agg["cpi"],
            mode='lines',
            name="Inflacja CPI",
            line=dict(color='red'),
            yaxis="y1"
        ))
    
    if 'USD' in selected_lines:
        fig.add_trace(go.Scatter(
            x=df_agg.index,
            y=df_agg["USD_PLN"],
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
            range=[0, df_agg["cpi"].max()*2]
        ),
        yaxis2=dict(
            title=dict(text="Kurs USD/PLN", font=dict(color="blue")),
            tickfont=dict(color="blue"),
            overlaying="y",
            side="right",
            range=[0, df_agg["USD_PLN"].max()*2]
        ),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig

# ------------------------------
# 6️⃣ Uruchomienie serwera
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)


