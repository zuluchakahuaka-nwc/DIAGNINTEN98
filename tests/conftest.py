"""Общие настройки тестов.

- QT_QPA_PLATFORM=offscreen выставляется ДО любого импорта Qt:
  GUI-тесты и снятие скриншотов работают без дисплея.
- QT_QPA_FONTDIR: offscreen-Qt не видит системных шрифтов (Qt больше не
  поставляет собственные) — без этого кириллица и CJK рендерятся квадратами.
- CJK-шрифты (.ttc) регистрируются дополнительно после создания QApplication —
  см. diagninten98.fonts и fixture _offscreen_fonts ниже.
"""

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

if sys.platform == "win32" and os.path.isdir(r"C:\Windows\Fonts"):
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")

import pytest  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _offscreen_fonts(qapp):
    """Регистрирует CJK-шрифты Windows в offscreen-режиме (один раз за прогон)."""
    from diagninten98.fonts import register_offscreen_fonts

    register_offscreen_fonts()
