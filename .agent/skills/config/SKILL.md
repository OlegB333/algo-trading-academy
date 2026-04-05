---
name: config
description: Управление конфигурацией Freqtrade через override-механизм. Используй когда пользователь хочет изменить настройки бота, пары, размер позиции, добавить Telegram, изменить биржу, или говорит "настройки", "конфиг", "config", "параметры", "пары", "whitelist", "Telegram", "wallet", "кошелёк".
---

# Конфигурация Freqtrade

## Главное правило

**Не изменяй `user_data/config/config.json`** — это базовый конфиг, общий для всех.
Все изменения — через **override-файл**.

## Как работает override

Freqtrade мержит несколько конфигов слева направо. Последний перезаписывает предыдущий.

1. Создай `user_data/config/config.override.json`
2. Запускай с двумя конфигами:
   ```bash
   docker compose run --rm freqtrade trade \
     --config /freqtrade/user_data/config/config.json \
     --config /freqtrade/user_data/config/config.override.json \
     --strategy ИмяСтратегии
   ```

Override-файл содержит ТОЛЬКО те поля, которые нужно изменить.

## Примеры override

### Изменить размер кошелька и макс. сделок
```json
{
    "dry_run_wallet": 5000,
    "max_open_trades": 5,
    "stake_amount": 200
}
```

### Добавить пары
```json
{
    "exchange": {
        "pair_whitelist": [
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
            "XRP/USDT"
        ]
    }
}
```

### Включить Telegram
```json
{
    "telegram": {
        "enabled": true,
        "token": "YOUR_BOT_TOKEN",
        "chat_id": "YOUR_CHAT_ID"
    }
}
```

> Telegram-токен лучше хранить в `.env` и ссылаться через переменные окружения,
> а не хардкодить в override-файле.

### Настроить для бэктеста
```json
{
    "max_open_trades": 50,
    "stake_amount": "unlimited",
    "available_capital": 10000,
    "dry_run_wallet": 10000
}
```

## Базовый конфиг (справочно)

Основные параметры в `config.json` (read-only):

| Параметр | Значение | Описание |
|----------|----------|----------|
| `dry_run` | `true` | Виртуальная торговля |
| `dry_run_wallet` | `1000` | Стартовый баланс USDT |
| `stake_currency` | `USDT` | Валюта торговли |
| `trading_mode` | `spot` | Спот (не фьючерсы) |
| `exchange.name` | `binance` | Биржа |
| `max_open_trades` | `2` | Макс. одновременных сделок |
| `api_server.enabled` | `true` | FreqUI включён |
| `dataformat_ohlcv` | `parquet` | Формат данных |

## Переход на live

Для реальной торговли нужно:

1. Создать `.env` файл из `.env.example`:
   ```bash
   cp .env.example .env
   ```
2. Заполнить API-ключи Binance в `.env`
3. Создать override:
   ```json
   {
       "dry_run": false,
       "exchange": {
           "key": "${EXCHANGE_KEY}",
           "secret": "${EXCHANGE_SECRET}"
       }
   }
   ```

⚠️ **Переход на live — только с ДВОЙНЫМ подтверждением пользователя.**

## Частые ошибки

1. **Изменили config.json напрямую** → откатить через `git checkout user_data/config/config.json`
2. **Забыли добавить `--config` для override** → override не применится
3. **JSON-синтаксис** → проверь запятые и скобки, trailing comma запрещена
