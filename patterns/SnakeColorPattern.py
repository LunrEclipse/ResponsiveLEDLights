import time

from .Pattern import Color, Pattern


class SnakeColorPattern(Pattern):
    def __init__(
        self, length: int, snake_length: int, step: int, interval: float, color: Color
    ):
        super().__init__(length)
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
                self.current_pos + 1, self.current_pos + self.snake_length + 1
            ):
                current_color = self.color
                current_color.red -= (self.current_pos + self.snake_length - i) * (
                    self.color.red // self.snake_length
                )
                current_color.green -= (self.current_pos + self.snake_length - i) * (
                    self.color.green // self.snake_length
                )
                current_color.blue -= (self.current_pos + self.snake_length - i) * (
                    self.color.blue // self.snake_length
                )
                self.strip[i] = current_color
            # self.strip[self.current_pos] = Color(0, 0, 0, 0)

            self.current_pos += self.step
            if self.current_pos + self.snake_length >= self.length:
                self.going_forward = False
                self.current_pos -= self.step
        else:
            self.strip = [Color(0, 0, 0)] * self.length
            for i in range(self.current_pos, self.current_pos + self.snake_length):
                current_color = self.color
                current_color.red -= (i - self.current_pos) * (
                    self.color.red // self.snake_length
                )
                current_color.green -= (i - self.current_pos) * (
                    self.color.green // self.snake_length
                )
                current_color.blue -= (i - self.current_pos) * (
                    self.color.blue // self.snake_length
                )
                self.strip[i] = current_color
            # self.strip[self.current_pos + self.snake_length] = Color(0, 0, 0)

            self.current_pos -= self.step
            if self.current_pos < 0:
                self.going_forward = True
                self.current_pos += self.step

        self.last_updated = time.time()
        return self.strip

    def update_available(self):
        return time.time() - self.last_updated > self.interval
