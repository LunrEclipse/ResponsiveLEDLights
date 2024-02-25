import colorsys
import math

import numpy as np

from audio_lib import SwhRecorder

from .Pattern import Color, Pattern


class WinstonPattern1(Pattern):
    def __init__(self, length: int, recorder: SwhRecorder, flip=False):
        super().__init__(length)
        self.recorder = recorder
        self.count = 0
        self.flip = flip

    def get_led_strip(self):
        xs, fft = self.recorder.fft()
        xs = xs[:600]
        fft = fft[:600]

        self.count += 1

        mr = np.nan_to_num(fft)
        interpd = np.interp(
            np.linspace(0, len(mr), self.length), np.arange(len(mr)), mr
        )
        interpd /= np.max(interpd)
        interpd = np.clip(interpd, 0.00, 1)

        hues = np.ones((self.length))  # 600x1
        sats = np.ones((self.length))  # 600x1
        vals = np.ones((self.length))  # 600x1

        sats = (
            np.linspace(0.85 + self.count / 500, 1.05 + self.count / 500, self.length)
            % 1
        )

        hues = (
            np.linspace(0.85 + self.count / 500, 1.05 + self.count / 500, self.length)
            % 1
        )
        vals = interpd

        # self.strip = [Color(1, 1, 1)] * self.length
        values = [
            list(colorsys.hsv_to_rgb(hues[i], sats[i], vals[i]))
            for i in range(self.length)
        ]
        for i in range(self.length):
            r, g, b = colorsys.hsv_to_rgb(hues[i], sats[i], vals[i])
            if math.isnan(r):
                r = 0
            if math.isnan(g):
                g = 0
            if math.isnan(b):
                b = 0
            r = max(math.floor(r * 255), 2)
            g = max(math.floor(g * 255), 2)
            b = max(math.floor(b * 255), 2)
            # print(r, g, b)

            self.strip[i] = Color(int(r), int(g), int(b))

        if self.flip:
            self.strip = self.strip[::-1]

        return self.strip

    def update_available(self) -> bool:
        return True
