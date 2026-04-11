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

Если ученик просит скачать данные для **Фьючерсов**, обязательно добавляй флаг `--trading-mode futures`. Боту нужны специальные файлы (mark prices, funding rates) для симуляции фьючерсного рынка кросс/изолированной маржи.
**ВАЖНО:** Для фьючерсов названия пар пишутся в формате `BASE/QUOTE:SETTLE` (например, `BTC/USDT:USDT`):
```bash
docker compose run --rm freqtrade download-data \
  --config /freqtrade/user_data/config/config.json \
  --pairs BTC/USDT:USDT ETH/USDT:USDT \
  --exchange binance \
  --days 90 \
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
