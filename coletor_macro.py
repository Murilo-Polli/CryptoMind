import yfinance as yf
import pandas as pd

print("--- A conectar aos Servidores de Wall Street (Yahoo Finance) ---")

# O símbolo do S&P 500 no mercado financeiro é ^GSPC
ticker_sp500 = "^GSPC"

print(f"A descarregar o histórico do índice {ticker_sp500}...")
# Descarregamos os últimos 4 anos para garantir que temos datas suficientes para cruzar com o Bitcoin
dados_sp500 = yf.download(ticker_sp500, period="4y")

# O Yahoo Finance traz muita informação. Nós só queremos o Preço de Fecho (Close)
tabela_sp500 = dados_sp500[['Close']].reset_index()

# Renomear as colunas para o nosso padrão
tabela_sp500.columns = ['Data', 'Fecho_SP500']

# A data vem com horas e fuso horário, precisamos de a limpar para ficar igual ao formato da Binance (YYYY-MM-DD)
tabela_sp500['Data'] = tabela_sp500['Data'].dt.strftime('%Y-%m-%d')

# Guardar o ficheiro para usarmos amanhã!
nome_ficheiro = "historico_sp500.csv"
tabela_sp500.to_csv(nome_ficheiro, index=False)

print("\n=============================================")
print(f"SUCESSO! Ficheiro '{nome_ficheiro}' criado.")
print("=============================================")
print("As últimas 5 linhas do mercado americano:")
print(tabela_sp500.tail())