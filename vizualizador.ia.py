import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

print("--- A iniciar o Módulo de Visão Computacional (Matplotlib) ---")

# 1. Carregar dados e treinar o modelo rapidamente (o mesmo da aula passada)
tabela_btc = pd.read_csv("dados_preparados_btc.csv")
X = tabela_btc.drop(columns=['Data', 'Alvo'])
y = tabela_btc['Alvo']

X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=0.20, shuffle=False)

modelo_rf = RandomForestClassifier(n_estimators=100, random_state=42)
modelo_rf.fit(X_treino, y_treino)

print("Cérebro treinado. A gerar o Raio-X do Modelo...")

# 2. FEATURE IMPORTANCE (O que a IA achou mais importante?)
# O robô diz-nos qual coluna foi mais decisiva para ele acertar as previsões
importancia = modelo_rf.feature_importances_
colunas = X.columns

# 3. Criar o Gráfico Profissional
plt.figure(figsize=(10, 6)) # Tamanho da "folha" de papel
plt.bar(colunas, importancia, color='darkblue') # Criar barras azuis

# Adicionar títulos e estilo
plt.title('Raio-X da IA: O Que Importa Mais para o Bitcoin?', fontsize=16, fontweight='bold')
plt.ylabel('Nível de Importância Matemática', fontsize=12)
plt.xlabel('Variáveis (Features)', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

print("GRÁFICO PRONTO! Olhe para a nova janela que se abriu no seu computador.")
print("(Pode fechar a janela do gráfico quando quiser terminar o programa)")

# Exibir o gráfico no ecrã do seu computador
plt.show()