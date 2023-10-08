#!/usr/bin/env python3

import math
import struct
import sys

# Write the "CD" format: signed 16 bit little endian, 44100 Hertz, stereo
SAMPLE_RATE = 44100
SAMPLE_FORMAT = struct.Struct("<hh")
GEN_SECONDS = 1.5


def beep(frequency):
    amplitude = 3300000 / frequency
    #amplitude = 7500
    for sample in range(round(GEN_SECONDS * SAMPLE_RATE)):
        value = round(amplitude * math.sin(2 * math.pi * frequency / SAMPLE_RATE * sample))
        sys.stdout.buffer.write(SAMPLE_FORMAT.pack(value, value))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        beep(440)
    elif len(sys.argv) == 2:
        frequency = float(sys.argv[1])
        assert 100 <= frequency <= 13000, frequency
        beep(frequency)
    else:
        raise AssertionError()
