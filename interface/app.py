import streamlit as st
import json
from pathlib import Path
import time

CONFIG_FILE = "runtime_config.json"

# ==========================
# Load / Save config
# ==========================

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


# ==========================
# Dark Theme CSS
# ==========================

DARK_CSS = """
<style>
body {
    background-color: #0b1020;
    color: #e3f2fd;
}
section.main > div {
    background-color: #0b1020;
}
div.stButton > button {
    background-color: #4fc3f7;
    color: black;
    border-radius: 6px;
    padding: 0.6em 1.2em;
    font-weight: bold;
}
div.block-container {
    padding-top: 2rem;
}
.panel {
    background-color: #182235;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}
.panel-title {
    color: #4fc3f7;
    font-size: 1.2rem;
    font-weight: bold;
}
.panel-sub {
    color: #b0bec5;
    font-size: 0.9rem;
}
</style>
"""

st.markdown(DARK_CSS, unsafe_allow_html=True)

# ==========================
# Load config
# ==========================

config = load_config()

st.title("🚀 Trading Bot Dashboard (Dark Mode)")

# ==========================
# BOT CONTROL
# ==========================

st.markdown("<div class='panel'>", unsafe_allow_html=True)
st.markdown("<div class='panel-title'>Bot Control</div>", unsafe_allow_html=True)

config["bot_enabled"] = st.toggle("Bot Enabled", config["bot_enabled"])
config["market_filter"] = st.toggle("Market Filter", config["market_filter"])
config["volume_filter"] = st.toggle("Volume Filter", config["volume_filter"])

st.markdown("</div>", unsafe_allow_html=True)

# ==========================
# RISK SETTINGS
# ==========================

st.markdown("<div class='panel'>", unsafe_allow_html=True)
st.markdown("<div class='panel-title'>Risk Settings</div>", unsafe_allow_html=True)

config["risk_per_trade"] = st.slider("Risk per trade", 0.001, 0.05, float(config["risk_per_trade"]))
config["sl_mult"] = st.slider("Stop Loss Multiplier", 0.5, 5.0, float(config["sl_mult"]))
config["tp_mult"] = st.slider("Take Profit Multiplier", 1.0, 10.0, float(config["tp_mult"]))

st.markdown("</div>", unsafe_allow_html=True)

# ==========================
# FILTER SETTINGS
# ==========================

st.markdown("<div class='panel'>", unsafe_allow_html=True)
st.markdown("<div class='panel-title'>Market Filters</div>", unsafe_allow_html=True)

config["min_volume_ratio"] = st.slider("Min Volume Ratio", 0.0, 2.0, float(config["min_volume_ratio"]))

st.markdown("</div>", unsafe_allow_html=True)

# ==========================
# SAVE BUTTON
# ==========================

if st.button("💾 Save Settings"):
    save_config(config)
    st.success("Saved!")

# ==========================
# LIVE BOT STATE (placeholder)
# ==========================

st.markdown("<div class='panel'>", unsafe_allow_html=True)
st.markdown("<div class='panel-title'>Live Bot State</div>", unsafe_allow_html=True)

st.markdown("<div class='panel-sub'>Це місце для живих даних від Trader</div>", unsafe_allow_html=True)

# Example placeholder
st.json({
    "price": 43250.2,
    "strategy_signal": "BUY",
    "market_filter": True,
    "risk_lock": False,
    "cooldown": False,
})

st.markdown("</div>", unsafe_allow_html=True)
