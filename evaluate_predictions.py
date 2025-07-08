import os
import pandas as pd
from datetime import datetime, timedelta

DATA_DIR = "E:/CODE/FOREX_CRYPTO_V2/data"
LOG_DIR = "E:/CODE/FOREX_CRYPTO_V2/logs/eval_ai"
os.makedirs(LOG_DIR, exist_ok=True)

SIGNAL_LOG = "E:/CODE/FOREX_CRYPTO_V2/logs/signal_log.csv"
RESULT_CSV = os.path.join(LOG_DIR, "evaluated_signals.csv")
HTML_REPORT = os.path.join(LOG_DIR, "index.html")

# Parametri
FINESTRA_MINUTI = 30

def carica_dati_signal():
    righe_valide = []
    righe_saltate = 0
    with open(SIGNAL_LOG, "r", encoding="utf-8") as f:
        for i, riga in enumerate(f.readlines()):
            campi = riga.strip().split(",")
            if i == 0 and "timestamp" in campi[0].lower():
                continue  # salta intestazione
            if len(campi) < 5:
                continue  # riga incompleta
            try:
                timestamp = pd.to_datetime(campi[0], errors="coerce")
                symbol = campi[1].strip()
                azione = campi[2].strip()
                if campi[3] in ['N/A', '', None] or campi[4] in ['N/A', '', None]:
                    tp = sl = None
                else:
                    tp = float(campi[3])
                    sl = float(campi[4])

                righe_valide.append({
                    "timestamp": timestamp,
                    "symbol": symbol,
                    "azione": azione,
                    "tp": tp,
                    "sl": sl
                })
            except Exception as e:
                righe_saltate += 1
                print(f"❌ Riga {i+1} saltata: {e}")
                with open(os.path.join(LOG_DIR, "invalid_signals.csv"), 'a', encoding='utf-8') as f_log:
                    f_log.write(f"{campi[0]},{campi[1]},{campi[2]},{campi[3]},{campi[4]}\n")
                continue

    df = pd.DataFrame(righe_valide)
    print(f"📥 Segnali caricati: {len(df)} righe da {SIGNAL_LOG}")
    print(f"⚠️ Righe saltate per errore: {righe_saltate}")
    return df

def carica_dati_prezzo(symbol):
    csv_file = os.path.join(DATA_DIR, f"binance_{symbol}.csv")
    if not os.path.exists(csv_file):
        return pd.DataFrame()
    df = pd.read_csv(csv_file, parse_dates=["timestamp"])
    return df

def valuta_segnale(row, df_prezzo):
    ts_inizio = row["timestamp"]
    ts_fine = ts_inizio + timedelta(minutes=FINESTRA_MINUTI)
    df_finestra = df_prezzo[(df_prezzo["timestamp"] > ts_inizio) & (df_prezzo["timestamp"] <= ts_fine)]

    if df_finestra.empty:
        return "NESSUNO"

    azione = row["azione"]
    tp = row["tp"]
    sl = row["sl"]

    alti = df_finestra["high"]
    bassi = df_finestra["low"]

    if azione == "BUY":
        if any(alti >= tp):
            return "TP"
        elif any(bassi <= sl):
            return "SL"
    elif azione == "SELL":
        if any(bassi <= tp):
            return "TP"
        elif any(alti >= sl):
            return "SL"

    return "NESSUNO"

def genera_html(df, market_summary):
    df_val = df[df["status"] == "VALIDATO"]
    df_attesa = df[df["status"].str.strip().str.startswith("IN ATTESA")]

    gruppi = df_val.groupby(["azione", "esito"]).size().unstack(fill_value=0)
    gruppi["precision"] = gruppi.apply(lambda r: round(r.get("TP", 0) / (r.get("TP", 0) + r.get("SL", 0) + 1e-9) * 100, 2), axis=1)
    gruppi["recall"] = gruppi.apply(lambda r: round(r.get("TP", 0) / df_val[df_val["azione"] == r.name]["esito"].count() * 100, 2), axis=1)

    # Calcolo per tabella "ultimi segnali"
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df_recent = df.dropna(subset=["timestamp", "symbol", "azione", "tp", "sl"]).copy()
    df_recent = df_recent.sort_values("timestamp", ascending=False).head(10)
    df_recent["valutabile_da"] = df_recent["timestamp"] + timedelta(minutes=FINESTRA_MINUTI)
    ora_attuale = datetime.now()
    df_recent["tempo_residuo"] = df_recent["valutabile_da"].apply(lambda x: max(0, int((x - ora_attuale).total_seconds() // 60)))
    df_recent["valutabile_da"] = df_recent["valutabile_da"].dt.strftime("%H:%M:%S")

    html = [
        """
        <html>
        <head>
            <title>Valutazione AI</title>
            <style>
                body { font-family: sans-serif; margin: 40px; background: #f5f5f5; }
                h1, h2 { color: #333; }
                table { border-collapse: collapse; margin: 20px 0; width: 90%; background: white; }
                th, td { padding: 10px 15px; border: 1px solid #ddd; text-align: center; }
                th { background-color: #f0f0f0; }
                tr:nth-child(even) { background-color: #fafafa; }
                .tp { background-color: #c8e6c9; }
                .sl { background-color: #ffcdd2; }
                .none { background-color: #eeeeee; }
            </style>
        </head>
        <body>
        """,
        "<h1>📊 Risultati valutazione predizioni AI</h1>",
        "<h2>✅ Valutati (con TP/SL)</h2>",
        gruppi.to_html(border=0, justify='center'),
        f"""
        <p><b>Totale segnali:</b> {len(df)}<br>
        <b>Validati:</b> {len(df_val)}<br>
        <b>In attesa:</b> {len(df_attesa)}<br></p>
        <hr><br>
        """
    ]
    # Blocco riepilogo visivo TP vs SL
    tp_count = df_val[df_val["esito"] == "TP"].shape[0]
    sl_count = df_val[df_val["esito"] == "SL"].shape[0]
    totale_val = tp_count + sl_count
    percent_tp = round(tp_count / totale_val * 100, 2) if totale_val else 0
    percent_sl = round(sl_count / totale_val * 100, 2) if totale_val else 0

    html.append(f"""
    <h2>💰 Rendimento operativo stimato</h2>
    <p><b>Operazioni valutate:</b> {totale_val}</p>
    <table>
        <tr><th>Esito</th><th>Conteggio</th><th>Percentuale</th></tr>
        <tr class="tp"><td>TP</td><td>{tp_count}</td><td>{percent_tp}%</td></tr>
        <tr class="sl"><td>SL</td><td>{sl_count}</td><td>{percent_sl}%</td></tr>
    </table>
    """)

    # Sezione MARKET STATUS

    if market_summary['rsi_medio'] is not None:
        rsi_medio_str = f"{market_summary['rsi_medio']:.2f}"
    else:
        rsi_medio_str = "N/A"

    html.append(f"""
    <p><b>Trend MA50 vs MA200:</b> {market_summary['trend']} (MA50={market_summary['ma50']:.2f} / MA200={market_summary['ma200']:.2f})<br>
    <b>RSI medio ultimi 50 segnali:</b> {rsi_medio_str} <br>
    <b>% TP ultimi 50 BUY:</b> {market_summary['pct_buy']:.2f}% <br>
    <b>% TP ultimi 50 SELL:</b> {market_summary['pct_sell']:.2f}% <br>
    <b>RACCOMANDAZIONE:</b> {market_summary['raccomandazione']} <br>
    </p>
    <hr>
    """)
    
    # Rendimento per risk_score
    if "risk_score" in df.columns:
        risk_summary = (
            df[df["esito"].isin(["TP", "SL", "NESSUNO"])]
            .groupby(["risk_score", "esito"])
            .size()
            .unstack(fill_value=0)
        )

        risk_summary["Totale"] = risk_summary.sum(axis=1)
        risk_summary["Winrate %"] = (risk_summary.get("TP", 0) / risk_summary["Totale"] * 100).round(2)
        risk_summary = risk_summary.reset_index()
        risk_summary.columns.name = None

        html.append("<h2>🎯 Rendimento per RISK SCORE</h2>")
        html.append(risk_summary.to_html(index=False, border=0, justify='center'))

    # Blocco storico giornaliero
    df_val = df_val.copy()
    df_val["data"] = df_val["timestamp"].dt.date
    storico = (
        df_val[df_val["esito"].isin(["TP", "SL"])]
        .groupby(["data", "esito"])
        .size()
        .unstack(fill_value=0)
        .sort_index(ascending=False)
        .head(10)
    )
    storico["Totale"] = storico.sum(axis=1)
    storico["Precision"] = (storico["TP"] / storico["Totale"] * 100).round(2)
    storico = storico.reset_index()
    storico.columns.name = None

    html.append("<h2>📅 Storico rendimento (ultimi 10 giorni)</h2>")
    html.append(storico[["data", "TP", "SL", "Precision"]].to_html(index=False, border=0, justify='center'))

    if not df_attesa.empty:
        html.append("<h2>⏳ Segnali ancora in attesa</h2>")
        html.append(df_attesa[["timestamp", "symbol", "azione", "tp", "sl", "status"]].to_html(index=False, border=0, justify='center'))

    # ✅ Nuova sezione: ultimi segnali
    html.append("<hr><h2>📋 Ultimi segnali registrati</h2>")
    html.append(df_recent[["timestamp", "symbol", "azione", "tp", "sl", "status", "valutabile_da", "tempo_residuo"]].to_html(index=False, border=0, justify='center'))

    html.append("</body></html>")

    with open(HTML_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(html))

def calcola_market_status(df_signal, df_price):
    print("\n************* MARKET STATUS *************")

    rsi_medio = None  # inizializza SEMPRE la variabile!

    # Calcolo MA50 e MA200 sul df_price
    df_price["ma50"] = df_price["close"].rolling(window=50).mean()
    df_price["ma200"] = df_price["close"].rolling(window=200).mean()

    last_ma50 = df_price["ma50"].iloc[-1]
    last_ma200 = df_price["ma200"].iloc[-1]

    if last_ma50 > last_ma200:
        trend = "BULLISH"
    elif last_ma50 < last_ma200:
        trend = "BEARISH"
    else:
        trend = "LATERALE"

    print(f"Trend MA50 vs MA200: {trend} (MA50={last_ma50:.2f} / MA200={last_ma200:.2f})")

    # Calcolo RSI medio ultimi 50 segnali
    if "rsi" in df_signal.columns:
        rsi_medio = df_signal["rsi"].dropna().tail(50).mean()
        print(f"RSI medio ultimi 50 segnali: {rsi_medio:.2f}" if rsi_medio is not None else "RSI medio ultimi 50 segnali: N/A")
    else:
        rsi_medio = None
        print("RSI medio ultimi 50 segnali: N/A (colonna RSI non presente)")

    # % TP su ultimi 50 BUY
    df_buy = df_signal[df_signal["azione"] == "BUY"].tail(50)
    n_buy = len(df_buy)
    tp_buy = df_buy[df_buy["esito"] == "TP"].shape[0]
    pct_buy = (tp_buy / n_buy * 100) if n_buy > 0 else 0
    print(f"% TP ultimi 50 BUY: {pct_buy:.2f}% ({tp_buy}/{n_buy})")

    # % TP su ultimi 50 SELL
    df_sell = df_signal[df_signal["azione"] == "SELL"].tail(50)
    n_sell = len(df_sell)
    tp_sell = df_sell[df_sell["esito"] == "TP"].shape[0]
    pct_sell = (tp_sell / n_sell * 100) if n_sell > 0 else 0
    print(f"% TP ultimi 50 SELL: {pct_sell:.2f}% ({tp_sell}/{n_sell})")

    # Raccomandazione finale
    raccomandazione = ""
    if trend == "BULLISH" and pct_buy > pct_sell:
        raccomandazione = "OPERARE SOLO BUY"
    elif trend == "BEARISH" and pct_sell > pct_buy:
        raccomandazione = "OPERARE SOLO SELL"
    else:
        raccomandazione = "STARE FUORI"

    market_summary = {
        "trend": trend,
        "ma50": last_ma50,
        "ma200": last_ma200,
        "rsi_medio": rsi_medio if "rsi_medio" in locals() else None,
        "pct_buy": pct_buy,
        "pct_sell": pct_sell,
        "raccomandazione": raccomandazione
    }
    
    print(f"→ RACCOMANDAZIONE: {raccomandazione}")
    print("*****************************************\n")

    return market_summary

def main():
    df_signal = carica_dati_signal()
    df_signal["timestamp"] = pd.to_datetime(df_signal["timestamp"], errors="coerce")
#    df_signal["symbol"] = df_signal["symbol"].str.replace("USDT", "")
    esiti = []
    stati = []

    ora_corrente = datetime.utcnow()

    cache = {}

    for i, row in df_signal.iterrows():
        # Rende compatibile sia BTCUSD che BTC-USD
        symbol_base = row["symbol"].replace("-", "")
        if symbol_base.endswith("USD"):
            symbol = symbol_base[:-3] + "USDT"
        else:
            symbol = symbol_base
        if symbol not in cache:
            print(f"📂 Caricamento file: binance_{symbol}.csv")
            df_price = carica_dati_prezzo(symbol)
            cache[symbol] = df_price
        else:
            df_price = cache[symbol]
        ts_inizio = row["timestamp"]
        minuti_passati = (ora_corrente - ts_inizio).total_seconds() / 60

        if pd.isna(row["azione"]) or pd.isna(row["tp"]) or pd.isna(row["sl"]):
            esiti.append("NESSUNO")
            stati.append("DATI INCOMPLETI (ma TP/SL presenti)" if not pd.isna(row["tp"]) and not pd.isna(row["sl"]) else "DATI INCOMPLETI")
            continue

        if minuti_passati < FINESTRA_MINUTI:
            esiti.append("NESSUNO")
            stati.append(f"IN ATTESA ({int(FINESTRA_MINUTI - minuti_passati)} min)")
            continue

        if df_price.empty:
            esiti.append("NESSUNO")
            stati.append("DATI MANCANTI")
            continue

        esito = valuta_segnale(row, df_price)
        esiti.append(esito)
        stati.append("VALIDATO")

    df_signal["esito"] = esiti
    df_signal["status"] = stati

    # Filtro segnale validi e coerenti prima di generare l’HTML
    df_validi = df_signal.dropna(subset=["timestamp", "symbol", "azione", "tp", "sl"])
    df_validi = df_validi[df_validi["timestamp"] <= datetime.now()]
    df_validi = df_validi.sort_values("timestamp")

    df_validi.to_csv(RESULT_CSV, index=False)
    
    # Calcolo Market Status sul primo symbol disponibile (esempio BTCUSDT)
    symbol_base = df_signal["symbol"].dropna().unique()[0].replace("-", "")
    if symbol_base.endswith("USD"):
        symbol = symbol_base[:-3] + "USDT"
    else:
        symbol = symbol_base
    df_price = carica_dati_prezzo(symbol)

    # calcola_market_status(df_signal, df_price)
    market_summary = calcola_market_status(df_signal, df_price)

    genera_html(df_validi, market_summary)

    print(f"✅ Analisi completata. Risultati salvati in: {RESULT_CSV}")
    print(f"🌐 Dashboard: {HTML_REPORT}")
    ultimi = df_signal.sort_values("timestamp", ascending=False).head(3)[["timestamp", "symbol", "azione", "status"]]
    print("\n🧾 Ultimi segnali analizzati:\n", ultimi.to_string(index=False))
    df_oggi = df_signal[df_signal["timestamp"].dt.date == datetime.today().date()]
    print(f"🟢 Segnali registrati oggi: {len(df_oggi)}")
    print(df_oggi[["timestamp", "symbol", "azione", "status"]].tail(5).to_string(index=False))


import webbrowser
webbrowser.open("file://" + os.path.abspath(HTML_REPORT))

if __name__ == "__main__":
    main()


 
