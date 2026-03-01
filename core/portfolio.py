# core/portfolio.py

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class Position:
    symbol: str
    entry_price: float
    size: float
    sl: float
    tp: float


class Portfolio:
    def __init__(self, cooldown_candles: int = 3):
        self.position: Optional[Position] = None
        self.cooldown_candles = cooldown_candles
        self._cooldown_left = 0

    def can_open(self) -> bool:
        return self.position is None and self._cooldown_left == 0

    def open(self, symbol: str, price: float, size: float, sl: float, tp: float):
        self.position = Position(symbol, price, size, sl, tp)
        self._cooldown_left = self.cooldown_candles

    def close(self):
        self.position = None

    def tick(self):
        if self._cooldown_left > 0:
            self._cooldown_left -= 1

    def get_position_dict(self) -> Optional[Dict]:
        if self.position is None:
            return None
        return {
            "symbol": self.position.symbol,
            "entry_price": self.position.entry_price,
            "size": self.position.size,
            "sl": self.position.sl,
            "tp": self.position.tp,
        }
