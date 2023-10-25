#!/usr/bin/env python3

import argparse
import math
import struct
import sys


def halftones(rel):
    return 2 ** (rel / 12)


# Write the "CD" format: signed 16 bit little endian, 44100 Hertz, stereo
SAMPLE_RATE = 44100
SAMPLE_FORMAT = struct.Struct("<hh")
SECS_PARTS = (0.1, 0.1, 0.8, 0.5)  # Attack, sustain, decay, silence
#BASE_AMPLITUDE = 6000
BASE_AMPLITUDE = 1193  # FIXME?!
FREQ_BASE = 880
FREQ_FACTORS = [1.0, halftones(-5), halftones(-8), halftones(-12), halftones(-12-5), halftones(-12-8), halftones(-24), halftones(-24-5), halftones(-24-8)]
#FREQ_FACTORS = [1.0]

PHI = (1 + math.sqrt(5)) / 2
SAMPLES_PARTS = [
    round(part * SAMPLE_RATE)
    for part in SECS_PARTS[:-1]
]
SAMPLE_DURATIONS_PER_VOICE = [
    round(sum(SECS_PARTS) * SAMPLE_RATE * PHI ** i) for i in range(len(FREQ_FACTORS))
]
print(f"Ding will be off by {round(sum(SECS_PARTS[:-1]) * SAMPLE_RATE) - sum(SAMPLES_PARTS)} samples in length (not period)", file=sys.stderr)
MAX_AMPLITUDE = sum(1 / freq for freq in FREQ_FACTORS)
print(f"Max amplitude will be {BASE_AMPLITUDE} * {MAX_AMPLITUDE} = {BASE_AMPLITUDE * MAX_AMPLITUDE} <= {2 ** 15}", file=sys.stderr)
assert BASE_AMPLITUDE * MAX_AMPLITUDE < 2 ** 15


def init_vec():
    return [SAMPLE_DURATIONS_PER_VOICE[0]] * len(FREQ_FACTORS)


def compute_single_sample(freq_factor, sample_i):
    # print(f"{freq_factor=} {sample_i=}", file=sys.stderr)
    attack, sustain, decay = SAMPLES_PARTS
    if sample_i < attack:
        # We're attacking!
        stage_amplitude = sample_i / attack
    elif sample_i < attack + sustain:
        # We're sustaining!
        stage_amplitude = 1.0
    elif sample_i < attack + sustain + decay:
        # We're decaying!
        stage_amplitude = 1.0 - (sample_i - attack - sustain) / decay
    else:
        return 0.0
    phase = sample_i * 2 * math.pi * FREQ_BASE * freq_factor / SAMPLE_RATE
    voice_sample = stage_amplitude * (1 / freq_factor) * math.sin(phase)
    #print(f"{stage_amplitude=} {freq_factor=} {voice_sample=}", file=sys.stderr)
    return voice_sample


def compute_sample(state_vec):
    assert len(state_vec) == len(FREQ_FACTORS) == len(SAMPLE_DURATIONS_PER_VOICE)
    # print(f"Computing sample for {state_vec=} …", file=sys.stderr)
    return BASE_AMPLITUDE * sum(compute_single_sample(freq_factor, sample_i) for freq_factor, sample_i in zip(FREQ_FACTORS, state_vec))


def advance_state(state_vec):
    for i in range(len(state_vec)):
        state_vec[i] += 1
        state_vec[i] %= SAMPLE_DURATIONS_PER_VOICE[i]


def iteration(state_vec):
    sample_value = round(compute_sample(state_vec))
    sys.stdout.buffer.write(SAMPLE_FORMAT.pack(sample_value, sample_value))
    advance_state(state_vec)


def run(num_secs):
    state_vec = init_vec()
    if num_secs is None:
        while True:
            iteration(state_vec)
    elif num_secs is not None:
        num_samples = round(num_secs * SAMPLE_RATE + 0.5)
        for _ in range(num_samples):
            iteration(state_vec)


def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("num_secs", type=float, nargs='?', default=None)
    return parser


if __name__ == "__main__":
    run(make_parser().parse_args().num_secs)
