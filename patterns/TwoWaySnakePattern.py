import time

from .Pattern import Color, Pattern


class TwoWaySnakePattern(Pattern):
    def __init__(
        self, length: int, snake_length: int, step: int, interval: float, color: Color
    ):
        super().__init__(length)
        self.center = length // 2
        self.current_pos = 0
        self.snake_length = snake_length
        self.step = step
        self.color = color
        self.going_forward = True
        self.interval = interval
        self.last_updated = 0

    def get_led_strip(self):
        if self.going_forward:
            self.strip = [Color(0, 0, 0)] * self.length
            for i in range(
                self.center + self.current_pos, self.center + self.current_pos + self.snake_length + 1
            ):
                self.strip[i] = self.color
            for i in range(self.center - self.current_pos, min(self.current_pos + self.snake_length - self.current_pos, self.center)):
                self.strip[i] = self.color
            self.current_pos += self.step
            if self.current_pos + self.snake_length + self.center >= self.length:
                self.going_forward = False
                self.current_pos -= self.step
        else:
            self.strip = [Color(0, 0, 0)] * self.length
            for i in range(self.current_pos, self.current_pos + self.snake_length):
                self.strip[i] = self.color
            for i in range(self.center + self.current_pos, min(self.center + self.current_pos + self.snake_length, self.length)):
                self.strip[i] = self.color

            self.current_pos -= self.step
            if self.current_pos < 0:
                self.going_forward = True
                self.current_pos += self.step

        self.last_updated = time.time()
        return self.strip

    def update_available(self):
        return time.time() - self.last_updated > self.interval
