# core/state.py

from dataclasses import dataclass, asdict
from typing import Dict, Optional


@dataclass
class BotState:
    price: Optional[float] = None
    indicators: Optional[Dict] = None
    strategy_signal: Optional[str] = None
    strategy_reason: Optional[str] = None
    market_filter_allow: Optional[bool] = None
    market_filter_reason: Optional[str] = None
    risk_locked: bool = False
    position: Optional[Dict] = None
    cooldown: bool = False

    def to_dict(self) -> Dict:
        return asdict(self)
