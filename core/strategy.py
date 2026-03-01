# core/strategy.py

from dataclasses import dataclass
from typing import Dict
from loguru import logger


@dataclass
class StrategyResult:
    signal: str          # BUY / SELL / HOLD
    reason: str          # Пояснення
    sl: float = None     # Stop Loss (опційно)
    tp: float = None     # Take Profit (опційно)


class DefaultStrategy:
    """
    Проста стратегія:
    - BUY: RSI < 30, MACD hist > 0, EMA50 > EMA200
    - SELL: RSI > 60, MACD hist < 0, EMA50 < EMA200
    - HOLD: інакше
    """

    def evaluate(self, ind: Dict) -> StrategyResult:
        rsi = ind.get("rsi")
        macd_hist = ind.get("macd_hist")
        ema50 = ind.get("ema50")
        ema200 = ind.get("ema200")

        if rsi is None or macd_hist is None or ema50 is None or ema200 is None:
            return StrategyResult("HOLD", "Not enough indicators")

        # BUY
        if rsi < 30 and macd_hist > 0 and ema50 > ema200:
            reason = f"BUY | rsi={rsi:.2f}, macd_hist={macd_hist:.4f}"
            logger.debug(reason)
            return StrategyResult("BUY", reason)

        # SELL
        if rsi > 60 and macd_hist < 0 and ema50 < ema200:
            reason = f"SELL | rsi={rsi:.2f}, macd_hist={macd_hist:.4f}"
            logger.debug(reason)
            return StrategyResult("SELL", reason)

        # HOLD
        reason = f"HOLD | rsi={rsi:.2f}, macd_hist={macd_hist:.4f}"
        logger.debug(reason)
        return StrategyResult("HOLD", reason)


def load_default_strategy() -> DefaultStrategy:
    return DefaultStrategy()
