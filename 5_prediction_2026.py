import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "retail_data.db")
conn = sqlite3.connect(db_path)

query = """
    SELECT NAICS_Code, Category, Year, SUM(Sales_Millions) as Sales
    FROM sales_history
    WHERE Adjustment_Status = 'Not Adjusted'
    AND Year BETWEEN 2015 AND 2025
    GROUP BY Year, NAICS_Code
"""
df = pd.read_sql(query, conn)
conn.close()

df['NAICS_Code'] = df['NAICS_Code'].astype(str).str.replace('.0', '', regex=False)
df = df[df['NAICS_Code'].str.len() == 3].copy()
df['Sales_Billions'] = df['Sales'] / 1000

forecast_rows = []
unique_codes = df['NAICS_Code'].unique()

for code in unique_codes:
    sector_df = df[df['NAICS_Code'] == code].sort_values('Year')
    if len(sector_df) < 5: continue

    X = sector_df[['Year']]
    y = sector_df['Sales_Billions']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)

    accuracy = r2_score(y_test, model.predict(X_test))
    pred_2026 = model.predict([[2026]])[0]
    
    forecast_rows.append({
        'Year': 2026, 'NAICS_Code': code, 'Category': sector_df['Category'].iloc[0],
        'Sales_Billions': round(pred_2026, 2), 'R2_Score': round(accuracy, 4), 'Data_Type': 'Predicted'
    })

df['Data_Type'] = 'Actual'
df['R2_Score'] = None 
final_export = pd.concat([df[['Year', 'NAICS_Code', 'Category', 'Sales_Billions', 'R2_Score', 'Data_Type']], pd.DataFrame(forecast_rows)])
final_export.to_csv(os.path.join(script_dir, "full_forecast_data.csv"), index=False)
print("Engine Complete using 2015-2025 training window.")
