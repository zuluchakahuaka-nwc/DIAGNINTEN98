"""Регистрация шрифтов для offscreen-рендера (тесты, скриншоты).

Offscreen-платформа Qt использует FreeType и не знает о системной подстановке
шрифтов Windows. Каталог QT_QPA_FONTDIR=C:\\Windows\\Fonts даёт кириллицу
(arial.ttf и т.п.), но CJK-шрифты лежат в .ttc-коллекциях (msyh.ttc и др.),
которые offscreen сам не подхватывает, — китайский рендерится квадратами.
Решение: явно зарегистрировать их через QFontDatabase.addApplicationFont.
"""

from __future__ import annotations

import sys
from pathlib import Path

WIN_FONTS = Path(r"C:\Windows\Fonts")

# Кандидаты в порядке приоритета: Microsoft YaHei (覆盖 latin/cyrillic/CJK),
# затем типовые CJK-шрифты Windows с языковыми пакетами.
CJK_CANDIDATES: tuple[str, ...] = (
    "msyh.ttc",      # Microsoft YaHei (упрощённый китайский)
    "msyhl.ttc",     # Microsoft YaHei Light
    "simhei.ttf",    # SimHei
    "simsun.ttc",    # SimSun
    "msjh.ttc",      # Microsoft JhengHei (традиционный китайский)
    "malgun.ttf",    # Malgun Gothic (корейский) — на будущее
)


def register_offscreen_fonts() -> list[str]:
    """Зарегистрировать CJK-шрифты Windows. Вызывать после создания QApplication.

    Возвращает список имён зарегистрированных файлов (для диагностики).
    """
    registered: list[str] = []
    if sys.platform != "win32" or not WIN_FONTS.is_dir():
        return registered

    from PySide6.QtGui import QFontDatabase

    for name in CJK_CANDIDATES:
        path = WIN_FONTS / name
        if path.is_file():
            QFontDatabase.addApplicationFont(str(path))
            registered.append(name)
    return registered
