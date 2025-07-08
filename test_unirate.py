# import os
# import requests
# import pandas as pd
# from dotenv import load_dotenv

# Carica variabili da .env
# load_dotenv()
# API_KEY = os.getenv("UNIRATE_API_KEY")
# BASE_SYMBOL = "BTC"
# DATA_PATH = "E:\\CODE\\FOREX_CRYPTO_V2\\data"

# if not API_KEY:
#     print("❌ ERRORE: Variabile UNIRATE_API_KEY non trovata nel .env")
#     exit(1)

# URL dell’endpoint per i tassi da BTC verso altre valute
# url = f"https://api.unirateapi.com/api/rates?api_key={API_KEY}&from={BASE_SYMBOL}"

# try:
#     response = requests.get(url)
#     response.raise_for_status()
#     data = response.json()

#     rates = data.get("rates", {})
#     if not rates:
#         print("⚠️ Nessun tasso ricevuto dalla API.")
#         exit(1)

    # Crea DataFrame per confrontarlo con gli altri fetcher
#     df = pd.DataFrame([
#         {
#             "timestamp": pd.Timestamp.now(),
#             "base": BASE_SYMBOL,
#             "symbol": symbol,
#             "rate": float(rate)
#         }
#         for symbol, rate in rates.items()
#     ])

#     print("✅ Tassi ricevuti:")
#     print(df.head())

    # Salvataggio CSV
#     os.makedirs(DATA_PATH, exist_ok=True)
#     file_path = os.path.join(DATA_PATH, f"unirate_{BASE_SYMBOL}.csv")
#     df.to_csv(file_path, index=False)
#     print(f"📁 CSV salvato in: {file_path}")

# except requests.RequestException as e:
#     print(f"❌ Errore nella richiesta HTTP: {e}")
# except Exception as e:
#     print(f"❌ Errore imprevisto: {e}")
 
import requests
import certifi

session = requests.Session()
session.verify = certifi.where()

url = "https://api.unirateapi.com/api/rates?api_key=YOUR_API_KEY&from=BTC"
response = session.get(url)
print(response.status_code)
print(response.json())
