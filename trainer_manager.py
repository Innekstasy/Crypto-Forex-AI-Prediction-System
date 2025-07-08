import os
import pandas as pd
from src.utils import get_predefined_pairs
from src.training import train_model

DATA_DIR = "E:/CODE/FOREX_CRYPTO_V2/data"
LOG_FILE = "E:/CODE/FOREX_CRYPTO_V2/logs/training_log.txt"

def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def run_training_for_pair(pair):
    symbol = pair["binance"]
    log(f"\n Inizio training per {symbol}")

    # Cerca tutti i CSV che contengono il nome del simbolo (es. BTC)
    matching_files = [
        f for f in os.listdir(DATA_DIR)
        if symbol.replace("USDT", "").replace("-", "") in f and f.endswith(".csv")
    ]

    if not matching_files:
        log(f" Nessun file CSV trovato per {symbol}")
        return

    dfs = []
    for file in matching_files:
        file_path = os.path.join(DATA_DIR, file)
        try:
            df = pd.read_csv(file_path, low_memory=False)
            dfs.append(df)
        except Exception as e:
            log(f" Errore nel file {file}: {e}")

    if not dfs:
        log(f" Nessun DataFrame valido trovato per {symbol}")
        return

    try:
        df_combined = pd.concat(dfs, ignore_index=True)
        # Forza conversione numerica delle colonne principali
        for col in ["open", "high", "low", "close", "volume"]:
            if col in df_combined.columns:
                df_combined[col] = pd.to_numeric(df_combined[col], errors="coerce")
        # Elimina righe con valori mancanti fondamentali
        df_combined.dropna(subset=["open", "high", "low", "close", "volume"], inplace=True)

        log(f" Dati combinati: {len(df_combined)} righe da {len(dfs)} file")
        result = train_model(df_combined)

        if result:
            log(f" Training completato per {symbol}")
        else:
            log(f" Training fallito per {symbol} — dati insufficienti o non validi dopo preprocessing.")
    except Exception as e:
        log(f" Errore durante training {symbol}: {e}")

def main():
    log(" === TRAINING BATCH AVVIATO ===")
    for pair in get_predefined_pairs():
        run_training_for_pair(pair)
    log(" Fine training.\n")

if __name__ == "__main__":
    main()

