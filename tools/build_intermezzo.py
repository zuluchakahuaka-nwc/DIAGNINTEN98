"""Сборка intermezzo — стадий-1 заглушки fusée gelée (ARM32/A32).

Своя реализация алгоритма (константы — публично документированная техника):
  1) скопировать свой хвост на 0x40000000 (безопасная зона BPMP IRAM);
  2) прыгнуть туда;
  3) хвост копирует 0x20000 байт payload'а с 0x40020000 на 0x40010000;
  4) прыгнуть на payload.

Инструкции кодируются вручную (E3x/MOVW-MOVT и пр.) и проверяются
дизассемблером capstone (dev-зависимость). Результат — модуль
src/diagninten98/usb/intermezzo.py с байтами.

Запуск: uv run python tools/build_intermezzo.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "src" / "diagninten98" / "usb" / "intermezzo.py"

INTERMEZZO_ADDR = 0x4001F000  # адрес загрузки заглушки
SAFE_ADDR = 0x40000000  # куда релоцируется хвост
PAYLOAD_SRC = 0x40020000  # где лежит payload после приёма
PAYLOAD_DST = 0x40010000  # куда payload должен скопироваться
PAYLOAD_LEN = 0x20000  # безопасная длина копирования (IRAM)


def movw(rd: int, imm: int) -> int:
    return 0xE3000000 | ((imm >> 12) << 16) | (rd << 12) | (imm & 0xFFF)


def movt(rd: int, imm: int) -> int:
    return 0xE3400000 | ((imm >> 12) << 16) | (rd << 12) | (imm & 0xFFF)


def load32(rd: int, value: int) -> list[int]:
    return [movw(rd, value & 0xFFFF), movt(rd, value >> 16)]


def bx(rd: int) -> int:
    return 0xE12FFF10 | rd


def bl(offset_words: int) -> int:
    return 0xEB000000 | (offset_words & 0xFFFFFF)


def bne(offset_words: int) -> int:
    return 0x1A000000 | (offset_words & 0xFFFFFF)


def build() -> bytes:
    """Собрать образ intermezzo (фиксированный layout, см. docstring)."""
    tail_off = 0x28
    tail_addr = INTERMEZZO_ADDR + tail_off
    tail_len = 0x64 - tail_off

    words: list[int] = [
        # stage 0: релоцируем хвост на 0x40000000 и прыгаем туда
        *load32(0, tail_addr),          # 00,04: r0 = &tail
        *load32(1, SAFE_ADDR),          # 08,0c: r1 = 0x40000000
        *load32(2, tail_len),           # 10,14: r2 = len(tail)
        bl((0x50 - 0x18 - 8) // 4),     # 18:   bl copy
        *load32(0, SAFE_ADDR),          # 1c,20: r0 = 0x40000000
        bx(0),                          # 24:   bx r0
        # tail: копируем payload и прыгаем на него
        *load32(0, PAYLOAD_SRC),        # 28,2c
        *load32(1, PAYLOAD_DST),        # 30,34
        *load32(2, PAYLOAD_LEN),        # 38,3c
        bl((0x50 - 0x40 - 8) // 4),     # 40:   bl copy
        *load32(0, PAYLOAD_DST),        # 44,48
        bx(0),                          # 4c:   bx r0
        # copy: r0=src, r1=dst, r2=len (пост-инкремент, слова)
        0xE4903004,                     # 50: ldr r3, [r0], #4  (P=0,U=1,W=0,L=1)
        0xE4813004,                     # 54: str r3, [r1], #4  (L=0, Rn=r1)
        0xE2522004,                     # 58: subs r2, r2, #4
        bne((0x50 - 0x5C - 8) // 4),    # 5c: bne copy
        bx(14),                         # 60: bx lr
    ]
    return b"".join(w.to_bytes(4, "little") for w in words)


_EXPECTED_TARGET = f"#0x{INTERMEZZO_ADDR + 0x50:x}"

EXPECTED_DISASM = [
    "movw r0, #0xf028",
    "movt r0, #0x4001",
    "movw r1, #0",
    "movt r1, #0x4000",
    "movw r2, #0x3c",
    "movt r2, #0",
    f"bl {_EXPECTED_TARGET}",
    "movw r0, #0",
    "movt r0, #0x4000",
    "bx r0",
    "movw r0, #0",
    "movt r0, #0x4002",
    "movw r1, #0",
    "movt r1, #0x4001",
    "movw r2, #0",
    "movt r2, #2",
    f"bl {_EXPECTED_TARGET}",
    "movw r0, #0",
    "movt r0, #0x4001",
    "bx r0",
    "ldr r3, [r0], #4",
    "str r3, [r1], #4",
    "subs r2, r2, #4",
    f"bne {_EXPECTED_TARGET}",
    "bx lr",
]


def verify(blob: bytes) -> list[str]:
    try:
        import capstone
    except ImportError:
        print("WARNING: capstone не установлен — верификация пропущена")
        return []
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM | capstone.CS_MODE_LITTLE_ENDIAN)
    lines = [
        f"{ins.mnemonic} {ins.op_str}".strip()
        for ins in md.disasm(blob, INTERMEZZO_ADDR)
    ]
    return lines


def main() -> int:
    blob = build()
    print(f"intermezzo: {len(blob)} bytes ({len(blob)//4} инструкций)")

    lines = verify(blob)
    if lines:
        for line in lines:
            print(f"  {line}")
        if lines != EXPECTED_DISASM:
            raise SystemExit("FAIL: дизассемблер не совпал с ожиданием")

    OUT.write_text(
        '"""Интермеццо — стадия-1 fusée gelée (сгенерировано tools/build_intermezzo.py).\n\n'
        "Не редактировать руками: перегенерация — uv run python tools/build_intermezzo.py.\n"
        '"""\n\n'
        f"INTERMEZZO_BIN = bytes.fromhex(\n    \"{blob.hex()}\"\n)\n",
        encoding="utf-8",
    )
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
