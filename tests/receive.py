from data_over_audio import DataOverAudio

# Lorem


def main():
    doa = DataOverAudio(3000, 100, 50, 16)
    binary: list[int] = doa.receive()
    unicode_numbers: list[int] = []

    length_necessary = len(binary) % 8
    for i in range(length_necessary):
        binary.append(0)

    for i in range(int(len(binary) / 8)):
        index = i * 8
        binary_str = ''.join(str(bit) for bit in binary[index:index+8])
        # print(binary_str)
        unicode_numbers.append(int(binary_str, base=2))

    unicode_string = ''.join(chr(num) for num in unicode_numbers)
    print(unicode_numbers)
    print(unicode_string)


if __name__ == "__main__":
    main()
