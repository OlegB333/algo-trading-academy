---
name: data
description: Скачивание и управление рыночными данными для Freqtrade. Используй когда пользователь хочет скачать данные, добавить пары, проверить какие данные есть, изменить таймфрейм, или говорит "данные", "data", "свечи", "скачай", "download", "пары", "history", "исторические данные".
---

# Управление рыночными данными

## Скачивание данных

```bash
docker compose run --rm freqtrade download-data \
  --config /freqtrade/user_data/config/config.json \
  --pairs BTC/USDT ETH/USDT \
  --exchange binance \
  --days 90 \
  -t 1h
```

## Параметры

| Параметр | Описание | Пример |
|----------|----------|--------|
| `--pairs` | Торговые пары (через пробел) | `BTC/USDT ETH/USDT SOL/USDT` |
| `--exchange` | Биржа | `binance` |
| `--days` | Сколько дней назад | `90`, `365` |
| `--timerange` | Точный период (вместо --days) | `20250101-20260101` |
| `-t` | Таймфрейм | `1m`, `5m`, `15m`, `1h`, `4h`, `1d` |
| `--erase` | Удалить старые данные перед скачиванием | — |

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
├── BTC_USDT-1h.parquet
├── BTC_USDT-4h.parquet
├── ETH_USDT-1h.parquet
└── ...
```

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

## Размер данных

Примерные размеры parquet-файлов:
- 90 дней 1h = ~100KB на пару
- 1 год 1h = ~400KB на пару
- 1 год 5m = ~5MB на пару
- 1 год 1m = ~25MB на пару

Лимит в git-репозитории: < 50MB. Большие датасеты скачивай и не коммить
(они в `.gitignore` если > разумного размера).

## Частые ошибки

1. **Пара не найдена** → проверь формат: `BTC/USDT`, не `BTCUSDT`
2. **Timeout при скачивании** → уменьши `--days` или скачивай по одной паре
3. **Нет данных для бэктеста** → скачай данные за нужный период перед запуском
