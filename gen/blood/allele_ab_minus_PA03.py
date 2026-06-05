import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# 1. Pobieranie mapy z pliku GeoJSON
url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
try:
    world = gpd.read_file(url)
except:
    import geodatasets
    url = geodatasets.get_path('naturalearth.admin_0_countries')
    world = gpd.read_file(url)

name_col = 'ADMIN' if 'ADMIN' in world.columns else 'name' if 'name' in world.columns else 'name_en'

# 2. DYNAMICZNE WYCIĄGNIĘCIE WSZYSTKICH KRAJÓW Z JSON
all_countries = world[name_col].unique()

# Twoje rzeczywiste dane dla wybranych populacji
real_data = {
    'Poland': {'p_A': 0.38, 'q_B': 0.19, 'Rh_neg': 0.15, 'f3_admix': -0.020, 'D_stat': -0.20},
    'Israel': {'p_A': 0.34, 'q_B': 0.22, 'Rh_neg': 0.12, 'f3_admix': -0.050, 'D_stat': 0.40},
    'Japan': {'p_A': 0.28, 'q_B': 0.17, 'Rh_neg': 0.005, 'f3_admix': 0.001, 'D_stat': 0.80},
    'Hungary': {'p_A': 0.36, 'q_B': 0.20, 'Rh_neg': 0.14, 'f3_admix': -0.030, 'D_stat': -0.10},
    'India': {'p_A': 0.18, 'q_B': 0.25, 'Rh_neg': 0.02, 'f3_admix': -0.010, 'D_stat': 0.60},
    'Lithuania': {'p_A': 0.39, 'q_B': 0.16, 'Rh_neg': 0.15, 'f3_admix': -0.015, 'D_stat': -0.30},
    'Ukraine': {'p_A': 0.35, 'q_B': 0.23, 'Rh_neg': 0.09, 'f3_admix': -0.040, 'D_stat': 0.20},
    'Czechia': {'p_A': 0.37, 'q_B': 0.18, 'Rh_neg': 0.15, 'f3_admix': -0.022, 'D_stat': -0.18},
    'Slovakia': {'p_A': 0.36, 'q_B': 0.19, 'Rh_neg': 0.14, 'f3_admix': -0.025, 'D_stat': -0.15}
}

# 3. BUDOWANIE PEŁNEJ BAZY DANYCH (Realne + Symulowane dla reszty)
np.random.seed(42) # Stałe ziarno, żeby kolory nie skakały przy każdym uruchomieniu
data_rows = []

for country in all_countries:
    if country in real_data:
        # Jeśli mamy prawdziwe dane - użyj ich
        row = {'name': country, **real_data[country]}
    else:
        # Jeśli nie mamy, generujemy "mock data" by wypełnić mapę
        row = {
            'name': country,
            'p_A': np.random.uniform(0.15, 0.45),
            'q_B': np.random.uniform(0.05, 0.30),
            'Rh_neg': np.random.uniform(0.0, 0.16),
            'f3_admix': np.random.uniform(-0.06, 0.02),
            'D_stat': np.random.uniform(-0.5, 1.0)
        }
    data_rows.append(row)

df = pd.DataFrame(data_rows)

# 4. Obliczenia fenotypów
df['AB_total'] = 2 * df['p_A'] * df['q_B']
df['AB_minus'] = df['AB_total'] * df['Rh_neg']

# 5. Łączenie pełnej tabeli z geometrią
merged = world.merge(df, left_on=name_col, right_on='name', how='left')

# 6. Wizualizacja (Układ z poprzedniego kodu)
fig = plt.figure(figsize=(22, 14))
fig.suptitle('Serogenetyka Populacyjna: Pełny Glob (Dane Rzeczywiste + Symulowane)', fontsize=24, fontweight='bold', y=0.98)
gs = gridspec.GridSpec(2, 3, height_ratios=[1.5, 1])

ax1 = plt.subplot(gs[0, 0])
ax2 = plt.subplot(gs[0, 1])
ax3 = plt.subplot(gs[0, 2])
ax4 = plt.subplot(gs[1, :])

# Mapa 1: Fenotyp AB-
merged.plot(column='AB_minus', ax=ax1, legend=True, cmap='magma', legend_kwds={'shrink': 0.5})
ax1.set_title('Fenotyp AB- (Rh- x Allel B)', fontsize=14)
ax1.set_axis_off()

# Mapa 2: Statystyka f3
merged.plot(column='f3_admix', ax=ax2, legend=True, cmap='RdBu', legend_kwds={'shrink': 0.5})
ax2.set_title('Statystyka f3 (Admixture Level)', fontsize=14)
ax2.set_axis_off()

# Mapa 3: Allel B 
merged.plot(column='q_B', ax=ax3, legend=True, cmap='YlGnBu', legend_kwds={'shrink': 0.5})
ax3.set_title('Częstotliwość Allelu B', fontsize=14)
ax3.set_axis_off()

# Wykres 4: Przestrzeń Genetyczna (PCA) - Pokazujemy tylko wybrane (rzeczywiste) kraje dla czytelności!
ax4.set_facecolor('#f9f9f9')
# Filtrujemy df tylko do krajów z prawdziwymi danymi, inaczej wykres miałby 250 zlewających się kropek
df_real = df[df['name'].isin(real_data.keys())].reset_index()

scatter = ax4.scatter(df_real['D_stat'], df_real['f3_admix'], s=df_real['AB_total']*1500, 
                      c=df_real['AB_total'], cmap='viridis', edgecolors='black', alpha=0.8, zorder=3)

for i, txt in enumerate(df_real['name']):
    x_offset, y_offset = 7, 7
    if txt == 'Poland': y_offset = 12
    if txt == 'Czechia': y_offset = -15
    if txt == 'Slovakia': x_offset = -30; y_offset = 12
    
    ax4.annotate(txt, (df_real['D_stat'][i], df_real['f3_admix'][i]), 
                 xytext=(x_offset, y_offset), textcoords='offset points', 
                 fontsize=11, fontweight='bold', zorder=4)

ax4.plot([-0.5, 1.0], [0, -0.06], '--', color='red', alpha=0.6, label='European-Levant Cline', zorder=2)
ax4.set_title('Przestrzeń Genetyczna: D-statistic vs f3 (Tylko analizowane kraje)', fontsize=16)
ax4.set_xlabel('D-stat (Distance)', fontsize=12)
ax4.set_ylabel('f3 (Admixture)', fontsize=12)
ax4.grid(True, linestyle='--', alpha=0.5, zorder=1)
ax4.scatter([0.35], [-0.055], s=400, marker='*', color='gold', edgecolors='black', label='★ Ashkenazi Isolate (18% AB)', zorder=5)
ax4.legend(loc='lower left')

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()


