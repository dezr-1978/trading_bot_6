# core/execution.py

import time
from loguru import logger

from core.strategy import load_default_strategy, StrategyResult
from core.risk import RiskManager
from core.portfolio import Portfolio
from core.state import BotState
from utils.logger import (
    log_trade_open,
    log_trade_close,
    log_risk_block,
)


class Trader:
    """
    Головний торговий цикл бота.
    """

    def __init__(
        self,
        exchange,
        market_filter,
        portfolio: Portfolio,
        risk: RiskManager,
        settings: dict,
        candle_duration_sec: int,
        ml_filter=None,
        paper: bool = True,
    ):
        self.exchange = exchange
        self.market_filter = market_filter
        self.portfolio = portfolio
        self.risk = risk
        self.settings = settings
        self.paper = paper
        self.running = True
        self.candle_duration_sec = candle_duration_sec
        self.ml_filter = ml_filter

        # НОВА СТРАТЕГІЯ
        self.strategy = load_default_strategy()

        # Виконавець угод
        self.executor = TradeExecutor(
            exchange=exchange,
            portfolio=portfolio,
            risk=risk,
            candle_duration_sec=candle_duration_sec,
            paper=paper,
            ml_filter=ml_filter,
            strategy=self.strategy,
        )

        # Стан для UI
        self._state = BotState()

        # Початкові дані (опційно)
        self.symbol = None
        self.df = None
        self.last_price = None

    def set_initial_df(self, symbol, df):
        """
        Зберігає початковий DataFrame зі свічками.
        Викликається один раз при запуску бота.
        """
        self.symbol = symbol
        self.df = df
        if "close" in df.columns:
            self.last_price = df["close"].iloc[-1]
        else:
            self.last_price = None

    def run(self):
        logger.info("[TRADER] Bot started")
        while self.running:
            try:
                self.process()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.warning("[TRADER] Stopped by user")
                self.running = False
            except Exception as e:
                logger.exception(f"[TRADER] Runtime error: {e}")
                time.sleep(5)

    def process(self):
        """
        Один повний торговий цикл.
        """
        for symbol in self.settings["symbols"]:

            # --- 1. Отримуємо індикатори ---
            indicators = self.exchange.get_latest_indicators(
                symbol=symbol,
                timeframe=self.settings["timeframe"],
            )

            if not indicators:
                continue

            self._state.indicators = indicators
            self._state.price = indicators.get("close")

            # --- 2. Market Filter ---
            allow, reason = self.market_filter.allow_trade(indicators)
            self._state.market_filter_allow = allow
            self._state.market_filter_reason = reason

            if not allow:
                logger.info(f"[FILTER] {symbol} blocked: {reason}")
                continue

            # --- 3. Баланс ---
            balance = self.exchange.get_balance()

            # --- 4. Виконання торгової логіки ---
            exec_result = self.executor.process_symbol(
                symbol=symbol,
                indicators=indicators,
                balance=balance,
            )

            if exec_result is None:
                continue

            (
                signal,
                reason,
                position_snapshot,
                risk_locked,
                cooldown,
            ) = exec_result

            self._state.strategy_signal = signal
            self._state.strategy_reason = reason
            self._state.position = position_snapshot
            self._state.risk_locked = risk_locked
            self._state.cooldown = cooldown

    def get_state(self) -> dict:
        """
        Повертає стан бота у вигляді dict для UI.
        """
        return {
            "price": self._state.price,
            "indicators": self._state.indicators,
            "strategy_signal": self._state.strategy_signal,
            "strategy_reason": self._state.strategy_reason,
            "market_filter_allow": self._state.market_filter_allow,
            "market_filter_reason": self._state.market_filter_reason,
            "risk_locked": self._state.risk_locked,
            "position": self._state.position,
            "cooldown": self._state.cooldown,
        }


class TradeExecutor:
    """
    Виконання торгових рішень (BUY / SELL).
    """

    def __init__(
        self,
        exchange,
        portfolio: Portfolio,
        risk: RiskManager,
        candle_duration_sec: int,
        paper: bool = True,
        ml_filter=None,
        strategy=None,
    ):
        self.exchange = exchange
        self.portfolio = portfolio
        self.risk = risk
        self.candle_duration_sec = candle_duration_sec
        self.paper = paper
        self.ml_filter = ml_filter
        self.strategy = strategy  # НОВЕ

    def process_symbol(
        self,
        symbol: str,
        indicators: dict,
        balance: float,
    ):
        """
        Повертає:
        (signal, reason, position_snapshot, risk_locked, cooldown)
        """

        # --- 1. RISK LOCK ---
        if not self.risk.can_trade():
            log_risk_block(symbol, "Daily risk lock")
            return ("HOLD", "Risk locked", self._snapshot_position(symbol), True, False)

        price = indicators.get("close")
        atr = indicators.get("atr")

        if price is None or atr is None:
            return None

        # --- 2. Управління відкритою позицією ---
        if self.portfolio.has_open_position(symbol):
            self._manage_open_position(symbol, price)
            return ("HOLD", "Managing open position", self._snapshot_position(symbol), False, False)

        # --- 3. Cooldown ---
        if self.portfolio.in_cooldown(symbol, self.candle_duration_sec):
            return ("HOLD", "Cooldown", self._snapshot_position(symbol), False, True)

        # --- 4. Strategy ---
        result: StrategyResult = self.strategy.evaluate(indicators)
        signal = result.signal
        reason = result.reason

        if signal != "BUY":
            return (signal, reason, self._snapshot_position(symbol), False, False)

        # --- 5. ML Filter (optional) ---
        if self.ml_filter:
            import pandas as pd
            features = pd.DataFrame([indicators])
            allow_ml = self.ml_filter.allow_trade(features)
            if not allow_ml:
                return ("HOLD", "ML blocked", self._snapshot_position(symbol), False, False)

        # --- 6. Position sizing ---
        params = self.risk.calculate_position(
            balance=balance,
            entry_price=price,
            atr=atr,
        )

        if not params:
            return ("HOLD", "Risk rejected position", self._snapshot_position(symbol), False, False)

        size = params["size"]
        stop_loss = params["stop_loss"]
        take_profit = params["take_profit"]

        # --- 7. BUY execution ---
        if not self.paper:
            order = self.exchange.place_buy(symbol, size)
            if not order:
                return ("HOLD", "Order failed", self._snapshot_position(symbol), False, False)

        self.portfolio.open_position(
            symbol=symbol,
            entry_price=price,
            size=size,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

        log_trade_open(
            symbol=symbol,
            side="BUY",
            price=price,
            size=size,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

        return ("BUY", reason, self._snapshot_position(symbol), False, False)

    def _manage_open_position(self, symbol: str, price: float):
        pos = self.portfolio.get_position(symbol)
        if not pos:
            return

        if price <= pos.stop_loss:
            self._close_position(symbol, price, "STOP_LOSS")

        elif price >= pos.take_profit:
            self._close_position(symbol, price, "TAKE_PROFIT")

    def _close_position(self, symbol: str, price: float, reason: str):
        pos = self.portfolio.get_position(symbol)
        if not pos:
            return

        if not self.paper:
            self.exchange.place_sell(symbol, pos.size)

        pnl_pct = self.portfolio.close_position(symbol, price, reason)
        self.risk.update_daily_pnl(pnl_pct)

        log_trade_close(
            symbol=symbol,
            side="SELL",
            price=price,
            pnl_pct=pnl_pct * 100,
            reason=reason,
        )

    def _snapshot_position(self, symbol: str):
        pos = self.portfolio.get_position(symbol)
        if not pos:
            return None

        return {
            "symbol": pos.symbol,
            "entry_price": pos.entry_price,
            "size": pos.size,
            "stop_loss": pos.stop_loss,
            "take_profit": pos.take_profit,
            "is_open": pos.is_open,
        }
