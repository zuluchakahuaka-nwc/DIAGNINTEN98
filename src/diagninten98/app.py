"""Точка входа GUI: окно с вкладками, выбор языка, сборка отчёта.

Вкладки фаз: USB-монитор, RCM, Поломки, Отчёт — реальная логика (фаза 1);
«Коды ошибок» — заглушка до фазы 3.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from . import __version__, report as report_mod
from . import strings
from .strings import LANG_NAMES, LANGS, tr
from .views import FaultsTab, RcmTab, ReportTab, UsbMonitorTab

APP_TITLE = "DIAGNINTEN98 — Nintendo Switch Diagnostics"

# Порядок вкладок: ключ локализации заголовка (он же objectName страницы).
TAB_KEYS = ["usb_tab", "rcm_tab", "faults_tab", "codes_tab", "report_tab"]


class MainWindow(QMainWindow):
    def __init__(
        self,
        usb_enumerate_fn=None,
        usb_poll_ms: int = 2000,
        rcm_enumerate_fn=None,
        rcm_driver_poll_ms: int = 3000,
        report_dir: str = "reports",
    ) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE} v{__version__}")
        self.resize(960, 640)
        self._settings = QSettings("diagninten98", "diagninten98")

        central = QWidget()
        root = QVBoxLayout(central)

        # Верхняя панель: выбор языка.
        top = QHBoxLayout()
        self._lang_label = QLabel(tr("language"))
        self._lang_combo = QComboBox()
        for code in LANGS:
            self._lang_combo.addItem(LANG_NAMES[code], code)
        self._lang_combo.currentIndexChanged.connect(self._on_language_changed)
        top.addWidget(self._lang_label)
        top.addWidget(self._lang_combo)
        top.addStretch(1)
        root.addLayout(top)

        # Вкладки.
        self.usb_tab = UsbMonitorTab(enumerate_fn=usb_enumerate_fn, poll_ms=usb_poll_ms)
        self.rcm_tab = RcmTab(
            enumerate_fn=rcm_enumerate_fn, driver_poll_ms=rcm_driver_poll_ms
        )
        self.faults_tab = FaultsTab()
        self.codes_tab = self._make_stub_page("codes_tab", "phase3_stub")
        self.report_tab = ReportTab(default_dir=report_dir)
        self.report_tab.set_provider(self._build_report)

        self._tabs = QTabWidget()
        for key, page in zip(
            TAB_KEYS,
            (self.usb_tab, self.rcm_tab, self.faults_tab, self.codes_tab, self.report_tab),
        ):
            page.setObjectName(key)
            self._tabs.addTab(page, tr(key))
        root.addWidget(self._tabs)
        self.setCentralWidget(central)

        saved = str(self._settings.value("language", strings.LANG))
        if saved not in LANGS:
            saved = strings.LANG
        self._lang_combo.setCurrentIndex(LANGS.index(saved))
        self._apply_language(saved)

    @staticmethod
    def _make_stub_page(object_name: str, text_key: str) -> QWidget:
        page = QWidget()
        page.setObjectName(object_name)
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel(tr(text_key))
        label.setObjectName(f"{object_name}_stub")
        layout.addWidget(label)
        return page

    def _build_report(self) -> dict:
        """Провайдер для вкладки отчёта: снапшоты всех вкладок."""
        return report_mod.build_report(
            strings.LANG,
            self.usb_tab.snapshot(),
            self.rcm_tab.snapshot(),
            self.faults_tab.snapshot(),
        )

    def _on_language_changed(self, index: int) -> None:
        code = self._lang_combo.itemData(index)
        if code:
            self._apply_language(str(code))

    def _apply_language(self, code: str) -> None:
        strings.set_language(code)
        self._settings.setValue("language", code)
        self._retranslate()

    def _retranslate(self) -> None:
        self._lang_label.setText(tr("language"))
        for i, key in enumerate(TAB_KEYS):
            self._tabs.setTabText(i, tr(key))
        stub = self.codes_tab.findChild(QLabel, "codes_tab_stub")
        if stub is not None:
            stub.setText(tr("phase3_stub"))
        self.usb_tab.retranslate()
        self.rcm_tab.retranslate()
        self.faults_tab.retranslate()
        self.report_tab.retranslate()


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
