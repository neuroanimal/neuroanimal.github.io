import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
import os
from adjustText import adjust_text

# --- 1. ŁADOWANIE I MAPOWANIE DANYCH ---
def get_processed_data(filename='data/genetics_data.json'):
    if not os.path.exists(filename):
        print("Błąd: Brak pliku JSON. Uruchom najpierw parser!")
        return None, None
    
    with open(filename, 'r') as f:
        df = pd.DataFrame(json.load(f))

    # Obliczenia bazowe (na surowych danych)
    df['p_A'] = pd.to_numeric(df['p_A'])
    df['q_B'] = pd.to_numeric(df['q_B'])
    df['Rh_neg'] = pd.to_numeric(df['Rh_neg'])
    df['AB_total'] = 2 * df['p_A'] * df['q_B']
    df['AB_minus'] = df['AB_total'] * df['Rh_neg']

    # Słownik mapowania nazw G25 -> Nazwy standardowe dla mapy
    name_map = {
        'Czech': 'Czechia',
        'Slovakian': 'Slovakia',
        'Polish': 'Poland',
        'Polish_Kashubian': 'Poland',
        'Polish_Silesian': 'Poland',
        'Belarussian': 'Belarus',
        'Ukrainian': 'Ukraine',
        'Hungarian': 'Hungary'
    }

    # Funkcja czyszcząca nazwy pod mapę
    def to_map_name(name):
        if name in name_map: return name_map[name]
        if 'Russian_' in name: return 'Russia'
        if 'Ashkenazi_' in name:
            country = name.split('_')[-1]
            return name_map.get(country, country)
        return name

    df['map_name'] = df['name'].apply(to_map_name)

    # Agregacja dla mapy (uśredniamy regiony takie jak Orel, Kursk do jednego kraju)
    df_map_agg = df.groupby('map_name').agg({
        'p_A': 'mean', 'q_B': 'mean', 'Rh_neg': 'mean',
        'AB_total': 'mean', 'AB_minus': 'mean',
        'f3_admix': 'mean'
    }).reset_index()

    return df, df_map_agg

df_genetics, df_for_map = get_processed_data()

# --- 2. PRZYGOTOWANIE GEOGRAFII ---
url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
world = gpd.read_file(url)

# Poprawki specyficzne dla nazw w pliku GeoJSON
geojson_fix = {
    'Russia': 'Russian Federation',
    'Czechia': 'Czech Republic',
    'Palestine': 'West Bank'
}
df_for_map['map_name'] = df_for_map['map_name'].replace(geojson_fix)

# Łączenie danych z poligonami mapy
merged = world.merge(df_for_map, left_on='name', right_on='map_name', how='left')

# --- 3. WIZUALIZACJA ---
fig = plt.figure(figsize=(24, 18))
fig.suptitle('Analiza Serogenetyczna Europy Środkowo-Wschodniej', fontsize=28, fontweight='bold', y=0.95)
gs = gridspec.GridSpec(2, 3, height_ratios=[1.2, 1])

ax_ab = plt.subplot(gs[0, 0])
ax_f3 = plt.subplot(gs[0, 1])
ax_b = plt.subplot(gs[0, 2])
ax_pca = plt.subplot(gs[1, :])

map_params = {'missing_kwds': {'color': '#efefef'}, 'legend': True}

# MAPA 1: AB- (Kluczowy fenotyp)
merged.plot(column='AB_minus', ax=ax_ab, cmap='plasma', 
            vmin=df_for_map['AB_minus'].min(), vmax=df_for_map['AB_minus'].max(), **map_params)
ax_ab.set_title('Fenotyp AB- (Częstość)', fontsize=16)

# MAPA 2: f3 (Sygnał dryfu/domieszki)
merged.plot(column='f3_admix', ax=ax_f3, cmap='RdYlBu', **map_params)
ax_f3.set_title('Sygnał f3 (G25 PC2)', fontsize=16)

# MAPA 3: Allel B (Gradient wschodni)
merged.plot(column='q_B', ax=ax_b, cmap='YlOrRd', 
            vmin=0.08, vmax=0.25, **map_params)
ax_b.set_title('Częstość Allelu B', fontsize=16)

# Kadrowanie map na Europę
for ax in [ax_ab, ax_f3, ax_b]:
    ax.set_xlim(-15, 55)
    ax.set_ylim(34, 70)
    ax.set_axis_off()

# --- 4. WYKRES PCA (PEŁNA DYNAMIKA) ---
ax_pca.set_facecolor('#fafafa')

# Na PCA rysujemy wszystkie punkty z df_genetics (nieuśrednione!)
scatter = ax_pca.scatter(df_genetics['D_stat'] * 100, 
                         df_genetics['f3_admix'] * -100,
                         s=df_genetics['AB_total'] * 5000, 
                         c=df_genetics['q_B'], cmap='YlOrRd', 
                         vmin=0.08, vmax=0.25,
                         edgecolors='black', alpha=0.75, zorder=3)

plt.colorbar(scatter, ax=ax_pca, label='Częstość Allelu B')

# Etykiety punktów
texts = []
for i, row in df_genetics.iterrows():
    label = row['name'].replace('Ashkenazi_', 'Ashk_').replace('Russian_', 'Rus_')
    texts.append(ax_pca.text(row['D_stat'] * 100, row['f3_admix'] * -100, label, fontsize=9))

adjust_text(texts, ax=ax_pca, arrowprops=dict(arrowstyle='->', color='red', lw=0.5))

ax_pca.set_xlabel('Genetic Distance (PC1) x 100', fontsize=12)
ax_pca.set_ylabel('Admixture Signal (PC2) x -100', fontsize=12)
ax_pca.grid(True, linestyle='--', alpha=0.4)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()


