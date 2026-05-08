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

query = """
    SELECT Year, SUM(Sales_Millions) as Total_Sales
    FROM sales_history
    WHERE Adjustment_Status = 'Not Adjusted'
    GROUP BY Year
    ORDER BY Year
"""
df_macro = pd.read_sql(query, conn)
conn.close()

plt.figure()

sns.lineplot(x=df_macro['Year'], y=df_macro['Total_Sales'] / 1000, color='#2c3e50', marker='o')

plt.title('Macroeconomic Trend: Total U.S. Retail Sales (1992-2025)')
plt.xlabel('Year')
plt.ylabel('Total Sales (Billions of $)')

output_path = os.path.join(script_dir, 'macro_trend_1992_2025.png')
plt.savefig(output_path, dpi=300) # dpi=300 ensures it is perfectly crisp for your report
print(f"Saved Macro Trend visualization to: {output_path}")
