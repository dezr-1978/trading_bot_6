# basckets/visualizewalk_forward.py

import pandas as pd
from loguru import logger

from backtest.backtester import Backtester
from backtest.metrics import summary_metrics
from utils.time import TIMEFRAME_SECONDS


class WalkForwardTester:
    """
    Walk-forward тест на базі нового Backtester.

    Ідея:
    - df: повний історичний DataFrame з індикаторами
    - рухаємося вікнами: train_size + test_size
    - на кожному кроці:
        * НЕ оптимізуємо параметри (чистий WF)
        * ганяємо Backtester тільки на test_df
        * рахуємо метрики, переносимо balance далі
    """

    def __init__(
        self,
        df: pd.DataFrame,
        symbol: str,
        initial_balance: float,
        risk_config: dict,
        timeframe: str,
        train_size: int,
        test_size: int,
    ):
        self.df = df.reset_index(drop=True)
        self.symbol = symbol
        self.initial_balance = initial_balance
        self.risk_config = risk_config
        self.candle_sec = TIMEFRAME_SECONDS[timeframe]
        self.train_size = train_size
        self.test_size = test_size

    def run(self) -> pd.DataFrame:
        """
        Запускає walk-forward тест.
        Повертає DataFrame з метриками по кожному вікну.
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
                f"[WALK] Window start={start}, "
                f"train={len(train_df)}, test={len(test_df)}"
            )

            # ❗ НІЧОГО не оптимізуємо — чистий WF
            bt = Backtester(
                initial_balance=balance,
                risk_config=self.risk_config,
                candle_duration_sec=self.candle_sec,
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

            balance = metrics["final_balance"]
            metrics["balance_after"] = balance

            results.append(metrics)

            start += step

        logger.info("[WALK] Finished")
        return pd.DataFrame(results)
