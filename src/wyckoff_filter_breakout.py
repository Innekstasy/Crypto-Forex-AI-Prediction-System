import pandas as pd

def is_breakout(df, window=20, breakout_margin=0.0015):
    """
    Verifica se è in corso un breakout Wyckoff.

    Parameters:
        df (pd.DataFrame): DataFrame con colonne 'high', 'low', 'close'
        window (int): Numero di candele da considerare per il range
        breakout_margin (float): Margine minimo in percentuale per validare il breakout

    Returns:
        bool: True se breakout presente, False altrimenti
    """
    if len(df) < window + 1:
        return False  # non ci sono abbastanza dati

    recent_df = df.tail(window)
    max_range = recent_df["high"].max()
    min_range = recent_df["low"].min()

    current_close = df["close"].iloc[-1] if not df["close"].empty else 0

    # breakout long
    if current_close > max_range * (1 + breakout_margin):
        print(f"✅ Breakout UP rilevato sopra {max_range:.2f}")
        return True

    # breakout short
    if current_close < min_range * (1 - breakout_margin):
        print(f"✅ Breakout DOWN rilevato sotto {min_range:.2f}")
        return True

    # ancora in range
    return False
 
