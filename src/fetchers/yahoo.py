import yfinance as yf
import pandas as pd
import os

def get_yahoo_data(symbol="BTC-USD", interval="5m", period="1d"):
    try:
        print(f" Recupero dati da Yahoo Finance per {symbol}...")
        df = yf.download(tickers=symbol, interval=interval, period=period, auto_adjust=True)
        if df.empty:
            print(" Yahoo Finance non ha restituito dati.")
            return None

        df = df.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        })
        df.reset_index(inplace=True)
        df = df[["Datetime", "open", "high", "low", "close", "volume"]]
        df.rename(columns={"Datetime": "timestamp"}, inplace=True)
                # Salvataggio CSV per debugging e analisi storica
        file_path = f"E:\\CODE\\FOREX_CRYPTO_V2\\data\\yahoo_{symbol}.csv"
        from src.utils import append_and_clean_csv
        df = append_and_clean_csv(df, file_path)
        print(" Dati Yahoo ricevuti.")
        return df

    except Exception as e:
        print(f" Errore Yahoo Finance: {e}")
        return None
