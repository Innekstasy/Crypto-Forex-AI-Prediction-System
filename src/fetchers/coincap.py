import requests
import pandas as pd

def get_coincap_data(symbol="bitcoin"):
    """
    Ottiene il prezzo attuale da CoinCap e lo adatta a OHLCV.
    """
    mapping = {
        "btc": "bitcoin",
        "eth": "ethereum",
        "ada": "cardano",
        "xrp": "ripple",
        "sol": "solana"
    }
    symbol_full = mapping.get(symbol.lower(), symbol.lower())
    url = f"https://rest.coincap.io/v3/assets/{symbol_full}?apiKey=5f85de402685499d0ca172935d70ee74b3eac58bbba6757cbac50bdfb0fe704d"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        asset = data.get("data", {})
        if not asset:
            print(" CoinCap: Nessun dato disponibile.")
            return None

        price = float(asset["priceUsd"])
        volume = float(asset.get("volumeUsd24Hr", 0.0))
        timestamp = pd.Timestamp.now()

        df = pd.DataFrame([{
            "timestamp": timestamp,
            "open": price,
            "high": price,
            "low": price,
            "close": price,
            "volume": volume
        }])
        print(f" Dati CoinCap ricevuti: {len(df)} righe")

        from src.utils import append_and_clean_csv
        file_path = f"E:\\CODE\\FOREX_CRYPTO_V2\\data\\coincap_{symbol}.csv"
        df = append_and_clean_csv(df, file_path)

        return df

    except Exception as e:
        print(f" Errore CoinCap: {e}")
        return None
 
