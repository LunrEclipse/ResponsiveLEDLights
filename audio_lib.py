import threading
import time

import numpy as np
import pyaudio


class SwhRecorder:
    """Simple, cross-platform class to record from the microphone."""

    def __init__(self):
        """minimal garb is executed when class is loaded."""
        self.rate = 44100
        SECS_TO_RECORD = 0.3
        self.buffer_size = 2**10  # 1024 is a good buffer size
        self.fft_result = (np.array([]), np.array([]))

        """initialize sound card."""
        # TODO - windows detection vs. alsa or something for linux
        # TODO - try/except for sound card selection/initiation

        self.buffers_to_record = int(self.rate * SECS_TO_RECORD / self.buffer_size)
        assert self.buffers_to_record > 0, "Buffers to record not greater than 0"

        self.pyaudio = pyaudio.PyAudio()

        audio_devices = []
        for i in range(self.pyaudio.get_device_count()):
            audio_device_info = self.pyaudio.get_device_info_by_index(i)
            audio_devices.append(f"{i}. {audio_device_info['name']} with {audio_device_info['maxOutputChannels']} output channels")

        source_idx = None
        for i in range(len(audio_devices)):
            audio_device_info = self.pyaudio.get_device_info_by_index(i)
            if "BlackHole" in audio_device_info["name"]:
                source_idx = i
                break

        if source_idx is None:
            print('\n'.join(audio_devices))
            source_idx = int(input('Choose Channel: '))

        self.instream = self.pyaudio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.buffer_size,
            input_device_index=source_idx,
        )

        self.thread = threading.Thread(target=self.record)
        self.thread.start()

    def close(self):
        """cleanly back out and release sound card."""
        self.pyaudio.close(self.instream)

    ### RECORDING AUDIO ###

    def get_audio(self):
        """get a single buffer size worth of audio."""
        audio_bytes = self.instream.read(self.buffer_size, False)
        return np.frombuffer(audio_bytes, dtype=np.int16)

    def record(self):
        """record secToRecord seconds of audio."""
        audio = np.empty((self.buffers_to_record * self.buffer_size), dtype=np.int16)

        for i in range(self.buffers_to_record):
            audio[
                i * self.buffer_size : (i + 1) * self.buffer_size
            ] = self.get_audio()

        while True:
            audio = np.roll(audio, -self.buffer_size)

            audio[
                (self.buffers_to_record - 1)
                * self.buffer_size : self.buffers_to_record
                * self.buffer_size
            ] = self.get_audio()
            
            xs, fft_output = self._fft(audio.flatten())
            self.fft_result = self.downsample(xs, fft_output, 8)

    ### MATH ###

    def downsample(self, xs, fft_output, mult):
        """Downsample the 1D FFT output and take the lowest frequency value of each bin in xs."""

        # Check if downsampling factor is larger than the length of the data
        if mult > len(fft_output):
            raise ValueError(
                "Downsampling factor must be less than the length of the FFT output"
            )

        # Downsampling the FFT output
        overhang = len(fft_output) % mult
        if overhang:
            fft_output = fft_output[:-overhang]
        reshaped_fft_output = np.reshape(fft_output, (-1, mult))
        downsampled_fft_output = np.mean(reshaped_fft_output, axis=1)

        # Taking the lowest frequency value in each bin for xs
        downsampled_xs = xs[::mult][: len(downsampled_fft_output)]

        return downsampled_xs, downsampled_fft_output

    def _fft(self, data, trimBy=1, logScale=False, divBy=100):
        # Perform FFT
        fft_result = np.fft.fft(data)
        fft_magnitude = np.abs(fft_result)

        # Use only the first half of the FFT output, as it's symmetrical for real inputs
        half_length = len(fft_result) // 2
        fft_magnitude = fft_magnitude[:half_length]

        # Frequency bins
        xs = np.linspace(0, self.rate / 2, half_length, endpoint=False)

        # Optional logarithmic scaling
        if logScale:
            fft_magnitude = np.multiply(20, np.log10(fft_magnitude))

        # Optional trimming
        if trimBy:
            i = int(half_length / trimBy)
            fft_magnitude = fft_magnitude[:i]
            xs = xs[:i]

        # Optional division by a value
        if divBy:
            fft_magnitude = fft_magnitude / float(divBy)

        return xs, fft_magnitude

    def fft(self):
        return self.fft_result

    def fft_mean(self, low_freq: int, high_freq: int):
        """
        Calculate the mean of the FFT output between low_freq and high_freq.

        :param low_freq: The lower bound of the frequency range.
        :param high_freq: The upper bound of the frequency range.
        :return: Mean of the FFT output between low_freq and high_freq.
        """
        xs, fft_outputs = self.fft_result

        # Validate frequencies
        if low_freq < xs[0] or high_freq > xs[-1]:
            raise ValueError("Frequency bounds are outside the range of the data.")
        if low_freq > high_freq:
            raise ValueError("Low frequency must be less than high frequency.")

        # Find the indices that correspond to the low and high frequency
        low_idx = np.searchsorted(xs, low_freq, side="left")
        high_idx = np.searchsorted(xs, high_freq, side="right")

        # Calculate and return the mean of the FFT output in the specified range
        mean_fft = np.mean(fft_outputs[low_idx:high_idx])

        return mean_fft


def main():
    import matplotlib.pyplot as plt

    plt.ion()
    plt.figure(figsize=(10, 5))
    plt.axis()

    while True:
        recorder = SwhRecorder()

        while True:
            plt.pause(0.005)
            plt.clf()
            plt.ylim(0, 50000)
            plt.xlim(-250, 20000)

            begin_time = time.time_ns()
            xs, fft = recorder.fft()
            # print(len(fft))

            end_time = time.time_ns()
            # print("FFT TIME", (end_time - begin_time) / 1e6, "ms")

            plt.fill_between(xs, fft)
            # plt.fill_between(np.arange(50), fft_buckets)
            plt.show()


if __name__ == "__main__":
    main()
