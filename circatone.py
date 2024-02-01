#!/usr/bin/env python3

import math
import random
import struct
import sys

# Write the "CD" format: signed 16 bit little endian, 44100 Hertz, stereo
SAMPLE_RATE = 44100
SAMPLE_FORMAT = struct.Struct("<hh")
TARGET_HZ = 391.995  # G4
STDDEV_CENTS = 80
DWELL_SECONDS = 0.13
AMPLITUDE = 6000


def generate_tone():
    phase = 0.0
    rng = random.Random()
    dwell_samples = int(round(DWELL_SECONDS * SAMPLE_RATE))
    print(f"Dwelling {dwell_samples / SAMPLE_RATE}s ({dwell_samples} samples) instead of requested {DWELL_SECONDS}s")
    while True:
        cents_this_block = rng.gauss(0.0, STDDEV_CENTS)
        hz_this_block = TARGET_HZ * 2 ** (cents_this_block / 1200)
        phase_per_sample = 2 * math.pi * hz_this_block / SAMPLE_RATE
        for _ in range(dwell_samples):
            phase += phase_per_sample
            phase %= 2 * math.pi
            yield int(round(AMPLITUDE * math.sin(phase)))


def run():
    for sample1, sample2 in zip(generate_tone(), generate_tone()):
        sys.stdout.buffer.write(SAMPLE_FORMAT.pack(sample1, sample2))


if __name__ == "__main__":
    run()
