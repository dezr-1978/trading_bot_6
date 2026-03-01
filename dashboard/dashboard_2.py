# dashboard/dashboard.py

import streamlit as st
import json
from pathlib import Path

CONFIG_FILE = "runtime_config.json"


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

st.title("🚀 Trading Bot Control Panel")

config["bot_enabled"] = st.toggle("Bot Enabled", config["bot_enabled"])
config["market_filter"] = st.toggle("Market Filter", config["market_filter"])
config["volume_filter"] = st.toggle("Volume Filter", config["volume_filter"])

st.divider()

st.subheader("Risk Settings")

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

st.subheader("Market Filters")

config["min_volume_ratio"] = st.slider(
    "Min Volume Ratio",
    0.0, 2.0,
    float(config["min_volume_ratio"])
)

if st.button("💾 Save Settings"):
    save_config(config)
    st.success("Saved!")
