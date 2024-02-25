import math
import time

import matplotlib.pyplot as plt
import numpy as np

from audio_lib import SwhRecorder

from .Pattern import Color, Pattern

SOUND_MIN = 1e3
BASE_SOUND_MAX = 30000  # 3e5

BASS_COLORS = [
    Color(255, 0, 0),  # RED
    Color(255, 127, 0),  # ORANGE
    Color(0, 153, 0),  # DARK GREEN
    Color(0, 0, 255),  # DARK BLUE
    Color(102, 0, 204),  # DARK PURPLE
]

plt.ion()


def bucket_average(arr, num_buckets=50):
    # if len(arr) != 1024:
    #     raise ValueError("Array must be of size 1024")

    # Reshape the array to have 'num_buckets' rows
    reshaped_arr = arr.reshape(num_buckets, -1)

    # Compute the average of each bucket
    bucket_averages = np.mean(reshaped_arr, axis=1)

    return bucket_averages


class AlternatingPattern(Pattern):
    def __init__(self, length: int, recorder: SwhRecorder):
        super().__init__(length)
        self.recorder = recorder
        self.bass_alt = False

        self.bass_color = 0
        self.bass_hit = False
        self.bass_last_hit = 0

        self.treble_color = 0

    # def bass_hit(self):
    #     r = np.random.randint(0, 256)
    #     g = np.random.randint(0, 256)
    #     b = np.random.randint(0, 256)
    #     for i in range(0, self.length // 2):
    #         self.strip[i] = Color(r, g, b)

    def get_led_strip(self):
        bass = self.recorder.fft_mean(low_freq=60, high_freq=250)
        treble = self.recorder.fft_mean(low_freq=5000, high_freq=10000)

        if bass > 35000:
            # self.bass_hit()
            bass_color = BASS_COLORS[self.bass_color]
            if treble < 4000:
                bass_color = Color(255, 0, 0)
            for i in range(0, self.length, 2):
                self.strip[i] = bass_color
            self.bass_hit = True
            self.bass_last_hit = time.time()
        elif self.bass_hit and time.time() - self.bass_last_hit > 1:
            self.bass_hit = False
            self.bass_color = (self.bass_color + 1) % len(BASS_COLORS)
        else:
            for i in range(0, self.length, 2):
                self.strip[i] = Color(
                    int(
                        (0.15)
                        * (bass / BASE_SOUND_MAX)
                        * BASS_COLORS[self.bass_color].red
                    ),
                    int(
                        (0.15)
                        * (bass / BASE_SOUND_MAX)
                        * BASS_COLORS[self.bass_color].green
                    ),
                    int(
                        (0.15)
                        * (bass / BASE_SOUND_MAX)
                        * BASS_COLORS[self.bass_color].blue
                    ),
                )

        color_intensity = int(max(min((treble / 8000) * 50, 50), 10)) + 10
        treble_color = Color(color_intensity, color_intensity, color_intensity)
        for i in range(1, self.length, 2):
            self.strip[i] = treble_color

        return self.strip

    def update_available(self):
        return True
