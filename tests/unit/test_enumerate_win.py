"""Смоук-тест SetupAPI-энумератора (только Windows, реальная система)."""

import sys

import pytest

from diagninten98.usb.enumerate_win import list_usb_devices

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows only")


def test_list_usb_devices_smoke():
    devices = list_usb_devices()
    assert isinstance(devices, list)
    for d in devices:
        assert 0 <= d.vendor_id <= 0xFFFF
        assert 0 <= d.product_id <= 0xFFFF
        assert "VID_" in d.instance_id or d.instance_id == ""
