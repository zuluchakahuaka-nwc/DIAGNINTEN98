"""Вкладка «Поломки»: дерево симптом → вероятные причины."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from .. import strings
from ..knowledge.symptoms import GROUPS
from ..strings import LANGS, tr


def _l(names: tuple[str, str, str]) -> str:
    return names[LANGS.index(strings.LANG)]


class FaultsTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("faults_tab")

        self._groups_list = QListWidget()
        self._symptoms_list = QListWidget()
        self._causes_list = QListWidget()

        self._groups_caption = QLabel()
        self._symptoms_caption = QLabel()
        self._causes_caption = QLabel()
        self._hint_label = QLabel()
        self._hint_label.setStyleSheet("color: gray;")

        self._groups_list.currentRowChanged.connect(self._on_group)
        self._symptoms_list.currentRowChanged.connect(self._on_symptom)

        from PySide6.QtWidgets import QHBoxLayout

        columns = QHBoxLayout()
        for caption, widget in (
            (self._groups_caption, self._groups_list),
            (self._symptoms_caption, self._symptoms_list),
            (self._causes_caption, self._causes_list),
        ):
            column = QVBoxLayout()
            column.addWidget(caption)
            column.addWidget(widget)
            columns.addLayout(column)

        layout = QVBoxLayout(self)
        layout.addLayout(columns)
        layout.addWidget(self._hint_label)

        self._fill_groups()
        self.retranslate()

    # --- заполнение ---

    def _fill_groups(self) -> None:
        selected_group = self.selected_group_id()
        selected_symptom = self.selected_symptom_id()
        self._groups_list.blockSignals(True)
        self._groups_list.clear()
        for group in GROUPS:
            item = QListWidgetItem(_l(group.name))
            item.setData(0x0100, group.id)  # Qt.UserRole
            self._groups_list.addItem(item)
        self._groups_list.blockSignals(False)
        self._restore_selection(selected_group, selected_symptom)
        if self._groups_list.count() and self._groups_list.currentRow() < 0:
            self._groups_list.setCurrentRow(0)

    def _restore_selection(self, group_id: str | None, symptom_id: str | None) -> None:
        for row in range(self._groups_list.count()):
            if self._groups_list.item(row).data(0x0100) == group_id:
                self._groups_list.setCurrentRow(row)
                self._fill_symptoms(symptom_id)
                return

    def _fill_symptoms(self, select_id: str | None = None) -> None:
        group = GROUPS[self._groups_list.currentRow()] if self._groups_list.currentRow() >= 0 else None
        self._symptoms_list.blockSignals(True)
        self._symptoms_list.clear()
        if group is not None:
            for symptom in group.symptoms:
                item = QListWidgetItem(_l(symptom.name))
                item.setData(0x0100, symptom.id)
                self._symptoms_list.addItem(item)
        self._symptoms_list.blockSignals(False)
        if select_id:
            for row in range(self._symptoms_list.count()):
                if self._symptoms_list.item(row).data(0x0100) == select_id:
                    self._symptoms_list.setCurrentRow(row)
                    return
        if self._symptoms_list.count():
            self._symptoms_list.setCurrentRow(0)
        else:
            self._causes_list.clear()

    # --- события ---

    def _on_group(self, row: int) -> None:
        self._fill_symptoms()

    def _on_symptom(self, row: int) -> None:
        symptom = self._current_symptom()
        self._causes_list.clear()
        if symptom is not None:
            for i, cause in enumerate(symptom.causes, 1):
                self._causes_list.addItem(f"{i}. {_l(cause.name)}")

    def _current_symptom(self):
        group = GROUPS[self._groups_list.currentRow()] if self._groups_list.currentRow() >= 0 else None
        if group is None:
            return None
        row = self._symptoms_list.currentRow()
        if row < 0 or row >= len(group.symptoms):
            return None
        return group.symptoms[row]

    # --- данные ---

    def selected_group_id(self) -> str | None:
        row = self._groups_list.currentRow()
        if row < 0 or row >= len(GROUPS):
            return None
        return GROUPS[row].id

    def selected_symptom_id(self) -> str | None:
        item = self._symptoms_list.currentItem()
        return item.data(0x0100) if item else None

    def snapshot(self) -> dict:
        group = GROUPS[self._groups_list.currentRow()] if self._groups_list.currentRow() >= 0 else None
        symptom = self._current_symptom()
        return {
            "group_id": group.id if group else None,
            "group": _l(group.name) if group else None,
            "symptom_id": symptom.id if symptom else None,
            "symptom": _l(symptom.name) if symptom else None,
            "causes": [_l(c.name) for c in symptom.causes] if symptom else [],
        }

    # --- отображение ---

    def retranslate(self) -> None:
        self._groups_caption.setText(tr("faults_groups"))
        self._symptoms_caption.setText(tr("faults_symptoms"))
        self._causes_caption.setText(tr("faults_causes"))
        self._hint_label.setText(tr("faults_hint"))
        self._fill_groups()  # перезаливка с текущим языком (сохраняет выбор)
        self._on_symptom(self._symptoms_list.currentRow())
