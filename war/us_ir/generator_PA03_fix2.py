import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os

# --- KONFIGURACJA ---
HEADERS = {'User-Agent': 'NeuroAnimal-Bot/1.0'}
CSV_MARKET = 'market_data.csv'

def get_safe_float(val):
    try:
        return float(str(val).replace(',', '.').replace(' ', '').split()[0])
    except:
        return None

def fetch_market_data():
    print("--- POBIERANIE DANYCH RYNKOWYCH ---")
    
    # 1. YAHOO FINANCE
    try:
        oil = yf.Ticker("BZ=F").history(period="1d")['Close'].iloc[-1]
        usd = yf.Ticker("USDPLN=X").history(period="1d")['Close'].iloc[-1]
    except:
        oil, usd = None, None

    # 2. AUTOCENTRUM (Detal)
    detal = {}
    try:
        r = requests.get("https://www.autocentrum.pl/paliwa/ceny-paliw/", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for box in soup.find_all('div', class_='fuel-price-item'):
            name = box.find('div', class_='name').get_text(strip=True)
            price = box.find('div', class_='price').get_text(strip=True)
            detal[name] = get_safe_float(price)
    except:
        print("Błąd Autocentrum")

    # 3. E-PETROL (Hurt - Twój parser na divach)
    hurt = {}
    try:
        r = requests.get("https://www.e-petrol.pl/notowania/rynek-krajowy/hurt", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        rows = soup.find_all('div', class_='tab-divs')
        for row in rows:
            cols = row.find_all('div', class_='col')
            if len(cols) == 2:
                label = cols[0].get_text(strip=True)
                val = get_safe_float(cols[1].get_text(strip=True))
                if 'Pb95' in label: hurt['95'] = val / 1000 # Konwersja na litr
                if 'ON' in label: hurt['on'] = val / 1000
        print(f"Hurt pobrany: ON {hurt.get('on'):.2f} zł/l (netto)")
    except:
        print("Błąd e-petrol")

    return oil, usd, detal, hurt

def update_database(oil, usd, detal, hurt):
    if not os.path.exists(CSV_MARKET):
        df = pd.DataFrame(columns=['dates', 'brent', 'usd_pln', 'diesel_detal', 'diesel_hurt'])
    else:
        df = pd.read_csv(CSV_MARKET)

    today = datetime.now().strftime("%d.%m")
    
    # Obliczanie marży (Detal - Hurt) - uproszczone, bo hurt jest netto
    # Możesz tu dodać +VAT do hurtu dla pełnego obrazu
    new_row = {
        'dates': today,
        'brent': oil or (df['brent'].iloc[-1] if not df.empty else 0),
        'usd_pln': usd or (df['usd_pln'].iloc[-1] if not df.empty else 0),
        'diesel_detal': detal.get('ON') or (df['diesel_detal'].iloc[-1] if not df.empty else 0),
        'diesel_hurt': hurt.get('on') or (df['diesel_hurt'].iloc[-1] if not df.empty else 0)
    }

    if today in df['dates'].values:
        df.loc[df['dates'] == today, list(new_row.keys())] = list(new_row.values())
    else:
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    df.to_csv(CSV_MARKET, index=False)
    return df

def create_dashboard(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 1. ROPA BRENT
    fig.add_trace(go.Scatter(x=df['dates'], y=df['brent'], name="Brent Oil (USD)",
                             line=dict(color='#e74c3c', width=3)), secondary_y=False)

    # 2. DIESEL DETAL (Autocentrum)
    fig.add_trace(go.Scatter(x=df['dates'], y=df['diesel_detal'], name="ON Detal (PLN)",
                             line=dict(color='#3498db', width=4)), secondary_y=True)

    # 3. DIESEL HURT (e-petrol)
    fig.add_trace(go.Scatter(x=df['dates'], y=df['diesel_hurt'], name="ON Hurt Netto (PLN)",
                             line=dict(color='#2ecc71', width=2, dash='dash')), secondary_y=True)

    # 4. MARŻA (Wypełnienie między detalam a hurtem)
    fig.add_trace(go.Bar(x=df['dates'], y=df['diesel_detal'] - df['diesel_hurt'], 
                         name="Spread Detal-Hurt", marker_color='rgba(241, 196, 15, 0.3)'), secondary_y=True)

    fig.update_layout(
        title="<b>NeuroAnimal: Analiza Spreadu Paliwowego</b>",
        template="plotly_dark",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.1),
        paper_bgcolor="#111", plot_bgcolor="#111"
    )

    fig.update_yaxes(title_text="Ropa (USD)", secondary_y=False)
    fig.update_yaxes(title_text="Cena/Litr (PLN)", secondary_y=True)

    fig.write_html("index.html")
    print("Dashboard gotowy.")

if __name__ == "__main__":
    o, u, d, h = fetch_market_data()
    df = update_database(o, u, d, h)
    create_dashboard(df)



