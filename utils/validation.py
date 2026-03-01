# utils/validation.py

import pandas as pd
from loguru import logger


# ============================================================
# VALIDATE RAW CANDLE DATA
# ============================================================

def validate_candles(df: pd.DataFrame, min_candles: int = 200) -> bool:
    """
    Перевіряє коректність свічкових даних.
    Очікує колонки:
    ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    """

    if df is None or df.empty:
        logger.warning("[VALIDATION] DataFrame is empty or None")
        return False

    required = {"timestamp", "open", "high", "low", "close", "volume"}
    missing = required - set(df.columns)

    if missing:
        logger.error(f"[VALIDATION] Missing columns: {missing}")
        return False

    # Мінімальна кількість свічок
    if len(df) < min_candles:
        logger.warning(
            f"[VALIDATION] Not enough candles: {len(df)} < {min_candles}"
        )
        return False

    # NaN перевірка
    if df[list(required)].isnull().any().any():
        logger.error("[VALIDATION] NaN values detected in candle data")
        return False

    # Типи даних
    numeric_cols = ["open", "high", "low", "close", "volume"]
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            logger.error(f"[VALIDATION] Column {col} is not numeric")
            return False

    # Логіка цін
    invalid = df[
        (df["high"] < df["low"]) |
        (df["open"] <= 0) |
        (df["close"] <= 0)
    ]

    if not invalid.empty:
        logger.error("[VALIDATION] Invalid price values detected")
        return False

    return True


# ============================================================
# VALIDATE INDICATORS
# ============================================================

def validate_indicators(df: pd.DataFrame, required: list) -> bool:
    """
    Перевіряє, що всі індикатори присутні та валідні.
    """

    if df is None or df.empty:
        logger.warning("[VALIDATION] Empty DataFrame for indicators")
        return False

    missing = [col for col in required if col not in df.columns]
    if missing:
        logger.error(f"[VALIDATION] Missing indicators: {missing}")
        return False

    # Перевірка NaN
    if df[required].isnull().any().any():
        logger.error("[VALIDATION] NaN detected in indicators")
        return False

    # Перевірка типів
    for col in required:
        if not pd.api.types.is_numeric_dtype(df[col]):
            logger.error(f"[VALIDATION] Indicator {col} is not numeric")
            return False

    return True
