import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.patches as mpatches

# --- 1. PEŁNE DANE WEJŚCIOWE ---
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

# Przywrócenie pełnych informacji o podmiotach
nodes_info = {
    "USA": {"etnos": "Zachód", "wiara": "Chrześcijanie", "pos": (-1.0, 0.0), "status": "umiarkowany", "lat": 38.0, "lon": 15.0, "f_usa": 100, "f_irn": 0},
    "Izrael": {"etnos": "Żydzi", "wiara": "Judaizm", "pos": (-0.6, 0.6), "status": "umiarkowany", "lat": 31.7, "lon": 35.2, "f_usa": 98, "f_irn": 0},
    "S. Arabia": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.6, -0.4), "status": "umiarkowany", "lat": 24.7, "lon": 46.6, "f_usa": 80, "f_irn": 5},
    "Kurdowie": {"etnos": "Kurdowie", "wiara": "Sunnici", "pos": (-0.1, 0.3), "status": "umiarkowany", "lat": 36.2, "lon": 44.0, "f_usa": 75, "f_irn": 0},
    "Katar": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (-0.1, -0.5), "status": "umiarkowany", "lat": 25.3, "lon": 51.5, "f_usa": 50, "f_irn": 25},
    "ZEA": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (0.3, -0.6), "status": "umiarkowany", "lat": 24.4, "lon": 54.3, "f_usa": 75, "f_irn": 0},
    "Syria": {"etnos": "Arabowie", "wiara": "Alawici", "pos": (0.4, 0.5), "status": "radykalny", "lat": 33.5, "lon": 36.3, "f_usa": 0, "f_irn": 85},
    "Hezbollah": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.5, 0.1), "status": "radykalny", "lat": 33.8, "lon": 35.5, "f_usa": 0, "f_irn": 95},
    "Hamas": {"etnos": "Arabowie", "wiara": "Sunnici", "pos": (0.6, -0.3), "status": "radykalny", "lat": 31.5, "lon": 34.4, "f_usa": 0, "f_irn": 70},
    "Huti": {"etnos": "Arabowie", "wiara": "Szyici", "pos": (0.6, -0.7), "status": "radykalny", "lat": 15.3, "lon": 44.2, "f_usa": 0, "f_irn": 90},
    "Iran": {"etnos": "Persowie", "wiara": "Szyici", "pos": (1.0, 0.0), "status": "radykalny", "lat": 35.7, "lon": 51.4, "f_usa": 0, "f_irn": 100}
}

fig = plt.figure(figsize=(18, 36))

# --- WYKRES 1: MAPA RELACJI ---
ax1 = fig.add_subplot(311)
G = nx.Graph()
pos_net = {k: v['pos'] for k, v in nodes_info.items()}

# Relacje polityczne
rel_pol = [("Iran", "Hezbollah", "green"), ("Iran", "Huti", "green"), ("Iran", "Syria", "green"), ("Iran", "Hamas", "green"), 
           ("Iran", "Izrael", "red"), ("Iran", "USA", "red"), ("USA", "Izrael", "green"), ("USA", "Katar", "green"), 
           ("S. Arabia", "USA", "green"), ("Kurdowie", "USA", "green"), ("ZEA", "USA", "green"), ("Hamas", "Izrael", "red")]

# Linie Wiary (Intensywny Fiolet dla Szyitów)
for u in nodes_info:
    for v in nodes_info:
        if u < v:
            if nodes_info[u]['wiara'] == "Szyici" and nodes_info[v]['wiara'] == "Szyici":
                nx.draw_networkx_edges(G, pos_net, edgelist=[(u,v)], edge_color="darkviolet", style='--', width=3, alpha=0.7, ax=ax1)
            if nodes_info[u]['etnos'] == "Arabowie" and nodes_info[v]['etnos'] == "Arabowie":
                nx.draw_networkx_edges(G, pos_net, edgelist=[(u,v)], edge_color="darkorange", style=':', width=3, alpha=0.6, ax=ax1)

for u, v, c in rel_pol:
    nx.draw_networkx_edges(G, pos_net, edgelist=[(u,v)], edge_color=c, width=2.5, ax=ax1)

for node, p in pos_net.items():
    info = nodes_info[node]
    color = "saddlebrown" if info['status'] == "radykalny" else "darkgrey"
    label = f"{node}\n({info['status']})\n{info['etnos']}\n{info['wiara']}"
    ax1.text(p[0], p[1], label, size=8, ha='center', va='center', fontweight='bold', color='white',
             bbox=dict(facecolor=color, edgecolor='black', boxstyle='round,pad=0.6'))
ax1.set_title("WYKRES 1: GEOPOLITYCZNA MAPA RELACJI, WYZNAŃ I ETNOSÓW", fontsize=16)
ax1.axis('off')

# --- WYKRES 2: RYNKI ---
ax2 = fig.add_subplot(312)
ax2_v, ax2_p = ax2.twinx(), ax2.twinx()
ax2_p.spines['right'].set_position(('outward', 60))

p1, = ax2_p.plot(df['Data'], df['ON_PL'], color='saddlebrown', marker='s', label='PLN (zł) Diesel PL', linewidth=2.5)
p2, = ax2.plot(df['Data'], df['Brent_Oil'], color='red', marker='o', label='USD ($) Ropa Brent', linewidth=3)
p3, = ax2_v.plot(df['Data'], df['USD_PLN'], color='gold', linestyle=':', label='USD/PLN Kurs waluty', linewidth=2)
p4, = ax2_p.plot(df['Data'], df['LNG_PL'], color='turquoise', marker='^', label='PLN (zł) LNG PL')
p5, = ax2.plot(df['Data'], df['Gas_World'], color='green', marker='d', label='USD ($) Gaz Świat', linewidth=2)

for i, txt in enumerate(df['Event']):
    ax2.annotate(txt, (df['Data'][i], df['Gas_World'][i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, rotation=35, fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.3))

ax2.set_title("WYKRES 2: WPŁYW KONFLIKTU NA CENY ENERGII I WALUTY", fontsize=16)
ax2.legend(handles=[p1, p2, p3, p4, p5], loc='upper left')
ax2.grid(True, alpha=0.3)

# --- WYKRES 3: MAPA FINANSOWANIA (ZARYS KRAJÓW I NASYCENIE) ---
ax3 = fig.add_subplot(313)
plot_n = {k: v for k, v in nodes_info.items() if k != "USA"}
lats = [v['lat'] for v in plot_n.values()]
lons = [v['lon'] for v in plot_n.values()]
f_usa = [v['f_usa'] for v in plot_n.values()]
f_irn = [v['f_irn'] for v in plot_n.values()]

# Wykorzystujemy dwa mapowania kolorów na jednym punkcie
# USA = Kolor wnętrza, Iran = Kolor obramowania
sc = ax3.scatter(lons, lats, c=f_usa, cmap='Blues', s=600, edgecolors=plt.cm.Reds(np.array(f_irn)/100), linewidths=5, zorder=3)

# Dodanie Legend Nasycenia
cbar_usa = plt.colorbar(plt.cm.ScalarMappable(cmap='Blues'), ax=ax3, location='left', pad=0.1)
cbar_usa.set_label('Finansowanie przez USA (%)', fontsize=10)
cbar_irn = plt.colorbar(plt.cm.ScalarMappable(cmap='Reds'), ax=ax3, location='right', pad=0.1)
cbar_irn.set_label('Finansowanie przez IRAN (%)', fontsize=10)

for i, name in enumerate(plot_n.keys()):
    ax3.annotate(name, (lons[i], lats[i]), xytext=(10, 10), textcoords='offset points', fontsize=10, fontweight='bold')

# Zarysy "geograficzne" (uproszczone siatką)
ax3.axhspan(12, 42, color='lightblue', alpha=0.1, zorder=1) # Symulacja morza/regionu
ax3.set_title("WYKRES 3: MAPA FINANSOWANIA I UZBROJENIA (NASYCENIE DWUKANAŁOWE)", fontsize=16)
ax3.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout(pad=6.0)
plt.show()


