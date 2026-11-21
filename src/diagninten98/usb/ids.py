"""Идентификация USB-устройств Nintendo Switch.

Факты сверены с fusee-launcher (форк Smeat/fusee-launcher, 2026-11-20):
RCM (boot ROM Tegra X1) — VID 0x0955 (NVIDIA), PID 0x7321.
MTP (загруженная система) — VID 0x057E (Nintendo), PID 0x2010 (см. FACTS_TO_VERIFY).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class DeviceKind(Enum):
    RCM = auto()  # APX: boot ROM, jig + Vol+ + Power
    MTP = auto()  # полностью загруженная система (официальный MTP)
    MTP_DBI = auto()  # загруженная система + DBI/хомбрю в MTP-режиме
    OTHER = auto()


@dataclass(frozen=True)
class UsbDeviceInfo:
    vendor_id: int
    product_id: int
    instance_id: str = ""
    name: str = ""
    service: str = ""  # драйвер (например, WinUSB) — пусто, если не установлен


RCM_VID_PID = (0x0955, 0x7321)
MTP_VID_PID = (0x057E, 0x2010)
# DBI (DB Installer, хомбрю) в MTP-режиме — подтверждено живой консолью
# 2026-11-21: name "Switch", service WUDFWpdMtp.
DBI_MTP_VID_PID = (0x057E, 0x201D)

# kind → ключ локализации названия режима
KIND_KEYS: dict[DeviceKind, str] = {
    DeviceKind.RCM: "mon_kind_rcm",
    DeviceKind.MTP: "mon_kind_mtp",
    DeviceKind.MTP_DBI: "mon_kind_mtp_dbi",
    DeviceKind.OTHER: "mon_kind_other",
}


def classify(vid: int, pid: int) -> DeviceKind:
    if (vid, pid) == RCM_VID_PID:
        return DeviceKind.RCM
    if (vid, pid) == MTP_VID_PID:
        return DeviceKind.MTP
    if (vid, pid) == DBI_MTP_VID_PID:
        return DeviceKind.MTP_DBI
    return DeviceKind.OTHER


def format_vidpid(vid: int, pid: int) -> str:
    return f"{vid:04X}:{pid:04X}"


def headline_key(devices: list[UsbDeviceInfo]) -> str:
    """Ключ локализации общего статуса по списку устройств (приоритет RCM > MTP)."""
    kinds = {classify(d.vendor_id, d.product_id) for d in devices}
    if DeviceKind.RCM in kinds:
        return "mon_rcm"
    if DeviceKind.MTP in kinds or DeviceKind.MTP_DBI in kinds:
        return "mon_mtp"
    return "mon_none"


def dominant_kind(devices: list[UsbDeviceInfo]) -> DeviceKind | None:
    """Основной режим консоли в списке устройств (RCM > MTP), иначе None."""
    kinds = {classify(d.vendor_id, d.product_id) for d in devices}
    if DeviceKind.RCM in kinds:
        return DeviceKind.RCM
    if DeviceKind.MTP in kinds:
        return DeviceKind.MTP
    if DeviceKind.MTP_DBI in kinds:
        return DeviceKind.MTP_DBI
    return None
