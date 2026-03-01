import json
from dataclasses import dataclass
from pathlib import Path

CONFIG_FILE = "runtime_config.json"


DEFAULT_RUNTIME_CONFIG = {
    "bot_enabled": False,
    "market_filter": True,
    "volume_filter": False,
    "risk_per_trade": 0.01,
    "sl_mult": 1.5,
    "tp_mult": 3.0,
    "min_volume_ratio": 0.3,
}


@dataclass
class RuntimeConfig:
    bot_enabled: bool
    market_filter: bool
    volume_filter: bool
    risk_per_trade: float
    sl_mult: float
    tp_mult: float
    min_volume_ratio: float


def load_runtime_config() -> RuntimeConfig:
    if not Path(CONFIG_FILE).exists():
        cfg = DEFAULT_RUNTIME_CONFIG.copy()
        return RuntimeConfig(**cfg)

    try:
        raw = json.loads(Path(CONFIG_FILE).read_text())
    except Exception:
        raw = DEFAULT_RUNTIME_CONFIG.copy()

    merged = DEFAULT_RUNTIME_CONFIG.copy()
    merged.update(raw)

    return RuntimeConfig(**merged)


def save_runtime_config(cfg: RuntimeConfig):
    data = {
        "bot_enabled": cfg.bot_enabled,
        "market_filter": cfg.market_filter,
        "volume_filter": cfg.volume_filter,
        "risk_per_trade": cfg.risk_per_trade,
        "sl_mult": cfg.sl_mult,
        "tp_mult": cfg.tp_mult,
        "min_volume_ratio": cfg.min_volume_ratio,
    }

    Path(CONFIG_FILE).write_text(json.dumps(data, indent=2))
