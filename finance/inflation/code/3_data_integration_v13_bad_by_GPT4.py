import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# ------------------------------
# 1️⃣ Wczytanie danych
# ------------------------------
df_nbp = pd.read_csv("data/nbp/all.csv")       # kolumny: date, USD_PLN
df_gus = pd.read_csv("data/gus/all.csv")       # kolumny: year, cpi_avg_wiki

# ------------------------------
# 2️⃣ Konwersja dat
# ------------------------------
df_nbp["date"] = pd.to_datetime(df_nbp["date"], errors="coerce")

df_gus["year"] = df_gus["year"].astype(int)
df_gus["date"] = pd.to_datetime(df_gus["year"].astype(str) + "-12-31")
df_gus["cpi"] = df_gus["cpi_avg_wiki"]

# ------------------------------
# 3️⃣ Połączenie danych
# ------------------------------
df = pd.merge(df_gus[["date","cpi"]], df_nbp[["date","USD_PLN"]], on="date", how="outer")
df = df.sort_values("date").set_index("date")

# ------------------------------
# 4️⃣ Funkcja dynamicznej agregacji
# ------------------------------
def aggregate_dynamic(df_subset, max_points=1000):
    n = len(df_subset)
    if n <= max_points:
        return df_subset
    if n > max_points*4:
        return df_subset.resample("Y").mean()
    elif n > max_points*2:
        return df_subset.resample("Q").mean()
    else:
        return df_subset.resample("ME").mean()

# ------------------------------
# 5️⃣ Aplikacja Dash
# ------------------------------
app = Dash(__name__)
app.title = "Inflacja CPI vs USD/PLN - Dashboard"

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

    dcc.Graph(id='cpi-usd-graph', config={'scrollZoom': True})
])

# ------------------------------
# 6️⃣ Callback interaktywny
# ------------------------------
@app.callback(
    Output('cpi-usd-graph', 'figure'),
    [Input('year-range-slider', 'value'),
     Input('line-toggle', 'value')]
)
def update_graph(year_range, selected_lines):
    start_year, end_year = year_range
    df_filtered = df[(df.index.year >= start_year) & (df.index.year <= end_year)]
    
    df_agg = aggregate_dynamic(df_filtered)
    
    fig = go.Figure()
    
    if 'CPI' in selected_lines:
        fig.add_trace(go.Scatter(
            x=df_agg.index, y=df_agg["cpi"],
            mode='lines+markers',
            name="Inflacja CPI",
            line=dict(color='red'),
            marker=dict(size=4),
            yaxis="y1",
            hovertemplate="Data: %{x|%Y-%m-%d}<br>CPI: %{y:.2f}%<extra></extra>"
        ))
    
    if 'USD' in selected_lines:
        fig.add_trace(go.Scatter(
            x=df_agg.index, y=df_agg["USD_PLN"],
            mode='lines+markers',
            name="USD/PLN",
            line=dict(color='blue'),
            marker=dict(size=4),
            yaxis="y2",
            hovertemplate="Data: %{x|%Y-%m-%d}<br>USD/PLN: %{y:.2f}<extra></extra>"
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
            overlaying="y", side="right",
            range=[0, df_agg["USD_PLN"].max()*2]
        ),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig

# ------------------------------
# 7️⃣ Uruchomienie Dash
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)


