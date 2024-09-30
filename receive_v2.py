import time

import numpy as np

import send
from __init__ import *

import sounddevice as sd

from scipy.fft import *


def freq(sr, data, start_time: float, end_time: float):
    # Open the file and convert to mono
    if data.ndim > 1:
        data = data[:, 0]
    else:
        pass

    # Return a slice of the data from start_time to end_time
    dataToRead = data[int(start_time * sr / 1000):int(end_time * sr / 1000) + 1]

    # Fourier Transform
    N = len(dataToRead)
    yf = rfft(dataToRead)
    xf = rfftfreq(N, 1 / sr)

    # Uncomment these to see the frequency spectrum as a plot
    # plt.plot(xf, np.abs(yf))
    # plt.show()

    # Get the most dominant frequency and return it
    idx = np.argmax(np.abs(yf))
    freq = xf[idx]
    return freq


def retrieve_sound(record_speed: int, sampling_rate: int = 44100):
    # print(f"SAMPLE FRAME RATE: {((1 / record_speed) * sampling_rate)}")
    result = sd.rec(int((1 / (record_speed * 2)) * sampling_rate), samplerate=sampling_rate, channels=1)
    sd.wait()
    return result


def within_error(current_value: float, target_value: int, error: float):
    return (target_value - error) <= current_value <= (target_value + error)


def loop(probing: bool, transmitting_data: bool, binary_list: list):
    target_speed = speed + (((speed * 4) - speed) * probing)

    # print(target_speed)

    sampling_rate = 48000
    result = retrieve_sound(target_speed, sampling_rate)
    frequency: np.float64 = freq(sampling_rate, result, 0, (1 / (target_speed * 2)) * 1000)

    within_call_error = within_error(frequency.item(), CALL_FREQUENCY, error_margin)

    print(frequency.item())

    if probing and not within_call_error and not transmitting_data:
        return True, False, binary_list
    elif probing and within_call_error and not transmitting_data:
        return True, True, binary_list
    elif not probing and transmitting_data and within_call_error:
        return False, False, binary_list

    if within_error(frequency.item(), UP_FREQUENCY, error_margin):
        binary_list.append(1)
    elif within_error(frequency.item(), base_frequency, error_margin):
        binary_list.append(0)

    # binary_str += '0' if within_error(frequency.item(), base_frequency, error_margin) else '1'

    # binary_list.append(int(within_error(frequency.item(), base_frequency + up_frequency_offset, error_margin)))

    return False, True, binary_list
    # print(set(sorted(frequencies, key=float)))


def main():
    probe = True
    binary: list[int] = []
    transmitted_data = False
    record_error_margin = 0.0

    start, end = 0.0, 0.0

    try:
        while probe or transmitted_data:
            start = time.time()
            probe, transmitted_data, binary = loop(probe, transmitted_data, binary)
            # print(record_error_margin)
            end = time.time()

            record_error_margin = end - start
            time.sleep(((1 / speed) - record_error_margin) * (not probe))
    except KeyboardInterrupt:
        pass

    print(error_margin)
    print(''.join(str(x) for x in binary))
    print(send.str_to_bin(SAMPLE_TEXT))
    print(len(binary))


if __name__ == "__main__":
    main()
