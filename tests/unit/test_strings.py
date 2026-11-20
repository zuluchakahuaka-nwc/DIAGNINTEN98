"""Компонентные тесты словаря локализации (ru/en/zh) и tr()."""

from diagninten98 import strings
from diagninten98.strings import LANGS

# Ключи, где переводы закономерно совпадают во всех языках
# (аббревиатуры и технические обозначения).
SAME_IN_ALL = {
    "rcm_tab",
    "mon_vidpid",
    "mon_kind_rcm",
    "mon_kind_other",
    "rep_sec_rcm",
    "chip_picofly",
    "chip_hwfly",
    "model_standard_v1",
    "model_standard_v2",
    "model_lite",
    "model_oled",
}


def test_strings_cover_all_languages():
    """Каждый ключ — кортеж непустых строк по числу языков."""
    for key, value in strings.STRINGS.items():
        assert isinstance(value, tuple), key
        assert len(value) == len(LANGS), key
        for text in value:
            assert isinstance(text, str) and text.strip(), key


def test_strings_differ_across_languages():
    """Не-аббревиатуры должны различаться между языками."""
    for key, value in strings.STRINGS.items():
        if key in SAME_IN_ALL:
            continue
        assert len(set(value)) > 1, f"все переводы совпадают для {key}"


def test_tr_for_each_language(monkeypatch):
    for i, lang in enumerate(LANGS):
        monkeypatch.setattr(strings, "LANG", lang)
        for key in strings.STRINGS:
            assert strings.tr(key) == strings.STRINGS[key][i]


def test_set_language_and_reject_unknown():
    strings.set_language("zh")
    try:
        assert strings.LANG == "zh"
    finally:
        strings.set_language("ru")
    try:
        strings.set_language("xx")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown language must raise ValueError")


def test_tr_fmt_substitution(monkeypatch):
    monkeypatch.setattr(strings, "LANG", "ru")
    assert "boom" in strings.tr_fmt("mon_enum_error", err="boom")
