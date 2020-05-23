#!/usr/bin/env python
"""
    Byte
    Tap Data
    00  Lenght of Block 0
    01  Lenght of Block 1
    02  Flag byte (0 for a header, 255 for the body of the file)
    03  Type 0: program 1: num_array 2: char_array 3: bytes

    Speccy Data
    04  Name Char 0
    05  Name Char 1
    06  Name Char 2
    07  Name Char 3
    08  Name Char 4
    09  Name Char 5
    10  Name Char 6
    11  Name Char 7
    12  Name Char 8
    13  Name Char 9
    14  Next block Size 0
    15  Next block Size 1
    16  Start 0
    17  Start 1
    18  Flag (Basic varible letter - 1???)
    19  ??? 128
    20  Check sum

    https://faqwiki.zxnet.co.uk/wiki/TAP_format
    """

"""
    Extra bytes on first string
    00 size 0-255
    01 border color
    02 screen paper color
    03 screen ink color
    04 highlight paper color
    05 highlight ink color

    """
from os.path import isfile, join
from os import listdir
from argparse import ArgumentParser
from array import array
import math
__version__ = "0.0.1"


def get_parity(data):
    parity = 0
    # data[len(data)-1] = 0x00
    for b in data:
        # print("Byte " + hex(b) + " Paridad " + hex(parity))
        parity ^= b
    # print("Paridad " + hex(parity))
    return parity


def create_header_block(title='', length=0, start=0,  flag=0, data_type=3):
    header = [0, data_type]
    header.extend([ord(c) for c in title[:10].ljust(10)])
    header.extend((length % 256, length // 256))

    # header.extend((start % 256, start // 256))
    header.extend([0])
    header.extend([flag])
    header.extend([0])
    header.extend([128])
    header.append(get_parity(header))
    return header


def create_data_block(data):
    body = [255]
    body.extend(data)
    parity = [get_parity(body)]
    body.extend(parity)
    return body


def create_tap_data_block(data):
    data_block = create_data_block(data)
    length = len(data_block)
    return [length % 256, length // 256] + data_block


def create_tap_header_block(title='', start=0, length=0, flag=0, data_type=3):
    return [19, 0] + create_header_block(title, start, length, flag, data_type)


def main():

    import os

    files = os.listdir()
    # print(tap_names)

    parser = ArgumentParser(description="tappack",
                            epilog="Copyleft (C) 2020 Cristian Gonzalez",
                            )

    parser.add_argument("--version", action="version",
                        version="%(prog)s " + __version__)
    # parser.add_argument("--convert", action="store_true", default=False)
    parser.add_argument("title", help="new name", nargs="?")
    parser.add_argument("name", help="new name", nargs="?")
    parser.add_argument("tap", help="tap to rename", nargs="?")

    args = parser.parse_args()

    if not args.tap:
        parser.error("required parameter: tap")

    if not args.name:
        parser.error("required parameter: name")

    if not args.title:
        parser.error("required parameter: title")

    if len(args.name) > 10:
        parser.error("name max len is 10 chars")
    f = open(args.tap, 'wb')

    #    create_tap_header_block(data_type=0),
    #    create_tap_data_block(basic_data),
    #    create_tap_header_block(start=code_start),
    #    create_tap_data_block(code)
    # code_data = bytearray()
    data_list = []
    tapnames = bytearray()
    files.sort()  # reverse=True
    string_width = 32
    string_max = 9  # min, extra data needs 9 bytes
    elements = 0

    loader = open('loader', "rb")
    bytes_loader = loader.read()

    # get max width n elements
    for file in files:
        if (file.endswith(".tap") or file.endswith(".TAP")) and file != args.tap:
            tapfile = open(file, "rb")
            tapnames.extend(tapfile.read(14)[4:14])
            tapfile.close()
            elements += 1
            file = file.replace(".tap", "")
            file = file.replace(".TAP", "")
            if len(file) > string_max:
                string_max = len(file)

    for file in files:
        if (file.endswith(".tap") or file.endswith(".TAP")) and file != args.tap:
            file = file.replace(".tap", "")
            file = file.replace(".TAP", "")
            file = file.ljust(string_width)
            data_list.extend(file[0:string_width])

    if elements == 0:
        print("No files to pack, add the files to pack on current directory.")
        quit()

    # Zx Spectrum Basic Array (data) sizes
    basic_data = bytearray(5)
    # 5 Bytes
    basic_data[0] = 0x02
    basic_data[1] = elements + 2
    basic_data[2] = 0x00
    basic_data[3] = string_width
    basic_data[4] = 0x00
    # Packer extra data is encoded on first row for menu
    extra_data = bytearray(string_width)
    # elements
    extra_data[0] = elements + 2
    # string width
    extra_data[1] = string_max  # for centering
    # border color
    extra_data[2] = 0
    # screen attribs
    extra_data[3] = 0
    extra_data[4] = 7
    # highlighted attribs
    extra_data[5] = 2
    extra_data[6] = 7
    # title attribs
    extra_data[7] = 1
    extra_data[8] = 4

    # Menu title encoded at array title
    tap_data0 = basic_data.decode(encoding="utf-8", errors="strict")
    titulo = args.title.center(string_width)

    tap_data = basic_data + extra_data + \
        bytearray(titulo, "utf-8") + \
        bytearray([ord(char) for char in data_list])

    body = create_tap_data_block(tap_data)
    header = create_tap_header_block(
        'titles',    # title
        len(body)-4,  # length
        0x0,
        0xc1,         # basic variable name fixed as a$
        0x2           # block data type
    )

    bytes_titles = bytearray()
    bytes_titles += bytearray(header)
    bytes_titles += bytearray(body)

    # ZX Basic Program Names

    basic_data[0] = 0x02
    basic_data[1] = elements + 2
    basic_data[2] = 0x00
    basic_data[3] = 10  # ZX Basic filenamea 10, trailing spaces doesn't matter
    basic_data[4] = 0x00
    tap_data = basic_data + tapnames

    body = create_tap_data_block(tap_data)
    header = create_tap_header_block(
        'filenames',    # title
        len(body)-4,    # length
        0x0,
        0xc2,           # basic variable name fixed as b$
        0x2             # block data type
    )

    bytes_programs = bytearray()
    bytes_programs += bytearray(header)
    bytes_programs += bytearray(body)

    # Summary
    bytes_taps = bytearray()
    print('Program: ', args.name, ' - Main Loader')
    for file in files:
        if (file.endswith(".tap") or file.endswith(".TAP")) and file != args.tap:
            tapfile = open(file, "rb")
            bytes_taps += tapfile.read()
            tapfile.close()
            tapfile = open(file, "rb")
            print(' Program: ', tapfile.read(14)[
                  4:14].decode("utf-8").strip(), '-', file)

            tapfile.close()

    # Rename Tap Basic main Program
    bytes_tapname = bytearray()
    bytes_tapname.extend(map(ord, args.name[:10].ljust(10)))

    bytes_loader = bytearray(bytes_loader)
    for x in range(0, 10):
        bytes_loader[x+4] = bytes_tapname[x]

    # Calculate New Parity
    parity = 0

    for x in range(4, 20):
        parity ^= bytes_loader[x]

    bytes_loader[20] = parity
    # Write Data
    f.write(bytes_loader + bytes_titles + bytes_programs + bytes_taps)


if __name__ == "__main__":
    main()
