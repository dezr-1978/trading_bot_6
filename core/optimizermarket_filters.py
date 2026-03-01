# core/optimizemarket_filters.py

from loguru import logger


class MarketFilter:
    def __init__(
        self,
        min_atr_pct: float = 0.001,        # мін. ATR у % від ціни (0.1%)
        min_volume_ratio: float = 1.0,     # volume / volume_sma20
        min_ema_distance_pct: float = 0.001,  # мін. відстань EMA50-EMA200
    ):
        self.min_atr_pct = min_atr_pct
        self.min_volume_ratio = min_volume_ratio
        self.min_ema_distance_pct = min_ema_distance_pct

    def allow_trade(self, ind: dict) -> tuple[bool, str]:
        """
        Повертає (allow, reason)
        """

        price = ind["close"]
        atr = ind["atr"]
        volume = ind["volume"]
        volume_sma20 = ind["volume_sma20"]
        ema50 = ind["ema50"]
        ema200 = ind["ema200"]

        # === LOW VOLATILITY FILTER ===
        atr_pct = atr / price
        if atr_pct < self.min_atr_pct:
            return False, f"Low volatility (ATR%={atr_pct:.4f})"

        # === LOW LIQUIDITY FILTER ===
        volume_ratio = volume / volume_sma20
        if volume_ratio < self.min_volume_ratio:
            return False, f"Low volume (ratio={volume_ratio:.2f})"

        # === FLAT MARKET FILTER ===
        ema_dist_pct = abs(ema50 - ema200) / price
        if ema_dist_pct < self.min_ema_distance_pct:
            return False, f"Flat market (EMA dist%={ema_dist_pct:.4f})"

        return True, "Market OK"