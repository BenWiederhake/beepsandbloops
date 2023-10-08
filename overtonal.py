#!/usr/bin/env python3

# Usage: python3 overtonal.py | aplay -f cd

import math
import random
import struct
import sys

BASE_FREQ = 220
NUM_OVERTONES = 10
STEP_BPM = 100

# 5k is a nice background volume, 10k is a bit loud
MAX_AMPLITUDE = 6000

# Write the "CD" format: signed 16 bit little endian, 44100 Hertz, stereo
SAMPLE_RATE = 44100
SAMPLE_FORMAT = struct.Struct("<hh")
NUM_BUFFER_SAMPLES = 50
RUNUP_SAMPLES = 440

# Precompute some values
STEP_SAMPLES = round(SAMPLE_RATE * 60 / STEP_BPM)

# Buggy sample: 188970


class OvertoneState:
    def __init__(self, factor):
        assert 1 <= factor <= NUM_OVERTONES
        self.frequency = BASE_FREQ * factor
        self.old_amplitude = 0
        self.new_amplitude = MAX_AMPLITUDE if factor == 1 else 0

    def generate_sample(self, sample_in_cycle, total_sample):
        assert sample_in_cycle < STEP_SAMPLES
        sample_amplitude = self.old_amplitude + (self.new_amplitude - self.old_amplitude) * sample_in_cycle / STEP_SAMPLES
        phase = 2 * math.pi * self.frequency * total_sample / SAMPLE_RATE
        return sample_amplitude * math.sin(phase)


def reroll_amplitude_vector():
    # The actual range of valid values of the amplitude for factor i goes from 0 to MAX_AMPLITUDE / factor.
    # By "valid" I mean: This way we can nicely map sine, square, triangle and sawtooth waves, without anything terribly exotic.
    unscaled_amplitudes = []
    for factor in range(1, 1 + NUM_OVERTONES):
        unscaled_amplitudes.append(MAX_AMPLITUDE ** random.random())
    # The *sum* of all amplitudes is the amplitude of the overall signal, which we would like to normalize also to roughly MAX_AMPLITUDE,
    # in case we randomly have a very quiet or very loud signal.
    scale_factor = MAX_AMPLITUDE / sum(unscaled_amplitudes)
    amplitudes = [e * scale_factor / (1 + i) for i, e in enumerate(unscaled_amplitudes)]
    return amplitudes


def run():
    buffers = [OvertoneState(i) for i in range(1, 1 + NUM_OVERTONES)]
    sample_buffer = []
    total_sample = 0
    # Slight run-up so that we don't start with a click:
    for sample in range(-RUNUP_SAMPLES, 0):
        amplitude = MAX_AMPLITUDE ** ((sample + RUNUP_SAMPLES) / RUNUP_SAMPLES)
        phase = 2 * math.pi * BASE_FREQ * sample / SAMPLE_RATE
        sample_value = round(amplitude * math.sin(phase))
        sample_buffer.append(SAMPLE_FORMAT.pack(sample, sample))
    while True:
        sample_in_cycle = total_sample % STEP_SAMPLES
        if sample_in_cycle == 0:
            for overtone, new_amplitude in zip(buffers, reroll_amplitude_vector()):
                overtone.old_amplitude = overtone.new_amplitude
                overtone.new_amplitude = new_amplitude
        sample = round(sum(buf.generate_sample(sample_in_cycle, total_sample) for buf in buffers))
        sample_buffer.append(SAMPLE_FORMAT.pack(sample, sample))
        if len(sample_buffer) >= NUM_BUFFER_SAMPLES:
            sys.stdout.buffer.write(b"".join(sample_buffer))
            sample_buffer.clear()
        total_sample += 1


if __name__ == "__main__":
    run()
