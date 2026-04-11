---
name: data
description: Скачивание и управление рыночными данными для Freqtrade. Используй когда пользователь хочет скачать данные, добавить пары, проверить какие данные есть, изменить таймфрейм, или говорит "данные", "data", "свечи", "скачай", "download", "пары", "history", "исторические данные".
---

# Управление рыночными данными

## Стартовый набор проекта

В репозитории уже есть данные для немедленного бэктеста:
- **Пары:** BTC/USDT, ETH/USDT
- **Таймфрейм:** 1h
- **Период:** 90 дней
- **Формат:** parquet

Эти данные находятся в `user_data/data/binance/` и закоммичены в git.

## Скачивание данных

Базовая команда (по умолчанию скачивает **Спот**):
```bash
docker compose run --rm freqtrade download-data \
  --config /freqtrade/user_data/config/config.json \
  --pairs BTC/USDT ETH/USDT \
  --exchange binance \
  --days 90 \
  -t 1h
```

Если ученик просит скачать данные для **Фьючерсов (Крипта)** (например, Binance Futures), добавляй флаг `--trading-mode futures`. Названия пар пишутся в формате `BASE/QUOTE:SETTLE` (например, `BTC/USDT:USDT`):
```bash
docker compose run --rm freqtrade download-data \
  --config /freqtrade/user_data/config/config.json \
  --pairs BTC/USDT:USDT ETH/USDT:USDT \
  --exchange binance \
  --days 90 \
  -t 1h \
  --trading-mode futures
```

Если ученик просит скачать данные для **Фьючерсов (отличных от крипты)** (например, S&P 500, Nasdaq через Interactive Brokers):
Используй конфиг `config_futures.json` и указывай биржу `interactivebrokers`. Пары также пишутся через USD.

**ПРИМЕЧАНИЕ ОБ ИНТЕГРАЦИИ:** Перед скачиванием любых данных с Interactive Brokers (Акции, Форекс, Фьючерсы CME), ты должен быть уверен, что контейнер `ib-gateway` настроен и запущен. Если скачивание падает с ошибкой соединения (Connection Refused), подскажи ученику: *"Похоже, интеграция IB не запущена. Давайте сначала запустим её через настройку IB Gateway"* (согласно навыку `ib-setup`).

**ПРАВИЛО МАРШРУТИЗАЦИИ:** Для IB фьючерсов требуется знать конкретную биржу (CME, CBOT, NYMEX и т.д.).
Если ученик просит скачать нестандартный тикер (например `HO/USD` или `VX/USD`), и ты не уверен, на какой бирже он торгуется, **ОБЯЗАТЕЛЬНО СПРОСИ УЧЕНИКА**: *"На какой бирже торгуется этот фьючерс (например, NYMEX, CFE)?"*. 
Получив ответ, **сначала добавь** этот тикер в раздел `futures_contracts` файла `user_data/config_futures.json`:
```json
"futures_contracts": [
    ...
    {"symbol": "HO", "exchange": "NYMEX"}
]
```
И только после этого запускай скачивание:
```bash
docker compose run --rm freqtrade download-data \
  --config /freqtrade/user_data/config_futures.json \
  --pairs ES/USD HO/USD \
  --exchange interactivebrokers \
  --days 30 \
  -t 1h \
  --trading-mode futures
```

Если пары или биржа были изменены через override, добавь его:
```bash
docker compose run --rm freqtrade download-data \
  --config /freqtrade/user_data/config/config.json \
  --config /freqtrade/user_data/config/config.override.json \
  --days 90 \
  -t 1h
```

Если ученик просит скачать данные для **Форекс (Forex)** или **Акций (Stocks)** через Interactive Brokers:
Всегда используй соответствующий конфигурационный файл из корня `user_data` и явно указывай биржу `interactivebrokers`:
```bash
docker compose run --rm freqtrade download-data \
  --config /freqtrade/user_data/config_forex.json \
  --pairs EUR/USD GBP/USD \
  --exchange interactivebrokers \
  --days 30 \
  -t 1h \
  --trading-mode spot
```
*(Для акций используй `--config /freqtrade/user_data/config_stocks.json` и указывай тикеры через USD, например `AAPL/USD`, `MSFT/USD`).*
В этом случае пары возьмутся из `pair_whitelist` в override.

## Данные по сделкам (Trades)

Если ученик просит скачать **сделки (trades)**, тики, ленту или "tick data" (вместо обычных свечей OHLCV), используй флаг `--dl-trades`.
**Осторожно:** скачивание "trades" за длительные периоды (долгие месяцы/годы) — это очень тяжелая операция, которая может привести к падению контейнера по памяти (OOM). Если период не указан жестко, всегда начинай с малого (например, `--days 5`).

```bash
docker compose run --rm freqtrade download-data \
  --config /freqtrade/user_data/config/config.json \
  --pairs BTC/USDT \
  --exchange binance \
  --days 5 \
  --dl-trades
```
*(Для фьючерсов — так же, как и всегда, не забудь `--trading-mode futures` и суффикс `:USDT` к парам).*


## Параметры

| Параметр | Описание | Пример |
|----------|----------|--------|
| `--pairs` | Торговые пары (через пробел) | `BTC/USDT ETH/USDT SOL/USDT` |
| `--exchange` | Биржа | `binance` |
| `--days` | Сколько дней назад | `90`, `365` |
| `--timerange` | Точный период (вместо --days) | `20250101-20260101` |
| `-t` | Таймфрейм | `1m`, `5m`, `15m`, `1h`, `4h`, `1d` |
| `--trading-mode` | Тип рынка | `spot` или `futures` (обязателен для скачивания данных для фьючей) |
| `--dl-trades` | Скачать сырые сделки (ticks) | Используется вместо `-t` для продвинутого анализа |
| `--erase` | ⚠️ Удалить старые данные перед скачиванием | Только по явному запросу пользователя |

`--erase` безвозвратно удаляет существующие данные для указанных пар. Не используй
без явной просьбы пользователя — по умолчанию Freqtrade дозаписывает данные к существующим.

## Таймфрейм: данные ↔ стратегия

Таймфрейм скачанных данных должен совпадать с `timeframe` в стратегии.
Если стратегия использует `timeframe = "5m"`, а данные скачаны за `1h` — бэктест
либо упадёт, либо выдаст пустые результаты.

Перед скачиванием проверь таймфрейм стратегии:
```python
# В файле стратегии
timeframe = "1h"  # ← данные нужны за этот таймфрейм
```

## Несколько таймфреймов

```bash
docker compose run --rm freqtrade download-data \
  --config /freqtrade/user_data/config/config.json \
  --pairs BTC/USDT \
  --exchange binance \
  --days 180 \
  -t 1h 4h 1d
```

## Где хранятся

Данные сохраняются в `user_data/data/binance/` в формате parquet:
```
user_data/data/binance/
├── BTC_USDT-1h.parquet    ← стартовый набор (в git)
├── ETH_USDT-1h.parquet    ← стартовый набор (в git)
├── SOL_USDT-1h.parquet    ← скачано дополнительно (НЕ в git)
└── ...
```

## Правило: не коммить дополнительные данные

Стартовый набор (BTC/USDT + ETH/USDT 1h) уже в git. Все дополнительно скачанные
данные — не коммить. Они воспроизводимы командой `download-data` и утяжеляют
репозиторий. `.gitignore` исключает всё кроме базовых файлов.

## Проверка доступных данных

```bash
docker compose run --rm freqtrade list-data \
  --config /freqtrade/user_data/config/config.json
```

## Доступные пары

```bash
docker compose run --rm freqtrade list-pairs \
  --config /freqtrade/user_data/config/config.json \
  --exchange binance \
  --quote USDT
```

## Размер данных (справочно)

| Период | Таймфрейм | Размер на пару |
|--------|-----------|----------------|
| 90 дней | 1h | ~100 KB |
| 1 год | 1h | ~400 KB |
| 1 год | 5m | ~5 MB |
| 1 год | 1m | ~25 MB |

## Частые ошибки

1. **Пара не найдена** → формат: `BTC/USDT`, не `BTCUSDT`
2. **Timeout при скачивании** → уменьши `--days` или скачивай по одной паре
3. **Бэктест пустой** → таймфрейм данных ≠ таймфрейм стратегии
4. **Нет данных за период** → скачай данные перед запуском бэктеста
5. **Данные не обновляются** → Freqtrade дозаписывает; если нужно заново — `--erase` (с подтверждением)
