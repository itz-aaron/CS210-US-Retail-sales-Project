import pandas as pd
import sqlite3
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "cleaned_retail_sales.csv")
db_path = os.path.join(script_dir, "retail_data.db")

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    
    conn = sqlite3.connect(db_path)

    df.to_sql('sales_history', conn, if_exists='replace', index=False)

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales_history")
    row_count = cursor.fetchone()[0]

    print("\nDatabase Schema Preview:")
    cursor.execute("PRAGMA table_info(sales_history)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
        
    conn.close()
    
else:
    print("Error")