import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os

# --- KONFIGURACJA ---
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
CSV_MARKET = 'market_data.csv'

def get_safe_float(val):
    if not val: return None
    try:
        clean = str(val).replace('zł', '').replace(',', '.').replace('\xa0', '').replace(' ', '').strip()
        return float(clean)
    except: return None

def fetch_all_data():
    print("\n--- 1. POBIERANIE HISTORII (Yahoo Finance) ---")
    # Pobieramy ostatnie 30 dni dla ciągłości wykresu
    oil_hist = yf.Ticker("BZ=F").history(period="1mo")['Close']
    usd_hist = yf.Ticker("USDPLN=X").history(period="1mo")['Close']
    
    # Tworzymy bazowy DataFrame z datami z Yahoo
    df = pd.DataFrame({
        'date': oil_hist.index.strftime('%Y-%m-%d'),
        'brent': oil_hist.values,
        'usd_pln': usd_hist.reindex(oil_hist.index, method='ffill').values
    })

    print("\n--- 2. POBIERANIE CEN BIEŻĄCYCH (Detal + Hurt) ---")
    # Detal (Autocentrum)
    detal_on = None
    try:
        r = requests.get("https://www.autocentrum.pl/paliwa/ceny-paliw/", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('.fuel-price-item'):
            if 'ON' in item.select_one('.name').get_text():
                detal_on = get_safe_float(item.select_one('.price').get_text())
                break
    except: print("Błąd Autocentrum")

    # Hurt (e-petrol - Twoja metoda na divach)
    hurt_on_netto = None
    try:
        r = requests.get("https://www.e-petrol.pl/notowania/rynek-krajowy/hurt", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for row in soup.find_all('div', class_='tab-divs'):
            cols = row.find_all('div', class_='col')
            if len(cols) == 2 and 'ON' in cols[0].text:
                hurt_on_netto = get_safe_float(cols[1].text) / 1000
                break
    except: print("Błąd e-petrol")

    # Dodajemy dzisiejsze dane do DataFrame
    today_str = datetime.now().strftime('%Y-%m-%d')
    hurt_on_brutto = (hurt_on_netto * 1.23) if hurt_on_netto else None
    
    # Aktualizujemy ostatni wiersz lub dodajemy nowy
    if today_str in df['date'].values:
        idx = df.index[df['date'] == today_str][0]
        df.at[idx, 'diesel_detal'] = detal_on
        df.at[idx, 'diesel_hurt_brutto'] = hurt_on_brutto
    else:
        new_row = {'date': today_str, 'brent': oil_hist.iloc[-1], 'usd_pln': usd_hist.iloc[-1], 
                   'diesel_detal': detal_on, 'diesel_hurt_brutto': hurt_on_brutto}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Uzupełniamy braki w detal/hurt poprzednimi wartościami (ffill), żeby wykres nie był dziurawy
    df['diesel_detal'] = df['diesel_detal'].ffill()
    df['diesel_hurt_brutto'] = df['diesel_hurt_brutto'].ffill()
    
    return df

def create_rich_dashboard(df):
    # Tworzymy 3 subloty (jeden pod drugim)
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=("1. Ropa Brent (USD) vs Kurs Dolara (PLN)", 
                        "2. Ceny ON: Detal vs Hurt Brutto (PLN)", 
                        "3. Analiza Marży / Spreadu (PLN)")
    )

    # WYKRES 1: Ropa i USD
    fig.add_trace(go.Scatter(x=df['date'], y=df['brent'], name="Brent (USD)", line=dict(color='#e74c3c')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['date'], y=df['usd_pln'], name="USD/PLN", line=dict(color='#f1c40f')), row=1, col=1)

    # WYKRES 2: Paliwa
    fig.add_trace(go.Scatter(x=df['date'], y=df['diesel_detal'], name="ON Detal (PLN)", line=dict(color='#3498db', width=4)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['date'], y=df['diesel_hurt_brutto'], name="ON Hurt Brutto (PLN)", line=dict(color='#2ecc71', dash='dot')), row=2, col=1)

    # WYKRES 3: Marża (Spread)
    spread = df['diesel_detal'] - df['diesel_hurt_brutto']
    fig.add_trace(go.Bar(x=df['date'], y=spread, name="Marża (Spread)", marker_color='#9b59b6'), row=3, col=1)

    fig.update_layout(height=900, template="plotly_dark", title="<b>NeuroAnimal: Raport Paliwowy v3.0</b>", showlegend=True)
    fig.write_html("index.html")
    print("Dashboard v3.0 gotowy.")

if __name__ == "__main__":
    data = fetch_all_data()
    create_rich_dashboard(data)


