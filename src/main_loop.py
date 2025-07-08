import os
import time
import pandas as pd
import datetime
import csv
from pathlib import Path
from datetime import datetime, timedelta

import sys
sys.path.append("E:\\CODE\\FOREX_CRYPTO_V2")

from strategy import predict_trade
from src.fetchers.binance import get_current_price
from src.fetchers.unirate import get_unirate_data
from blockchair import get_blockchair_data
from src.trailing_stop import adjust_sl



MODEL_PATH = "E:\\CODE\\FOREX_CRYPTO_V2\\models"
MODEL_FILE = os.path.join(MODEL_PATH, "trading_model.pkl")
SCALER_FILE = os.path.join(MODEL_PATH, "scaler.pkl")
DATA_PATH = "E:/CODE/FOREX_CRYPTO_V2/data/binance_BTCUSDT.csv"
LOG_PATH = Path("logs") / "signal_log.csv"

PAIR_BINANCE = "BTCUSDT"
PAIR_COINBASE = "BTC-USD"

print("\n🎯 Avvio automatico di analisi predittiva solo per BTCUSDT ogni 30 minuti...\n")

while True:
    print(f"\n📊 [{datetime.now().strftime('%H:%M:%S')}] Esecuzione analisi su {PAIR_BINANCE}...")

    # === Carica dati dal CSV ===
    if not os.path.exists(DATA_PATH):
        print(f"❌ ERRORE: File dati mancante: {DATA_PATH}")
        continue

    df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"]).sort_values("timestamp").reset_index(drop=True)

    if df.empty or any(col not in df.columns for col in ["open", "high", "low", "close", "volume"]):
        print("❌ Dati incompleti o errati.")
        continue

    print(f"✅ Ultimo timestamp disponibile: {df['timestamp'].iloc[-1]}")

    # === Simulazione delay ===
    # delay_sec = 15
    # print(f"⏳ Attendo {delay_sec}s per emulare ritardo real-time...\n")
    # time.sleep(delay_sec)

    # === Live price ===
    current_price = get_current_price(PAIR_BINANCE)
    if current_price is None:
        print("⚠️ Prezzo live non disponibile. Attendo 60 secondi...\n")
        time.sleep(60)
        continue

    print(f"💰 Prezzo live: {current_price}")

    # === Predizione ===
    df.attrs["symbol"] = PAIR_BINANCE
    signal = predict_trade(df, live_price=current_price)

    if not signal or not isinstance(signal, dict):
        print("❌ Segnale non valido.")
        continue

    # === Trailing SL dinamico
    signal = adjust_sl(signal, current_price)

    unirate_confirma = None
    blockchair_confirma = None

    # === UniRate ===
    unirate_df = get_unirate_data(base="BTC")
    if unirate_df is not None and not unirate_df.empty:
        row = unirate_df[unirate_df["symbol"] == "USDT"]
        if not row.empty:
            unirate_price = row["rate"].values[0]
            soglia = df["close"].tail(5).mean()
            unirate_confirma = unirate_price >= soglia

    # === Blockchair ===
    blockchair_data = get_blockchair_data()
    if blockchair_data:
        tx_count = blockchair_data["tx_count_24h"]
        soglia_tx = int(df["close"].tail(5).mean() * 6)
        blockchair_confirma = tx_count >= soglia_tx

    # === Log ===
    LOG_PATH.parent.mkdir(exist_ok=True)
    log_row = {
        "timestamp": pd.Timestamp.now(),
        "symbol": PAIR_COINBASE,
        "azione": signal["azione"] if signal else "N/A",
        "tp": signal["TP"] if signal else "N/A",
        "sl": signal["SL"] if signal else "N/A",
        "unirate_confirma": unirate_confirma,
        "blockchair_confirma": blockchair_confirma,
        "decisione": (
            "CONFERMATO" if unirate_confirma and blockchair_confirma else
            "DA MONITORARE" if unirate_confirma or blockchair_confirma else
            "ANNULLATO"
        ),
        "esito": signal["esito"] if signal else "N/A",
        "rsi": signal["rsi"] if signal else "N/A",
        "tp_diff": signal["tp_diff"] if signal else "N/A",
        "sl_diff": signal["sl_diff"] if signal else "N/A",
        "price_entry": signal["price_entry"] if signal else "N/A",
        "lot_size": signal["lot_size"] if signal else "N/A",
        "pip_value": signal["pip_value"] if signal else "N/A",
        "binance_timeframe": "1m",
        # "simulated_delay": delay_sec,
        "live_price": current_price,
        "entry_vs_live_diff": round(current_price - df["close"].iloc[-1], 4) if not df["close"].isna().all() else "N/A",
        "motivo_blocco": signal.get("motivo_blocco", "") if signal else "",
    }

    log_row['note_tp_sl'] = 'TP/SL OPERATIVI' if signal and not signal.get('motivo_blocco') else 'TP/SL INFORMATIVI - SEGNALI AD ALTO RISCHIO'
    print()
    print(f" Note TP/SL: {log_row['note_tp_sl']}")
    
#    write_header = not LOG_PATH.exists()
#    with open(LOG_PATH, mode="a", newline="", encoding="utf-8") as f:
#        writer = csv.DictWriter(f, fieldnames=log_row.keys())
#        if write_header:
#            writer.writeheader()
#        writer.writerow(log_row)

#    print(f"\n📥 Log registrato in: {LOG_PATH.name}")

    slippage_tollerato = 15
    slippage_effettivo = abs(current_price - signal["price_entry"]) if signal else float('inf')

    if slippage_effettivo > slippage_tollerato:
        print(f"\n⛔️ SLIPPAGE TROPPO ALTO: {slippage_effettivo:.2f} USD > {slippage_tollerato} USD")
        print("❌ Segnale SCARTATO. Log NON registrato.\n")
        continue

    write_header = not LOG_PATH.exists()
    with open(LOG_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=log_row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(log_row)
    print(f"\n📥 Log registrato in: {LOG_PATH.name}")

    # === Countdown visivo ===
    countdown = 60 * 5
    print(f"\n⏳ Prossima analisi tra 5 minuti:")
    for i in range(countdown, 0, -1):
        mins, secs = divmod(i, 60)
        time.sleep(1)
        print(f"\r⌛ {mins:02d}:{secs:02d} min", end="", flush=True)
    print()
 
