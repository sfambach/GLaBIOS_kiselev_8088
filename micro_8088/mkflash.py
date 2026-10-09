#!/usr/bin/env python3
"""Build a 128 KiB SST39SF010A image for the micro_8088.

Lower 64 KiB (JP1 open):   kept from the existing flash image (fallback BIOS).
Upper 64 KiB (JP1 closed): XTIDE option ROM at F000:0000, optional GLaTICK (RTC) option ROM
                           right behind it, GLaBIOS at FE00:0000.
"""
import argparse

KIB = 1024


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("glabios", help="8 KiB GLaBIOS ROM")
    parser.add_argument("output", help="128 KiB flash image to write")
    parser.add_argument("--base", help="existing 64 or 128 KiB flash image; its lower 64 KiB is kept")
    parser.add_argument("--xtide", help="XTIDE Universal BIOS option ROM")
    parser.add_argument("--glatick", help="GLaTICK real time clock option ROM")
    args = parser.parse_args()

    glabios = open(args.glabios, "rb").read()
    if len(glabios) != 8 * KIB or sum(glabios) & 0xFF:
        raise SystemExit("GLaBIOS ROM must be 8 KiB with a valid checksum")

    image = bytearray(b"\xff" * 128 * KIB)
    if args.base:
        base = open(args.base, "rb").read()
        image[: 64 * KIB] = base[: 64 * KIB].ljust(64 * KIB, b"\xff")
    offset = 64 * KIB
    for name in (args.xtide, args.glatick):
        if not name:
            continue
        rom = open(name, "rb").read()
        if rom[:2] != b"\x55\xaa":
            raise SystemExit(f"{name} is not an option ROM (no 55AA signature)")
        if offset + len(rom) > 120 * KIB:
            raise SystemExit("option ROMs must fit below FE00:0000")
        image[offset : offset + len(rom)] = rom
        # option ROM scan steps in 2 KiB blocks
        offset += -(-len(rom) // (2 * KIB)) * 2 * KIB
    image[120 * KIB :] = glabios

    open(args.output, "wb").write(image)
    print(f"Wrote {args.output}: JP1 open = base image, JP1 closed = GLaBIOS")


if __name__ == "__main__":
    main()
