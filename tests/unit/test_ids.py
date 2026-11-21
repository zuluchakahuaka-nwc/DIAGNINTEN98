"""Тесты классификации USB-устройств Switch."""

from diagninten98.usb.ids import (
    DeviceKind,
    UsbDeviceInfo,
    classify,
    dominant_kind,
    format_vidpid,
    headline_key,
)


def dev(vid: int, pid: int) -> UsbDeviceInfo:
    return UsbDeviceInfo(vid, pid)


def test_classify_known():
    assert classify(0x0955, 0x7321) is DeviceKind.RCM
    assert classify(0x057E, 0x2010) is DeviceKind.MTP
    # DBI (хомбрю-установщик) в MTP-режиме — подтверждено живой консолью
    assert classify(0x057E, 0x201D) is DeviceKind.MTP_DBI


def test_classify_other():
    assert classify(0x1234, 0x5678) is DeviceKind.OTHER


def test_format_vidpid():
    assert format_vidpid(0x0955, 0x7321) == "0955:7321"
    assert format_vidpid(0x05, 0x0A) == "0005:000A"


def test_headline_priority_rcm_over_mtp():
    devices = [dev(0x057E, 0x2010), dev(0x0955, 0x7321)]
    assert headline_key(devices) == "mon_rcm"


def test_headline_mtp_and_none():
    assert headline_key([dev(0x057E, 0x2010)]) == "mon_mtp"
    assert headline_key([]) == "mon_none"
    assert headline_key([dev(0x1111, 0x2222)]) == "mon_none"


def test_dominant_kind():
    assert dominant_kind([dev(0x0955, 0x7321)]) is DeviceKind.RCM
    assert dominant_kind([dev(0x1111, 0x2222)]) is None
    assert dominant_kind([]) is None


def test_dbi_counts_as_booted_system():
    """DBI в MTP-режиме = система полностью загружена (статус mon_mtp)."""
    dbi = [dev(0x057E, 0x201D)]
    assert headline_key(dbi) == "mon_mtp"
    assert dominant_kind(dbi) is DeviceKind.MTP_DBI
    # RCM приоритетнее, даже если рядом DBI
    mixed = [dev(0x057E, 0x201D), dev(0x0955, 0x7321)]
    assert headline_key(mixed) == "mon_rcm"
