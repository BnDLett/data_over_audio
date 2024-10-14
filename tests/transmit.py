from data_over_audio import DataOverAudio
# Lorem


def main():
    doa = DataOverAudio(3000, 100, 50, 16)
    doa.transmit_text("Hello, world!")


if __name__ == "__main__":
    main()
