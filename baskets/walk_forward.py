# backtest/walk_forward.py

import pandas as pd
from loguru import logger

from backtest.backtester import Backtester
from backtest.metrics import summary_metrics


class WalkForwardTester:
    """
    Walk-forward тестування стратегії.
    Працює з новою архітектурою Backtester.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        symbol: str,
        initial_balance: float,
        risk_config: dict,
        candle_duration_sec: int,
        train_size: int,
        test_size: int,
        strategy=None,
        ml_filter=None,
    ):
        self.df = df.reset_index(drop=True)
        self.symbol = symbol
        self.initial_balance = initial_balance
        self.risk_config = risk_config
        self.candle_duration_sec = candle_duration_sec
        self.train_size = train_size
        self.test_size = test_size
        self.strategy = strategy
        self.ml_filter = ml_filter

    # ============================================================
    # MAIN WF LOOP
    # ============================================================

    def run(self) -> pd.DataFrame:
        """
        Повертає DataFrame з результатами кожного WF-вікна.
        """

        results = []
        balance = self.initial_balance
        start = 0
        step = self.test_size

        logger.info("[WALK] Starting walk-forward test")

        while start + self.train_size + self.test_size <= len(self.df):

            train_df = self.df.iloc[start : start + self.train_size]
            test_df = self.df.iloc[
                start + self.train_size :
                start + self.train_size + self.test_size
            ]

            logger.info(
                f"[WALK] Train={len(train_df)} candles | Test={len(test_df)} candles"
            )

            # === Backtest only on test window ===
            bt = Backtester(
                initial_balance=balance,
                risk_config=self.risk_config,
                candle_duration_sec=self.candle_duration_sec,
                strategy=self.strategy,
                ml_filter=self.ml_filter,
            )

            bt.run(test_df.copy(), self.symbol)
            trades = bt.results()

            if trades.empty:
                logger.warning("[WALK] No trades in this window")
                start += step
                continue

            metrics = summary_metrics(trades, balance)

            metrics["window_start"] = start
            metrics["window_end"] = start + self.train_size + self.test_size

            # balance переноситься у наступне вікно
            balance = metrics["final_balance"]
            metrics["balance_after"] = balance

            results.append(metrics)

            start += step

        logger.info("[WALK] Finished")

        return pd.DataFrame(results)
