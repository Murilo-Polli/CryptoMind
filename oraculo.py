import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import RFE
from sklearn.preprocessing import StandardScaler
import warnings

# Esconder avisos matemáticos chatos do terminal para ficar limpo
warnings.filterwarnings('ignore') 

print("=====================================================")
print(" 🔮 ORÁCULO CRYPTOMIND - SINAL QUANTITATIVO AO VIVO 🔮 ")
print("=====================================================")

# 1. Carregar a Base de Dados
tabela_btc = pd.read_csv("dados_finais_ml.csv")

# 2. Recriar o Gerente de Risco (MM50) ANTES de apagar linhas
tabela_btc['MM50'] = tabela_btc['Fecho'].rolling(window=50).mean()

# 3. ISOLAR O DIA DE HOJE (A última linha do ficheiro)
# Nós precisamos separar o "Hoje" antes de treinar, porque o "Hoje" não tem 
# o alvo do futuro (obviamente, nós não sabemos o preço de amanhã ainda!)
hoje_df = tabela_btc.iloc[[-1]].copy()

data_hoje = hoje_df['Data'].values[0]
preco_hoje = hoje_df['Fecho'].values[0]
rsi_hoje = hoje_df['RSI_14'].values[0]
mm50_hoje = hoje_df['MM50'].values[0]

# 4. PREPARAR O PASSADO PARA TREINAR A IA RÁPIDO
# O Alvo é a tendência de 3 dias
tabela_btc['Fecho_3d'] = tabela_btc['Fecho'].shift(-3)
tabela_btc['Alvo_Tendencia'] = (tabela_btc['Fecho_3d'] > tabela_btc['Fecho']).astype(int)

# O "Treino" é tudo o que tem resposta (sem NaN)
treino_df = tabela_btc.dropna()

# Remover as colunas que a máquina não pode ver
colunas_proibidas = ['Data', 'Alvo', 'Alvo_Tendencia', 'Fecho_3d', 'Fecho_Amanha', 
                     'Abertura', 'Maxima', 'Minima', 'Fecho', 'Volume', 
                     'MM7', 'MM30', 'Volume_MM7', 'Fecho_SP500', 'MM50']

colunas_remover = [c for c in colunas_proibidas if c in treino_df.columns]

X_treino = treino_df.drop(columns=colunas_remover)
y_treino = treino_df['Alvo_Tendencia']

# A pergunta para o Oráculo (O dia de Hoje, apagar apenas o que existe hoje)
colunas_remover_hoje = [c for c in colunas_proibidas if c in hoje_df.columns]
X_hoje = hoje_df.drop(columns=colunas_remover_hoje)

# 5. PADRONIZAÇÃO
scaler = StandardScaler()
X_treino_escalado = scaler.fit_transform(X_treino)
X_hoje_escalado = scaler.transform(X_hoje)

# 6. O FILTRO DE ELITE (RFE)
print("-> A auditar o passado e afiar o modelo...")
jeep_base = LogisticRegression(class_weight='balanced', random_state=42)
seletor = RFE(estimator=jeep_base, n_features_to_select=4, step=1)
seletor.fit(X_treino_escalado, y_treino)

X_treino_limpo = seletor.transform(X_treino_escalado)
X_hoje_limpo = seletor.transform(X_hoje_escalado)

# 7. O TREINO E A PREVISÃO DO FUTURO
modelo_final = LogisticRegression(class_weight='balanced', random_state=42)
modelo_final.fit(X_treino_limpo, y_treino)

# A IA cospe a probabilidade matemática do Bitcoin subir nos próximos 3 dias
probabilidade_alta = modelo_final.predict_proba(X_hoje_limpo)[0][1]

# 8. O GERENTE DE RISCO E O VEREDICTO FINAL
limiar_compra = 0.54
limiar_venda = 0.46

veredito = "[ MANTER EM DÓLAR (CASH) - Aguardar oportunidade mais clara ]"

if probabilidade_alta > limiar_compra:
    if preco_hoje < mm50_hoje:
        veredito = "[ VETADO PELO GERENTE ] A IA queria Comprar, mas o preço está abaixo da Média 50d."
    else:
        veredito = "[ COMPRAR BITCOIN (LONG) - Tendência de Alta Detetada ]"
elif probabilidade_alta < limiar_venda:
    if rsi_hoje < 40:
        veredito = "[ VETADO PELO GERENTE ] A IA queria Vender (Short), mas o mercado já sangrou muito (RSI baixo)."
    else:
        veredito = "[ APOSTAR NA QUEDA (SHORT) - Tendência de Baixa Detetada ]"

# 9. IMPRIMIR O RELATÓRIO DO ORÁCULO
print("\n-----------------------------------------------------")
print(f" RESUMO DO MERCADO ({data_hoje}):")
print("-----------------------------------------------------")
print(f" -> Preço do Bitcoin:       ${preco_hoje:,.2f}")
print(f" -> Média de 50 Dias:       ${mm50_hoje:,.2f}")
print(f" -> Exaustão Global (RSI):  {rsi_hoje:.2f}")
print(f" -> Probabilidade (IA):     {probabilidade_alta * 100:.2f}% de chance de Alta")
print("=====================================================")
print(f" 🤖 ORDEM OFICIAL: {veredito}")
print("=====================================================\n")