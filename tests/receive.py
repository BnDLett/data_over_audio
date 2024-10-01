from data_over_audio import DataOverAudio


def main():
    doa = DataOverAudio(3000, 200, 100, 16)
    binary: list[int] = doa.receive()
    print(binary)


if __name__ == "__main__":
    main()
