# E:\CODE\FOREX_CRYPTO_V2\src\wyckoff_filter.py

def is_in_consolidation(df, window=20, threshold=0.005):
    """
    Rileva fase laterale (accumulo/distribuzione) usando la differenza tra massimo e minimo.
    threshold: percentuale max tra high e low per considerare "range stretto"
    """
    if len(df) < window:
        return False  # non abbastanza dati

    recent = df.tail(window)
    high = recent["high"].max()
    low = recent["low"].min()
    close = recent["close"].iloc[-1]

    # range percentuale rispetto al prezzo attuale
    range_pct = (high - low) / close if close != 0 else 0

    if range_pct < threshold:
        print(f"⛔️ Blocco Wyckoff: range laterale rilevato (range={range_pct:.4f}, soglia={threshold})")
        return True
    return False
 
