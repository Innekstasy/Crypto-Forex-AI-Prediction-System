import requests
import pandas as pd
import os

DATA_PATH = "E:\\CODE\\FOREX_CRYPTO_V2\\data"

# Dati OHLC da CryptoCompare (1h, 48 intervalli = 2 giorni)
url = "https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=48"

try:
    response = requests.get(url)
    response.raise_for_status()
    raw = response.json()

    if raw.get("Response") != "Success":
        print("❌ CryptoCompare: Risposta non valida")
        exit(1)

    data = raw["Data"]["Data"]
    df = pd.DataFrame(data)

    df["timestamp"] = pd.to_datetime(df["time"], unit="s")
    df.rename(columns={"volumefrom": "volume"}, inplace=True)
    df = df[["timestamp", "open", "high", "low", "close", "volume"]]
    df.sort_values("timestamp", inplace=True)

    print(f"✅ Dati CryptoCompare ricevuti: {len(df)} righe")
    print(df.head())

    os.makedirs(DATA_PATH, exist_ok=True)
    df.to_csv(os.path.join(DATA_PATH, "cryptocompare_BTC.csv"), index=False)
    print(f"📁 File salvato in: {os.path.join(DATA_PATH, 'cryptocompare_BTC.csv')}")

except Exception as e:
    print(f"❌ Errore CryptoCompare: {e}")
 
