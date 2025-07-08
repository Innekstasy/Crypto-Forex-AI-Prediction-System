import numpy as np

def fibonacci_levels(high, low):
    retracements = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
    levels = [low + (high - low) * r for r in retracements]
    return levels

def calculate_elliott_wave_features(df):
    """
    Semplice analisi di onde basata su swing di prezzo.
    Restituisce un 'wave_score' basato su pattern up/down.
    """
    wave_score = 0
    for i in range(2, len(df)):
        prev = df["close"].iloc[i - 1]
        prev2 = df["close"].iloc[i - 2]
        curr = df["close"].iloc[i]

        if prev2 < prev > curr:  # possibile top
            wave_score -= 1
        elif prev2 > prev < curr:  # possibile bottom
            wave_score += 1

    return wave_score / len(df)

def calculate_rsi(df, period=14):
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = np.where(avg_loss == 0, 0, avg_gain / avg_loss)
    rsi = 100 - (100 / (1 + rs))
    df["rsi"] = rsi
    return df

def calculate_atr(df, period=14):
    df["H-L"] = df["high"] - df["low"]
    df["H-PC"] = abs(df["high"] - df["close"].shift())
    df["L-PC"] = abs(df["low"] - df["close"].shift())
    df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1)
    df["ATR"] = df["TR"].rolling(window=period).mean()
    df.drop(columns=["H-L", "H-PC", "L-PC", "TR"], inplace=True, errors="ignore")
    return df

def calculate_adx(df, period=14):
    """
    Calcola l'ADX (Average Directional Index) per determinare la forza del trend.
    """
    df["DM+"] = np.where((df["high"] - df["high"].shift(1)) > (df["low"].shift(1) - df["low"]), 
                         df["high"] - df["high"].shift(1), 0)
    df["DM-"] = np.where((df["low"].shift(1) - df["low"]) > (df["high"] - df["high"].shift(1)), 
                         df["low"].shift(1) - df["low"], 0)
    df["TR_ADX"] = np.maximum(df["high"] - df["low"], 
                          abs(df["high"] - df["close"].shift(1)), 
                          abs(df["low"] - df["close"].shift(1)))
    df["DI+"] = 100 * (df["DM+"].rolling(window=period).mean() / df["TR_ADX"].rolling(window=period).mean())
    df["DI-"] = 100 * (df["DM-"].rolling(window=period).mean() / df["TR_ADX"].rolling(window=period).mean())
    df["DX"] = (abs(df["DI+"] - df["DI-"]) / (df["DI+"] + df["DI-"])) * 100
    df["ADX"] = df["DX"].rolling(window=period).mean()
    return df
