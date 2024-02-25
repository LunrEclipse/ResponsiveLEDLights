import time

from .Pattern import Color, Pattern


class BreathingPattern(Pattern):
    def __init__(
        self, length: int, interval: float, color: Color, range=100
    ):
        super().__init__(length)
        self.color = color
        self.interval = interval
        self.last_updated = 0
        self.step = 1
        self.range = range
        self.increasing = True

    def get_led_strip(self):
        self.strip = [Color(0, 0, 0)] * self.length
        for i in range(0, self.length, 2):
            current_color = self.color
            current_color.red = (current_color.red * self.step // self.range)
            current_color.green = (current_color.green * self.step // self.range)
            current_color.blue = (current_color.blue * self.step // self.range)
            self.strip[i] = current_color
        
        if self.increasing:
            self.step += 1
            if self.step >= self.range:
                self.increasing = False
        else:
            self.step -= 1
            if self.step <= 1:
                self.increasing = True

        self.last_updated = time.time()
        return self.strip

    def update_available(self):
        return time.time() - self.last_updated > self.interval
