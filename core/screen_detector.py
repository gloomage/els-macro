import time
import numpy as np
from PIL import ImageGrab


class ScreenDetector:

    def __init__(self, threshold: int = 20, confirm_seconds: float = 1.0):
        self.threshold = threshold          # média de brilho abaixo disso = preto
        self.confirm_seconds = confirm_seconds  # tempo mínimo para confirmar loading

    def get_screen_brightness(self) -> float:
        try:
            screenshot = ImageGrab.grab()
            pixels = np.array(screenshot)
            return float(pixels.mean())
        except Exception:
            return 255.0

    def is_black(self) -> bool:
        return self.get_screen_brightness() < self.threshold

    def wait_for_loading(self, stop_flag: list, timeout: int = 90) -> bool:
      
        black_since = None
        loading_confirmed = False
        deadline = time.time() + timeout

        while time.time() < deadline:
            if stop_flag[0]:
                return False

            if self.is_black():
                if black_since is None:
                    black_since = time.time()
                elif not loading_confirmed and (time.time() - black_since) >= self.confirm_seconds:
                    loading_confirmed = True
            else:
                if loading_confirmed:
                    return True
                black_since = None

            time.sleep(0.1)

        return False  # timeout
