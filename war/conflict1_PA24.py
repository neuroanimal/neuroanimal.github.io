import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.patches as mpatches
import os

# =============================================================================
# STEP 1: GENERATE CSV FILES (One-time setup or data update)
# =============================================================================

# 1.1 Market Data
market_df = pd.DataFrame({
    'dates': ['27.02', '28.02', '02.03', '08.03', '10.03', '11.03', '12.03', '13.03', '14.03'],
    'brent': [70, 72, 77, 126, 83, 91, 96, 104, 110],
    'gas': [2.80, 2.90, 3.10, 5.80, 3.05, 3.25, 3.20, 3.40, 3.65],
    'usd_pln': [4.00, 4.05, 4.15, 4.50, 4.40, 4.38, 4.35, 4.42, 4.45],
    'diesel': [6.70, 6.80, 7.10, 8.50, 8.20, 8.15, 7.95, 8.25, 8.40],
    'lng': [2.85, 2.90, 3.05, 4.20, 3.80, 3.75, 3.60, 3.90, 4.10],
    'events': [
        'Stan gotowości sił USA', 'Początek nalotów USA i Izraela na Iran',
        'Atak odwetowy Iranu na ZEA, Kuwejt i Katar', 'Całkowita blokada Cieśniny Ormuz przez Pasdaranów',
        'Zgoda USA na import ropy z Rosji przez Indie', 'Zmasowany atak dronów na infrastrukturę Dubaju',
        'Uwolnienie rezerw strategicznych przez IEA', 'Ciężki ostrzał rakietowy centrum Doszy',
        'Ewakuacja cywilów z dzielnicy Musheireb'
    ]
})
market_df.to_csv('market_data.csv', index=False)

# 1.2 Nodes Config (Coordinates and attributes)
nodes_df = pd.DataFrame([
    {"id": "USA", "eth": "Zachód", "rel": "Chrześcijanie", "pos_x": -1.7, "pos_y": 0.4, "type": "mod", "lat": 38, "lon": -10, "f_usa": 100, "f_irn": 0},
    {"id": "Izrael", "eth": "Żydzi", "rel": "Judaizm", "pos_x": -1.1, "pos_y": 0.7, "type": "mod", "lat": 31.7, "lon": 35.2, "f_usa": 98, "f_irn": 0},
    {"id": "Egipt", "eth": "Arabowie", "rel": "Sunnici", "pos_x": -1.7, "pos_y": -0.2, "type": "mod", "lat": 30.0, "lon": 31.2, "f_usa": 40, "f_irn": 0},
    {"id": "Turcja", "eth": "Turcy", "rel": "Sunnici", "pos_x": -0.6, "pos_y": 0.55, "type": "mod", "lat": 39.9, "lon": 32.8, "f_usa": 30, "f_irn": 0},
    {"id": "Turcja: Kurdystan", "eth": "Kurdowie", "rel": "Sunnici", "pos_x": -0.3, "pos_y": 0.55, "type": "mod", "lat": 36.2, "lon": 42.0, "f_usa": 75, "f_irn": 0},
    {"id": "Palestyna: Hamas", "eth": "Arabowie", "rel": "Sunnici", "pos_x": 0.0, "pos_y": 0.7, "type": "rad", "lat": 31.5, "lon": 34.4, "f_usa": 0, "f_irn": 75},
    {"id": "Liban: Hezbollah", "eth": "Arabowie", "rel": "Szyici", "pos_x": 0.3, "pos_y": 0.55, "type": "rad", "lat": 33.8, "lon": 35.5, "f_usa": 0, "f_irn": 95},
    {"id": "Syria", "eth": "Arabowie", "rel": "Alawici", "pos_x": 0.6, "pos_y": 0.4, "type": "rad", "lat": 33.5, "lon": 36.3, "f_usa": 0, "f_irn": 85},
    {"id": "Irak: Kurdystan", "eth": "Kurdowie", "rel": "Sunnici", "pos_x": -0.35, "pos_y": 0.1, "type": "mod", "lat": 36.5, "lon": 44.0, "f_usa": 60, "f_irn": 0},
    {"id": "Irak", "eth": "Arabowie", "rel": "Sunnici", "pos_x": -0.1, "pos_y": 0.1, "type": "mod", "lat": 33.3, "lon": 44.0, "f_usa": 30, "f_irn": 20},
    {"id": "Irak ", "eth": "Arabowie", "rel": "Szyici", "pos_x": 0.15, "pos_y": 0.1, "type": "mod", "lat": 33.3, "lon": 45.0, "f_usa": 30, "f_irn": 60},
    {"id": "Iran", "eth": "Persowie", "rel": "Szyici", "pos_x": 0.9, "pos_y": 0.2, "type": "rad", "lat": 35.7, "lon": 51.4, "f_usa": 0, "f_irn": 100},
    {"id": "Jemen: Huti", "eth": "Arabowie", "rel": "Szyici", "pos_x": 0.3, "pos_y": -0.6, "type": "rad", "lat": 15.3, "lon": 44.2, "f_usa": 0, "f_irn": 90},
    {"id": "S. Arabia", "eth": "Arabowie", "rel": "Sunnici", "pos_x": -1.0, "pos_y": -0.6, "type": "mod", "lat": 24.7, "lon": 46.6, "f_usa": 80, "f_irn": 5},
    {"id": "Katar", "eth": "Arabowie", "rel": "Sunnici", "pos_x": -0.5, "pos_y": -0.7, "type": "mod", "lat": 25.3, "lon": 48.0, "f_usa": 90, "f_irn": 10},
    {"id": "ZEA", "eth": "Arabowie", "rel": "Sunnici", "pos_x": -0.3, "pos_y": -0.8, "type": "mod", "lat": 24.4, "lon": 52.0, "f_usa": 85, "f_irn": 0},
    {"id": "Afganistan", "eth": "Pasztuni", "rel": "Sunnici", "pos_x": 1.2, "pos_y": 0.6, "type": "rad", "lat": 33.9, "lon": 67.7, "f_usa": 0, "f_irn": 30},
    {"id": "Pakistan", "eth": "Pendżabczycy", "rel": "Sunnici", "pos_x": 1.2, "pos_y": -0.1, "type": "mod", "lat": 30.3, "lon": 69.3, "f_usa": 40, "f_irn": 20},
    {"id": "Indie", "eth": "Indusowie", "rel": "Hinduizm", "pos_x": 1.6, "pos_y": -0.2, "type": "mod", "lat": 20.5, "lon": 78.9, "f_usa": 60, "f_irn": 30},
    {"id": "Rosja", "eth": "Słowianie", "rel": "Prawosławie", "pos_x": 1.6, "pos_y": 0.6, "type": "mod", "lat": 55, "lon": 37, "f_usa": 0, "f_irn": 80},
    {"id": "Chiny", "eth": "Han", "rel": "Buddyzm/Ateizm", "pos_x": 1.9, "pos_y": 0.1, "type": "mod", "lat": 35, "lon": 105, "f_usa": 10, "f_irn": 40}
])
nodes_df.to_csv('nodes_config.csv', index=False)

# 1.3 Edges Config
edges_df = pd.DataFrame([
    ("Iran", "Liban: Hezbollah", "green", "-"), ("Iran", "Jemen: Huti", "green", "-"), ("Iran", "Syria", "green", "-"),
    ("Iran", "Palestyna: Hamas", "green", "-"), ("USA", "Izrael", "green", "-"), ("USA", "Egipt", "green", "-"),
    ("USA", "Katar", "green", "-"), ("USA", "ZEA", "green", "-"), ("S. Arabia", "USA", "green", "-"),
    ("Rosja", "Syria", "green", "-"), ("Rosja", "Iran", "green", "-"), ("Rosja", "Chiny", "green", "-"),
    ("Chiny", "Iran", "green", "-"), ("Chiny", "Syria", "green", "--"), ("Turcja", "USA", "green", "-"),
    ("Izrael", "S. Arabia", "green", "--"), ("Turcja", "Turcja: Kurdystan", "red", "--"),
    ("Iran", "Izrael", "red", "-"), ("Iran", "USA", "red", "-"), ("Liban: Hezbollah", "Izrael", "red", "-"),
    ("Iran", "S. Arabia", "red", "--"), ("Iran", "ZEA", "red", "--"), ("Iran", "Pakistan", "red", "--"),
    ("Indie", "Rosja", "green", "-"), ("Indie", "USA", "green", "--"), ("Indie", "Pakistan", "red", "--"), 
    ("Indie", "Chiny", "red", "--"), ("Afganistan", "Iran", "red", "--"), ("Afganistan", "Pakistan", "red", "--"), 
    ("Afganistan", "Rosja", "green", "--")
], columns=['source', 'target', 'color', 'style'])
edges_df.to_csv('edges_config.csv', index=False)

# 1.4 Translations (Locale)
trans_df = pd.DataFrame({
    'key': [
        'title_geopolitics', 'title_market', 'title_funding', 'label_oil', 'label_gas', 
        'label_usd', 'label_diesel', 'label_lng', 'axis_usd', 'axis_fx', 'axis_pln', 
        'legend_mod', 'legend_rad', 'rel_full', 'rel_part', 'rel_hostile', 'rel_tension', 
        'rel_shia', 'rel_sunni', 'fund_usa', 'fund_iran'
    ],
    'PL': [
        'GEOPOLITYCZNA MAPA RELACJI', 'WPŁYW KONFLIKTU NA CENY SUROWCÓW', 'POZIOM FINANSOWANIA UZBROJENIA',
        'Ropa Brent ($)', 'Gaz Świat ($)', 'Kurs USD/PLN', 'Diesel PL (zł)', 'LNG PL (zł)',
        'USD ($) - Ropa i Gaz Świat', 'Kurs Waluty USD/PLN', 'Cena PLN (zł) - Paliwa PL',
        'Umiarkowani', 'Radykalni', 'Sojusz pełny (Biznes i Wojsko)', 'Sojusz częściowy (Wspólny Wróg)',
        'Wrogość (Ostrzał Zmasowany)', 'Napięcie (Ostrzał Punktowy)', 'Korelacja Szyici/Alawici',
        'Korelacja Sunnici', 'Finansowanie USA (%)', 'Finansowanie Iran (%)'
    ]
})
trans_df.to_csv('translations.csv', index=False)

# =============================================================================
# STEP 2: DASHBOARD ENGINE (Load from CSV and Render)
# =============================================================================

# Global Settings
LOCALE = 'PL'
m_df = pd.read_csv('market_data.csv')
n_df = pd.read_csv('nodes_config.csv')
e_df = pd.read_csv('edges_config.csv')
t_df = pd.read_csv('translations.csv').set_index('key')[LOCALE].to_dict()

# --- FIGURE 1: GEOPOLITICS ---
fig1 = plt.figure(figsize=(18, 10))
ax1 = fig1.add_subplot(111)
fig1.subplots_adjust(left=0.05, right=0.75, top=0.9, bottom=0.05)

G = nx.Graph()
pos_net = {row['id']: (row['pos_x'], row['pos_y']) for _, row in n_df.iterrows()}

# Background Correlations
for i, u in n_df.iterrows():
    for j, v in n_df.iterrows():
        if i < j:
            if u['rel'] in ["Szyici", "Alawici"] and v['rel'] in ["Szyici", "Alawici"]:
                ax1.plot([u['pos_x'], v['pos_x']], [u['pos_y'], v['pos_y']], color="darkviolet", ls=':', alpha=0.3, zorder=1)
            if u['rel'] == "Sunnici" and v['rel'] == "Sunnici":
                ax1.plot([u['pos_x'], v['pos_x']], [u['pos_y'], v['pos_y']], color="blue", ls=':', alpha=0.2, zorder=1)

# Political Edges
for _, row in e_df.iterrows():
    width = 2.5 if row['style'] == "-" else 1.5
    u_pos, v_pos = pos_net[row['source']], pos_net[row['target']]
    ax1.plot([u_pos[0], v_pos[0]], [u_pos[1], v_pos[1]], color=row['color'], ls=row['style'], lw=width, zorder=2)

# Nodes
for _, row in n_df.iterrows():
    color = "saddlebrown" if row['type'] == "rad" else "darkgrey"
    ax1.text(row['pos_x'], row['pos_y'], f"{row['id']}\n{row['eth']}\n{row['rel']}", 
             size=8, ha='center', va='center', fontweight='bold', color='white', 
             bbox=dict(facecolor=color, edgecolor='black', boxstyle='round,pad=0.5'), zorder=3)

leg_el = [
    mpatches.Patch(color='darkgrey', label=t_df["legend_mod"]), 
    mpatches.Patch(color='saddlebrown', label=t_df["legend_rad"]),
    plt.Line2D([0], [0], color='green', lw=2.5, label=t_df["rel_full"]),
    plt.Line2D([0], [0], color='green', lw=1.5, ls='--', label=t_df["rel_part"]),
    plt.Line2D([0], [0], color='red', lw=2.5, label=t_df["rel_hostile"]),
    plt.Line2D([0], [0], color='red', lw=1.5, ls='--', label=t_df["rel_tension"]),
    plt.Line2D([0], [0], color='darkviolet', ls=':', label=t_df["rel_shia"]),
    plt.Line2D([0], [0], color='blue', ls=':', label=t_df["rel_sunni"])
]
ax1.legend(handles=leg_el, loc='upper left', bbox_to_anchor=(1.01, 1.0), fontsize=9)
ax1.set_title(t_df["title_geopolitics"], fontsize=16, fontweight='bold', loc='left', pad=20)
ax1.axis('off')
fig1.savefig('geopolitics.png', dpi=150)

# --- FIGURE 2: MARKET ---
fig2 = plt.figure(figsize=(18, 9))
ax2 = fig2.add_subplot(111)
# Padding: left=0.05, right=0.85 (space for 2nd and 3rd Y axis)
fig2.subplots_adjust(left=0.05, right=0.82, top=0.85, bottom=0.15)

ax2_fx, ax2_pln = ax2.twinx(), ax2.twinx()
ax2_pln.spines['right'].set_position(('outward', 70)) # Odsunięcie trzeciej osi

# Plotting with explicit handles for the legend
p1, = ax2_pln.plot(m_df['dates'], m_df['diesel'], color='saddlebrown', marker='s', lw=1.5, label=t_df["label_diesel"])
p2, = ax2.plot(m_df['dates'], m_df['brent'], color='red', marker='o', lw=2.5, label=t_df["label_oil"])
p3, = ax2_fx.plot(m_df['dates'], m_df['usd_pln'], color='gold', ls=':', lw=2, label=t_df["label_usd"])
p4, = ax2_pln.plot(m_df['dates'], m_df['lng'], color='turquoise', marker='^', lw=1.5, label=t_df["label_lng"])
p5, = ax2.plot(m_df['dates'], m_df['gas'], color='green', marker='d', lw=2, label=t_df["label_gas"])

# Annotations (Events)
for i, txt in enumerate(m_df['events']):
    ax2.annotate(txt, (m_df['dates'][i], m_df['gas'][i]), textcoords="offset points", xytext=(0,20), 
                 ha='center', fontsize=8, rotation=35, fontweight='bold', 
                 bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='grey', alpha=0.9))

# X-Axis Fix: Ensure all dates are visible and padding is maintained
ax2.set_xticks(range(len(m_df['dates'])))
ax2.set_xticklabels(m_df['dates'])
ax2.set_xlim(-0.8, len(m_df['dates']) - 0.2)

# Labels & Title
ax2.set_title(t_df["title_market"], fontsize=18, fontweight='bold', loc='left', pad=40)
ax2.set_ylabel(t_df["axis_usd"], color='red', fontweight='bold')
ax2_fx.set_ylabel(t_df["axis_fx"], color='gold', fontweight='bold')
ax2_pln.set_ylabel(t_df["axis_pln"], color='saddlebrown', fontweight='bold')

# Unified Legend from all axes
all_handles = [p1, p2, p3, p4, p5]
all_labels = [h.get_label() for h in all_handles]
ax2.legend(all_handles, all_labels, loc='upper left', frameon=True, fontsize=10)

ax2.grid(True, linestyle='--', alpha=0.4)
fig2.savefig('market.png', dpi=150)

# --- FIGURE 3: FUNDING ---
fig3 = plt.figure(figsize=(18, 8))
ax3 = fig3.add_subplot(111)
fig3.subplots_adjust(left=0.08, right=0.92, top=0.9, bottom=0.1)
ax3.set_xlim(29, 82)
ax3.set_ylim(10, 45)

plot_n = n_df[~n_df['id'].isin(["USA", "Rosja", "Chiny"])]
for i, (_, row) in enumerate(plot_n.iterrows()):
    ax3.scatter(row['lon'], row['lat'], c=[row['f_irn']], cmap='Reds', vmin=0, vmax=100, 
                s=350, edgecolors=plt.cm.Blues(row['f_usa']/100), linewidths=5)
    ax3.annotate(row['id'], (row['lon'], row['lat']), xytext=(0, 12 if i%2==0 else -20), 
                 textcoords='offset points', ha='center', fontsize=8, fontweight='bold')

plt.colorbar(plt.cm.ScalarMappable(cmap='Blues'), ax=ax3, location='left', pad=0.02, shrink=0.7).set_label(t_df["fund_usa"])
plt.colorbar(plt.cm.ScalarMappable(cmap='Reds'), ax=ax3, location='right', pad=0.02, shrink=0.7).set_label(t_df["fund_iran"])
ax3.set_title(t_df["title_funding"], fontsize=16, fontweight='bold', loc='left', pad=20)
ax3.grid(True, alpha=0.15)
fig3.savefig('funding.png', dpi=150)

plt.show()


