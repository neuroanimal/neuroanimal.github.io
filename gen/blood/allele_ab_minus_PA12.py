import pandas as pd
import matplotlib.pyplot as plt
import json
import os

# 1. Wczytanie danych
with open('data/genetics_data.json', 'r') as f:
    df = pd.DataFrame(json.load(f))

# 2. Ręczne uśrednienie dla krajów, żeby nie było bałaganu
# Mapujemy nazwy z G25 na proste nazwy krajów
mapping = {
    'Polish': 'Poland', 'Czech': 'Czechia', 'Slovakian': 'Slovakia',
    'Russian_Orel': 'Russia', 'Russian_Kursk': 'Russia', 'Russian_Voronez': 'Russia',
    'Ashkenazi_Poland': 'Poland', 'Ashkenazi_Russia': 'Russia'
}
df['country'] = df['name'].apply(lambda x: mapping.get(x, x))
df_avg = df.groupby('country').mean(numeric_only=True).reset_index()

# 3. Zamiast wczytywać mapę, która wywala błąd, zróbmy wykres bąbelkowy 
# na układzie współrzędnych, który udaje mapę (D_stat i f3_admix)
# To zadziała ZAWSZE, bo nie zależy od zewnętrznych plików.

fig, ax = plt.subplots(figsize=(14, 10))

# Rysujemy kropki
scatter = ax.scatter(
    df['D_stat'] * 100, 
    df['f3_admix'] * -100,
    s=df['AB_total'] * 5000, 
    c=df['q_B'], 
    cmap='YlOrRd', 
    edgecolors='black', 
    alpha=0.7
)

# Dodajemy nazwy
for i, txt in enumerate(df['name']):
    ax.annotate(txt, (df['D_stat'].iloc[i]*100, df['f3_admix'].iloc[i]*-100), fontsize=8)

plt.colorbar(scatter, label='Częstość Allelu B')
ax.set_title("Relacje genetyczne i Allel B (Bez zewnętrznej mapy)", fontsize=16)
ax.set_xlabel("D-stat (PC1)")
ax.set_ylabel("f3-signal (PC2)")
ax.grid(True, linestyle=':', alpha=0.6)

plt.show()


