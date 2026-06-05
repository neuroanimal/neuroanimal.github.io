import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import geodatasets

# # 1. Załadowanie bazy geograficznej
# world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
# 1. Wczytanie mapy świata (nowy sposób dla GeoPandas 1.0+)
# url = geodatasets.get_path('naturalearth.land')
# 1. Pobieranie mapy bezpośrednio z pewnego źródła (odporne na błędy bibliotek)
url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
try:
    world = gpd.read_file(url)
except:
    url = geodatasets.get_path('naturalearth.admin_0_countries') # or naturalearth_countries ???
    world = gpd.read_file(url)

# 2. Przykładowe dane (docelowo wczytasz swój CSV)
# data = {
#     'name': ['Poland', 'Israel', 'Japan', 'Hungary', 'India'],
#     'p_A': [0.38, 0.34, 0.28, 0.36, 0.18],
#     'q_B': [0.19, 0.22, 0.17, 0.20, 0.25],
#     'Rh_neg': [0.15, 0.12, 0.005, 0.14, 0.02]
# }
# 2. Rozbudowana baza danych: Allele + Statystyki Populacyjne
# f3: ujemne wartości = silna domieszka (miks genetyczny)
# D: dystans (np. -1 = Europa Zach., +1 = Lewant/Step)
data = {
    'name': ['Poland', 'Israel', 'Japan', 'Hungary', 'India', 'Lithuania', 'Ukraine', 'Czechia'],
    'p_A': [0.38, 0.34, 0.28, 0.36, 0.18, 0.39, 0.35, 0.37],
    'q_B': [0.19, 0.22, 0.17, 0.20, 0.25, 0.16, 0.23, 0.18],
    'Rh_neg': [0.15, 0.12, 0.005, 0.14, 0.02, 0.15, 0.09, 0.15],
    'f3_admix': [-0.02, -0.05, 0.001, -0.03, -0.01, -0.015, -0.04, -0.02],
    'D_stat': [-0.2, 0.4, 0.8, -0.1, 0.6, -0.3, 0.2, -0.2]
}
df = pd.DataFrame(data)

# 3. Obliczenia fenotypów (Serogenetyka)
# Grupa AB (ogólnie) = 2 * p * q
df['AB_total'] = 2 * df['p_A'] * df['q_B']
# Grupa AB- = AB_total * Rh_neg
df['AB_minus'] = df['AB_total'] * df['Rh_neg']
# RH_add = 1 - Rh_neg
# Grupa AB+ = AB_total * Rh_add
df['AB_plus'] = df['AB_total'] * (1 - df['Rh_neg'])

# 4. Łączenie z geometrią mapy
# merged = world.merge(df, on='name', how='left')
# Uwaga: Natural Earth używa 'name' lub 'name_en'
name_col = 'NAME' if 'NAME' in world.columns else 'name' if 'name' in world.columns else 'name_en'
# merged = world.merge(df, left_on=name_col, right_on='country_name', how='left')
merged = world.merge(df, on=name_col, how='left')

# # 5. Wizualizacja
# fig, ax = plt.subplots(1, 1, figsize=(15, 10))
# merged.plot(column='AB_minus', ax=ax, legend=True, 
#             legend_kwds={'label': "Częstotliwość grupy AB-"},
#             missing_kwds={'color': 'lightgrey'}, cmap='YlOrRd')
# plt.title('Dystrybucja rzadkiego fenotypu AB- (Modele Admixture)')
# plt.show()

# 5. Generowanie zestawu map
fig, axes = plt.subplots(2, 2, figsize=(20, 12))
# fig.suptitle('Genetyka Populacyjna Grup Krwi: Allele vs f3/D Statistics', fontsize=20)
fig.suptitle('Serogenetyka Populacyjna: Allele, f3 oraz D-Statistic', fontsize=22)

# Mapa A: Fenotyp AB- (Unikat Międzymorza)
# Mapa 1: AB- (Unikat Środkowoeuropejski)
# merged.plot(column='AB_minus', ax=axes[0,0], legend=True, cmap='Purples', missing_kwds={'color': 'whitesmoke'})
merged.plot(column='AB_minus', ax=axes[0,0], legend=True, cmap='magma', missing_kwds={'color': '#f0f0f0'})
# axes[0,0].set_title('Dystrybucja AB- (Model Rh- x Allele B)')
axes[0,0].set_title('Fenotyp AB- (Rh- x Allel B)', fontsize=14)

# Mapa B: Allel B (Gradient Wschodni)
# Mapa 3: Allel B (Gradient Wschodni)
# merged.plot(column='q_B', ax=axes[0,1], legend=True, cmap='YlOrBr', missing_kwds={'color': 'whitesmoke'})
merged.plot(column='q_B', ax=axes[1,0], legend=True, cmap='YlGnBu', missing_kwds={'color': '#f0f0f0'})
# axes[0,1].set_title('Częstotliwość Allelu B (Gradient Migracji)')
axes[1,0].set_title('Częstotliwość Allelu B', fontsize=14)

# Mapa C: f3 Admixture Signal (Siła zmieszania)
# Mapa 2: f3 Admixture (Sygnał mieszania populacji)
# Im ciemniejszy, tym bardziej ujemne f3 (silniejszy miks A i B)
# Ujemne f3 (niebieskie) = silne zmieszanie
# merged.plot(column='f3_admix', ax=axes[0,1], legend=True, cmap='RdBu', missing_kwds={'color': '#f0f0f0'})
merged.plot(column='f3_admix', ax=axes[1,0], legend=True, cmap='RdBu_r', missing_kwds={'color': 'whitesmoke'})
# axes[1,0].set_title('Statystyka f3 (Sygnał Admixture Lewant-Europa)')
axes[0,1].set_title('Statystyka f3 (Admixture Level)', fontsize=14)

# Mapa D: Hot-spots (Izolaty i Grupy Etniczne)
# Tutaj ręcznie naniesiemy punkty dla izolatów (np. Aszkenazyjczycy 18%)
# merged.plot(ax=axes[1,1], color='lightgrey')
# isolates = pd.DataFrame({
#     'name': ['Ashkenazi_Isolate', 'Samaritans'],
#     'lat': [52.2, 32.2], 'lon': [21.0, 35.2], 'AB_val': [18, 20]
# })
# plt.scatter(isolates.lon, isolates.lat, s=isolates.AB_val*10, color='red', alpha=0.7, label='Izolaty (AB %)')
# axes[1,1].set_title('Izolaty Etniczne i Punkty Przełomowe')
# Mapa 4: Wykres PCA (D-stat vs f3) - tu wizualizujemy te Twoje linie v i w
axes[1,1].set_facecolor('#f9f9f9')
scatter = axes[1,1].scatter(df['D_stat'], df['f3_admix'], s=df['AB_total']*1000, 
                            c=df['AB_total'], cmap='viridis', edgecolors='black', alpha=0.8)
for i, txt in enumerate(df[name_col]):
    axes[1,1].annotate(txt, (df['D_stat'][i], df['f3_admix'][i]), xytext=(5,5), textcoords='offset points')

# Dodanie "linii gradientu" (Clines), o których wspominałeś (v i w)
axes[1,1].plot([-0.5, 1.0], [0, -0.06], '--', color='red', alpha=0.6, label='European-Levant Cline')
axes[1,1].set_title('Przestrzeń Genetyczna: D-statistic vs f3', fontsize=14)
axes[1,1].set_xlabel('D-stat (Distance)')
axes[1,1].set_ylabel('f3 (Admixture)')
axes[1,1].legend()

# Dodanie adnotacji dla izolatów (np. te 18%)
# Koordynaty dla Izraela: 34.8, 31.0
plt.text(34.8, 31.0, '★ Isolate 18%', color='gold', fontweight='bold')
plt.title('Dystrybucja AB- oraz punkty ekstremalne (f3/D Analysis)')
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()


