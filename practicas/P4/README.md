# Requisitos


https://github.com/mortbopet/Ripes

Descarga el simulador:
https://github.com/mortbopet/Ripes/releases/download/v2.2.6/Ripes-v2.2.6-linux-x86_64.AppImage

Configuración del compilador de C a RISC-V:
https://github.com/mortbopet/Ripes/blob/master/docs/c_programming.md

Descarga el compilador:
https://static.dev.sifive.com/dev-tools/riscv64-unknown-elf-gcc-8.3.0-2020.04.1-x86_64-linux-ubuntu14.tar.gz

Añade al PATH: p.ej. PATH="$PATH:~/local/riscv/bin"

RIPES->Settings->Compiler:
Compiler path: $HOME/local/riscv-gcc-ripes/bin/riscv64-unknown-elf-gcc
Linker arguments: -static -lm -nostdlib

Es recomendable usar el flag -nostdlib para generar ensamblador más legible. El programa de ejemplo matmul es compatible con esta opción.