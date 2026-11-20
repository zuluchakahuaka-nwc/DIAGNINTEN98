"""Вкладка «RCM»: чтение Device ID (только чтение) + ревизия по серийнику."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .. import strings
from ..knowledge import serials
from ..strings import tr
from ..usb import rcm as rcm_mod


class RcmTab(QWidget):
    def __init__(
        self,
        read_fn=None,
        serial_fn=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("rcm_tab")
        self._read = read_fn or rcm_mod.read_device_id
        self._serial_check = serial_fn or serials.check
        self._device_id: str | None = None
        self._read_error: str | None = None
        self._serial_result: str = ""

        # Device ID
        self._id_box = QGroupBox()
        id_layout = QVBoxLayout(self._id_box)
        self._id_value = QLabel("—")
        self._id_value.setStyleSheet("font-family: Consolas, monospace;")
        self._id_status = QLabel()
        self._id_status.setWordWrap(True)
        self._read_btn = QPushButton()
        self._read_btn.clicked.connect(self._on_read)
        id_layout.addWidget(self._read_btn)
        id_layout.addWidget(self._id_value)
        id_layout.addWidget(self._id_status)

        # Серийник
        self._serial_box = QGroupBox()
        serial_layout = QVBoxLayout(self._serial_box)
        self._serial_edit = QLineEdit()
        self._serial_edit.setPlaceholderText("XAW10001234567")
        self._serial_btn = QPushButton()
        self._serial_btn.clicked.connect(self._on_serial)
        self._serial_result_label = QLabel()
        self._serial_result_label.setWordWrap(True)
        serial_layout.addWidget(self._serial_edit)
        serial_btn_row = QHBoxLayout()
        serial_btn_row.addWidget(self._serial_btn)
        serial_btn_row.addStretch(1)
        serial_layout.addLayout(serial_btn_row)
        serial_layout.addWidget(self._serial_result_label)

        layout = QVBoxLayout(self)
        layout.addWidget(self._id_box)
        layout.addWidget(self._serial_box)
        layout.addStretch(1)

        self.retranslate()

    # --- действия ---

    def _on_read(self) -> None:
        self._read_error = None
        try:
            data = self._read()
            self._device_id = rcm_mod.format_device_id(data)
            self._id_status.setText(tr("rcm_read_ok"))
        except Exception as exc:  # noqa: BLE001 — любая ошибка USB показывается
            self._device_id = None
            self._read_error = str(exc)
            self._id_status.setText(tr("rcm_read_fail"))
        self._id_value.setText(self._device_id or "—")

    def _on_serial(self) -> None:
        info = self._serial_check(self._serial_edit.text())
        self._serial_result = info.describe()
        self._serial_result_label.setText(self._serial_result)

    # --- данные ---

    def snapshot(self) -> dict:
        return {
            "device_id": self._device_id,
            "read_error": self._read_error,
            "serial": self._serial_edit.text().strip().upper(),
            "serial_result": self._serial_result or None,
        }

    # --- отображение ---

    def retranslate(self) -> None:
        self._id_box.setTitle(tr("rcm_id_title"))
        self._read_btn.setText(tr("rcm_read_btn"))
        self._serial_box.setTitle(tr("rcm_serial_title"))
        self._serial_btn.setText(tr("rcm_serial_btn"))
