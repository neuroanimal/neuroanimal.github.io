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
    """Fetches real-time Brent Oil and USD/PLN prices."""
    print("Fetching live data from Yahoo Finance...")
    try:
        oil_ticker = yf.Ticker("BZ=F")
        usd_ticker = yf.Ticker("USDPLN=X")
        
        current_oil = oil_ticker.history(period="1d")['Close'].iloc[-1]
        current_usd = usd_ticker.history(period="1d")['Close'].iloc[-1]
        
        return round(current_oil, 2), round(current_usd, 4)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None, None

def update_csv_with_live(oil, usd):
    """Updates the market CSV with the latest data."""
    df = pd.read_csv(CSV_MARKET)
    today = datetime.now().strftime("%d.%m")
    
    if today in df['dates'].values:
        # Update existing record for today
        idx = df[df['dates'] == today].index
        df.at[idx[0], 'brent'] = oil
        df.at[idx[0], 'usd_pln'] = usd
    else:
        # Append new record (using last known values for gas/diesel/lng)
        new_row = {
            'dates': today,
            'brent': oil,
            'gas': df['gas'].iloc[-1],
            'usd_pln': usd,
            'diesel': df['diesel'].iloc[-1],
            'lng': df['lng'].iloc[-1],
            'events': 'Live Market Update'
        }
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
oil, usd = fetch_live_data()
if oil and usd:
    update_csv_with_live(oil, usd)
create_interactive_dashboard()


