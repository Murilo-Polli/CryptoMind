import requests
import csv
from datetime import datetime

print("Iniciando o programa")

# Conectar com a API da Binance
url_historico = "https://api.binance.com/api/v3/klines"
parametros = {
    "symbol": "BTCUSDT",
    "interval": "1d",
    "limit": 1000
}

resposta = requests.get(url_historico, params=parametros)
dados_historicos = resposta.json()

print(f"Foram descarregados {len(dados_historicos)} dias de histórico do Bitcoin")

# Cria o CSV para armazenar os dados da binance
print("A iniciar processo de limpeza e gravação em CSV...")

nome_ficheiro = "historico_bitcoin.csv"

# Abrir o ficheiro em modo de escrita "w"
with open(nome_ficheiro, mode='w', newline='') as ficheiro_csv:
    escritor = csv.writer(ficheiro_csv)

    # Escrever o cabeçalho (os nomes das colunas na tabela)
    escritor.writerow(['Data', 'Abertura', 'Maxima', 'Minima', 'Fecho', 'Volume'])

    # Processar cada dia dos 1000 descarregados
    for dia in dados_historicos:
        # A Binance envia o tempo em milissegundos, converter para segundos (/1000)
        timestamp_ms = dia[0]
        data_real = datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d')

        abertura = dia[1]
        maxima = dia[2]
        minima = dia[3]
        fecho = dia[4]
        volume = dia[5]

        # Escrever a linha limpa no nosso ficheiro
        escritor.writerow([data_real, abertura, maxima, minima, fecho, volume])

print(f"BINGO! Ficheiro '{nome_ficheiro}' criado com sucesso na sua pasta.")