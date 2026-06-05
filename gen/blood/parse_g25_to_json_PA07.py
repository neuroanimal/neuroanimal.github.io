import pandas as pd
import json


def update_genetics_full(g25_path):
    g25_df = pd.read_csv(g25_path, index_col=0)
    
    # Rozszerzona mapa nazw (Klucz w G25 : Nazwa w GeoJSON)
    mapping = {
        'Polish': 'Poland', 'Ukrainian': 'Ukraine', 'Slovak': 'Slovakia',
        'Czech': 'Czechia', 'Lithuanian': 'Lithuania', 'Latvian': 'Latvia',
        'Estonian': 'Estonia', 'Belarusian': 'Belarus', 'Russian_Orel': 'Russia',
        'Hungarian': 'Hungary', 'German': 'Germany', 'Israel_Jewish': 'Israel',
        'Palestinian': 'Palestine', 'Lebanese_Christian': 'Lebanon', 'Greek_Central': 'Greece'
    }

    genetics_data = []
    for pop_name in g25_df.index:
        # Pobieramy kraje z mapy LUB wszystkie Ashkenazi
        is_ashkenazi = "Ashkenazi" in pop_name
        is_country = pop_name in mapping
        
        if is_country or is_ashkenazi:
            row = g25_df.loc[pop_name]
            name = mapping.get(pop_name, pop_name)
            
            # Prosta heurystyka dla q_B (Allel B jest wyższy na Wschodzie)
            q_B = 0.22 if is_ashkenazi else 0.18
            if "Lithuanian" in pop_name or "Estonian" in pop_name: q_B = 0.14
            
            genetics_data.append({
                "name": name,
                "is_isolate": is_ashkenazi,
                "p_A": 0.35, "q_B": q_B, "Rh_neg": 0.14,
                "D_stat": float(row['PC1']), 
                "f3_admix": float(row['PC2'])
            })
    
    with open('data/genetics_data.json', 'w') as f:
        json.dump(genetics_data, f, indent=4)

update_genetics_full("data/Global25_PCA_modern_pop_averages_scaled.txt")


