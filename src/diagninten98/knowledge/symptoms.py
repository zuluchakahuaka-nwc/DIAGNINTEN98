"""Дерево симптомов → вероятные причины (структура knowledge/symptoms.md).

L10N — кортеж (ru, en, zh). Чипы-кандидаты упорядочены по приоритету проверки
(от частого к редкому). Имена микросхем оставлены латиницей во всех языках.
"""

from __future__ import annotations

from dataclasses import dataclass

L10N = tuple[str, str, str]


@dataclass(frozen=True)
class Cause:
    id: str
    name: L10N


@dataclass(frozen=True)
class Symptom:
    id: str
    name: L10N
    causes: tuple[Cause, ...]


@dataclass(frozen=True)
class SymptomGroup:
    id: str
    name: L10N
    symptoms: tuple[Symptom, ...]


# --- причины (переиспользуются между симптомами) ---

C = {
    "usb_port_mech": Cause(
        "usb_port_mech",
        ("USB-C порт: механика/окисление", "USB-C port: mechanical wear/oxidation", "USB-C 接口：机械磨损/氧化"),
    ),
    "m92t36": Cause(
        "m92t36",
        ("M92T36 (PD-контроллер) — частый виновник", "M92T36 (PD controller) — frequent culprit", "M92T36（PD 控制器）——常见故障点"),
    ),
    "bq24193": Cause(
        "bq24193",
        ("BQ24193 (зарядный IC)", "BQ24193 (charging IC)", "BQ24193（充电芯片）"),
    ),
    "battery_deep": Cause(
        "battery_deep",
        ("Батарея: глубокий разряд / BMS", "Battery: deep discharge / BMS", "电池：深度放电 / BMS"),
    ),
    "pmic": Cause(
        "pmic",
        ("PMIC MAX77620 / цепи питания SoC", "PMIC MAX77620 / SoC power rails", "电源管理 MAX77620 / SoC 供电电路"),
    ),
    "display_cable": Cause(
        "display_cable",
        ("Шлейф дисплея / разъём", "Display ribbon cable / connector", "屏幕排线 / 连接器"),
    ),
    "panel_backlight": Cause(
        "panel_backlight",
        ("Панель: подсветка", "Panel: backlight", "屏幕：背光"),
    ),
    "board_damage": Cause(
        "board_damage",
        ("Плата: последствия падения/жидкости", "Board: drop/liquid damage", "主板：摔落/进水损伤"),
    ),
    "panel_matrix": Cause(
        "panel_matrix",
        ("Панель: матрица", "Panel: matrix", "屏幕：液晶层"),
    ),
    "cable_partial": Cause(
        "cable_partial",
        ("Шлейф: частичный контакт", "Ribbon: partial contact", "排线：接触不良"),
    ),
    "soc_gpu": Cause(
        "soc_gpu",
        ("SoC/GPU (редко)", "SoC/GPU (rare)", "SoC/GPU（少见）"),
    ),
    "battery_worn": Cause(
        "battery_worn",
        (
            "Батарея: износ (проверить фазой 2: MAX17050)",
            "Battery: wear (check in phase 2: MAX17050)",
            "电池：老化（阶段 2 检查：MAX17050）",
        ),
    ),
    "fuel_gauge_cal": Cause(
        "fuel_gauge_cal",
        ("Калибровка fuel gauge (MAX17050)", "Fuel gauge calibration (MAX17050)", "电量计校准（MAX17050）"),
    ),
    "emmc": Cause(
        "emmc",
        ("eMMC: деградация (фаза 2: eMMC health)", "eMMC: degradation (phase 2: eMMC health)", "eMMC：老化（阶段 2：eMMC 健康度）"),
    ),
    "firmware": Cause(
        "firmware",
        ("Прошивка: неудачное обновление", "Firmware: failed update", "固件：升级失败"),
    ),
    "boot01": Cause(
        "boot01",
        ("boot0/boot1 повреждены", "boot0/boot1 corrupted", "boot0/boot1 损坏"),
    ),
    "emmc_dead": Cause(
        "emmc_dead",
        ("eMMC: отсутствует/мёртв", "eMMC: missing/dead", "eMMC：缺失/损坏"),
    ),
    "rail": Cause(
        "rail",
        ("Рейка Joy-Con / контроллер рейки", "Joy-Con rail / rail controller", "Joy-Con 滑轨 / 滑轨控制芯片"),
    ),
    "rail_cable": Cause(
        "rail_cable",
        ("Шлейф рейки", "Rail ribbon", "滑轨排线"),
    ),
    "wifi_module": Cause(
        "wifi_module",
        ("Модуль Wi-Fi/BT (модель — уточнить)", "Wi-Fi/BT module (model TBD)", "Wi-Fi/蓝牙模块（型号待核实）"),
    ),
    "antenna": Cause(
        "antenna",
        ("Антенный кабель", "Antenna cable", "天线线缆"),
    ),
    "joycon_pots": Cause(
        "joycon_pots",
        (
            "Сам Joy-Con: потенциометры стика (консоль не при чём)",
            "Joy-Con itself: stick potentiometers (console is fine)",
            "Joy-Con 本体：摇杆电位器（与主机无关）",
        ),
    ),
    "thermal_paste": Cause(
        "thermal_paste",
        ("Термопаста/термопрокладки", "Thermal paste/pads", "导热硅脂/导热垫"),
    ),
    "fan": Cause(
        "fan",
        ("Вентилятор: пыль, подшипник", "Fan: dust, bearing", "风扇：积尘、轴承"),
    ),
    "radiator": Cause(
        "radiator",
        ("Радиатор: пыль", "Heatsink: dust", "散热器：积尘"),
    ),
}


def _c(*ids: str) -> tuple[Cause, ...]:
    return tuple(C[i] for i in ids)


GROUPS: tuple[SymptomGroup, ...] = (
    SymptomGroup(
        "power",
        ("Питание и включение", "Power & startup", "电源与开机"),
        (
            Symptom(
                "dead",
                (
                    "Совсем не включается (нет реакции, LED не горит)",
                    "Completely dead (no response, no LED)",
                    "完全无法开机（无反应、无指示灯）",
                ),
                _c("usb_port_mech", "m92t36", "bq24193", "battery_deep", "pmic"),
            ),
            Symptom(
                "black_no_backlight",
                (
                    "Чёрный экран, подсветки нет",
                    "Black screen, no backlight",
                    "黑屏且无背光",
                ),
                _c("display_cable", "panel_backlight", "board_damage"),
            ),
            Symptom(
                "backlight_no_image",
                (
                    "Подсветка есть, изображения нет",
                    "Backlight on, no image",
                    "有背光无画面",
                ),
                _c("panel_matrix", "cable_partial", "soc_gpu"),
            ),
        ),
    ),
    SymptomGroup(
        "charge",
        ("Заряд", "Charging", "充电"),
        (
            Symptom(
                "no_charge",
                (
                    "Не заряжается, но работает",
                    "Won't charge, but works",
                    "不充电但能开机运行",
                ),
                _c("usb_port_mech", "m92t36", "bq24193"),
            ),
            Symptom(
                "cable_position",
                (
                    "Заряжается только при положении кабеля",
                    "Charges only at a cable angle",
                    "仅特定线缆角度充电",
                ),
                _c("usb_port_mech"),
            ),
            Symptom(
                "fast_drain",
                ("Быстро разряжается", "Drains fast", "掉电快"),
                _c("battery_worn", "fuel_gauge_cal"),
            ),
        ),
    ),
    SymptomGroup(
        "boot",
        ("Загрузка", "Boot", "启动"),
        (
            Symptom(
                "logo_loop",
                (
                    "Не грузится дальше логотипа / циклическая перезагрузка",
                    "Stuck at logo / boot loop",
                    "卡 logo / 循环重启",
                ),
                _c("emmc", "firmware", "boot01"),
            ),
            Symptom(
                "rcm_only",
                (
                    "RCM виден (APX), система не грузится",
                    "RCM visible (APX), system won't boot",
                    "可见 RCM（APX），系统不启动",
                ),
                _c("emmc_dead", "firmware"),
            ),
        ),
    ),
    SymptomGroup(
        "peripheral",
        ("Периферия", "Peripherals", "外设"),
        (
            Symptom(
                "joycon_one_side",
                (
                    "Не видит Joy-Con (одна сторона)",
                    "One Joy-Con side not detected",
                    "单侧 Joy-Con 无法识别",
                ),
                _c("rail", "rail_cable"),
            ),
            Symptom(
                "no_wifi",
                ("Нет Wi-Fi/Bluetooth", "No Wi-Fi/Bluetooth", "无 Wi-Fi/蓝牙"),
                _c("wifi_module", "antenna"),
            ),
            Symptom(
                "drift",
                ("Дрейф стиков", "Stick drift", "摇杆漂移"),
                _c("joycon_pots"),
            ),
        ),
    ),
    SymptomGroup(
        "thermal",
        ("Температура", "Temperature", "温度"),
        (
            Symptom(
                "overheat",
                (
                    "Перегрев / троттлинг / шум вентилятора",
                    "Overheating / throttling / loud fan",
                    "过热 / 降频 / 风扇噪音大",
                ),
                _c("thermal_paste", "fan", "radiator"),
            ),
        ),
    ),
)


def find_group(group_id: str) -> SymptomGroup | None:
    return next((g for g in GROUPS if g.id == group_id), None)


def find_symptom(group_id: str, symptom_id: str) -> Symptom | None:
    group = find_group(group_id)
    if group is None:
        return None
    return next((s for s in group.symptoms if s.id == symptom_id), None)
