"""E2E: скриншоты всех вкладок на всех языках (ru/en/zh) → artifacts/screenshots/.

Дальше актуальные скриншоты сравниваются с золотыми (tests/golden/)
зрением через MCP zai-vision — протокол описан в AGENTS.md.
"""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QComboBox

from diagninten98.app import LANGS, MainWindow, TABS
from diagninten98.capture import capture_tabs

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts" / "screenshots"


@pytest.mark.e2e
def test_capture_all_tabs_all_languages(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)
    win.resize(960, 640)
    win.show()
    combo = win.findChild(QComboBox)
    assert combo is not None

    for idx, lang in enumerate(LANGS):
        combo.setCurrentIndex(idx)
        paths = capture_tabs(win, ARTIFACTS, suffix=f"_{lang}")
        assert len(paths) == len(TABS), f"язык {lang}: снято не всё"
        for p in paths:
            assert p.exists(), f"скриншот не сохранён: {p}"
            assert p.stat().st_size > 0, f"пустой скриншот: {p}"
