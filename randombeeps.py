#!/usr/bin/env python3

# Usage: python3 randombeeps.py | aplay -f cd

import math
import random
import struct
import sys

MIN_FREQ_HERTZ = 100
MAX_FREQ_HERTZ = 13000
# 5k is a nice background volume, 10k is a bit loud
MAX_AMPLITUDE = 7500

# We generate a polyphony of random tones, each swelling and ebbing:
NUM_TONES = 3
MIN_TONE_SECONDS = 1.10
MAX_TONE_SECONDS = 2.50

# Write the "CD" format: signed 16 bit little endian, 44100 Hertz, stereo
SAMPLE_RATE = 44100
SAMPLE_FORMAT = struct.Struct("<hh")
NUM_BUFFER_SAMPLES = 50

# Partial results that actually are constants:
MIN_TONE_SAMPLES = round(MIN_TONE_SECONDS * SAMPLE_RATE)
MAX_TONE_SAMPLES = round(MAX_TONE_SECONDS * SAMPLE_RATE)
RANGE_OCTAVES = math.log2(MAX_FREQ_HERTZ / MIN_FREQ_HERTZ)


class ToneBuffer:
    def __init__(self):
        self.sample_factor = 1
        self.remaining_samples = 0
        self.total_samples = 0

    def generate_sample(self):
        if self.remaining_samples == 0:
            self.total_samples = random.randrange(MIN_TONE_SAMPLES, MAX_TONE_SAMPLES + 1)
            self.remaining_samples = self.total_samples
            octaves = random.random() * RANGE_OCTAVES
            freq = MIN_FREQ_HERTZ * 2 ** octaves
            #print(f"{self.total_samples / SAMPLE_RATE:.3f} s, {freq:.1f} Hz", file=sys.stderr)
            self.sample_factor = freq / SAMPLE_RATE * 2 * math.pi
        # Note: Loudness is not linear in amplitude, in fact it is logarithmic in amplitude.
        # This means that a triangle amplitude already feels like it quickly reaches it
        # near-maximum loudness, plateus for a while, and then drops off quickly.
        # By using a sine wave, this is effect is made even more intense.
        sample = self.total_samples - self.remaining_samples
        self.remaining_samples -= 1
        amplitude = math.sin(math.pi * sample / self.total_samples) * MAX_AMPLITUDE
        phase = sample * self.sample_factor
        return amplitude * math.sin(phase)


def run():
    buffers_left = [ToneBuffer() for _ in range(NUM_TONES)]
    buffers_right = [ToneBuffer() for _ in range(NUM_TONES)]
    sample_buffer = []
    while True:
        sample_left = round(sum(buf.generate_sample() for buf in buffers_left) / NUM_TONES)
        sample_right = round(sum(buf.generate_sample() for buf in buffers_right) / NUM_TONES)
        sample_buffer.append(SAMPLE_FORMAT.pack(sample_left, sample_right))
        if len(sample_buffer) >= NUM_BUFFER_SAMPLES:
            sys.stdout.buffer.write(b"".join(sample_buffer))
            sample_buffer.clear()


if __name__ == "__main__":
    run()
