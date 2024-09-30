import numpy as np
import parselmouth

import sounddevice as sd
import matplotlib.pyplot as plt
import wavio

from scipy.fft import *
from scipy.io import wavfile

sampling_rate = 44100
duration = 10
result = sd.rec(int(duration * sampling_rate), samplerate=sampling_rate, channels=1)
sd.wait()
wavio.write("result.wav", result, sampling_rate, sampwidth=2)

snd = parselmouth.Sound('result.wav')


def draw_spectrogram(spectrogram, dynamic_range=70):
    X, Y = spectrogram.x_grid(), spectrogram.y_grid()
    sg_db = 10 * np.log10(spectrogram.values)
    plt.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='afmhot')
    plt.ylim([spectrogram.ymin, spectrogram.ymax])
    plt.xlabel("time [s]")
    plt.ylabel("frequency [Hz]")


def draw_amplitude():
    plt.figure()
    plt.plot(snd.xs(), snd.values.T)
    plt.xlim([snd.xmin, snd.xmax])
    plt.xlabel("time [s]")
    plt.ylabel("amplitude")
    plt.show()  # or plt.savefig("sound.png"), or plt.savefig("sound.pdf")


def draw_intensity(intensity):
    plt.plot(intensity.xs(), intensity.values.T, linewidth=3, color='w')
    plt.plot(intensity.xs(), intensity.values.T, linewidth=1)
    plt.grid(False)
    plt.ylim(0)
    plt.ylabel("intensity [dB]")


def main():
    plt.figure()

    draw_spectrogram(snd.to_spectrogram(1/16), 70)
    # plt.twinx()
    # draw_amplitude()

    plt.xlim([snd.xmin, snd.xmax])
    plt.show()

    rate = 32 / 2

    # spectrogram: parselmouth.Spectrogram = snd.to_spectrogram(1/(rate * 2))
    #
    # frequencies: list = []
    #
    # for x in spectrogram.x_grid().tolist():
    #     # print(x)
    #     # print((x - 1/16 if x - 1/16 > 0 else 0) * 1000)
    #     frequency: np.float64 = freq('result.wav', (x - 1/rate if x - 1/rate > 0 else 0) * 1000, (x + 1/rate) * 1000)
    #     frequencies.append(frequency.item())
    #
    # print(frequencies)

    # print(set(sorted(frequencies, key=float)))


if __name__ == "__main__":
    main()
