import os
import pandas as pd
from binance.client import Client
from dotenv import load_dotenv

# Carica API Keys
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)
DATA_PATH = "E:\\CODE\\FOREX_CRYPTO_V2\\data"

def get_binance_data(symbol="BTCUSDT", interval="1m", limit=100):
    """
    Scarica i dati da Binance e aggiorna il file CSV.
    """
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        if not klines:
            print(f" ERRORE: Nessun dato ricevuto da Binance per {symbol}")
            return None

        df = pd.DataFrame(klines, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "trades", "taker_base", "taker_quote", "ignore"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)

        # Salvataggio CSV
        file_path = os.path.join(DATA_PATH, f"binance_{symbol}.csv")
        from src.utils import append_and_clean_csv
        df = append_and_clean_csv(df, file_path)

        print(f" Dati Binance ricevuti: {len(df)} righe")

        return df
    except Exception as e:
        print(f" ERRORE Fetch Binance: {e}")
        return None

def get_current_price(symbol="BTCUSDT"):
    """
    Recupera il prezzo attuale della coppia da Binance.
    """
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker["price"])
    except Exception as e:
        print(f" ERRORE nel fetch del prezzo attuale: {e}")
        return None
