from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional

import pandas as pd
from loguru import logger


@dataclass
class RiskConfig:
    risk_per_trade: float = 0.01
    sl_mult: float = 1.5
    tp_mult: float = 3.0


@dataclass
class Position:
    symbol: str
    entry_price: float
    size: float
    sl: float
    tp: float
    entry_ts: int


class Backtester:
    def __init__(
        self,
        initial_balance: float,
        risk_config: Dict,
        candle_duration_sec: int,
    ):
        self.initial_balance = float(initial_balance)
        self.balance = float(initial_balance)
        self.candle_duration_sec = candle_duration_sec

        self.risk_cfg = RiskConfig(
            risk_per_trade=risk_config.get("risk_per_trade", 0.01),
            sl_mult=risk_config.get("sl_mult", 1.5),
            tp_mult=risk_config.get("tp_mult", 3.0),
        )

        self._trades: List[Dict] = []
        self._position: Optional[Position] = None

    def run(self, df: pd.DataFrame, symbol: str):
        if df.empty:
            logger.warning("[BT] Empty DataFrame, nothing to backtest")
            return

        df = df.reset_index(drop=True)

        logger.info(f"[BT] Starting backtest for {symbol}, candles={len(df)}")

        for _, row in df.iterrows():
            ts = int(row.get("timestamp", 0))
            price = float(row["close"])
            signal = row.get("signal", "HOLD")

            if self._position is None:
                if signal == "BUY":
                    self._open_position(symbol, price, row, ts)
            else:
                self._maybe_close_position(price, row, ts, signal)

        logger.info(f"[BT] Finished backtest, trades={len(self._trades)}")

    def _open_position(self, symbol: str, price: float, row, ts: int):
        atr = float(row.get("atr", 0.0))

        if atr > 0:
            sl = price - atr * self.risk_cfg.sl_mult
            tp = price + atr * self.risk_cfg.tp_mult
        else:
            sl = price * 0.99
            tp = price * 1.02

        risk_amount = self.balance * self.risk_cfg.risk_per_trade
        risk_per_unit = max(price - sl, 1e-6)
        size = risk_amount / risk_per_unit

        self._position = Position(
            symbol=symbol,
            entry_price=price,
            size=size,
            sl=sl,
            tp=tp,
            entry_ts=ts,
        )

        logger.debug(
            f"[BT] OPEN {symbol} price={price:.2f} size={size:.6f} "
            f"sl={sl:.2f} tp={tp:.2f}"
        )

    def _maybe_close_position(self, price: float, row, ts: int, signal: str):
        if self._position is None:
            return

        pos = self._position

        hit_sl = price <= pos.sl
        hit_tp = price >= pos.tp
        force_sell = signal == "SELL"

        if not (hit_sl or hit_tp or force_sell):
            return

        exit_price = price
        pnl = (exit_price - pos.entry_price) * pos.size
        self.balance += pnl

        trade = {
            "symbol": pos.symbol,
            "entry_price": pos.entry_price,
            "exit_price": exit_price,
            "pnl": float(pnl),
            "balance_after": float(self.balance),
            "timestamp": ts,
        }
        self._trades.append(trade)

        logger.debug(
            f"[BT] CLOSE {pos.symbol} entry={pos.entry_price:.2f} "
            f"exit={exit_price:.2f} pnl={pnl:.2f} balance={self.balance:.2f}"
        )

        self._position = None

    def results(self) -> pd.DataFrame:
        if not self._trades:
            return pd.DataFrame(
                columns=[
                    "symbol",
                    "entry_price",
                    "exit_price",
                    "pnl",
                    "balance_after",
                    "timestamp",
                ]
            )

        return pd.DataFrame(self._trades)
