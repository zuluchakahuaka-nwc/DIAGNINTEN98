"""Вкладка «RCM»: профиль консоли, Device ID (чтение), драйвер APX, payload, серийник."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .. import strings
from ..knowledge import serials
from ..profile import (
    CHIP_TYPES,
    MODELS,
    VARIANT_MODCHIP,
    VARIANT_STOCK,
    ConsoleProfile,
)
from ..strings import tr, tr_fmt
from ..usb import enumerate_win
from ..usb import payload as payload_mod
from ..usb import rcm as rcm_mod
from ..usb.ids import RCM_VID_PID, UsbDeviceInfo

_CHIP_KEYS = {"picofly": "chip_picofly", "hwfly": "chip_hwfly", "other": "chip_other"}
_VARIANT_KEYS = {VARIANT_STOCK: "profile_variant_a", VARIANT_MODCHIP: "profile_variant_b"}
_MODEL_KEYS = {
    "unknown": "model_unknown",
    "standard_v1": "model_standard_v1",
    "standard_v2": "model_standard_v2",
    "lite": "model_lite",
    "oled": "model_oled",
}


class RcmTab(QWidget):
    profile_changed = Signal(object)  # ConsoleProfile

    def __init__(
        self,
        read_fn=None,
        serial_fn=None,
        enumerate_fn=None,
        send_fn=None,
        confirm_fn=None,
        driver_poll_ms: int = 3000,
        initial_profile: ConsoleProfile | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("rcm_tab")
        self._read = read_fn or rcm_mod.read_device_id
        self._serial_check = serial_fn or serials.check
        self._enumerate = enumerate_fn or enumerate_win.list_usb_devices
        self._send = send_fn or payload_mod.launch_from_file
        self._confirm = confirm_fn or (lambda text: QMessageBox.question(
            self, tr("rcm_payload_title"), text,
            QMessageBox.Yes | QMessageBox.No,
        ) == QMessageBox.Yes)

        self._device_id: str | None = None
        self._read_error: str | None = None
        self._serial_result: str = ""
        self._payload_status: str = ""
        self._profile = initial_profile or ConsoleProfile()

        # Профиль консоли (вариант А/Б + чип + модель)
        self._profile_box = QGroupBox()
        profile_layout = QVBoxLayout(self._profile_box)
        self._variant_combo = QComboBox()
        self._chip_combo = QComboBox()
        self._model_combo = QComboBox()
        self._variant_combo.currentIndexChanged.connect(lambda _: self._on_profile())
        self._chip_combo.currentIndexChanged.connect(lambda _: self._on_profile())
        self._model_combo.currentIndexChanged.connect(lambda _: self._on_profile())
        variant_row = QHBoxLayout()
        variant_row.addWidget(self._variant_combo, 2)
        variant_row.addWidget(self._chip_combo, 2)
        variant_row.addWidget(self._model_combo, 2)
        profile_layout.addLayout(variant_row)
        self._fill_profile_combos()

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

        # Драйвер APX
        self._driver_box = QGroupBox()
        driver_layout = QVBoxLayout(self._driver_box)
        self._driver_label = QLabel()
        self._driver_label.setWordWrap(True)
        driver_layout.addWidget(self._driver_label)

        # Payload
        self._payload_box = QGroupBox()
        payload_layout = QVBoxLayout(self._payload_box)
        self._payload_path = QLineEdit()
        self._payload_path.setPlaceholderText(tr("rcm_payload_path_hint"))
        self._browse_btn = QPushButton()
        self._browse_btn.clicked.connect(self._on_browse)
        self._send_btn = QPushButton()
        self._send_btn.clicked.connect(self._on_send)
        path_row = QHBoxLayout()
        path_row.addWidget(self._payload_path, 1)
        path_row.addWidget(self._browse_btn)
        send_row = QHBoxLayout()
        send_row.addWidget(self._send_btn)
        send_row.addStretch(1)
        self._payload_status_label = QLabel()
        self._payload_status_label.setWordWrap(True)
        payload_layout.addLayout(path_row)
        payload_layout.addLayout(send_row)
        payload_layout.addWidget(self._payload_status_label)

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
        layout.addWidget(self._profile_box)
        layout.addWidget(self._id_box)
        layout.addWidget(self._driver_box)
        layout.addWidget(self._payload_box)
        layout.addWidget(self._serial_box)
        layout.addStretch(1)

        self._driver_timer = QTimer(self)
        self._driver_timer.setInterval(max(int(driver_poll_ms), 0))
        if driver_poll_ms and driver_poll_ms > 0:
            self._driver_timer.timeout.connect(self._refresh_driver_hint)
            self._driver_timer.start()

        self.retranslate()
        self._refresh_driver_hint()

    # --- профиль ---

    def _fill_profile_combos(self) -> None:
        """Наполнить комбобоксы профиля (ключи в userData), сохраняя выбор."""
        def refill(combo, items, selected, tr_key):
            combo.blockSignals(True)
            combo.clear()
            for key in items:
                combo.addItem(strings.tr(tr_key(key)), key)
            index = list(items).index(selected) if selected in items else 0
            combo.setCurrentIndex(index)
            combo.blockSignals(False)

        refill(self._variant_combo, (VARIANT_STOCK, VARIANT_MODCHIP),
               self._profile.variant, lambda k: _VARIANT_KEYS[k])
        refill(self._chip_combo, CHIP_TYPES, self._profile.chip_or_default,
               lambda k: _CHIP_KEYS[k])
        refill(self._model_combo, MODELS, self._profile.model,
               lambda k: _MODEL_KEYS[k])
        self._chip_combo.setEnabled(self._profile.is_modchip)

    def profile(self) -> ConsoleProfile:
        """Текущий профиль из комбобоксов."""
        variant = self._variant_combo.currentData() or VARIANT_STOCK
        chip = self._chip_combo.currentData() if variant == VARIANT_MODCHIP else None
        model = self._model_combo.currentData() or "unknown"
        return ConsoleProfile(variant=str(variant), chip=chip, model=str(model))

    def _on_profile(self) -> None:
        self._profile = self.profile()
        self._chip_combo.setEnabled(self._profile.is_modchip)
        self.profile_changed.emit(self._profile)

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

    def _on_browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, tr("rcm_payload_title"), "", "Payload (*.bin);;All files (*)"
        )
        if path:
            self._payload_path.setText(path)

    def _on_send(self) -> None:
        path = self._payload_path.text().strip()
        if not path or not Path(path).is_file():
            self._set_payload_status(tr("rcm_payload_no_file"))
            return
        if not self._confirm(tr("rcm_payload_confirm")):
            return
        try:
            launched = self._send(path)
        except Exception as exc:  # noqa: BLE001
            self._set_payload_status(tr_fmt("rcm_payload_error", err=exc))
            return
        key = "rcm_payload_sent" if launched else "rcm_payload_not_smashed"
        self._set_payload_status(tr(key))

    def _set_payload_status(self, text: str) -> None:
        self._payload_status = text
        self._payload_status_label.setText(text)

    def _on_serial(self) -> None:
        info = self._serial_check(self._serial_edit.text())
        self._serial_result = info.describe()
        self._serial_result_label.setText(self._serial_result)

    # --- драйвер ---

    def _refresh_driver_hint(self) -> None:
        try:
            devices = list(self._enumerate())
        except Exception:  # noqa: BLE001 — без перечисления просто тишина
            return
        self.update_driver_hint(devices)

    def update_driver_hint(self, devices: list[UsbDeviceInfo]) -> None:
        """Показать статус драйвера APX (по service-полю устройства)."""
        apx = [
            d
            for d in devices
            if (d.vendor_id, d.product_id) == RCM_VID_PID
        ]
        if not apx:
            self._driver_label.setText(tr("rcm_driver_absent"))
            return
        service = (apx[0].service or "").lower()
        if "winusb" in service:
            self._driver_label.setText(tr("rcm_driver_ok"))
            self._driver_label.setStyleSheet("color: green;")
        else:
            self._driver_label.setText(
                tr("rcm_driver_missing") + "\n" + tr("rcm_zadig_steps")
            )
            self._driver_label.setStyleSheet("color: darkorange;")

    # --- данные ---

    def snapshot(self) -> dict:
        return {
            "profile": self.profile().as_dict(),
            "device_id": self._device_id,
            "read_error": self._read_error,
            "serial": self._serial_edit.text().strip().upper(),
            "serial_result": self._serial_result or None,
            "payload_path": self._payload_path.text().strip() or None,
            "payload_status": self._payload_status or None,
        }

    # --- отображение ---

    def retranslate(self) -> None:
        self._profile_box.setTitle(tr("profile_title"))
        self._fill_profile_combos()
        self._id_box.setTitle(tr("rcm_id_title"))
        self._read_btn.setText(tr("rcm_read_btn"))
        self._driver_box.setTitle(tr("rcm_driver_title"))
        self._payload_box.setTitle(tr("rcm_payload_title"))
        self._browse_btn.setText(tr("rcm_payload_browse"))
        self._send_btn.setText(tr("rcm_payload_send"))
        self._serial_box.setTitle(tr("rcm_serial_title"))
        self._serial_btn.setText(tr("rcm_serial_btn"))
