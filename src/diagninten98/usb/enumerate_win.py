"""Перечисление USB-устройств Windows через cfgmgr32 (CM_* API).

Почему не SetupDiGetClassDevs: на части сборок Windows вызов с энумератором
возвращал INVALID_HANDLE_VALUE с ERROR_INVALID_PARAMETER (наблюдено на машине
разработки 2026-11-20), тогда как cfgmgr32-вариант проще и работает:
CM_Get_Device_ID_ListW("USB", PRESENT|ENUMERATOR) — один вызов, без структур.
Имя устройства — CM_Get_DevNode_Registry_PropertyW (CM_DRP_DEVICEDESC).

CM-API видит устройства без установленного драйвера — консоль в RCM (APX)
видна ещё до установки WinUSB (Zadig).
"""

from __future__ import annotations

import ctypes
import re
import sys
from ctypes import wintypes

from .ids import UsbDeviceInfo

CM_GETIDLIST_FILTER_ENUMERATOR = 0x00000001
CM_GETIDLIST_FILTER_PRESENT = 0x00000100
CM_LOCATE_DEVNODE_NORMAL = 0x00000000
CM_DRP_DEVICEDESC = 0x00000001
CM_DRP_SERVICE = 0x00000005  # = SPDRP_SERVICE (0x4) + 1

_VID_PID_RE = re.compile(r"VID_([0-9A-Fa-f]{4})&PID_([0-9A-Fa-f]{4})")


def _load_cfgmgr32():
    cfg = ctypes.WinDLL("cfgmgr32", use_last_error=True)
    cfg.CM_Get_Device_ID_List_SizeW.argtypes = (
        ctypes.POINTER(wintypes.ULONG), ctypes.c_wchar_p, wintypes.ULONG,
    )
    cfg.CM_Get_Device_ID_List_SizeW.restype = wintypes.DWORD  # CONFIGRET
    cfg.CM_Get_Device_ID_ListW.argtypes = (
        ctypes.c_wchar_p, ctypes.c_wchar_p, wintypes.ULONG, wintypes.ULONG,
    )
    cfg.CM_Get_Device_ID_ListW.restype = wintypes.DWORD
    cfg.CM_Locate_DevNodeW.argtypes = (
        ctypes.POINTER(wintypes.DWORD), ctypes.c_wchar_p, wintypes.ULONG,
    )
    cfg.CM_Locate_DevNodeW.restype = wintypes.DWORD
    cfg.CM_Get_DevNode_Registry_PropertyW.argtypes = (
        wintypes.DWORD, wintypes.ULONG, ctypes.POINTER(wintypes.ULONG),
        ctypes.c_void_p, ctypes.POINTER(wintypes.ULONG), wintypes.ULONG,
    )
    cfg.CM_Get_DevNode_Registry_PropertyW.restype = wintypes.DWORD
    return cfg


def _device_property(cfg, device_id: str, prop: int) -> str:
    devinst = wintypes.DWORD(0)
    if cfg.CM_Locate_DevNodeW(
        ctypes.byref(devinst), device_id, CM_LOCATE_DEVNODE_NORMAL
    ) != 0:
        return ""
    buf = ctypes.create_unicode_buffer(512)
    buflen = wintypes.ULONG(ctypes.sizeof(buf))
    reg_type = wintypes.ULONG(0)
    if cfg.CM_Get_DevNode_Registry_PropertyW(
        devinst.value, prop, ctypes.byref(reg_type),
        ctypes.cast(buf, ctypes.c_void_p), ctypes.byref(buflen), 0,
    ) != 0:
        return ""
    return buf.value


def _device_name(cfg, device_id: str) -> str:
    return _device_property(cfg, device_id, CM_DRP_DEVICEDESC)


def list_usb_devices() -> list[UsbDeviceInfo]:
    """Присутствующие устройства ветки USB (enumerator 'USB', только live).

    Работает без установленного драйвера — APX/RCM виден сразу.
    """
    if sys.platform != "win32":
        return []

    cfg = _load_cfgmgr32()
    flags = CM_GETIDLIST_FILTER_ENUMERATOR | CM_GETIDLIST_FILTER_PRESENT

    size = wintypes.ULONG(0)
    if cfg.CM_Get_Device_ID_List_SizeW(ctypes.byref(size), "USB", flags) != 0:
        raise OSError("CM_Get_Device_ID_List_SizeW failed")
    buf = ctypes.create_unicode_buffer(size.value)
    if cfg.CM_Get_Device_ID_ListW("USB", buf, size.value, flags) != 0:
        raise OSError("CM_Get_Device_ID_ListW failed")

    raw = ctypes.wstring_at(ctypes.addressof(buf), size.value)
    devices: list[UsbDeviceInfo] = []
    for device_id in (part for part in raw.split("\0") if part):
        match = _VID_PID_RE.search(device_id)
        if not match:
            continue
        devices.append(
            UsbDeviceInfo(
                vendor_id=int(match.group(1), 16),
                product_id=int(match.group(2), 16),
                instance_id=device_id,
                name=_device_name(cfg, device_id),
                service=_device_property(cfg, device_id, CM_DRP_SERVICE),
            )
        )
    return devices
