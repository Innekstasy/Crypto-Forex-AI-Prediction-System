import pandas as pd
from pathlib import Path
import sys

try:
    import matplotlib.pyplot as plt
    plt.rcParams["axes.unicode_minus"] = False  # evita problemi con simboli unicode
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

LOG_CSV = Path("E:/CODE/FOREX_CRYPTO_V2/logs/signal_log.csv")
LOG_TXT = Path("E:/CODE/FOREX_CRYPTO_V2/logs/analisi_log.txt")
IMG_DIR = LOG_TXT.parent  # stessa cartella dei log

def analizza_log(path):
    if not path.exists():
        print(f"[X] File non trovato: {path}")
        return

    df = pd.read_csv(path, encoding="utf-8", on_bad_lines="skip")
    original_len = sum(1 for _ in open(path, encoding="utf-8")) - 1  # -1 per intestazione
    read_len = len(df)
    skipped = original_len - read_len
    if skipped > 0:
        print(f" Saltate {skipped} righe malformate durante l'import del CSV.")

    output = []

    output.append(f" Segnali totali: {len(df)}\n")

    azioni = df["azione"].value_counts()
    azioni_pct = df["azione"].value_counts(normalize=True).round(2) * 100
    output.append("🪙 Tipi di segnali (BUY / SELL):")
    for az in azioni.index:
        output.append(f"   {az}: {azioni[az]} ({azioni_pct[az]:.1f}%)")
    output.append("")

    decisioni = df["decisione"].value_counts()
    decisioni_pct = df["decisione"].value_counts(normalize=True).round(2) * 100
    output.append(" Stato decisionale:")
    for dec in decisioni.index:
        output.append(f"   {dec}: {decisioni[dec]} ({decisioni_pct[dec]:.1f}%)")
    output.append("")

    asset = df["symbol"].value_counts()
    output.append(" Asset più presenti:")
    output.append(asset.to_string())
    output.append("")

    output.append(" Ultimi 5 segnali:")
    output.append(df.tail(5)[["timestamp", "symbol", "azione", "decisione"]].to_string(index=False))
    output.append("")

    # (Preparazione) Analisi su esito, se presente
    if "esito" in df.columns:
        risultati = df["esito"].value_counts()
        risultati_pct = df["esito"].value_counts(normalize=True).round(2) * 100
        output.append(" Esito operazioni:")
        if "azione" in df.columns:
            for action in ["BUY", "SELL"]:
                subset = df[(df["azione"] == action) & (df["esito"].isin(["TP", "SL"]))]
                if not subset.empty:
                    tp_count = (subset["esito"] == "TP").sum()
                    sl_count = (subset["esito"] == "SL").sum()
                    win_rate = tp_count / (tp_count + sl_count) * 100
                    output.append(f" Win rate {action}: {win_rate:.1f}% (TP: {tp_count}, SL: {sl_count})")
            output.append("")

        for res in risultati.index:
            output.append(f"   {res}: {risultati[res]} ({risultati_pct[res]:.1f}%)")
        output.append("")
    else:
        output.append("Nessun campo 'esito' trovato nel log. Aggiungilo per analisi futura.")

    # Scrittura su file .txt
    LOG_TXT.parent.mkdir(exist_ok=True)
    # RSI medio e distribuzione
    if "rsi" in df.columns:
            rsi_medio = df["rsi"].mean().round(2)
            rsi_min = df["rsi"].min().round(2)
            rsi_max = df["rsi"].max().round(2)
            output.append(f" RSI medio: {rsi_medio} (min: {rsi_min}, max: {rsi_max})")

            rsi_buy = df[df["azione"] == "BUY"]["rsi"]
            rsi_sell = df[df["azione"] == "SELL"]["rsi"]

            if not rsi_buy.empty:
                output.append(f"   RSI BUY: media {rsi_buy.mean().round(2)}, min {rsi_buy.min().round(2)}, max {rsi_buy.max().round(2)}")
            if not rsi_sell.empty:
                output.append(f"   RSI SELL: media {rsi_sell.mean().round(2)}, min {rsi_sell.min().round(2)}, max {rsi_sell.max().round(2)}")
            output.append("")
    else:
        output.append(" Campo 'rsi' non trovato nel log.")

    # Distanze TP/SL
    if "tp_diff" in df.columns and "sl_diff" in df.columns:
        tp_avg = df["tp_diff"].mean()
        sl_avg = df["sl_diff"].mean()
        output.append(f" Distanza media TP: {tp_avg:.4f} | SL: {sl_avg:.4f}")

        # Calcolo rapporto
        if sl_avg > 0:
            ratio = tp_avg / sl_avg
            output.append(f" Rapporto medio TP/SL: {ratio:.2f}")
            if "lot_size" in df.columns:
                lot_avg = df["lot_size"].mean()
                output.append(f" Lotto medio suggerito: {lot_avg:.2f}")
                output.append("")

            if "binance_timeframe" in df.columns:
                tf_counts = df["binance_timeframe"].value_counts()
                output.append(" Timeframe usati (Binance):")
                output.append(tf_counts.to_string())
                output.append("")

            if "simulated_delay" in df.columns:
                delay_medio = df["simulated_delay"].mean()
                output.append(f" Delay medio simulato: {delay_medio:.1f} sec")
                output.append("")

            if ratio < 2:
                output.append(" ATTENZIONE: il rapporto TP/SL è inferiore al 2:1 desiderato.")
        else:
            output.append("[X]Impossibile calcolare il rapporto TP/SL (SL = 0)")
        output.append("")
    else:
        output.append(" Distanze TP/SL non disponibili.")
    
    # Analisi della differenza tra prezzi storici e live
    if "live_diff" in df.columns:
        live_diff_mean = df["live_diff"].mean()
        live_diff_std = df["live_diff"].std()
        output.append(f" Differenza media prezzo storico/live: {live_diff_mean:.4f} (±{live_diff_std:.4f})")
        output.append("")

    with open(LOG_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(output))
    
    print()
    print(" Analisi completata. Risultato salvato in:")
    print(LOG_TXT)
    # === Aggiorna index.html con il contenuto del report
    try:
        template_path = IMG_DIR / "index.html"
        if template_path.exists():
            template_html = template_path.read_text(encoding="utf-8")
            report_txt = LOG_TXT.read_text(encoding="utf-8")
            html_filled = template_html.replace("{{REPORT_TXT}}", report_txt)
            template_path.write_text(html_filled, encoding="utf-8")
            print(f" index.html aggiornato con il report.")
            
            # Apri automaticamente nel browser
            import webbrowser
            webbrowser.open(str(template_path.resolve()))
        else:
            print(" index.html non trovato nella cartella log.")
    except Exception as e:
        print(f" Errore durante aggiornamento/apertura index.html: {e}")

    # Grafici opzionali
    if MATPLOTLIB_AVAILABLE:
        try:
            # Pulizia simboli Unicode che possono causare errori nei grafici
            df["decisione"] = df["decisione"].astype(str).str.replace("❌", "X")
            plt.figure(figsize=(10, 4))
            decisioni.plot(kind="bar", title="Decisioni finali")
            plt.ylabel("Conteggio")
            plt.tight_layout()
            plt.savefig(IMG_DIR / "decisioni_finali.png")
            plt.close()


            asset.head(10).plot(kind="bar", title="Top 10 Asset per segnali")
            plt.ylabel("Frequenza")
            plt.tight_layout()
            plt.savefig(IMG_DIR / "top_asset.png")
            plt.close()
            if "rsi" in df.columns:
                plt.figure(figsize=(8, 4))
                df["rsi"].hist(bins=20)
                plt.title("Distribuzione RSI")
                plt.xlabel("RSI")
                plt.ylabel("Frequenza")
                plt.tight_layout()
                plt.savefig(IMG_DIR / "rsi_distribution.png")
                plt.close()

            if "tp_diff" in df.columns and "sl_diff" in df.columns:
                plt.figure(figsize=(6, 4))
                plt.scatter(df["tp_diff"], df["sl_diff"], alpha=0.6)
                plt.xlabel("TP diff")
                plt.ylabel("SL diff")
                plt.title("TP vs SL distance")
                plt.grid(True)
                plt.tight_layout()
                plt.savefig(IMG_DIR / "tp_vs_sl.png")
                plt.close()

        except Exception as e:
            print(f" Errore nella generazione dei grafici: {e}")
    else:
        print(" matplotlib non disponibile: i grafici sono stati saltati.")

if __name__ == "__main__":
    analizza_log(LOG_CSV)
