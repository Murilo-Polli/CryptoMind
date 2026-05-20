import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import RFE
from sklearn.preprocessing import StandardScaler
import warnings

# Hide non-critical math warnings from the terminal output
warnings.filterwarnings('ignore') 

print("=====================================================")
print(" 🔮 CRYPTOMIND ORACLE - LIVE QUANTITATIVE SIGNAL 🔮 ")
print("=====================================================")

# 1. Load the Supreme Database
master_df = pd.read_csv("dados_finais_ml.csv")

# 2. Re-establish the Risk Manager (MA50) BEFORE dropping any rows
master_df['MA50'] = master_df['Close'].rolling(window=50).mean()

# 3. ISOLATE "TODAY" (The very last row of the dataset)
# We must isolate 'Today' before training because 'Today' does not have 
# the future target yet (we cannot know tomorrow's price today).
today_df = master_df.iloc[[-1]].copy()

date_today = today_df['Date'].values[0]
price_today = today_df['Close'].values[0]
rsi_today = today_df['RSI_14'].values[0]
ma50_today = today_df['MA50'].values[0]

# 4. PREPARE HISTORICAL DATA FOR RAPID AI TRAINING
# The target is the 3-day trend direction
master_df['Close_3d'] = master_df['Close'].shift(-3)
master_df['Trend_Target'] = (master_df['Close_3d'] > master_df['Close']).astype(int)

# The 'Training Set' is everything that has a known target answer (no NaN)
train_df = master_df.dropna()

# Remove data that the machine cannot see (preventing Data Leakage)
prohibited_columns = ['Date', 'Target', 'Trend_Target', 'Close_3d', 'Next_Day_Close', 
                      'Open', 'High', 'Low', 'Close', 'Volume', 
                      'MA7', 'MA30', 'Volume_MA7', 'Close_SP500', 'MA50']

columns_to_remove = [c for c in prohibited_columns if c in train_df.columns]

X_train = train_df.drop(columns=columns_to_remove)
y_train = train_df['Trend_Target']

# The prompt for the Oracle (Today's data, dropping only the prohibited columns present today)
columns_to_remove_today = [c for c in prohibited_columns if c in today_df.columns]
X_today = today_df.drop(columns=columns_to_remove_today)

# 5. STANDARDIZATION
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_today_scaled = scaler.transform(X_today)

# 6. THE ELITE FILTER (RFE)
print("-> Auditing history and sharpening the algorithmic model...")
base_estimator = LogisticRegression(class_weight='balanced', random_state=42)
selector = RFE(estimator=base_estimator, n_features_to_select=4, step=1)
selector.fit(X_train_scaled, y_train)

X_train_clean = selector.transform(X_train_scaled)
X_today_clean = selector.transform(X_today_scaled)

# 7. TRAINING AND LIVE PREDICTION
final_model = LogisticRegression(class_weight='balanced', random_state=42)
final_model.fit(X_train_clean, y_train)

# The AI calculates the mathematical probability of Bitcoin rising in the next 3 days
probability_up = final_model.predict_proba(X_today_clean)[0][1]

# 8. RISK MANAGER AND FINAL VERDICT
buy_threshold = 0.54
sell_threshold = 0.46

verdict = "[ HOLD CASH - Awaiting a clearer statistical edge ]"

if probability_up > buy_threshold:
    if price_today < ma50_today:
        verdict = "[ VETOED BY RISK MANAGER ] AI suggested LONG, but price is below the 50-day MA."
    else:
        verdict = "[ EXECUTE LONG (BUY) - Uptrend Probability Detected ]"
elif probability_up < sell_threshold:
    if rsi_today < 40:
        verdict = "[ VETOED BY RISK MANAGER ] AI suggested SHORT, but market is severely oversold (Low RSI)."
    else:
        verdict = "[ EXECUTE SHORT (SELL) - Downtrend Probability Detected ]"

# 9. PRINT THE ORACLE REPORT
print("\n-----------------------------------------------------")
print(f" LIVE MARKET SUMMARY ({date_today}):")
print("-----------------------------------------------------")
print(f" -> Current BTC Price:      ${price_today:,.2f}")
print(f" -> 50-Day Moving Average:  ${ma50_today:,.2f}")
print(f" -> Market Exhaustion (RSI):{rsi_today:.2f}")
print(f" -> AI Bull Probability:    {probability_up * 100:.2f}% chance of Uptrend")
print("=====================================================")
print(f" 🤖 OFFICIAL ORDER: {verdict}")
print("=====================================================\n")