import requests
import pandas as pd
import os

def get_coingecko_data(symbol="bitcoin", vs_currency="usd", days=1):
    """
    Restituisce dati OHLC da CoinGecko per un asset (es. BTC).
    Output: DataFrame con timestamp, open, high, low, close, volume.
    """
    mapping = {
        "btc": "bitcoin",
        "eth": "ethereum",
        "ada": "cardano",
        "xrp": "ripple",
        "sol": "solana"
    }
    symbol_full = mapping.get(symbol.lower(), symbol.lower())
    url = f"https://api.coingecko.com/api/v3/coins/{symbol_full}/ohlc?vs_currency={vs_currency}&days={days}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        raw_data = response.json()

        if not raw_data:
            print(" CoinGecko: Nessun dato ricevuto.")
            return None

        df = pd.DataFrame(raw_data, columns=["timestamp", "open", "high", "low", "close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["volume"] = 0.0  # volume non fornito da CoinGecko

        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        df.sort_values("timestamp", inplace=True)

        print(f" Dati CoinGecko ricevuti: {len(df)} righe")

        from src.utils import append_and_clean_csv
        file_path = f"E:\\CODE\\FOREX_CRYPTO_V2\\data\\coingecko_{symbol}.csv"
        df = append_and_clean_csv(df, file_path)


        return df

    except Exception as e:
        print(f" Errore CoinGecko: {e}")
        return None
 
