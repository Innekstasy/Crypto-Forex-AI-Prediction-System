import os
import pandas as pd
from datetime import datetime, timedelta

LOG_DIR = "logs"
DATA_DIR = "data"
OUTPUT_DIR = "logs/eval_ai"

os.makedirs(OUTPUT_DIR, exist_ok=True)

FINESTRA_MINUTI = 30  # come standard

signal_path = os.path.join(LOG_DIR, "signal_log.csv")
df_signals = pd.read_csv(signal_path, sep=",", on_bad_lines='skip')
if "motivo_blocco" not in df_signals.columns:
    df_signals["motivo_blocco"] = ""

# Filtra solo i blocchi Wyckoff
df_blocked = df_signals[df_signals["motivo_blocco"] == "wyckoff"].copy()

# Filtra anche i breakout Wyckoff Fase 2
df_breakout = df_signals[df_signals["motivo_blocco"] == "wyckoff_breakout"].copy()

results_breakout = []

for _, row in df_breakout.iterrows():
    coppia = row["coppia"]
    azione = row["azione"]
    entry = float(row["price_entry"])
    tp = float(row["TP"])
    sl = float(row["SL"])
    timestamp = pd.to_datetime(row["data"])

    file_price = f"binance_{coppia}.csv"
    price_path = os.path.join(DATA_DIR, file_price)

    if not os.path.exists(price_path):
        continue

    df_price = pd.read_csv(price_path)
    df_price["timestamp"] = pd.to_datetime(df_price["timestamp"])
    df_window = df_price[(df_price["timestamp"] >= timestamp) &
                         (df_price["timestamp"] <= timestamp + timedelta(minutes=FINESTRA_MINUTI))]

    esito = "NESSUNO"
    for _, pr in df_window.iterrows():
        high = pr["high"]
        low = pr["low"]
        if azione == "BUY":
            if high >= tp:
                esito = "TP"
                break
            if low <= sl:
                esito = "SL"
                break
        else:  # SELL
            if low <= tp:
                esito = "TP"
                break
            if high >= sl:
                esito = "SL"
                break

    results_breakout.append({
        "data": row["data"],
        "coppia": coppia,
        "azione": azione,
        "esito": esito,
        "price_entry": entry,
        "TP": tp,
        "SL": sl
    })

df_result_breakout = pd.DataFrame(results_breakout)
out_path_breakout = os.path.join(OUTPUT_DIR, "wyckoff_breakout_analysis.csv")
df_result_breakout.to_csv(out_path_breakout, index=False)

print()
print(f"Totale segnali Wyckoff FASE 2 (BREAKOUT) analizzati: {len(df_result_breakout)}")
print(f"Report salvato in: {out_path_breakout}")


results = []

for _, row in df_blocked.iterrows():
    coppia = row["coppia"]
    azione = row["azione"]
    entry = float(row["price_entry"])
    tp = float(row["TP"])
    sl = float(row["SL"])
    timestamp = pd.to_datetime(row["data"])

    file_price = f"binance_{coppia}.csv"
    price_path = os.path.join(DATA_DIR, file_price)

    if not os.path.exists(price_path):
        continue

    df_price = pd.read_csv(price_path)
    df_price["timestamp"] = pd.to_datetime(df_price["timestamp"])
    df_window = df_price[(df_price["timestamp"] >= timestamp) &
                         (df_price["timestamp"] <= timestamp + timedelta(minutes=FINESTRA_MINUTI))]

    esito = "NESSUNO"
    for _, pr in df_window.iterrows():
        high = pr["high"]
        low = pr["low"]
        if azione == "BUY":
            if high >= tp:
                esito = "TP"
                break
            if low <= sl:
                esito = "SL"
                break
        else:  # SELL
            if low <= tp:
                esito = "TP"
                break
            if high >= sl:
                esito = "SL"
                break

    results.append({
        "data": row["data"],
        "coppia": coppia,
        "azione": azione,
        "esito": esito,
        "price_entry": entry,
        "TP": tp,
        "SL": sl
    })

df_result = pd.DataFrame(results)
out_path = os.path.join(OUTPUT_DIR, "wyckoff_blocked_analysis.csv")
df_result.to_csv(out_path, index=False)

# Riepilogo
tot = len(df_result)

if tot > 0:
    tp = (df_result["esito"] == "TP").sum()
    sl = (df_result["esito"] == "SL").sum()
    nessuno = (df_result["esito"] == "NESSUNO").sum()
else:
    tp = sl = nessuno = 0

print(f"Totale segnali Wyckoff BLOCCATI analizzati: {tot}")
print(f"TP virtuali: {tp}")
print(f"SL virtuali: {sl}")
print(f"Nessun esito: {nessuno}")
print(f"Report salvato in: {out_path}")

# Genera pagina HTML wyckoff
html_path = os.path.join(OUTPUT_DIR, "wyckoff.html")

html_content = f"""
<html>
<head>
<title>Report Wyckoff</title>
<meta charset="UTF-8">
<style>
body {{ font-family: Arial; margin: 20px; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 40px; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
th {{ background-color: #f2f2f2; }}
h2 {{ color: #333; }}
</style>
</head>
<body>
<h1>Valutazione Wyckoff</h1>

<h2>Segnali BLOCCATI</h2>
<p>Totale: {tot} | TP: {tp} | SL: {sl} | NESSUNO: {nessuno}</p>
<a href='wyckoff_blocked_analysis.csv'>Download CSV BLOCCATI</a>
<br><br>
{df_result.to_html(index=False)}

<h2>Segnali FASE 2 (BREAKOUT)</h2>
<p>Totale: {len(df_result_breakout)}</p>
<a href='wyckoff_breakout_analysis.csv'>Download CSV BREAKOUT</a>
<br><br>
{df_result_breakout.to_html(index=False)}

</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Pagina HTML generata: {html_path}")
