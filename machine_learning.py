import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import RFE
from sklearn.preprocessing import StandardScaler

print("=====================================================================")
print("--- Laboratórios de IA V22 (Relatório Institucional de Wall Street) ---")
print("=====================================================================")

# 1. Carregar a MATRIZ SUPREMA
ficheiro = "dados_finais_ml.csv"
tabela_btc = pd.read_csv(ficheiro)

print("A preparar os dados e o Gerente de Risco...")
tabela_btc['MM50'] = tabela_btc['Fecho'].rolling(window=50).mean()
tabela_btc['Fecho_3d'] = tabela_btc['Fecho'].shift(-3)
tabela_btc['Alvo_Tendencia'] = (tabela_btc['Fecho_3d'] > tabela_btc['Fecho']).astype(int)
tabela_btc = tabela_btc.dropna()

# 2. Divisão de Tempo Absoluta (A Prova Final - 400 dias)
dias_de_prova = 400
treino_df = tabela_btc.iloc[:-dias_de_prova]
teste_df = tabela_btc.iloc[-dias_de_prova:]

# 3. Remover Dados Proibidos
colunas_proibidas = ['Data', 'Alvo', 'Alvo_Tendencia', 'Fecho_3d', 'Fecho_Amanha', 
                     'Abertura', 'Maxima', 'Minima', 'Fecho', 'Volume', 
                     'MM7', 'MM30', 'Volume_MM7', 'Fecho_SP500', 'MM50']

colunas_remover = [c for c in colunas_proibidas if c in tabela_btc.columns]

X_treino = treino_df.drop(columns=colunas_remover)
y_treino = treino_df['Alvo_Tendencia']
X_teste = teste_df.drop(columns=colunas_remover)
y_teste = teste_df['Alvo_Tendencia']

# 4. Padronização
scaler = StandardScaler()
X_treino_escalado = scaler.fit_transform(X_treino)
X_teste_escalado = scaler.transform(X_teste)

# =====================================================================
# FASE 1 & 2: O FILTRO E O CÉREBRO
# =====================================================================
jeep_base = LogisticRegression(class_weight='balanced', random_state=42)
seletor = RFE(estimator=jeep_base, n_features_to_select=4, step=1)
seletor.fit(X_treino_escalado, y_treino)

X_treino_limpo = seletor.transform(X_treino_escalado)
X_teste_limpo = seletor.transform(X_teste_escalado)

modelo_final = LogisticRegression(class_weight='balanced', random_state=42)
modelo_final.fit(X_treino_limpo, y_treino)

prob_teste = modelo_final.predict_proba(X_teste_limpo)[:, 1]

# =====================================================================
# FASE 3: O GERENTE DE RISCO
# =====================================================================
limiar_compra = 0.54
limiar_venda = 0.46

decisao_bruta = np.where(prob_teste > limiar_compra, 1, 
                         np.where(prob_teste < limiar_venda, -1, 0))

fecho_real = teste_df['Fecho'].values
mm50_real = teste_df['MM50'].values
rsi_real = teste_df['RSI_14'].values

decisao_final = decisao_bruta.copy()
# Regra 1: Vetar Compras se o mercado estiver abaixo da MM50
decisao_final = np.where((decisao_final == 1) & (fecho_real < mm50_real), 0, decisao_final)
# Regra 2: Vetar Short se o mercado já estiver sobrevendido
decisao_final = np.where((decisao_final == -1) & (rsi_real < 40), 0, decisao_final)

# =====================================================================
# FASE 4: O SIMULADOR DA CONTA BANCÁRIA
# =====================================================================
print("A executar Simulação de Capital com Taxas Reais (0.1%)...")

capital_inicial = 10000.0
taxa_corretora = 0.001

capital_robo = capital_inicial
capital_mercado = capital_inicial

historico_robo = [capital_inicial]
historico_mercado = [capital_inicial]

posicao_atual = 0 
operacoes_feitas = 0

fechos_seguintes = teste_df['Fecho'].shift(-1).values

for i in range(len(decisao_final) - 1):
    sinal = decisao_final[i]
    preco_hoje = fecho_real[i]
    preco_amanha = fechos_seguintes[i]
    
    retorno_dia = (preco_amanha - preco_hoje) / preco_hoje
    
    capital_mercado = capital_mercado * (1 + retorno_dia)
    historico_mercado.append(capital_mercado)
    
    if sinal != posicao_atual:
        capital_robo = capital_robo * (1 - taxa_corretora)
        posicao_atual = sinal
        operacoes_feitas += 1
        
    if posicao_atual == 1:
        capital_robo = capital_robo * (1 + retorno_dia)
    elif posicao_atual == -1:
        capital_robo = capital_robo * (1 - retorno_dia)
        
    historico_robo.append(capital_robo)

# =====================================================================
# FASE 5: MÉTRICAS INSTITUCIONAIS (NÍVEL MIT)
# =====================================================================
# Calcular a maior queda (Drawdown) do Robô vs Mercado
serie_robo = pd.Series(historico_robo)
picos_robo = serie_robo.cummax()
drawdown_robo = ((serie_robo - picos_robo) / picos_robo).min() * 100

serie_mercado = pd.Series(historico_mercado)
picos_mercado = serie_mercado.cummax()
drawdown_mercado = ((serie_mercado - picos_mercado) / picos_mercado).min() * 100

# Calcular Sharpe Ratio (Retorno sobre o Risco) - Simplificado anualizado
retornos_diarios_robo = serie_robo.pct_change().dropna()
sharpe_robo = (retornos_diarios_robo.mean() / retornos_diarios_robo.std()) * np.sqrt(365)

print("\n=================================================")
print(" RELATÓRIO INSTITUCIONAL FINAL (400 DIAS):")
print(f" -> Orçamento Inicial:    ${capital_inicial:,.2f}")
print("-------------------------------------------------")
print(f" -> Investidor Comum:     ${capital_mercado:,.2f}")
print(f" -> Robô CryptoMind (IA): ${capital_robo:,.2f}")
print("-------------------------------------------------")
print(" ANÁLISE DE RISCO (O que os fundos querem ver):")
print(f" -> Pior Queda do Mercado (Max Drawdown): {drawdown_mercado:.2f}% (Destrutivo)")
print(f" -> Pior Queda da IA (Max Drawdown):      {drawdown_robo:.2f}% (Controlado)")
print(f" -> Sharpe Ratio da IA:                   {sharpe_robo:.2f} (Maior que 1 é excelente!)")
print(f" -> Total de Transações:                  {operacoes_feitas} (Taxas pagas)")
print("=================================================")

# Gráfico
datas_grafico = teste_df['Data'].iloc[:] # Pega todas as datas para alinhar com a lista inicializada

plt.figure(figsize=(14, 7))
plt.plot(datas_grafico.values, historico_mercado, label='Mercado (Comprar e Segurar)', color='red', alpha=0.5, linewidth=2)
plt.plot(datas_grafico.values, historico_robo, label='Robô CryptoMind (Capital)', color='green', linewidth=3)
plt.axhline(y=capital_inicial, color='black', linestyle='-', alpha=0.8, linewidth=1.5, label='Orçamento Inicial ($10k)')

plt.title('Evolução do Capital ($): Robô vs Mercado com Métricas de Risco', fontsize=16, fontweight='bold')
plt.ylabel('Saldo na Conta (USD)', fontsize=12)
plt.xlabel('Linha do Tempo', fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(ticks=range(0, len(datas_grafico), 30), rotation=45)
plt.tight_layout()

plt.show()