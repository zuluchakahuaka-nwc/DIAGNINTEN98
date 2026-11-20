"""Компонентные тесты словаря локализации (ru/en/zh) и tr()."""

from diagninten98 import app
from diagninten98.app import LANGS

# Ключи, где переводы закономерно совпадают во всех языках (аббревиатуры).
SAME_IN_ALL = {"rcm_tab"}


def test_strings_cover_all_languages():
    """Каждый ключ — кортеж непустых строк по числу языков."""
    for key, value in app.STRINGS.items():
        assert isinstance(value, tuple), key
        assert len(value) == len(LANGS), key
        for text in value:
            assert isinstance(text, str) and text.strip(), key


def test_strings_differ_across_languages():
    """Не-аббревиатуры должны различаться между языками."""
    for key, value in app.STRINGS.items():
        if key in SAME_IN_ALL:
            continue
        assert len(set(value)) > 1, f"все переводы совпадают для {key}"


def test_tr_for_each_language(monkeypatch):
    for i, lang in enumerate(LANGS):
        monkeypatch.setattr(app, "LANG", lang)
        for key in app.STRINGS:
            assert app.tr(key) == app.STRINGS[key][i]
