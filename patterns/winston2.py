import colorsys
import math
import time

import matplotlib.pyplot as plt
import numpy as np

from audio_lib import SwhRecorder

from .Pattern import Color, Pattern


class WinstonPattern2(Pattern):
    def __init__(self, length: int, recorder: SwhRecorder, flip=False):
        super().__init__(length)
        self.recorder = recorder
        self.count = 0
        self.flip = flip

    def get_led_strip(self):
        self.count += 1
        xs, fft = self.recorder.fft()
        xs = xs[:600]
        fft = fft[:600]

        # bass is 6hz to 250 hz
        # fft
        mr = np.nan_to_num(fft)
        interpd = np.interp(
            np.linspace(0, len(mr), self.length), np.arange(len(mr)), mr
        )
        interpd /= np.max(interpd)
        # interpd = np.exp(interpd * 2 - 2)
        # interpd = np.clip(interpd, 0.02, 1)

        hues = np.ones((self.length))  # 600x1
        sats = np.ones((self.length))  # 600x1
        vals = np.ones((self.length))  # 600x1

        hues = (
            np.linspace(0.85 + self.count / 1000, 1.05 + self.count / 1000, self.length)
            % 0.15
        )
        hues = (hues - 0.8) % 1

        # vals = self.smooth(interpd)
        vals = interpd

        # self.strip = [Color(1, 0, 0, 0)] * self.length
        for i in range(self.length):
            r, g, b = colorsys.hsv_to_rgb(hues[i], sats[i], vals[i])
            if math.isnan(r):
                r = 0
            if math.isnan(g):
                g = 0
            if math.isnan(b):
                b = 0
            r = int(math.floor(r * 255))
            g = int(math.floor(g * 255))
            b = int(math.floor(b * 255))
            # print(r, g, b)

            prev = (self.strip[i].red, self.strip[i].green, self.strip[i].blue)

            rate = 0.1
            r = r * rate + prev[0] * (1 - rate)
            g = g * rate + prev[1] * (1 - rate)
            b = b * rate + prev[2] * (1 - rate)

            self.strip[i] = Color(int(r), int(g), int(b))

        if self.flip:
            return self.strip[::-1]

        return self.strip

    def update_available(self):
        return True

    def smooth(self, ar):
        return np.convolve(ar, np.ones(11) / 11)[5:-5]
