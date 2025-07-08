import yfinance as yf
import pandas as pd

def test_yahoo_crypto_fetch(symbol="BTC-USD", interval="5m", period="1d"):
    print(f"🔍 Fetching {symbol} data from Yahoo Finance...")
    try:
        data = yf.download(tickers=symbol, interval=interval, period=period)
        if data.empty:
            print("⚠️ Nessun dato restituito.")
        else:
            print("✅ Dati ricevuti correttamente:")
            print(data.tail(5))  # Mostra le ultime 5 righe
    except Exception as e:
        print(f"❌ Errore nel recupero dati da Yahoo: {e}")

if __name__ == "__main__":
    test_yahoo_crypto_fetch()
