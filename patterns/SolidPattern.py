from .Pattern import Color, Pattern


class SolidPattern(Pattern):
    def __init__(self, length: int, color: Color):
        super().__init__(length)
        for i in range(0, self.length):
            self.strip[i] = color

    def get_led_strip(self):
        return self.strip

    def update_available(self):
        return False
