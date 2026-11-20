"""Тесты модели отчёта и экспорта TXT/JSON."""

import json

from diagninten98.report import build_report, render_txt, save_json, save_txt


def _sample(lang: str = "ru") -> dict:
    usb = {
        "devices": [
            {"vid": 0x0955, "pid": 0x7321, "name": "APX", "kind": "rcm"},
            {"vid": 0x057E, "pid": 0x2010, "name": "Switch", "kind": "mtp"},
        ],
        "status": "rcm",
        "error": None,
    }
    rcm = {
        "device_id": "00112233445566778899aabbccddeeff",
        "read_error": None,
        "serial": "XAW10001234567",
        "serial_result": "регион: Америка, поколение: erista",
    }
    faults = {
        "group_id": "power",
        "group": "Питание и включение",
        "symptom_id": "dead",
        "symptom": "Совсем не включается",
        "causes": ["USB-C порт", "M92T36", "BQ24193"],
    }
    return build_report(lang, usb, rcm, faults)


def test_build_report_structure():
    report = _sample()
    assert report["tool"]["name"] == "DIAGNINTEN98"
    assert report["usb"]["status"] == "rcm"
    assert report["rcm"]["device_id"].startswith("0011")
    assert report["faults"]["causes"]


def test_render_txt_contains_data():
    text = render_txt(_sample())
    assert "0955:7321" in text
    assert "00112233445566778899aabbccddeeff" in text
    assert "XAW10001234567" in text
    assert "M92T36" in text


def test_render_txt_localized():
    text = render_txt(_sample("en"))
    assert "USB devices" in text
    assert "Fault analysis" in text


def test_render_txt_empty_sections():
    report = build_report(
        "ru", {"devices": [], "status": "none", "error": None},
        {"device_id": None, "read_error": None, "serial": "", "serial_result": None},
        {"group_id": None, "group": None, "symptom_id": None, "symptom": None, "causes": []},
    )
    text = render_txt(report)
    assert "не проводилось" in text


def test_save_roundtrip(tmp_path):
    report = _sample()
    txt_path = save_txt(report, tmp_path)
    json_path = save_json(report, tmp_path)
    assert txt_path.exists() and json_path.exists()
    assert txt_path.suffix == ".txt" and json_path.suffix == ".json"
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["rcm"]["serial"] == "XAW10001234567"
    # язык после рендера восстановлен
    from diagninten98 import strings

    assert strings.LANG == "ru"
