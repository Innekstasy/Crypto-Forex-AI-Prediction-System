import requests
import pandas as pd
import os

symbol = "bitcoin"
url = url = f"https://rest.coincap.io/v3/assets/{symbol}?apiKey=5f85de402685499d0ca172935d70ee74b3eac58bbba6757cbac50bdfb0fe704d"
DATA_PATH = "E:\\CODE\\FOREX_CRYPTO_V2\\data"

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    if "data" not in data:
        print("❌ Risposta CoinCap non valida.")
        exit(1)

    asset = data["data"]
    price = float(asset["priceUsd"])
    timestamp = pd.Timestamp.now()

    # Costruisci riga OHLCV singola (come Coinbase)
    df = pd.DataFrame([{
        "timestamp": timestamp,
        "open": price,
        "high": price,
        "low": price,
        "close": price,
        "volume": float(asset.get("volumeUsd24Hr", 0.0))  # se disponibile
    }])

    print("✅ Dati CoinCap ricevuti:")
    print(df)

    # Salvataggio CSV
    # os.makedirs(DATA_PATH, exist_ok=True)
    # file_path = os.path.join(DATA_PATH, "coincap_BTC.csv")
    # df.to_csv(file_path, index=False)
    # print(f"📁 File salvato in: {file_path}")

except Exception as e:
    print(f"❌ Errore CoinCap: {e}")
 
