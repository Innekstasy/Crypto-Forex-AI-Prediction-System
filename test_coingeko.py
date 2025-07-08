import requests
import pandas as pd
import time
import os

# === CONFIG ===
symbol = "bitcoin"
vs_currency = "usd"
days = 1  # Usa '1' per oggi, oppure '30' per 30 giorni
DATA_PATH = "E:\\CODE\\FOREX_CRYPTO_V2\\data"

url = f"https://api.coingecko.com/api/v3/coins/{symbol}/ohlc?vs_currency={vs_currency}&days={days}"

try:
    response = requests.get(url)
    response.raise_for_status()
    raw_data = response.json()

    if not raw_data:
        print("❌ Nessun dato ricevuto da CoinGecko.")
        exit(1)

    # CoinGecko restituisce: [timestamp, open, high, low, close]
    df = pd.DataFrame(raw_data, columns=["timestamp", "open", "high", "low", "close"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["volume"] = 0.0  # CoinGecko OHLC non include volume

    df = df[["timestamp", "open", "high", "low", "close", "volume"]]
    df.sort_values("timestamp", inplace=True)

    print("✅ Dati CoinGecko ricevuti:")
    print(df.head())

    os.makedirs(DATA_PATH, exist_ok=True)
    file_path = os.path.join(DATA_PATH, "coingecko_BTC.csv")
    df.to_csv(file_path, index=False)
    print(f"📁 File salvato in: {file_path}")

except Exception as e:
    print(f"❌ Errore CoinGecko: {e}")
 
