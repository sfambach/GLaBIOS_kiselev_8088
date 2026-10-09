# GLaBIOS for the micro_8088

Build files for [Sergey Kiselev's micro_8088](https://github.com/skiselev/micro_8088) (Faraday FE2010A).

A standard or Turbo GLaBIOS build does not run on this board. GLaBIOS already has a preset for it:
`ARCH_TYPE=ARCH_FE2010` with `ARCH_SUB_TYPE=ARCH_M88`. It configures the FE2010A through port 63h,
skips the timer 1 test, disables DRAM refresh (the board uses SRAM) and boots at 9.54 MHz.

The ROMs here are built with `POST_ERR_WAIT=0`: a POST error such as `1000 FDC` (no floppy
controller installed) is shown, but the BIOS keeps booting instead of waiting for a key.

## Files

| File | Purpose |
|---|---|
| `roms/GLABIOS_M88_CPU_8088.ROM` | 8 KiB GLaBIOS for Intel 8088 / 80C88 |
| `roms/GLABIOS_M88_CPU_V20.ROM` | 8 KiB GLaBIOS for NEC V20 |
| `build.sh` | Rebuilds both ROMs with [JWasm](https://github.com/Baron-von-Riedesel/JWasm) |
| `mkflash.py` | Builds a 128 KiB image for the SST39SF010A flash |

## Flash layout

The board maps 64 KiB of the 128 KiB flash to `F000:0000`; jumper JP1 selects which half.

| Flash offset | Address | Content |
|---|---|---|
| `0x00000-0x0FFFF` | JP1 open | existing image (e.g. Sergey's BIOS with XTIDE) as fallback |
| `0x10000` | JP1 closed, `F000:0000` | XTIDE Universal BIOS (optional) |
| next 2 KiB block | JP1 closed | [GLaTICK](https://github.com/640-KB/GLaTICK) real time clock ROM (optional) |
| `0x1E000-0x1FFFF` | JP1 closed, `FE00:0000` | GLaBIOS |

GLaBIOS scans for option ROMs up to `FE00:0000`, so it finds XTIDE and GLaTICK in the same flash.
GLaBIOS has no RTC support of its own; GLaTICK adds it (`GLaTICK_*_AT.ROM` for DS12x85/MC146818 at 70h, 240h or 2C0h).

```sh
JWASM_BIN=/path/to/jwasm ./build.sh
python3 mkflash.py roms/GLABIOS_M88_CPU_8088.ROM flash.bin --base old_flash.bin --xtide xtide.bin --glatick GLaTICK_0.8.8_AT.ROM
```

Program `flash.bin`, close JP1 to boot GLaBIOS, open JP1 to return to the old BIOS.
