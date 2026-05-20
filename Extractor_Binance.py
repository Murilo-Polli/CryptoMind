import requests
import csv
from datetime import datetime

print("--- Initiating Data Ingestion (Binance API) ---")

# 1. API Configuration
binance_url = "https://api.binance.com/api/v3/klines"
api_params = {
    "symbol": "BTCUSDT",
    "interval": "1d",
    "limit": 1000
}

try:
    # 2. Fetching the Data
    response = requests.get(binance_url, params=api_params)
    response.raise_for_status() # Security check: guarantees connection is OK
    historical_data = response.json()

    print(f"SUCCESS: Downloaded {len(historical_data)} days of Bitcoin history.")
    print("Starting data cleaning and CSV export process...")

    # 3. Data Processing and Storage
    filename = "historico_bitcoin.csv"

    # Open the file in write mode
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)

        # Professional English header
        writer.writerow(['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

        # Process each of the 1000 downloaded days
        for day in historical_data:
            # Binance sends timestamp in ms, convert to seconds
            timestamp_ms = day[0]
            real_date = datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d')

            open_price = float(day[1])
            high_price = float(day[2])
            low_price = float(day[3])
            close_price = float(day[4])
            volume = float(day[5])

            # Write the clean row to our file
            writer.writerow([real_date, open_price, high_price, low_price, close_price, volume])

    print(f"BINGO! File '{filename}' successfully created and populated.")

except Exception as e:
    print(f"CRITICAL ERROR: Failed to fetch data from Binance. Details: {e}")