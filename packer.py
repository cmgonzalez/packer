#!/usr/bin/env python
"""
    Packer - a tool to create ZX Spectrum tap's Packs with a basic menu
    Parameters

    path: Path of the sources Taps files
    tap: Output tap file name

    title: Title of the Basic Menu
    program: Basic Menu program name
    


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
__version__ = "0.3"


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
    black = 0
    blue = 1
    red = 2
    magenta = 3
    green = 4
    cyan = 5
    yellow = 6
    white = 7

    parser = ArgumentParser(description="tappack",
                            epilog="Copyleft (C) 2020 Cristian Gonzalez",
                            )

    parser.add_argument("--version", action="version",
                        version="%(prog)s " + __version__)
    # parser.add_argument("--convert", action="store_true", default=False)
    parser.add_argument("path", help="Source Tap file path", nargs="?")
    parser.add_argument("tap", help="Output Tap file name", nargs="?")
    parser.add_argument("title", help="Pack Title", nargs="?")
    parser.add_argument("program", help="Basic Program Name", nargs="?")

    parser.add_argument("paper", help="Menu Paper", nargs="?")
    parser.add_argument("ink", help="Menu Ink", nargs="?")
    parser.add_argument("border", help="Menu Border", nargs="?")

    parser.add_argument("sel_paper", help="Selected item Paper", nargs="?")
    parser.add_argument("sel_ink", help="Selected item Ink", nargs="?")

    parser.add_argument("title_paper", help="Menu Title Paper", nargs="?")
    parser.add_argument("title_ink", help="Menu Title ink", nargs="?")

    # default values
    border = black
    paper = black
    ink = white

    sel_paper = red
    sel_ink = white

    title_paper = blue
    title_ink = green

    args = parser.parse_args()

    if not args.path:
        parser.error("required parameter: path")

    if not args.tap:
        parser.error("required parameter: tap")

    if not args.program:
        parser.error("required parameter: program")

    if not args.title:
        parser.error("required parameter: title")

    # Screen Colors
    if args.border:
        border = int(args.border)
    if args.paper:
        paper = int(args.paper)
    if args.ink:
        ink = int(args.ink)
    # Selected Colors
    if args.sel_paper:
        sel_paper = int(args.sel_paper)
    if args.sel_ink:
        sel_ink = int(args.sel_ink)
    # Title Colors
    if args.title_paper:
        title_paper = int(args.title_paper)
    if args.title_ink:
        title_ink = int(args.title_ink)

    if len(args.program) > 10:
        parser.error("name max len is 10 chars")

    f = open(args.tap, 'wb')

    # read path files
    files = os.listdir(args.path)
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
            tapfile = open(args.path+file, "rb")
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
    extra_data[0] = elements  # + 2
    # string width
    extra_data[1] = string_max  # for centering
    # border color
    extra_data[2] = border
    # screen attribs
    extra_data[3] = paper
    extra_data[4] = ink
    # selected item attribs
    extra_data[5] = sel_paper
    extra_data[6] = sel_ink
    # title attribs
    extra_data[7] = title_paper
    extra_data[8] = title_ink

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
    print('Program: ', args.program, ' - Main Loader')
    for file in files:
        if (file.endswith(".tap") or file.endswith(".TAP")) and file != args.tap:
            tapfile = open(args.path+file, "rb")
            bytes_taps += tapfile.read()
            tapfile.close()
            tapfile = open(args.path+file, "rb")
            print(' Program: ', tapfile.read(14)[
                  4:14].decode("utf-8").strip(), '-', file)

            tapfile.close()
    print('Total Tap files:', elements)
    # Rename Tap Basic main Program
    bytes_tapname = bytearray()
    bytes_tapname.extend(map(ord, args.program[:10].ljust(10)))

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
