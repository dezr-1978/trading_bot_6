# ai/features.py

import pandas as pd
from loguru import logger


# ============================================================
# FEATURE LIST
# ============================================================

FEATURE_COLUMNS = [
    "rsi",
    "ema50_slope",
    "ema200_slope",
    "macd_hist",
    "atr_pct",
    "volume_ratio",
]


# ============================================================
# FEATURE BUILDER
# ============================================================

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Створює ML-фічі з DataFrame з індикаторами.
    Очікує колонки:
    close, ema50, ema200, rsi, macd_hist, atr, volume, volume_sma20
    """

    if df is None or df.empty:
        logger.warning("[FEATURES] Empty DataFrame")
        return pd.DataFrame()

    try:
        features = pd.DataFrame(index=df.index)

        # RSI
        features["rsi"] = df["rsi"]

        # EMA slopes
        features["ema50_slope"] = df["ema50"].diff()
        features["ema200_slope"] = df["ema200"].diff()

        # MACD histogram
        features["macd_hist"] = df["macd_hist"]

        # ATR as % of price
        features["atr_pct"] = df["atr"] / df["close"]

        # Volume ratio
        features["volume_ratio"] = df["volume"] / df["volume_sma20"]

        # Drop NaN rows
        features = features.dropna()

        return features

    except Exception:
        logger.exception("[FEATURES] Failed to build features")
        return pd.DataFrame()
