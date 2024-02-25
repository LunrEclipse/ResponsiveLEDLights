import math
import time

import matplotlib.pyplot as plt
import numpy as np

from audio_lib import SwhRecorder

from .Pattern import Color, Pattern

SOUND_MIN = 1e3
BASE_SOUND_MAX = 1e5  # 3e5

BASS_COLORS = [
    Color(255, 0, 0),
    Color(255, 127, 0),
    Color(238, 175, 97),
    Color(106, 13, 131),
    Color(102, 0, 204),
    Color(0, 0, 255),
]


class BassOnlyPattern(Pattern):
    def __init__(self, length: int, recorder: SwhRecorder):
        super().__init__(length)
        self.recorder = recorder
        self.bass_color = 0
        self.base_step = 0
        self.base_fade_step = 200

    def get_led_strip(self):
        xs, fft = self.recorder.fft()

        bass = np.mean(fft[:12])

        current_bass_color = BASS_COLORS[self.bass_color]
        next_bass_color = BASS_COLORS[(self.bass_color + 1) % len(BASS_COLORS)]
        bass_color = Color(
            int(
                current_bass_color.red
                + (next_bass_color.red - current_bass_color.red)
                * self.base_step
                / self.base_fade_step
            ),
            int(
                current_bass_color.green
                + (next_bass_color.green - current_bass_color.green)
                * self.base_step
                / self.base_fade_step
            ),
            int(
                current_bass_color.blue
                + (next_bass_color.blue - current_bass_color.blue)
                * self.base_step
                / self.base_fade_step
            ),
        )
        self.base_step += 1
        if self.base_step >= self.base_fade_step:
            self.base_step = 0
            self.bass_color = (self.bass_color + 1) % len(BASS_COLORS)

        if bass > BASE_SOUND_MAX:
            for i in range(0, self.length):
                self.strip[i] = bass_color
        else:
            for i in range(0, self.length):
                self.strip[i] = Color(
                    int((0.15) * (bass / BASE_SOUND_MAX) * bass_color.red),
                    int((0.15) * (bass / BASE_SOUND_MAX) * bass_color.green),
                    int((0.15) * (bass / BASE_SOUND_MAX) * bass_color.blue),
                )

        return self.strip

    def update_available(self):
        return True
