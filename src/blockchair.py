import requests
import pandas as pd

def get_blockchair_data():
    """
    Ritorna un dizionario con metriche on-chain da Blockchair (BTC)
    """
    url = "https://api.blockchair.com/bitcoin/stats"

    try:
        response = requests.get(url)
        response.raise_for_status()
        stats = response.json().get("data", {})

        return {
            "timestamp": pd.Timestamp.now(),
            "tx_count_24h": stats.get("transactions_24h"),
            "hashrate_24h": stats.get("hashrate_24h")
        }

    except Exception as e:
        print()
        print(f" Errore Blockchair: {e}")
        print()
        return None
 
