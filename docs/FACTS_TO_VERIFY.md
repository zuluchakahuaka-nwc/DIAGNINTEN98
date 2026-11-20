# Факты к проверке при реализации

Веб-поиск в сессии недоступен (403), поэтому эти утверждения проверяются по первоисточникам
(GitHub: fusee-launcher / TegraRcmGUI / hekate; switchbrew.org) на фазе 1–2.

| # | Факт | Использование | Источник для проверки |
|---|---|---|---|
| 1 | ✅ RCM-режим: USB VID `0955` (NVIDIA), PID `7321` — подтверждено по исходнику fusee-launcher (Smeat/fusee-launcher, 2026-11-20): `DEFAULT_VID/PID` | детект консоли в RCM | проверено |
| 2 | ✅ Device ID читается bulk-read 16 байт с endpoint `0x81`, таймаут 1 c (НЕ контрольный трансфер) — подтверждено fusee-launcher: `read_device_id() -> self.read(16)` | вкладка RCM | проверено |
| 3 | Обычный режим: MTP VID `057E` (Nintendo), PID `2010` | USB-монитор: «система грузится» | switchbrew |
| 4 | Mariko (T214) в RCM даёт тот же PID, но fusée gelée закрыта | определение ревизии | fusee-launcher, switchbrew |
| 5 | Зарядный IC — TI BQ24193; fuel gauge — MAX17050 | база знаний «не заряжается» | switchbrew, схемы ремонта |
| 6 | PD-контроллер — M92T36 (частый виновник «не заряжается») | база знаний | ремонтные форумы |
| 7 | Чип Wi-Fi/BT (erista — Broadcom? mariko — ?) — уточнить марку | база знаний «нет Wi-Fi» | switchbrew, teardown |
| 8 | Что именно отдает hekate по eMMC health / батарее / фьюзам | парсер фазы 2 | исходники hekate (nyx) |
| 9 | Таблицы серийников «patched/unpatched» (XAW/GAW/...); префикс Европы и mariko-префиксы в knowledge/serials.py — черновик | определение ревизии | публичные базы (dgql и др.) |
| 10 | SetupDiGetClassDevs с энумератором «USB» на части сборок Windows даёт ERROR_INVALID_PARAMETER → используем cfgmgr32 CM_Get_Device_ID_ListW | перечисление USB | наблюдено на машине разработки |
