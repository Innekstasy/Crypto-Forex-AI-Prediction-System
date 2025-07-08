
import pandas as pd

def detect_candlestick_patterns(df):
    if df.isnull().values.any() or df.empty:
        return []

    required_cols = {"open", "high", "low", "close", "timestamp"}
    if not required_cols.issubset(df.columns):
        return []

    patterns = []
    if len(df) < 5:
        return patterns

    for i in range(2, len(df)):
        c1, c2, c3 = df.iloc[i - 2], df.iloc[i - 1], df.iloc[i]

        # DOJI - corpo quasi nullo, shadow significativa
        body_size = abs(c3['close'] - c3['open'])
        candle_range = c3['high'] - c3['low']
        if body_size < candle_range * 0.05 and candle_range > 0:
            patterns.append((c3['timestamp'], 'Doji'))

        # BULLISH ENGULFING - corpo reale maggiore, range significativo
        if (
            c2['close'] < c2['open'] and
            c3['close'] > c3['open'] and
            c3['open'] < c2['close'] and
            c3['close'] > c2['open'] and
            abs(c3['close'] - c3['open']) > abs(c2['close'] - c2['open']) * 1.2
        ):
            patterns.append((c3['timestamp'], 'Bullish Engulfing'))

        # BEARISH ENGULFING
        if (
            c2['close'] > c2['open'] and
            c3['close'] < c3['open'] and
            c3['open'] > c2['close'] and
            c3['close'] < c2['open'] and
            abs(c3['open'] - c3['close']) > abs(c2['open'] - c2['close']) * 1.2
        ):
            patterns.append((c3['timestamp'], 'Bearish Engulfing'))

        # HAMMER - shadow inferiore lunga, corpo nella parte alta
        lower_shadow = min(c3['open'], c3['close']) - c3['low']
        upper_shadow = c3['high'] - max(c3['open'], c3['close'])
        body = abs(c3['close'] - c3['open'])
        if (
            lower_shadow > 2 * body and
            upper_shadow < body and
            body / candle_range > 0.1
        ):
            patterns.append((c3['timestamp'], 'Hammer'))

        # INVERTED HAMMER - shadow superiore lunga, corpo nella parte bassa
        if (
            upper_shadow > 2 * body and
            lower_shadow < body and
            body / candle_range > 0.1
        ):
            patterns.append((c3['timestamp'], 'Inverted Hammer'))

        # MORNING STAR
        if (
            c1['close'] < c1['open'] and
            (c2['high'] - c2['low']) > 0 and abs(c2['close'] - c2['open']) / (c2['high'] - c2['low']) < 0.2 and
            c3['close'] > c3['open'] and
            c3['close'] > ((c1['open'] + c1['close']) / 2)
        ):
            patterns.append((c3['timestamp'], 'Morning Star'))

        # EVENING STAR
        if (
            c1['close'] > c1['open'] and
            (c2['high'] - c2['low']) > 0 and abs(c2['close'] - c2['open']) / (c2['high'] - c2['low']) < 0.2 and
            c3['close'] < c3['open'] and
            c3['close'] < ((c1['open'] + c1['close']) / 2)
        ):
            patterns.append((c3['timestamp'], 'Evening Star'))

    return patterns
