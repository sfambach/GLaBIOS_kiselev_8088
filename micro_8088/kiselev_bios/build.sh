#!/bin/sh
# Build Sergey Kiselev's micro_8088 BIOS with enhanced-keyboard.patch and setup-menu.patch
# (needs git and nasm).
# Usage: ./build.sh [xtide.rom]
# Writes ../roms/KISELEV_M88_XTIDE.ROM: the 64 KiB lower flash half (JP1 open),
# usable as --base for ../mkflash.py. Default XTIDE ROM: upstream r625, XT-CF-Lite at 320h.
set -e
cd "$(dirname "$0")"
OUT="$(pwd)/../roms/KISELEV_M88_XTIDE.ROM"
XTIDE="${1:+$(realpath "$1")}"
rm -rf 8088_bios
git clone -q https://github.com/skiselev/8088_bios.git
cd 8088_bios
git checkout -q ce2ac99f7622853ade69ae26fdf27fe3c27a9a5d
git apply ../enhanced-keyboard.patch
git apply --whitespace=nowarn ../setup-menu.patch
[ -n "$XTIDE" ] && cp "$XTIDE" xtide_r625/ide_xt-cf-lite_320h.bin
make -C src bios-micro8088-xtide.rom >/dev/null 2>&1
head -c 65536 src/bios-micro8088-xtide.rom > "$OUT"
cd .. && rm -rf 8088_bios
echo "Wrote $OUT"
