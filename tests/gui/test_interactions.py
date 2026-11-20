"""GUI-тесты интерактива: клики по вкладкам (таб-бар)."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QTabWidget

from diagninten98.app import MainWindow


def _tabs(win: MainWindow) -> QTabWidget:
    tabs = win.findChild(QTabWidget)
    assert tabs is not None, "QTabWidget не найден"
    return tabs


def test_tab_click_switches_page(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)
    win.show()
    tabs = _tabs(win)
    bar = tabs.tabBar()
    for target in (2, 4, 1):
        qtbot.mouseClick(bar, Qt.LeftButton, pos=bar.tabRect(target).center())
        assert tabs.currentIndex() == target


def test_placeholder_label_present(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)
    tabs = _tabs(win)
    label = tabs.widget(0).findChild(QLabel)
    assert label is not None
    assert label.text()  # заглушка с непустым текстом
