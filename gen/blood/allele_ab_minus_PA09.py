import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
import os
from adjustText import adjust_text

# 1. Ładowanie danych - bez agresywnego przycinania
def load_data(filename='data/genetics_data.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            df = pd.DataFrame(json.load(f))
            # Konwersja na liczby, by uniknąć błędów typu string
            cols = ['p_A', 'q_B', 'Rh_neg', 'D_stat', 'f3_admix']
            df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
            return df
    else:
        print(f"Błąd: Nie znaleziono pliku {filename}!")
        return pd.DataFrame()

df_genetics = load_data()

# 2. Mapa
url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
world = gpd.read_file(url)

# 3. Obliczenia
df_genetics['AB_total'] = 2 * df_genetics['p_A'] * df_genetics['q_B']
df_genetics['AB_minus'] = df_genetics['AB_total'] * df_genetics['Rh_neg']

print("--- TEST DANYCH ---")
print(df_genetics[['name', 'q_B', 'AB_minus']].head(10))
print("Unikalne wartości q_B:", df_genetics['q_B'].unique())
print("Typy kolumn:\n", df_genetics.dtypes)

# 4. Merge
merged = world.merge(df_genetics, on='name', how='left')

# 5. Wizualizacja
fig = plt.figure(figsize=(24, 16))
fig.suptitle('Atlas Serogenetyczny: Analiza G25 i Grup Krwi', fontsize=26, fontweight='bold')
gs = gridspec.GridSpec(2, 3, height_ratios=[1.2, 1])

ax_ab = plt.subplot(gs[0, 0])
ax_f3 = plt.subplot(gs[0, 1])
ax_b = plt.subplot(gs[0, 2])
ax_pca = plt.subplot(gs[1, :])

map_params = {'missing_kwds': {'color': '#e0e0e0'}, 'legend': True}

# # MAPY - Używamy percentyli do skali kolorów, aby Estonia nie psuła widoku
# # To sprawi, że kolory będą zróżnicowane niezależnie od ekstremów
# merged.plot(column='AB_minus', ax=ax_ab, cmap='plasma', **map_params)
# ax_ab.set_title('Fenotyp AB-', fontsize=14)
# 
# merged.plot(column='f3_admix', ax=ax_f3, cmap='RdYlBu', **map_params)
# ax_f3.set_title('Sygnał f3', fontsize=14)
# 
# merged.plot(column='q_B', ax=ax_b, cmap='YlOrRd', **map_params)
# ax_b.set_title('Częstość Allelu B', fontsize=14)

# --- MAPY: Dynamiczne skalowanie kolorów ---

# Obliczamy granice kolorów na podstawie 10. i 90. percentyla
# To odcina ekstremalne wartości (outliery) tylko na potrzeby kolorowania
def get_vlimits(series):
    return series.quantile(0.1), series.quantile(0.9)

# Dla AB-
v_min_ab, v_max_ab = get_vlimits(df_genetics['AB_minus'])
merged.plot(column='AB_minus', ax=ax_ab, cmap='plasma', 
            vmin=v_min_ab, vmax=v_max_ab, **map_params)
ax_ab.set_title('Fenotyp AB- (Skala zbalansowana)', fontsize=14)

# Dla f3
merged.plot(column='f3_admix', ax=ax_f3, cmap='RdYlBu', **map_params)
ax_f3.set_title('Sygnał f3', fontsize=14)

# Dla Allelu B
v_min_b, v_max_b = get_vlimits(df_genetics['q_B'])
merged.plot(column='q_B', ax=ax_b, cmap='YlOrRd', 
            vmin=v_min_b, vmax=v_max_b, **map_params)
ax_b.set_title('Częstość Allelu B (Skala zbalansowana)', fontsize=14)

for ax in [ax_ab, ax_f3, ax_b]:
    ax.set_xlim(-15, 50)
    ax.set_ylim(32, 68)
    ax.set_axis_off()

# --- WYKRES PCA ---
ax_pca.set_facecolor('#fdfdfd')

# Usuwamy tylko wiersze, które naprawdę nie mają współrzędnych
df_plot = df_genetics.dropna(subset=['D_stat', 'f3_admix']).copy()

if not df_plot.empty:
    # Rysujemy wszystko razem, by uniknąć problemów z pustymi df_countries
    scatter = ax_pca.scatter(df_plot['D_stat'] * 100, 
                             df_plot['f3_admix'] * -100,
                             s=df_plot['AB_total'] * 4000, 
                             c=df_plot['q_B'], cmap='YlOrRd', 
                             edgecolors='black', alpha=0.7, zorder=3)
    
    # Dodajemy legendę kolorów (Allelu B) dla PCA
    plt.colorbar(scatter, ax=ax_pca, label='Częstość Allelu B')

    # Automatyczne skalowanie osi zamiast set_xlim
    ax_pca.autoscale(enable=True, tight=False)

    texts = []
    for i, row in df_plot.iterrows():
        display_name = row['name'].replace('Ashkenazi_', 'Ashk_')
        texts.append(ax_pca.text(row['D_stat'] * 100, row['f3_admix'] * -100, 
                                 display_name, fontsize=10))

    adjust_text(texts, ax=ax_pca, arrowprops=dict(arrowstyle='->', color='red', lw=0.5))

ax_pca.set_xlabel('PC1 (Genetic Distance x 100)')
ax_pca.set_ylabel('PC2 (North-South inverted x 100)')
ax_pca.grid(True, linestyle='--', alpha=0.3)

plt.tight_layout()
plt.show()


