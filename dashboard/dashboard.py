import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)

import streamlit as st
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
# 
from baskets.data_loader import fetch_binance_klines, klines_to_df
from core.data import prepare_market_data
from core.indicators import add_indicators
from backtest.metrics import equity_curve


CONFIG_FILE = "runtime_config.json"


# ------------------------------------------------------------
# CONFIG HANDLING
# ------------------------------------------------------------

def load_config():
    if not Path(CONFIG_FILE).exists():
        return {
            "bot_enabled": False,
            "market_filter": True,
            "volume_filter": False,
            "risk_per_trade": 0.01,
            "sl_mult": 1.5,
            "tp_mult": 3.0,
            "min_volume_ratio": 0.3,
        }
    return json.loads(Path(CONFIG_FILE).read_text())


def save_config(cfg):
    Path(CONFIG_FILE).write_text(json.dumps(cfg, indent=2))


config = load_config()


# ------------------------------------------------------------
# UI LAYOUT
# ------------------------------------------------------------

st.set_page_config(page_title="Trading Bot Dashboard", layout="wide")

st.title("🚀 Trading Bot Control Panel")


# ============================================================
# LEFT COLUMN — SETTINGS
# ============================================================

left, right = st.columns([1, 2])

with left:
    st.subheader("⚙️ Bot Settings")

    config["bot_enabled"] = st.toggle("Bot Enabled", config["bot_enabled"])
    config["market_filter"] = st.toggle("Market Filter", config["market_filter"])
    config["volume_filter"] = st.toggle("Volume Filter", config["volume_filter"])

    st.divider()
    st.subheader("📉 Risk Settings")

    config["risk_per_trade"] = st.slider(
        "Risk per trade",
        0.001, 0.05,
        float(config["risk_per_trade"])
    )

    config["sl_mult"] = st.slider(
        "Stop Loss Multiplier",
        0.5, 5.0,
        float(config["sl_mult"])
    )

    config["tp_mult"] = st.slider(
        "Take Profit Multiplier",
        1.0, 10.0,
        float(config["tp_mult"])
    )

    st.divider()
    st.subheader("📊 Market Filters")

    config["min_volume_ratio"] = st.slider(
        "Min Volume Ratio",
        0.0, 2.0,
        float(config["min_volume_ratio"])
    )

    if st.button("💾 Save Settings"):
        save_config(config)
        st.success("Saved!")


# ============================================================
# RIGHT COLUMN — BOT STATUS + CHARTS
# ============================================================

with right:
    st.subheader("🤖 Bot Status")

    # Load last candle for status
    try:
        klines = fetch_binance_klines("BTCUSDT", "15m", 200)
        df = klines_to_df(klines)
        df = prepare_market_data(df)
        df = add_indicators(df)
        df = df.dropna().reset_index(drop=True)

        last = df.iloc[-1]

        st.metric("Price", f"{last['close']:.2f} USDT")
        st.write(f"RSI: **{last['rsi']:.2f}**")
        st.write(f"MACD Histogram: **{last['macd_hist']:.4f}**")
        st.write(f"ATR: **{last['atr']:.2f}**")
        st.write(f"Volume Ratio: **{last['volume'] / last['volume_sma20']:.2f}**")

    except Exception as e:
        st.error(f"Cannot load live data: {e}")

    st.divider()
    st.subheader("📈 Technical Charts")

    # RSI Chart
    st.write("### RSI")
    fig_rsi, ax_rsi = plt.subplots(figsize=(8, 2))
    ax_rsi.plot(df["rsi"], label="RSI", color="purple")
    ax_rsi.axhline(30, color="green", linestyle="--")
    ax_rsi.axhline(70, color="red", linestyle="--")
    ax_rsi.set_title("RSI")
    st.pyplot(fig_rsi)

    # MACD Chart
    st.write("### MACD Histogram")
    fig_macd, ax_macd = plt.subplots(figsize=(8, 2))
    ax_macd.bar(df.index, df["macd_hist"], color="blue")
    ax_macd.set_title("MACD Histogram")
    st.pyplot(fig_macd)

    # Equity Curve (based on synthetic trades)
    st.write("### Equity Curve (Backtest Preview)")

    # Fake trades for preview (real backtest uses run_backtest.py)
    fake_trades = pd.DataFrame({
        "balance_after": 1000 + (df["close"].pct_change().fillna(0).cumsum() * 1000)
    })

    eq = equity_curve(fake_trades, 1000)

    fig_eq, ax_eq = plt.subplots(figsize=(8, 3))
    ax_eq.plot(eq, label="Equity", color="orange")
    ax_eq.set_title("Equity Curve (Preview)")
    st.pyplot(fig_eq)
