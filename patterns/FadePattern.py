import time

from .Pattern import RAINBOW_COLOR, Color, Pattern


class FadePattern(Pattern):
    def __init__(self, length: int, interval: float, fade_steps: int = 100):
        super().__init__(length)
        self.current_color = 0
        self.step = 0
        self.fade_steps = fade_steps
        self.interval = interval
        self.last_updated = 0

    def get_led_strip(self):
        current_color = RAINBOW_COLOR[self.current_color]
        next_color = RAINBOW_COLOR[(self.current_color + 1) % 12]

        fade_color = Color(
            int(
                current_color.red
                + (next_color.red - current_color.red) * self.step / self.fade_steps
            ),
            int(
                current_color.green
                + (next_color.green - current_color.green) * self.step / self.fade_steps
            ),
            int(
                current_color.blue
                + (next_color.blue - current_color.blue) * self.step / self.fade_steps
            ),
        )

        self.strip = [fade_color] * self.length

        self.step += 1
        if self.step >= self.fade_steps:
            self.step = 0
            self.current_color = (self.current_color + 1) % 12

        self.last_updated = time.time()
        return self.strip

    def update_available(self):
        return time.time() - self.last_updated > self.interval
