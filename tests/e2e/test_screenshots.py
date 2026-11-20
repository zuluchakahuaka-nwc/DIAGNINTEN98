"""E2E: скриншоты всех вкладок на всех языках (ru/en/zh) → artifacts/screenshots/.

Дальше актуальные скриншоты сравниваются с золотыми (tests/golden/)
зрением через MCP zai-vision — протокол описан в AGENTS.md.
"""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QComboBox

from diagninten98.app import TAB_KEYS, MainWindow
from diagninten98.capture import capture_tabs
from diagninten98.demo import demo_enumerate
from diagninten98.strings import LANGS

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts" / "screenshots"


@pytest.mark.e2e
def test_capture_all_tabs_all_languages(qtbot):
    # Демо-набор (RCM + хаб + мышь): скриншоты детерминированы на любой машине.
    win = MainWindow(
        usb_enumerate_fn=demo_enumerate,
        usb_poll_ms=0,
        rcm_enumerate_fn=demo_enumerate,
        rcm_driver_poll_ms=0,
    )
    qtbot.addWidget(win)
    win.resize(960, 640)
    win.show()
    combo = win.findChild(QComboBox)
    assert combo is not None

    for idx, lang in enumerate(LANGS):
        combo.setCurrentIndex(idx)
        paths = capture_tabs(win, ARTIFACTS, suffix=f"_{lang}")
        assert len(paths) == len(TAB_KEYS), f"язык {lang}: снято не всё"
        for p in paths:
            assert p.exists(), f"скриншот не сохранён: {p}"
            assert p.stat().st_size > 0, f"пустой скриншот: {p}"
