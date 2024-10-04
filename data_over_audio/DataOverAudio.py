import os
import time
import pysine
import numpy as np
import sounddevice as sd
from matplotlib import pyplot as plt

from .constants import *

from scipy.fft import (
    rfft,
    rfftfreq,
)
from data_over_audio.exceptions import (
    NegativeValue  # This is expected to eventually be multiple imports. Hence, the positioning of it.
)

from logging import Logger
from typing import Iterable


class DataOverAudio:
    __base_frequency__: int
    __frequency_step__: int
    __speed__: int

    logger: Logger

    UP_FREQUENCY: int
    CALL_FREQUENCY: int

    def __init__(self, base_frequency: int, frequency_step: int, speed: int, log_level: int = 1):
        f"""
        {DESCRIPTION}
        :param base_frequency: The base frequency in hertz.
        :param frequency_step: The rate at which the frequency steps up. The highest frequency is double the frequency
        step rate. For example, a base frequency of 3000 with a step-rate of 200 would have a maximum frequency of
        ~3400 Hz.
        :param speed: The speed at which the data will transmit at. This can be understood as bits per second.
        """

        self.set_base_frequency(base_frequency)
        self.set_frequency_step(frequency_step)
        self.set_speed(speed)

        self.logger = Logger("Data Over Audio Logger", level=log_level)

        self.UP_FREQUENCY = base_frequency + frequency_step
        self.CALL_FREQUENCY = self.UP_FREQUENCY + frequency_step

    # ---- STATIC METHODS ----
    # -- Utilities --

    @staticmethod
    def str_to_bin(text: str) -> str:
        return ''.join(format(ord(i), '08b') for i in text)

    @staticmethod
    def play_binary(base_frequency: int, speed: int, binary: Iterable, offset: int = 200) -> None:
        for bit in binary:
            do_offset = bit == "1"

            pysine.sine(base_frequency + (offset * do_offset), 1 / speed)

    @staticmethod
    def check_frequencies(sampling_rate, data, start_time: float, end_time: float, base_frequency: int,
                          up_frequency: int, call_frequency: int, threshold: int) -> int | None:
        # Open the file and convert to mono
        if data.ndim > 1:
            data = data[:, 0]
        else:
            pass

        # Return a slice of the data from start_time to end_time
        data_to_read = data[int(start_time * sampling_rate / 1000):int(end_time * sampling_rate / 1000) + 1]

        # Fourier Transform
        window_length = len(data_to_read)
        y_frequency: np.ndarray = rfft(data_to_read, n=window_length * 16)
        x_frequency: np.ndarray = rfftfreq(window_length * 16, 1 / sampling_rate)

        closest_base_frequency = np.argmin(np.abs(x_frequency - base_frequency)).item().real
        closest_up_frequency = np.argmin(np.abs(x_frequency - up_frequency)).item().real
        closest_call_frequency = np.argmin(np.abs(x_frequency - call_frequency)).item().real

        # os.system('clear')

        # print(f"up: {y_frequency[closest_up_frequency].item().real}\ndown: "
        #       f"{y_frequency[closest_base_frequency].item().real}\ncall: "
        #       f"{y_frequency[closest_call_frequency].item().real}")

        # print(x_frequency[closest_low_frequency])
        # print(x_frequency[closest_high_frequency])

        np.abs(y_frequency)

        abs_base = y_frequency[closest_base_frequency].item().real
        abs_up = y_frequency[closest_up_frequency].item().real
        abs_call = y_frequency[closest_call_frequency].item().real

        freq_dict = {
            0: abs_base,
            1: abs_up,
            2: abs_call,
        }

        highest = max(freq_dict, key=freq_dict.get)

        # print(freq_dict)
        # print(freq_dict[highest])
        # print(highest)

        # plt.clf()
        #
        # plt.title("Pitch intensities.")
        # plt.xlabel("Pitch")
        # plt.ylabel("Intensity")
        # plt.ylim(top=200)
        # plt.xlim(2500, 4500)
        #
        # plt.plot(x_frequency, np.abs(y_frequency))
        # plt.pause(0.0000001)  # did that because they won't let me use zero. 0/10 experience.

        return highest if freq_dict[highest] >= threshold else None

        # if y_frequency[closest_base_frequency] >= threshold:
        #     return 0
        # elif y_frequency[closest_up_frequency] >= threshold:
        #     return 1
        # elif y_frequency[closest_call_frequency] >= threshold:
        #     return 2

    @staticmethod
    def retrieve_sound(record_speed: int, sampling_rate: int = 44100):
        # print(f"SAMPLE FRAME RATE: {((1 / record_speed) * sampling_rate)}")
        result = sd.rec(int((1 / (record_speed * 2)) * sampling_rate), samplerate=sampling_rate, channels=1)
        sd.wait()
        return result

    @staticmethod
    def within_error(current_value: float, target_value: int, error: float):
        return (target_value - error) <= current_value <= (target_value + error)

    # -- Receiving --

    @staticmethod
    def receive_bit(probing: bool, transmitting_data: bool, base_frequency: int, up_frequency: int, call_frequency: int,
                    speed: int) -> tuple[bool, bool, int | None]:
        target_speed = speed + (((speed * 4) - speed) * probing)

        # print(target_speed)

        # target_high_frequency = call_frequency if probing else up_frequency
        sampling_rate = 48000
        result = DataOverAudio.retrieve_sound(target_speed, sampling_rate)

        frequency: int | None = DataOverAudio.check_frequencies(sampling_rate, result, 0,
                                                                (1 / (target_speed * 2)) * 1000,
                                                                base_frequency, up_frequency, call_frequency, 10)

        # print(type(frequency))

        # return probing transmitting_data bit

        # if probing and frequency and not transmitting_data:
        #     return True, True, None
        # elif probing and not frequency and not transmitting_data:
        #     return True, False, None

        if probing and frequency != 2 and not transmitting_data:
            return True, False, None
        elif probing and frequency == 2 and not transmitting_data:
            return True, True, None
        elif not probing and transmitting_data and frequency == 2:
            return False, False, None

        result = frequency if frequency != 2 else None

        # binary_str += '0' if within_error(frequency.item(), base_frequency, error_margin) else '1'

        # binary_list.append(int(within_error(frequency.item(), base_frequency + up_frequency_offset, error_margin)))

        return False, True, result
        # print(set(sorted(frequencies, key=float)))

    @staticmethod
    def receive_data_stream(base_frequency: int, up_frequency: int, call_frequency: int, speed: int) -> list[int]:
        binary_list: list[int] = []
        probe, transmitted_data = True, False

        while probe or transmitted_data:
            start = time.time()
            probe, transmitted_data, binary = DataOverAudio.receive_bit(probe, transmitted_data, base_frequency,
                                                                        up_frequency, call_frequency,
                                                                        speed)
            end = time.time()

            if binary is not None:
                binary_list.append(binary)

            record_error_margin = end - start

            target_sleep_duration = ((1 / speed) - record_error_margin) * (not probe)
            sleep_duration = target_sleep_duration if target_sleep_duration >= 0 else 0
            print(sleep_duration)
            time.sleep(sleep_duration)
        return binary_list

    # ---- SETTERS ----

    def set_base_frequency(self, new_value: int):
        if new_value < 0:
            return NegativeValue("The error margin that was provided is a negative number.")

        self.__base_frequency__ = new_value

    def set_frequency_step(self, new_value: int):
        if new_value < 0:
            return NegativeValue("The error margin that was provided is a negative number.")

        self.__frequency_step__ = new_value

    def set_error_margin(self, new_value: int):
        if new_value > (self.__frequency_step__ / 2):
            return ValueError(
                f"The error margin provided is too large. Maximum allowed is {self.__frequency_step__ / 2} Hz."
                f" If you wish to increase the error margin, then increase your frequency step.")
        elif new_value < 0:
            return NegativeValue("The error margin that was provided is a negative number.")

        self.__error_margin__ = new_value

    def set_speed(self, new_value: int):
        if new_value < 0:
            return NegativeValue("The error margin that was provided is a negative number.")

        self.__speed__ = new_value

    # ---- GETTERS ----

    def get_base_frequency(self) -> int:
        return self.__base_frequency__

    def get_frequency_step(self) -> int:
        return self.__frequency_step__

    def get_error_margin(self) -> int:
        return self.__error_margin__

    def get_speed(self) -> int:
        return self.__speed__

    # ---- NON-STATIC METHODS ----
    # -- Transmitting --

    def transmit(self, binary: Iterable) -> None:
        pysine.sine(0, 0.5)  # Warm up the program.

        pysine.sine(self.CALL_FREQUENCY, 1 / self.__speed__)
        self.play_binary(self.__base_frequency__, self.__speed__, binary, self.__frequency_step__)
        pysine.sine(self.CALL_FREQUENCY, 1 / self.__speed__)

    def transmit_text(self, text: str):
        binary_text = self.str_to_bin(text)
        self.transmit(binary_text)

    # -- Receiving --

    def receive(self) -> list[int]:
        binary: list[int] = self.receive_data_stream(self.__base_frequency__, self.UP_FREQUENCY, self.CALL_FREQUENCY,
                                                     self.__speed__)

        return binary
