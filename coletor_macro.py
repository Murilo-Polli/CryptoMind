import yfinance as yf
import pandas as pd

print("--- Connecting to Wall Street Servers (Yahoo Finance API) ---")

# S&P 500 ticker symbol in global markets
sp500_ticker = "^GSPC"

try:
    print(f"Downloading historical data for {sp500_ticker}...")
    # Downloading the last 4 years to ensure enough date overlap with Bitcoin
    sp500_raw_data = yf.download(sp500_ticker, period="4y")
    
    if sp500_raw_data.empty:
        raise ValueError("No data returned from Yahoo Finance.")

    # Extracting only the 'Close' price and resetting index to access the Date
    sp500_df = sp500_raw_data[['Close']].reset_index()

    # Renaming columns to our English standard
    sp500_df.columns = ['Date', 'Close_SP500']

    # Formatting the Date to match the Binance (YYYY-MM-DD) standard perfectly
    sp500_df['Date'] = sp500_df['Date'].dt.strftime('%Y-%m-%d')

    # Saving the macro environment dataset
    filename = "historico_sp500.csv"
    sp500_df.to_csv(filename, index=False)

    print("\n=============================================")
    print(f"SUCCESS: Macroeconomic dataset '{filename}' created.")
    print("=============================================")
    print("Latest US Market Action (Last 5 days):")
    print(sp500_df.tail())

except Exception as e:
    print(f"CRITICAL ERROR: Failed to fetch macro data. Details: {e}")