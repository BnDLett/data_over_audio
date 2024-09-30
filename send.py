import time
from typing import Iterable
from __init__ import *

import pysine


def str_to_bin(text: str) -> str:
    return ''.join(format(ord(x), 'b') for x in text)


def play_binary(binary: Iterable, offset: int = 200) -> None:
    for bit in binary:
        do_offset = bit == "1"

        pysine.sine(base_frequency + (offset * do_offset), 1 / speed)


def transmit(binary: Iterable, offset: int = 200) -> None:
    pysine.sine(0, 2)  # Warm up the program.

    pysine.sine(CALL_FREQUENCY, 1 / speed)
    play_binary(binary, offset)
    pysine.sine(CALL_FREQUENCY, 1 / speed)


def main():
    binary = str_to_bin(SAMPLE_TEXT)

    print(f"Transmitting {len(binary)} bits.\n"
          f"Also known as {len(binary) / 8} bytes.")
    # for i in range(100):
    #     binary += str_to_bin("Hello, world!")

    start = time.time_ns()

    transmit(binary, up_frequency_offset)

    end = time.time_ns()

    print(f"Finished transmitting in {end - start} ns OR {(end - start) / 1e9} seconds. \n"
          f"Speed of ~{((len(binary) / (end - start)) * 1e9):.2f} bits per second.")


if __name__ == "__main__":
    # while True:
    main()
