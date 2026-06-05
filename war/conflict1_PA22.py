import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.patches as mpatches

# =============================================================================
# DATA CONSTANTS (To be moved to CSV in the next step)
# =============================================================================

# Language and Labels
LOCALE = "PL"
TEXT_RESOURCES = {
    "PL": {
        "title_geopolitics": "GEOPOLITYCZNA MAPA RELACJI",
        "title_market": "WPŁYW KONFLIKTU NA CENY SUROWCÓW",
        "title_funding": "POZIOM FINANSOWANIA UZBROJENIA",
        "label_oil": "Ropa Brent ($)",
        "label_gas": "Gaz Świat ($)",
        "label_usd": "Kurs USD/PLN",
        "label_diesel": "Diesel PL (zł)",
        "label_lng": "LNG PL (zł)",
        "axis_usd": "USD ($) - Ropa i Gaz Świat",
        "axis_fx": "Kurs Waluty USD/PLN",
        "axis_pln": "Cena PLN (zł) - Paliwa PL",
        "legend_mod": "Umiarkowani",
        "legend_rad": "Radykalni",
        "rel_full": "Sojusz pełny (Biznes i Wojsko)",
        "rel_part": "Sojusz częściowy (Wspólny Wróg)",
        "rel_hostile": "Wrogość (Ostrzał Zmasowany)",
        "rel_tension": "Napięcie (Ostrzał Punktowy)",
        "rel_shia": "Korelacja Szyici/Alawici",
        "rel_sunni": "Korelacja Sunnici",
        "fund_usa": "Finansowanie USA (%)",
        "fund_iran": "Finansowanie Iran (%)"
    }
}

# Market Timeseries Data
MARKET_DATA = {
    'dates': ['27.02', '28.02', '02.03', '08.03', '10.03', '11.03', '12.03', '13.03', '14.03'],
    'brent': [70, 72, 77, 126, 83, 91, 96, 104, 110],
    'gas': [2.80, 2.90, 3.10, 5.80, 3.05, 3.25, 3.20, 3.40, 3.65],
    'usd_pln': [4.00, 4.05, 4.15, 4.50, 4.40, 4.38, 4.35, 4.42, 4.45],
    'diesel': [6.70, 6.80, 7.10, 8.50, 8.20, 8.15, 7.95, 8.25, 8.40],
    'lng': [2.85, 2.90, 3.05, 4.20, 3.80, 3.75, 3.60, 3.90, 4.10],
    'events': [
        'Stan gotowości sił USA',
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

# Nodes Definition (Geographical & Political)
NODES_CONFIG = {
    "USA": {"eth": "Zachód", "rel": "Chrześcijanie", "pos": (-1.7, 0.4), "type": "mod", "lat": 38, "lon": -10, "f_usa": 100, "f_irn": 0},
    "Izrael": {"eth": "Żydzi", "rel": "Judaizm", "pos": (-1.1, 0.7), "type": "mod", "lat": 31.7, "lon": 35.2, "f_usa": 98, "f_irn": 0},
    "Egipt": {"eth": "Arabowie", "rel": "Sunnici", "pos": (-1.7, -0.2), "type": "mod", "lat": 30.0, "lon": 31.2, "f_usa": 40, "f_irn": 0},
    "Turcja": {"eth": "Turcy", "rel": "Sunnici", "pos": (-0.6, 0.55), "type": "mod", "lat": 39.9, "lon": 32.8, "f_usa": 30, "f_irn": 0},
    "Turcja: Kurdystan": {"eth": "Kurdowie", "rel": "Sunnici", "pos": (-0.3, 0.55), "type": "mod", "lat": 36.2, "lon": 42.0, "f_usa": 75, "f_irn": 0},
    "Palestyna: Hamas": {"eth": "Arabowie", "rel": "Sunnici", "pos": (0.0, 0.7), "type": "rad", "lat": 31.5, "lon": 34.4, "f_usa": 0, "f_irn": 75},
    "Liban: Hezbollah": {"eth": "Arabowie", "rel": "Szyici", "pos": (0.3, 0.55), "type": "rad", "lat": 33.8, "lon": 35.5, "f_usa": 0, "f_irn": 95},
    "Syria": {"eth": "Arabowie", "rel": "Alawici", "pos": (0.6, 0.4), "type": "rad", "lat": 33.5, "lon": 36.3, "f_usa": 0, "f_irn": 85},
    "Irak: Kurdystan": {"eth": "Kurdowie", "rel": "Sunnici", "pos": (-0.35, 0.1), "type": "mod", "lat": 36.5, "lon": 44.0, "f_usa": 60, "f_irn": 0},
    "Irak": {"eth": "Arabowie", "rel": "Sunnici", "pos": (-0.1, 0.1), "type": "mod", "lat": 33.3, "lon": 44.0, "f_usa": 30, "f_irn": 20},
    "Irak ": {"eth": "Arabowie", "rel": "Szyici", "pos": (0.15, 0.1), "type": "mod", "lat": 33.3, "lon": 45.0, "f_usa": 30, "f_irn": 60},
    "Iran": {"eth": "Persowie", "rel": "Szyici", "pos": (0.9, 0.2), "type": "rad", "lat": 35.7, "lon": 51.4, "f_usa": 0, "f_irn": 100},
    "Jemen: Huti": {"eth": "Arabowie", "rel": "Szyici", "pos": (0.3, -0.6), "type": "rad", "lat": 15.3, "lon": 44.2, "f_usa": 0, "f_irn": 90},
    "S. Arabia": {"eth": "Arabowie", "rel": "Sunnici", "pos": (-1.0, -0.6), "type": "mod", "lat": 24.7, "lon": 46.6, "f_usa": 80, "f_irn": 5},
    "Katar": {"eth": "Arabowie", "rel": "Sunnici", "pos": (-0.5, -0.7), "type": "mod", "lat": 25.3, "lon": 48.0, "f_usa": 90, "f_irn": 10},
    "ZEA": {"eth": "Arabowie", "rel": "Sunnici", "pos": (-0.3, -0.8), "type": "mod", "lat": 24.4, "lon": 52.0, "f_usa": 85, "f_irn": 0},
    "Afganistan": {"eth": "Pasztuni", "rel": "Sunnici", "pos": (1.2, 0.6), "type": "rad", "lat": 33.9, "lon": 67.7, "f_usa": 0, "f_irn": 30},
    "Pakistan": {"eth": "Pendżabczycy", "rel": "Sunnici", "pos": (1.2, -0.1), "type": "mod", "lat": 30.3, "lon": 69.3, "f_usa": 40, "f_irn": 20},
    "Indie": {"eth": "Indusowie", "rel": "Hinduizm", "pos": (1.6, -0.2), "type": "mod", "lat": 20.5, "lon": 78.9, "f_usa": 60, "f_irn": 30},
    "Rosja": {"eth": "Słowianie", "rel": "Prawosławie", "pos": (1.6, 0.6), "type": "mod", "lat": 55, "lon": 37, "f_usa": 0, "f_irn": 80},
    "Chiny": {"eth": "Han", "rel": "Buddyzm/Ateizm", "pos": (1.9, 0.1), "type": "mod", "lat": 35, "lon": 105, "f_usa": 10, "f_irn": 40}
}

# Alliance and Conflict Edge Definitions
EDGES_CONFIG = [
    ("Iran", "Liban: Hezbollah", "green", "-"), ("Iran", "Jemen: Huti", "green", "-"), 
    ("Iran", "Syria", "green", "-"), ("Iran", "Palestyna: Hamas", "green", "-"), 
    ("USA", "Izrael", "green", "-"), ("USA", "Egipt", "green", "-"),
    ("USA", "Katar", "green", "-"), ("USA", "ZEA", "green", "-"), ("S. Arabia", "USA", "green", "-"),
    ("Rosja", "Syria", "green", "-"), ("Rosja", "Iran", "green", "-"), ("Rosja", "Chiny", "green", "-"),
    ("Chiny", "Iran", "green", "-"), ("Chiny", "Syria", "green", "--"), ("Turcja", "USA", "green", "-"),
    ("Izrael", "S. Arabia", "green", "--"), ("Turcja", "Turcja: Kurdystan", "red", "--"),
    ("Iran", "Izrael", "red", "-"), ("Iran", "USA", "red", "-"), ("Liban: Hezbollah", "Izrael", "red", "-"),
    ("Iran", "S. Arabia", "red", "--"), ("Iran", "ZEA", "red", "--"), ("Iran", "Pakistan", "red", "--"),
    ("Indie", "Rosja", "green", "-"), ("Indie", "USA", "green", "--"), ("Indie", "Pakistan", "red", "--"), 
    ("Indie", "Chiny", "red", "--"), ("Afganistan", "Iran", "red", "--"), ("Afganistan", "Pakistan", "red", "--"), 
    ("Afganistan", "Rosja", "green", "--")
]

# Layout Positions (Normalized Coordinates 0-1)
LAYOUT = {
    "fig_size": (24, 52),
    "margin_left": 0.05,
    "graph_pos": [0.05, 0.68, 0.75, 0.30], # Top chart moved max up
    "market_pos": [0.05, 0.38, 0.85, 0.25],
    "funding_pos": [0.05, 0.05, 0.85, 0.25],
    "hspace": 0.6,
    "map_y_lim": (10, 45),
    "map_x_lim": (29, 82),
    "market_x_padding": 0.8
}

# =============================================================================
# DASHBOARD ENGINE (Logical Processing)
# =============================================================================

T = TEXT_RESOURCES[LOCALE]
df = pd.DataFrame(MARKET_DATA)
fig = plt.figure(figsize=LAYOUT["fig_size"])

# --- CHART 1: GEOPOLITICS (TOP) ---
ax1 = fig.add_axes(LAYOUT["graph_pos"])
G = nx.Graph()
pos_net = {k: v['pos'] for k, v in NODES_CONFIG.items()}

# Religious Correlations (Dotted lines)
for u_name, u_cfg in NODES_CONFIG.items():
    for v_name, v_cfg in NODES_CONFIG.items():
        if u_name < v_name:
            if u_cfg['rel'] in ["Szyici", "Alawici"] and v_cfg['rel'] in ["Szyici", "Alawici"]:
                nx.draw_networkx_edges(G, pos_net, edgelist=[(u_name, v_name)], edge_color="darkviolet", style=':', width=1.0, alpha=0.3, ax=ax1)
            if u_cfg['rel'] == "Sunnici" and v_cfg['rel'] == "Sunnici":
                nx.draw_networkx_edges(G, pos_net, edgelist=[(u_name, v_name)], edge_color="blue", style=':', width=1.0, alpha=0.2, ax=ax1)

# Political & Military Edges
for u, v, col, style in EDGES_CONFIG:
    width = 2.5 if style == "-" else 1.5
    nx.draw_networkx_edges(G, pos_net, edgelist=[(u,v)], edge_color=col, style=style, width=width, ax=ax1)

# Draw Node Labels/Boxes
for name, cfg in NODES_CONFIG.items():
    color = "saddlebrown" if cfg['type'] == "rad" else "darkgrey"
    ax1.text(cfg['pos'][0], cfg['pos'][1], f"{name}\n{cfg['eth']}\n{cfg['rel']}", 
             size=8, ha='center', va='center', fontweight='bold', color='white', 
             bbox=dict(facecolor=color, edgecolor='black', boxstyle='round,pad=0.5'))

# Geopolitical Legend
leg_el = [
    mpatches.Patch(color='darkgrey', label=T["legend_mod"]), 
    mpatches.Patch(color='saddlebrown', label=T["legend_rad"]),
    plt.Line2D([0], [0], color='green', lw=2.5, label=T["rel_full"]),
    plt.Line2D([0], [0], color='green', lw=1.5, ls='--', label=T["rel_part"]),
    plt.Line2D([0], [0], color='red', lw=2.5, label=T["rel_hostile"]),
    plt.Line2D([0], [0], color='red', lw=1.5, ls='--', label=T["rel_tension"]),
    plt.Line2D([0], [0], color='darkviolet', ls=':', label=T["rel_shia"]),
    plt.Line2D([0], [0], color='blue', ls=':', label=T["rel_sunni"])
]
ax1.legend(handles=leg_el, loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize=10)
ax1.set_title(T["title_geopolitics"], fontsize=18, pad=30, loc='left')
ax1.axis('off')

# --- CHART 2: MARKET IMPACT (MIDDLE) ---
ax2 = fig.add_axes(LAYOUT["market_pos"])
ax2_fx, ax2_pln = ax2.twinx(), ax2.twinx()
ax2_pln.spines['right'].set_position(('outward', 60))

# Plot Series
p1, = ax2_pln.plot(df['dates'], df['diesel'], 'saddlebrown', marker='s', label=T["label_diesel"])
p2, = ax2.plot(df['dates'], df['brent'], 'red', marker='o', label=T["label_oil"], lw=2)
p3, = ax2_fx.plot(df['dates'], df['usd_pln'], 'gold', ls=':', lw=2, label=T["label_usd"])
p4, = ax2_pln.plot(df['dates'], df['lng'], 'turquoise', marker='^', label=T["label_lng"])
p5, = ax2.plot(df['dates'], df['gas'], 'green', marker='d', label=T["label_gas"])

# Event Annotations
for i, txt in enumerate(df['events']):
    ax2.annotate(txt, (df['dates'][i], df['gas'][i]), textcoords="offset points", xytext=(0,15), 
                 ha='center', fontsize=8, rotation=35, fontweight='bold', 
                 bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='grey', alpha=0.9))

ax2.set_xlim(-LAYOUT["market_x_padding"], len(df['dates']) - (1 - LAYOUT["market_x_padding"]))
ax2.set_ylabel(T["axis_usd"], color='red', fontweight='bold')
ax2_fx.set_ylabel(T["axis_fx"], color='gold', fontweight='bold')
ax2_pln.set_ylabel(T["axis_pln"], color='saddlebrown', fontweight='bold')
ax2.legend(handles=[p1, p2, p3, p4, p5], loc='upper left')
ax2.set_title(T["title_market"], fontsize=18, pad=40, loc='left')
ax2.grid(True, alpha=0.3)

# --- CHART 3: FUNDING MAP (BOTTOM) ---
ax3 = fig.add_axes(LAYOUT["funding_pos"])
ax3.set_xlim(LAYOUT["map_x_lim"])
ax3.set_ylim(LAYOUT["map_y_lim"])

# Filter non-global powers for the map view
plot_nodes = {k: v for k, v in NODES_CONFIG.items() if k not in ["USA", "Rosja", "Chiny"]}
for i, (name, val) in enumerate(plot_nodes.items()):
    ax3.scatter(val['lon'], val['lat'], c=[val['f_irn']], cmap='Reds', vmin=0, vmax=100, 
                s=400, edgecolors=plt.cm.Blues(val['f_usa']/100), linewidths=6, zorder=3)
    ax3.annotate(name, (val['lon'], val['lat']), xytext=(0, 15 if i%2==0 else -25), 
                 textcoords='offset points', ha='center', fontsize=9, fontweight='bold')

# Funding Colorbars
plt.colorbar(plt.cm.ScalarMappable(cmap='Blues'), ax=ax3, location='left', pad=0.03, shrink=0.8).set_label(T["fund_usa"])
plt.colorbar(plt.cm.ScalarMappable(cmap='Reds'), ax=ax3, location='right', pad=0.03, shrink=0.8).set_label(T["fund_iran"])

ax3.set_title(T["title_funding"], fontsize=18, pad=30, loc='left')
ax3.grid(True, alpha=0.2)

plt.show()


