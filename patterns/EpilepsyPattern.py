import random
import time

from .Pattern import RAINBOW_COLOR, Color, Pattern


class EpilepsyPattern(Pattern):
    def __init__(self, length: int, interval: float):
        super().__init__(length)
        self.current_color = 0
        self.interval = interval
        self.last_updated = 0

    def get_led_strip(self):
        self.strip = [
            Color(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
        ] * self.length
        # self.strip = [RAINBOW_COLOR[self.current_color]] * self.length
        self.current_color = (self.current_color + 1) % 12
        self.last_updated = time.time()
        return self.strip

    def update_available(self):
        return time.time() - self.last_updated > self.interval
