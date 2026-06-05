import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
import os

from adjustText import adjust_text


# 1. Ładowanie danych z pliku zewnętrznego
def load_data(filename='data/genetics_data.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return pd.DataFrame(json.load(f))
    else:
        print(f"Błąd: Nie znaleziono pliku {filename}!")
        return pd.DataFrame()

df_genetics = load_data()

# 2. Pobieranie mapy
url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
world = gpd.read_file(url)
name_col = 'name' # W tym JSONie to zazwyczaj 'name'

# 3. Obliczenia
df_genetics['AB_total'] = 2 * df_genetics['p_A'] * df_genetics['q_B']
df_genetics['AB_minus'] = df_genetics['AB_total'] * df_genetics['Rh_neg']

# 4. Merge
merged = world.merge(df_genetics, on='name', how='left')

# 5. Wizualizacja (Układ: Mapy góra, PCA dół)
fig = plt.figure(figsize=(24, 15))
fig.suptitle('Globalny Atlas Serogenetyczny: Interakcja Alleli i Admixture (f3/D)', fontsize=26, fontweight='bold')
gs = gridspec.GridSpec(2, 3, height_ratios=[1.2, 1])

# Definicja osi
ax_ab = plt.subplot(gs[0, 0])
ax_f3 = plt.subplot(gs[0, 1])
ax_b = plt.subplot(gs[0, 2])
ax_pca = plt.subplot(gs[1, :])

# Konfiguracja wspólna dla map
map_params = {'missing_kwds': {'color': '#e0e0e0', 'label': 'Brak danych'}, 'legend': True}

# --- MAPY: Dodajemy zoom na Europę i Bliski Wschód ---
merged.plot(column='AB_minus', ax=ax_ab, cmap='plasma', **map_params)
ax_ab.set_title('Fenotyp AB- (Częstość występowania)', fontsize=15)

merged.plot(column='f3_admix', ax=ax_f3, cmap='RdYlBu', **map_params)
ax_f3.set_title('Sygnał f3 (Outgroup Admixture)', fontsize=15)

merged.plot(column='q_B', ax=ax_b, cmap='YlOrRd', **map_params)
ax_b.set_title('Częstość Allelu B', fontsize=15)

# for ax in [ax_ab, ax_f3, ax_b]: ax.set_axis_off()
# Przybliżenie na Europę (wykonujemy to dla każdej mapy)
for ax in [ax_ab, ax_f3, ax_b]:
    ax.set_xlim(-15, 55)  # Granice długości geograficznej
    ax.set_ylim(30, 70)   # Granice szerokości geograficznej
    ax.set_axis_off()

# --- WYKRES PCA: Skalujemy dane G25 (D_stat i f3_admix) ---
ax_pca.set_facecolor('#fdfdfd')

# Wykres PCA (D-stat vs f3)
ax_pca.set_facecolor('#fdfdfd')
# scatter = ax_pca.scatter(df_genetics['D_stat'], df_genetics['f3_admix'], 
#                          s=df_genetics['AB_total']*2500, c=df_genetics['AB_total'], 
#                          cmap='viridis', edgecolors='black', alpha=0.7, zorder=3)
# Mnożymy wartości przez 100, aby ułamki (np. 0.01) stały się czytelnymi jednostkami
scatter = ax_pca.scatter(df_genetics['D_stat'] * 100, 
                         df_genetics['f3_admix'] * 100,
                         s=df_genetics['AB_total'] * 2500, 
                         c=df_genetics['AB_total'],
                         cmap='viridis', edgecolors='black', alpha=0.7, zorder=3)

# Inteligentne etykiety (z drobnym rozproszeniem)
texts = []
# for i, row in df_genetics.iterrows():
#     # ax_pca.annotate(row['name'], (row['D_stat'], row['f3_admix']), 
#     #                 xytext=(5, 5), textcoords='offset points', fontsize=10, fontweight='bold')
#     texts.append(ax_pca.text(row['D_stat'], row['f3_admix'], row['name'], 
#                              fontsize=10, fontweight='bold'))
# Inteligentne etykiety (również skalujemy pozycję tekstu)
texts = []
for i, row in df_genetics.iterrows():
    texts.append(ax_pca.text(row['D_stat'] * 100, 
                             row['f3_admix'] * 100, 
                             row['name'],
                             fontsize=10, fontweight='bold'))

# Automatyczne rozsuwanie tekstów, by się nie nakładały
adjust_text(texts, ax=ax_pca, arrowprops=dict(arrowstyle='->', color='red', lw=0.5))

# Linie pomocnicze (Gradienty)
# ax_pca.plot([-0.5, 1.0], [0, -0.07], '--', color='red', alpha=0.4, label='Major Genetic Cline')
# ax_pca.set_xlabel('D-statistic (Genetic Distance to Reference)', fontsize=12)
# ax_pca.set_ylabel('f3-statistic (Admixture Strength)', fontsize=12)
# ax_pca.grid(True, linestyle=':', alpha=0.6)
# Dodajemy opisy osi dla lepszej orientacji
ax_pca.set_xlabel('D-stat (Scaled PC1 x 100)', fontsize=12)
ax_pca.set_ylabel('f3-admix (Scaled PC2 x 100)', fontsize=12)
ax_pca.grid(True, linestyle='--', alpha=0.3)

# Dodanie Izolatu (Aszkenazyjczycy) jako gwiazdka
ax_pca.scatter([0.35], [-0.06], s=500, marker='*', color='gold', edgecolors='black', label='★ Ashkenazi Isolate (Extrema)', zorder=5)
ax_pca.legend()

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()


