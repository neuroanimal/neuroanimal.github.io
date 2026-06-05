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
merged.plot(column='AB_minus', ax=ax_ab, cmap='plasma', vmin=0, vmax=0.015, **map_params)
ax_ab.set_title('Fenotyp AB- (Częstość występowania)', fontsize=15)

merged.plot(column='f3_admix', ax=ax_f3, cmap='RdYlBu', **map_params)
ax_f3.set_title('Sygnał f3 (Outgroup Admixture)', fontsize=15)

merged.plot(column='q_B', ax=ax_b, cmap='YlOrRd', vmin=0.05, vmax=0.25, **map_params)
ax_b.set_title('Częstość Allelu B', fontsize=15)

# for ax in [ax_ab, ax_f3, ax_b]: ax.set_axis_off()
# Przybliżenie na Europę (wykonujemy to dla każdej mapy)
for ax in [ax_ab, ax_f3, ax_b]:
    ax.set_xlim(-15, 55)  # Granice długości geograficznej
    ax.set_ylim(30, 70)   # Granice szerokości geograficznej
    ax.set_axis_off()

# --- WYKRES PCA (D-stat vs f3) ---
ax_pca.set_facecolor('#f9f9f9')

# Rozdzielamy kraje od izolatów dla lepszej kontroli wizualnej
df_countries = df_genetics[df_genetics['is_isolate'] == False].dropna(subset=['D_stat', 'f3_admix'])
df_isolates = df_genetics[df_genetics['is_isolate'] == True].dropna(subset=['D_stat', 'f3_admix'])

# 1. Rysujemy kraje (Kółka)
# UWAGA: Mnożymy f3_admix przez -100, aby Północ była na górze!
ax_pca.scatter(df_countries['D_stat'] * 100, df_countries['f3_admix'] * -100, 
               s=df_countries['AB_total'] * 2000, c='#3498db', edgecolors='black', alpha=0.6, label='Państwa')

# 2. Rysujemy Izolaty (Gwiazdki/Krzyżyki)
ax_pca.scatter(df_isolates['D_stat'] * 100, df_isolates['f3_admix'] * -100, 
               s=df_isolates['AB_total'] * 1500, c='#e74c3c', marker='X', alpha=0.8, label='Izolaty Ashkenazi')

# 3. Inteligentne etykiety z adjust_text
texts = []
for i, row in df_genetics.iterrows():
    # Krótsza nazwa dla Ashkenazi (np. "Ashk_Poland")
    display_name = row['name'].replace('Ashkenazi_', 'Ashk_')
    
    texts.append(ax_pca.text(row['D_stat'] * 100, row['f3_admix'] * -100, display_name,
                             fontsize=9, fontweight='bold' if not row['is_isolate'] else 'normal'))

# Magia adjust_text - rozsunie zlewające się kraje V4 i Ashkenazi
adjust_text(texts, ax=ax_pca, 
            expand_points=(1.5, 1.5), 
            arrowprops=dict(arrowstyle='->', color='grey', lw=0.5))

# Opisy osi
ax_pca.set_xlabel('Genetic Distance (PC1 scaled)', fontsize=12)
ax_pca.set_ylabel('North-South Admixture (PC2 inverted)', fontsize=12)
ax_pca.set_title('Przestrzeń Genetyczna: Klastry Populacyjne i Izolaty', fontsize=16)
ax_pca.legend(loc='upper left')
ax_pca.grid(True, linestyle=':', alpha=0.4)

# Dodanie Izolatu (Aszkenazyjczycy) jako gwiazdka
# ax_pca.scatter([0.35], [-0.06], s=500, marker='*', color='gold', edgecolors='black', label='★ Ashkenazi Isolate (Extrema)', zorder=5)
ax_pca.legend()

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()


