import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import chart_style

# 1. Apply the professional styling
chart_style.apply_report_style()

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "retail_data.db")

print("\n--- Interactive Seasonality Heatmap Generator ---")
start_year = int(input("Enter the Start Year (e.g., 2010): ").strip())
end_year = int(input("Enter the End Year (e.g., 2024): ").strip())

print("\nChoose Map Type:")
print("1: Total Retail Sales")
print("2: Individual Sector")
map_choice = input("Enter 1 or 2: ").strip()

conn = sqlite3.connect(db_path)

# 2. Dynamically build the SQL query based on user input
if map_choice == '1':
    title_prefix = "Total U.S. Retail Sales"
    query = f"""
        SELECT Year, Month, SUM(Sales_Millions) as Total_Sales
        FROM sales_history
        WHERE Adjustment_Status = 'Not Adjusted'
        AND Year BETWEEN {start_year} AND {end_year}
        GROUP BY Year, Month
    """
elif map_choice == '2':
    naics_code = input("Enter the NAICS code for the sector (e.g., 441): ").strip()
    
    # Grab the category name so we can put it in the chart title
    cat_query = f"SELECT Category FROM sales_history WHERE NAICS_Code = '{naics_code}' LIMIT 1"
    cat_result = pd.read_sql(cat_query, conn)
    
    if cat_result.empty:
        print("Invalid NAICS code. Exiting.")
        conn.close()
        exit()
        
    cat_name = cat_result.iloc[0]['Category']
    title_prefix = f"{cat_name} ({naics_code})"

    query = f"""
        SELECT Year, Month, SUM(Sales_Millions) as Total_Sales
        FROM sales_history
        WHERE Adjustment_Status = 'Not Adjusted'
        AND NAICS_Code = '{naics_code}'
        AND Year BETWEEN {start_year} AND {end_year}
        GROUP BY Year, Month
    """
else:
    print("Invalid choice. Please run again and enter 1 or 2.")
    conn.close()
    exit()

df_heat = pd.read_sql(query, conn)
conn.close()

if df_heat.empty:
    print("No data found for those parameters.")
    exit()

# 3. Force chronological month sorting
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
df_heat['Month'] = pd.Categorical(df_heat['Month'], categories=month_order, ordered=True)

# 4. Pivot the data into a grid format
heatmap_data = df_heat.pivot(index='Year', columns='Month', values='Total_Sales')
heatmap_data.sort_index(inplace=True)

# 5. Generate the Heatmap
plt.figure(figsize=(12, 9)) # Made it slightly taller to accommodate the bottom legend

# 'YlOrRd' is Yellow-to-Red. 
# cbar_kws pushes the legend to the bottom and stretches it horizontally.
ax = sns.heatmap(
    heatmap_data / 1000, 
    cmap='YlOrRd', 
    annot=False, 
    linewidths=.5,
    cbar_kws={"orientation": "horizontal", "pad": 0.12, "label": "Sales (Billions of $)"}
)

# Invert the Y-axis so the oldest year is at the bottom
ax.invert_yaxis()

plt.title(f'Seasonality Heatmap: {title_prefix}\n({start_year} - {end_year})', pad=20)
plt.xlabel('Month', labelpad=15)
plt.ylabel('Year', labelpad=15)

output_path = os.path.join(script_dir, f'seasonality_heatmap_{start_year}_{end_year}.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight') 
print(f"\n--- Success! Saved Custom Heatmap to: {output_path} ---")