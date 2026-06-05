import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np

# --- 1. DANE WEJŚCIOWE (KROK 1 - AKTUALIZACJA) ---

# Kalendarium i Rynki
data = {
    'Data': ['28.02', '02.03', '08.03', '10.03', '11.03', '12.03', '13.03', '14.03'],
    'Brent_Oil': [72, 77, 126, 83, 91, 96, 104, 110],
    'Gas_World': [2.90, 3.10, 5.80, 3.05, 3.25, 3.20, 3.40, 3.65],
    'USD_PLN': [4.05, 4.15, 4.50, 4.40, 4.38, 4.35, 4.42, 4.45],
    'ON_PL': [6.80, 7.10, 8.50, 8.20, 8.15, 7.95, 8.25, 8.40],
    'LNG_PL': [2.90, 3.05, 4.20, 3.80, 3.75, 3.60, 3.90, 4.10],
    'Event': [
        'Początek nalotów USA i Izraela na Iran',
        'Atak odwetowy Iranu na ZEA, Kuwejt i Katar',
        'Całkowita blokada Cieśniny Ormuz przez Pasdaranów',
        'Zgoda USA na import ropy z Rosji przez Indie',
        'Zmasowany atak dronów na infrastrukturę Dubaju',
        'Uwolnienie rezerw strategicznych przez IEA',
        'Ciężki ostrzał rakietowy centrum Doszy',
        'Ewakuacja cywilów z dzielnicy Musheireb'
    ]
}
df = pd.DataFrame(data)

# Podmioty (Nody) z pozycjonowaniem Zachód-Wschód
# Pozycje X: ujemne = Zachód, dodatnie = Wschód
nodes_info = {
    "USA": {"etnos": "Zachód", "wiara": "Chrześcijanie", "pos": (-1.0, 0.0), "status": "umiarkowany", "lat": 38.9, "lon": -77.0},
    "Izrael": {"etnos": "Żydzi", "wiara": "Judaizm", "pos": (-0.6, -0.1), "status": "umiarkowany", "lat": 31.7, "lon": 35.2},
    "Kurdowie": {"etnos": "Kurdowie", "wiara": "Sunnici", "pos": (-0.4, 0.6), "status": "umiarkowany", "lat": 36.2, "lon": 44.0},
    "S. Arabia": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.2, -0.4), "status": "umiarkowany", "lat": 24.7, "lon": 46.6},
    "Katar": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (0.0, -0.6), "status": "umiarkowany", "lat": 25.3, "lon": 51.5},
    "Syria": {"etnos": "Arabowie", "wiara": "Alawici", "pos": (0.4, 0.5), "status": "radykalny", "lat": 33.5, "lon": 36.3},
    "Hezbollah": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.5, 0.2), "status": "radykalny", "lat": 33.8, "lon": 35.5},
    "Hamas": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (0.6, -0.3), "status": "radykalny", "lat": 31.5, "lon": 34.4},
    "Huti": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.7, -0.7), "status": "radykalny", "lat": 15.3, "lon": 44.2},
    "Iran": {"etnos": "Persowie", "wiara": "Szyici", "pos": (1.0, 0.0), "status": "radykalny", "lat": 35.7, "lon": 51.4}
}

# --- 2. GENEROWANIE GRAFIK ---

fig = plt.figure(figsize=(18, 32))

# WYKRES 1: Mapa Relacji (USA na lewo, Iran na prawo)
ax1 = fig.add_subplot(311)
G = nx.Graph()
for node in nodes_info: G.add_node(node)

rel_pol = [
    ("Iran", "Hezbollah", "green"), ("Iran", "Huti", "green"), ("Iran", "Syria", "green"),
    ("Iran", "Hamas", "green"), ("Iran", "Izrael", "red"), ("Iran", "USA", "red"),
    ("USA", "Izrael", "green"), ("USA", "Katar", "green"), ("S. Arabia", "USA", "green"),
    ("Kurdowie", "USA", "green"), ("Hamas", "Izrael", "red"), ("Hezbollah", "Izrael", "red"),
    ("Iran", "Katar", "red"), ("S. Arabia", "Iran", "orange")
]

pos_net = {k: v['pos'] for k, v in nodes_info.items()}

# Rysowanie linii wyznaniowych (przerywane)
for u in nodes_info:
    for v in nodes_info:
        if u < v:
            if nodes_info[u]['wiara'] == nodes_info[v]['wiara']:
                c = "purple" if nodes_info[u]['wiara'] == "Szyici" else "blue"
                if nodes_info[u]['wiara'] in ["Judaizm", "Chrześcijanie"]: c = "turquoise"
                nx.draw_networkx_edges(G, pos_net, edgelist=[(u, v)], edge_color=c, style='--', alpha=0.15, ax=ax1)

# Rysowanie linii politycznych
for u, v, c in rel_pol:
    nx.draw_networkx_edges(G, pos_net, edgelist=[(u, v)], edge_color=c, width=2.5, ax=ax1)

# Rysowanie nodów (prostokąty)
for node, p in pos_net.items():
    info = nodes_info[node]
    color = "saddlebrown" if info['status'] == "radykalny" else "darkgrey"
    label = f"{node}\n({info['status']})\n{info['etnos']}\n{info['wiara']}"
    ax1.text(p[0], p[1], label, size=8, ha='center', va='center', fontweight='bold', color='white',
             bbox=dict(facecolor=color, edgecolor='black', boxstyle='round,pad=0.5'))

ax1.set_title("WYKRES 1: GEOPOLITYCZNY UKŁAD SIŁ (ZACHÓD VS WSCHÓD)", fontsize=16, pad=20)
ax1.set_xlim(-1.3, 1.3)
ax1.axis('off')

# WYKRES 2: Rynek, Waluty i Detal
ax2 = fig.add_subplot(312)
ax2_val = ax2.twinx() 
ax2_detal = ax2.twinx()
ax2_detal.spines['right'].set_position(('outward', 60))

p1, = ax2.plot(df['Data'], df['Brent_Oil'], 'r-o', label='Ropa Brent ($)', linewidth=3)
p2, = ax2.plot(df['Data'], df['Gas_World'], color='teal', marker='d', label='Gaz Świat ($)')
p3, = ax2_val.plot(df['Data'], df['USD_PLN'], color='gold', label='USD/PLN', linewidth=2, linestyle=':')
p4, = ax2_detal.plot(df['Data'], df['ON_PL'], 'g-s', label='Diesel PL (zł)')
p5, = ax2_detal.plot(df['Data'], df['LNG_PL'], 'b--^', label='LNG PL (zł)')

for i, txt in enumerate(df['Event']):
    ax2.annotate(txt, (df['Data'][i], df['Brent_Oil'][i]), textcoords="offset points", 
                 xytext=(0,15), ha='center', fontsize=7, rotation=35, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.2))

ax2.set_ylabel("Ceny Surowców ($)", color='r', fontsize=12)
ax2_val.set_ylabel("Kurs USD/PLN", color='orange', fontsize=12)
ax2_detal.set_ylabel("Cena w Polsce (zł)", color='g', fontsize=12)
ax2.set_title("WYKRES 2: WPŁYW WOJNY NA CENY I WALUTY", fontsize=16)
ax2.grid(True, alpha=0.2)
ax2.legend(handles=[p1, p2, p3, p4, p5], loc='upper left')

# WYKRES 3: Realna Mapa Geopolityczna (Współrzędne)
ax3 = fig.add_subplot(313)
lats = [v['lat'] for v in nodes_info.values()]
lons = [v['lon'] for v in nodes_info.values()]
names = list(nodes_info.keys())
colors = ["saddlebrown" if v['status'] == "radykalny" else "darkgrey" for v in nodes_info.values()]

ax3.scatter(lons, lats, c=colors, s=300, edgecolors='black', zorder=3)

for i, name in enumerate(names):
    ax3.annotate(name, (lons[i], lats[i]), xytext=(5, 5), textcoords='offset points', fontsize=9, fontweight='bold')

# Dodanie prostego tła geograficznego (Siatka)
ax3.set_xlabel("Długość geograficzna (Longitude)")
ax3.set_ylabel("Szerokość geograficzna (Latitude)")
ax3.set_title("WYKRES 3: GEOGRAFICZNE ROZMIESZCZENIE PODMIOTÓW KONFLIKTU", fontsize=16)
ax3.grid(True, linestyle='--', alpha=0.5)
ax3.set_facecolor('#f0f8ff') # Kolor wody

plt.tight_layout(pad=6.0)
plt.show()


