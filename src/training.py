import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from joblib import dump
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import VotingClassifier
from sklearn.utils import resample
from src.indicators import fibonacci_levels, calculate_elliott_wave_features


# Percorso della cartella modelli
MODEL_PATH = "E:\\CODE\\FOREX_CRYPTO_V2\\models"

def prepare_data(df):
    """Prepara i dati per il training: calcola i rendimenti e imposta il target."""
    if df is None or df.empty:
        print()
        print(" ERRORE: Il DataFrame dei dati è vuoto. Controlla il fetcher.")
        print()
        return None

    print(f" Preprocessing dati... Numero righe iniziali: {len(df)}")
    
    df["returns"] = df["close"].pct_change()

    # ✅ Fibonacci (differenza tra close attuale e livello 0.618)
    high = df["high"].max()
    low = df["low"].min()
    fibs = fibonacci_levels(high, low)
    df["fib_level_diff"] = abs(df["close"] - fibs[5])

    # ✅ Elliott wave
    df["wave_score"] = calculate_elliott_wave_features(df)
    df["target"] = np.where(df["returns"].shift(-1) > 0, 1, 0)  # 1 = BUY, 0 = SELL
    df.dropna(subset=["returns", "fib_level_diff", "wave_score"], inplace=True)

    if df.empty:
        print()
        print(" ERRORE: Dopo il preprocessing, il DataFrame è vuoto!")
        return None

    print()
    print(f"✅ Preprocessing completato. Numero righe finali: {len(df)}")
    
    return df

def train_model(df):
    """Allena il modello AI e salva i file."""
    df = prepare_data(df)
    if df is None:
        print()
        print(" Training annullato: dati non validi.")
        return False

    # Se la cartella models/ non esiste, creala
    if not os.path.exists(MODEL_PATH):
        print()
        print(f" Creazione cartella modelli: {MODEL_PATH}")
        os.makedirs(MODEL_PATH)

    try:
        # Definizione delle features e target
        X = df[["open", "high", "low", "close", "volume", "fib_level_diff", "wave_score"]]
        y = df["target"]
        print(f"⚖️ Distribuzione target: BUY={sum(y==1)}, SELL={sum(y==0)}")

        # ⚖️ Bilanciamento delle classi per evitare bias

        buy_df = df[df["target"] == 1]
        sell_df = df[df["target"] == 0]

        min_len = min(len(buy_df), len(sell_df))
        buy_df_bal = resample(buy_df, replace=False, n_samples=min_len, random_state=42)
        sell_df_bal = resample(sell_df, replace=False, n_samples=min_len, random_state=42)

        df_balanced = pd.concat([buy_df_bal, sell_df_bal]).sample(frac=1, random_state=42)

        X = df_balanced[["open", "high", "low", "close", "volume", "fib_level_diff", "wave_score"]]
        y = df_balanced["target"]

        print()
        print(f" Dati per il training: {X.shape[0]} righe, {X.shape[1]} colonne")
        
        # Normalizzazione
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Divisione train/test
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        # Addestramento modello
        # model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        lr = LogisticRegression(max_iter=1000)
        model = VotingClassifier(estimators=[
            ("rf", rf),
            ("lr", lr)
        ], voting="soft")

        model.fit(X_train, y_train)

        # Salvataggio del modello e scaler
        model_file = os.path.join(MODEL_PATH, "trading_model.pkl")
        scaler_file = os.path.join(MODEL_PATH, "scaler.pkl")

        dump(model, model_file)
        dump(scaler, scaler_file)

        # Verifica se il file è stato salvato
        if os.path.exists(model_file) and os.path.exists(scaler_file):
            print()
            print(" Modello AI addestrato e salvato con successo!")
            
            return True
        else:
            print()
            print(" ERRORE: Il modello non è stato salvato correttamente.")
            
            return False

    except Exception as e:
        print()
        print(f" ERRORE durante il training: {e}")
        
        return False
