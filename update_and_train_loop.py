import time
import subprocess
import sys
import os
import pandas as pd
import json
import matplotlib.pyplot as plt

STATE_FILE = "last_training_state.json"
DATA_DIR = "E:/CODE/FOREX_CRYPTO_V2/data"
LOG_DIR = "E:/CODE/FOREX_CRYPTO_V2/logs"
SYMBOLS = [
    "BTCUSDT",
    # "ETHUSDT",
    # "XRPUSDT",
    # "ADAUSDT",
    # "SOLUSDT"
]
MIN_NEW_ROWS = 2000

def get_current_row_count(symbol):
    keyword = "binance_" + symbol
    files = [f for f in os.listdir(DATA_DIR) if keyword in f]
    if not files:
        return 0
    df = pd.read_csv(os.path.join(DATA_DIR, files[0]))
    return len(df)

def load_last_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def generate_daily_row_report():
    report_dir = os.path.join(LOG_DIR, "daily_reports")
    os.makedirs(report_dir, exist_ok=True)

    html_path = os.path.join(report_dir, "index.html")
    html_lines = [
        "<html><head><title>Report Giornaliero Dati</title></head><body>",
        "<h1>Grafici righe per giorno</h1>"
    ]

    print("📈 Generazione report grafico per ogni CSV...")

    for file in os.listdir(DATA_DIR):
        if file.endswith(".csv") and file != "signals.csv":
            path = os.path.join(DATA_DIR, file)
            try:
                df = pd.read_csv(path, low_memory=False)
                if "timestamp" not in df.columns:
                    continue
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
                df.dropna(subset=["timestamp"], inplace=True)
                df["date"] = df["timestamp"].dt.date
                daily_counts = df.groupby("date").size()

                plt.figure(figsize=(10, 4))
                daily_counts.plot(kind="bar", title=f"{file}", ylabel="Righe", xlabel="Data")
                plt.subplots_adjust(bottom=0.2)

                img_name = f"{file.replace('.csv','')}.png"
                img_path = os.path.join(report_dir, img_name)
                plt.savefig(img_path)
                plt.close()

                html_lines.append(f"<div><h3>{file}</h3><img src='{img_name}' style='max-width:800px;'></div>")
                print(f"✅ Grafico salvato: {img_path}")
            except Exception as e:
                print(f"⚠️ Errore su {file}: {e}")

    html_lines.append("</body></html>")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    print(f"📄 Report HTML generato: {html_path}")

def clean_signals_csv():
    file_path = os.path.join(LOG_DIR, "signals.csv")
    if not os.path.exists(file_path):
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return

    header = lines[0].strip().split(",")
    expected_cols = len(header)

    cleaned_lines = [lines[0]]
    corrupted = 0

    for line in lines[1:]:
        if line.count(",") == expected_cols - 1:
            cleaned_lines.append(line)
        else:
            corrupted += 1

    if corrupted:
        backup_path = file_path.replace(".csv", "_backup.csv")
        os.rename(file_path, backup_path)
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(cleaned_lines)
        print(f"🧹 signals.csv ripulito ({corrupted} righe rimosse). Backup creato: {backup_path}")
    else:
        print("✅ signals.csv integro. Nessuna modifica necessaria.")

def run_loop():
    while True:
        print("\n⏳ Avvio ciclo: fetch + (eventuale) training...")

        subprocess.call([sys.executable, "update_all_fetchers.py"])

        clean_signals_csv()

        current_state = load_last_state()
        updated = False

        symbol_updates = {
            symbol: get_current_row_count(symbol)
            for symbol in SYMBOLS
        }

        for symbol, current_size in symbol_updates.items():
            last_size = current_state.get(symbol, 0)
            print(f"📊 {symbol}: {current_size} righe (precedente: {last_size})")
            updated = True
            current_state[symbol] = current_size

        if updated:
            print("🧠 Dati sufficienti per almeno una coppia. Avvio training...")
            subprocess.call([sys.executable, "trainer_manager.py"])
            save_state(current_state)
        else:
            print("⏸️ Nessuna coppia ha abbastanza dati nuovi. Training saltato.")

        generate_daily_row_report()

        countdown = 30 * 60
        print("\n⏱️ Attendo 30 minuti prima del prossimo ciclo:")
        for i in range(countdown, 0, -1):
            mins, secs = divmod(i, 60)
            time.sleep(1)
            print(f"\r⌛ {mins:02d}:{secs:02d} min", end="", flush=True)
        print()

if __name__ == "__main__":
    run_loop()
