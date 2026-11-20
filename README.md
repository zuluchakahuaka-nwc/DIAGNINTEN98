# DIAGNINTEN98

**EN:** Read-only hardware diagnostics for the Nintendo Switch (2017, HAC-001 "erista"/"mariko") on Windows.
**RU:** Диагностическая программа для Nintendo Switch 1 (HAC-001) под Windows. Только чтение состояния и анализ поломок — **ничего не записывается на консоль**.

## Возможности (по фазам)

| Фаза | Что входит | Статус |
|---|---|---|
| 0 | Каркас проекта, git, зависимости | ✅ |
| 1 | USB-монитор (cfgmgr32: детект APX/RCM `0955:7321`, MTP `057E:2010` — без драйвера), чтение Device ID по RCM (16 байт, EP 0x81), ревизия по серийнику, мастер поломок, отчёт TXT/JSON | ✅ |
| 2 | Авто-установка WinUSB-драйвера + запуск read-only payload (hekate): eMMC health, батарея, фьюзы | ⬜ |
| 3 | База кодов ошибок (2162-xxxx и т.п.), история по серийникам | ⬜ |

## Структура

```
DIAGNINTEN98/
├── src/diagninten98/     # код (PySide6 GUI + USB-слой)
├── knowledge/            # база знаний: симптомы→причины, коды ошибок
├── payloads/             # payload'ы (появятся в фазе 2)
├── docs/                 # план, факты к проверке
└── pyproject.toml
```

## Тесты

```
uv run pytest                  # компонентные + GUI + e2e со скриншотами
uv run pytest -m "not e2e"     # без скриншотов
```

Политика тестирования, золотые скриншоты и проверка UI зрением — см. [docs/TESTING.md](docs/TESTING.md).

## Запуск

```
uv sync
uv run diagninten98
```

Требуется Python 3.11+ (управляется через `uv`).

## Драйвер APX (RCM)

Для работы с консолью в режиме RCM устройству `APX` (VID `0955`, PID `7321`) нужен драйвер WinUSB.
В фазе 1 — вручную через [Zadig](https://zadig.akeo.ie/), в фазе 2 — автоматически из программы.

## Принцип «read-only»

- На консоль ничего не пишется: ни eMMC, ни фьюзы, ни калибровка.
- Payload фазы 2 (hekate) выполняется только в RAM и не модифицирует накопитель.
- Все действия, выходящие за рамки чтения, сопровождаются явным предупреждением.

## Ссылки (референсы для реализации)

- fusee-launcher (протокол RCM по USB): https://github.com/Qyriad/fusee-launcher
- TegraRcmGUI (пример GUI + авто-драйвер): https://github.com/eliboa/TegraRcmGUI
- hekate (payload, источник данных): https://github.com/CTCaer/hekate
- SwitchBrew (документация по железу/протоколам): https://switchbrew.org
