import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import RFE
from sklearn.preprocessing import StandardScaler

print("=====================================================================")
print("--- AI Labs V22 (Institutional Quantitative Backtest) ---")
print("=====================================================================")

# 1. Load the SUPREME MATRIX
filename = "dados_finais_ml.csv"
master_df = pd.read_csv(filename)

print("Preparing data and the Risk Management Engine...")
master_df['MA50'] = master_df['Close'].rolling(window=50).mean()
# The AI aims to predict if the price will be higher 3 days from now
master_df['Close_3d'] = master_df['Close'].shift(-3)
master_df['Trend_Target'] = (master_df['Close_3d'] > master_df['Close']).astype(int)
master_df = master_df.dropna()

# 2. Absolute Time Split (The Final Test - 400 days out of sample)
test_days = 400
train_df = master_df.iloc[:-test_days]
test_df = master_df.iloc[-test_days:]

# 3. Removing Prohibited and Leakage Data
prohibited_columns = ['Date', 'Target', 'Trend_Target', 'Close_3d', 'Next_Day_Close', 
                      'Open', 'High', 'Low', 'Close', 'Volume', 
                      'MA7', 'MA30', 'Volume_MA7', 'Close_SP500', 'MA50']

columns_to_remove = [c for c in prohibited_columns if c in master_df.columns]

X_train = train_df.drop(columns=columns_to_remove)
y_train = train_df['Trend_Target']
X_test = test_df.drop(columns=columns_to_remove)
y_test = test_df['Trend_Target']

# 4. Standardization (Crucial for Logistic Regression)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# =====================================================================
# PHASE 1 & 2: THE FILTER (RFE) AND THE BRAIN
# =====================================================================
base_estimator = LogisticRegression(class_weight='balanced', random_state=42)
# Select the top 4 most powerful mathematical features
selector = RFE(estimator=base_estimator, n_features_to_select=4, step=1)
selector.fit(X_train_scaled, y_train)

X_train_clean = selector.transform(X_train_scaled)
X_test_clean = selector.transform(X_test_scaled)

final_model = LogisticRegression(class_weight='balanced', random_state=42)
final_model.fit(X_train_clean, y_train)

# Get the probability that the market will go UP
prob_test = final_model.predict_proba(X_test_clean)[:, 1]

# =====================================================================
# PHASE 3: THE RISK MANAGER
# =====================================================================
buy_threshold = 0.54
sell_threshold = 0.46

# 1 = LONG (Buy), -1 = SHORT (Sell), 0 = CASH (Hold)
raw_decision = np.where(prob_test > buy_threshold, 1, 
                         np.where(prob_test < sell_threshold, -1, 0))

actual_close = test_df['Close'].values
actual_ma50 = test_df['MA50'].values
actual_rsi = test_df['RSI_14'].values

final_decision = raw_decision.copy()
# Rule 1: Veto Long positions if the market is below the 50-day Moving Average (Downtrend)
final_decision = np.where((final_decision == 1) & (actual_close < actual_ma50), 0, final_decision)
# Rule 2: Veto Short positions if the market is already heavily oversold (RSI < 40)
final_decision = np.where((final_decision == -1) & (actual_rsi < 40), 0, final_decision)

# =====================================================================
# PHASE 4: THE CAPITAL SIMULATOR (ACCOUNTING FOR REAL FEES)
# =====================================================================
print("Executing Capital Simulation with Real Trading Fees (0.1%)...")

initial_capital = 10000.0
broker_fee = 0.001

algo_capital = initial_capital
market_capital = initial_capital

algo_history = [initial_capital]
market_history = [initial_capital]

current_position = 0 
total_trades = 0

next_closes = test_df['Close'].shift(-1).values

for i in range(len(final_decision) - 1):
    signal = final_decision[i]
    price_today = actual_close[i]
    price_tomorrow = next_closes[i]
    
    daily_return = (price_tomorrow - price_today) / price_today
    
    market_capital = market_capital * (1 + daily_return)
    market_history.append(market_capital)
    
    # Apply broker fee if position changes
    if signal != current_position:
        algo_capital = algo_capital * (1 - broker_fee)
        current_position = signal
        total_trades += 1
        
    if current_position == 1:
        algo_capital = algo_capital * (1 + daily_return)
    elif current_position == -1:
        algo_capital = algo_capital * (1 - daily_return)
        
    algo_history.append(algo_capital)

# =====================================================================
# PHASE 5: INSTITUTIONAL METRICS (MIT LEVEL)
# =====================================================================
# Calculate Max Drawdown
algo_series = pd.Series(algo_history)
algo_peaks = algo_series.cummax()
algo_drawdown = ((algo_series - algo_peaks) / algo_peaks).min() * 100

market_series = pd.Series(market_history)
market_peaks = market_series.cummax()
market_drawdown = ((market_series - market_peaks) / market_peaks).min() * 100

# Calculate Annualized Sharpe Ratio
algo_daily_returns = algo_series.pct_change().dropna()
algo_sharpe = (algo_daily_returns.mean() / algo_daily_returns.std()) * np.sqrt(365)

print("\n=================================================")
print(" INSTITUTIONAL BACKTEST REPORT (400 DAYS):")
print(f" -> Initial Budget:      ${initial_capital:,.2f}")
print("-------------------------------------------------")
print(f" -> Retail Investor:     ${market_capital:,.2f}")
print(f" -> CryptoMind AI:       ${algo_capital:,.2f}")
print("-------------------------------------------------")
print(" RISK ANALYSIS (What Hedge Funds care about):")
print(f" -> Market Max Drawdown: {market_drawdown:.2f}% (Destructive)")
print(f" -> AI Max Drawdown:     {algo_drawdown:.2f}% (Controlled Risk)")
print(f" -> AI Sharpe Ratio:     {algo_sharpe:.2f} (>1 is excellent!)")
print(f" -> Total Trades Executed: {total_trades} (Fees paid)")
print("=================================================")

# Plotting the Final Simulation Chart
chart_dates = test_df['Date'].iloc[:]

plt.figure(figsize=(14, 7))
plt.plot(chart_dates.values, market_history, label='Market (Buy & Hold)', color='red', alpha=0.5, linewidth=2)
plt.plot(chart_dates.values, algo_history, label='CryptoMind AI (Capital)', color='green', linewidth=3)
plt.axhline(y=initial_capital, color='black', linestyle='-', alpha=0.8, linewidth=1.5, label='Initial Budget ($10k)')

plt.title('Capital Evolution ($): CryptoMind AI vs Market with Risk Metrics', fontsize=16, fontweight='bold')
plt.ylabel('Account Balance (USD)', fontsize=12)
plt.xlabel('Timeline', fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(ticks=range(0, len(chart_dates), 30), rotation=45)
plt.tight_layout()

# Save the chart automatically for the GitHub README
plt.savefig('Gráfico de simulação.png', dpi=300)
plt.show()