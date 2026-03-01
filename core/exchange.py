# core/exchange.py

from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
from loguru import logger
from typing import List, Optional, Dict, Any

from core.data import prepare_market_data
from core.indicators import add_indicators, latest_indicators
from utils.validation import validate_candles, validate_indicators


class BinanceExchange:
    """
    Обгортка над Binance API.
    Відповідає за:
    - отримання свічок
    - отримання балансу
    - виконання ордерів
    - підготовку індикаторів для трейдера
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        testnet: bool = False,
        request_timeout: int = 10,
    ):
        self.client = Client(
            api_key,
            api_secret,
            testnet=testnet
        )
        self.client.REQUEST_TIMEOUT = request_timeout

        logger.info("[EXCHANGE] Binance client initialized")

    # ============================================================
    # MARKET DATA
    # ============================================================

    def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 500
    ) -> List[list]:
        """
        Отримує сирі свічки з Binance.
        Повертає список списків або [] у разі помилки.
        """
        try:
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            return klines

        except Exception as e:
            logger.exception(f"[EXCHANGE] Failed to fetch klines for {symbol}")
            return []

    # ============================================================
    # BALANCE
    # ============================================================

    def get_balance(self, asset: str = "USDT") -> float:
        """
        Повертає доступний баланс у вказаному asset.
        """
        try:
            balance = self.client.get_asset_balance(asset=asset)
            free = float(balance["free"])
            logger.debug(f"[EXCHANGE] Balance {asset}: {free}")
            return free

        except Exception:
            logger.exception("[EXCHANGE] Failed to fetch balance")
            return 0.0

    # ============================================================
    # ORDERS
    # ============================================================

    def place_buy(
        self,
        symbol: str,
        quantity: float
    ) -> Optional[Dict[str, Any]]:
        """
        Market BUY (spot).
        """
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=round(quantity, 6)
            )
            logger.info(f"[EXCHANGE] BUY order placed | {symbol} qty={quantity}")
            return order

        except Exception:
            logger.exception(f"[EXCHANGE] BUY order failed | {symbol}")
            return None

    def place_sell(
        self,
        symbol: str,
        quantity: float
    ) -> Optional[Dict[str, Any]]:
        """
        Market SELL (spot).
        """
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=round(quantity, 6)
            )
            logger.info(f"[EXCHANGE] SELL order placed | {symbol} qty={quantity}")
            return order

        except Exception:
            logger.exception(f"[EXCHANGE] SELL order failed | {symbol}")
            return None

    # ============================================================
    # INDICATORS PIPELINE
    # ============================================================

    def get_latest_indicators(
        self,
        symbol: str,
        timeframe: str,
        lookback: int = 200,
    ) -> Optional[Dict[str, float]]:
        """
        Повертає останні індикатори для трейдингу.
        Повний pipeline:
        1) get_klines
        2) prepare_market_data
        3) validate_candles
        4) add_indicators
        5) validate_indicators
        6) latest_indicators
        """

        # 1. Raw klines
        klines = self.get_klines(
            symbol=symbol,
            interval=timeframe,
            limit=lookback + 50,
        )

        if not klines:
            return None

        # 2. Convert to DataFrame
        df = prepare_market_data(klines, lookback)

        # 3. Validate candles
        if not validate_candles(df):
            return None

        # 4. Add indicators
        df = add_indicators(df)

        # 5. Validate indicators
        required = [
            "ema50",
            "ema200",
            "rsi",
            "macd_hist",
            "atr",
            "volume",
            "volume_sma20",
        ]

        if not validate_indicators(df, required):
            return None

        # 6. Return last row as dict
        return latest_indicators(df)
