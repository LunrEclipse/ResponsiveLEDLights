import time
from typing import Optional

import board
import matplotlib.pyplot as plt
import neopixel_spi
import numpy as np
import serial
import serial.tools.list_ports

from audio_lib import SwhRecorder
from patterns.Pattern import Color, Pattern

FIRST_WALL_END = 246
SECOND_WALL_END = 534

"""
Computer to Arduino Protocol:
24 bits per LED
[Red - 7 bits] [Control bit - 1 bit] [Green - 8 bits] [Blue - 8 bits]

If control bit is 1, then it is the beginning of the LED sequence
"""

BAUD_RATE = 115200
MAX_CHUNK_SIZE_BYTES = 60
STRIP_LENGTH = 900
SLEEP_TIME = 0.5


def get_ports():
    ports = serial.tools.list_ports.comports()
    ind = 0
    psec = {}
    for port, desc, hwid in sorted(ports):
        print(f"{ind}: {port}")
        psec[ind] = port
        ind += 1

    return psec


class LEDRunner:
    def __init__(
        self,
        strip_length: int,
        testing: bool = False,
        spi: Optional[board.SPI] = None,
        arduino: Optional[serial.Serial] = None,
    ):
        self.strip_length = strip_length
        self.testing = testing
        self.arduino = arduino
        self.spi = spi

        if self.spi:
            self.pixels = neopixel_spi.NeoPixel_SPI(
                spi,
                strip_length,
                pixel_order=neopixel_spi.GRB,
                auto_write=False,
                brightness=0.2,
            )
            self.pixels.fill(0)
            self.pixels.show()

        if self.testing:
            plt.ion()
            plt.figure(figsize=(18, 0.3))

        self.led_state: list[Color] = [Color(0, 0, 0)] * self.strip_length
        self.patterns: list[tuple[int, int, Pattern]] = []  # (begin, end, pattern)

    def add_pattern(self, begin: int, end: int, pattern_instance: Pattern):
        """
        This DOES NOT fails if a pattern exists in that region.
        If will just override the old pattern.
        """

        # assert that pattern instance does not exist
        for _, _, pat in self.patterns:
            assert pat != pattern_instance, "Pattern instance already added"

        assert (
            end - begin + 1 == pattern_instance.get_length()
        ), "Pattern length does not match"
        self.patterns.append((begin, end, pattern_instance))

        self.led_state[begin : end + 1] = pattern_instance.get_led_strip()

    def remove_pattern(self, pattern_instance: Pattern):
        for i in range(len(self.patterns)):
            if self.patterns[i][3] == pattern_instance:
                beg, end, pat = self.patterns.pop(i)
                for i in range(beg, end + 1):
                    self.led_state[i] = Color(0, 0, 0)
                return

        assert False, "Could not remove pattern that does not exist"

    def rasterize(self):
        for begin, end, pat in self.patterns:  # (begin, end, pattern)
            if pat.update_available():
                strip_output = pat.get_led_strip()

                assert (
                    len(strip_output) == end - begin + 1
                ), "Pattern returned wrong length"

                self.led_state[begin : end + 1] = strip_output

    def loop_step(self):
        self.rasterize()

        if self.testing:
            self.push_to_plot()

        if self.spi:
            self.push_to_spi()
        elif self.arduino:
            self.push_to_arduino()

    def loop(self):
        begin_time = time.time_ns()

        total_frames = 0
        while True:
            self.loop_step()
            total_frames += 1
            if total_frames % 50 == 0:
                print(1e9 * total_frames / (time.time_ns() - begin_time), "FPS")
            if total_frames == 100:
                total_frames = 0
                begin_time = time.time_ns()

    def push_to_plot(self):
        plt.clf()
        rgb_array = np.zeros((1, self.strip_length, 3), dtype=np.uint8)

        for i, led in enumerate(self.led_state):
            assert led.validate()
            rgb_array[0][i][0] = led.red
            rgb_array[0][i][1] = led.green
            rgb_array[0][i][2] = led.blue

        if np.max(rgb_array) > 1.0:
            rgb_array = rgb_array / 255.0

        # Scale the values if the image is too dark
        rgb_array = rgb_array * 1

        # Apply gamma correction
        gamma = 5
        rgb_array = np.power(rgb_array, 1 / gamma)

        # Ensure values are within [0, 1] after adjustments
        rgb_array = np.clip(rgb_array, 0, 1)

        rgb_array = np.repeat(rgb_array, 14, axis=1)
        rgb_array = np.repeat(rgb_array, 1, axis=0)

        plt.imshow(rgb_array, aspect="auto", alpha=1)
        plt.show()
        plt.pause(0.01)

    def push_to_spi(self):
        assert self.spi
        for i, led in enumerate(self.led_state):
            assert led.validate()
            self.pixels[i] = ((led.red << 16) + (led.green << 8) + led.blue).to_bytes(
                3, "big"
            )

        self.pixels.show()

    def push_to_arduino(self):
        byte_string = b""
        control = 0b1
        count = 0
        for led in self.led_state:
            assert led.validate()
            data_chunk = (
                (control << 16) + ((led.red >> 1) << 17) + (led.green << 8) + led.blue
            )

            data_chunk = data_chunk.to_bytes(3, "big")

            byte_string += data_chunk
            count += 3
            control = 0b0

            if count == MAX_CHUNK_SIZE_BYTES:
                self.arduino.write(byte_string)
                byte_string = b""

        if len(byte_string) > 0:
            self.arduino.write(byte_string)


def main():
    # psec = get_ports()
    # sel = int(input("Select Arduino Port: "))
    # sel=7
    # led_runner = LEDRunner(
    #     arduino=serial.Serial(port=psec[sel], baudrate=BAUD_RATE, timeout=0),
    #     strip_length=STRIP_LENGTH,
    # )

    led_runner = LEDRunner(spi=board.SPI(), strip_length=STRIP_LENGTH)
    # led_runner = LEDRunner(testing=True, strip_length=STRIP_LENGTH)

    recorder = SwhRecorder()
    time.sleep(0.5)

    from patterns.AlternatingPattern import AlternatingPattern
    from patterns.BassOnlyPattern import BassOnlyPattern
    from patterns.Beep import Beep
    from patterns.EpilepsyPattern import EpilepsyPattern
    from patterns.FadePattern import FadePattern
    from patterns.SnakeColorPattern import SnakeColorPattern

    snake_pattern_full = SnakeColorPattern(
        length=STRIP_LENGTH,
        snake_length=20,
        step=1,
        interval=0,
        color=Color(0, 255, 0),
    )
    # led_runner.add_pattern(0, STRIP_LENGTH - 1, snake_pattern_full)

    fade_pattern = FadePattern(length=247, interval=0, fade_steps=25)
    # led_runner.add_pattern(0, 246, fade_pattern)
    snake_pattern_second_wall = SnakeColorPattern(
        288,
        step=1,
        snake_length=30,
        color=Color(red=0, green=255, blue=0),
        interval=0,
    )
    # led_runner.add_pattern(247, 534, snake_pattern_second_wall)
    fade_pattern_2 = FadePattern(length=65, interval=0, fade_steps=25)
    # led_runner.add_pattern(535, 599, fade_pattern_2)
    epliepsy_pattern_third_wall = EpilepsyPattern(65, interval=0)
    # led_runner.add_pattern(535, 599, epliepsy_pattern_third_wall)

    # epilpesy = EpilepsyPattern(STRIP_LENGTH, interval=0)
    # led_runner.add_pattern(0, STRIP_LENGTH - 1, epilpesy)
    # fade_pattern = FadePattern(length=600, interval=SLEEP_TIME, fade_steps=25)
    # led_runner.add_pattern(0, 599, fade_pattern)
    # solid_pattern = SolidPattern(600, Color(255, 0, 0))
    # led_runner.add_pattern(0, 599, solid_pattern)
    beep_pattern = Beep(600, recorder=recorder)
    # led_runner.add_pattern(0, 599, beep_pattern)
    from patterns.winston1 import WinstonPattern1
    from patterns.winston2 import WinstonPattern2

    # WALL 1: 0 - 246 (247)
    # WALL 2: 247 - 534 (288)
    # WALL 3: 535 - 599 (65)
    # base_only_1 = BassOnlyPattern(length=247, recorder=recorder)
    # winston = WinstonPattern2(length=288, recorder=recorder)
    winston = WinstonPattern1(length=450, recorder=recorder)
    winston_flip = WinstonPattern1(length=450, recorder=recorder, flip=True)
    # base_only_2 = BassOnlyPattern(length=65, recorder=recorder)
    # led_runner.add_pattern(0, 246, base_only_1)
    led_runner.add_pattern(0, 449, winston_flip)
    led_runner.add_pattern(450, 899, winston)
    # led_runner.add_pattern(535, 599, base_only_2)
    bass_only = BassOnlyPattern(length=600, recorder=recorder)
    # led_runner.add_pattern(0, 599, bass_only)

    # winston = WinstonPattern2(length=300, recorder=recorder)
    winston_flip = WinstonPattern2(length=300, recorder=recorder, flip=True)
    # led_runner.add_pattern(0, 299, winston_flip)
    # led_runner.add_pattern(300, 599, winston)

    winston2 = WinstonPattern2(length=150, recorder=recorder)
    winston_flip2 = WinstonPattern2(length=150, recorder=recorder, flip=True)
    # led_runner.add_pattern(0, 149, winston)
    # led_runner.add_pattern(150, 299, winston_flip)
    # led_runner.add_pattern(300, 449, winston2)
    # led_runner.add_pattern(450, 599, winston_flip2)

    alternating_pattern = AlternatingPattern(length=STRIP_LENGTH, recorder=recorder)
    # led_runner.add_pattern(0, 599, alternating_pattern)

    # riseUp = RiseUp(length=600, recorder=recorder)
    # led_runner.add_pattern(0, 599, riseUp)

    led_runner.loop()


if __name__ == "__main__":
    main()
