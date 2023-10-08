#!/usr/bin/env python3

import math
import struct
import sys

# Write the "CD" format: signed 16 bit little endian, 44100 Hertz, stereo
SAMPLE_RATE = 44100
SAMPLE_FORMAT = struct.Struct("<hh")
GEN_SECONDS = 1.5
FREQ_A = 440
FREQ_B = 660
MAX_AMPLITUDE = 7500
TOTAL_SAMPLES = round(GEN_SECONDS * SAMPLE_RATE)

for sample in range(TOTAL_SAMPLES):
    amp_a = MAX_AMPLITUDE * (TOTAL_SAMPLES - sample) / TOTAL_SAMPLES
    amp_b = MAX_AMPLITUDE * sample / (1.5 * TOTAL_SAMPLES)
    value_a = amp_a * math.sin(2 * math.pi * FREQ_A / SAMPLE_RATE * sample)
    value_b = amp_b * math.sin(2 * math.pi * FREQ_B / SAMPLE_RATE * sample)
    value = round(value_a + value_b)
    sys.stdout.buffer.write(SAMPLE_FORMAT.pack(value, value))
