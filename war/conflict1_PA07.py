import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np

# --- 1. DANE WEJŚCIOWE ---

data = {
    'Data': ['28.02', '02.03', '08.03', '10.03', '11.03', '12.03', '13.03', '14.03'],
    'Brent_Oil': [72, 77, 126, 83, 91, 96, 104, 110],
    'Gas_World': [2.90, 3.10, 5.80, 3.05, 3.25, 3.20, 3.40, 3.65],
    'USD_PLN': [4.05, 4.15, 4.50, 4.40, 4.38, 4.35, 4.42, 4.45],
    'ON_PL': [6.80, 7.10, 8.50, 8.20, 8.15, 7.95, 8.25, 8.40],
    'LNG_PL': [2.90, 3.05, 4.20, 3.80, 3.75, 3.60, 3.90, 4.10],
    'Event': ['Atak USA/IZR', 'Odwet Iranu', 'Blokada Ormuz', 'Import RU/IN', 'Drony Dubaj', 'Rezerwy IEA', 'Atak Dosza', 'Ewakuacja']
}
df = pd.DataFrame(data)

# Podmioty - Nowa Architektura Położeń
nodes_info = {
    "USA": {"etnos": "Zachód", "wiara": "Chrześcijanie", "pos": (-1.0, 0.0), "status": "umiarkowany", "lat": 38, "lon": 10, "f_usa": 100, "f_irn": 0},
    "Izrael": {"etnos": "Żydzi", "wiara": "Judaizm", "pos": (-0.6, 0.6), "status": "umiarkowany", "lat": 31.7, "lon": 35.2, "f_usa": 95, "f_irn": 0},
    "S. Arabia": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.6, -0.4), "status": "umiarkowany", "lat": 24.7, "lon": 46.6, "f_usa": 80, "f_irn": 5},
    "Kurdowie": {"etnos": "Kurdowie", "wiara": "Sunnici", "pos": (-0.1, 0.3), "status": "umiarkowany", "lat": 36.2, "lon": 44.0, "f_usa": 75, "f_irn": 0},
    "Katar": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.1, -0.5), "status": "umiarkowany", "lat": 25.3, "lon": 51.5, "f_usa": 60, "f_irn": 20},
    "ZEA": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (0.2, -0.6), "status": "umiarkowany", "lat": 24.4, "lon": 54.3, "f_usa": 70, "f_irn": 0},
    "Syria": {"etnos": "Arabowie", "wiara": "Alawici", "pos": (0.4, 0.5), "status": "radykalny", "lat": 33.5, "lon": 36.3, "f_usa": 0, "f_irn": 85},
    "Hezbollah": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.5, 0.1), "status": "radykalny", "lat": 33.8, "lon": 35.5, "f_usa": 0, "f_irn": 95},
    "Hamas": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (0.6, -0.3), "status": "radykalny", "lat": 31.5, "lon": 34.4, "f_usa": 0, "f_irn": 70},
    "Huti": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.5, -0.7), "status": "radykalny", "lat": 15.3, "lon": 44.2, "f_usa": 0, "f_irn": 90},
    "Iran": {"etnos": "Persowie", "wiara": "Szyici", "pos": (1.0, 0.0), "status": "radykalny", "lat": 35.7, "lon": 51.4, "f_usa": 0, "f_irn": 100}
}

# --- 2. GENEROWANIE ---

fig = plt.figure(figsize=(16, 32))

# WYKRES 1: RELACJE
ax1 = fig.add_subplot(311)
G = nx.Graph()
for node in nodes_info: G.add_node(node)
pos_net = {k: v['pos'] for k, v in nodes_info.items()}

# Relacje polityczne
rel_pol = [("Iran", "Hezbollah", "green"), ("Iran", "Huti", "green"), ("Iran", "Syria", "green"), ("Iran", "Hamas", "green"), 
           ("Iran", "Izrael", "red"), ("Iran", "USA", "red"), ("USA", "Izrael", "green"), ("USA", "Katar", "green"), 
           ("S. Arabia", "USA", "green"), ("Kurdowie", "USA", "green"), ("ZEA", "USA", "green"), ("Hamas", "Izrael", "red")]

# Linie Wiary i Etnosu (intensywne kolory)
for u in nodes_info:
    for v in nodes_info:
        if u < v:
            # Szyici - Intensywny Fiolet
            if nodes_info[u]['wiara'] == "Szyici" and nodes_info[v]['wiara'] == "Szyici":
                nx.draw_networkx_edges(G, pos_net, edgelist=[(u, v)], edge_color="darkviolet", style='--', width=2, alpha=0.6, ax=ax1)
            # Arabowie - Mocny Pomarańcz
            if nodes_info[u]['etnos'] == "Arabowie" and nodes_info[v]['etnos'] == "Arabowie":
                nx.draw_networkx_edges(G, pos_net, edgelist=[(u, v)], edge_color="darkorange", style=':', width=2, alpha=0.5, ax=ax1)

for u, v, c in rel_pol:
    nx.draw_networkx_edges(G, pos_net, edgelist=[(u, v)], edge_color=c, width=2.5, ax=ax1)

for node, p in pos_net.items():
    color = "saddlebrown" if nodes_info[node]['status'] == "radykalny" else "darkgrey"
    ax1.text(p[0], p[1], f"{node}\n({nodes_info[node]['status']})", size=8, ha='center', va='center', fontweight='bold', color='white',
             bbox=dict(facecolor=color, edgecolor='black', boxstyle='round,pad=0.5'))
ax1.set_title("WYKRES 1: MAPA RELACJI (POPRAWIONY UKŁAD GEOPOLITYCZNY)", fontsize=15)
ax1.axis('off')

# WYKRES 2: RYNEK
ax2 = fig.add_subplot(312)
ax2_v, ax2_p = ax2.twinx(), ax2.twinx()
ax2_p.spines['right'].set_position(('outward', 60))
p1, = ax2_p.plot(df['Data'], df['ON_PL'], color='saddlebrown', marker='s', label='PLN (zł) Diesel PL')
p2, = ax2.plot(df['Data'], df['Brent_Oil'], color='red', marker='o', label='USD ($) Ropa Brent', linewidth=3)
p3, = ax2_v.plot(df['Data'], df['USD_PLN'], color='gold', linestyle=':', label='USD/PLN Kurs waluty', linewidth=2)
p4, = ax2_p.plot(df['Data'], df['LNG_PL'], color='turquoise', marker='^', label='PLN (zł) LNG PL')
p5, = ax2.plot(df['Data'], df['Gas_World'], color='green', marker='d', label='USD ($) Gaz Świat')

for i, txt in enumerate(df['Event']):
    ax2.annotate(txt, (df['Data'][i], df['Gas_World'][i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=7, rotation=45)
ax2.legend(handles=[p1, p2, p3, p4, p5], loc='upper left')
ax2.set_title("WYKRES 2: WPŁYW KONFLIKTU NA CENY ENERGII", fontsize=15)

# WYKRES 3: FINANSOWANIE (DWIE INTENSYWNOŚCI)
ax3 = fig.add_subplot(313)
plot_n = {k: v for k, v in nodes_info.items() if k != "USA"}
x = np.arange(len(plot_n))
width = 0.35

ax3.bar(x - width/2, [v['f_usa'] for v in plot_n.values()], width, label='Finansowanie USA (%)', color='royalblue', alpha=0.8)
ax3.bar(x + width/2, [v['f_irn'] for v in plot_n.values()], width, label='Finansowanie Iran (%)', color='crimson', alpha=0.8)

ax3.set_xticks(x)
ax3.set_xticklabels(plot_n.keys(), rotation=45)
ax3.set_ylabel("Procent wsparcia (%)")
ax3.set_title("WYKRES 3: POZIOM FINANSOWANIA I UZBROJENIA (USA vs IRAN)", fontsize=15)
ax3.legend()
ax3.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout(pad=5.0)
plt.show()


