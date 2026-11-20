"""Точка входа GUI.

Фаза 0: каркас окна с вкладками и выбором языка интерфейса (RU/EN/ZH).
Фаза 1 наполнит вкладки реальной логикой: USB-монитор, RCM, мастер поломок, отчёт.
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

APP_TITLE = "DIAGNINTEN98 — Nintendo Switch Diagnostics"
VERSION = "0.1.0"

# Языки интерфейса; порядок элементов в STRINGS соответствует этому кортежу.
LANGS: tuple[str, ...] = ("ru", "en", "zh")
LANG_NAMES: dict[str, str] = {"ru": "Русский", "en": "English", "zh": "中文"}

STRINGS: dict[str, tuple[str, str, str]] = {
    # (ru, en, zh)
    "usb_tab": ("USB / Монитор", "USB / Monitor", "USB / 监控"),
    "rcm_tab": ("RCM", "RCM", "RCM"),
    "faults_tab": ("Поломки", "Faults", "故障"),
    "codes_tab": ("Коды ошибок", "Error codes", "错误代码"),
    "report_tab": ("Отчёт", "Report", "报告"),
    "phase1_stub": ("Реализация — фаза 1", "Implementation — phase 1", "实现 — 阶段 1"),
    "phase3_stub": ("Реализация — фаза 3", "Implementation — phase 3", "实现 — 阶段 3"),
    "language": ("Язык", "Language", "语言"),
}

# Текущий язык (используется tr()); переключается из GUI.
LANG = "ru"

# Порядок вкладок: (ключ локализации заголовка, ключ заглушки-контента).
# Ключи ASCII — по ним именуются скриншоты (см. diagninten98.capture).
TABS: list[tuple[str, str]] = [
    ("usb_tab", "phase1_stub"),
    ("rcm_tab", "phase1_stub"),
    ("faults_tab", "phase1_stub"),
    ("codes_tab", "phase3_stub"),
    ("report_tab", "phase1_stub"),
]


def tr(key: str) -> str:
    return STRINGS[key][LANGS.index(LANG)]


def _placeholder(text: str) -> tuple[QWidget, QLabel]:
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setAlignment(Qt.AlignCenter)
    label = QLabel(text)
    layout.addWidget(label)
    return widget, label


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE} v{VERSION}")
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
        self._tabs = QTabWidget()
        self._stub_labels: list[tuple[str, QLabel]] = []
        for key, stub_key in TABS:
            page, label = _placeholder(tr(stub_key))
            page.setObjectName(key)  # стабильное ASCII-имя для тестов/скриншотов
            self._tabs.addTab(page, tr(key))
            self._stub_labels.append((stub_key, label))
        root.addWidget(self._tabs)
        self.setCentralWidget(central)

        saved = str(self._settings.value("language", LANG))
        if saved not in LANGS:
            saved = LANG
        self._lang_combo.setCurrentIndex(LANGS.index(saved))
        self._apply_language(saved)

    def _on_language_changed(self, index: int) -> None:
        code = self._lang_combo.itemData(index)
        if code:
            self._apply_language(str(code))

    def _apply_language(self, code: str) -> None:
        global LANG
        LANG = code
        self._settings.setValue("language", code)
        self._retranslate()

    def _retranslate(self) -> None:
        self._lang_label.setText(tr("language"))
        for i, (key, _stub) in enumerate(TABS):
            self._tabs.setTabText(i, tr(key))
        for stub_key, label in self._stub_labels:
            label.setText(tr(stub_key))


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
