# core/data.py

import pandas as pd


def prepare_market_data(df: pd.DataFrame, lookback: int | None = None) -> pd.DataFrame:
    """
    Приводить сирі дані до стандартного формату:
    timestamp, open, high, low, close, volume
    Опційно обрізає по lookback.
    """
    cols = ["timestamp", "open", "high", "low", "close", "volume"]
    missing = set(cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in market data: {missing}")

    df = df.copy()
    df = df[cols]

    df["timestamp"] = df["timestamp"].astype(int)
    float_cols = ["open", "high", "low", "close", "volume"]
    for c in float_cols:
        df[c] = df[c].astype(float)

    if lookback is not None and len(df) > lookback:
        df = df.iloc[-lookback:]

    df = df.reset_index(drop=True)
    return df
