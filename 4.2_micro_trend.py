import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import chart_style

chart_style.apply_report_style()

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "retail_data.db")
conn = sqlite3.connect(db_path)

print("\nRetail Micro-Trend Explorer: ")
target_naics = input("Enter a NAICS code to visualize (e.g., 441, 442, 4451): ").strip()

query = f"""
    SELECT Category, Year, SUM(Sales_Millions) as Total_Sales
    FROM sales_history
    WHERE NAICS_Code = '{target_naics}' AND Adjustment_Status = 'Not Adjusted'
    GROUP BY Year, Category
    ORDER BY Year
"""
df_micro = pd.read_sql(query, conn)
conn.close()

if df_micro.empty:
    print(f"Error: No data found for NAICS code {target_naics}. Check your code and try again.")
else:
    category_name = df_micro['Category'].iloc[0]

    plt.figure()
    sns.lineplot(x=df_micro['Year'], y=df_micro['Total_Sales'], color='#e74c3c', marker='s')
    
    plt.title(f'Micro-Trend: {category_name} ({target_naics})')
    plt.xlabel('Year')
    plt.ylabel('Annual Sales (Millions of $)')

    output_path = os.path.join(script_dir, f'micro_trend_{target_naics}.png')
    plt.savefig(output_path, dpi=300)
    print(f"Saved specific industry visualization to: {output_path}")
