"""Версия пакета синхронизирована с pyproject.toml."""

import tomllib
from pathlib import Path

import diagninten98

ROOT = Path(__file__).resolve().parents[2]


def test_version_matches_pyproject():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["version"] == diagninten98.__version__
