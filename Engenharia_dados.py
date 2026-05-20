import pandas as pd

print("--- Loading Analytical Engine (Pandas) V2.0 ---")

# 1. Load the raw CSV file
filename = "historico_bitcoin.csv"
btc_df = pd.read_csv(filename)

# 2. Ensure numerical format (float) for price and volume columns
for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
    btc_df[col] = btc_df[col].astype(float)

# 3. Classic Moving Averages
btc_df['MA7'] = btc_df['Close'].rolling(window=7).mean()
btc_df['MA30'] = btc_df['Close'].rolling(window=30).mean()

# ====================================================================
# 4. ADVANCED FEATURE ENGINEERING (The Wall Street Edge)
# ====================================================================
print("Injecting Strength, Volatility, and Momentum metrics...")

# Feature 1: Daily Return (% change from Open to Close)
btc_df['Daily_Return'] = (btc_df['Close'] - btc_df['Open']) / btc_df['Open']

# Feature 2: Volatility / Amplitude (How wild was the daily swing?)
btc_df['Volatility_Amplitude'] = (btc_df['High'] - btc_df['Low']) / btc_df['Open']

# Feature 3: Distance from MAs (Is the price overextended?)
btc_df['Dist_MA7'] = (btc_df['Close'] - btc_df['MA7']) / btc_df['MA7']
btc_df['Dist_MA30'] = (btc_df['Close'] - btc_df['MA30']) / btc_df['MA30']

# Feature 4: Volume Momentum (Is trading activity surging?)
btc_df['Volume_MA7'] = btc_df['Volume'].rolling(window=7).mean()
btc_df['Volume_Momentum'] = (btc_df['Volume'] - btc_df['Volume_MA7']) / btc_df['Volume_MA7']

# ====================================================================

# 5. The Target Label (Machine Learning Objective)
# Shift closing price backwards by 1 to get tomorrow's close on today's row
btc_df['Next_Day_Close'] = btc_df['Close'].shift(-1)
# 1 if tomorrow's close is higher than today's (UP), else 0 (DOWN)
btc_df['Target'] = (btc_df['Next_Day_Close'] > btc_df['Close']).astype(int)

# Clean missing data caused by moving average windows (drops the first 30 days)
btc_df = btc_df.dropna()

# 6. Save the mathematically enriched dataset
final_filename = "dados_preparados_btc.csv"
btc_df.to_csv(final_filename, index=False)

print(f"\nPhase 2 (V2) Complete! Mathematical database '{final_filename}' successfully generated.")