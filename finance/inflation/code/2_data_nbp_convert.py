# from openpyxl import load_workbook
import numpy as np
import pandas as pd

from IPython.display import display as ipython_display

import warnings


warnings.filterwarnings(
    action='ignore', category=UserWarning, message=r"Boolean Series.*"
)


excel_dir_path = "data/nbp"
excel_file_prefix = "archiwum_tab_a_"
excel_file_suffix = ".xls"

dfz = pd.DataFrame(columns=["date", "value"])


def div_high_curr(val):
    #  autofix currency value: if higher than 10000 div by 10000
    #  autofix currency value: if higher than 100 div by 100
    if isinstance(val, int):
        if val >= 10000:
            return float(val / 10000.0)
        elif val >= 100:
            return float(val / 100.0)
        else:
            return val
    elif isinstance(val, float):
        if val >= 10000.0:
            return float(val / 10000.0)
        elif val >= 100.0:
            return float(val / 100.0)
        else:
            return val
    elif isinstance(val, str):
        print(f"WARNING! I want to skip string value of currency: ({val.__class__.__name__}) '{val}'")
        # return None
        return val
        # return np.nan
    else:
        # unknown type?
        print(f"FATAL ERROR! Unknown data type: {val.__class__.__name__} {val}")
        exit(100)
        return val


def mux_low_curr(val):
    if isinstance(val, int):
        if val < 50:
            return int(val * 10000)
        elif val < 50000:
            return int(val * 100)
        else:
            return val
    elif isinstance(val, float):
        if val < 50.0:
            return int(round(val * 10000))
        elif val < 50000.0:
            return int(round(val * 100))
        else:
            return val
    elif isinstance(val, str):
        print(f"WARNING! I want to skip string value of currency: ({val.__class__.__name__}) '{val}'")
        # return None
        return val
        # return np.nan
    else:
        # unknown type?
        print(f"FATAL ERROR! Unknown data type: {val.__class__.__name__} {val}")
        exit(100)
        return val


year_min = 1984  # 1988  # 1984
year_max = 2026  # 1992  # 2026

for year in range(year_min, year_max):
    excel_file_name = f"{excel_file_prefix}{year}{excel_file_suffix}"
    excel_file_path = f"{excel_dir_path}/{excel_file_name}"
    print(f"Processing {excel_file_path}")
    df = pd.read_excel(excel_file_path, sheet_name=None, header=None)  # , header=[0, 1])
    sheet_names = list(df.keys())
    for sheet_name in sheet_names:
        dfn = df[sheet_name]
        if dfn.empty:
            continue
        dfn = dfn.dropna(how='all').dropna(how='all', axis=1)
        dfn.reset_index(inplace=True)
        i = 0
        headers = dfn.iloc[i]
        while pd.isna(headers[i]):
            i += 1
            headers = dfn.iloc[i]
        headers = list(headers)
        # print(f"Columns in worksheet {sheet_name}: {headers}")
        dfn = pd.DataFrame(dfn.values[i + 1:], columns=headers)
        num_rows, num_cols = dfn.shape
        size_rows_cols = dfn.size
        if size_rows_cols < 1:
            continue
        cols = dfn.columns
        cols_lst = cols.values.tolist()
        if len(cols_lst) < 1:
            continue
        ### print(f"{excel_file_name}\t{sheet_name}\t{num_cols} x {num_rows} = {size_rows_cols}\t{cols_lst}")
        # find index and name of column with data/date/Data/Date
        # find index and name of column with USA/1 USD/100 USD
        col_idx_date = None
        col_nam_date = None
        col_idx_curr = None
        col_nam_curr = None
        col_idx = 0
        for col_nam in cols_lst:
            col_name = str(col_nam)
            if col_nam == year or col_name == str(year) or "data" in col_name.lower() or "date" in col_name.lower() or "KURS" in col_name:
                col_idx_date = col_idx
                col_nam_date = col_nam
            elif "USD" in col_name.upper() or "USA" in col_name.upper() or "dolar ameryka" in col_name.lower():
                col_idx_curr = col_idx
                col_nam_curr = col_nam
            col_idx += 1
        if col_nam_date is None:
            print("Cannot find column with date.")
            exit(-1)
        elif col_nam_curr is None:
            print("Cannot find column with currency: dollar.")
            exit(-2)
        date = dfn[col_nam_date]  # 'data' or 'Data' or unnamed?
        curr = dfn[col_nam_curr]  # dfn['1 USD' if '1 USD' in cols_lst else 'USA']
        # tabi = dfn[cols_lst[-2]]  # normal tab index
        # tabj = dfn[cols_lst[-1]]  # extended tab index
        ## print(f"Column index of date found: {col_nam_date}")
        ## print("Date dataframe read:")
        ## ipython_display(date)

        ## print("\n\nTry1\n")
        ## ipython_display(dfn)

        # curr = curr.apply(div_high_curr)

        ### dfn = dfn[curr.notnull().notna()][curr != '1 dolar'][curr.apply(div_high_curr)]  #  autofix currency value
        dfn = dfn[date.notnull().notna()][date != 'data'][date != "Nr"][date != 'kod ISO'][date != 'nazwa waluty'][date != 'liczba jednostek']
        dfn = dfn[date.notnull().notna()][date.apply(lambda ccc: not pd.isnull(ccc) and (not isinstance(ccc, str) or "korekta" not in ccc.lower()))]
        dfn = dfn[date.notnull().notna()][date.apply(lambda ccc: not pd.isnull(ccc) and (not isinstance(ccc, str) or "tabela" not in ccc.lower()))]
        dfn = dfn[date.notnull().notna()][date.apply(lambda ccc: not pd.isnull(ccc) and (not isinstance(ccc, str) or not ccc.lstrip().startswith("*")))]
        ### dfn = dfn[date.notnull().notna()][curr.apply(div_high_curr)]  #  autofix currency value
        dfn = dfn[curr.notnull().notna()]  # [curr.str.contains("korekta") == False]
        dfn.reset_index(inplace=True)

        ## print("\n\nTry5\n")
        ## ipython_display(dfn)

        date = dfn[col_nam_date]
        curr = dfn[col_nam_curr]
        datel = len(date)
        currl = len(curr)
        if datel != currl:
            print(f"Misaligned number of date entries ({datel}) comparing to currency entries ({currl})")
            exit(-3)
        ### print(f"Dates found: ({date.__class__.__name__}) {date} : {date.dtype}")
        date = date.astype('datetime64[ns]')
        for single_date in date:
            if single_date < pd.to_datetime('1984-01-01'):
                print(f"FATAL ERROR! Date '{single_date}' is too old. Expected date >= 1984-01-01.")
                exit(1)
        ### print(f"Dates converted: ({date.__class__.__name__}) {date} : {date.dtype}")
        data = {
            "date": date,
            "value": curr
        }
        # print(data)
        dfx = pd.DataFrame(data)
        dfx.reset_index(inplace=True)
        ### dfz.reset_index(inplace=True)
        # dfx = pd.concat([date, curr], keys=['date', 'value'])
        ### ipython_display(dfx)
        # dfz = pd.concat([dfz, dfx])
        df_list = [dfz, dfx]
        dfz = pd.concat([df for df in df_list if not df.empty])
        ### dfz.reset_index(inplace=True)

dfz = dfz.drop_duplicates().reset_index(drop=True)
dfz['value2'] = np.where(not isinstance(dfz['value'], str), dfz['value'].apply(mux_low_curr), dfz['value'])
denomination_day = pd.to_datetime("1995-01-01")
dfz['value3'] = np.where(dfz['date'] >= denomination_day, dfz['value2'].apply(lambda vvv: 100 * vvv), dfz['value2'])
dfz['USD_PLN'] = dfz['value3'].apply(lambda vvv: float(vvv / 1000000))
ipython_display(dfz)

dfz.reset_index(inplace=True)
dfz.to_csv("data/nbp/all.csv", date_format="%Y-%m-%d")

import matplotlib.pyplot as plt

plt.figure(figsize=(12,6))
plt.plot(dfz.index, dfz['USD_PLN'], label="USD/PLN", alpha=0.7)
plt.legend()
plt.title("Kurs USD/PLN od 1984 do 2025")
plt.show()


