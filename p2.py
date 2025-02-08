import pandas as pd

def load_order_data(csv_file):
    try:
        df = pd.read_csv(csv_file)
        df['Order_Placed'] = pd.to_datetime(df['Order_Placed'])
        df['Order_Completed'] = pd.to_datetime(df['Order_Completed'])
        return df
    except FileNotFoundError:
        print("File not found.")
        return None

def calculate_processing_times(df):
    df['Processing_Time'] = (df['Order_Completed'] - df['Order_Placed']).dt.total_seconds() / 3600
    avg_processing_time = df['Processing_Time'].mean()
    print(f"Average Order Processing Time: {avg_processing_time:.2f} hours\n")
    long_orders = df[df['Processing_Time'] > avg_processing_time]
    print("Orders Taking Longer Than Average:")
    print(long_orders[['Order_ID', 'Processing_Time']].to_string(index=False))
    print("\nTop 5 Slowest Orders:")
    slowest_orders = df.nlargest(5, 'Processing_Time')
    print(slowest_orders[['Order_ID', 'Processing_Time']].to_string(index=False))

def main():
    csv_file = r'C:\one drive local data\Programming\STEP_saturday_extra_class\order_processing_log.csv'
    df = load_order_data(csv_file)
    if df is not None:
        calculate_processing_times(df)

if __name__ == "__main__":
    main()
