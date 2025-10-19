import numpy as np
import pandas as pd

from IPython.display import display as ipython_display

import warnings


warnings.filterwarnings(
    action='ignore', category=UserWarning, message=r"Boolean Series.*"
)

df_yr_1917_cpi = pd.read_table("data/gus/gus_inflation_cpi_by_year_since_1917.tsv")
df_yr_2013_hicp = pd.read_table("data/gus/eurostat_inflation_hicp_by_year_since_2013.tsv")
df_mo_1982_cpi = pd.read_csv("data/gus/gus_inflation_cpi_by_month_since_1982.csv", sep=';', encoding='cp1250')  # not iso-8859-2 = latin2, but Windows-1250 = cp1250
df_yr_1950_cpi = pd.read_csv("data/gus/gus_inflation_cpi_by_year_since_1950.csv", sep=';', encoding='cp1250')   # not iso-8859-2 = latin2, but Windows-1250 = cp1250

df_yr_1917_cpi = df_yr_1917_cpi[['year', 'cpi']]     # filter out rest of columns
df_yr_1950_cpi = df_yr_1950_cpi[['Rok', 'Wartość']]  # filter out rest of columns
df_mo_1982_cpi = df_mo_1982_cpi[['Rok', 'Wartość', 'Miesiąc', 'Sposób prezentacji']]  # filter out rest of columns
df_yr_2013_hicp = df_yr_2013_hicp.rename(str.strip, axis = 'columns')  # strip whitespaces in column names
df_yr_2013_hicp = df_yr_2013_hicp.loc[df_yr_2013_hicp['freq,unit,coicop,geo'] == 'A,RCH_A_AVG,CP00,PL']  # filter out rest of rows

df_yr_1917_cpi.reset_index(inplace=True)
df_yr_1950_cpi.reset_index(inplace=True)
df_mo_1982_cpi.reset_index(inplace=True)
df_yr_2013_hicp.reset_index(inplace=True)

# ipython_display(df_yr_1917_cpi)
# ipython_display(df_yr_1950_cpi)
# ipython_display(df_mo_1982_cpi)
# ipython_display(df_yr_2013_hicp)
# print(list(df_yr_2013_hicp.columns.values))

# Sposób prezentacji:
#   Grudzień poprzedniego roku = 100
#   Poprzedni miesiąc = 100
#   Analogiczny miesiąc poprzedniego roku = 100
#   Analogiczny okres narastający poprzedniego roku = 100
#   Rok poprzedni = 100

df = pd.DataFrame(columns=["date", "hicp_avg_eurostat", "cpi_avg_wiki", "cpi_avg_gus", "cpi_mo2Dec_gus", "cpi_mo2mo_gus", "cpi_mo2moyr_gus", "cpi_mo2momo_gus", "cpi_mo2yr_gus"])
idx = 0
for year in range(1917, 2026):
    for month in range(1, 13):
        period = pd.Period(f"{year}/{month}", freq='M')
        dti = pd.date_range(start=period.start_time, end=period.end_time, freq='D')
        for day in dti:
            if day > pd.Timestamp(2025,9,30):
                break
            df.at[idx, 'date'] = day
            if year >= 2013 and year <= 2024:
                df.at[idx, 'hicp_avg_eurostat'] = 100 + float(df_yr_2013_hicp[str(year)].iloc[0])
            if year >= 1917 and year <= 2024:
                df.at[idx, 'cpi_avg_wiki'] = float(df_yr_1917_cpi[df_yr_1917_cpi['year'] == year]['cpi'].iloc[0])
            if year >= 1950 and year <= 2024:
                df.at[idx, 'cpi_avg_gus'] = float(df_yr_1950_cpi[df_yr_1950_cpi['Rok'] == year]['Wartość'].iloc[0].replace(',', '.'))
            if year >= 1982 and year <= 2025:

                tmp = df_mo_1982_cpi[df_mo_1982_cpi['Rok'] == year][df_mo_1982_cpi['Miesiąc'] == month][df_mo_1982_cpi['Sposób prezentacji'] == "Grudzień poprzedniego roku = 100"]['Wartość']
                if not tmp.empty:
                    df.at[idx, 'cpi_mo2Dec_gus'] = float(tmp.iloc[0].replace(',', '.'))

                df.at[idx, 'cpi_mo2mo_gus'] = float(df_mo_1982_cpi[df_mo_1982_cpi['Rok'] == year][df_mo_1982_cpi['Miesiąc'] == month][df_mo_1982_cpi['Sposób prezentacji'] == "Poprzedni miesiąc = 100"]['Wartość'].iloc[0].replace(',', '.'))

                df.at[idx, 'cpi_mo2moyr_gus'] = float(df_mo_1982_cpi[df_mo_1982_cpi['Rok'] == year][df_mo_1982_cpi['Miesiąc'] == month][df_mo_1982_cpi['Sposób prezentacji'] == "Analogiczny miesiąc poprzedniego roku = 100"]['Wartość'].iloc[0].replace(',', '.'))

                tmp = df_mo_1982_cpi[df_mo_1982_cpi['Rok'] == year][df_mo_1982_cpi['Miesiąc'] == month][df_mo_1982_cpi['Sposób prezentacji'] == "Analogiczny okres narastający poprzedniego roku = 100"]['Wartość']
                if not tmp.empty:
                    df.at[idx, 'cpi_mo2momo_gus'] = float(tmp.iloc[0].replace(',', '.'))

                tmp = df_mo_1982_cpi[df_mo_1982_cpi['Rok'] == year][df_mo_1982_cpi['Miesiąc'] == month][df_mo_1982_cpi['Sposób prezentacji'] == "Rok poprzedni = 100"]['Wartość']
                if not tmp.empty:
                    df.at[idx, 'cpi_mo2yr_gus'] = float(tmp.iloc[0].replace(',', '.'))

            idx += 1

# ipython_display(df)
df.to_csv("data/gus/all.csv", date_format="%Y-%m-%d")

