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

# Podmioty - Przebudowany układ współrzędnych (pos)
nodes_info = {
    "USA": {"etnos": "Zachód", "wiara": "Chrześcijanie", "pos": (-1.5, 0.4), "status": "umiarkowany", "lat": 38, "lon": -10, "f_usa": 100, "f_irn": 0},
    "Izrael": {"etnos": "Żydzi", "wiara": "Judaizm", "pos": (-0.9, 0.7), "status": "umiarkowany", "lat": 31.7, "lon": 35.2, "f_usa": 98, "f_irn": 0},
    "Egipt": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.9, -0.2), "status": "umiarkowany", "lat": 30.0, "lon": 31.2, "f_usa": 40, "f_irn": 0},
    "Turcja: Turcy": {"etnos": "Turcy", "wiara": "Sunnici", "pos": (-0.4, 0.4), "status": "umiarkowany", "lat": 39.9, "lon": 32.8, "f_usa": 30, "f_irn": 0},
    "Turcja: Kurdystan": {"etnos": "Kurdowie", "wiara": "Sunnici", "pos": (-0.1, 0.4), "status": "umiarkowany", "lat": 36.2, "lon": 42.0, "f_usa": 75, "f_irn": 0},
    
    # Blok Iraku (na poziomie 0.1)
    "Irak: Kurdystan": {"etnos": "Kurdowie", "wiara": "Sunnici", "pos": (-0.1, 0.1), "status": "umiarkowany", "lat": 36.5, "lon": 44.0, "f_usa": 60, "f_irn": 0},
    "Irak": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (0.2, 0.1), "status": "umiarkowany", "lat": 33.3, "lon": 44.0, "f_usa": 30, "f_irn": 20},
    "Irak ": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.5, 0.1), "status": "umiarkowany", "lat": 33.3, "lon": 45.0, "f_usa": 30, "f_irn": 60},
    
    "Palestyna: Hamas": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (0.4, 0.5), "status": "radykalny", "lat": 31.5, "lon": 34.4, "f_usa": 0, "f_irn": 75},
    "Liban: Hezbollah": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.5, 0.4), "status": "radykalny", "lat": 33.8, "lon": 35.5, "f_usa": 0, "f_irn": 95},
    "Syria": {"etnos": "Arabowie", "wiara": "Alawici", "pos": (0.8, 0.4), "status": "radykalny", "lat": 33.5, "lon": 36.3, "f_usa": 0, "f_irn": 85},
    "Jemen: Huti": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.5, -0.6), "status": "radykalny", "lat": 15.3, "lon": 44.2, "f_usa": 0, "f_irn": 90},
    
    "Iran": {"etnos": "Persowie", "wiara": "Szyici", "pos": (1.1, 0.2), "status": "radykalny", "lat": 35.7, "lon": 51.4, "f_usa": 0, "f_irn": 100},
    "S. Arabia": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.8, -0.6), "status": "umiarkowany", "lat": 24.7, "lon": 46.6, "f_usa": 80, "f_irn": 5},
    "Katar": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.3, -0.7), "status": "umiarkowany", "lat": 25.3, "lon": 48.0, "f_usa": 60, "f_irn": 10},
    "ZEA": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.1, -0.8), "status": "umiarkowany", "lat": 24.4, "lon": 52.0, "f_usa": 75, "f_irn": 0},
    
    # Mocarstwa po prawej
    "Rosja": {"etnos": "Słowianie", "wiara": "Prawosławie", "pos": (1.6, 0.5), "status": "umiarkowany", "lat": 55, "lon": 37, "f_usa": 0, "f_irn": 50},
    "Chiny": {"etnos": "Han", "wiara": "Buddyzm/Ateizm", "pos": (1.6, -0.4), "status": "umiarkowany", "lat": 35, "lon": 105, "f_usa": 10, "f_irn": 40}
}

fig = plt.figure(figsize=(24, 46))

# --- WYKRES 1: GEOPOLITYCZNA MAPA RELACJI ---
ax1 = fig.add_subplot(311)
G = nx.Graph()
pos_net = {k: v['pos'] for k, v in nodes_info.items()}

# Kropkowane linie religijne
for u in nodes_info:
    for v in nodes_info:
        if u < v:
            u_i, v_i = nodes_info[u], nodes_info[v]
            if u_i['wiara'] in ["Szyici", "Alawici"] and v_i['wiara'] in ["Szyici", "Alawici"]:
                nx.draw_networkx_edges(G, pos_net, edgelist=[(u,v)], edge_color="darkviolet", style=':', width=1.0, alpha=0.4, ax=ax1)
            if u_i['wiara'] == "Sunnici" and v_i['wiara'] == "Sunnici":
                nx.draw_networkx_edges(G, pos_net, edgelist=[(u,v)], edge_color="blue", style=':', width=1.0, alpha=0.3, ax=ax1)

# Relacje polityczne
rel_pol = [
    ("Iran", "Liban: Hezbollah", "green"), ("Iran", "Jemen: Huti", "green"), ("Iran", "Syria", "green"), ("Iran", "Palestyna: Hamas", "green"), 
    ("Iran", "Izrael", "red"), ("Iran", "USA", "red"), ("USA", "Izrael", "green"), ("USA", "Egipt", "green"), ("Rosja", "Syria", "green"), 
    ("S. Arabia", "USA", "green"), ("Turcja: Turcy", "USA", "green"), ("Chiny", "Iran", "green"),
    ("Liban: Hezbollah", "Izrael", "red"), ("S. Arabia", "Iran", "red"), ("ZEA", "Iran", "red"), ("Katar", "Iran", "red"),
    ("Irak: Kurdystan", "USA", "green")
]
for u, v, c in rel_pol:
    # Ostrzał zmasowany (Iran-IZR, Iran-USA, Hamas-IZR) = linia ciągła czerwona, reszta przerywana
    is_zmasowany = (u,v) in [("Iran", "Izrael"), ("Iran", "USA"), ("Palestyna: Hamas", "Izrael"), ("Liban: Hezbollah", "Izrael")]
    line_style = '-' if c == "green" or is_zmasowany else '--'
    nx.draw_networkx_edges(G, pos_net, edgelist=[(u,v)], edge_color=c, style=line_style, width=2.2, ax=ax1)

for node, p in pos_net.items():
    color = "saddlebrown" if nodes_info[node]['status'] == "radykalny" else "darkgrey"
    ax1.text(p[0], p[1], f"{node}\n{nodes_info[node]['etnos']}\n{nodes_info[node]['wiara']}", size=8, ha='center', va='center', fontweight='bold', color='white', bbox=dict(facecolor=color, edgecolor='black', boxstyle='round,pad=0.5'))

leg1 = [
    mpatches.Patch(color='darkgrey', label='Umiarkowani'), mpatches.Patch(color='saddlebrown', label='Radykalni'),
    plt.Line2D([0], [0], color='green', label='Sojusz'),
    plt.Line2D([0], [0], color='red', label='Wrogość (Ostrzał zmasowany)'),
    plt.Line2D([0], [0], color='red', linestyle='--', label='Napięcie (Ostrzał punktowy)'),
    plt.Line2D([0], [0], color='darkviolet', linestyle=':', label='Korelacja Szyici/Alawici'),
    plt.Line2D([0], [0], color='blue', linestyle=':', label='Korelacja Sunnici')
]
ax1.legend(handles=leg1, loc='upper right', fontsize=10)
ax1.set_title("GEOPOLITYCZNA MAPA RELACJI", fontsize=18)
ax1.axis('off')

# --- WYKRES 2: WPŁYW KONFLIKTU NA CENY SUROWCÓW (Zgodnie z ustaleniami) ---
ax2 = fig.add_subplot(312)
ax2_v, ax2_p = ax2.twinx(), ax2.twinx()
ax2_p.spines['right'].set_position(('outward', 60))
p1, = ax2_p.plot(df['Data'], df['ON_PL'], 'saddlebrown', marker='s', label='Diesel PL (zł)')
p2, = ax2.plot(df['Data'], df['Brent_Oil'], 'red', marker='o', label='Ropa Brent ($)', linewidth=2)
p3, = ax2_v.plot(df['Data'], df['USD_PLN'], 'gold', linestyle=':', label='USD/PLN Kurs Walut')
p4, = ax2_p.plot(df['Data'], df['LNG_PL'], 'turquoise', marker='^', label='LNG PL (zł)')
p5, = ax2.plot(df['Data'], df['Gas_World'], 'green', marker='d', label='Gaz Świat ($)')
for i, txt in enumerate(df['Event']):
    ax2.annotate(txt, (df['Data'][i], df['Gas_World'][i]), textcoords="offset points", xytext=(0,15), ha='center', fontsize=8, rotation=25, fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='grey', alpha=0.9))
ax2.legend(handles=[p1, p2, p3, p4, p5], loc='upper left')
ax2.set_title("WPŁYW KONFLIKTU NA CENY SUROWCÓW", fontsize=18)
ax2.grid(True, alpha=0.3)

# --- WYKRES 3: POZIOM FINANSOWANIA UZBROJENIA (Ekstremalnie poszerzony) ---
ax3 = fig.add_subplot(313)
ax3.set_xlim(29, 53) 
ax3.set_ylim(13, 43)
ax3.set_box_aspect(0.2) # Jeszcze szerszy prostokąt

plot_n = {k: v for k, v in nodes_info.items() if k not in ["USA", "Rosja", "Chiny"]}
for i, (name, val) in enumerate(plot_n.items()):
    ax3.scatter(val['lon'], val['lat'], c=[val['f_irn']], cmap='Reds', vmin=0, vmax=100, s=400, edgecolors=plt.cm.Blues(val['f_usa']/100), linewidths=6, zorder=3)
    ax3.annotate(name, (val['lon'], val['lat']), xytext=(0, 15 if i%2==0 else -20), textcoords='offset points', ha='center', fontsize=9, fontweight='bold')

plt.colorbar(plt.cm.ScalarMappable(cmap='Blues'), ax=ax3, location='left', pad=0.05).set_label('Otoczka: Finansowanie USA (%)')
plt.colorbar(plt.cm.ScalarMappable(cmap='Reds'), ax=ax3, location='right', pad=0.05).set_label('Środek: Finansowanie Iran (%)')
ax3.set_title("POZIOM FINANSOWANIA UZBROJENIA", fontsize=18)
ax3.grid(True, alpha=0.2)

plt.tight_layout()
plt.show()


