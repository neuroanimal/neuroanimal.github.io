import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np

# --- DANE DO DIAGRAMÓW ---

# 1. Dane do mapy relacji (Oś Oporu i Rywale)
nodes = {
    "Iran": {"color": "limegreen", "group": "Persowie / Szyici"},
    "Hezbollah": {"color": "forestgreen", "group": "Arabowie / Szyici"},
    "Huti": {"color": "darkgreen", "group": "Arabowie / Szyici"},
    "Syria (Asad)": {"color": "greenyellow", "group": "Arabowie / Alawici"},
    "Hamas": {"color": "olive", "group": "Arabowie / Sunnici"},
    "Izrael": {"color": "blue", "group": "Żydzi"},
    "USA": {"color": "navy", "group": "Zachód"},
    "Arabia Saudyjska": {"color": "sandybrown", "group": "Arabowie / Sunnici"},
    "Katar": {"color": "orange", "group": "Arabowie / Sunnici"},
    "Kurdowie": {"color": "yellow", "group": "Kurdowie / Sunnici"}
}

edges = [
    ("Iran", "Hezbollah", "Sojusz"), ("Iran", "Huti", "Sojusz"), ("Iran", "Syria (Asad)", "Sojusz"),
    ("Iran", "Hamas", "Wsparcie"), ("Hezbollah", "Izrael", "Wojna"), ("Hamas", "Izrael", "Wojna"),
    ("Iran", "Izrael", "Wojna"), ("Iran", "USA", "Konflikt"), ("USA", "Izrael", "Sojusz"),
    ("USA", "Katar", "Baza Al Udeid"), ("Iran", "Katar", "Atak (III 2026)"),
    ("Arabia Saudyjska", "Iran", "Rywalizacja"), ("USA", "Kurdowie", "Wsparcie")
]

# 2. Dane do wykresu korelacji cen (Kalendarium)
dates = ['28.02', '02.03', '08.03', '10.03', '11.03', '12.03', '13.03', '14.03']
oil_prices = [72, 77, 126, 83, 91, 96, 104, 110]
gas_prices = [2.9, 3.0, 5.8, 3.0, 3.2, 3.2, 3.1, 3.5]
events = ["Start nalotów", "Atak na ZEA/Katar", "Blokada Ormuz", "Ropa z Rosji", "Drony na Dubaj", "Rezerwy IEA", "Ostrzał Doszy", "Ewakuacja Doszy"]

# --- GENEROWANIE WYKRESÓW ---

fig = plt.figure(figsize=(16, 18))

# DIAGRAM 1: Mapa Relacji (Sieć)
ax1 = fig.add_subplot(311)
G = nx.Graph()
for node, attr in nodes.items():
    G.add_node(node, color=attr["color"])
G.add_edges_from([(e[0], e[1]) for e in edges])

pos = nx.spring_layout(G, seed=42)
node_colors = [nodes[n]["color"] for n in G.nodes()]
nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=3000, font_size=10, font_weight="bold", ax=ax1)
ax1.set_title("Mapa Relacji i Podziałów (Etniczność/Religia)", fontsize=15)

# DIAGRAM 2: Korelacja Cen i Wydarzeń (Wykres dwuosiowy)
ax2 = fig.add_subplot(312)
ax2_gas = ax2.twinx()

lns1 = ax2.plot(dates, oil_prices, 'r-o', label='Ropa Brent ($)', linewidth=3)
lns2 = ax2_gas.plot(dates, gas_prices, 'b-s', label='Gaz ($)', linewidth=2)

for i, txt in enumerate(events):
    ax2.annotate(txt, (dates[i], oil_prices[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, fontweight='bold')

ax2.set_xlabel('Data (Marzec 2026)')
ax2.set_ylabel('Cena Ropy ($)', color='r')
ax2_gas.set_ylabel('Cena Gazu ($)', color='b')
ax2.grid(True, linestyle='--')
ax2.set_title("Wpływ Ataków na Rynki Energii", fontsize=15)

# DIAGRAM 3: Wyznania i Grupy (Wykres słupkowy orientacyjny)
ax3 = fig.add_subplot(313)
groups = [attr["group"] for attr in nodes.values()]
unique_groups, counts = np.unique(groups, return_counts=True)
ax3.barh(unique_groups, counts, color='skyblue')
ax3.set_title("Struktura Wyznaniowo-Etniczna podmiotów w konflikcie", fontsize=15)
ax3.set_xlabel("Liczba kluczowych graczy w danej grupie")

plt.tight_layout()
plt.show()


