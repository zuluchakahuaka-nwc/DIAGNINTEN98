"""Тесты разбора серийного номера Switch."""

import pytest

from diagninten98 import strings
from diagninten98.knowledge.serials import check


def test_erista_americas():
    info = check("XAW10001234567")
    assert info.ok
    assert info.region_key == "serial_region_us"
    assert info.generation_key == "serial_gen_erista"


def test_mariko_japan_case_insensitive():
    info = check(" xkj20001234567 ")
    assert info.ok
    assert info.region_key == "serial_region_jp"
    assert info.generation_key == "serial_gen_mariko"


def test_bad_format():
    for bad in ("", "12345", "XAW123", "XAW100012345678901234", "SW-1234"):
        info = check(bad)
        assert not info.ok, bad


def test_unknown_prefix_still_ok():
    info = check("XQZ90001234567")
    assert info.ok
    assert info.region_key == "serial_region_unknown"


def test_xke_mariko_europe():
    """XKE — Европа, эра mariko (V2): вторая буква K."""
    info = check("XKE10001234567")
    assert info.ok
    assert info.region_key == "serial_region_eu"
    assert info.generation_key == "serial_gen_mariko"


def test_xje_lite_unknown_generation():
    """XJE — префикс Switch Lite (HDH-001); поколение по второй букве неизвестно."""
    info = check("XJE10013236891")
    assert info.ok
    assert info.generation_key == "serial_gen_unknown"


def test_describe_bad_format_localized(monkeypatch):
    monkeypatch.setattr(strings, "LANG", "ru")
    info = check("nope")
    assert not info.ok
    assert "серийн" in info.describe()


def test_describe_ok_localized(monkeypatch):
    monkeypatch.setattr(strings, "LANG", "en")
    info = check("XAW10001234567")
    text = info.describe()
    assert "Americas" in text
    assert "erista" in text
