import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
CSV_MARKET = 'market_data.csv'

def get_safe_float(val):
    try:
        return float(str(val).replace(',', '.').replace(' ', '').split()[0])
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
        boxes = soup.find_all('div', class_='fuel-price-item')
        for box in boxes:
            name = box.find('div', class_='name').get_text(strip=True)
            price = box.find('div', class_='price').get_text(strip=True)
            val = get_safe_float(price)
            detal[name] = val
            print(f"  > Detal {name}: {val} PLN/l")
    except Exception as e:
        print(f"  ! Błąd Autocentrum: {e}")

    print("\n--- 3. POBIERANIE CEN HURTOWYCH (e-petrol) ---")
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
                if 'Pb95' in label: hurt['95'] = val / 1000
                if 'ON' in label: hurt['on'] = val / 1000
        
        on_brutto = hurt.get('on', 0) * 1.23
        print(f"  > Hurt ON (netto):  {hurt.get('on'):.2f} PLN/l")
        print(f"  > Hurt ON (brutto): {on_brutto:.2f} PLN/l")
    except Exception as e:
        print(f"  ! Błąd e-petrol: {e}")

    return oil, usd, detal, hurt

# ... (funkcja update_database i create_dashboard zostają jak w fix2/3) ...

if __name__ == "__main__":
    o, u, d, h = fetch_market_data()
    df = update_database(o, u, d, h)
    create_dashboard(df)
    print("\n--- PROCES ZAKOŃCZONY SUKCESEM ---")



