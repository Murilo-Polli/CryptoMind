The idea for this project came after a severe 40% Bitcoin market crash. Therefore, I realized the need for a quantitative personal assistant that would not only deepen my understanding of the financial market but also forecast trends to mitigate portfolio risk during similar market downturns.

The foundation of the project relies on a robust data pipeline. Using Python, I engineered an automated script to interface directly with the Binance REST API via HTTP requests. The system extracts 1,000 days of historical market data, specifically pulling the daily OHLCV (Open, High, Low, Close, Volume) metrics, and structures this raw data into a persistent CSV file for subsequent feature engineering.

To give the machine learning model an analytical edge, I utilized the Pandas library to conduct advanced feature engineering. Beyond basic price action, I calculated technical indicators such as the 50-day Moving Average (MA50) to establish market trend direction, and the Relative Strength Index (RSI) to quantify market exhaustion cycles (fear and greed). Recognizing that cryptocurrency does not operate in a vacuum, I also integrated the Yahoo Finance API to fetch daily S&P 500 data, effectively embedding global macroeconomic sentiment into the bot's decision-making process.

To transform the engineered features into actionable trading signals, I developed a predictive model using Logistic Regression to classify future market movements. The model acts as the core decision engine, distinguishing between safe holding periods and high-risk downturns. To validate the system, I built a custom backtesting framework to simulate historical performance. The results proved the algorithm's risk mitigation capabilities: while a standard buy-and-hold strategy suffered a severe -49.5% maximum drawdown during the analyzed period, the ML-driven portfolio successfully constrained losses to just -19.4%, effectively protecting capital during market crashes.

Core Technologies: Python, Pandas, Scikit-Learn (Logistic Regression), yfinance, Binance REST API.

Execution Pipeline:
To completely replicate the project's data flow, train the model, and view the final predictions, execute the modules in the following order via your terminal:

Step 1: Data Ingestion (Micro & Macro)

python Extractor_Binance.py (Fetches raw BTC data)

python coletor_macro.py (Fetches raw S&P 500 data)

Step 2: Feature Engineering

python Engenharia_dados.py (Calculates technical indicators like MA50 and RSI)

python engenharia_macro.py (Merges macro environment data)

Step 3: Machine Learning Engine

python machine_learning.py (Trains the Logistic Regression model and generates the backtesting results)

Step 4: Live Predictions & Visualization

python oraculo.py (The core bot predicting the next market movement)

python vizualizador_ia.py (Generates the final performance and simulation charts)