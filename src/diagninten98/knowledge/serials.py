"""Определение региона/поколения Switch по серийному номеру (черновик).

Формат: буква X + буква поколения + буква региона + цифры (пример: XAW10001234567).
Поколение: 'A' — эра erista (T210), 'K' — эра mariko (T214: v2/Lite/OLED).
Таблица префиксов — ЧЕРНОВИК: регион Европы и mariko-префиксы требуют сверки
с публичными базами (см. docs/FACTS_TO_VERIFY, №9). Точный вердикт
patched/unpatched — фаза 2 (таблицы диапазонов + поведение RCM).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_SERIAL_RE = re.compile(r"^X([A-Z])([A-Z])(\d{8,13})$")

# 3-буквенный префикс → ключ локализации региона.
_REGION_PREFIXES: dict[str, str] = {
    "XAW": "serial_region_us",  # erista, Америка
    "XAJ": "serial_region_jp",  # erista, Япония
    "XEW": "serial_region_eu",  # erista, Европа — префикс под вопросом
    "XKW": "serial_region_us",  # mariko, Америка — под вопросом
    "XKJ": "serial_region_jp",  # mariko, Япония — под вопросом
}

# Вторая буква → поколение.
_GENERATION_LETTERS: dict[str, str] = {
    "A": "serial_gen_erista",
    "K": "serial_gen_mariko",
}


@dataclass(frozen=True)
class SerialInfo:
    serial: str
    ok: bool
    region_key: str = "serial_region_unknown"
    generation_key: str = "serial_gen_unknown"

    def describe(self) -> str:
        """Локализованное описание (использует текущий язык)."""
        from ..strings import tr

        if not self.ok:
            return tr("serial_bad_format")
        return f"{tr(self.region_key)}, {tr(self.generation_key)}"


def check(serial: str) -> SerialInfo:
    """Разобрать серийник: регион + поколение. ok=False при плохом формате."""
    cleaned = serial.strip().upper()
    match = _SERIAL_RE.match(cleaned)
    if match is None:
        return SerialInfo(serial=cleaned, ok=False)
    prefix = cleaned[:3]
    region = _REGION_PREFIXES.get(prefix, "serial_region_unknown")
    generation = _GENERATION_LETTERS.get(match.group(1), "serial_gen_unknown")
    return SerialInfo(
        serial=cleaned, ok=True, region_key=region, generation_key=generation
    )
