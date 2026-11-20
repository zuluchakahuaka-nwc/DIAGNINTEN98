"""Точка входа GUI. Фаза 0: каркас окна с вкладками.

Фаза 1 наполнит вкладки реальной логикой:
  USB-монитор, RCM-диагностика, мастер поломок, отчёт.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

APP_TITLE = "DIAGNINTEN98 — Nintendo Switch Diagnostics"
VERSION = "0.1.0"

# Двуязычный UI (RU/EN). Пока — константа, позже настройка в конфиге.
STRINGS = {
    "usb_tab": ("USB / Монитор", "USB / Monitor"),
    "rcm_tab": ("RCM", "RCM"),
    "faults_tab": ("Поломки", "Faults"),
    "codes_tab": ("Коды ошибок", "Error codes"),
    "report_tab": ("Отчёт", "Report"),
    "phase1_stub": ("Реализация — фаза 1", "Implementation — phase 1"),
    "phase3_stub": ("Реализация — фаза 3", "Implementation — phase 3"),
}
LANG = "ru"  # "ru" | "en"


def tr(key: str) -> str:
    ru, en = STRINGS[key]
    return ru if LANG == "ru" else en


def _placeholder(text: str) -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setAlignment(Qt.AlignCenter)
    layout.addWidget(QLabel(text))
    return widget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE} v{VERSION}")
        self.resize(960, 640)

        tabs = QTabWidget()
        tabs.addTab(_placeholder(tr("phase1_stub")), tr("usb_tab"))
        tabs.addTab(_placeholder(tr("phase1_stub")), tr("rcm_tab"))
        tabs.addTab(_placeholder(tr("phase1_stub")), tr("faults_tab"))
        tabs.addTab(_placeholder(tr("phase3_stub")), tr("codes_tab"))
        tabs.addTab(_placeholder(tr("phase1_stub")), tr("report_tab"))
        self.setCentralWidget(tabs)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
