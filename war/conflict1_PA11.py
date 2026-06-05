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

nodes_info = {
    "USA": {"etnos": "Zachód", "wiara": "Chrześcijanie", "pos": (-1.3, 0.0), "status": "umiarkowany", "lat": 38.0, "lon": -10.0, "f_usa": 100, "f_irn": 0},
    "Izrael": {"etnos": "Żydzi", "wiara": "Judaizm", "pos": (-0.8, 0.6), "status": "umiarkowany", "lat": 31.7, "lon": 35.2, "f_usa": 98, "f_irn": 0},
    "Turcja: Kurdystan": {"etnos": "Kurdowie", "wiara": "Sunnici", "pos": (-0.1, 0.3), "status": "umiarkowany", "lat": 36.2, "lon": 42.0, "f_usa": 75, "f_irn": 0},
    "Palestyna: Hamas": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (0.4, 0.5), "status": "radykalny", "lat": 31.5, "lon": 34.4, "f_usa": 0, "f_irn": 75},
    "Liban: Hezbollah": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.5, 0.1), "status": "radykalny", "lat": 33.8, "lon": 35.5, "f_usa": 0, "f_irn": 95},
    "Syria": {"etnos": "Arabowie", "wiara": "Alawici", "pos": (0.6, -0.3), "status": "radykalny", "lat": 33.5, "lon": 36.3, "f_usa": 0, "f_irn": 85},
    "Jemen: Huti": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.2, -0.8), "status": "radykalny", "lat": 15.3, "lon": 44.2, "f_usa": 0, "f_irn": 90},
    "Iran": {"etnos": "Persowie", "wiara": "Szyici", "pos": (1.1, 0.0), "status": "radykalny", "lat": 35.7, "lon": 51.4, "f_usa": 0, "f_irn": 100},
    "S. Arabia (Sun)": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.8, -0.4), "status": "umiarkowany", "lat": 24.7, "lon": 46.6, "f_usa": 80, "f_irn": 5},
    "Katar (Sun)": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.3, -0.6), "status": "umiarkowany", "lat": 25.3, "lon": 48.0, "f_usa": 60, "f_irn": 10},
    "ZEA (Sun)": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.1, -0.7), "status": "umiarkowany", "lat": 24.4, "lon": 52.0, "f_usa": 75, "f_irn": 0},
    "Irak (Sun)": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (0.2, 0.1), "status": "umiarkowany", "lat": 33.3, "lon": 44.0, "f_usa": 30, "f_irn": 20},
    "Irak (Szy)": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.2, -0.1), "status": "umiarkowany", "lat": 33.3, "lon": 45.0, "f_usa": 30, "f_irn": 60},
    "ZEA (Szy)": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.0, -0.9), "status": "umiarkowany", "lat": 24.4, "lon": 55.0, "f_usa": 0, "f_irn": 10}
}

fig = plt.figure(figsize=(18, 38))

# --- WYKRES 1: GEOPOLITYCZNA MAPA RELACJI ---
ax1 = fig.add_subplot(311)
G = nx.Graph()
pos_net = {k: v['pos'] for k, v in nodes_info.items()}

# 1. Relacje wyznaniowe
for u in nodes_info:
    for v in nodes_info:
        if u < v:
            u_info, v_info = nodes_info[u], nodes_info[v]
            szyici_plus = ["Szyici", "Alawici"]
            if u_info['wiara'] in szyici_plus and v_info['wiara'] in szyici_plus:
                nx.draw_networkx_edges(G, pos_net, edgelist=[(u, v)], edge_color="darkviolet", style='--', width=2.0, alpha=0.6, ax=ax1)
            if u_info['wiara'] == "Sunnici" and v_info['wiara'] == "Sunnici":
                nx.draw_networkx_edges(G, pos_net, edgelist=[(u, v)], edge_color="blue", style='--', width=1.5, alpha=0.5, ax=ax1)
            if u_info['etnos'] == "Arabowie" and v_info['etnos'] == "Arabowie":
                nx.draw_networkx_edges(G, pos_net, edgelist=[(u, v)], edge_color="darkorange", style=':', width=1.0, alpha=0.4, ax=ax1)

# 2. Relacje polityczne (Zaktualizowane nazewnictwo i brak pogrubienia czerwonych)
rel_pol = [
    ("Iran", "Liban: Hezbollah", "green"), ("Iran", "Jemen: Huti", "green"), ("Iran", "Syria", "green"), ("Iran", "Palestyna: Hamas", "green"), 
    ("Iran", "Izrael", "red"), ("Iran", "USA", "red"), ("USA", "Izrael", "green"), ("USA", "Katar (Sun)", "green"), 
    ("S. Arabia (Sun)", "USA", "green"), ("Turcja: Kurdystan", "USA", "green"), ("ZEA (Sun)", "USA", "green"), ("Palestyna: Hamas", "Izrael", "red"),
    ("Liban: Hezbollah", "Izrael", "orange"), # Ostrzał punktowy
    ("S. Arabia (Sun)", "Iran", "orange"),    # Ostrzał punktowy
    ("ZEA (Sun)", "Iran", "orange"),          # Ostrzał punktowy
    ("Katar (Sun)", "Iran", "orange")         # Ostrzał punktowy
]
for u, v, c in rel_pol:
    nx.draw_networkx_edges(G, pos_net, edgelist=[(u, v)], edge_color=c, width=2.0, ax=ax1)

for node, p in pos_net.items():
    color = "saddlebrown" if nodes_info[node]['status'] == "radykalny" else "darkgrey"
    label = f"{node}\n({nodes_info[node]['status']})\n{nodes_info[node]['etnos']}\n{nodes_info[node]['wiara']}"
    ax1.text(p[0], p[1], label, size=8, ha='center', va='center', fontweight='bold', color='white',
             bbox=dict(facecolor=color, edgecolor='black', boxstyle='round,pad=0.5'))

leg_h = [
    mpatches.Patch(color='darkgrey', label='Umiarkowani'),
    mpatches.Patch(color='saddlebrown', label='Radykalni'),
    plt.Line2D([0], [0], color='green', label='Sojusz'),
    plt.Line2D([0], [0], color='red', label='Wrogość (Ostrzał zmasowany)'),
    plt.Line2D([0], [0], color='orange', label='Napięcie (Ostrzał punktowy)'),
    plt.Line2D([0], [0], color='darkviolet', linestyle='--', label='Relacja Szyici/Alawici'),
    plt.Line2D([0], [0], color='blue', linestyle='--', label='Relacja Sunnici'),
    plt.Line2D([0], [0], color='darkorange', linestyle=':', label='Wspólnota Arabska')
]
ax1.legend(handles=leg_h, loc='upper right', fontsize=9)
ax1.set_title("GEOPOLITYCZNA MAPA RELACJI", fontsize=16)
ax1.axis('off')

# --- WYKRES 2: WPŁYW KONFLIKTU NA CENY SUROWCÓW ---
ax2 = fig.add_subplot(312)
ax2_v, ax2_p = ax2.twinx(), ax2.twinx()
ax2_p.spines['right'].set_position(('outward', 60))

p1, = ax2_p.plot(df['Data'], df['ON_PL'], color='saddlebrown', marker='s', label='PLN (zł) Diesel PL', linewidth=2.5)
p2, = ax2.plot(df['Data'], df['Brent_Oil'], color='red', marker='o', label='USD ($) Ropa Brent', linewidth=3)
p3, = ax2_v.plot(df['Data'], df['USD_PLN'], color='gold', linestyle=':', label='USD/PLN Kurs Walut', linewidth=2)
p4, = ax2_p.plot(df['Data'], df['LNG_PL'], color='turquoise', marker='^', label='PLN (zł) LNG PL')
p5, = ax2.plot(df['Data'], df['Gas_World'], color='green', marker='d', label='USD ($) Gaz Świat', linewidth=2)

for i, txt in enumerate(df['Event']):
    ax2.annotate(txt, (df['Data'][i], df['Gas_World'][i]), textcoords="offset points", xytext=(0,15), ha='center', fontsize=8, rotation=25, fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='grey', alpha=0.9))

ax2.set_ylabel("USD ($) Surowce Świat", color='red')
ax2_v.set_ylabel("Kurs Walut (USD/PLN)", color='gold')
ax2_p.set_ylabel("Ceny w Polsce (zł)", color='saddlebrown')
ax2.set_title("WPŁYW KONFLIKTU NA CENY SUROWCÓW", fontsize=16)
ax2.legend(handles=[p1, p2, p3, p4, p5], loc='upper left')
ax2.grid(True, alpha=0.3)

# --- WYKRES 3: POZIOM FINANSOWANIA UZBROJENIA (POSZERZONA OŚ X) ---
ax3 = fig.add_subplot(313)
plot_n = {k: v for k, v in nodes_info.items() if k != "USA"}
lats = [v['lat'] for v in plot_n.values()]
lons = [v['lon'] for v in plot_n.values()]
f_usa = [v['f_usa'] for v in plot_n.values()]
f_irn = [v['f_irn'] for v in plot_n.values()]

sc = ax3.scatter(lons, lats, c=f_irn, cmap='Reds', s=400, edgecolors=plt.cm.Blues(np.array(f_usa)/100), linewidths=6, zorder=3)

# Realne poszerzenie osi X (widok od Atlantyku po Środkową Azję)
ax3.set_xlim(-20, 80) 
ax3.set_ylim(10, 50)

plt.colorbar(plt.cm.ScalarMappable(cmap='Blues'), ax=ax3, location='left', label='Otoczka: Finansowanie USA (%)')
plt.colorbar(plt.cm.ScalarMappable(cmap='Reds'), ax=ax3, location='right', label='Środek: Finansowanie Iran (%)')

for i, name in enumerate(plot_n.keys()):
    ax3.annotate(name, (lons[i], lats[i]), xytext=(12, 12), textcoords='offset points', fontsize=9, fontweight='bold')

ax3.set_title("POZIOM FINANSOWANIA UZBROJENIA", fontsize=16)
ax3.grid(True, alpha=0.2)

plt.tight_layout(pad=6.0)
plt.show()


