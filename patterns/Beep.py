import numpy as np

from audio_lib import SwhRecorder

from .Pattern import Color, Pattern


class Beep(Pattern):
    def __init__(self, length: int, recorder):
        self.length = length
        self.strip = [Color(0, 0, 0) for _ in range(length)]
        self.recorder = recorder

    def get_led_strip(self) -> list[Color]:
        """Return a list of colors of length self.length"""
        # xs, fft = self.recorder.fft()
        # bass is 6hz to 250 hz
        bass = self.recorder.fft_mean(60, 250)
        print(bass)
        if bass > 42000:
            # print("hit")
            r = np.random.randint(0, 256)
            g = np.random.randint(0, 256)
            b = np.random.randint(0, 256)
            for i in range(self.length):
                self.strip[i] = Color(r, g, b)
        else:
            for i in range(self.length):
                self.strip[i] = Color(5, 5, 5)
        return self.strip

    def update_available(self) -> bool:
        """
        Return whether or not there is a new LED strip output.
        get_led_strip() will only be called if this method returns true
        """
        return True
