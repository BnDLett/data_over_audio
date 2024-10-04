from data_over_audio import DataOverAudio


def main():
    doa = DataOverAudio(3000, 400, 8)
    doa.transmit_text("Hello, world!")


if __name__ == "__main__":
    main()
