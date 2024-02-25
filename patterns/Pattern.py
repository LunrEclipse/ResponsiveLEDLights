from dataclasses import dataclass


@dataclass
class Color:
    red: int
    green: int
    blue: int

    def __hash__(self):
        return (self.red << 16) + (self.green << 8) + self.blue

    def validate(self) -> bool:
        return (
            self.red < 256
            and self.green < 256
            and self.blue < 256
            and self.red >= 0
            and self.green >= 0
            and self.blue >= 0
            and type(self.red) == int
            and type(self.green) == int
            and type(self.blue) == int
        )


RAINBOW_COLOR = [
    Color(255, 0, 0),
    Color(255, 127, 0),
    Color(255, 255, 0),
    Color(127, 255, 0),
    Color(0, 255, 0),
    Color(0, 255, 127),
    Color(0, 255, 255),
    Color(0, 127, 255),
    Color(0, 0, 255),
    Color(127, 0, 255),
    Color(255, 0, 255),
    Color(255, 0, 127),
]


class Pattern:
    """this is a super class"""

    def __init__(self, length: int):
        self.length = length
        self.strip = [Color(0, 0, 0) for _ in range(length)]

    def get_led_strip(self):
        """Return a list of colors of length self.length"""
        raise NotImplementedError()

    def update_available(self) -> bool:
        """
        Return whether or not there is a new LED strip output.
        get_led_strip() will only be called if this method returns true
        """
        raise NotImplementedError()

    def get_length(self) -> int:
        return self.length
