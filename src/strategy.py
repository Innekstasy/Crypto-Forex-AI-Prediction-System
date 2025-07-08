import os
import numpy as np
import pandas as pd
from joblib import load
from src.training import train_model
from src.fetchers.binance import get_binance_data
from src.wyckoff_filter import is_in_consolidation
from src.wyckoff_filter_breakout import is_breakout
from src.utils import check_tp_sl, calculate_risk_score


MODEL_PATH = "E:\\CODE\\FOREX_CRYPTO_V2\\models"
MODEL_FILE = os.path.join(MODEL_PATH, "trading_model.pkl")
SCALER_FILE = os.path.join(MODEL_PATH, "scaler.pkl")

def load_model():
    """Carica il modello AI se esiste, altrimenti lo riaddestra."""
    if not os.path.exists(MODEL_FILE) or not os.path.exists(SCALER_FILE):
        print()
        print(" Modello AI non trovato. Tentativo di riaddestramento...")

        df_train = get_binance_data(symbol="BTCUSDT", interval="5m", limit=500)
        if df_train is not None and not df_train.empty:
            success = train_model(df_train)
            if success:
                print()
                print(" Modello AI riaddestrato con successo!")
                
            else:
                print()
                print(" ERRORE: Fallimento nell'addestramento automatico.")
                
                return None, None

        else:
            print()
            print(" ERRORE: Nessun dato disponibile per l'addestramento.")
            
            return None, None

    try:
        model = load(MODEL_FILE)
        scaler = load(SCALER_FILE)
        return model, scaler
    except Exception as e:
        print()
        print(f" ERRORE nel caricamento del modello: {e}")
        
        return None, None

# Carica il modello
model, scaler = load_model()

def predict_trade(df, live_price=None):
    
    """Genera un segnale di trading basato sul modello AI."""
    if model is None or scaler is None:
        print()
        print(" ERRORE: Il modello AI non è stato caricato correttamente.")
        
        return None

    try:
        df["returns"] = df["close"].pct_change()
        df.dropna(inplace=True)
        from src.indicators import calculate_rsi
        df = calculate_rsi(df)
        # Filtro direzionale: se RSI troppo neutro, salta il trade
        rsi_val = df["rsi"].iloc[-1]
        if 45 < rsi_val < 55:
            print()
            print(f" RSI troppo neutro ({rsi_val:.2f}). Nessuna direzione chiara, ma si procede comunque con la previsione AI.")

        from src.indicators import fibonacci_levels, calculate_elliott_wave_features, calculate_atr

        # === Trend direction semplice con MA50 e MA200
        df["ma50"] = df["close"].rolling(window=50).mean()
        df["ma200"] = df["close"].rolling(window=200).mean()
        trend = "up" if df["ma50"].iloc[-1] > df["ma200"].iloc[-1] else "down"
        print()
        print(f" Trend rilevato: {trend.upper()} (MA50: {df['ma50'].iloc[-1]:.2f}, MA200: {df['ma200'].iloc[-1]:.2f})")

        # === Filtro Wyckoff: blocco se range troppo stretto
        if is_in_consolidation(df, window=20, threshold=0.006) and not is_breakout(df, window=20, breakout_margin=0.0015):
            print("⚠️ Blocco Wyckoff attivo. Generazione TP/SL a scopo informativo...")

            # Calcolo rapido solo per riferimento manuale
            from src.indicators import calculate_atr
            df = calculate_atr(df)
            last_close = live_price if live_price is not None else df["close"].iloc[-1]
            try:
                last_close = float(last_close)
                if last_close > 100000:
                    print(f"⚠️ Prezzo elevato rilevato: {last_close}")
                    last_close = round(last_close, 2)  # Usa il prezzo live corretto
            except Exception as e:
                print(f"⚠️ Errore nella conversione del prezzo: {e}")
                last_close = live_price  # Fallback sicuro

            atr_value = df["ATR"].iloc[-1]

            action = "BUY"
            if trend == "down":
                action = "SELL"

            risk_score = calculate_risk_score(df, action, trend, atr_value, rsi_val)

            print()
            print(f" RISK SCORE del segnale: {risk_score}/3")


            if np.isnan(atr_value) or atr_value == 0:
                atr_value = last_close * 0.007

            tp = last_close + (atr_value * 2.0)
            sl = last_close - (atr_value * 1.0)
            action = "BUY"

            if trend == "down":
                action = "SELL"
                tp, sl = sl, tp

            tp_diff = abs(tp - last_close)
            sl_diff = abs(sl - last_close)

            # Calcolo lotto
            base = "BTC"  # fissi semplificati
            pip_value = 1.0
            risk_eur = 500 * 0.03
            lotto_raw = risk_eur / (sl_diff * pip_value)
            lot_size = round(min(max(lotto_raw, 0.01), 0.1), 2)

            if not all([tp, sl]) or any(v in ["N/A", 0] for v in [tp, sl]):
                print(f"⚠️ TP o SL non validi, li forzo per sicurezza.")
                last_close = live_price if live_price is not None else df["close"].iloc[-1]
                from src.indicators import calculate_adx
                df = calculate_adx(df)

                adx_value = df["ADX"].iloc[-1]
                print(f"⚙️ ADX calcolato: {adx_value:.2f} (forza del trend)")

                if adx_value > 25:
                    print("🔍 Trend forte rilevato: SL più ampio")
                    sl_multiplier = 1.5  # SL più ampio per trend forte
                else:
                    print("🔍 Trend debole o laterale: SL standard")
                    sl_multiplier = 1.0  # SL standard

                # Calcolo SL dinamico
                sl = last_close - (atr_value * sl_multiplier)
                tp = last_close + (atr_value * 2.0)
                if action == "SELL":
                    tp, sl = sl, tp

#            tp, sl = check_tp_sl(tp, sl, last_close, atr_value, action)
            tp, sl = check_tp_sl(tp, sl, last_close, atr_value, action, df=df, trend=trend)


            return {
                "azione": action,
                "TP": tp,
                "SL": sl,
                "rsi": df["rsi"].iloc[-1],
                "confidence": 0,
                "price_entry": last_close,
                "fib_0618": None,
                "esito": "BLOCCATO_WYCKOFF",
                "lot_size": lot_size,
                "pip_value": pip_value,
                "tp_diff": tp_diff,
                "sl_diff": sl_diff,
                "motivo_blocco": "wyckoff",
                "risk_score": risk_score,
            }

        df = calculate_atr(df)
        
        # Calcolo feature extra
        high = df["high"].max()
        low = df["low"].min()
        fibs = fibonacci_levels(high, low)
        print()
        print(f" Livelli Fibonacci (da {low} a {high}):")
        for i, level in enumerate(fibs):
            print(f"   Livello {i}: {level:.2f}")

        df["fib_level_diff"] = abs(df["close"] - fibs[5])
        df["wave_score"] = calculate_elliott_wave_features(df)
        print()
        print(f" Elliott Wave Score: {df['wave_score'].iloc[-1]}")

        # ⚠️ Allineamento ultima candela con prezzo live
        if live_price is not None:
            try:
                df.at[df.index[-1], "close"] = live_price
                df.at[df.index[-1], "open"] = df["close"].iloc[-2]
                df.at[df.index[-1], "high"] = max(live_price, df["close"].iloc[-2])
                df.at[df.index[-1], "low"] = min(live_price, df["close"].iloc[-2])
                print(f"✅ Ultima candela aggiornata con prezzo live: {live_price}")
            except Exception as e:
                print(f"⚠️ Errore nell'aggiornamento candela con live price: {e}")

        X = df[["open", "high", "low", "close", "volume", "fib_level_diff", "wave_score"]]
        X_scaled = scaler.transform(X)

        prediction = model.predict(X_scaled[-1].reshape(1, -1))
        action = "BUY" if prediction[0] == 1 else "SELL"
        proba = model.predict_proba(X_scaled[-1].reshape(1, -1))[0]
        confidence = proba[1] if action == "BUY" else proba[0]
        print(f" Probabilità {action}: {confidence:.2f}")
        if 45 < rsi_val < 55 and confidence < 0.65:
            print("❌ RSI neutro + confidenza bassa. Trade bloccato.")
            
            # Simula comunque calcolo per mostrare il TP/SL teorico
            last_close = live_price if live_price is not None else df["close"].iloc[-1]
            atr_value = df["ATR"].iloc[-1]

            action = "BUY"
            if trend == "down":
                action = "SELL"

            try:
                risk_score = calculate_risk_score(df, action, trend, atr_value, rsi_val)
                print(f"✅ RISK SCORE calcolato correttamente: {risk_score}/3")
            except Exception as e:
                print(f"⚠️ ERRORE nel calcolo del RISK SCORE: {e}")
                risk_score = 0  # Imposta il rischio a 0 in caso di errore

            print()
            print(f" RISK SCORE del segnale: {risk_score}/3")


            if atr_value < 30:
                print("⏸️ Volatilità troppo bassa, trade ignorato.")

                # Calcolo risk score
                risk_score = calculate_risk_score(df, action, trend, atr_value, rsi_val)

                print()
                print(f" RISK SCORE del segnale: {risk_score}/3")

                tp_theoretical, sl_theoretical = check_tp_sl(tp_theoretical, sl_theoretical, last_close, atr_value, action)

                return {
                    "azione": action,
                    "TP": tp_theoretical,
                    "SL": sl_theoretical,
                    "rsi": rsi_val,
                    "confidence": confidence,
                    "price_entry": last_close,
                    "fib_0618": None,
                    "esito": "BLOCCATO_ATR",
                    "lot_size": lot_size,
                    "pip_value": pip_value,
                    "tp_diff": tp_diff,
                    "sl_diff": sl_diff,
                    "motivo_blocco": "atr_basso",
                    "risk_score": risk_score,
                }

            if np.isnan(atr_value) or atr_value == 0:
                atr_value = last_close * 0.007

            tp_theoretical = last_close + (atr_value * 2.0)
            sl_theoretical = last_close - (atr_value * 1.0)
            if action == "SELL":
                tp_theoretical, sl_theoretical = sl_theoretical, tp_theoretical


            print(f" TP teorico (senza esecuzione): {tp_theoretical:.2f}")
            print(f" SL teorico (senza esecuzione): {sl_theoretical:.2f}")

            # Calcolo pip value e lotto anche se è bloccato
            symbol_used = df.attrs.get("symbol", "BTCUSDT")
            import re
            base = re.sub(r"[-_/]*USD[T]?$", "", symbol_used, flags=re.IGNORECASE).upper()
            pip_map = {"BTC": 1.0, "ETH": 0.1, "XRP": 0.01, "ADA": 0.01, "SOL": 0.01}
            pip_value = pip_map.get(base, 0.0001)

            tp_diff = atr_value * 2.0
            sl_diff = atr_value * 1.0
            risk_eur = 500 * 0.03  # stesso capitale e rischio come sopra
            lotto_raw = risk_eur / (sl_diff * pip_value)
            lot_size = round(min(max(lotto_raw, 0.01), 0.1), 2)

            tp_theoretical, sl_theoretical = check_tp_sl(tp_theoretical, sl_theoretical, last_close, atr_value, action)

            return {
                "azione": action,
                "TP": tp_theoretical,
                "SL": sl_theoretical,
                "rsi": rsi_val,
                "confidence": confidence,
                "price_entry": last_close,
                "fib_0618": None,
                "esito": "BLOCCATO_CONFIDENCE",  # puoi anche lasciare "N/A" se preferisci, io ti consiglio di uniformarlo
                "lot_size": lot_size,
                "pip_value": pip_value,
                "tp_diff": tp_diff,
                "sl_diff": sl_diff,
                "risk_score": risk_score,
                "motivo_blocco": "confidence_bassa",  # 👉 QUESTA è la chiave che ti mancava
            }

        # ✅ Filtro più flessibile: solo avviso se non allineato
        # ❌ Blocco BUY molto debole
        if action == "BUY" and trend == "down" and rsi_val < 45 and df["wave_score"].iloc[-1] < 0:
            print("❌ Trade BUY bloccato: trend ribassista, RSI basso e onda negativa.")
            
            risk_score = calculate_risk_score(df, action, trend, atr_value, rsi_val)

            print()
            print(f" RISK SCORE del segnale: {risk_score}/3")

#            tp, sl = check_tp_sl(tp, sl, last_close, atr_value, action)
            tp, sl = check_tp_sl(tp, sl, last_close, atr_value, action, df=df, trend=trend)

            return {
                "azione": action,
                "TP": tp,
                "SL": sl,
                "rsi": rsi_val,
                "confidence": confidence,
                "price_entry": last_close,
                "fib_0618": None,
                "esito": "BLOCCATO_FILTRI",
                "lot_size": lot_size,
                "pip_value": pip_value,
                "tp_diff": tp_diff,
                "sl_diff": sl_diff,
                "motivo_blocco": "filtro_trend_rsi",
                "risk_score": risk_score,
            }

        if action == "BUY" and trend == "down" and rsi_val < 45:
            print("❌ BUY bloccato: trend ribassista e RSI sotto 45.")
            
            # 1. Calcolo ATR
            if "ATR" not in df.columns:
                from src.indicators import calculate_atr
                df = calculate_atr(df)
            atr_value = df["ATR"].iloc[-1]
            
            # 2. Calcolo risk_score subito
            risk_score = calculate_risk_score(df, action, trend, atr_value, rsi_val)
            print(f" RISK SCORE del segnale: {risk_score}/3")
            
            # 3. Calcolo TP/SL 
            last_close = live_price if live_price is not None else df["close"].iloc[-1]
            tp = last_close + (atr_value * 2.0)
            sl = last_close - (atr_value * 1.0)
            
            # 4. Calcolo differenze e lot size
            tp_diff = abs(tp - last_close)
            sl_diff = abs(sl - last_close)
            
            risk_eur = 500 * 0.03
            pip_value = 1.0  # default per BTC
            lotto_raw = risk_eur / (sl_diff * pip_value)
            lot_size = round(min(max(lotto_raw, 0.01), 0.1), 2)
            
            if action == "SELL":
                tp, sl = sl, tp

            return {
                "azione": action,
                "TP": tp,
                "SL": sl,
                "rsi": rsi_val,
                "confidence": confidence,
                "price_entry": last_close,
                "fib_0618": None,
                "esito": "BLOCCATO_TREND",
                "lot_size": lot_size,
                "pip_value": pip_value,
                "tp_diff": tp_diff,
                "sl_diff": sl_diff,
                "motivo_blocco": "trend_rsi",
                "risk_score": risk_score
            }
            
    except Exception as e:
        print(f"❌ ERRORE nella previsione del trade: {str(e)}")
        return None

