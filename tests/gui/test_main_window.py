"""GUI-тесты главного окна (pytest-qt, offscreen)."""

import pytest
from PySide6.QtWidgets import QComboBox, QTabWidget

from diagninten98 import app as app_module
from diagninten98.app import LANGS, STRINGS, TABS, MainWindow


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
    monkeypatch.setattr(app_module, "LANG", "ru")


def _titles(win: MainWindow) -> list[str]:
    tabs = win.findChild(QTabWidget)
    assert tabs is not None
    return [tabs.tabText(i) for i in range(tabs.count())]


def test_window_title(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)
    assert "DIAGNINTEN98" in win.windowTitle()
    assert win.windowTitle().count("0.") > 0  # версия в заголовке


def test_five_tabs_with_expected_titles(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)
    expected = [STRINGS[key][0] for key, _stub in TABS]  # ru по умолчанию
    assert _titles(win) == expected


def test_language_combo_present(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)
    combo = win.findChild(QComboBox)
    assert combo is not None
    assert combo.count() == len(LANGS)
    assert [combo.itemText(i) for i in range(combo.count())] == [
        "Русский", "English", "中文"
    ]


def test_switch_to_zh_updates_tabs(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)
    combo = win.findChild(QComboBox)
    combo.setCurrentIndex(LANGS.index("zh"))
    assert app_module.LANG == "zh"
    expected = [STRINGS[key][2] for key, _stub in TABS]
    assert _titles(win) == expected


def test_switch_to_en_updates_tabs(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)
    combo = win.findChild(QComboBox)
    combo.setCurrentIndex(LANGS.index("en"))
    assert app_module.LANG == "en"
    expected = [STRINGS[key][1] for key, _stub in TABS]
    assert _titles(win) == expected
