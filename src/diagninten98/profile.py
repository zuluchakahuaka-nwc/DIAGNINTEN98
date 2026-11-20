"""Профиль консоли: вариант А/Б, тип модчипа, модель.

Профиль меняет диагностику, а не просто хранится:
- вариант Б → группа «Модчип» в мастере поломок поднимается в начало,
  а модчиповые причины продвигаются в топ каждого симптома;
- модель → поколение (Lite/V2/OLED = mariko всегда) и контекст ремонта
  (на Lite стики несъёмные — ремонт = пайка);
- интерпретация RCM в USB-мониторе предупреждает о принудительном RCM;
- профиль попадает в отчёт.
"""

from __future__ import annotations

from dataclasses import dataclass

VARIANT_STOCK = "stock"  # вариант А — обычная консоль
VARIANT_MODCHIP = "modchip"  # вариант Б — с глитч-модчипом

CHIP_TYPES: tuple[str, ...] = ("picofly", "hwfly", "other")
DEFAULT_CHIP = "other"

MODELS: tuple[str, ...] = (
    "unknown",
    "standard_v1",  # HAC-001 — erista
    "standard_v2",  # HAC-001(-01) — mariko
    "lite",  # HDH-001 — всегда mariko, стики несъёмные (пайка)
    "oled",  # HEG-001 — всегда mariko
)
_MARIKO_MODELS = frozenset({"standard_v2", "lite", "oled"})

_MODEL_KEYS: dict[str, str] = {
    "standard_v1": "model_standard_v1",
    "standard_v2": "model_standard_v2",
    "lite": "model_lite",
    "oled": "model_oled",
}


@dataclass(frozen=True)
class ConsoleProfile:
    variant: str = VARIANT_STOCK
    chip: str | None = None
    model: str = "unknown"

    @property
    def is_modchip(self) -> bool:
        return self.variant == VARIANT_MODCHIP

    @property
    def is_mariko(self) -> bool:
        """Lite/V2/OLED — всегда mariko (fusée gelée закрыта)."""
        return self.model in _MARIKO_MODELS

    @property
    def chip_or_default(self) -> str:
        return self.chip if self.chip in CHIP_TYPES else DEFAULT_CHIP

    def as_dict(self) -> dict:
        """Для snapshot/отчёта (чистые данные, без локализации)."""
        return {
            "variant": self.variant,
            "chip": self.chip if self.is_modchip else None,
            "model": self.model,
        }


def profile_from_dict(data: dict | None) -> ConsoleProfile:
    """Восстановить профиль из snapshot/QSettings (с защитой от мусора)."""
    if not isinstance(data, dict):
        return ConsoleProfile()
    variant = data.get("variant", VARIANT_STOCK)
    if variant not in (VARIANT_STOCK, VARIANT_MODCHIP):
        variant = VARIANT_STOCK
    chip = data.get("chip")
    model = data.get("model", "unknown")
    return ConsoleProfile(
        variant=variant,
        chip=chip if chip in CHIP_TYPES else None,
        model=model if model in MODELS else "unknown",
    )


def profile_label(profile: ConsoleProfile) -> str:
    """Локализованное «вариант + чип» для GUI/отчёта."""
    from .strings import tr

    if profile.is_modchip:
        chip_key = {
            "picofly": "chip_picofly",
            "hwfly": "chip_hwfly",
        }.get(profile.chip_or_default, "chip_other")
        return f"{tr('profile_variant_b')} — {tr(chip_key)}"
    return tr("profile_variant_a")


def model_label(profile: ConsoleProfile) -> str:
    """Локализованное название модели."""
    from .strings import tr

    return tr(_MODEL_KEYS.get(profile.model, "model_unknown"))
