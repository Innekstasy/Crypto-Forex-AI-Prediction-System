import os
import sys
import pandas as pd
import csv
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.fetchers.binance import get_binance_data
from src.fetchers.coinbase import get_coinbase_data
from src.strategy import predict_trade
from src.utils import select_pair
from src.training import train_model
from src.fetchers.yahoo import get_yahoo_data
from src.fetchers.unirate import get_unirate_data
from src.fetchers.coingecko import get_coingecko_data
from src.fetchers.coincap import get_coincap_data
from src.fetchers.cryptocompare import get_cryptocompare_data
from blockchair import get_blockchair_data


# Percorso del modello AI
MODEL_PATH = "E:\\CODE\\FOREX_CRYPTO_V2\\models"
MODEL_FILE = os.path.join(MODEL_PATH, "trading_model.pkl")
SCALER_FILE = os.path.join(MODEL_PATH, "scaler.pkl")

# ✅ 1. Creazione della cartella MODELS se non esiste
if not os.path.exists(MODEL_PATH):
    print(f" Creazione cartella modello: {MODEL_PATH}")
    os.makedirs(MODEL_PATH)

# ✅ 2. Controllare se il modello esiste, altrimenti addestrarlo
# ✅ Mostra data ultimo training del modello

# ✅ Mostra data ultimo training del modello
if os.path.exists(MODEL_FILE):
    last_mod_time = datetime.fromtimestamp(os.path.getmtime(MODEL_FILE))
    print(f"\n 📅 Ultimo addestramento modello: {last_mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
    minutes_passed = int((datetime.now() - last_mod_time).total_seconds() / 60)
    print()
    print(f" ⏱️ Tempo trascorso dall'addestramento: {minutes_passed} minuti\n")
else:
    print("\n ⚠️ Nessun modello trovato: training non ancora eseguito.\n")

# === 2.1 Controlla se i modelli sono troppo vecchi
MODEL_AGE_HOURS = 1

def is_stale(file):
    if not os.path.exists(file):
        return True
    last_mod = datetime.fromtimestamp(os.path.getmtime(file))
    return datetime.now() - last_mod > timedelta(hours=MODEL_AGE_HOURS)

# === [AUTO-TRAINING DISABILITATO – ORA GESTITO DA update_and_train_loop.py] ===
# if (
#     not os.path.exists(MODEL_FILE)
#     or not os.path.exists(SCALER_FILE)
#     or is_stale(MODEL_FILE)
#     or is_stale(SCALER_FILE)
# ):
#     print(f" Modello troppo vecchio o mancante. Ultimo aggiornamento > {MODEL_AGE_HOURS} ore fa.")
#     print()
#     print(" Procedo con l'addestramento automatico tramite trainer_manager.py...\n")
#     print()
#
#     import subprocess
#     import sys
#
#     exit_code = subprocess.call([sys.executable, "trainer_manager.py"])
#
#     if exit_code != 0:
#         print(" ERRORE durante l'esecuzione di trainer_manager.py")
#         sys.exit(1)
#     else:
#         print(" Addestramento completato. Avvio l'analisi...\n")
#         print()
# else:
#     print()
#     print(f" Modello aggiornato: nessun retraining necessario (modificato da meno di {MODEL_AGE_HOURS} ore).")
#     print()
#     print(" Puoi forzare il retraining eseguendo trainer_manager.py manualmente se vuoi.")

# ✅ 3. Seleziona la coppia da analizzare
selected_pair = select_pair()
print(f"\n Analisi per {selected_pair['binance']} / {selected_pair['coinbase']}...")
print()

# ✅ 4. Recupera i dati di mercato da tutti i fetcher
# dataframes = []

# Timeframe dinamico in base alla volatilità media stimata o coppia
# default_interval = "1m" if "BTC" in selected_pair["binance"] else "5m"
# print(f" Timeframe selezionato per Binance: {default_interval}")
# print()
# binance_df = get_binance_data(symbol=selected_pair["binance"], interval=default_interval)

# if binance_df is not None and not binance_df.empty:
#     dataframes.append(binance_df)

# coinbase_df = get_coinbase_data(symbol=selected_pair["coinbase"])
# if isinstance(coinbase_df, pd.DataFrame) and not coinbase_df.empty:
#     dataframes.append(coinbase_df)

# print(f" Simbolo Yahoo selezionato: {selected_pair.get('yahoo', selected_pair['coinbase'])}")
# print()
# yahoo_df = get_yahoo_data(symbol=selected_pair.get("yahoo", selected_pair["coinbase"]))
# if yahoo_df is not None and not yahoo_df.empty:
#     dataframes.append(yahoo_df)

# coingecko_symbol = selected_pair["coinbase"].split("-")[0].lower()
# coingecko_df = get_coingecko_data(symbol=coingecko_symbol, vs_currency="usd", days=1)
# if coingecko_df is not None and not coingecko_df.empty:
#     dataframes.append(coingecko_df)

# coincap_symbol = selected_pair["coinbase"].split("-")[0].lower()
# coincap_df = get_coincap_data(symbol=coincap_symbol)
# if coincap_df is not None and not coincap_df.empty:
#     dataframes.append(coincap_df)

# cryptocompare_df = get_cryptocompare_data()
# if cryptocompare_df is not None and not cryptocompare_df.empty:
#     dataframes.append(cryptocompare_df)

# 🧹 Normalizza timestamp per tutti i DataFrame
# for i in range(len(dataframes)):
#     if "timestamp" in dataframes[i].columns:
#         dataframes[i]["timestamp"] = pd.to_datetime(dataframes[i]["timestamp"], utc=True)
#         dataframes[i]["timestamp"] = dataframes[i]["timestamp"].dt.tz_localize(None)


# ✅ Combina i dataframe
# if not dataframes:
#     for i, df in enumerate(dataframes):
#         print(f" DataFrame #{i+1} – righe: {len(df)}, colonne: {list(df.columns)}")
#         print(df.head(2))  # Mostra i primi timestamp

#     print(" ERRORE: Nessun dato disponibile per questa coppia da nessun fetcher.")
#     print()
#     sys.exit(1)

# 🔁 Unione e media dei dati per timestamp
# df_combined = pd.concat(dataframes).sort_values("timestamp")
# ✨ Forza i tipi numerici per evitare problemi di aggregazione
# for col in ["open", "high", "low", "close", "volume"]:
#     df_combined[col] = pd.to_numeric(df_combined[col], errors="coerce")

# df_combined = df_combined.groupby("timestamp").agg({
#     "open": "mean",
#     "high": "mean",
#     "low": "mean",
#     "close": "mean",
#     "volume": "sum"  # volume si può sommare
# }).reset_index()

# ✅ Assegna manualmente il timeframe usato per Binance (già noto dai dati)
# === FISSO: usiamo "1m" perché i dati Binance sono già preparati con questo timeframe
default_interval = "1m"  # Valore fisso perché carichiamo da CSV con timeframe fisso

# ✅ Caricamento dati già aggiornati dal CSV locale
csv_path = f"E:/CODE/FOREX_CRYPTO_V2/data/binance_{selected_pair['binance']}.csv"
if not os.path.exists(csv_path):
    print(f" ERRORE: Il file {csv_path} non esiste.")
    sys.exit(1)

df = pd.read_csv(csv_path, parse_dates=["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

# Assicuriamoci di avere colonne corrette
required_cols = ["open", "high", "low", "close", "volume"]
if not all(col in df.columns for col in required_cols):
    print(" ERRORE: Colonne mancanti nei dati combinati.")
    sys.exit(1)

df = df.sort_values("timestamp").reset_index(drop=True)

print("\n🧾 Prime 2 righe del CSV caricato:")
print(df.head(2).to_string(index=False))
print()


# Simulazione di ritardo per emulare latenze reali (es: 30s)
# import time
# real_time_delay = 15  # secondi
# print()
# print(f" Simulazione delay di {real_time_delay}s per entry realistica...")
# time.sleep(real_time_delay)

from src.fetchers.binance import get_current_price

current_price = get_current_price(selected_pair["binance"])
print()
print(f" Live price per {selected_pair['binance']}: {current_price}")

if current_price is not None:
    try:
        # Usa direttamente il live price come entry per coerenza operativa
        entry_price = current_price
        print("⚙️ Entry price forzato al live per coerenza operativa.")

        price_diff = round(current_price - entry_price, 6)
        print()
        print(f"Prezzo attuale: {current_price}")
        print(f"Differenza tra prezzo attuale e storico: {price_diff:.4f}")
        output = {}
        output["live_price"] = current_price
        output["entry_vs_live_diff"] = round(price_diff, 2)
    except Exception as e:
        print(f"⚠️ Errore nel calcolo dell'entry price: {e}")

# ✅ 5. Esegui previsione
df.attrs["symbol"] = selected_pair["binance"]  # ad esempio ETHUSDT
trade_signal = predict_trade(df, live_price=current_price)
# === SL dinamico con trailing stop ===
from src.trailing_stop import adjust_sl
trade_signal = adjust_sl(trade_signal, current_price)

print()
print(f" Prezzo usato per calcolo TP/SL: {current_price:.4f} (live)")
print(f" Differenza vs. storico: {current_price - df['close'].iloc[-1]:.4f}")


if trade_signal is not None:
    if "motivo_blocco" in trade_signal:
        print()
        print(f"⚠️ Segnale bloccato per: {trade_signal['motivo_blocco'].upper()}")
        print("⚠️ TP e SL forniti SOLO a scopo informativo → esecuzione altamente sconsigliata.")
        print("➡️ Valori consigliati (uso manuale):")
    else:
        print()
        print("✅ Segnale AI attivo. Esecuzione possibile.")

    print(f" Azione: {trade_signal.get('azione', 'N/A')}")
    print(f" Take Profit: {trade_signal.get('TP', 'N/A')}")
    print(f" Stop Loss: {trade_signal.get('SL', 'N/A')}")
    print(f" Lotto consigliato: {trade_signal.get('lot_size', 'N/A')}")
    print(f" Entry price: {trade_signal.get('price_entry', 'N/A')}")
    print(f" Risk Score: {trade_signal.get('risk_score', 'N/A')}/3")
    

    # Loggare comunque una riga nel CSV per sapere che è stato bloccato
    log_row = {
        "timestamp": pd.Timestamp.now(),
        "symbol": selected_pair["coinbase"],
        "azione": "BLOCCATO",
        "tp": "N/A",
        "sl": "N/A",
        "unirate_confirma": None,
        "blockchair_confirma": None,
        "decisione": "BLOCCATO",
        "esito": "N/A",
        "rsi": df["rsi"].iloc[-1] if "rsi" in df.columns else "N/A",
        "tp_diff": "N/A",
        "sl_diff": "N/A",
        "price_entry": entry_price,
        "lot_size": trade_signal["lot_size"] if trade_signal and "lot_size" in trade_signal else "N/A",
        "pip_value": trade_signal["pip_value"] if trade_signal and "pip_value" in trade_signal else "N/A",
        "binance_timeframe": default_interval,
        # "simulated_delay": real_time_delay,
        "live_price": current_price,
        "entry_vs_live_diff": round(current_price - df['close'].iloc[-1], 4),
        "motivo_blocco": trade_signal.get("motivo_blocco", "") if trade_signal else "",

    }

    log_row['note_tp_sl'] = 'TP/SL OPERATIVI' if trade_signal and not trade_signal.get('motivo_blocco') else 'TP/SL INFORMATIVI - SEGNALI AD ALTO RISCHIO'
    print()
    print(f" Note TP/SL: {log_row['note_tp_sl']}")


# ✅ 6. Validazione esterna con UniRate
base_symbol = selected_pair["coinbase"].split("-")[0]
unirate_df = get_unirate_data(base=base_symbol)

# if unirate_df is not None and not unirate_df.empty:
    # Trova BTC → USDT se disponibile
#     usdt_row = unirate_df[unirate_df["symbol"] == "USDT"]

#     if not usdt_row.empty:
#         unirate_price = usdt_row["rate"].values[0]
#         print(f" UniRate BTC → USDT: {unirate_price:.2f}")

        # Applica filtro su segnale BUY (es: solo se prezzo > 85000)
#         soglia_dinamica = df["close"].tail(5).mean()
#         print(f" Soglia dinamica (media ultimi 5 close): {soglia_dinamica:.2f}")

#         if trade_signal and trade_signal["azione"] == "BUY" and unirate_price < soglia_dinamica:
#             print(" UniRate: BUY annullato, prezzo sotto soglia.")
#         else:
#             print(" UniRate: Segnale confermato.")
#     else:
#         print(" UniRate: Nessun tasso BTC → USDT trovato.")

    # Salva CSV per confronto
#     unirate_df.to_csv("E:\\CODE\\FOREX_CRYPTO_V2\\data\\unirate_BTC.csv", index=False)
# else:
#     print(" ERRORE: Nessun dato ricevuto da UniRate.")

# ✅ 7. Contesto fondamentale da Blockchair (on-chain)
blockchair_data = get_blockchair_data()

# if blockchair_data:
#     tx_count = blockchair_data["tx_count_24h"]
#     hashrate = blockchair_data["hashrate_24h"]

#     print(f" Blockchair BTC - TX last 24h: {tx_count}")
#     print(f" Hashrate 24h: {hashrate}")

#     soglia_tx_dinamica = int(df["close"].tail(5).mean() * 6)  # es. 6 transazioni per USD medio

#     print(f" Soglia dinamica TX (stimata): {soglia_tx_dinamica}")

#     if trade_signal and trade_signal["azione"] == "BUY" and tx_count < soglia_tx_dinamica:
#         print(" Blockchair: BUY annullato, TX sotto soglia dinamica.")
#     else:
#         print(" Blockchair: Segnale confermato.")
# else:
#     print(" Nessun dato disponibile da Blockchair.")

# ✅ 8. Decisione finale aggregata (UniRate + Blockchair)

# Flag di conferma da entrambi i validatori
unirate_confirma = None
blockchair_confirma = None

# UniRate
if unirate_df is not None and not unirate_df.empty:
    usdt_row = unirate_df[unirate_df["symbol"] == "USDT"]
    if not usdt_row.empty:
        unirate_price = usdt_row["rate"].values[0]
        soglia_dinamica = df["close"].tail(5).mean()
        unirate_confirma = unirate_price >= soglia_dinamica
        print()
        print(f" UniRate {base_symbol} → USDT: {unirate_price:.2f}")
        print(f" Soglia dinamica UniRate: {soglia_dinamica:.2f}")
        print(" UniRate: confermato." if unirate_confirma else "⚠️ UniRate: sotto soglia.")
        print()
    else:
        print(" UniRate: Nessun dato per BTC → USDT")
        print()

# Blockchair
if blockchair_data:
    tx_count = blockchair_data["tx_count_24h"]
    hashrate = blockchair_data["hashrate_24h"]
    soglia_tx_dinamica = int(df["close"].tail(5).mean() * 6)
    blockchair_confirma = tx_count >= soglia_tx_dinamica
    print(f" Blockchair TX 24h: {tx_count} / soglia: {soglia_tx_dinamica}")
    print(" Blockchair: confermato." if blockchair_confirma else " Blockchair: sotto soglia.")
    print()
else:
    print()
    print(" Nessun dato da Blockchair")
    print()

# Decisione finale
if trade_signal and trade_signal["azione"] == "BUY":
    if unirate_confirma and blockchair_confirma:
        print()
        print(" DECISIONE FINALE: BUY confermato ")
    elif unirate_confirma or blockchair_confirma:
        print()
        print(" DECISIONE FINALE: BUY da monitorare ")
    else:
        print("********************************************")
        print(" DECISIONE FINALE: BUY annullato ")

# === 9. Logging segnale ===
log_path = Path("logs")
log_path.mkdir(exist_ok=True)

log_file = log_path / "signal_log.csv"

log_row = {
    "timestamp": pd.Timestamp.now(),
    "symbol": selected_pair["coinbase"],
    "azione": trade_signal["azione"] if trade_signal else "N/A",
    "tp": trade_signal["TP"] if trade_signal else "N/A",
    "sl": trade_signal["SL"] if trade_signal else "N/A",
    "unirate_confirma": unirate_confirma,
    "blockchair_confirma": blockchair_confirma,
    "decisione": (
        "CONFERMATO " if unirate_confirma and blockchair_confirma else
        "DA MONITORARE " if unirate_confirma or blockchair_confirma else
        "ANNULLATO "
    ),
    "esito": trade_signal["esito"] if trade_signal and "esito" in trade_signal else "N/A",
    "rsi": trade_signal["rsi"] if trade_signal and "rsi" in trade_signal else "N/A",
    "tp_diff": trade_signal["tp_diff"] if trade_signal and "tp_diff" in trade_signal else "N/A",
    "sl_diff": trade_signal["sl_diff"] if trade_signal and "sl_diff" in trade_signal else "N/A",
    "price_entry": trade_signal["price_entry"] if trade_signal and "price_entry" in trade_signal else "N/A",
    "lot_size": trade_signal["lot_size"] if trade_signal and "lot_size" in trade_signal else "N/A",
    "pip_value": trade_signal["pip_value"] if trade_signal and "pip_value" in trade_signal else "N/A",
    "binance_timeframe": default_interval,
    # "simulated_delay": real_time_delay,
    "live_price": current_price,
    "entry_vs_live_diff": round(current_price - df['close'].iloc[-1], 4),
}

header = list(log_row.keys())
write_header = not log_file.exists()

with open(log_file, mode="a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=header)
    if write_header:
        writer.writeheader()
    writer.writerow(log_row)

#print(f" Segnale loggato in: {log_file}")

slippage_tollerato = 50  # USD massimo tollerabile tra entry e live
if trade_signal is not None:
    slippage_effettivo = abs(current_price - trade_signal.get("price_entry", current_price))

    if slippage_effettivo > slippage_tollerato:
        print(f"⛔️ SLIPPAGE TROPPO ALTO: {slippage_effettivo:.2f} USD > {slippage_tollerato} USD")
        print("❌ Segnale SCARTATO. Log NON registrato per evitare incoerenze operative.\n")
    else:
        with open(log_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            if write_header:
                writer.writeheader()
            writer.writerow(log_row)

        print("📥 Log registrato correttamente.")
else:
    print("❌ Nessun segnale valido generato (trade_signal = None). Log non scritto.\n")
    print()
    print("ℹ️ INFO DI MERCATO ATTUALE:")
    print(f" Live price: {current_price}")
    print(f" Entry close: {df['close'].iloc[-1]}")
    print(f" MA50: {df['ma50'].iloc[-1] if 'ma50' in df.columns else 'N/A'}")
    print(f" MA200: {df['ma200'].iloc[-1] if 'ma200' in df.columns else 'N/A'}")
    print(f" ADX: {df['adx'].iloc[-1] if 'adx' in df.columns else 'N/A'}")
    print(f" RSI: {df['rsi'].iloc[-1] if 'rsi' in df.columns else 'N/A'}")
    print("→ Probabile condizione laterale / volatilità anomala / filtro attivo.")


# === 10. Analisi automatica del log? ===
analizza = input(" Vuoi eseguire l'analisi dei segnali ora? (s/n): ").strip().lower()

if analizza == "s":
    try:
        from src.analyze_log import analizza_log
        analizza_log(log_file)
    except Exception as e:
        print(f" Errore nell'esecuzione dell'analisi: {e}")
