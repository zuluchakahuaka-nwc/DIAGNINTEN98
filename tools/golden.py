"""Перегенерация ЗОЛОТЫХ скриншотов (tests/golden/) для всех языков.

Запуск: uv run python tools/golden.py

Золото обновлять только осознанно после ожидаемых изменений GUI —
см. AGENTS.md, раздел «Проверка зрением».
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if sys.platform == "win32" and os.path.isdir(r"C:\Windows\Fonts"):
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")

ROOT = Path(__file__).resolve().parents[1]
GOLDEN_DIR = ROOT / "tests" / "golden"

from PySide6.QtWidgets import QApplication, QComboBox  # noqa: E402

from diagninten98.app import MainWindow  # noqa: E402
from diagninten98.capture import capture_tabs  # noqa: E402
from diagninten98.demo import demo_enumerate  # noqa: E402
from diagninten98.fonts import register_offscreen_fonts  # noqa: E402
from diagninten98.strings import LANGS  # noqa: E402


def main() -> int:
    app = QApplication(sys.argv)
    register_offscreen_fonts()  # CJK в offscreen без этого рендерится квадратами
    win = MainWindow(usb_enumerate_fn=demo_enumerate, usb_poll_ms=0)
    win.resize(960, 640)
    win.show()
    combo = win.findChild(QComboBox)
    assert combo is not None

    paths = []
    for idx, lang in enumerate(LANGS):
        combo.setCurrentIndex(idx)
        QApplication.processEvents()
        paths += capture_tabs(win, GOLDEN_DIR, suffix=f"_{lang}")

    print(f"Golden screenshots: {len(paths)} ({len(LANGS)} языков)")
    for p in paths:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
