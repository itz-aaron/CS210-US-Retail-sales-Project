import sqlite3
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import os

# 1. Data Processing Logic
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "retail_data.db")

def load_growth_data():
    conn = sqlite3.connect(db_path)
    # Pulling only 'Not Adjusted' data
    query = "SELECT NAICS_Code, Category, Year, Sales_Millions FROM sales_history WHERE Adjustment_Status = 'Not Adjusted'"
    raw_df = pd.read_sql(query, conn)
    conn.close()

    # Filter: Keep only 3-digit NAICS codes (to avoid hierarchical double-counting)
    raw_df['NAICS_Code'] = raw_df['NAICS_Code'].astype(str).str.replace('.0', '', regex=False)
    df_3digit = raw_df[raw_df['NAICS_Code'].str.len() == 3].copy()

    # Step 1: Aggregate monthly data to Annual totals
    annual_df = df_3digit.groupby(['Year', 'NAICS_Code', 'Category'])['Sales_Millions'].sum().reset_index()
    annual_df.rename(columns={'Sales_Millions': 'Annual_Sales'}, inplace=True)
    annual_df = annual_df.sort_values(['NAICS_Code', 'Year'])

    # Step 2: Calculate Growth Rate per Category ((Final - Initial) / Initial) * 100
    annual_df['Growth_Rate'] = annual_df.groupby('NAICS_Code')['Annual_Sales'].pct_change() * 100

    # Step 3: Calculate Total Market Growth (Aggregate of all 3-digit sectors)
    total_market = annual_df.groupby('Year')['Annual_Sales'].sum().reset_index()
    total_market['Growth_Rate'] = total_market['Annual_Sales'].pct_change() * 100
    total_market['NAICS_Code'] = 'TOTAL'
    total_market['Category'] = 'Total US Retail Market'
    
    # Combine individual sectors with the Total Market baseline
    return pd.concat([annual_df, total_market], ignore_index=True)

df = load_growth_data()
# Get unique list of sectors for the dropdown (excluding the Total baseline)
sectors = df[df['NAICS_Code'] != 'TOTAL'][['Category', 'NAICS_Code']].drop_duplicates()

# 2. App Layout
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Annual Retail Sales Growth Analysis", style={'textAlign': 'center', 'fontFamily': 'Arial'}),
    
    html.Div([
        html.Label("Compare 3-Digit Industry Sectors:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='sector-drop',
            options=[{'label': row['Category'], 'value': row['NAICS_Code']} for _, row in sectors.iterrows()],
            value=[], # Starts empty so user can choose
            multi=True,
            placeholder="Select sectors to compare with Total Market..."
        ),
        html.Br(),
        html.Label("Select Year Range:", style={'fontWeight': 'bold'}),
        dcc.RangeSlider(
            id='year-slide',
            min=df['Year'].min(), max=df['Year'].max(),
            value=[1993, 2024], # Starting at 1993 because 1992 has no growth rate
            marks={str(y): str(y) for y in range(df['Year'].min(), df['Year'].max()+1, 5)},
            step=1
        )
    ], style={'padding': '20px', 'backgroundColor': '#f4f4f4', 'borderBottom': '1px solid #ccc'}),

    dcc.Graph(id='growth-chart', style={'height': '650px'})
], style={'fontFamily': 'Arial', 'maxWidth': '1300px', 'margin': '0 auto'})

# 3. Interactive Logic
@app.callback(
    Output('growth-chart', 'figure'),
    [Input('sector-drop', 'value'),
     Input('year-slide', 'value')]
)
def update_chart(selected_naics, selected_years):
    # Always include 'TOTAL' in the selection to act as the baseline
    comparison_list = ['TOTAL'] + selected_naics
    
    # Filter the data
    dff = df[
        (df['NAICS_Code'].isin(comparison_list)) & 
        (df['Year'].between(selected_years[0], selected_years[1]))
    ]
    
    # Generate the Line Chart
    fig = px.line(
        dff, 
        x="Year", 
        y="Growth_Rate", 
        color="NAICS_Code",
        hover_name="Category",
        title=f"Annual Growth Rate % ({selected_years[0]} - {selected_years[1]})",
        labels={"Growth_Rate": "Year-over-Year Growth (%)", "Year": "Year"},
        line_shape="linear"
    )

    # Make the "TOTAL" market line stand out (Thicker and dashed)
    fig.for_each_trace(lambda t: t.update(line=dict(width=5, dash='dash')) if t.name == 'TOTAL' else t.update(line=dict(width=3)))

    fig.update_layout(
        template="simple_white",
        hovermode="x unified",
        yaxis_ticksuffix="%",
        legend_title="Sector Code"
    )
    
    return fig

if __name__ == '__main__':
    print("Growth Dashboard starting...")
    print("Visit http://127.0.0.1:8050/ in your browser.")
    app.run(debug=True, port=8050)