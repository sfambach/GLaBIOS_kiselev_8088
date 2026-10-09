#!/usr/bin/env python3
"""Build a 128 KiB SST39SF010A image for the micro_8088.

Lower 64 KiB (JP1 open):   kept from the existing flash image (fallback BIOS).
Upper 64 KiB (JP1 closed): XTIDE option ROM at F000:0000, GLaBIOS at FE00:0000.
"""
import argparse

KIB = 1024


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("glabios", help="8 KiB GLaBIOS ROM")
    parser.add_argument("output", help="128 KiB flash image to write")
    parser.add_argument("--base", help="existing 64 or 128 KiB flash image; its lower 64 KiB is kept")
    parser.add_argument("--xtide", help="XTIDE Universal BIOS option ROM (max 56 KiB)")
    args = parser.parse_args()

    glabios = open(args.glabios, "rb").read()
    if len(glabios) != 8 * KIB or sum(glabios) & 0xFF:
        raise SystemExit("GLaBIOS ROM must be 8 KiB with a valid checksum")

    image = bytearray(b"\xff" * 128 * KIB)
    if args.base:
        base = open(args.base, "rb").read()
        image[: 64 * KIB] = base[: 64 * KIB].ljust(64 * KIB, b"\xff")
    if args.xtide:
        xtide = open(args.xtide, "rb").read()
        if xtide[:2] != b"\x55\xaa" or len(xtide) > 56 * KIB:
            raise SystemExit("XTIDE ROM must start with 55AA and fit below FE00:0000")
        image[64 * KIB : 64 * KIB + len(xtide)] = xtide
    image[120 * KIB :] = glabios

    open(args.output, "wb").write(image)
    print(f"Wrote {args.output}: JP1 open = base image, JP1 closed = GLaBIOS")


if __name__ == "__main__":
    main()
