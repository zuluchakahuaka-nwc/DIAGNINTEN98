"""Вкладка «USB / Монитор»: перечисление устройств, статус консоли.

Перечисление через SetupAPI (usb.enumerate_win) — работает до установки
драйвера, поэтому APX/RCM виден сразу. Опрос по QTimer (интервал настраивается,
0/None — только вручную; используется в тестах).
"""

from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .. import strings
from ..strings import tr, tr_fmt
from ..usb import enumerate_win
from ..usb.ids import (
    KIND_KEYS,
    DeviceKind,
    UsbDeviceInfo,
    classify,
    dominant_kind,
    format_vidpid,
    headline_key,
)

_COLUMNS = 3  # устройство, VID:PID, режим


class UsbMonitorTab(QWidget):
    def __init__(
        self,
        enumerate_fn=None,
        poll_ms: int = 2000,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("usb_tab")
        self._enumerate = enumerate_fn or enumerate_win.list_usb_devices
        self._devices: list[UsbDeviceInfo] = []
        self._enum_error: str | None = None

        self._status_label = QLabel()
        self._status_label.setWordWrap(True)
        self._status_label.setStyleSheet("font-weight: bold;")

        self._table = QTableWidget(0, _COLUMNS)
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch
        )

        self._refresh_btn = QPushButton()
        self._refresh_btn.clicked.connect(self.refresh)

        self._hint_label = QLabel()
        self._hint_label.setStyleSheet("color: gray;")

        top = QHBoxLayout()
        top.addWidget(self._refresh_btn)
        top.addStretch(1)
        top.addWidget(self._hint_label)

        layout = QVBoxLayout(self)
        layout.addWidget(self._status_label)
        layout.addLayout(top)
        layout.addWidget(self._table)

        self._timer = QTimer(self)
        self._timer.setInterval(max(int(poll_ms), 0))
        if poll_ms and poll_ms > 0:
            self._timer.timeout.connect(self.refresh)
            self._timer.start()

        self.retranslate()
        self.refresh()

    # --- данные ---

    def refresh(self) -> None:
        """Перечислить устройства и перерисовать таблицу/статус."""
        self._enum_error = None
        try:
            self._devices = list(self._enumerate())
        except Exception as exc:  # noqa: BLE001 — показываем любую ошибку перечисления
            self._devices = []
            self._enum_error = str(exc)
        self._render()

    def snapshot(self) -> dict:
        """Снимок состояния для отчёта (чистые данные)."""
        devices = [
            {
                "vid": d.vendor_id,
                "pid": d.product_id,
                "name": d.name,
                "kind": classify(d.vendor_id, d.product_id).name.lower(),
            }
            for d in self._devices
        ]
        status = "error" if self._enum_error else (dominant_kind(self._devices).name.lower() if dominant_kind(self._devices) else "none")
        return {"devices": devices, "status": status, "error": self._enum_error}

    # --- отображение ---

    def retranslate(self) -> None:
        self._refresh_btn.setText(tr("mon_refresh"))
        self._hint_label.setText(tr("mon_hint"))
        self._table.setHorizontalHeaderLabels(
            [tr("mon_device"), tr("mon_vidpid"), tr("mon_kind")]
        )
        self._render()

    def _render(self) -> None:
        if self._enum_error:
            self._status_label.setText(tr_fmt("mon_enum_error", err=self._enum_error))
        else:
            self._status_label.setText(tr(headline_key(self._devices)))

        self._table.setRowCount(len(self._devices))
        for row, dev in enumerate(self._devices):
            kind = classify(dev.vendor_id, dev.product_id)
            self._table.setItem(row, 0, QTableWidgetItem(dev.name or dev.instance_id))
            self._table.setItem(
                row, 1, QTableWidgetItem(format_vidpid(dev.vendor_id, dev.product_id))
            )
            self._table.setItem(row, 2, QTableWidgetItem(tr(KIND_KEYS[kind])))
