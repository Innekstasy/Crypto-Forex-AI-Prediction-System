import requests
import pandas as pd
import os

DATA_PATH = "E:\\CODE\\FOREX_CRYPTO_V2\\data"
url = "https://api.blockchair.com/bitcoin/stats"

try:
    response = requests.get(url)
    response.raise_for_status()
    raw = response.json()

    stats = raw.get("data", {})
    if not stats:
        print("❌ Nessun dato trovato in risposta.")
        exit(1)

    # Estrai metriche chiave
    data = {
        "timestamp": pd.Timestamp.now(),
        "tx_count_24h": stats.get("transactions_24h"),
        "volume_usd_24h": stats.get("volume_usd"),
        "active_addresses": stats.get("addresses_active"),
        "hashrate_24h": stats.get("hashrate_24h")
    }

    # Stampa dati estratti
    print("✅ Dati Blockchair (BTC) ricevuti:")
    for k, v in data.items():
        print(f"{k}: {v}")

    # Salva per confronto futuro
    df = pd.DataFrame([data])
    os.makedirs(DATA_PATH, exist_ok=True)
    df.to_csv(os.path.join(DATA_PATH, "blockchair_btc_stats.csv"), index=False)
    print(f"📁 Dati salvati in: {os.path.join(DATA_PATH, 'blockchair_btc_stats.csv')}")

except Exception as e:
    print(f"❌ Errore Blockchair: {e}")
 
