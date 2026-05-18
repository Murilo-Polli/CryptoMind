import pandas as pd
import numpy as np

print("--- Laboratório V5: Injetando Indicadores Quantitativos (RSI) ---")

# 1. Carregar bases de dados
print("A carregar bases de dados...")
btc = pd.read_csv("dados_preparados_btc.csv")
sp500 = pd.read_csv("historico_sp500.csv")

# 2. O Cruzamento (Merge)
tabela_mestra = pd.merge(btc, sp500, on='Data', how='left')

# 3. Tratamento de Valores Nulos (Bolsa fechada nos fins de semana)
tabela_mestra['Fecho_SP500'] = tabela_mestra['Fecho_SP500'].ffill().bfill()

# 4. Features Macroeconómicas Clássicas
tabela_mestra['Retorno_SP500'] = tabela_mestra['Fecho_SP500'].pct_change()
tabela_mestra['Retorno_SP500_Ontem'] = tabela_mestra['Retorno_SP500'].shift(1)
tabela_mestra['Correlacao_BTC_SP500'] = tabela_mestra['Retorno_Diario'].rolling(window=30).corr(tabela_mestra['Retorno_SP500'])

# =====================================================================
# 5. A NOVA ARMA: RSI (Índice de Força Relativa - 14 dias)
# =====================================================================
print("A calcular a exaustão do mercado (RSI 14 dias)...")

# Passo A: Separar os dias de lucro dos dias de prejuízo
delta = tabela_mestra['Fecho'].diff()
ganhos = delta.clip(lower=0)
perdas = -1 * delta.clip(upper=0)

# Passo B: Calcular a média exponencial de 14 dias de ganhos e perdas
media_ganhos = ganhos.ewm(com=13, adjust=False).mean()
media_perdas = perdas.ewm(com=13, adjust=False).mean()

# Passo C: A fórmula final do RSI
rs = media_ganhos / media_perdas
tabela_mestra['RSI_14'] = 100 - (100 / (1 + rs))

# =====================================================================

# Limpar buracos gerados pelos novos cálculos
tabela_mestra = tabela_mestra.dropna()

# 6. Guardar a Matriz Final para a IA
nome_ficheiro = "dados_finais_ml.csv"
tabela_mestra.to_csv(nome_ficheiro, index=False)

print("\n--- Amostra do RSI ---")
print(tabela_mestra[['Data', 'Fecho', 'RSI_14', 'Alvo']].tail())
print(f"\nMatriz Suprema Atualizada! Ficheiro '{nome_ficheiro}' pronto.")