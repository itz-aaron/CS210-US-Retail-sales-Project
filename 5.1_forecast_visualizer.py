import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "retail_data.db")

def load_clean_data():
    conn = sqlite3.connect(db_path)
    query = "SELECT Year, NAICS_Code, Category, SUM(Sales_Millions) as Sales FROM sales_history WHERE Adjustment_Status = 'Not Adjusted' AND Year BETWEEN 2015 AND 2025 GROUP BY Year, NAICS_Code"
    df = pd.read_sql(query, conn)
    conn.close()
    df['NAICS_Code'] = df['NAICS_Code'].astype(str).str.replace('.0', '', regex=False)
    df = df[df['NAICS_Code'].str.len() == 3].copy()
    df['Sales_Billions'] = df['Sales'] / 1000
    return df

df = load_clean_data()
available_codes = df['NAICS_Code'].unique().tolist()
target_code = input(f"Enter code ({', '.join(available_codes)}): ").strip()

sector_df = df[df['NAICS_Code'] == target_code].sort_values('Year')
model = LinearRegression().fit(sector_df[['Year']], sector_df['Sales_Billions'])
pred_2026 = model.predict([[2026]])[0]

plt.figure(figsize=(10, 6))
plt.plot(sector_df['Year'], sector_df['Sales_Billions'], marker='o', color='#2c3e50', label='Actual Sales (2015-2025)', linewidth=2)

plt.plot([2025, 2026], [sector_df['Sales_Billions'].iloc[-1], pred_2026], linestyle='--', color='#e74c3c', linewidth=2)
plt.plot(2026, pred_2026, marker='*', markersize=15, color='#e74c3c', label='2026 Forecast')

plt.title(f"Retail Forecast: {sector_df['Category'].iloc[0]}\n(Focusing on 2015-2025 Trend)", fontsize=14, fontweight='bold')
plt.ylabel("Annual Sales (Billions $)")
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()

plt.annotate(f'Projected 2026:\n${pred_2026:.2f}B', xy=(2026, pred_2026), xytext=(2022, pred_2026),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1),
             bbox=dict(boxstyle="round", fc="white", ec="gray"))

plt.show()
