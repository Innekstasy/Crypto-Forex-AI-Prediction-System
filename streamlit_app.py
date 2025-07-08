import streamlit as st
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Segnali", layout="wide")

# === Caricamento file
LOG_PATH = Path("E:/CODE/FOREX_CRYPTO_V2/logs/signal_log.csv")

if not LOG_PATH.exists():
    st.error(f"File non trovato: {LOG_PATH}")
    st.stop()

df = pd.read_csv(LOG_PATH, encoding="utf-8", on_bad_lines="skip")
st.warning("⚠️ Alcune righe malformate sono state ignorate durante il caricamento del file.")

st.title("📊 Dashboard Segnali Trading")
st.markdown("---")

# === Filtri
col1, col2 = st.columns(2)

with col1:
    asset_selezionato = st.selectbox("Filtra per asset", ["Tutti"] + sorted(df["symbol"].unique().tolist()))

with col2:
    azione_selezionata = st.selectbox("Filtra per azione", ["Tutte", "BUY", "SELL"])

# === Applica filtri
df_filtrato = df.copy()

if asset_selezionato != "Tutti":
    df_filtrato = df_filtrato[df_filtrato["symbol"] == asset_selezionato]

if azione_selezionata != "Tutte":
    df_filtrato = df_filtrato[df_filtrato["azione"] == azione_selezionata]

# === Tabella
st.subheader("🧾 Segnali filtrati")
st.dataframe(df_filtrato.sort_values(by="timestamp", ascending=False), use_container_width=True)

# === Statistiche
st.markdown("---")
st.subheader("📈 Statistiche")

col1, col2, col3 = st.columns(3)

col4, col5 = st.columns(2)

with col4:
    if "binance_timeframe" in df_filtrato.columns:
        tf_mode = df_filtrato["binance_timeframe"].mode()[0]
        st.metric("Timeframe più usato", tf_mode)

with col5:
    if "simulated_delay" in df_filtrato.columns:
        delay_medio = df_filtrato["simulated_delay"].mean()
        st.metric("Delay simulato medio (s)", f"{delay_medio:.0f}")

with col1:
    st.metric("Segnali totali", len(df_filtrato))

with col2:
    if "TP" in df_filtrato["esito"].values or "SL" in df_filtrato["esito"].values:
        subset = df_filtrato[df_filtrato["esito"].isin(["TP", "SL"])]
        tp = (subset["esito"] == "TP").sum()
        sl = (subset["esito"] == "SL").sum()
        total = tp + sl
        winrate = (tp / total) * 100 if total > 0 else 0
        st.metric("Win Rate", f"{winrate:.1f}%")
    else:
        st.write("Nessun dato per calcolo winrate")

with col3:
    rsi_media = df_filtrato["rsi"].mean() if "rsi" in df_filtrato else None
    st.metric("RSI medio", f"{rsi_media:.1f}" if rsi_media else "N/A")
    # === Rapporto medio TP/SL
    if "tp_diff" in df_filtrato.columns and "sl_diff" in df_filtrato.columns:
        tp_avg = df_filtrato["tp_diff"].mean()
        sl_avg = df_filtrato["sl_diff"].mean()

        if sl_avg > 0:
            ratio = tp_avg / sl_avg
            colore = "green" if ratio >= 2 else "orange"
            st.metric("📐 Rapporto medio TP/SL", f"{ratio:.2f}")
            if "lot_size" in df_filtrato.columns:
                lot_avg = df_filtrato["lot_size"].mean()
                st.metric("📦 Lotto medio suggerito", f"{lot_avg:.2f}")

            if ratio < 2:
                st.warning("⚠️ Il rapporto TP/SL è inferiore al 2:1 desiderato.")
        else:
            st.error("❌ SL medio nullo: impossibile calcolare il rapporto TP/SL.")

if "live_diff" in df_filtrato.columns:
    diff_media = df_filtrato["live_diff"].mean()
    st.metric("Delta medio prezzo storico/live", f"{diff_media:.4f}")

# === Grafico RSI
if "rsi" in df_filtrato.columns:
    st.markdown("### 📉 Distribuzione RSI")
    fig, ax = plt.subplots(figsize=(8, 3))
    df_filtrato["rsi"].hist(bins=20, ax=ax)
    ax.set_xlabel("RSI")
    ax.set_ylabel("Frequenza")
    ax.grid(True)
    st.pyplot(fig)

# === Footer
st.markdown("---")
st.caption("© 2025 - Sistema Trading Personalizzato")
 
