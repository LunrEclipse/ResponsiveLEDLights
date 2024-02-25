import math
import time

import matplotlib.pyplot as plt
import numpy as np

from audio_lib import SwhRecorder

from .Pattern import Color, Pattern

BASE_SOUND_MAX = 1e5  # 3e5

class BassOnlyPattern(Pattern):
    def __init__(self, length: int, color: Color, recorder: SwhRecorder):
        super().__init__(length)
        self.recorder = recorder
        self.color = color
        self.cur = 0

    def get_led_strip(self):
        xs, fft = self.recorder.fft(trimBy=1)

        bass = np.mean(fft[:12])

        if bass > BASE_SOUND_MAX:
            for i in range(0, self.cur, 2):
                self.strip[i] = self.color
            if self.cur < self.length:
                self.cur += 4
                if self.length < self.cur:
                    self.cur = self.length
        else:
            for i in range(0, self.length):
                self.strip[i] = Color(
                    0,
                    int((0.15) * (bass / BASE_SOUND_MAX) * self.color.red),
                    int((0.15) * (bass / BASE_SOUND_MAX) * self.color.green),
                    int((0.15) * (bass / BASE_SOUND_MAX) * self.color.blue),
                )

        return self.strip

    def update_available(self):
        return True
