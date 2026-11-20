"""Вкладка «Отчёт»: сборка отчёта из снапшотов и сохранение TXT/JSON."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .. import report as report_mod
from ..strings import tr, tr_fmt


class ReportTab(QWidget):
    def __init__(
        self,
        default_dir: Path | str = "reports",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("report_tab")
        self._dir = Path(default_dir)
        self._provider = None  # callable() -> dict (снапшот всей сессии)
        self._report: dict | None = None

        self._text = QTextEdit()
        self._text.setReadOnly(True)

        self._generate_btn = QPushButton()
        self._generate_btn.clicked.connect(self._on_generate)
        self._txt_btn = QPushButton()
        self._txt_btn.clicked.connect(lambda: self._on_save("txt"))
        self._json_btn = QPushButton()
        self._json_btn.clicked.connect(lambda: self._on_save("json"))
        self._txt_btn.setEnabled(False)
        self._json_btn.setEnabled(False)

        self._status = QLabel()

        buttons = QHBoxLayout()
        buttons.addWidget(self._generate_btn)
        buttons.addWidget(self._txt_btn)
        buttons.addWidget(self._json_btn)
        buttons.addStretch(1)
        buttons.addWidget(self._status)

        layout = QVBoxLayout(self)
        layout.addLayout(buttons)
        layout.addWidget(self._text)

        self.retranslate()

    def set_provider(self, provider) -> None:
        """provider() -> dict (готовый отчёт, см. report.build_report)."""
        self._provider = provider

    # --- действия ---

    def _on_generate(self) -> None:
        if self._provider is None:
            self._text.setPlainText(tr("rep_empty"))
            return
        self._report = self._provider()
        self._text.setPlainText(report_mod.render_txt(self._report))
        self._txt_btn.setEnabled(True)
        self._json_btn.setEnabled(True)

    def _on_save(self, fmt: str) -> None:
        if self._report is None:
            return
        path = (
            report_mod.save_txt(self._report, self._dir)
            if fmt == "txt"
            else report_mod.save_json(self._report, self._dir)
        )
        self._status.setText(tr_fmt("rep_saved", path=str(path)))

    # --- данные ---

    def snapshot(self) -> dict:
        """Текущий отчёт (может быть None, если не сформирован)."""
        return dict(self._report) if self._report else {}

    # --- отображение ---

    def retranslate(self) -> None:
        self._generate_btn.setText(tr("rep_generate"))
        self._txt_btn.setText(tr("rep_save_txt"))
        self._json_btn.setText(tr("rep_save_json"))
        if self._text.toPlainText() == "":
            self._text.setPlaceholderText(tr("rep_empty"))
