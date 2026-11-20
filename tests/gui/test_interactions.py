"""GUI-тесты интерактива: клики по вкладкам (таб-бар), заглушка кодов."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QTabWidget

from diagninten98.app import MainWindow


def _window(qtbot):
    win = MainWindow(usb_enumerate_fn=lambda: [])
    qtbot.addWidget(win)
    return win


def _tabs(win: MainWindow) -> QTabWidget:
    tabs = win.findChild(QTabWidget)
    assert tabs is not None, "QTabWidget не найден"
    return tabs


def test_tab_click_switches_page(qtbot):
    win = _window(qtbot)
    win.show()
    tabs = _tabs(win)
    bar = tabs.tabBar()
    for target in (2, 4, 1):
        qtbot.mouseClick(bar, Qt.LeftButton, pos=bar.tabRect(target).center())
        assert tabs.currentIndex() == target


def test_codes_tab_stub_label(qtbot):
    """Вкладка «Коды ошибок» — заглушка до фазы 3, с непустым текстом."""
    win = _window(qtbot)
    tabs = _tabs(win)
    label = tabs.widget(3).findChild(QLabel, "codes_tab_stub")
    assert label is not None
    assert label.text()
