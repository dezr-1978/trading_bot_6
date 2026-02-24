import sys
from loguru import logger
from pathlib import Path


def setup_logger(
    log_file: str = "logs/bot.log",
    level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "14 days",
):
    """
    Налаштовує глобальний логер для всього проєкту
    """

    # Створюємо папку logs, якщо її нема
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Видаляємо стандартний логер
    logger.remove()

    # Лог у консоль
    logger.add(
        sys.stdout,
        level=level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )

    # Лог у файл
    logger.add(
        log_file,
        level=level,
        rotation=rotation,
        retention=retention,
        compression="zip",
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name}:{function}:{line} - "
            "{message}"
        ),
    )

    logger.info("Logger initialized successfully")


# ===== ДОПОМІЖНІ ЛОГ-ФУНКЦІЇ =====

def log_trade_open(symbol, side, price, size, sl, tp):
    logger.info(
        f"[TRADE OPEN] {symbol} | {side} | "
        f"price={price:.4f} size={size:.6f} "
        f"SL={sl:.4f} TP={tp:.4f}"
    )


def log_trade_close(symbol, side, price, pnl, reason):
    logger.info(
        f"[TRADE CLOSE] {symbol} | {side} | "
        f"exit_price={price:.4f} "
        f"PNL={pnl:.2f}% reason={reason}"
    )


def log_signal(symbol, signal, reason):
    logger.debug(
        f"[SIGNAL] {symbol} | signal={signal} | reason={reason}"
    )


def log_risk_block(symbol, reason):
    logger.warning(
        f"[RISK BLOCK] {symbol} | reason={reason}"
    )


def log_error(message, exception: Exception | None = None):
    if exception:
        logger.exception(f"[ERROR] {message}")
    else:
        logger.error(f"[ERROR] {message}")