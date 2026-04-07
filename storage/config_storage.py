import json
import os

CONFIG_PATH = "config.json"

DEFAULTS = {
    "delay_max":        1.0,
    "wait_before_f8":   16,
    "wait_after_f8":    3,
    "wait_after_enter": 13,
    "screen_threshold": 15,
}


class ConfigStorage:

    def load(self) -> dict:
        if not os.path.exists(CONFIG_PATH):
            return dict(DEFAULTS)
        try:
            with open(CONFIG_PATH, 'r') as f:
                data = json.load(f)
            return {**DEFAULTS, **data}
        except Exception:
            return dict(DEFAULTS)

    def save(self, cfg: dict):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(cfg, f, indent=2)
