"""Тесты профиля консоли (А/Б, чип, модель) и ранжирования базы знаний."""

from diagninten98 import strings
from diagninten98.knowledge.symptoms import (
    GROUPS,
    MODCHIP_GROUP_ID,
    find_symptom,
    ordered_causes,
    ordered_groups,
)
from diagninten98.profile import (
    VARIANT_MODCHIP,
    VARIANT_STOCK,
    ConsoleProfile,
    model_label,
    profile_from_dict,
    profile_label,
)

STOCK = ConsoleProfile()
MODCHIP = ConsoleProfile(variant=VARIANT_MODCHIP, chip="picofly", model="lite")


def test_stock_order_is_default():
    assert ordered_groups(STOCK) == GROUPS
    assert ordered_groups(STOCK)[0].id == "power"


def test_modchip_group_promoted_first():
    groups = ordered_groups(MODCHIP)
    assert groups[0].id == MODCHIP_GROUP_ID
    assert len(groups) == len(GROUPS)  # ничего не потеряли
    # остальные группы — в исходном порядке (power сразу за modchip)
    assert [g.id for g in groups[1:]] == [g.id for g in GROUPS if g.id != MODCHIP_GROUP_ID]


def test_modchip_causes_promoted():
    dead = find_symptom("power", "dead")
    mod_order = [c.id for c in ordered_causes(dead, MODCHIP)]
    stock_order = [c.id for c in ordered_causes(dead, STOCK)]
    # для Б модчиповые причины — в топ, относительный порядок сохранён
    assert mod_order[:2] == ["modchip_wires", "modchip_dat0"]
    # для А — в конце (низкий приоритет), состав тот же
    assert stock_order[-2:] == ["modchip_wires", "modchip_dat0"]
    assert set(mod_order) == set(stock_order)

    black = find_symptom("power", "black_no_backlight")
    assert ordered_causes(black, MODCHIP)[0].id == "modchip_no_sd"


def test_error_blink_first_cause_no_sd():
    """Нет SD — самая частая причина цикла ошибки чипа (жизненный кейс)."""
    blink = find_symptom("modchip", "error_blink")
    assert blink.causes[0].id == "modchip_no_sd"


def test_mariko_by_model():
    assert ConsoleProfile(model="lite").is_mariko
    assert ConsoleProfile(model="standard_v2").is_mariko
    assert ConsoleProfile(model="oled").is_mariko
    assert not ConsoleProfile(model="standard_v1").is_mariko
    assert not ConsoleProfile(model="unknown").is_mariko


def test_roundtrip_and_garbage():
    prof = ConsoleProfile(variant=VARIANT_MODCHIP, chip="picofly", model="lite")
    assert profile_from_dict(prof.as_dict()) == prof
    assert profile_from_dict(None) == ConsoleProfile()
    assert profile_from_dict({"variant": "junk", "chip": "junk", "model": "junk"}) == (
        ConsoleProfile()
    )
    # у варианта А чип не сохраняется
    stock = ConsoleProfile(variant=VARIANT_STOCK, chip="picofly")
    assert stock.as_dict()["chip"] is None


def test_labels_localized(monkeypatch):
    monkeypatch.setattr(strings, "LANG", "ru")
    assert "PicoFly" in profile_label(MODCHIP)
    assert "Б" in profile_label(MODCHIP)
    assert "А" in profile_label(STOCK)
    assert "Lite" in model_label(MODCHIP)
    monkeypatch.setattr(strings, "LANG", "zh")
    assert "Lite" in model_label(MODCHIP)  # модель содержит латиницу
    assert "B——" in profile_label(MODCHIP)
