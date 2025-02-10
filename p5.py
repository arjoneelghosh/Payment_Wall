import pandas as pd

def load_sales_data(csv_file):
    try:
        df = pd.read_csv(csv_file)
        
        # Attempt to auto-detect mixed date formats
        df['Date'] = pd.to_datetime(df['Date'], format='mixed', errors='coerce')
        
        # Check for any invalid dates
        if df['Date'].isna().sum() > 0:
            print("Warning: Some dates could not be parsed correctly. Check for inconsistencies.")
            print("Sample problematic rows:")
            print(df[df['Date'].isna()].head())
        
        return df
    except FileNotFoundError:
        print("File not found. Please provide a valid file.")
        return None

def find_top_weekends(df):
    # Extract day of the week (0 = Monday, 6 = Sunday)
    df['Day_of_Week'] = df['Date'].dt.dayofweek
    
    # Filter for only Saturdays (5) and Sundays (6)
    weekend_sales = df[df['Day_of_Week'].isin([5, 6])].copy()
    
    # Group by weekend and sum the sales
    weekend_sales['Weekend'] = weekend_sales['Date'].dt.to_period('W')
    top_weekends = weekend_sales.groupby('Weekend')['Sales'].sum().nlargest(3)
    
    print("Top 3 Most Productive Weekends (Revenue):")
    print(top_weekends)

def find_top_customers(csv_file):
    try:
        df = pd.read_csv(csv_file)
        
        # Count orders per customer
        top_customers = df['Customer_ID'].value_counts()
        
        print("Customers with Maximum Number of Orders (From Most to Least):")
        print(top_customers)
    except FileNotFoundError:
        print("File not found. Please provide a valid file.")

def main():
    sales_csv = r'sales_data.csv' 
    customer_csv = r'customer_purchases.csv'  
    df_sales = load_sales_data(sales_csv)
    if df_sales is not None:
        find_top_weekends(df_sales)
    
    find_top_customers(customer_csv)

if __name__ == "__main__":
    main()
