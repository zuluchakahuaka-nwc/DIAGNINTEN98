"""Захват скриншотов вкладок главного окна.

Используется e2e-тестами (актуальные скриншоты, artifacts/screenshots/)
и tools/golden.py (золотые скриншоты, tests/golden/).
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget


def _safe_name(text: str) -> str:
    """Только ASCII-буквы/цифры/-/_: имена скриншотов должны быть переносимы."""
    return "".join(
        c if (c.isascii() and (c.isalnum() or c in "-_")) else "_" for c in text
    ).strip("_")


def capture_tabs(
    window: QMainWindow,
    out_dir: str | Path,
    prefix: str = "tab",
    suffix: str = "",
) -> list[Path]:
    """Перебирает вкладки окна и сохраняет скриншот каждой в out_dir.

    Имя файла: `tab_<индекс>_<objectName><suffix>.png` (только ASCII).
    `suffix` используется, чтобы различать снимки по языку (`_ru`, `_en`, `_zh`).
    Возвращает список путей к PNG в порядке вкладок.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    tabs = window.findChild(QTabWidget)
    if tabs is None:
        raise ValueError("QTabWidget не найден в окне")

    paths: list[Path] = []
    for i in range(tabs.count()):
        tabs.setCurrentIndex(i)
        QApplication.processEvents()
        widget = tabs.widget(i)
        name = _safe_name(widget.objectName()) if widget is not None else ""
        if not name:
            name = _safe_name(tabs.tabText(i)) or str(i)
        path = out / f"{prefix}_{i:02d}_{name}{suffix}.png"
        if not window.grab().save(str(path)):
            raise RuntimeError(f"не удалось сохранить скриншот: {path}")
        paths.append(path)
    return paths
