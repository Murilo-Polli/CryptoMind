import random

print("--- Crypto Volatility Simulator ---")

current_price = 63000

# random.uniform generates a random decimal number between the two limits
# Here, we represent -5% as -0.05 and +5% as 0.05
fluctuation = random.uniform(-0.05, 0.05) 

# Math logic: New Price = Current Price * (1 + fluctuation)
new_price = current_price * (1 + fluctuation)

# The 'f' before the string allows us to inject variables directly inside {}
# The ':.2f' rounds the number to 2 decimal places (like real money)
print(f"Current Price: ${current_price}")
print(f"Simulated New Price: ${new_price:.2f}")