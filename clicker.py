import threading
import time
from pynput.mouse import Controller

class ClickerManager:
    def __init__(self):
        self.clicking = False
        self.click_thread = None
        self.listener_running = False
        self._simulating = False
        self._sim_lock = threading.Lock()
        self.cps_mode = "fixed"
        self.cps_fixed = 10.0
        self.cps_min = 5.0
        self.cps_max = 15.0
        self._runtime_cps_fixed = 10.0
        self._runtime_cps_min = 5.0
        self._runtime_cps_max = 15.0
        self.extra_click_interval = 1.0 / 19.0
    def click_loop(self, stop_event):
        while not stop_event.is_set():
            if not self.clicking:
                time.sleep(0.1)
                continue
            interval = self.get_next_interval()
            if interval is None:
                break
            with self._sim_lock:
                self._simulating = True
            try:
                Controller().click(Button.left)
            finally:
                with self._sim_lock:
                    self._simulating = False
            time.sleep(0.001)
            time.sleep(interval)
    def get_next_interval(self):
        try:
            if self.cps_mode == "fixed":
                return 1.0 / self.cps_fixed
            elif self.cps_mode == "random":
                return 1.0 / __import__("random").uniform(self.cps_min, self.cps_max)
            elif self.cps_mode == "adaptive":
                import random
                return 1.0 / random.uniform(self.cps_min, self.cps_max)
        except Exception:
            return None
    def start_clicking(self):
        self.clicking = True
        self._simulating = False
        stop_event = threading.Event()
        self.click_thread = threading.Thread(target=self.click_loop, args=(stop_event,), daemon=True)
        self.click_thread.start()
        return stop_event
    def stop_clicking(self):
        self.clicking = False
    def toggle_simulating(self):
        with self._sim_lock:
            self._simulating = not self._simulating
    def to_config(self):
        return {
            "cps_mode": self.cps_mode,
            "cps_fixed": self.cps_fixed,
            "cps_min": self.cps_min,
            "cps_max": self.cps_max,
        }
    def apply_config(self, config):
        self.cps_mode = config.get("cps_mode", "fixed")
        self.cps_fixed = float(config.get("cps_fixed", 10.0))
        self.cps_min = float(config.get("cps_min", 5.0))
        self.cps_max = float(config.get("cps_max", 15.0))
