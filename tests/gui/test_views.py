"""GUI-тесты вкладок фазы 1: монитор, RCM, поломки, отчёт."""

import json

from diagninten98 import strings
from diagninten98.knowledge.symptoms import GROUPS
from diagninten98.profile import VARIANT_MODCHIP, VARIANT_STOCK, ConsoleProfile
from diagninten98.report import build_report
from diagninten98.strings import tr
from diagninten98.usb.ids import UsbDeviceInfo
from diagninten98.usb.rcm import RcmError
from diagninten98.views import FaultsTab, ReportTab, RcmTab, UsbMonitorTab


def _fake_rcm_device() -> list[UsbDeviceInfo]:
    return [UsbDeviceInfo(0x0955, 0x7321, "USB\\VID_0955&PID_7321\\000", "APX")]


# --- USB-монитор ---


def test_monitor_rcm_detected(qtbot):
    tab = UsbMonitorTab(enumerate_fn=_fake_rcm_device, poll_ms=0)
    qtbot.addWidget(tab)
    assert tab._status_label.text() == tr("mon_rcm")
    snap = tab.snapshot()
    assert snap["status"] == "rcm"
    assert snap["devices"][0]["kind"] == "rcm"
    assert tab._table.rowCount() == 1
    assert tab._table.item(0, 1).text() == "0955:7321"


def test_monitor_no_console(qtbot):
    tab = UsbMonitorTab(enumerate_fn=lambda: [], poll_ms=0)
    qtbot.addWidget(tab)
    assert tab._status_label.text() == tr("mon_none")
    assert tab.snapshot()["status"] == "none"
    assert tab._table.rowCount() == 0


def test_monitor_enumeration_error(qtbot):
    def boom():
        raise RuntimeError("setupapi failure")

    tab = UsbMonitorTab(enumerate_fn=boom, poll_ms=0)
    qtbot.addWidget(tab)
    assert "setupapi failure" in tab._status_label.text()
    snap = tab.snapshot()
    assert snap["status"] == "error"
    assert snap["error"] == "setupapi failure"


def test_monitor_mtp_and_other_rows(qtbot):
    devices = [
        UsbDeviceInfo(0x057E, 0x2010, "i1", "Nintendo Switch"),
        UsbDeviceInfo(0x8087, 0x0024, "i2", "Hub"),
    ]
    tab = UsbMonitorTab(enumerate_fn=lambda: devices, poll_ms=0)
    qtbot.addWidget(tab)
    assert tab._status_label.text() == tr("mon_mtp")
    assert tab._table.rowCount() == 2
    assert tab._table.item(1, 2).text() == tr("mon_kind_other")


# --- RCM ---


def test_rcm_read_ok(qtbot):
    payload = bytes(range(16))
    tab = RcmTab(read_fn=lambda: payload, enumerate_fn=lambda: [], driver_poll_ms=0)
    qtbot.addWidget(tab)
    tab._read_btn.click()
    assert tab._id_value.text() == payload.hex()
    assert tab._id_status.text() == tr("rcm_read_ok")
    assert tab.snapshot()["device_id"] == payload.hex()


def test_rcm_read_fail(qtbot):
    def boom():
        raise RcmError("no device")

    tab = RcmTab(
        read_fn=boom, enumerate_fn=lambda: [], driver_poll_ms=0
    )
    qtbot.addWidget(tab)
    tab._read_btn.click()
    assert tab._id_status.text() == tr("rcm_read_fail")
    assert tab.snapshot()["device_id"] is None
    assert tab.snapshot()["read_error"] == "no device"


def test_rcm_serial_check(qtbot):
    tab = RcmTab(enumerate_fn=lambda: [], driver_poll_ms=0)
    qtbot.addWidget(tab)
    tab._serial_edit.setText("XAW10001234567")
    tab._serial_btn.click()
    assert "erista" in tab._serial_result_label.text()
    assert tab.snapshot()["serial"] == "XAW10001234567"


# --- драйвер APX ---


def test_rcm_driver_hint_no_apx(qtbot):
    tab = RcmTab(enumerate_fn=lambda: [], driver_poll_ms=0)
    qtbot.addWidget(tab)
    assert tab._driver_label.text() == tr("rcm_driver_absent")


def test_rcm_driver_hint_winusb_ok(qtbot):
    devices = [UsbDeviceInfo(0x0955, 0x7321, "i", "APX", service="WinUSB")]
    tab = RcmTab(enumerate_fn=lambda: devices, driver_poll_ms=0)
    qtbot.addWidget(tab)
    assert tab._driver_label.text() == tr("rcm_driver_ok")


def test_rcm_driver_hint_missing(qtbot):
    devices = [UsbDeviceInfo(0x0955, 0x7321, "i", "APX", service="")]
    tab = RcmTab(enumerate_fn=lambda: devices, driver_poll_ms=0)
    qtbot.addWidget(tab)
    text = tab._driver_label.text()
    assert "Zadig" in text and "WinUSB" in text


# --- payload ---


def test_rcm_payload_send_success(qtbot, tmp_path):
    payload_file = tmp_path / "payload.bin"
    payload_file.write_bytes(b"\x00" * 16)
    sent = {}

    def fake_send(path):
        sent["path"] = path
        return True

    tab = RcmTab(
        enumerate_fn=lambda: [],
        driver_poll_ms=0,
        send_fn=fake_send,
        confirm_fn=lambda text: True,
    )
    qtbot.addWidget(tab)
    tab._payload_path.setText(str(payload_file))
    tab._send_btn.click()
    assert sent["path"] == str(payload_file)
    assert tab._payload_status_label.text() == tr("rcm_payload_sent")
    assert tab.snapshot()["payload_status"] == tr("rcm_payload_sent")


def test_rcm_payload_send_declined(qtbot, tmp_path):
    payload_file = tmp_path / "p.bin"
    payload_file.write_bytes(b"x")
    tab = RcmTab(
        enumerate_fn=lambda: [],
        driver_poll_ms=0,
        send_fn=lambda p: True,
        confirm_fn=lambda text: False,
    )
    qtbot.addWidget(tab)
    tab._payload_path.setText(str(payload_file))
    tab._send_btn.click()
    assert tab._payload_status_label.text() == ""  # подтверждения не было — тишина


def test_rcm_payload_no_file(qtbot):
    tab = RcmTab(enumerate_fn=lambda: [], driver_poll_ms=0, confirm_fn=lambda t: True)
    qtbot.addWidget(tab)
    tab._send_btn.click()
    assert tab._payload_status_label.text() == tr("rcm_payload_no_file")


# --- Поломки ---


def test_faults_default_selection(qtbot):
    tab = FaultsTab()
    qtbot.addWidget(tab)
    assert tab._groups_list.count() == len(GROUPS)  # все группы в списке
    assert tab.selected_group_id() == "power"
    assert tab.selected_symptom_id() == "dead"
    assert tab._causes_list.count() >= 3
    snap = tab.snapshot()
    assert snap["symptom_id"] == "dead"
    assert "M92T36" in " ".join(snap["causes"])


def test_faults_switch_symptom(qtbot):
    tab = FaultsTab()
    qtbot.addWidget(tab)
    tab._symptoms_list.setCurrentRow(1)  # black_no_backlight
    assert tab.selected_symptom_id() == "black_no_backlight"
    # 3 базовых причины + 3 модчиповых (для варианта А — в конце списка)
    assert tab._causes_list.count() == 6


def test_faults_retranslate_zh(monkeypatch, qtbot):
    tab = FaultsTab()
    qtbot.addWidget(tab)
    monkeypatch.setattr(strings, "LANG", "zh")
    tab.retranslate()
    assert tab._groups_list.item(0).text() == "电源与开机"
    assert tab.selected_group_id() == "power"  # выбор сохранён
    assert "USB-C" in tab._causes_list.item(0).text()
    assert "M92T36" in tab._causes_list.item(1).text()


# --- профиль консоли ---


def test_rcm_profile_default_stock(qtbot):
    tab = RcmTab(enumerate_fn=lambda: [], driver_poll_ms=0)
    qtbot.addWidget(tab)
    assert tab.profile() == ConsoleProfile()
    assert not tab._chip_combo.isEnabled()  # тип чипа неактивен для варианта А


def test_rcm_profile_switch_to_modchip(qtbot):
    tab = RcmTab(enumerate_fn=lambda: [], driver_poll_ms=0)
    qtbot.addWidget(tab)
    tab._variant_combo.setCurrentIndex(1)  # вариант Б
    tab._chip_combo.setCurrentIndex(0)  # PicoFly
    tab._model_combo.setCurrentIndex(3)  # Switch Lite
    prof = tab.profile()
    assert prof.variant == VARIANT_MODCHIP
    assert prof.chip == "picofly"
    assert prof.model == "lite"
    assert prof.is_mariko
    assert tab._chip_combo.isEnabled()
    snap = tab.snapshot()
    assert snap["profile"] == {"variant": "modchip", "chip": "picofly", "model": "lite"}


def test_rcm_profile_signal(qtbot):
    tab = RcmTab(enumerate_fn=lambda: [], driver_poll_ms=0)
    qtbot.addWidget(tab)
    received = []
    tab.profile_changed.connect(lambda p: received.append(p))
    tab._variant_combo.setCurrentIndex(1)
    assert len(received) == 1
    assert received[0].variant == VARIANT_MODCHIP
    # возврат к А — чип сбрасывается
    tab._variant_combo.setCurrentIndex(0)
    assert received[-1].chip is None


def test_faults_modchip_profile_ranks_modchip_first(qtbot):
    mod = ConsoleProfile(variant=VARIANT_MODCHIP, chip="picofly", model="lite")
    tab = FaultsTab(profile=mod)
    qtbot.addWidget(tab)
    assert tab.selected_group_id() == "modchip"  # группа модчипа — первая
    assert "SD" in tab._causes_list.item(0).text()  # нет SD — причина №1
    # возврат к А: стандартный порядок
    tab.set_profile(ConsoleProfile(variant=VARIANT_STOCK))
    assert tab.selected_group_id() == "power"


def test_faults_modchip_causes_promoted_in_power_group(qtbot):
    mod = ConsoleProfile(variant=VARIANT_MODCHIP)
    tab = FaultsTab(profile=mod)
    qtbot.addWidget(tab)
    tab._groups_list.setCurrentRow(1)  # «Питание» — вторая группа при профиле Б
    tab._symptoms_list.setCurrentRow(0)  # «совсем не включается»
    first_cause = tab._causes_list.item(0).text()
    assert "модчип" in first_cause.lower()  # провода чипа — причина №1 при Б


def test_monitor_rcm_headline_modchip_profile(qtbot):
    tab = UsbMonitorTab(enumerate_fn=_fake_rcm_device, poll_ms=0)
    qtbot.addWidget(tab)
    tab.set_profile_provider(
        lambda: ConsoleProfile(variant=VARIANT_MODCHIP, chip="picofly")
    )
    tab.refresh()
    assert tab._status_label.text() == tr("mon_rcm_modchip")
    tab.set_profile_provider(lambda: ConsoleProfile())  # вариант А — обычный текст
    tab.refresh()
    assert tab._status_label.text() == tr("mon_rcm")


# --- Отчёт ---


def _provider():
    usb = {"devices": [{"vid": 0x0955, "pid": 0x7321, "name": "APX", "kind": "rcm"}],
           "status": "rcm", "error": None}
    rcm = {"device_id": "00ff" * 8, "read_error": None,
           "serial": "", "serial_result": None}
    faults = {"group_id": "power", "group": "Питание", "symptom_id": "dead",
              "symptom": "Не включается", "causes": ["USB-C порт"]}
    return build_report("ru", usb, rcm, faults)


def test_report_generate_and_save(qtbot, tmp_path):
    tab = ReportTab(default_dir=tmp_path)
    qtbot.addWidget(tab)
    tab.set_provider(_provider)
    assert not tab._txt_btn.isEnabled()
    tab._generate_btn.click()
    text = tab._text.toPlainText()
    assert "0955:7321" in text and "00ff00ff" in text
    assert tab._txt_btn.isEnabled()
    tab._txt_btn.click()
    tab._json_btn.click()
    txt_files = list(tmp_path.glob("*.txt"))
    json_files = list(tmp_path.glob("*.json"))
    assert txt_files and json_files
    data = json.loads(json_files[0].read_text(encoding="utf-8"))
    assert data["usb"]["status"] == "rcm"


def test_report_generate_without_provider(qtbot):
    tab = ReportTab(default_dir=".")
    qtbot.addWidget(tab)
    tab._generate_btn.click()
    assert tab._text.toPlainText() == tr("rep_empty")
