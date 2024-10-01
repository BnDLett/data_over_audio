import time
import pysine
import numpy as np
import sounddevice as sd
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
    __error_margin__: int
    __speed__: int

    logger: Logger

    UP_FREQUENCY: int
    CALL_FREQUENCY: int

    def __init__(self, base_frequency: int, frequency_step: int, error_margin: int, speed: int, log_level: int = 1):
        f"""
        {DESCRIPTION}
        :param base_frequency: The base frequency in hertz.
        :param frequency_step: The rate at which the frequency steps up. The highest frequency is double the frequency
        step rate. For example, a base frequency of 3000 with a step-rate of 200 would have a maximum frequency of
        ~3400 Hz.
        :param error_margin: The margin of error for the frequency. Generally speaking, this shouldn't go above half the
        step frequency.
        :param speed: The speed at which the data will transmit at. This can be understood as bits per second.
        """

        self.set_base_frequency(base_frequency)
        self.set_frequency_step(frequency_step)
        self.set_error_margin(error_margin)
        self.set_speed(speed)

        self.logger = Logger("Data Over Audio Logger", level=log_level)

        self.UP_FREQUENCY = base_frequency + frequency_step
        self.CALL_FREQUENCY = self.UP_FREQUENCY + frequency_step


    # ---- STATIC METHODS ----

    @staticmethod
    def str_to_bin(text: str) -> str:
        return ''.join(format(ord(x), 'b') for x in text)

    @staticmethod
    def play_binary(base_frequency: int, speed: int, binary: Iterable, offset: int = 200) -> None:
        for bit in binary:
            do_offset = bit == "1"

            pysine.sine(base_frequency + (offset * do_offset), 1 / speed)

    @staticmethod
    def freq(sr, data, start_time: float, end_time: float):
        # Open the file and convert to mono
        if data.ndim > 1:
            data = data[:, 0]
        else:
            pass

        # Return a slice of the data from start_time to end_time
        data_to_read = data[int(start_time * sr / 1000):int(end_time * sr / 1000) + 1]

        # Fourier Transform
        n = len(data_to_read)
        yf = rfft(data_to_read)
        xf = rfftfreq(n, 1 / sr)

        # Uncomment these to see the frequency spectrum as a plot
        # plt.plot(xf, np.abs(yf))
        # plt.show()

        # Get the most dominant frequency and return it
        idx = np.argmax(np.abs(yf))
        freq = xf[idx]
        return freq

    @staticmethod
    def retrieve_sound(record_speed: int, sampling_rate: int = 44100):
        # print(f"SAMPLE FRAME RATE: {((1 / record_speed) * sampling_rate)}")
        result = sd.rec(int((1 / (record_speed * 2)) * sampling_rate), samplerate=sampling_rate, channels=1)
        sd.wait()
        return result

    @staticmethod
    def within_error(current_value: float, target_value: int, error: float):
        return (target_value - error) <= current_value <= (target_value + error)

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
            return ValueError(f"The error margin provided is too large. Maximum allowed is {self.__frequency_step__ / 2} Hz."
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
        pysine.sine(0, 2)  # Warm up the program.

        pysine.sine(self.CALL_FREQUENCY, 1 / self.__speed__)
        self.play_binary(self.__base_frequency__, self.__speed__, binary, self.__frequency_step__)
        pysine.sine(self.CALL_FREQUENCY, 1 / self.__speed__)

    def transmit_text(self, text: str):
        binary_text = self.str_to_bin(text)
        self.transmit(binary_text)


    # -- Receiving --

    def receive_data(self, probing: bool, transmitting_data: bool, binary_list: list) -> tuple[bool, bool, list]:
        target_speed = self.__speed__ + (((self.__speed__ * 4) - self.__speed__) * probing)

        # print(target_speed)

        sampling_rate = 48000
        result = self.retrieve_sound(target_speed, sampling_rate)
        frequency: np.float64 = self.freq(sampling_rate, result, 0, (1 / (target_speed * 2)) * 1000)

        within_call_error = self.within_error(frequency.item(), self.CALL_FREQUENCY, self.__error_margin__)

        print(frequency.item())

        if probing and not within_call_error and not transmitting_data:
            return True, False, binary_list
        elif probing and within_call_error and not transmitting_data:
            return True, True, binary_list
        elif not probing and transmitting_data and within_call_error:
            return False, False, binary_list

        if self.within_error(frequency.item(), self.UP_FREQUENCY, self.__error_margin__):
            binary_list.append(1)
        elif self.within_error(frequency.item(), self.__base_frequency__, self.__error_margin__):
            binary_list.append(0)

        # binary_str += '0' if within_error(frequency.item(), base_frequency, error_margin) else '1'

        # binary_list.append(int(within_error(frequency.item(), base_frequency + up_frequency_offset, error_margin)))

        return False, True, binary_list
        # print(set(sorted(frequencies, key=float)))

    def receive(self) -> list[int]:
        probe = True
        binary: list[int] = []
        transmitted_data = False

        while probe or transmitted_data:
            start = time.time()
            probe, transmitted_data, binary = self.receive_data(probe, transmitted_data, binary)
            end = time.time()

            record_error_margin = end - start

            target_sleep_duration = ((1 / self.__speed__) - record_error_margin) * (not probe)
            sleep_duration = target_sleep_duration if target_sleep_duration >= 0 else 0
            time.sleep(sleep_duration)

        return binary
