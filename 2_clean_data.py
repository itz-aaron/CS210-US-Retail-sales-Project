import pandas as pd
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
raw_csv_path = os.path.join(script_dir, "consolidated_retail_sales_raw.csv")
clean_csv_path = os.path.join(script_dir, "cleaned_retail_sales.csv")


if os.path.exists(raw_csv_path):
    df = pd.read_csv(raw_csv_path, low_memory=False)

    df.rename(columns={'Unnamed: 0': 'NAICS_Code', 'Unnamed: 1': 'Category'}, inplace=True)
    df['Adjustment_Status'] = pd.NA
    df.loc[df['Category'].astype(str).str.contains("NOT ADJUSTED", case=False), 'Adjustment_Status'] = 'Not Adjusted'
    df.loc[df['Category'].astype(str).str.contains("ADJUSTED", case=False) & 
           ~df['Category'].astype(str).str.contains("NOT", case=False), 'Adjustment_Status'] = 'Adjusted'

    df['Adjustment_Status'] = df['Adjustment_Status'].ffill()

    df = df[df['Category'].notna()]
    df = df[~df['Category'].astype(str).str.contains("ADJUSTED", case=False)]
    df = df[~df['NAICS_Code'].astype(str).str.contains("NAICS", case=False)]

    cols_to_drop = [col for col in df.columns if 'Unnamed' in col or 'CUM' in col or 'TOTAL' in col]
    df.drop(columns=cols_to_drop, inplace=True, errors='ignore')
    
    df_long = df.melt(
        id_vars=['NAICS_Code', 'Category', 'Data_Year', 'Adjustment_Status'], 
        var_name='Month_Year', 
        value_name='Sales_Millions'
    )

    df_long['Month'] = df_long['Month_Year'].astype(str).str[:3]
    df_long.rename(columns={'Data_Year': 'Year'}, inplace=True)

    df_long['Sales_Millions'] = df_long['Sales_Millions'].astype(str).str.replace(',', '')

    df_long['Sales_Millions'] = pd.to_numeric(df_long['Sales_Millions'], errors='coerce')

    df_long.dropna(subset=['Sales_Millions'], inplace=True)

    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    df_long['Month_Num'] = df_long['Month'].map(month_map)
    df_long.sort_values(by=['Year', 'Month_Num', 'NAICS_Code', 'Adjustment_Status'], inplace=True)

    final_columns = ['NAICS_Code', 'Category', 'Year', 'Month', 'Sales_Millions', 'Adjustment_Status']
    df_final = df_long[final_columns].copy()

    df_final.to_csv(clean_csv_path, index=False)

    print(f"Total valid rows ready for Database: {len(df_final)}")
else:
    print("Error: Could not find consolidated_retail_sales_raw.csv")