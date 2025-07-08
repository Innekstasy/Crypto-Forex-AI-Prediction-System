import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def get_coinbase_data(symbol="BTC-USD", granularity=None):
    """
    Recupera il prezzo spot per una coppia (supportato via OAuth2).
    """
    access_token = os.getenv("COINBASE_ACCESS_TOKEN")
    if not access_token:
        print(" Access token mancante. Autenticati prima con oauth_coinbase.py.")
        return None

    url = f"https://api.coinbase.com/v2/prices/{symbol}/spot"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    print("\n Debug della richiesta:")
    print(f"URL: {url}")
    print(f"Headers:\n{headers}")

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
                # Salvataggio in CSV con timestamp corrente
        data = response.json()
        amount = float(data["data"]["amount"])
        timestamp = pd.Timestamp.now()

        df = pd.DataFrame([{
            "timestamp": timestamp,
            "open": amount,
            "high": amount,
            "low": amount,
            "close": amount,
            "volume": 0.0
        }])

        file_path = f"E:\\CODE\\FOREX_CRYPTO_V2\\data\\coinbase_{symbol}.csv"
        from src.utils import append_and_clean_csv
        df = append_and_clean_csv(df, file_path)

        print(" Prezzo spot ricevuto con successo.")
        return response.json()
    else:
        print(f" Errore {response.status_code} da Coinbase: {response.text}")
        return None


def get_coinbase_public_data(symbol="BTC-USD"):
    """
    Ottiene i dati pubblici di mercato per una coppia di trading senza autenticazione.
    """
    base_url = "https://api.coinbase.com"
    request_path = f"/v2/prices/{symbol}/spot"
    url = f"{base_url}{request_path}"

    print(f"\n Tentativo di accesso a dati pubblici per {symbol}...")
    print(f"URL: {url}")

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(f" Dati pubblici ricevuti per {symbol}")
        return data
    else:
        print(f" Errore {response.status_code} da Coinbase: {response.text}")
        return None
