# utils/logger.py

from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, level="DEBUG", format="{time} | {level} | {message}")

def log_event(msg: str):
    logger.info(f"[EVENT] {msg}")

def log_trade_open(symbol, side, price, amount):
    print(f"[TRADE OPEN] {symbol} | {side} | price={price} | amount={amount}")

def log_trade_close(symbol, side, price, amount, pnl):
    print(f"[TRADE CLOSE] {symbol} | {side} | price={price} | amount={amount} | pnl={pnl}")

def log_error(msg):
    print(f"[ERROR] {msg}")

def log_info(msg):
    print(f"[INFO] {msg}")

def log_risk_block(symbol, reason):
    print(f"[RISK BLOCK] {symbol} blocked: {reason}")
