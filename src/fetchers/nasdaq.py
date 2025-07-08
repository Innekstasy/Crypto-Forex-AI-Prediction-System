import os
import pandas as pd
import quandl
from dotenv import load_dotenv
from src.utils import save_dataframe_to_csv

# Carica variabili d'ambiente
load_dotenv()
API_KEY = os.getenv("NASDAQ_API_KEY")

# Configura la chiave API
quandl.ApiConfig.api_key = API_KEY

def get_nasdaq_data(pair="BTC", interval="daily"):
    try:
        symbol = "XBTUSD" if pair.upper() == "BTC" else f"{pair.upper()}USD"
        dataset_code = f"BITFINEX/{symbol}"

        # Richiedi i dati storici da Nasdaq/Quandl
        df = quandl.get(dataset_code)

        df.reset_index(inplace=True)
        df.rename(columns={
            "Date": "timestamp",
            "High": "high",
            "Low": "low",
            "Open": "open",
            "Last": "close",
            "Volume": "volume"
        }, inplace=True)

        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Salva il CSV locale
        from src.utils import append_and_clean_csv
        file_path = f"E:\\CODE\\FOREX_CRYPTO_V2\\data\\nasdaq_{pair}.csv"
        df = append_and_clean_csv(df, file_path)


        return df

    except Exception as e:
        print(f" Errore durante il fetch da Nasdaq (Quandl): {e}")
        return None
