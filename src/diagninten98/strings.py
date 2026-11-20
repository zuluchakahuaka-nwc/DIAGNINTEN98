"""Единая локализация интерфейса: RU / EN / ZH.

LANG — текущий язык (модульная глобальная), переключается через set_language().
Порядок элементов в STRINGS: (ru, en, zh).
"""

from __future__ import annotations

LANGS: tuple[str, ...] = ("ru", "en", "zh")
LANG_NAMES: dict[str, str] = {"ru": "Русский", "en": "English", "zh": "中文"}

LANG = "ru"

STRINGS: dict[str, tuple[str, str, str]] = {
    # (ru, en, zh)
    # --- оболочка ---
    "usb_tab": ("USB / Монитор", "USB / Monitor", "USB / 监控"),
    "rcm_tab": ("RCM", "RCM", "RCM"),
    "faults_tab": ("Поломки", "Faults", "故障"),
    "codes_tab": ("Коды ошибок", "Error codes", "错误代码"),
    "report_tab": ("Отчёт", "Report", "报告"),
    "phase3_stub": ("Реализация — фаза 3", "Implementation — phase 3", "实现 — 阶段 3"),
    "language": ("Язык", "Language", "语言"),
    # --- USB-монитор ---
    "mon_status": ("Статус", "Status", "状态"),
    "mon_device": ("Устройство", "Device", "设备"),
    "mon_vidpid": ("VID:PID", "VID:PID", "VID:PID"),
    "mon_kind": ("Режим", "Mode", "模式"),
    "mon_kind_rcm": ("RCM (APX)", "RCM (APX)", "RCM (APX)"),
    "mon_kind_mtp": ("MTP (система)", "MTP (system)", "MTP（系统）"),
    "mon_kind_other": ("—", "—", "—"),
    "mon_none": (
        "Консоль не обнаружена. Подключите Switch по USB (любой режим) или введите "
        "его в RCM (jig + Vol+ + Power, держать до появления логотипа).",
        "No console detected. Connect the Switch via USB (any mode) or enter RCM "
        "(jig + Vol+ + Power, hold until the logo).",
        "未检测到主机。请用 USB 连接 Switch（任意模式），或进入 RCM"
        "（纸片 + 音量+ + 电源，按住至出现 logo）。",
    ),
    "mon_rcm": (
        "Обнаружена консоль в RCM (APX): SoC жив, boot ROM работает, USB-линии в "
        "порядке. Поломка вероятнее в eMMC/прошивке, чем в питании.",
        "Console detected in RCM (APX): SoC alive, boot ROM running, USB lines OK. "
        "Failure more likely in eMMC/firmware than in power.",
        "检测到 RCM（APX）模式的主机：SoC 正常、boot ROM 运行中、USB 线路正常。"
        "故障更可能在 eMMC/固件，而非供电。",
    ),
    "mon_mtp": (
        "Консоль полностью загружается (MTP-режим): система работает, «мёртвой» её "
        "считать нельзя.",
        "Console fully boots (MTP mode): the system runs — it is not 'dead'.",
        "主机可完整开机（MTP 模式）：系统正常运行，不算“死亡”主机。",
    ),
    "mon_enum_error": (
        "Ошибка перечисления USB-устройств: {err}",
        "USB enumeration error: {err}",
        "USB 设备枚举出错：{err}",
    ),
    "mon_refresh": ("Обновить", "Refresh", "刷新"),
    "mon_hint": (
        "Автообновление каждые 2 с",
        "Auto-refresh every 2 s",
        "每 2 秒自动刷新",
    ),
    # --- RCM-вкладка ---
    "rcm_read_btn": ("Прочитать Device ID", "Read Device ID", "读取 Device ID"),
    "rcm_id_title": ("Device ID (16 байт)", "Device ID (16 bytes)", "Device ID（16 字节）"),
    "rcm_read_ok": (
        "Прочитано — связь с boot ROM работает. Только чтение, на консоль ничего "
        "не записано.",
        "Read OK — boot ROM communication works. Read-only, nothing was written.",
        "读取成功——与 boot ROM 通信正常。只读操作，未向主机写入任何数据。",
    ),
    "rcm_read_fail": (
        "Не удалось прочитать: консоль не в RCM, либо для APX не установлен "
        "драйвер WinUSB (см. README — Zadig).",
        "Read failed: console not in RCM, or WinUSB driver not installed for APX "
        "(see README — Zadig).",
        "读取失败：主机不在 RCM 模式，或 APX 未安装 WinUSB 驱动（见 README — Zadig）。",
    ),
    "rcm_serial_title": (
        "Серийный номер (с наклейки)",
        "Serial number (from sticker)",
        "序列号（机身标签）",
    ),
    "rcm_serial_btn": ("Определить ревизию", "Check revision", "检查版本"),
    "rcm_serial_hint": (
        "Регион и поколение — по префиксу. Точная проверка patched/unpatched — фаза 2.",
        "Region and generation by prefix. Exact patched/unpatched check is phase 2.",
        "按前缀判断地区与世代。patched/unpatched 的精确检查在阶段 2。",
    ),
    # --- результаты проверки серийника ---
    "serial_region_us": ("регион: Америка", "region: Americas", "地区：美洲"),
    "serial_region_jp": ("регион: Япония", "region: Japan", "地区：日本"),
    "serial_region_eu": (
        "регион: Европа (префикс уточняется)",
        "region: Europe (prefix unverified)",
        "地区：欧洲（前缀待核实）",
    ),
    "serial_region_unknown": ("регион: неизвестен", "region: unknown", "地区：未知"),
    "serial_gen_erista": (
        "поколение: эра erista (T210, 2017–2019) — до патча уязвима к fusée gelée",
        "generation: erista era (T210, 2017–2019) — fusée gelée vulnerable before patch",
        "世代：erista（T210，2017–2019）——补丁前受 fusée gelée 影响",
    ),
    "serial_gen_mariko": (
        "поколение: эра mariko (T214: v2/Lite/OLED) — fusée gelée закрыта",
        "generation: mariko era (T214: v2/Lite/OLED) — fusée gelée patched",
        "世代：mariko（T214：v2/Lite/OLED）——fusée gelée 已修复",
    ),
    "serial_gen_unknown": (
        "поколение: неизвестно",
        "generation: unknown",
        "世代：未知",
    ),
    "serial_bad_format": (
        "Не похоже на серийный номер Switch (пример: XAW10001234567).",
        "Does not look like a Switch serial (example: XAW10001234567).",
        "不像 Switch 序列号（示例：XAW10001234567）。",
    ),
    # --- мастер поломок ---
    "faults_groups": ("Группа симптомов", "Symptom group", "症状分组"),
    "faults_symptoms": ("Симптом", "Symptom", "症状"),
    "faults_causes": (
        "Вероятные причины (по приоритету)",
        "Probable causes (by priority)",
        "可能原因（按优先级）",
    ),
    "faults_hint": (
        "Приоритет ≈ порядок проверки: от частого к редкому.",
        "Priority ≈ check order: most common first.",
        "优先级 ≈ 检查顺序：从常见到少见。",
    ),
    # --- отчёт ---
    "rep_title": ("Отчёт об обследовании", "Diagnostic report", "诊断报告"),
    "rep_generate": ("Сформировать", "Generate", "生成"),
    "rep_save_txt": ("Сохранить TXT", "Save TXT", "保存 TXT"),
    "rep_save_json": ("Сохранить JSON", "Save JSON", "保存 JSON"),
    "rep_saved": ("Сохранено: {path}", "Saved: {path}", "已保存：{path}"),
    "rep_empty": (
        "Данных пока нет — нажмите «Сформировать».",
        "No data yet — press 'Generate'.",
        "暂无数据——请点击“生成”。",
    ),
    "rep_sec_usb": ("USB-устройства", "USB devices", "USB 设备"),
    "rep_sec_rcm": ("RCM", "RCM", "RCM"),
    "rep_sec_faults": ("Анализ поломок", "Fault analysis", "故障分析"),
    "rep_none": ("не проводилось", "not performed", "未进行"),
}


def set_language(code: str) -> None:
    """Установить текущий язык (один из LANGS)."""
    global LANG
    if code not in LANGS:
        raise ValueError(f"unknown language: {code}")
    LANG = code


def tr(key: str) -> str:
    return STRINGS[key][LANGS.index(LANG)]


def tr_fmt(key: str, **kwargs) -> str:
    """Переведенная строка с подстановкой: tr + str.format."""
    return tr(key).format(**kwargs)
