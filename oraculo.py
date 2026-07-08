import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import RFE
from sklearn.preprocessing import StandardScaler
import warnings
import os
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException

# Hide non-critical math warnings from the terminal output
warnings.filterwarnings('ignore') 

print("=====================================================")
print(" 🔮 CRYPTOMIND ORACLE V2.0 - LIVE PAPER TRADING 🔮 ")
print("=====================================================")

# 1. Load the Supreme Database
master_df = pd.read_csv("dados_finais_ml.csv")

# 2. Re-establish the Risk Manager (MA50)
master_df['MA50'] = master_df['Close'].rolling(window=50).mean()

# 3. ISOLATE "TODAY" 
today_df = master_df.iloc[[-1]].copy()
date_today = today_df['Date'].values[0]
price_today = today_df['Close'].values[0]
rsi_today = today_df['RSI_14'].values[0]
ma50_today = today_df['MA50'].values[0]

# 4. PREPARE HISTORICAL DATA FOR RAPID AI TRAINING
master_df['Close_3d'] = master_df['Close'].shift(-3)
master_df['Trend_Target'] = (master_df['Close_3d'] > master_df['Close']).astype(int)
train_df = master_df.dropna()

prohibited_columns = ['Date', 'Target', 'Trend_Target', 'Close_3d', 'Next_Day_Close', 
                      'Open', 'High', 'Low', 'Close', 'Volume', 
                      'MA7', 'MA30', 'Volume_MA7', 'Close_SP500', 'MA50']
columns_to_remove = [c for c in prohibited_columns if c in train_df.columns]

X_train = train_df.drop(columns=columns_to_remove)
y_train = train_df['Trend_Target']
columns_to_remove_today = [c for c in prohibited_columns if c in today_df.columns]
X_today = today_df.drop(columns=columns_to_remove_today)

# 5. STANDARDIZATION & 6. FILTER (RFE)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_today_scaled = scaler.transform(X_today)

base_estimator = LogisticRegression(class_weight='balanced', random_state=42)
selector = RFE(estimator=base_estimator, n_features_to_select=4, step=1)
selector.fit(X_train_scaled, y_train)

X_train_clean = selector.transform(X_train_scaled)
X_today_clean = selector.transform(X_today_scaled)

# 7. TRAINING AND LIVE PREDICTION
final_model = LogisticRegression(class_weight='balanced', random_state=42)
final_model.fit(X_train_clean, y_train)
probability_up = final_model.predict_proba(X_today_clean)[0][1]

# 8. RISK MANAGER AND FINAL VERDICT
buy_threshold = 0.54
sell_threshold = 0.46
signal = 0 # 0 = Hold, 1 = Buy, -1 = Sell
verdict = "[ HOLD CASH - Awaiting a clearer statistical edge ]"

if probability_up > buy_threshold:
    if price_today < ma50_today:
        verdict = "[ VETOED BY RISK MANAGER ] AI suggested LONG, but price is below MA50."
    else:
        verdict = "[ EXECUTE LONG (BUY) - Uptrend Probability Detected ]"
        signal = 1
elif probability_up < sell_threshold:
    if rsi_today < 40:
        verdict = "[ VETOED BY RISK MANAGER ] AI suggested SHORT, but market is oversold."
    else:
        verdict = "[ EXECUTE SHORT (SELL) - Downtrend Probability Detected ]"
        signal = -1

print("\n-----------------------------------------------------")
print(f" LIVE MARKET SUMMARY ({date_today}):")
print("-----------------------------------------------------")
print(f" -> Current BTC Price:      ${price_today:,.2f}")
print(f" -> AI Bull Probability:    {probability_up * 100:.2f}% chance of Uptrend")
print(f" 🤖 AI VERDICT: {verdict}")
print("=====================================================\n")

# =====================================================================
# 9. V2.0: LIVE PAPER TRADING EXECUTION (BINANCE TESTNET)
# =====================================================================
print("Initiating Binance Testnet Connection...")

# Load Keys from the vault (.env)
load_dotenv()
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_SECRET_KEY')

if not API_KEY or not API_SECRET:
    print("❌ ERROR: API Keys not found in .env file. Execution aborted.")
else:
    try:
        # Connect to Binance TESTNET
        client = Client(API_KEY, API_SECRET, testnet=True)
        # Aumentar a janela de tolerância para 60 segundos (60000ms)
        client.recv_window = 60000 

        # Connect to Binance TESTNET
        client = Client(API_KEY, API_SECRET, testnet=True)
        
        # --- LINHA MÁGICA DE SINCRONIZAÇÃO ---
        import time
        server_time = client.get_server_time()['serverTime']
        client.timestamp_offset = server_time - int(time.time() * 1000)
        # --------------------------------------
        
        # Check Account Balance (Fake USD - USDT)
        
        # Check Account Balance (Fake USD - USDT)
        balance = client.get_asset_balance(asset='USDT')
        print(f"💼 Testnet Account Balance: ${float(balance['free']):,.2f} USDT")
        
        # Execute the Order based on AI Signal
        quantity_to_trade = 0.05 # Trading 0.05 BTC as a test size
        
        if signal == 1:
            print(f"🚀 Sending BUY order for {quantity_to_trade} BTC...")
            order = client.create_order(
                symbol='BTCUSDT',
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity_to_trade
            )
            print("✅ ORDER SUCCESSFUL! Fake money spent. BTC Acquired.")
            
        elif signal == -1:
            print(f"📉 Sending SELL order for {quantity_to_trade} BTC...")
            order = client.create_order(
                symbol='BTCUSDT',
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity_to_trade
            )
            print("✅ ORDER SUCCESSFUL! BTC Sold.")
            
        else:
            print("🛑 SIGNAL IS HOLD: No orders sent to the exchange today.")

    except BinanceAPIException as e:
        print(f"❌ API ERROR: {e}")
    except Exception as e:
        print(f"❌ SYSTEM ERROR: {e}")