#!/usr/bin/env python3

# Usage: python3 intonate.py | aplay -f cd

import math
import struct
import sys

# Write the "CD" format: signed 16 bit little endian, 44100 Hertz, stereo
SAMPLE_RATE = 44100
SAMPLE_FORMAT = struct.Struct("<hh")

SAMPLES_ATTACK = 400
SAMPLES_SUSTAIN = 5000
SAMPLES_DECAY = 800
AMPLITUDE = 8000
BASE_FREQUENCY_HERTZ = 247  # "B3"
LETTER_NAMES = [
    "B3",
    "C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
    "C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5",
    "C6",
]
assert len(LETTER_NAMES) == 26

SENTENCE = "HELLO WORLD I LOVE YOU VERY DEARLY HOW ARE YOU TODAY"


def compute_sample(t, amplitude, freq):
    frac_value = math.sin((t / SAMPLE_RATE) * freq * 2 * math.pi)
    value = round(amplitude * frac_value)
    return SAMPLE_FORMAT.pack(value, value)


def beep_tone(letter):
    freq = BASE_FREQUENCY_HERTZ * (2 ** (letter / 12))
    for i in range(SAMPLES_ATTACK):
        yield compute_sample(i, AMPLITUDE * (i + 1) / SAMPLES_ATTACK, freq)
    for i in range(SAMPLES_SUSTAIN):
        yield compute_sample(SAMPLES_ATTACK + i, AMPLITUDE, freq)
    for i in range(SAMPLES_DECAY):
        yield compute_sample(SAMPLES_ATTACK + SAMPLES_SUSTAIN + i, AMPLITUDE * (SAMPLES_DECAY - i) / SAMPLES_DECAY, freq)


def beep_wait():
    single_sample = SAMPLE_FORMAT.pack(0, 0)
    yield single_sample * (SAMPLES_ATTACK + SAMPLES_SUSTAIN + SAMPLES_DECAY)


def beep_sentence(sentence):
    for letter in sentence.upper():
        if "A" <= letter <= "Z":
            letter_index = ord(letter) - ord("A")
            print(f"{letter} -> {LETTER_NAMES[letter_index]}", file=sys.stderr)
            yield from beep_tone(letter_index)
        elif letter == " ":
            yield from beep_wait()
        else:
            raise AssertionError(f"Unknown letter >>{letter}<<!")


def run():
    ms_attack = 1000 * SAMPLES_ATTACK / SAMPLE_RATE
    ms_sustain = 1000 * SAMPLES_SUSTAIN / SAMPLE_RATE
    ms_decay = 1000 * SAMPLES_DECAY / SAMPLE_RATE
    print(
        f"Each beep will be {ms_attack:.0f} + {ms_sustain:.0f} + {ms_decay:.0f} = {ms_attack + ms_sustain + ms_decay:.0f} ms long.",
        file=sys.stderr,
    )
    data = b"".join(beep_sentence(SENTENCE))
    sys.stdout.buffer.write(data)


if __name__ == "__main__":
    run()
