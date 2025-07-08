import requests
import pandas as pd

def get_cryptocompare_data():
    """
    Recupera OHLC per BTC da CryptoCompare (ultime 48 ore, 1h)
    """
    url = "https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=48"

    try:
        response = requests.get(url)
        response.raise_for_status()
        raw = response.json()

        if raw.get("Response") != "Success":
            print(" CryptoCompare: Nessun dato valido.")
            return None

        data = raw["Data"]["Data"]
        df = pd.DataFrame(data)

        df["timestamp"] = pd.to_datetime(df["time"], unit="s")
        df.rename(columns={"volumefrom": "volume"}, inplace=True)
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        df.sort_values("timestamp", inplace=True)

        print(f" Dati CryptoCompare ricevuti: {len(df)} righe")

        from src.utils import append_and_clean_csv
        file_path = f"E:\\CODE\\FOREX_CRYPTO_V2\\data\\cryptocompare_BTC.csv"
        df = append_and_clean_csv(df, file_path)

        return df

    except Exception as e:
        print(f" Errore CryptoCompare: {e}")
        return None

