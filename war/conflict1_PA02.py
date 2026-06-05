import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np

# --- 1. PRZYGOTOWANIE DANYCH (MARZEC 2026) ---

# Dane do wykresu cenowego (Polska + Świat)
data = {
    'Data': ['28.02', '02.03', '08.03', '10.03', '11.03', '12.03', '13.03', '14.03'],
    'Brent_Oil': [72, 77, 126, 83, 91, 96, 104, 110],
    'USD_PLN': [4.05, 4.15, 4.50, 4.40, 4.38, 4.35, 4.42, 4.45],
    'ON_Polska': [6.80, 7.10, 8.50, 8.20, 8.15, 7.95, 8.25, 8.40],
    'LNG_Stacje': [2.90, 3.05, 4.20, 3.80, 3.75, 3.60, 3.90, 4.10],
    'Event': ['Naloty', 'Atak Zatoka', 'Blokada Ormuz', 'Ropa RU', 'Drony Dubaj', 'Rezerwy IEA', 'Ostrzał Doha', 'Ewakuacja']
}
df = pd.DataFrame(data)

# Dane do mapy relacji (Nody: Nazwa, Etnos, Wyznanie)
nodes_info = {
    "Iran": {"etnos": "Persowie", "wiara": "Szyici"},
    "Hezbollah": {"etnos": "Arabowie", "wiara": "Szyici"},
    "Hamas": {"etnos": "Arabowie", "wiara": "Sunnici"},
    "Izrael": {"etnos": "Żydzi", "wiara": "Judaizm"},
    "USA": {"etnos": "Zachód", "wiara": "Sekularni/Chrz."},
    "Katar": {"etnos": "Arabowie", "wiara": "Sunnici"},
    "S. Arabia": {"etnos": "Arabowie", "wiara": "Sunnici"},
    "Kurdowie": {"etnos": "Kurdowie", "wiara": "Sunnici"},
    "Huti": {"etnos": "Arabowie", "wiara": "Szyici (Zajdyci)"},
    "Syria": {"etnos": "Arabowie", "wiara": "Alawici"}
}

# Relacje (Start, Koniec, Kolor: green=sojusz, red=wróg, orange=neutral/napięty)
relations = [
    ("Iran", "Hezbollah", "green"), ("Iran", "Huti", "green"), ("Iran", "Syria", "green"),
    ("Iran", "Hamas", "green"), ("Iran", "Izrael", "red"), ("Iran", "USA", "red"),
    ("USA", "Izrael", "green"), ("USA", "Katar", "green"), ("Iran", "Katar", "red"),
    ("S. Arabia", "Iran", "orange"), ("S. Arabia", "USA", "green"), ("Kurdowie", "USA", "green"),
    ("Kurdowie", "Iran", "red"), ("Hamas", "Izrael", "red"), ("Hezbollah", "Izrael", "red")
]

# --- 2. GENEROWANIE WIZUALIZACJI ---

fig = plt.figure(figsize=(16, 22))
plt.rcParams['font.family'] = 'sans-serif'

# DIAGRAM 1: Zaawansowana Mapa Relacji
ax1 = fig.add_subplot(311)
G = nx.Graph()
for node in nodes_info: G.add_node(node)
G.add_edges_from([(r[0], r[1]) for r in relations])

pos = nx.shell_layout(G)
edge_colors = [r[2] for r in relations]

# Rysowanie krawędzi
nx.draw_networkx_edges(G, pos, edgelist=[(r[0], r[1]) for r in relations], 
                       edge_color=edge_colors, width=2.5, alpha=0.7, ax=ax1)

# Rysowanie nodów jako prostokątnych kart
for node, (x, y) in pos.items():
    info = nodes_info[node]
    label = f"{node}\n---\n{info['etnos']}\n{info['wiara']}"
    ax1.text(x, y, label, size=9, ha='center', va='center', fontweight='bold',
             bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

ax1.set_title("STRUKTURA KONFLIKTU (MARZEC 2026)\nZielony: Sojusz | Czerwony: Wróg | Pomarańczowy: Napięte relacje", fontsize=14, pad=20)
ax1.axis('off')

# DIAGRAM 2: Korelacja Cen Ropy, Gazu i Kosztów w Polsce (Multiaxis)
ax2 = fig.add_subplot(312)
ax2_detal = ax2.twinx() # Oś dla cen w PLN
ax2_usd = ax2.twinx()   # Oś dla USD/PLN
ax2_usd.spines['right'].set_position(('outward', 60))

# Linie wykresu
p1, = ax2.plot(df['Data'], df['Brent_Oil'], 'r-o', label='Ropa Brent ($)', linewidth=3)
p2, = ax2_detal.plot(df['Data'], df['ON_Polska'], 'g-s', label='Diesel (ON) Polska (zł)', linewidth=2)
p3, = ax2_detal.plot(df['Data'], df['LNG_Stacje'], 'b-^', label='LNG Polska (zł)', linewidth=2, linestyle='--')
p4, = ax2_usd.plot(df['Data'], df['USD_PLN'], color='gold', label='Kurs USD/PLN', linewidth=2, alpha=0.8)

# Adnotacje wydarzeń
for i, txt in enumerate(df['Event']):
    ax2.annotate(txt, (df['Data'][i], df['Brent_Oil'][i]), textcoords="offset points", 
                 xytext=(0,10), ha='center', fontsize=8, fontweight='bold', color='darkred')

ax2.set_ylabel('Cena Ropy ($)', color='r', fontsize=12)
ax2_detal.set_ylabel('Cena na stacjach w PL (zł)', color='darkgreen', fontsize=12)
ax2_usd.set_ylabel('Kurs USD/PLN', color='orange', fontsize=12)
ax2.set_title("WPŁYW WOJNY NA PORTFEL POLAKA (MARZEC 2026)", fontsize=14)
ax2.grid(True, alpha=0.3)
ax2.legend(handles=[p1, p2, p3, p4], loc='upper left')

# DIAGRAM 3: Wykres Wpływów / Finansowania (Kto kogo wspiera)
ax3 = fig.add_subplot(313)
support_data = {
    'Podmiot': ['Hezbollah', 'Izrael', 'Hamas', 'Huti', 'Syria', 'Kurdowie'],
    'Wsparcie od Iranu (%)': [90, 0, 70, 85, 80, 0],
    'Wsparcie od USA (%)': [0, 95, 0, 0, 0, 75]
}
sdf = pd.DataFrame(support_data)
sdf.set_index('Podmiot').plot(kind='bar', stacked=True, color=['limegreen', 'royalblue'], ax=ax3)

ax3.set_title("GŁÓWNE ŹRÓDŁA FINANSOWANIA I UZBROJENIA", fontsize=14)
ax3.set_ylabel("Szacunkowy stopień zależności (%)")
ax3.legend(["Oś Oporu (Iran)", "Zachód (USA)"])
plt.xticks(rotation=0)

plt.tight_layout()
plt.show()


