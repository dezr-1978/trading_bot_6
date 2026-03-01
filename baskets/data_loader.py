import pandas as pd
import requests
from pathlib import Path
from loguru import logger


def load_csv(path: str) -> pd.DataFrame:
    if not Path(path).exists():
        raise FileNotFoundError(f"CSV not found: {path}")

    df = pd.read_csv(path)

    required = {"timestamp", "open", "high", "low", "close", "volume"}
    if not required.issubset(df.columns):
        raise ValueError(f"CSV missing required columns: {required}")

    return df


def fetch_binance_klines(symbol: str, interval: str = "15m", limit: int = 1000):
    url = (
        f"https://api.binance.com/api/v3/klines"
        f"?symbol={symbol}&interval={interval}&limit={limit}"
    )

    logger.info(f"[DATA] Fetching Binance klines {symbol} {interval} limit={limit}")

    data = requests.get(url).json()

    if isinstance(data, dict) and data.get("code"):
        raise RuntimeError(f"Binance API error: {data}")

    return data


def klines_to_df(klines) -> pd.DataFrame:
    if not klines:
        logger.warning("[DATA] Empty klines list")
        return pd.DataFrame()

    cols = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "qav", "trades", "tbbav", "tbqav", "ignore"
    ]

    df = pd.DataFrame(klines, columns=cols)

    float_cols = ["open", "high", "low", "close", "volume"]
    for col in float_cols:
        df[col] = df[col].astype(float)

    df["timestamp"] = df["open_time"].astype(int)

    return df[["timestamp", "open", "high", "low", "close", "volume"]]
