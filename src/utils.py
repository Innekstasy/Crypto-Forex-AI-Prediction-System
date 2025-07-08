import os 
import pandas as pd
import numpy as np

from src.wyckoff_filter import is_in_consolidation
from src.wyckoff_filter_breakout import is_breakout
from src.indicators import calculate_adx


def get_predefined_pairs():
    """
    Restituisce una lista di coppie predefinite da analizzare.
    """
    return [
        {"binance": "BTCUSDT", "coinbase": "BTC-USD", "yahoo": "BTC-USD"},
        # {"binance": "ETHUSDT", "coinbase": "ETH-USD", "yahoo": "ETH-USD"},
        # {"binance": "XRPUSDT", "coinbase": "XRP-USD", "yahoo": "XRP-USD"},
        # {"binance": "ADAUSDT", "coinbase": "ADA-USD", "yahoo": "ADA-USD"},
        # {"binance": "SOLUSDT", "coinbase": "SOL-USD", "yahoo": "SOL-USD"}
    ]

def select_pair():
    """
    Permette all'utente di scegliere una coppia da analizzare da una lista numerata.
    """
    pairs = get_predefined_pairs()
    
    print("\n Seleziona una coppia da analizzare:")
    for i, pair in enumerate(pairs, start=1):
        print(f"{i}. {pair['binance']} / {pair['coinbase']} / {pair['yahoo']}")
        

    while True:
        try:
            choice = int(input("\nInserisci il numero della coppia da analizzare: "))
            if 1 <= choice <= len(pairs):
                return pairs[choice - 1]
            else:
                print()
                print(" Scelta non valida. Inserisci un numero corretto.")
        except ValueError:
            print()
            print(" Errore: Inserisci un numero valido.")

def save_dataframe_to_csv(df, filename):
    path = os.path.join("E:\\CODE\\FOREX_CRYPTO_V2\\data", filename)
    df.to_csv(path, index=False)

def append_and_clean_csv(new_df, file_path):
    """
    Unisce nuovi dati a CSV esistente, rimuove duplicati e ordina per timestamp.
    """
    if os.path.exists(file_path):
        try:
            old_df = pd.read_csv(file_path, low_memory=False)
            if "timestamp" in old_df.columns:
                old_df["timestamp"] = pd.to_datetime(old_df["timestamp"], errors="coerce")
            full_df = pd.concat([old_df, new_df], ignore_index=True)
            full_df.drop_duplicates(subset=["timestamp"], inplace=True)
            full_df.sort_values("timestamp", inplace=True)
        except Exception as e:
            print(f" Errore durante la lettura di {file_path}: {e}")
            full_df = new_df
    else:
        full_df = new_df

    full_df.to_csv(file_path, index=False)
    print(f" CSV aggiornato: {file_path} ({len(full_df)} righe)")
    return full_df

def calculate_risk_score(df, action, trend, atr_value, rsi_val):
    """
    Calcola un punteggio di rischio per il segnale (0 = rischio alto, 3 = rischio basso).
    Aggiunta gestione dei prezzi elevati.
    """

    score = 1  # partenza neutra

    try:
        last_close = float(df["close"].iloc[-1])

        # Gestione di prezzi elevati: arrotonda a 2 decimali per evitare overflow
        last_close = round(last_close, 2)

        # Controllo se il prezzo è troppo elevato
        if last_close > 100000:
            print(f"⚠️ Prezzo elevato rilevato: {last_close}")
            last_close = round(last_close, 2)  # Mantieni il prezzo live corretto

        # Filtro Wyckoff range stretto attivo
        if is_in_consolidation(df, window=20, threshold=0.006):
            score -= 1

        # Breakout presente
        if is_breakout(df, window=20, breakout_margin=0.0015):
            score += 1

        # ATR check
        if atr_value < last_close * 0.002:
            score -= 1
        else:
            score += 1

        # RSI check
        if 45 < rsi_val < 55:
            score -= 1
        else:
            score += 1

        # Calcolo della forza del trend tramite ADX
        df = calculate_adx(df)
        adx_value = df["ADX"].iloc[-1]
        print(f"⚙️ ADX calcolato: {adx_value:.2f} (forza del trend)")

        # Aggiustamento del punteggio di rischio in base alla forza del trend
        if adx_value > 25:
            print("🔍 Trend forte rilevato: punteggio di rischio ridotto")
            score += 1
        else:
            print("🔍 Trend debole o laterale: rischio invariato")

        # Allineamento al trend
        if (trend == "up" and action == "BUY") or (trend == "down" and action == "SELL"):
            score += 1
        else:
            score -= 1

        # Limita il punteggio tra 0 e 3
        score = max(0, min(score, 3))
        return score

    except Exception as e:
        print(f"⚠️ Errore nel calcolo del risk score: {e}")
        return 0

# def check_tp_sl(tp, sl, last_close, atr_value, action, df=None, trend=None):
#     """
#     Valida e corregge i valori di Take Profit e Stop Loss in base al prezzo corrente,
#     ATR, direzione del trade e range minimo.
#     """
#     if atr_value is None or atr_value == 0:
#         print(f"⚠️ ATR non valido: {atr_value}")
#         return None, None

#     try:
#         tp = float(tp)
#         sl = float(sl)
#         last_close = float(last_close)
#     except (ValueError, TypeError):
#         print(f"⚠️ TP, SL o prezzo non validi: tp={tp}, sl={sl}, price={last_close}")
#         return None, None

#     banda_minima = atr_value * 1.2
#     range_operativo = abs(tp - sl)

#     if range_operativo < banda_minima:
#         print(f"⚠️ Range TP/SL troppo stretto ({range_operativo:.2f} < {banda_minima:.2f}). Ricalcolo...")

#         if action == "BUY":
#             tp = last_close + (atr_value * 2.0)
#             sl = last_close - (atr_value * 1.0)
#         elif action == "SELL":
#             tp = last_close - (atr_value * 2.0)
#             sl = last_close + (atr_value * 1.0)

#     return tp, sl

def check_tp_sl(tp, sl, last_close, atr_value, action, df=None, trend=None):
    """
    Valida e corregge i valori di Take Profit e Stop Loss in base al prezzo corrente,
    ATR, direzione del trade e range minimo.
    """
    if atr_value is None or atr_value == 0:
        print(f"⚠️ ATR non valido: {atr_value}")
        return None, None

    try:
        tp = float(tp)
        sl = float(sl)
        last_close = float(last_close)
    except (ValueError, TypeError):
        print(f"⚠️ TP, SL o prezzo non validi: tp={tp}, sl={sl}, price={last_close}")
        # Provo a rigenerarli se last_close è valido
        if last_close is not None and isinstance(last_close, (int, float)):
            if action == "BUY":
                tp = last_close + atr_value * 2.0
                sl = last_close - atr_value * 1.0
            elif action == "SELL":
                tp = last_close - atr_value * 2.0
                sl = last_close + atr_value * 1.0
            return tp, sl
        else:
            return None, None

    banda_minima = atr_value * 1.2
    range_operativo = abs(tp - sl)

    if range_operativo < banda_minima:
        print(f"⚠️ Range TP/SL troppo stretto ({range_operativo:.2f} < {banda_minima:.2f}). Ricalcolo...")

        if action == "BUY":
            tp = last_close + (atr_value * 2.0)
            sl = last_close - (atr_value * 1.0)
        elif action == "SELL":
            tp = last_close - (atr_value * 2.0)
            sl = last_close + (atr_value * 1.0)

    return tp, sl
