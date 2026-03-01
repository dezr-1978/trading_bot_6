# core/risk.py

from dataclasses import dataclass
from typing import Dict


@dataclass
class RiskManager:
    risk_per_trade: float
    max_daily_loss: float
    atr_sl_multiplier: float
    atr_tp_multiplier: float
    min_rr_ratio: float

    def calc_position(self, balance: float, price: float, atr: float) -> Dict:
        """
        Розрахунок розміру позиції, SL, TP.
        """
        if atr <= 0 or price <= 0:
            sl = price * 0.99
            tp = price * 1.02
        else:
            sl = price - atr * self.atr_sl_multiplier
            tp = price + atr * self.atr_tp_multiplier

        risk_amount = balance * self.risk_per_trade
        risk_per_unit = max(price - sl, 1e-6)
        size = risk_amount / risk_per_unit

        rr = (tp - price) / (price - sl) if price > sl else 0.0
        if rr < self.min_rr_ratio:
            return {"allowed": False, "reason": f"RR too low ({rr:.2f})"}

        return {
            "allowed": True,
            "size": size,
            "sl": sl,
            "tp": tp,
            "rr": rr,
        }
