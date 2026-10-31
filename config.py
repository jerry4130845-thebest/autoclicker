import json
import os
from typing import Optional, Dict, Any

CONFIG_FILE = "option.txt"

DEFAULT_CONFIG = {
    "cps_mode": "fixed",
    "cps_fixed": 10.0,
    "cps_min": 5.0,
    "cps_max": 15.0,
    "click_button": "left",
    "auto_hotkey": "F6",
    "booster_left_enabled": False,
    "booster_left_hotkey": "1",
    "booster_left_count": 2,
    "booster_left_min": 1,
    "booster_left_max": 3,
    "booster_left_use_random": False,
    "booster_right_enabled": False,
    "booster_right_hotkey": "2",
    "booster_right_count": 2,
    "booster_right_min": 1,
    "booster_right_max": 3,
    "booster_right_use_random": False,
}

class ConfigManager:
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file

    def save(self, config_dict: Dict[str, Any]) -> None:
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=4, ensure_ascii=False)

    def load(self) -> Optional[Dict[str, Any]]:
        if not os.path.exists(self.config_file):
            return None
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def get_default_config(self) -> Dict[str, Any]:
        return DEFAULT_CONFIG.copy()