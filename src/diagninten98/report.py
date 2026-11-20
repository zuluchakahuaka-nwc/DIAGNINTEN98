"""Модель диагностического отчёта + экспорт TXT/JSON."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from . import __version__
from . import strings
from .strings import tr
from .usb.ids import format_vidpid

# snapshot() вкладок приходит как dict:
#   usb:    {"devices": [{"vid": int, "pid": int, "name": str, "kind": "rcm"|"mtp"|"other"}],
#            "status": "rcm"|"mtp"|"none"|"error"}
#   rcm:    {"device_id": hex|None, "read_error": str|None,
#            "serial": str, "serial_result": str}
#   faults: {"group_id", "group", "symptom_id", "symptom", "causes": [str]}


def build_report(lang: str, usb: dict, rcm: dict, faults: dict) -> dict:
    """Собрать отчёт из снапшотов вкладок (чистые данные, без локализации)."""
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "tool": {"name": "DIAGNINTEN98", "version": __version__},
        "language": lang,
        "usb": usb,
        "rcm": rcm,
        "faults": faults,
    }


def render_txt(report: dict) -> str:
    """Человекочитаемый TXT в языке, на котором отчёт сформирован."""
    lang = report.get("language", "ru")
    old = strings.LANG
    try:
        strings.set_language(lang)
        lines: list[str] = [
            f"{tr('rep_title')} — DIAGNINTEN98 v{report['tool']['version']}",
            f"{report['generated_at']}",
            "",
            f"== {tr('rep_sec_usb')} ==",
        ]
        devices = report["usb"].get("devices", [])
        if devices:
            for d in devices:
                lines.append(
                    f"  {format_vidpid(d['vid'], d['pid'])}  "
                    f"[{d['kind'].upper()}]  {d['name'] or '-'}"
                )
        else:
            lines.append(f"  {tr('mon_none')}")

        lines += ["", f"== {tr('rep_sec_rcm')} =="]
        dev_id = report["rcm"].get("device_id")
        if dev_id:
            lines.append(f"  Device ID: {dev_id}")
            lines.append(f"  {tr('rcm_read_ok')}")
        else:
            lines.append(f"  {tr('rep_none')}")
        serial = report["rcm"].get("serial")
        if serial:
            result = report["rcm"].get("serial_result")
            lines.append(f"  SN: {serial} — {result or tr('rep_none')}")
        payload_status = report["rcm"].get("payload_status")
        if payload_status:
            lines.append(f"  Payload: {payload_status}")

        lines += ["", f"== {tr('rep_sec_faults')} =="]
        symptom = report["faults"].get("symptom")
        if symptom:
            lines.append(f"  {report['faults'].get('group', '')} / {symptom}:")
            for i, cause in enumerate(report["faults"].get("causes", []), 1):
                lines.append(f"    {i}. {cause}")
        else:
            lines.append(f"  {tr('rep_none')}")
        lines.append("")
    finally:
        strings.set_language(old)
    return "\n".join(lines)


def _save(report: dict, directory: Path, suffix: str, content: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    stamp = report["generated_at"].replace(":", "").replace("-", "")
    path = directory / f"diagninten98_{stamp}{suffix}"
    path.write_text(content, encoding="utf-8")
    return path


def save_txt(report: dict, directory: Path | str = "reports") -> Path:
    return _save(report, Path(directory), ".txt", render_txt(report))


def save_json(report: dict, directory: Path | str = "reports") -> Path:
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    return _save(report, Path(directory), ".json", payload)
