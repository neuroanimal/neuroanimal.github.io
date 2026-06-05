import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np

# --- 1. ROZBUDOWANE DANE (MARZEC 2026) ---

# Kalendarium z pełnymi nazwami i cenami
data = {
    'Data': ['28.02', '02.03', '08.03', '10.03', '11.03', '12.03', '13.03', '14.03'],
    'Brent_Oil': [72, 77, 126, 83, 91, 96, 104, 110],
    'Gas_USD': [2.90, 3.10, 5.80, 3.05, 3.25, 3.20, 3.40, 3.65], # Cena gazu w USD (Henry Hub/TTF)
    'USD_PLN': [4.05, 4.15, 4.50, 4.40, 4.38, 4.35, 4.42, 4.45],
    'ON_Polska': [6.80, 7.10, 8.50, 8.20, 8.15, 7.95, 8.25, 8.40],
    'LNG_Stacje': [2.90, 3.05, 4.20, 3.80, 3.75, 3.60, 3.90, 4.10],
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

# Dane do mapy relacji (Nody)
# Postawa: 'radykalny' -> brązowy, 'umiarkowany' -> szary
nodes_info = {
    "Iran": {"etnos": "Persowie", "wiara": "Szyici", "postawa": "radykalny"},
    "Hezbollah": {"etnos": "Arabowie", "wiara": "Szyici", "postawa": "radykalny"},
    "Hamas": {"etnos": "Arabowie", "wiara": "Sunnici", "postawa": "radykalny"},
    "Izrael": {"etnos": "Żydzi", "wiara": "Judaizm", "postawa": "umiarkowany"},
    "USA": {"etnos": "Zachód", "wiara": "Chrześcijanie", "postawa": "umiarkowany"},
    "Katar": {"etnos": "Arabowie", "wiara": "Sunnici", "postawa": "umiarkowany"},
    "S. Arabia": {"etnos": "Arabowie", "wiara": "Sunnici", "postawa": "umiarkowany"},
    "Kurdowie": {"etnos": "Kurdowie", "wiara": "Sunnici", "postawa": "umiarkowany"},
    "Huti": {"etnos": "Arabowie", "wiara": "Szyici", "postawa": "radykalny"},
    "Syria": {"etnos": "Arabowie", "wiara": "Alawici", "postawa": "radykalny"}
}

# --- 2. GENEROWANIE WIZUALIZACJI ---
# Zwiększona wysokość (figsize), by zmieścić trzeci wykres
fig = plt.figure(figsize=(18, 28)) 

# DIAGRAM 1: Mapa Relacji z liniami wyznaniowymi
ax1 = fig.add_subplot(311)
G = nx.Graph()
for node in nodes_info: G.add_node(node)

# Relacje polityczne (stałe linie)
rel_pol = [
    ("Iran", "Hezbollah", "green"), ("Iran", "Huti", "green"), ("Iran", "Syria", "green"),
    ("Iran", "Hamas", "green"), ("Iran", "Izrael", "red"), ("Iran", "USA", "red"),
    ("USA", "Izrael", "green"), ("USA", "Katar", "green"), ("Iran", "Katar", "red"),
    ("S. Arabia", "Iran", "yellow"), ("S. Arabia", "USA", "green"), ("Kurdowie", "USA", "green"),
    ("Kurdowie", "Iran", "red"), ("Hamas", "Izrael", "red"), ("Hezbollah", "Izrael", "red"),
    ("S. Arabia", "Katar", "yellow") # Dodane połączenie
]

pos = nx.spring_layout(G, k=1.5, seed=42)

# Rysowanie linii wyznaniowych (przerywane)
for u in nodes_info:
    for v in nodes_info:
        if u < v:
            w1, w2 = nodes_info[u]['wiara'], nodes_info[v]['wiara']
            if w1 == w2:
                color = ""
                if w1 == "Szyici": color = "purple"
                elif w1 == "Sunnici": color = "blue"
                elif w1 in ["Chrześcijanie", "Judaizm", "Żydzi"]: color = "turquoise"
                
                if color:
                    nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=color, 
                                           style='--', width=1.5, alpha=0.4, ax=ax1)

# Rysowanie linii politycznych
for u, v, c in rel_pol:
    nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=c, width=3, ax=ax1)

# Rysowanie nodów (prostokąty)
for node, (x, y) in pos.items():
    info = nodes_info[node]
    node_color = "saddlebrown" if info['postawa'] == "radykalny" else "darkgrey"
    label = f"{node}\n({info['postawa']})\n---\n{info['etnos']}\n{info['wiara']}"
    ax1.text(x, y, label, size=9, ha='center', va='center', fontweight='bold', color='white',
             bbox=dict(facecolor=node_color, edgecolor='black', boxstyle='round,pad=0.8'))

ax1.set_title("KOMPLEKSOWA MAPA RELACJI I WYZNAŃ (MARZEC 2026)\nLinie ciągłe: Polityka | Przerywane: Wspólnota wiary", fontsize=15, pad=30)
ax1.axis('off')

# DIAGRAM 2: Ropa, Gaz USD i wpływ na polskie stacje
ax2 = fig.add_subplot(312)
ax2_detal = ax2.twinx() 
ax2_gas_usd = ax2.twinx()
ax2_gas_usd.spines['right'].set_position(('outward', 80))

p1, = ax2.plot(df['Data'], df['Brent_Oil'], 'r-o', label='Ropa Brent ($)', linewidth=4)
p2, = ax2_gas_usd.plot(df['Data'], df['Gas_USD'], color='teal', marker='d', label='Gaz Świat ($)', linewidth=2)
p3, = ax2_detal.plot(df['Data'], df['ON_Polska'], 'g-s', label='Diesel ON Polska (zł)', linewidth=2)
p4, = ax2_detal.plot(df['Data'], df['LNG_Stacje'], 'b-^', label='LNG Polska (zł)', linewidth=2, linestyle='--')

# Pełne nazwy wydarzeń na wykresie
for i, txt in enumerate(df['Event']):
    ax2.annotate(txt, (df['Data'][i], df['Brent_Oil'][i]), textcoords="offset points", 
                 xytext=(5,15), ha='left', rotation=45, fontsize=8, fontweight='bold', 
                 bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3))

ax2.set_ylabel('Cena Ropy ($)', color='r', fontsize=12)
ax2_detal.set_ylabel('Cena w Polsce (zł)', color='darkgreen', fontsize=12)
ax2_gas_usd.set_ylabel('Gaz Świat (USD)', color='teal', fontsize=12)
ax2.set_title("KORELACJA RYNKÓW ENERGII I POLSKIEGO DETALU", fontsize=15)
ax2.grid(True, alpha=0.2)
ax2.legend(handles=[p1, p2, p3, p4], loc='upper left')

# DIAGRAM 3: Finansowanie (Pojawi się dzięki większemu figsize)
ax3 = fig.add_subplot(313)
support_data = {
    'Podmiot': ['Hezbollah', 'Izrael', 'Hamas', 'Huti', 'Syria', 'Kurdowie'],
    'Wsparcie od Iranu (%)': [95, 0, 75, 90, 85, 0],
    'Wsparcie od USA (%)': [0, 98, 0, 0, 0, 80]
}
sdf = pd.DataFrame(support_data).set_index('Podmiot')
sdf.plot(kind='bar', stacked=True, color=['#A52A2A', '#4682B4'], ax=ax3)

ax3.set_title("ZALEŻNOŚĆ OD MOCARSTW (FINANSE I BROŃ)", fontsize=15)
ax3.set_ylabel("Stopień finansowania (%)")
plt.xticks(rotation=0)

plt.tight_layout(pad=5.0)
# plt.savefig("wojna_iran_2026_analiza.png") # Opcjonalnie zapis do pliku
plt.show()


