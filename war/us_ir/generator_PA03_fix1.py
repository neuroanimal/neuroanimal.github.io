import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io

# --- CONFIGURATION ---
LOCALE = 'PL'
HEADERS = {'User-Agent': 'NeuroAnimal-Bot/1.0'}
CSV_MARKET = 'market_data.csv'

def fetch_epetrol_wholesale():
    """Stabilniejszy scraper dla e-petrol.pl (Hurt)"""
    print("Scraping e-petrol.pl (Hurt)...")
    try:
        url = "https://www.e-petrol.pl/notowania/rynek-krajowy/hurt"
        response = requests.get(url, headers=HEADERS, timeout=10)
        html = response.text

        print(f"Request:\nGET {url}\n\nResponse: {html}\n\n")
        # Używamy pandas read_html na tekście z requests, bo to pozwala na lepszą obsługę błędów
        tables = pd.read_html(io.StringIO(html))
 
        # Szukamy tabeli, która ma kolumnę 'Produkt' lub odpowiednie dane
        for df in tables:
            if 'Produkt' in df.columns or 'Pb95' in df.columns:
                # Wyciągamy dane z pierwszego wiersza (średnia)
                on_val = df.iloc[0]['ON'].split()[0] # Usuwamy 'zł/m3' jeśli jest
                pb95_val = df.iloc[0]['Pb95'].split()[0]
                return float(on_val), float(pb95_val)
        
        print("Nie znaleziono tabeli z cenami hurtowymi.")
        return None, None
    except Exception as e:
        print(f"Błąd e-petrol Hurt: {e}")
        return None, None

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
    """Tworzy czytelny dashboard z dwiema niezależnymi osiami Y"""
    m_df = pd.read_csv(CSV_MARKET)
    
    # Tworzymy figurę z dwiema osiami
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 1. ROPA BRENT (Oś Lewa)
    fig.add_trace(
        go.Scatter(x=m_df['dates'], y=m_df['brent'], name="Ropa Brent (USD)",
                   line=dict(color='firebrick', width=4),
                   mode='lines+markers'),
        secondary_y=False,
    )

    # 2. DIESEL PL (Oś Prawa)
    fig.add_trace(
        go.Scatter(x=m_df['dates'], y=m_df['diesel'], name="Diesel PL (PLN)",
                   line=dict(color='royalblue', width=3, dash='dot'),
                   mode='lines+markers'),
        secondary_y=True,
    )

    # 3. USD/PLN (Oś Prawa - inna skala niż ropa)
    fig.add_trace(
        go.Scatter(x=m_df['dates'], y=m_df['usd_pln'], name="USD/PLN",
                   line=dict(color='gold', width=2),
                   mode='lines'),
        secondary_y=True,
    )

    # Ustawienia estetyczne i naprawa osi
    fig.update_layout(
        title="<b>Analiza Rynku Paliw - NeuroAnimal</b>",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_dark", # Ciemny motyw wygląda profesjonalniej na LinkedIn
        margin=dict(l=50, r=50, t=100, b=100)
    )

    # Opisy osi
    fig.update_yaxes(title_text="<b>Cena Baryłki (USD)</b>", color="firebrick", secondary_y=False)
    fig.update_yaxes(title_text="<b>Cena Detaliczna / Kurs (PLN)</b>", color="royalblue", secondary_y=True)

    # Dodanie źródła
    fig.add_annotation(
        text="Źródła: Autocentrum, e-petrol, Yahoo Finance | Bot: NeuroAnimal-Bot/1.0",
        xref="paper", yref="paper", x=0, y=-0.15, showarrow=False, font=dict(size=10, color="gray")
    )

    fig.write_html("index.html")
    print("Dashboard zapisany poprawnie.")


# --- EXECUTION ---
if __name__ == "__main__":
    update_database()
    create_dashboard()



