import pandas as pd

print("--- A carregar o Cérebro Analítico (Pandas) V2.0 ---")

# 1. Carregar o nosso ficheiro CSV bruto
nome_ficheiro = "historico_bitcoin.csv"
tabela_btc = pd.read_csv(nome_ficheiro)

# 2. Garantir que tudo é número (float)
for col in ['Abertura', 'Maxima', 'Minima', 'Fecho', 'Volume']:
    tabela_btc[col] = tabela_btc[col].astype(float)

# 3. Médias Móveis Clássicas
tabela_btc['MM7'] = tabela_btc['Fecho'].rolling(window=7).mean()
tabela_btc['MM30'] = tabela_btc['Fecho'].rolling(window=30).mean()

# ====================================================================
# 4. ENGENHARIA DE FEATURES AVANÇADA (O Segredo de Wall Street)
# ====================================================================
print("A injetar cálculos de Força, Volatilidade e Momentum...")

# Feature 1: Retorno Diário (Quanto % subiu ou caiu hoje face à abertura?)
tabela_btc['Retorno_Diario'] = (tabela_btc['Fecho'] - tabela_btc['Abertura']) / tabela_btc['Abertura']

# Feature 2: Amplitude / Volatilidade (Quão louco foi o dia?)
tabela_btc['Amplitude'] = (tabela_btc['Maxima'] - tabela_btc['Minima']) / tabela_btc['Abertura']

# Feature 3: Distância para as Médias (O preço está muito "esticado" ou muito abaixo do normal?)
tabela_btc['Distancia_MM7'] = (tabela_btc['Fecho'] - tabela_btc['MM7']) / tabela_btc['MM7']
tabela_btc['Distancia_MM30'] = (tabela_btc['Fecho'] - tabela_btc['MM30']) / tabela_btc['MM30']

# Feature 4: Momentum do Volume (O volume de negociação está a aumentar?)
tabela_btc['Volume_MM7'] = tabela_btc['Volume'].rolling(window=7).mean()
tabela_btc['Distancia_Volume'] = (tabela_btc['Volume'] - tabela_btc['Volume_MM7']) / tabela_btc['Volume_MM7']

# ====================================================================

# 5. O Rótulo (Target)
tabela_btc['Fecho_Amanha'] = tabela_btc['Fecho'].shift(-1)
tabela_btc['Alvo'] = (tabela_btc['Fecho_Amanha'] > tabela_btc['Fecho']).astype(int)

# Limpar dados vazios causados pelos cálculos das médias (apagamos os primeiros 30 dias)
tabela_btc = tabela_btc.dropna()

# 6. Guardar a tabela rica em matemática
ficheiro_final = "dados_preparados_btc.csv"
tabela_btc.to_csv(ficheiro_final, index=False)
print(f"\nFase 2 (V2) Concluída! Base de dados matemática '{ficheiro_final}' gerada com sucesso.")