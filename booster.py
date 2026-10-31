import random
import time
from PyQt6.QtWidgets import QLabel

class BoosterManager:
    def __init__(self):
        self.extra_click_interval = 1.0 / 19.0
        self.booster_left_enabled = False
        self.booster_left_hotkey_display = "1"
        self.booster_left_count = 2
        self.booster_left_min = 1
        self.booster_left_max = 3
        self.booster_left_use_random = False
        self.booster_left_status = None
        self.booster_left_hotkey_label = None
        self.booster_right_enabled = False
        self.booster_right_hotkey_display = "2"
        self.booster_right_count = 2
        self.booster_right_min = 1
        self.booster_right_max = 3
        self.booster_right_use_random = False
        self.booster_right_status = None
        self.booster_right_hotkey_label = None
    def _update_booster_status(self, side):
        if side == "left":
            enabled = self.booster_left_enabled
            label = self.booster_left_status
        else:
            enabled = self.booster_right_enabled
            label = self.booster_right_status
        if label is None:
            return
        label.setText("开启" if enabled else "关闭")
        label.setStyleSheet("color: #a6e3a1; font-weight: 600;" if enabled else "color: #f38ba8; font-weight: 600;")
    def toggle_booster_left(self):
        self.booster_left_enabled = not self.booster_left_enabled
        self._update_booster_status("left")
    def toggle_booster_right(self):
        self.booster_right_enabled = not self.booster_right_enabled
        self._update_booster_status("right")
    def on_left_random_toggle(self, enabled):
        self.booster_left_use_random = bool(enabled)
    def on_right_random_toggle(self, enabled):
        self.booster_right_use_random = bool(enabled)
    def get_booster_total(self, side):
        if side == "left":
            if self.booster_left_use_random:
                import random
                return random.randint(self.booster_left_min, self.booster_left_max)
            return self.booster_left_count
        else:
            if self.booster_right_use_random:
                import random
                return random.randint(self.booster_right_min, self.booster_right_max)
            return self.booster_right_count
    def perform_booster_click(self, button, total_clicks, _closing_flag):
        if total_clicks <= 1:
            return
        from pynput.mouse import Controller
        controller = Controller()
        for i in range(total_clicks - 1):
            if _closing_flag:
                break
            time.sleep(self.extra_click_interval)
            controller.click(button)
    def to_config(self):
        return {
            "booster_left_enabled": self.booster_left_enabled,
            "booster_left_hotkey": self.booster_left_hotkey_display,
            "booster_left_count": self.booster_left_count,
            "booster_left_min": self.booster_left_min,
            "booster_left_max": self.booster_left_max,
            "booster_left_use_random": self.booster_left_use_random,
            "booster_right_enabled": self.booster_right_enabled,
            "booster_right_hotkey": self.booster_right_hotkey_display,
            "booster_right_count": self.booster_right_count,
            "booster_right_min": self.booster_right_min,
            "booster_right_max": self.booster_right_max,
            "booster_right_use_random": self.booster_right_use_random,
        }
    def apply_config(self, config):
        self.booster_left_enabled = bool(config.get("booster_left_enabled", False))
        self.booster_left_count = int(config.get("booster_left_count", 2))
        self.booster_left_min = int(config.get("booster_left_min", 1))
        self.booster_left_max = int(config.get("booster_right_max", 3))
        self.booster_left_use_random = bool(config.get("booster_left_use_random", False))
        self._update_booster_status("left")
        self.booster_right_enabled = bool(config.get("booster_right_enabled", False))
        self.booster_right_count = int(config.get("booster_right_count", 2))
        self.booster_right_min = int(config.get("booster_right_min", 1))
        self.booster_right_max = int(config.get("booster_right_max", 3))
        self.booster_right_use_random = bool(config.get("booster_right_use_random", False))
        self._update_booster_status("right")
