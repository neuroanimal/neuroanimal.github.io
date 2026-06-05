import pandas as pd
import json

def update_genetics_from_g25(g25_path):
    g25_df = pd.read_csv(g25_path, index_col=0)
    
    # Kraje bazowe
    country_map = {
        'Polish': 'Poland', 'Ukrainian': 'Ukraine', 'Czech': 'Czechia',
        'Slovak': 'Slovakia', 'Lithuanian': 'Lithuania', 'German': 'Germany',
        'Spanish': 'Spain', 'Italian_North': 'Italy', 'Greek_Central': 'Greece',
        'Israel_Jewish': 'Israel', 'Palestinian': 'Palestine', 'Russian_Orel': 'Russia'
    }

    genetics_data = []

    # Przeszukujemy wszystkie populacje w G25
    for pop_name in g25_df.index:
        is_target = pop_name in country_map.keys()
        is_ashkenazi = "Ashkenazi" in pop_name

        if is_target or is_ashkenazi:
            row = g25_df.loc[pop_name]
            
            # Przypisanie alleli: 
            # Jeśli Ashkenazi - wyższe q_B (ok 0.20), jeśli Europa - wg klucza
            p_A, q_B, rh = 0.35, 0.15, 0.15 # Default
            if is_ashkenazi:
                p_A, q_B, rh = 0.34, 0.20, 0.13
            elif "Polish" in pop_name:
                p_A, q_B, rh = 0.38, 0.19, 0.15
            elif "Israel" in pop_name:
                p_A, q_B, rh = 0.34, 0.22, 0.12

            genetics_data.append({
                "name": country_map.get(pop_name, pop_name),
                "is_isolate": is_ashkenazi,
                "p_A": p_A, "q_B": q_B, "Rh_neg": rh,
                "D_stat": float(row['PC1']), 
                "f3_admix": float(row['PC2'])
            })

    with open('data/genetics_data.json', 'w') as f:
        json.dump(genetics_data, f, indent=4)

update_genetics_from_g25("data/Global25_PCA_modern_pop_averages_scaled.txt")

