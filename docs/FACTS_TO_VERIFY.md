# Факты к проверке при реализации

Веб-поиск в сессии недоступен (403), поэтому эти утверждения проверяются по первоисточникам
(GitHub: fusee-launcher / TegraRcmGUI / hekate; switchbrew.org) на фазе 1–2.

| # | Факт | Использование | Источник для проверки |
|---|---|---|---|
| 1 | RCM-режим: USB VID `0955` (NVIDIA), PID `7321` (Tegra X1/APX) | детект консоли в RCM | fusee-launcher, TegraRcmGUI |
| 2 | Device ID в RCM читается контрольным трансфером, 32 байта | вкладка RCM | fusee-launcher: `read_device_id` |
| 3 | Обычный режим: MTP VID `057E` (Nintendo), PID `2010` | USB-монитор: «система грузится» | switchbrew |
| 4 | Mariko (T214) в RCM даёт тот же PID, но fusée gelée закрыта | определение ревизии | fusee-launcher, switchbrew |
| 5 | Зарядный IC — TI BQ24193; fuel gauge — MAX17050 | база знаний «не заряжается» | switchbrew, схемы ремонта |
| 6 | PD-контроллер — M92T36 (частый виновник «не заряжается») | база знаний | ремонтные форумы |
| 7 | Чип Wi-Fi/BT (erista — Broadcom? mariko — ?) — уточнить марку | база знаний «нет Wi-Fi» | switchbrew, teardown |
| 8 | Что именно отдает hekate по eMMC health / батарее / фьюзам | парсер фазы 2 | исходники hekate (nyx) |
| 9 | Таблицы серийников «patched/unpatched» (XAW/GAW/...) | определение ревизии | публичные базы (dgql и др.) |
