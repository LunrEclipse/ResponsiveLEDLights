import colorsys
import math
import time

import matplotlib.pyplot as plt
import numpy as np

from audio_lib import SwhRecorder

from .Pattern import Color, Pattern


class RiseUp(Pattern):
    def __init__(self, length: int, recorder: SwhRecorder, flip=False):
        super().__init__(length)
        self.recorder = recorder
        self.count = 0
        self.flip = flip

    def get_led_strip(self):
        self.count += 1
        # plt.xticks([])
        # plt.yticks([])
        # begin = time.time_ns()
        xs, fft = self.recorder.fft()
        # fft_buckets = bucket_average(fft[:1000])
        # end = time.time_ns()
        # print("fft time: ", (end - begin) / 1e6)
        # bass is 6hz to 250 hz
        bass = self.recorder.fft_mean(low_freq=60, high_freq=250)
        # print(bass)
        if bass > 4e4:
            # print("hit")
            r = np.random.randint(0, 256)
            g = np.random.randint(0, 256)
            b = np.random.randint(0, 256)
            for i in range(self.length):
                self.strip[i] = Color(r, g, b)
            return self.strip
        else:
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
                np.linspace(
                    0.85 + self.count / 500, 1.05 + self.count / 500, self.length
                )
                % 1
            )
            vals = self.smooth(interpd)

            self.strip = [Color(0, 0, 0)] * self.length
            for i in range(self.length):
                r, g, b = colorsys.hsv_to_rgb(hues[i], sats[i], vals[i])
                if math.isnan(r):
                    r = 0
                if math.isnan(g):
                    g = 0
                if math.isnan(b):
                    b = 0
                r = math.floor(r * 255)
                g = math.floor(g * 255)
                b = math.floor(b * 255)
                # print(r, g, b)

                self.strip[i] = Color(int(r), int(g), int(b))

            if self.flip:
                self.strip = self.strip[::-1]

            return self.strip

    def update_available(self):
        return True

    def smooth(self, ar):
        return np.convolve(ar, np.ones(11) / 11)[5:-5]
