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

# Przywrócony i zaktualizowany układ podmiotów
nodes_info = {
    "USA": {"etnos": "Zachód", "wiara": "Chrześcijanie", "pos": (-1.5, 0.4), "status": "umiarkowany", "lat": 38, "lon": -10, "f_usa": 100, "f_irn": 0},
    "Izrael": {"etnos": "Żydzi", "wiara": "Judaizm", "pos": (-0.9, 0.7), "status": "umiarkowany", "lat": 31.7, "lon": 35.2, "f_usa": 98, "f_irn": 0},
    "Egipt": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.9, -0.2), "status": "umiarkowany", "lat": 30.0, "lon": 31.2, "f_usa": 40, "f_irn": 0},
    "Turcja: Turcy": {"etnos": "Turcy", "wiara": "Sunnici", "pos": (-0.4, 0.4), "status": "umiarkowany", "lat": 39.9, "lon": 32.8, "f_usa": 30, "f_irn": 0},
    "Turcja: Kurdystan": {"etnos": "Kurdowie", "wiara": "Sunnici", "pos": (-0.1, 0.4), "status": "umiarkowany", "lat": 36.2, "lon": 42.0, "f_usa": 75, "f_irn": 0},
    
    # Blok Iraku i Syrii
    "Irak: Kurdystan": {"etnos": "Kurdowie", "wiara": "Sunnici", "pos": (-0.1, 0.1), "status": "umiarkowany", "lat": 36.5, "lon": 44.0, "f_usa": 60, "f_irn": 0},
    "Irak": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (0.2, 0.1), "status": "umiarkowany", "lat": 33.3, "lon": 44.0, "f_usa": 30, "f_irn": 20},
    "Irak ": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.5, 0.1), "status": "umiarkowany", "lat": 33.3, "lon": 45.0, "f_usa": 30, "f_irn": 60},
    
    "Palestyna: Hamas": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (0.2, 0.7), "status": "radykalny", "lat": 31.5, "lon": 34.4, "f_usa": 0, "f_irn": 75},
    "Liban: Hezbollah": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.5, 0.7), "status": "radykalny", "lat": 33.8, "lon": 35.5, "f_usa": 0, "f_irn": 95},
    "Syria": {"etnos": "Arabowie", "wiara": "Alawici", "pos": (0.8, 0.7), "status": "radykalny", "lat": 33.5, "lon": 36.3, "f_usa": 0, "f_irn": 85},
    "Jemen: Huti": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.5, -0.6), "status": "radykalny", "lat": 15.3, "lon": 44.2, "f_usa": 0, "f_irn": 90},
    
    "Iran": {"etnos": "Persowie", "wiara": "Szyici", "pos": (1.1, 0.2), "status": "radykalny", "lat": 35.7, "lon": 51.4, "f_usa": 0, "f_irn": 100},
    "S. Arabia": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.8, -0.6), "status": "umiarkowany", "lat": 24.7, "lon": 46.6, "f_usa": 80, "f_irn": 5},
    "Katar": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.3, -0.7), "status": "umiarkowany", "lat": 25.3, "lon": 48.0, "f_usa": 90, "f_irn": 10},
    "ZEA": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.1, -0.8), "status": "umiarkowany", "lat": 24.4, "lon": 52.0, "f_usa": 85, "f_irn": 0},
    
    "Rosja": {"etnos": "Słowianie", "wiara": "Prawosławie", "pos": (1.6, 0.5), "status": "umiarkowany", "lat": 55, "lon": 37, "f_usa": 0, "f_irn": 80},
    "Chiny": {"etnos": "Han", "wiara": "Buddyzm/Ateizm", "pos": (1.6, -0.4), "status": "umiarkowany", "lat": 35, "lon": 105, "f_usa": 10, "f_irn": 40}
}

fig = plt.figure(figsize=(24, 46))

# --- WYKRES 1: GEOPOLITYCZNA MAPA RELACJI ---
ax1 = fig.add_subplot(311)
G = nx.Graph()
pos_net = {k: v['pos'] for k, v in nodes_info.items()}

# 1. Linie wyznaniowe (subtelne)
for u in nodes_info:
    for v in nodes_info:
        if u < v:
            u_i, v_i = nodes_info[u], nodes_info[v]
            if u_i['wiara'] in ["Szyici", "Alawici"] and v_i['wiara'] in ["Szyici", "Alawici"]:
                nx.draw_networkx_edges(G, pos_net, edgelist=[(u,v)], edge_color="darkviolet", style=':', width=1.0, alpha=0.3, ax=ax1)
            if u_i['wiara'] == "Sunnici" and v_i['wiara'] == "Sunnici":
                nx.draw_networkx_edges(G, pos_net, edgelist=[(u,v)], edge_color="blue", style=':', width=1.0, alpha=0.2, ax=ax1)

# 2. Relacje polityczne (Przywrócone i uzupełnione)
rel_pol = [
    # Sojusze Pełne (Ciągłe Zielone)
    ("Iran", "Liban: Hezbollah", "green", "-"), ("Iran", "Jemen: Huti", "green", "-"), ("Iran", "Syria", "green", "-"), 
    ("Iran", "Palestyna: Hamas", "green", "-"), ("USA", "Izrael", "green", "-"), ("USA", "Egipt", "green", "-"),
    ("USA", "Katar", "green", "-"), ("USA", "ZEA", "green", "-"), ("S. Arabia", "USA", "green", "-"),
    ("Rosja", "Syria", "green", "-"), ("Rosja", "Iran", "green", "-"), ("Rosja", "Chiny", "green", "-"),
    ("Turcja: Turcy", "USA", "green", "-"), ("Irak: Kurdystan", "USA", "green", "-"),
    # Sojusze Częściowe (Przerywane Zielone)
    ("Izrael", "S. Arabia", "green", "--"), ("Izrael", "ZEA", "green", "--"),
    # Wrogość (Czerwone)
    ("Iran", "Izrael", "red", "-"), ("Iran", "USA", "red", "-"), ("Liban: Hezbollah", "Izrael", "red", "-"),
    ("S. Arabia", "Iran", "red", "--"), ("ZEA", "Iran", "red", "--"), ("Katar", "Iran", "red", "--")
]

for u, v, c, s in rel_pol:
    nx.draw_networkx_edges(G, pos_net, edgelist=[(u,v)], edge_color=c, style=s, width=2.5 if c=="red" else 2.0, ax=ax1)

for node, p in pos_net.items():
    color = "saddlebrown" if nodes_info[node]['status'] == "radykalny" else "darkgrey"
    ax1.text(p[0], p[1], f"{node}\n{nodes_info[node]['etnos']}\n{nodes_info[node]['wiara']}", size=8, ha='center', va='center', fontweight='bold', color='white', bbox=dict(facecolor=color, edgecolor='black', boxstyle='round,pad=0.5'))

leg1 = [
    plt.Line2D([0], [0], color='green', lw=2, label='Sojusz Pełny'),
    plt.Line2D([0], [0], color='green', lw=2, ls='--', label='Sojusz Częściowy (Wspólny Wróg)'),
    plt.Line2D([0], [0], color='red', lw=2.5, label='Wrogość / Ostrzał'),
    mpatches.Patch(color='darkgrey', label='Umiarkowani'),
    mpatches.Patch(color='saddlebrown', label='Radykalni')
]
ax1.legend(handles=leg1, loc='upper right', fontsize=10)
ax1.set_title("GEOPOLITYCZNA MAPA RELACJI", fontsize=18)
ax1.axis('off')

# --- WYKRES 2: WPŁYW KONFLIKTU NA CENY SUROWCÓW (Bez zmian) ---
ax2 = fig.add_subplot(312)
ax2_v, ax2_p = ax2.twinx(), ax2.twinx()
ax2_p.spines['right'].set_position(('outward', 60))
p1, = ax2_p.plot(df['Data'], df['ON_PL'], 'saddlebrown', marker='s', label='Diesel PL (zł)')
p2, = ax2.plot(df['Data'], df['Brent_Oil'], 'red', marker='o', label='Ropa Brent ($)')
p3, = ax2_v.plot(df['Data'], df['USD_PLN'], 'gold', lw=2, ls=':', label='USD/PLN')
p4, = ax2_p.plot(df['Data'], df['LNG_PL'], 'turquoise', marker='^', label='LNG PL (zł)')
p5, = ax2.plot(df['Data'], df['Gas_World'], 'green', marker='d', label='Gaz Świat ($)')
for i, txt in enumerate(df['Event']):
    ax2.annotate(txt, (df['Data'][i], df['Gas_World'][i]), textcoords="offset points", xytext=(0,15), ha='center', fontsize=8, rotation=25, fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='grey', alpha=0.9))
ax2.set_ylabel("USD ($)", color='red')
ax2_v.set_ylabel("USD/PLN", color='gold')
ax2_p.set_ylabel("PLN (zł)", color='saddlebrown')
ax2.legend(handles=[p1, p2, p3, p4, p5], loc='upper left')
ax2.set_title("WPŁYW KONFLIKTU NA CENY SUROWCÓW", fontsize=18)
ax2.grid(True, alpha=0.3)

# --- WYKRES 3: POZIOM FINANSOWANIA UZBROJENIA (Poprawione proporcje) ---
ax3 = fig.add_subplot(313)
ax3.set_xlim(29, 53)
ax3.set_ylim(13, 43)

# Kluczowa zmiana: box_aspect dopasowany do Wykresu 2, aby prostokąty były spójne
ax3.set_box_aspect(0.4) 

plot_nodes = {k: v for k, v in nodes_info.items() if k not in ["USA", "Rosja", "Chiny"]}
for i, (name, val) in enumerate(plot_nodes.items()):
    ax3.scatter(val['lon'], val['lat'], c=[val['f_irn']], cmap='Reds', vmin=0, vmax=100, s=400, edgecolors=plt.cm.Blues(val['f_usa']/100), linewidths=6, zorder=3)
    ax3.annotate(name, (val['lon'], val['lat']), xytext=(0, 15 if i%2==0 else -25), textcoords='offset points', ha='center', fontsize=9, fontweight='bold')

# Węższe legendy, by nie "ściskały" wykresu
cb1 = plt.colorbar(plt.cm.ScalarMappable(cmap='Blues'), ax=ax3, location='left', pad=0.08, shrink=0.8)
cb1.set_label('Finansowanie USA (%)')
cb2 = plt.colorbar(plt.cm.ScalarMappable(cmap='Reds'), ax=ax3, location='right', pad=0.08, shrink=0.8)
cb2.set_label('Finansowanie Iran (%)')

ax3.set_title("POZIOM FINANSOWANIA UZBROJENIA", fontsize=18)
ax3.grid(True, alpha=0.2)

plt.tight_layout(pad=4.0)
plt.show()


