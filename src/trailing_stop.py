# E:\CODE\FOREX_CRYPTO_V2\src\trailing_stop.py

# def adjust_sl(signal, current_price):
#     """
#     Aggiorna dinamicamente lo SL se il prezzo ha superato una soglia di trailing.
#     Ritorna un nuovo dizionario segnale aggiornato.
#     """
#     if not signal or "azione" not in signal or "price_entry" not in signal or "SL" not in signal:
#         return signal

#     action = signal["azione"]
#     entry = signal["price_entry"]
#     original_sl = signal["SL"]
#     sl_updated = original_sl

#     # Soglia di attivazione trailing
#     threshold = signal["tp_diff"] * 0.5  # quando superato metà del tragitto TP

#     if action == "BUY" and current_price - entry >= threshold:
#         sl_updated = max(original_sl, entry)  # alza SL almeno a break-even
#     elif action == "SELL" and entry - current_price >= threshold:
#         sl_updated = min(original_sl, entry)  # abbassa SL almeno a break-even

#     if sl_updated != original_sl:
#         print(f"🔁 TRAILING ATTIVO: SL aggiornato da {original_sl:.2f} → {sl_updated:.2f} (prezzo live: {current_price:.2f})")
#         signal["SL"] = sl_updated

#     if "ADX" in signal:
#         adx_value = signal["ADX"]
#         if adx_value > 25:
#             print(f"⚙️ ADX forte ({adx_value:.2f}): SL più ampio mantenuto")
#             threshold = signal["tp_diff"] * 0.7  # Maggiore soglia per trend forte
#         else:
#             print(f"⚙️ ADX debole ({adx_value:.2f}): SL standard")
#             threshold = signal["tp_diff"] * 0.5  # Soglia standard

#     return signal
 
def adjust_sl(signal, current_price):
    """
    Aggiorna dinamicamente lo SL se il prezzo ha superato una soglia di trailing.
    Tolleranza aumentata per evitare modifiche premature.
    """
    if not signal or "azione" not in signal or "price_entry" not in signal or "SL" not in signal:
        return signal

    action = signal["azione"]
    entry = signal["price_entry"]
    original_sl = signal["SL"]
    sl_updated = original_sl

    # Tolleranza più alta
    threshold = signal["tp_diff"] * 0.75  # soglia trailing meno aggressiva

    if action == "BUY" and current_price - entry >= threshold:
        sl_updated = max(original_sl, entry)
    elif action == "SELL" and entry - current_price >= threshold:
        sl_updated = min(original_sl, entry)

    if sl_updated != original_sl:
        print(f"🔁 TRAILING ATTIVO: SL aggiornato da {original_sl:.2f} → {sl_updated:.2f} (prezzo live: {current_price:.2f})")
        signal["SL"] = sl_updated

    if "ADX" in signal:
        adx_value = signal["ADX"]
        if adx_value > 25:
            print(f"⚙️ ADX forte ({adx_value:.2f}): SL trailing meno aggressivo")
            threshold = signal["tp_diff"] * 0.85
        else:
            print(f"⚙️ ADX debole ({adx_value:.2f}): SL trailing standard")
            threshold = signal["tp_diff"] * 0.7

    return signal
