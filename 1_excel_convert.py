import pandas as pd
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
excel_file_name = 'retailsales.xlsx' 
excel_path = os.path.join(script_dir, excel_file_name)

all_years_data = []
print(f"Opening file: {excel_path}")
if os.path.exists(excel_path):
    try:
        
        all_sheets = pd.read_excel(excel_path, sheet_name=None, skiprows=4)
        
        for sheet_name, df_sheet in all_sheets.items():
            
            if str(sheet_name).isdigit():
                df_sheet['Data_Year'] = sheet_name
                all_years_data.append(df_sheet)
                print(f"Processed Tab: {sheet_name}")

        if all_years_data:
            master_df = pd.concat(all_years_data, ignore_index=True)
            output_path = os.path.join(script_dir, "consolidated_retail_sales_raw.csv")
            master_df.to_csv(output_path, index=False)
            print(f"\n--- Success! Combined {len(all_years_data)} tabs into: ---")
            print(output_path)
            
    except Exception as e:
        print(f"Error: {e}")
else:
    print(f"Error: Could not find '{excel_file_name}' in {script_dir}")