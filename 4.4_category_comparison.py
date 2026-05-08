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

print("\n--- Top 10 Category Box Plot Generator ---")
target_year = input("Enter the Year to analyze (e.g., 2024): ").strip()

# 1. Find the NAICS Codes of the Top 10 largest categories (Filtering out 'nan' and Nulls)
top_10_query = f"""
    SELECT NAICS_Code, SUM(Sales_Millions) as Total_Sales
    FROM sales_history
    WHERE Year = {target_year}
    AND Adjustment_Status = 'Not Adjusted'
    AND Category NOT LIKE '%total%'
    AND Category NOT LIKE '%GAFO%'
    AND NAICS_Code IS NOT NULL 
    AND NAICS_Code != 'nan'
    GROUP BY NAICS_Code
    ORDER BY Total_Sales DESC
    LIMIT 10
"""
top_10_df = pd.read_sql(top_10_query, conn)

if top_10_df.empty:
    print(f"No data found for the year {target_year}. Exiting.")
    conn.close()
    exit()

# 2. Force every single item into a string, stripping decimals
raw_naics_list = top_10_df['NAICS_Code'].tolist()
top_10_naics = [str(code).replace('.0', '') for code in raw_naics_list]

# 3. Format those codes so SQL can read them
naics_str = "('" + "', '".join(top_10_naics) + "')"

# 4. Query the individual monthly sales data for JUST those clean Top 10 NAICS codes
query = f"""
    SELECT NAICS_Code, Sales_Millions
    FROM sales_history
    WHERE Year = {target_year}
    AND Adjustment_Status = 'Not Adjusted'
    AND NAICS_Code IN {naics_str}
"""
df_box = pd.read_sql(query, conn)
conn.close()

# Convert to Billions for a much cleaner Y-axis
df_box['Sales_Billions'] = df_box['Sales_Millions'] / 1000

# Match the clean string format so Seaborn maps the boxes correctly
df_box['NAICS_Code'] = [str(code).replace('.0', '') for code in df_box['NAICS_Code'].tolist()]

# 5. Generate the Vertical Box Plot
plt.figure(figsize=(16, 9)) 

sns.boxplot(
    data=df_box, 
    x='NAICS_Code', 
    y='Sales_Billions', 
    palette='viridis',
    order=top_10_naics, # Keeps the boxes sorted from biggest to smallest
    showfliers=True, 
    fliersize=8, 
    linewidth=2
)

# X-axis labels straight and bold
plt.xticks(rotation=0, fontsize=12, weight='bold')

plt.title(f'Monthly Sales Distribution of Top 10 Retail NAICS Sectors ({target_year})', pad=20, fontsize=18)
plt.ylabel('Monthly Sales (Billions of $)', fontsize=14)
plt.xlabel('NAICS Industry Code', fontsize=14, labelpad=15)

# Add a subtle background grid 
plt.grid(axis='y', linestyle='--', alpha=0.7)

output_path = os.path.join(script_dir, f'top_10_categories_boxplot_{target_year}.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n--- Success! Saved pristine Box Plot to: {output_path} ---")