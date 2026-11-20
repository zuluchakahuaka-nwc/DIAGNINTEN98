"""Детерминированный демо-набор USB-устройств.

Используется e2e-тестами и tools/golden.py, чтобы скриншоты были
воспроизводимы на любой машине (реальный список USB у всех разный).
Демонстрирует ценность инструмента: консоль в RCM обнаружена.
"""

from __future__ import annotations

from .usb.ids import UsbDeviceInfo

DEMO_DEVICES: list[UsbDeviceInfo] = [
    UsbDeviceInfo(
        0x0955, 0x7321, "USB\\VID_0955&PID_7321\\00004D5A", "APX", service="WinUSB"
    ),
    UsbDeviceInfo(0x05E3, 0x0610, "USB\\VID_05E3&PID_0610\\5&3b784bf&0&9", "USB2.0 Hub"),
    UsbDeviceInfo(
        0x046D, 0xC077, "USB\\VID_046D&PID_C077\\6&2a53e7da&1&3", "USB Receiver"
    ),
]


def demo_enumerate() -> list[UsbDeviceInfo]:
    """Функция-перечислитель для детерминированных скриншотов (RCM присутствует)."""
    return list(DEMO_DEVICES)
