from loguru import logger

from baskets.data_loader import fetch_binance_klines, klines_to_df
from core.data import prepare_market_data
from core.indicators import add_indicators
from core.execution import Trader
from core.portfolio import Portfolio
from core.risk import RiskManager
from core.market_filter import MarketFilter, MarketFilterConfig
from core.config import load_runtime_config
from core.state import BotState
from utils.logger import log_event


class DummyExchange:
    def __init__(self, balance_usdt: float = 1000.0):
        self._balance = balance_usdt

    def get_balance(self):
        return self._balance

    def place_buy(self, symbol: str, size: float):
        log_event(f"Dummy BUY {symbol} size={size}")
        return {"status": "FILLED"}

    def place_sell(self, symbol: str, size: float):
        log_event(f"Dummy SELL {symbol} size={size}")
        return {"status": "FILLED"}


def build_trader(symbol: str = "BTCUSDT", interval: str = "15m", limit: int = 500) -> Trader:
    cfg = load_runtime_config()

    klines = fetch_binance_klines(symbol, interval, limit)
    df = klines_to_df(klines)
    df = prepare_market_data(df)
    df = add_indicators(df)
    df = df.dropna().reset_index(drop=True)

    exchange = DummyExchange(balance_usdt=1000.0)

    portfolio = Portfolio(cooldown_candles=3)

    risk = RiskManager(
        risk_per_trade=cfg.risk_per_trade,
        max_daily_loss=0.05,
        atr_sl_multiplier=cfg.sl_mult,
        atr_tp_multiplier=cfg.tp_mult,
        min_rr_ratio=1.5,
    )

    market_filter = MarketFilter(
        MarketFilterConfig(
            min_volume_ratio=cfg.min_volume_ratio
        )
    )

    settings = {
        "symbols": [symbol],
        "timeframe": interval,
    }

    trader = Trader(
        exchange=exchange,
        market_filter=market_filter if cfg.market_filter else None,
        portfolio=portfolio,
        risk=risk,
        settings=settings,
        candle_duration_sec=15 * 60,
        ml_filter=None,
        paper=True,
    )

    trader.set_initial_df(symbol, df)
    return trader


if __name__ == "__main__":
    logger.info("=== Starting Trading Bot (Full Pro Architecture) ===")

    trader = build_trader("BTCUSDT", "15m", 500)

    trader.process()
    state: BotState = trader.get_state()

    print("\n=== BOT STATE ===")
    print(state.to_dict() if hasattr(state, "to_dict") else state)
