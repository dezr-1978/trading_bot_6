import os

# ================= API =================

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# ================= TRADING MODE =================

DEMO_MODE = True
START_BALANCE = 1000.0

SETTINGS = {
    "mode": "paper",     # paper / real
    "symbols": ["BTCUSDT"],
    "timeframe": "5m",
    "candle_duration_sec": 300,
}

# ================= RISK =================

RISK_PER_TRADE = 0.01
MAX_POSITIONS = 3