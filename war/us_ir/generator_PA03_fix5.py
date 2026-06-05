import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os

# --- KONFIGURACJA ---
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
CSV_MARKET = 'market_data.csv'

def get_safe_float(val):
    if not val: return None
    try:
        # Obsługa formatów: "6,50 zł", "6.50", "6 495,20"
        clean = str(val).replace('zł', '').replace(',', '.').replace('\xa0', '').replace(' ', '').strip()
        return float(clean)
    except:
        return None

def fetch_market_data():
    print("\n--- 1. POBIERANIE DANYCH GIEŁDOWYCH (Yahoo) ---")
    oil, usd = None, None
    try:
        oil = yf.Ticker("BZ=F").history(period="1d")['Close'].iloc[-1]
        usd = yf.Ticker("USDPLN=X").history(period="1d")['Close'].iloc[-1]
        print(f"  > Ropa Brent: {oil:.2f} USD")
        print(f"  > Kurs USD:   {usd:.4f} PLN")
    except Exception as e:
        print(f"  ! Błąd Yahoo: {e}")

    print("\n--- 2. POBIERANIE CEN DETALICZNYCH (Autocentrum) ---")
    detal = {}
    try:
        r = requests.get("https://www.autocentrum.pl/paliwa/ceny-paliw/", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Nowy selektor: szukamy wewnątrz wrapperów paliw
        items = soup.select('.fuel-price-item')
        for item in items:
            name_tag = item.select_one('.name')
            price_tag = item.select_one('.price')
            if name_tag and price_tag:
                name = name_tag.get_text(strip=True)
                val = get_safe_float(price_tag.get_text(strip=True))
                detal[name] = val
                print(f"  > Detal {name}: {val} PLN/l")
    except Exception as e:
        print(f"  ! Błąd Autocentrum: {e}")

    print("\n--- 3. POBIERANIE CEN HURTOWYCH (e-petrol) ---")
    hurt = {}
    try:
        r = requests.get("https://www.e-petrol.pl/notowania/rynek-krajowy/hurt", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Twoja sprawdzona metoda na divach
        rows = soup.find_all('div', class_='tab-divs')
        for row in rows:
            cols = row.find_all('div', class_='col')
            if len(cols) == 2:
                label = cols[0].get_text(strip=True)
                val = get_safe_float(cols[1].get_text(strip=True))
                if val:
                    if 'Pb95' in label: hurt['95'] = val / 1000
                    if 'ON' in label: hurt['on'] = val / 1000
        
        if 'on' in hurt:
            print(f"  > Hurt ON (netto):  {hurt['on']:.2f} PLN/l")
            print(f"  > Hurt ON (brutto): {hurt['on']*1.23:.2f} PLN/l")
    except Exception as e:
        print(f"  ! Błąd e-petrol: {e}")

    return oil, usd, detal, hurt

def update_database(oil, usd, detal, hurt):
    target_cols = ['dates', 'brent', 'usd_pln', 'diesel_detal', 'diesel_hurt']
    
    if not os.path.exists(CSV_MARKET):
        df = pd.DataFrame(columns=target_cols)
    else:
        df = pd.read_csv(CSV_MARKET)
        # Migracja starych nazw kolumn jeśli istnieją
        if 'diesel' in df.columns: df = df.rename(columns={'diesel': 'diesel_detal'})
        for col in target_cols:
            if col not in df.columns: df[col] = 0.0

    today = datetime.now().strftime("%d.%m")
    
    def get_last(col_name):
        return df[col_name].iloc[-1] if not df.empty and col_name in df.columns else 0.0

    # Obliczamy Hurt Brutto dla ON (bo na stacji płacisz brutto)
    on_brutto = (hurt.get('on') * 1.23) if hurt.get('on') else None

    new_row = {
        'dates': today,
        'brent': oil if oil else get_last('brent'),
        'usd_pln': usd if usd else get_last('usd_pln'),
        'diesel_detal': detal.get('ON') if detal.get('ON') else get_last('diesel_detal'),
        'diesel_hurt': on_brutto if on_brutto else get_last('diesel_hurt')
    }

    if today in df['dates'].values:
        df.loc[df['dates'] == today, list(new_row.keys())] = list(new_row.values())
    else:
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    df.to_csv(CSV_MARKET, index=False)
    return df

def create_dashboard(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Ropa (lewa oś)
    fig.add_trace(go.Scatter(x=df['dates'], y=df['brent'], name="Brent (USD)", 
                             line=dict(color='#e74c3c', width=3)), secondary_y=False)
    
    # Ceny paliw (prawa oś)
    fig.add_trace(go.Scatter(x=df['dates'], y=df['diesel_detal'], name="ON Detal (PLN)",
                             line=dict(color='#3498db', width=4)), secondary_y=True)
    
    fig.add_trace(go.Scatter(x=df['dates'], y=df['diesel_hurt'], name="ON Hurt Brutto (PLN)",
                             line=dict(color='#2ecc71', width=2, dash='dot')), secondary_y=True)

    # Spread (Marża stacji)
    fig.add_trace(go.Bar(x=df['dates'], y=df['diesel_detal'] - df['diesel_hurt'],
                         name="Spread (Marża)", marker_color='rgba(241, 196, 15, 0.2)'), secondary_y=True)

    fig.update_layout(
        title="<b>Rynek Paliw: Brent vs Detal vs Hurt</b>",
        template="plotly_dark",
        paper_bgcolor="#111", plot_bgcolor="#111",
        legend=dict(orientation="h", y=1.1)
    )
    
    fig.write_html("index.html")
    print("Dashboard wygenerowany: index.html")

if __name__ == "__main__":
    o, u, d, h = fetch_market_data()
    df = update_database(o, u, d, h)
    create_dashboard(df)
    print("\n--- GOTOWE ---")


