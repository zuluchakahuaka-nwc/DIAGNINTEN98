"""Чтение Device ID из RCM — только чтение, эксплойт НЕ используется.

Протокол по fusee-launcher (Smeat/fusee-launcher, сверено 2026-11-20):
Device ID — первые 16 байт bulk-IN c endpoint 0x81, таймаут 1 c; VID/PID 0955:7321.
Чтение Device ID переводит boot ROM в состояние приёма команд, но ничего
не записывает и не триггерит уязвимость.

Требует WinUSB-драйвер для APX (Zadig) — см. README и подсказку на вкладке RCM.
"""

from __future__ import annotations

import usb1

from .ids import RCM_VID_PID

RCM_READ_ENDPOINT = 0x81
DEVICE_ID_LEN = 16
TIMEOUT_MS = 1000


class RcmError(RuntimeError):
    """Ошибка связи с консолью в RCM."""


def open_handle():
    """Найти консоль в RCM. Возвращает (USBContext, USBDeviceHandle).

    Контекст закрывает вызывающий (ctx.close()) — с ним умирает handle.
    """
    ctx = usb1.USBContext()
    handle = ctx.openByVendorIDAndProductID(*RCM_VID_PID, skip_on_error=True)
    if handle is None:
        ctx.close()
        raise RcmError("RCM device not found (0955:7321)")
    return ctx, handle


def read_device_id() -> bytes:
    """Найти консоль в RCM и прочитать 16-байтный Device ID.

    Бросает RcmError, если устройство не найдено или не отвечает.
    """
    ctx, handle = open_handle()
    try:
        try:
            handle.claimInterface(0)
        except usb1.USBError:
            pass  # Windows часто не требует явного claim
        try:
            data = handle.bulkRead(RCM_READ_ENDPOINT, DEVICE_ID_LEN, TIMEOUT_MS)
        except usb1.USBError as exc:
            raise RcmError(f"bulk read failed: {exc}") from exc
        return bytes(data)
    finally:
        ctx.close()


def format_device_id(data: bytes) -> str:
    """16 байт → hex-строка: '00112233...ff'."""
    return data.hex()
