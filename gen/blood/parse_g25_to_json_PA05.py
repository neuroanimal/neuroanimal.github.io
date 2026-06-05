import pandas as pd
import json

# Ścieżka do Twojego pliku
g25_path = "data/Global25_PCA_modern_pop_averages_scaled.txt"

# Lista populacji, które nas interesują (możesz dopisywać kolejne)
target_pops = [
    'Polish', 'Ashkenazi_Poland', 'Ashkenazi_Germany', 'Ashkenazi_Lithuania',
    'Israel_Jewish', 'Ukrainian', 'Czech', 'Slovak', 'Lithuanian', 
    'Russian_Orel', 'German', 'Spanish', 'Italian_North', 'Greek_Central', 
    'Lebanese_Christian', 'Palestinian'
]

def parse_g25_to_json(file_path, targets):
    # Wczytujemy plik tekstowy (G25 ma przecinek na początku, więc index_col=0)
    g25_df = pd.read_csv(file_path, index_col=0)
    
    genetics_data = []
    
    # Przykładowe dane serologiczne (do uzupełnienia o prawdziwe statystyki AB)
    # W docelowej wersji te dane p_A i q_B też powinny być w osobnym CSV
    serology_defaults = {
        'Polish': {'p_A': 0.38, 'q_B': 0.19, 'Rh_neg': 0.15},
        'Ashkenazi_Poland': {'p_A': 0.35, 'q_B': 0.20, 'Rh_neg': 0.13},
        'Israel_Jewish': {'p_A': 0.34, 'q_B': 0.22, 'Rh_neg': 0.12},
        # ... itd
    }

    for pop in targets:
        if pop in g25_df.index:
            row = g25_df.loc[pop]
            # Mapujemy populację na państwo dla mapy (Geopandas potrzebuje nazw państw)
            country_map = {
                'Polish': 'Poland', 'Ukrainian': 'Ukraine', 'Czech': 'Czechia',
                'Slovak': 'Slovakia', 'Lithuanian': 'Lithuania', 'German': 'Germany',
                'Spanish': 'Spain', 'Italian_North': 'Italy', 'Greek_Central': 'Greece',
                'Israel_Jewish': 'Israel', 'Palestinian': 'Palestine'
            }
            
            # Pobieramy allele (jeśli nie ma w słowniku, dajemy średnie)
            s_data = serology_defaults.get(pop, {'p_A': 0.3, 'q_B': 0.15, 'Rh_neg': 0.10})
            
            genetics_data.append({
                "name": country_map.get(pop, pop), # Jeśli to izolat, zostaje nazwa oryginalna
                "is_isolate": "_" in pop,
                "p_A": s_data['p_A'],
                "q_B": s_data['q_B'],
                "Rh_neg": s_data['Rh_neg'],
                "D_stat": row['PC1'], # PC1 to nasza oś pozioma
                "f3_admix": row['PC2'] # PC2 to nasza oś pionowa
            })
    
    with open('data/genetics_data.json', 'w') as f:
        json.dump(genetics_data, f, indent=4)
    print("Sukces! Dane G25 wyeksportowane do genetics_data.json")

parse_g25_to_json(g25_path, target_pops)


