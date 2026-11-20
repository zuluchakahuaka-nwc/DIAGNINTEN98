"""Тесты сборки RCM-образа и отправки payload (fusee gelée)."""

import struct

import pytest

from diagninten98.usb.intermezzo import INTERMEZZO_BIN
from diagninten98.usb.payload import (
    INTERMEZZO_LOCATION,
    MAX_COMMAND_LENGTH,
    PACKET_SIZE,
    PAYLOAD_LOAD_BLOCK,
    RCM_PAYLOAD_ADDR,
    PayloadError,
    RcmLink,
    build_image,
    send_payload,
)


class FakeHandle:
    """Фейк usb1.USBDeviceHandle: пишет журнал вызовов, имитирует smash."""

    def __init__(self, smash_succeeds: bool = True):
        self.bulk_reads: list = []
        self.bulk_writes: list = []
        self.control_reads: list = []
        self._smash_succeeds = smash_succeeds

    def bulkRead(self, endpoint, length, timeout):
        self.bulk_reads.append((endpoint, length, timeout))
        return b"\x11" * length

    def bulkWrite(self, endpoint, data, timeout):
        self.bulk_writes.append((endpoint, bytes(data), timeout))

    def controlRead(self, request_type, request, value, index, length, timeout):
        self.control_reads.append(
            (request_type, request, value, index, length, timeout)
        )
        if self._smash_succeeds:
            # bootROM сорвался после переполнения стека — ожидаемое поведение
            raise RuntimeError("usb: device detached (stack smashed)")
        return b"\x00" * length


def test_build_image_structure():
    payload = bytes(range(256)) * 8  # 2048 байт
    intermezzo = b"\xCC" * 100
    image = build_image(payload, intermezzo)

    # заголовок: длина команды
    assert image[:4] == MAX_COMMAND_LENGTH.to_bytes(4, "little")
    # образ выровнен по размеру пакета
    assert len(image) % PACKET_SIZE == 0

    # зона указателей смэша: 0xF000 байт от смещения 680, каждое слово = 0x4001F000.
    # (первые 680 байт — заголовок RCM-команды; далее image_off = 680 + addr-0x40010000)
    start = 680
    end = start + (INTERMEZZO_LOCATION - RCM_PAYLOAD_ADDR)
    for offset in range(start, end, 4):
        assert struct.unpack_from("<I", image, offset)[0] == INTERMEZZO_LOCATION

    # intermezzo сразу за зоной указателей (адрес 0x4001F000)
    assert image[end : end + len(intermezzo)] == intermezzo

    # payload по смещению 680 + (PAYLOAD_LOAD_BLOCK - RCM_PAYLOAD_ADDR)
    payload_off = start + (PAYLOAD_LOAD_BLOCK - RCM_PAYLOAD_ADDR)
    assert image[payload_off : payload_off + len(payload)] == payload


def test_build_image_oversized_intermezzo():
    with pytest.raises(PayloadError):
        build_image(b"x", b"\x00" * 0x1001)


def test_intermezzo_module_generated():
    assert len(INTERMEZZO_BIN) == 100
    # первая инструкция — movw r0, #0xF028 (адрес хвоста внутри intermezzo)
    assert INTERMEZZO_BIN[:4] == (0xE30F0028).to_bytes(4, "little")


def test_rcm_link_write_chunks():
    handle = FakeHandle()
    link = RcmLink(handle)
    link.write(b"\xAB" * (PACKET_SIZE * 2))
    assert len(handle.bulk_writes) == 2
    assert all(ep == 0x01 for ep, _data, _t in handle.bulk_writes)
    assert len(handle.bulk_writes[0][1]) == PACKET_SIZE


def test_send_payload_success():
    handle = FakeHandle(smash_succeeds=True)
    link = RcmLink(handle)

    launched = send_payload(link, b"PAYLOAD", b"\xCC" * 100)

    assert launched is True
    # первым делом прочитан Device ID (EP 0x81, 16 байт)
    assert handle.bulk_reads[0][:2] == (0x81, 16)
    # триггер: GET_STATUS (0x82) на верхнем буфере, длина 0x7000
    request = handle.control_reads[0]
    assert request[0] == 0x82
    assert request[1] == 0x00
    assert request[4] == 0x7000


def test_send_payload_not_launched():
    """Control-чтение вернулось — консоль эксплойт не приняла."""
    handle = FakeHandle(smash_succeeds=False)
    link = RcmLink(handle)
    assert send_payload(link, b"PAYLOAD", b"\xCC" * 100) is False
