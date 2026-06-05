import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os

# --- CONFIGURATION ---
LOCALE = 'PL'  # Change to EN, FR, DE, RU, IN, AR, FA to switch language
CSV_MARKET = 'market_data.csv'
CSV_NODES = 'nodes_config.csv'
CSV_EDGES = 'edges_config.csv'
CSV_TRANS = 'translations.csv'

def fetch_live_data():
    """Fetches real-time market data from Yahoo Finance."""
    print("Fetching live data from Yahoo Finance...")
    try:
        # Tickers: Brent Oil, USD/PLN, Natural Gas
        tickers = {
            "oil": "BZ=F",
            "usd": "USDPLN=X",
            "gas": "NG=F"
        }
        
        data = {}
        for key, symbol in tickers.items():
            t = yf.Ticker(symbol)
            data[key] = round(t.history(period="1d")['Close'].iloc[-1], 4)

        # Dynamiczne wyliczanie cen paliw w PL (uproszczony model korelacji)
        # Diesel PL ≈ (Brent * USD / 159) + marża/podatki (ok. 3.5 PLN)
        calc_diesel = round((data['oil'] * data['usd'] / 159 * 2) + 3.5, 2) 
        # LNG PL ≈ (Gas * USD / 10) + 1.5
        calc_lng = round((data['gas'] * data['usd'] / 5) + 1.2, 2)

        return {
            'brent': data['oil'],
            'usd_pln': data['usd'],
            'gas': data['gas'],
            'diesel': calc_diesel,
            'lng': calc_lng
        }
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def update_csv_with_live(live_data):
    """Updates the market CSV with full live data set."""
    df = pd.read_csv(CSV_MARKET)
    today = datetime.now().strftime("%d.%m")
    
    new_row = {
        'dates': today,
        'brent': live_data['brent'],
        'gas': live_data['gas'],
        'usd_pln': live_data['usd_pln'],
        'diesel': live_data['diesel'],
        'lng': live_data['lng'],
        'events': 'Live Market Update (Automated)'
    }

    if today in df['dates'].values:
        # Aktualizacja dzisiejszego wiersza
        idx = df[df['dates'] == today].index
        for key, value in new_row.items():
            df.at[idx[0], key] = value
    else:
        # Nowy dzień
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_csv(CSV_MARKET, index=False)
    return df

def create_interactive_dashboard():
    # Load data
    m_df = pd.read_csv(CSV_MARKET)
    t_df = pd.read_csv(CSV_TRANS).set_index('key')[LOCALE].to_dict()

    # --- CHART 2: MARKET IMPACT (PLOTLY) ---
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])

    # Brent Oil
    fig2.add_trace(go.Scatter(x=m_df['dates'], y=m_df['brent'], name=t_df['label_oil'],
                             line=dict(color='red', width=4), marker=dict(size=10)), secondary_y=False)

    # USD/PLN
    fig2.add_trace(go.Scatter(x=m_df['dates'], y=m_df['usd_pln'], name=t_df['label_usd'],
                             line=dict(color='gold', dash='dot', width=3)), secondary_y=True)

    # Diesel PL
    fig2.add_trace(go.Scatter(x=m_df['dates'], y=m_df['diesel'], name=t_df['label_diesel'],
                             line=dict(color='brown', width=2), marker=dict(symbol='square')), secondary_y=True)

    # Layout styling
    fig2.update_layout(
        title=dict(text=t_df['title_market'], x=0, font=dict(size=24)),
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=100, b=50)
    )

    fig2.update_xaxes(title_text="Data")
    fig2.update_yaxes(title_text=t_df['axis_usd'], color="red", secondary_y=False)
    fig2.update_yaxes(title_text=t_df['axis_fx'] + " / " + t_df['axis_pln'], secondary_y=True)

    # Save to HTML
    fig2.write_html("index.html", include_plotlyjs='cdn')
    print("Dashboard saved to index.html")

# Run sequence
live_data = fetch_live_data()
if live_data:
    update_csv_with_live(live_data)
create_interactive_dashboard()



