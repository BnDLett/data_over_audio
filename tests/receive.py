from data_over_audio import DataOverAudio


def main():
    doa = DataOverAudio(3000, 200, 100, 8)
    binary: list[int] = doa.receive()
    print(''.join(str(x) for x in binary))
    print(doa.str_to_bin("Hello, world!"))
    unicode_numbers: list[int] = []
    unicode_string: str = ''

    length_necessary = len(binary) % 8
    for i in range (length_necessary):
        binary.insert(0, 0)

    for i in range(int(len(binary) / 8)):
        binary_str = ''.join(str(bit) for bit in binary[i:i+8])
        unicode_numbers.append(int(binary_str, 2))

    unicode_string = ''.join(chr(num) for num in unicode_numbers)
    print(unicode_numbers)
    print(unicode_string)


if __name__ == "__main__":
    main()
