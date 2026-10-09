#!/bin/sh
# Build GLaBIOS for Sergey Kiselev's micro_8088 (FE2010A, sub-type M) with JWasm.
# Usage: JWASM_BIN=/path/to/jwasm ./build.sh
set -e
cd "$(dirname "$0")"
# JWasm reads options from the JWASM environment variable, so the binary path uses another name.
JWASM_BIN="${JWASM_BIN:-jwasm}"
for CPU in CPU_8088 CPU_V20; do
	"$JWASM_BIN" -Zm -bin -DCPU_TYPE=$CPU -DARCH_TYPE=ARCH_FE2010 -DARCH_SUB_TYPE=ARCH_M88 \
		-Fo"roms/$CPU.BIN" ../src/GLABIOS.ASM
	python3 ../src/gla2rom/gla2rom.py "roms/$CPU.BIN" "roms/GLABIOS_M88_$CPU.ROM"
	rm -f "roms/$CPU.BIN"
done
