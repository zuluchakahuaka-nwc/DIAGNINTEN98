"""GUI-тесты главного окна (pytest-qt, offscreen)."""

import pytest
from PySide6.QtWidgets import QComboBox, QTabWidget

from diagninten98 import app as app_module
from diagninten98 import strings as strings_module
from diagninten98.app import MainWindow
from diagninten98.strings import LANGS, STRINGS as _S

TAB_KEYS = ["usb_tab", "rcm_tab", "faults_tab", "codes_tab", "report_tab"]


class _FakeSettings:
    """QSettings без записи в реестр — тесты не оставляют следов в системе."""

    def __init__(self, *args, **kwargs):
        self.values: dict[str, object] = {}

    def value(self, key, default=None):
        return self.values.get(key, default)

    def setValue(self, key, value):
        self.values[key] = value


@pytest.fixture(autouse=True)
def _isolated_env(monkeypatch):
    monkeypatch.setattr(app_module, "QSettings", _FakeSettings)
    monkeypatch.setattr(strings_module, "LANG", "ru")


def _window(qtbot):
    win = MainWindow(usb_enumerate_fn=lambda: [])
    qtbot.addWidget(win)
    return win


def _titles(win: MainWindow) -> list[str]:
    tabs = win.findChild(QTabWidget)
    assert tabs is not None
    return [tabs.tabText(i) for i in range(tabs.count())]


def test_window_title(qtbot):
    win = _window(qtbot)
    assert "DIAGNINTEN98" in win.windowTitle()
    assert win.windowTitle().count("0.") > 0  # версия в заголовке


def test_five_tabs_with_expected_titles(qtbot):
    win = _window(qtbot)
    expected = [_S[key][0] for key in TAB_KEYS]  # ru по умолчанию
    assert _titles(win) == expected


def test_language_combo_present(qtbot):
    win = _window(qtbot)
    combo = win.findChild(QComboBox)
    assert combo is not None
    assert combo.count() == len(LANGS)
    assert [combo.itemText(i) for i in range(combo.count())] == [
        "Русский", "English", "中文"
    ]


def test_switch_to_zh_updates_tabs(qtbot):
    win = _window(qtbot)
    combo = win.findChild(QComboBox)
    combo.setCurrentIndex(LANGS.index("zh"))
    assert strings_module.LANG == "zh"
    expected = [_S[key][2] for key in TAB_KEYS]
    assert _titles(win) == expected


def test_switch_to_en_updates_tabs(qtbot):
    win = _window(qtbot)
    combo = win.findChild(QComboBox)
    combo.setCurrentIndex(LANGS.index("en"))
    assert strings_module.LANG == "en"
    expected = [_S[key][1] for key in TAB_KEYS]
    assert _titles(win) == expected
