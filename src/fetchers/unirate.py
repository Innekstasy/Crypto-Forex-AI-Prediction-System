import os
import requests
import pandas as pd
from dotenv import load_dotenv
import certifi


# Carica API Key da .env
load_dotenv()
API_KEY = os.getenv("UNIRATE_API_KEY")
BASE_URL = "https://api.unirateapi.com/api/rates"

def get_unirate_data(base="BTC"):
    """
    Recupera i tassi di cambio da UniRate per una crypto base (es. BTC).
    Ritorna un DataFrame con timestamp, base, symbol, rate.
    """

    if not API_KEY:
        print(" UNIRATE_API_KEY mancante nel file .env")
        return None

    url = f"{BASE_URL}?api_key={API_KEY}&from={base}"
    try:
        response = requests.get(url, verify=certifi.where())
        # response = requests.get(url, verify=False)
        response.raise_for_status()
        data = response.json()
        rates = data.get("rates", {})

        df = pd.DataFrame([
            {
                "timestamp": pd.Timestamp.now(),
                "base": base,
                "symbol": symbol,
                "rate": float(rate)
            }
            for symbol, rate in rates.items()
        ])

        print(f" Dati UniRate ricevuti: {len(df)} righe")

        from src.utils import append_and_clean_csv
        file_path = f"E:\\CODE\\FOREX_CRYPTO_V2\\data\\unirate_{base}.csv"
        df = append_and_clean_csv(df, file_path)


        return df

    except requests.exceptions.SSLError as ssl_err:
        print(" UniRate non disponibile (SSL error) – potrebbe essere causato da firewall o certificato mancante.")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f" UniRate errore rete: {req_err}")
        return None
    except Exception as e:
        print(f" UniRate errore sconosciuto: {e}")
        return None
