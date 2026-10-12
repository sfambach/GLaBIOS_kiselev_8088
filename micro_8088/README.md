# GLaBIOS for the micro_8088

Build files for [Sergey Kiselev's micro_8088](https://github.com/skiselev/micro_8088) (Faraday FE2010A).

A standard or Turbo GLaBIOS build does not run on this board. GLaBIOS already has a preset for it:
`ARCH_TYPE=ARCH_FE2010` with `ARCH_SUB_TYPE=ARCH_M88`. It configures the FE2010A through port 63h,
skips the timer 1 test, disables DRAM refresh (the board uses SRAM) and boots at 9.54 MHz.

The ROMs here are built with `POST_ERR_WAIT=0`: a POST error such as `1000 FDC` (no floppy
controller installed) is shown, but the BIOS keeps booting instead of waiting for a key.

The `ARCH_M88` preset in `src/GLABIOS.ASM` also has these changes for this board:

- `KB_EXT_FLAG=1`: POST sets bit 4 of `40:96h` (101/102-key keyboard installed). The on-board
  AT to XT converter passes the extended keys (E0 prefix, DIP SW2.3 = ON), but an XT keyboard
  interface cannot report the keyboard type. Without the flag, `KEYB GR` ignores the `<>` key (56h).
- `RAM_TEST_LONG=0`, `POST_TEST_FD=0`, `POST_TEST_SEEK=0`: faster boot. The board has SRAM, and
  often no floppy controller.

## Sergey's BIOS with the same keyboard fix

`kiselev_bios/` builds the lower flash half (JP1 open) from
[8088_bios](https://github.com/skiselev/8088_bios) with `enhanced-keyboard.patch`. The patch
sets the same `40:96h` bit at POST. `build.sh` takes the XTIDE ROM to bundle (for example the
first 8 KiB of an existing image) and writes `roms/KISELEV_M88_XTIDE.ROM` for `mkflash.py --base`.

## Files

| File | Purpose |
|---|---|
| `roms/GLABIOS_M88_CPU_8088.ROM` | 8 KiB GLaBIOS for Intel 8088 / 80C88 |
| `roms/GLABIOS_M88_CPU_V20.ROM` | 8 KiB GLaBIOS for NEC V20 |
| `build.sh` | Rebuilds both ROMs with [JWasm](https://github.com/Baron-von-Riedesel/JWasm) |
| `mkflash.py` | Builds a 128 KiB image for the SST39SF010A flash |
| `kiselev_bios/` | Patch and build script for Sergey's BIOS (lower flash half) |
| `roms/KISELEV_M88_XTIDE.ROM` | Lower flash half: Sergey's BIOS 1.0.2 with keyboard fix and XTIDE r624 |

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
