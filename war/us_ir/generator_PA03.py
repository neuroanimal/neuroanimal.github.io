import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os

# --- CONFIGURATION ---
LOCALE = 'PL'
HEADERS = {'User-Agent': 'NeuroAnimal-Bot/1.0'}
CSV_MARKET = 'market_data.csv'
CSV_TRANS = 'translations.csv'

# --- SCRAPER MODULES ---

def fetch_autocentrum_prices():
    """Pobiera ceny detaliczne z Autocentrum.pl"""
    print("Scraping Autocentrum.pl...")
    try:
        url = "https://www.autocentrum.pl/paliwa/ceny-paliw/"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        prices = {}
        # Szukamy głównej tabeli/listy cen
        # Uwaga: Selektory CSS mogą wymagać korekty, jeśli portal zmieni layout
        items = soup.find_all('div', class_='fuel-price-item')
        for item in items:
            name = item.find('div', class_='name').get_text(strip=True)
            val = item.find('div', class_='price').get_text(strip=True).replace(',', '.')
            prices[name] = float(val)
            
        update_info = soup.find('div', class_='last-update').get_text(strip=True)
        return prices, update_info
    except Exception as e:
        print(f"Błąd Autocentrum: {e}")
        return None, None

def fetch_epetrol_wholesale():
    """Pobiera dane hurtowe z e-petrol.pl"""
    print("Scraping e-petrol.pl (Hurt)...")
    try:
        url = "https://www.e-petrol.pl/notowania/rynek-krajowy/hurt"
        # read_html zwraca listę wszystkich tabel na stronie
        tables = pd.read_html(url, storage_options={'User-Agent': 'NeuroAnimal-Bot/1.0'})
        
        # Tabela 0 to zazwyczaj średnie ceny w rafineriach
        avg_wholesale = tables[0]
        # Wyciągamy najnowszy wiersz (ON i PB95)
        latest_on = avg_wholesale.iloc[0]['ON']
        latest_pb95 = avg_wholesale.iloc[0]['Pb95']
        
        return float(latest_on), float(latest_pb95)
    except Exception as e:
        print(f"Błąd e-petrol Hurt: {e}")
        return None, None

def fetch_yahoo_finance():
    """Pobiera surowce i waluty."""
    print("Fetching Yahoo Finance...")
    try:
        tickers = {"oil": "BZ=F", "usd": "USDPLN=X", "gas": "NG=F"}
        data = {}
        for key, symbol in tickers.items():
            t = yf.Ticker(symbol)
            data[key] = round(t.history(period="1d")['Close'].iloc[-1], 4)
        return data
    except Exception as e:
        print(f"Błąd Yahoo: {e}")
        return None

# --- MAIN UPDATER ---

def update_database():
    m_df = pd.read_csv(CSV_MARKET)
    today = datetime.now().strftime("%d.%m")
    
    # 1. Dane z Yahoo (zawsze aktualne)
    yahoo = fetch_yahoo_finance()
    
    # 2. Dane z Autocentrum (detal)
    auto_prices, auto_upd = fetch_autocentrum_prices()
    
    # 3. Dane z e-petrol (hurt)
    hurt_on, hurt_95 = fetch_epetrol_wholesale()

    new_row = {
        'dates': today,
        'brent': yahoo['oil'] if yahoo else m_df['brent'].iloc[-1],
        'gas': yahoo['gas'] if yahoo else m_df['gas'].iloc[-1],
        'usd_pln': yahoo['usd'] if yahoo else m_df['usd_pln'].iloc[-1],
        'diesel': auto_prices.get('ON', m_df['diesel'].iloc[-1]) if auto_prices else m_df['diesel'].iloc[-1],
        'lng': auto_prices.get('LPG', m_df['lng'].iloc[-1]) if auto_prices else m_df['lng'].iloc[-1],
        'events': f"Auto-Update ({auto_upd if auto_upd else 'Live'})"
    }

    # Inteligentne scalanie: jeśli data istnieje, aktualizuj. Jeśli nie, dodaj.
    if today in m_df['dates'].values:
        idx = m_df[m_df['dates'] == today].index
        for key, val in new_row.items():
            m_df.at[idx[0], key] = val
    else:
        m_df = pd.concat([m_df, pd.DataFrame([new_row])], ignore_index=True)

    m_df.to_csv(CSV_MARKET, index=False)
    return m_df

# --- DASHBOARD GENERATOR ---

def create_dashboard():
    m_df = pd.read_csv(CSV_MARKET)
    # Proste zabezpieczenie przed brakiem pliku tłumaczeń
    try:
        t_df = pd.read_csv(CSV_TRANS).set_index('key')[LOCALE].to_dict()
    except:
        t_df = {'title_market': 'Market Analysis', 'label_oil': 'Brent', 'label_usd': 'USD/PLN'}

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Wykresy
    fig.add_trace(go.Scatter(x=m_df['dates'], y=m_df['brent'], name="Brent Oil ($)", line=dict(color='red', width=3)), secondary_y=False)
    fig.add_trace(go.Scatter(x=m_df['dates'], y=m_df['diesel'], name="Diesel PL (zł)", line=dict(color='black', width=2)), secondary_y=True)
    fig.add_trace(go.Scatter(x=m_df['dates'], y=m_df['usd_pln'], name="USD/PLN", line=dict(color='gold', dash='dot')), secondary_y=True)

    # Stopka z źródłami (Punkt 3 Twojej listy)
    sources_text = (
        "Źródła: Dane detaliczne: Autocentrum.pl | "
        "Dane hurtowe: e-petrol.pl | "
        "Surowce i Waluty: Yahoo Finance API | "
        "Bot: NeuroAnimal-Bot/1.0"
    )
    
    fig.update_layout(
        title=dict(text="NEUROANIMAL GEOPOLITICAL DASHBOARD v3.0", font=dict(size=22)),
        template="plotly_white",
        annotations=[dict(
            xref="paper", yref="paper", x=0.5, y=-0.2,
            text=sources_text, showarrow=False, font=dict(size=10, color="gray")
        )]
    )

    fig.write_html("index.html")
    print("Dashboard gotowy: index.html")

# --- EXECUTION ---
if __name__ == "__main__":
    update_database()
    create_dashboard()


