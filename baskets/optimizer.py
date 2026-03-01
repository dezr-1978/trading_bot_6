# backtest/optimizer.py

import itertools
import pandas as pd
from loguru import logger

from backtest.backtester import Backtester
from backtest.metrics import summary_metrics


class StrategyOptimizer:
    """
    Перебирає параметри ризику та знаходить найкращі конфігурації.
    Працює з новою архітектурою Backtester.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        symbol: str,
        initial_balance: float,
        base_risk_config: dict,
        candle_duration_sec: int,
        strategy=None,
        ml_filter=None,
    ):
        self.df = df
        self.symbol = symbol
        self.initial_balance = initial_balance
        self.base_risk_config = base_risk_config
        self.candle_duration_sec = candle_duration_sec
        self.strategy = strategy
        self.ml_filter = ml_filter

    # ============================================================
    # MAIN OPTIMIZATION LOOP
    # ============================================================

    def optimize(self, param_grid: dict) -> pd.DataFrame:
        """
        param_grid приклад:

        {
            "risk_per_trade": [0.005, 0.01],
            "sl_mult": [1.2, 1.5, 2.0],
            "tp_mult": [2.5, 3.0, 3.5],
            "min_rr_ratio": [1.2, 1.5, 2.0]
        }
        """

        keys = list(param_grid.keys())
        combinations = list(itertools.product(*param_grid.values()))

        logger.info(f"[OPTIMIZER] Total combinations: {len(combinations)}")

        results = []

        for values in combinations:
            params = dict(zip(keys, values))
            risk_cfg = self._build_risk_config(params)

            bt = Backtester(
                initial_balance=self.initial_balance,
                risk_config=risk_cfg,
                candle_duration_sec=self.candle_duration_sec,
                strategy=self.strategy,
                ml_filter=self.ml_filter,
            )

            bt.run(self.df.copy(), self.symbol)
            trades = bt.results()

            # Мінімальна кількість угод для статистики
            if len(trades) < 30:
                continue

            metrics = summary_metrics(trades, self.initial_balance)
            metrics.update(params)
            results.append(metrics)

        return pd.DataFrame(results)

    # ============================================================
    # BUILD RISK CONFIG
    # ============================================================

    def _build_risk_config(self, params: dict) -> dict:
        """
        Створює risk_config на основі базового + параметрів оптимізації.
        """

        cfg = self.base_risk_config.copy()

        # risk_per_trade
        if "risk_per_trade" in params:
            cfg["risk_per_trade"] = params["risk_per_trade"]

        # SL multiplier
        if "sl_mult" in params:
            cfg["atr"]["sl_multiplier"] = params["sl_mult"]

        # TP multiplier
        if "tp_mult" in params:
            cfg["atr"]["tp_multiplier"] = params["tp_mult"]

        # мінімальне RR
        if "min_rr_ratio" in params:
            cfg["min_rr_ratio"] = params["min_rr_ratio"]

        return cfg
