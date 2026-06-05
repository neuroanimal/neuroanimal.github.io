import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
import os
from adjustText import adjust_text

# 1. Ładowanie danych
def load_data(filename='data/genetics_data.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            df = pd.DataFrame(json.load(f))
            return df
    return pd.DataFrame()

df_genetics = load_data()

# 2. Obliczenia podstawowe
df_genetics['AB_total'] = 2 * df_genetics['p_A'] * df_genetics['q_B']
df_genetics['AB_minus'] = df_genetics['AB_total'] * df_genetics['Rh_neg']

# --- 4. PRZYGOTOWANIE DANYCH DO MAPY (KLUCZOWE!) ---
# Tworzymy kopię danych tylko dla mapy, gdzie "Ashkenazi_Poland" zamieniamy na "Poland"
# Dzięki temu mapa "zobaczy" dane przypisane do konkretnego obszaru.
df_for_map = df_genetics.copy()

# Jeśli nazwa zawiera "Ashkenazi_", wyciągamy tylko nazwę kraju po podkreśleniu
df_for_map['map_name'] = df_for_map['name'].apply(lambda x: x.split('_')[-1] if 'Ashkenazi_' in x else x)

# Poprawki nazw dla GeoJSON (mapa ma "Czech Republic", "Russia" itd.)
map_fix = {
    'Czechia': 'Czech Republic',
    'Belarussia': 'Belarus',
    'Russia': 'Russian Federation' # lub 'Russia' zależnie od wersji GeoJSON
}
df_for_map['map_name'] = df_for_map['map_name'].replace(map_fix)

# 2. Pobieranie mapy
url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
world = gpd.read_file(url)

# 4. Merge (łączymy po 'map_name' z danymi i po 'name' z mapą świata)
merged = world.merge(df_for_map, left_on='name', right_on='map_name', how='left')

# 5. Wizualizacja
fig = plt.figure(figsize=(24, 16))
fig.suptitle('Globalny Atlas Serogenetyczny: G25 i Grupy Krwi', fontsize=26, fontweight='bold')
gs = gridspec.GridSpec(2, 3, height_ratios=[1.2, 1])

ax_ab = plt.subplot(gs[0, 0])
ax_f3 = plt.subplot(gs[0, 1])
ax_b = plt.subplot(gs[0, 2])
ax_pca = plt.subplot(gs[1, :])

map_params = {'missing_kwds': {'color': '#f0f0f0'}, 'legend': True}

# Ustawiamy dynamiczne granice kolorów, żeby widzieć różnice
# (Vmin/Vmax dobrane na podstawie Twoich unikalnych wartości [0.14 - 0.22])
merged.plot(column='AB_minus', ax=ax_ab, cmap='plasma', vmin=0.01, vmax=0.025, **map_params)
ax_ab.set_title('Fenotyp AB- (Częstość)', fontsize=15)

merged.plot(column='f3_admix', ax=ax_f3, cmap='RdYlBu', **map_params)
ax_f3.set_title('Sygnał f3 (PCA PC2)', fontsize=15)

merged.plot(column='q_B', ax=ax_b, cmap='YlOrRd', vmin=0.08, vmax=0.25, **map_params)
ax_b.set_title('Częstość Allelu B', fontsize=15)

for ax in [ax_ab, ax_f3, ax_b]:
    ax.set_xlim(-15, 50)
    ax.set_ylim(32, 68)
    ax.set_axis_off()

# --- WYKRES PCA ---
ax_pca.set_facecolor('#fdfdfd')
df_plot = df_genetics.dropna(subset=['D_stat', 'f3_admix'])

# Rysujemy kropki (kolorowane allelem B)
scatter = ax_pca.scatter(df_plot['D_stat'] * 100, df_plot['f3_admix'] * -100,
                         s=df_plot['AB_total'] * 4000, 
                         c=df_plot['q_B'], cmap='YlOrRd', vmin=0.08, vmax=0.25,
                         edgecolors='black', alpha=0.7, zorder=3)

plt.colorbar(scatter, ax=ax_pca, label='Częstość Allelu B')

texts = []
for i, row in df_plot.iterrows():
    display_name = row['name'].replace('Ashkenazi_', 'Ashk_')
    texts.append(ax_pca.text(row['D_stat'] * 100, row['f3_admix'] * -100, display_name, fontsize=10))

adjust_text(texts, ax=ax_pca, arrowprops=dict(arrowstyle='->', color='red', lw=0.5))

plt.tight_layout()
plt.show()


