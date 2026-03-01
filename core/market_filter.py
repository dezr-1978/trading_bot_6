from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class MarketFilterConfig:
    min_atr_pct: float = 0.001
    min_volume_ratio: float = 1.0
    min_ema_distance_pct: float = 0.001


class MarketFilter:
    def __init__(self, cfg: MarketFilterConfig):
        self.cfg = cfg

    def allow_trade(self, ind: Dict) -> Tuple[bool, str]:
        try:
            price = float(ind["close"])
            atr = float(ind["atr"])
            volume = float(ind["volume"])
            volume_sma20 = float(ind["volume_sma20"])
            ema50 = float(ind["ema50"])
            ema200 = float(ind["ema200"])
        except (KeyError, TypeError, ValueError):
            return False, "Invalid indicators for MarketFilter"

        atr_pct = atr / price if price > 0 else 0.0
        if atr_pct < self.cfg.min_atr_pct:
            return False, f"Low volatility (ATR%={atr_pct:.4f})"

        volume_ratio = volume / volume_sma20 if volume_sma20 > 0 else 0.0
        if volume_ratio < self.cfg.min_volume_ratio:
            return False, f"Low volume (ratio={volume_ratio:.2f})"

        ema_dist_pct = abs(ema50 - ema200) / price if price > 0 else 0.0
        if ema_dist_pct < self.cfg.min_ema_distance_pct:
            return False, f"Flat market (EMA dist%={ema_dist_pct:.4f})"

        return True, "Market OK"
