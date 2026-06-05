import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.patches as mpatches

# --- 1. DANE WEJŚCIOWE ---
data = {
    'Data': ['28.02', '02.03', '08.03', '10.03', '11.03', '12.03', '13.03', '14.03'],
    'Brent_Oil': [72, 77, 126, 83, 91, 96, 104, 110],
    'Gas_World': [2.90, 3.10, 5.80, 3.05, 3.25, 3.20, 3.40, 3.65],
    'USD_PLN': [4.05, 4.15, 4.50, 4.40, 4.38, 4.35, 4.42, 4.45],
    'ON_PL': [6.80, 7.10, 8.50, 8.20, 8.15, 7.95, 8.25, 8.40],
    'LNG_PL': [2.90, 3.05, 4.20, 3.80, 3.75, 3.60, 3.90, 4.10],
    'Event': ['Naloty USA/IZR', 'Odwet Iranu', 'Blokada Ormuz', 'Import RU/IN', 'Drony Dubaj', 'Rezerwy IEA', 'Atak Dosza', 'Ewakuacja']
}
df = pd.DataFrame(data)

nodes_info = {
    "USA": {"etnos": "Zachód", "wiara": "Chrześcijanie", "pos": (-1.5, 0.7), "status": "umiarkowany", "lat": 38, "lon": -10, "f_usa": 100, "f_irn": 0},
    "Izrael": {"etnos": "Żydzi", "wiara": "Judaizm", "pos": (-0.9, 0.7), "status": "umiarkowany", "lat": 31.7, "lon": 35.2, "f_usa": 98, "f_irn": 0},
    "Egipt": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-1.5, -0.2), "status": "umiarkowany", "lat": 30.0, "lon": 31.2, "f_usa": 40, "f_irn": 0},
    
    # Rząd GÓRNY (Palestyna, Liban, Syria)
    "Palestyna: Hamas": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (0.2, 0.7), "status": "radykalny", "lat": 31.5, "lon": 34.4, "f_usa": 0, "f_irn": 75},
    "Liban: Hezbollah": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.5, 0.7), "status": "radykalny", "lat": 33.8, "lon": 35.5, "f_usa": 0, "f_irn": 95},
    "Syria": {"etnos": "Arabowie", "wiara": "Alawici", "pos": (0.8, 0.7), "status": "radykalny", "lat": 33.5, "lon": 36.3, "f_usa": 0, "f_irn": 85},
    
    # Rząd ŚRODKOWY (Turcja, Iraki)
    "Turcja: Turcy": {"etnos": "Turcy", "wiara": "Sunnici", "pos": (-0.4, 0.4), "status": "umiarkowany", "lat": 39.9, "lon": 32.8, "f_usa": 30, "f_irn": 0},
    "Turcja: Kurdystan": {"etnos": "Kurdowie", "wiara": "Sunnici", "pos": (-0.1, 0.4), "status": "umiarkowany", "lat": 36.2, "lon": 42.0, "f_usa": 75, "f_irn": 0},
    "Irak: Kurdystan": {"etnos": "Kurdowie", "wiara": "Sunnici", "pos": (-0.1, 0.1), "status": "umiarkowany", "lat": 36.5, "lon": 44.0, "f_usa": 60, "f_irn": 0},
    "Irak": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (0.2, 0.1), "status": "umiarkowany", "lat": 33.3, "lon": 44.0, "f_usa": 30, "f_irn": 20},
    "Irak ": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.5, 0.1), "status": "umiarkowany", "lat": 33.3, "lon": 45.0, "f_usa": 30, "f_irn": 60},

    "Iran": {"etnos": "Persowie", "wiara": "Szyici", "pos": (1.1, 0.4), "status": "radykalny", "lat": 35.7, "lon": 51.4, "f_usa": 0, "f_irn": 100},
    "Jemen: Huti": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.5, -0.6), "status": "radykalny", "lat": 15.3, "lon": 44.2, "f_usa": 0, "f_irn": 90},
    
    # Kraje Zatoki
    "S. Arabia": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.8, -0.6), "status": "umiarkowany", "lat": 24.7, "lon": 46.6, "f_usa": 80, "f_irn": 5},
    "Katar": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.3, -0.7), "status": "umiarkowany", "lat": 25.3, "lon": 48.0, "f_usa": 90, "f_irn": 10},
    "ZEA": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.1, -0.8), "status": "umiarkowany", "lat": 24.4, "lon": 52.0, "f_usa": 85, "f_irn": 0},
    
    # Mocarstwa
    "Rosja": {"etnos": "Słowianie", "wiara": "Prawosławie", "pos": (1.6, 0.1), "status": "umiarkowany", "lat": 55, "lon": 37, "f_usa": 0, "f_irn": 80},
    "Chiny": {"etnos": "Han", "wiara": "Buddyzm/Ateizm", "pos": (1.6, -0.4), "status": "umiarkowany", "lat": 35, "lon": 105, "f_usa": 10, "f_irn": 40}
}

fig = plt.figure(figsize=(24, 46))

# --- WYKRES 1: RELACJE ---
ax1 = fig.add_subplot(311)
G = nx.Graph()
pos_net = {k: v['pos'] for k, v in nodes_info.items()}

# Relacje polityczne (Zróżnicowanie grubości)
rel_pol = [
    ("Iran", "Liban: Hezbollah", "green", 3), ("Iran", "Jemen: Huti", "green", 3), 
    ("Iran", "Syria", "green", 3), ("Iran", "Palestyna: Hamas", "green", 3),
    ("Rosja", "Syria", "green", 3), ("Rosja", "Iran", "green", 3), ("Rosja", "Chiny", "green", 3),
    ("USA", "Izrael", "green", 3), ("USA", "Egipt", "green", 3), ("USA", "Katar", "green", 3), 
    ("USA", "ZEA", "green", 3), ("S. Arabia", "USA", "green", 3),
    ("Izrael", "S. Arabia", "green", 1.5), # Wspólny wróg
    ("Iran", "Izrael", "red", 2.5), ("Iran", "USA", "red", 2.5), ("Liban: Hezbollah", "Izrael", "red", 2.5)
]

for u, v, c, w in rel_pol:
    line = '-' if c == "green" and w == 3 else '--'
    nx.draw_networkx_edges(G, pos_net, edgelist=[(u,v)], edge_color=c, style=line, width=w, ax=ax1)

for node, p in pos_net.items():
    color = "saddlebrown" if nodes_info[node]['status'] == "radykalny" else "darkgrey"
    ax1.text(p[0], p[1], f"{node}\n{nodes_info[node]['etnos']}\n{nodes_info[node]['wiara']}", size=8, ha='center', va='center', fontweight='bold', color='white', bbox=dict(facecolor=color, edgecolor='black', boxstyle='round,pad=0.5'))

leg1 = [
    plt.Line2D([0], [0], color='green', lw=3, label='Sojusz Pełny (Ekon. i Wojsk.)'),
    plt.Line2D([0], [0], color='green', lw=1.5, ls='--', label='Sojusz Częściowy (Wspólny Wróg)'),
    plt.Line2D([0], [0], color='red', lw=2.5, label='Wrogość / Ostrzał')
]
ax1.legend(handles=leg1, loc='upper right')
ax1.set_title("GEOPOLITYCZNA MAPA RELACJI (WERSJA ZWERYFIKOWANA)", fontsize=18)
ax1.axis('off')

# --- WYKRES 2: CENY (Z przywróconymi etykietami osi) ---
ax2 = fig.add_subplot(312)
ax2_v, ax2_p = ax2.twinx(), ax2.twinx()
ax2_p.spines['right'].set_position(('outward', 60))

p1, = ax2_p.plot(df['Data'], df['ON_PL'], 'saddlebrown', marker='s', label='Diesel PL (zł)')
p2, = ax2.plot(df['Data'], df['Brent_Oil'], 'red', marker='o', label='Ropa Brent ($)')
p3, = ax2_v.plot(df['Data'], df['USD_PLN'], 'gold', lw=2, ls=':', label='USD/PLN')
p4, = ax2_p.plot(df['Data'], df['LNG_PL'], 'turquoise', marker='^', label='LNG PL (zł)')
p5, = ax2.plot(df['Data'], df['Gas_World'], 'green', marker='d', label='Gaz Świat ($)')

ax2.set_ylabel("Cena USD ($)", color='red', fontweight='bold')
ax2_v.set_ylabel("Kurs USD/PLN", color='gold', fontweight='bold')
ax2_p.set_ylabel("Cena PLN (zł)", color='saddlebrown', fontweight='bold')
ax2.legend(handles=[p1, p2, p3, p4, p5], loc='upper left')
ax2.set_title("WPŁYW KONFLIKTU NA CENY SUROWCÓW", fontsize=18)

# --- WYKRES 3: FINANSOWANIE (Szeroki z wąskimi legendami) ---
ax3 = fig.add_subplot(313)
ax3.set_xlim(29, 53)
ax3.set_ylim(13, 43)
ax3.set_box_aspect(0.15) # Jeszcze szerszy!

plot_nodes = {k: v for k, v in nodes_info.items() if k not in ["USA", "Rosja", "Chiny"]}
for name, val in plot_nodes.items():
    ax3.scatter(val['lon'], val['lat'], c=[val['f_irn']], cmap='Reds', vmin=0, vmax=100, s=400, edgecolors=plt.cm.Blues(val['f_usa']/100), linewidths=6)
    ax3.annotate(name, (val['lon'], val['lat']), xytext=(0, 10), textcoords='offset points', ha='center', fontsize=9, fontweight='bold')

# Węższe legendy (shrink)
plt.colorbar(plt.cm.ScalarMappable(cmap='Blues'), ax=ax3, location='left', shrink=0.6, pad=0.02).set_label('USA %')
plt.colorbar(plt.cm.ScalarMappable(cmap='Reds'), ax=ax3, location='right', shrink=0.6, pad=0.02).set_label('Iran %')

ax3.set_title("POZIOM FINANSOWANIA UZBROJENIA", fontsize=18)
plt.tight_layout()
plt.show()


