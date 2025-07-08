import os
import nasdaqdatalink
from dotenv import load_dotenv

# Carica .env con la chiave API
load_dotenv()
nasdaq_key = os.getenv("NASDAQ_API_KEY")

# Imposta la chiave API nel modulo
nasdaqdatalink.ApiConfig.api_key = nasdaq_key

# Dataset di esempio pubblico accessibile
dataset_code = "BCHAIN/MKPRU"  # Market price (USD) dalla blockchain.info
# dataset_code = "BITSTAMP/USD"  <-- sostituibile se trovi un dataset crypto gratuito accessibile

try:
    data = nasdaqdatalink.get(dataset_code)
    print("✅ Dataset caricato con successo:")
    print(data.tail())
except Exception as e:
    print("❌ Errore:", e)
