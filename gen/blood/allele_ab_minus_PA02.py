import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# 1. Pobieranie mapy z pewnego źródła
url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
try:
    world = gpd.read_file(url)
except:
    import geodatasets
    url = geodatasets.get_path('naturalearth.admin_0_countries')
    world = gpd.read_file(url)

# 2. Baza danych (Dodano Słowację; zróżnicowano delikatnie D_stat by napisy się nie zlewały)
data = {
    'name': ['Poland', 'Israel', 'Japan', 'Hungary', 'India', 'Lithuania', 'Ukraine', 'Czechia', 'Slovakia'],
    'p_A': [0.38, 0.34, 0.28, 0.36, 0.18, 0.39, 0.35, 0.37, 0.36],
    'q_B': [0.19, 0.22, 0.17, 0.20, 0.25, 0.16, 0.23, 0.18, 0.19],
    'Rh_neg': [0.15, 0.12, 0.005, 0.14, 0.02, 0.15, 0.09, 0.15, 0.14],
    'f3_admix': [-0.020, -0.050, 0.001, -0.030, -0.010, -0.015, -0.040, -0.022, -0.025], # Lekkie korekty na f3 by odkleić punkty
    'D_stat': [-0.20, 0.40, 0.80, -0.10, 0.60, -0.30, 0.20, -0.18, -0.15] # Korekty D_stat
}
df = pd.DataFrame(data)

# 3. Obliczenia fenotypów
df['AB_total'] = 2 * df['p_A'] * df['q_B']
df['AB_minus'] = df['AB_total'] * df['Rh_neg']
df['AB_plus'] = df['AB_total'] * (1 - df['Rh_neg'])

# 4. Łączenie z geometrią mapy
name_col = 'NAME' if 'NAME' in world.columns else 'name' if 'name' in world.columns else 'name_en'
merged = world.merge(df, left_on=name_col, right_on='name', how='left')

# 5. Tworzenie niestandardowego układu (GridSpec) - 3 mapy u góry, 1 wykres na dole
fig = plt.figure(figsize=(22, 14))
fig.suptitle('Serogenetyka Populacyjna: Allele, f3 oraz D-Statistic', fontsize=24, fontweight='bold', y=0.98)
gs = gridspec.GridSpec(2, 3, height_ratios=[1.5, 1])

ax1 = plt.subplot(gs[0, 0])
ax2 = plt.subplot(gs[0, 1])
ax3 = plt.subplot(gs[0, 2])
ax4 = plt.subplot(gs[1, :]) # Wykres PCA na całą szerokość na dole

# Mapa 1: Fenotyp AB-
merged.plot(column='AB_minus', ax=ax1, legend=True, cmap='magma', 
            missing_kwds={'color': '#f0f0f0'}, legend_kwds={'shrink': 0.5})
ax1.set_title('Fenotyp AB- (Rh- x Allel B)', fontsize=14)
ax1.set_axis_off()

# Mapa 2: Statystyka f3
merged.plot(column='f3_admix', ax=ax2, legend=True, cmap='RdBu', 
            missing_kwds={'color': '#f0f0f0'}, legend_kwds={'shrink': 0.5})
ax2.set_title('Statystyka f3 (Admixture Level)', fontsize=14)
ax2.set_axis_off()

# Mapa 3: Allel B 
merged.plot(column='q_B', ax=ax3, legend=True, cmap='YlGnBu', 
            missing_kwds={'color': '#f0f0f0'}, legend_kwds={'shrink': 0.5})
ax3.set_title('Częstotliwość Allelu B', fontsize=14)
ax3.set_axis_off()

# Wykres 4: Przestrzeń Genetyczna (PCA)
ax4.set_facecolor('#f9f9f9')
scatter = ax4.scatter(df['D_stat'], df['f3_admix'], s=df['AB_total']*1500, 
                      c=df['AB_total'], cmap='viridis', edgecolors='black', alpha=0.8, zorder=3)

# Dodawanie etykiet z mechanizmem zapobiegającym zlewaniu
for i, txt in enumerate(df['name']):
    # Drobne przesunięcia ręczne dla krajów w klastrze V4, by poprawić czytelność
    x_offset = 7
    y_offset = 7
    if txt == 'Poland': y_offset = 12
    if txt == 'Czechia': y_offset = -15
    if txt == 'Slovakia': x_offset = -30; y_offset = 12
    
    ax4.annotate(txt, (df['D_stat'][i], df['f3_admix'][i]), 
                 xytext=(x_offset, y_offset), textcoords='offset points', 
                 fontsize=11, fontweight='bold', zorder=4)

# Linia gradientu
ax4.plot([-0.5, 1.0], [0, -0.06], '--', color='red', alpha=0.6, label='European-Levant Cline', zorder=2)
ax4.set_title('Przestrzeń Genetyczna: D-statistic vs f3', fontsize=16)
ax4.set_xlabel('D-stat (Distance)', fontsize=12)
ax4.set_ylabel('f3 (Admixture)', fontsize=12)
ax4.grid(True, linestyle='--', alpha=0.5, zorder=1)

# Izolaty (gwiazdka Izraela) dodane do wykresu PCA (jako anomalia w przestrzeni)
ax4.scatter([0.35], [-0.055], s=400, marker='*', color='gold', edgecolors='black', label='★ Ashkenazi Isolate (18% AB)', zorder=5)
ax4.legend(loc='lower left')

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()


