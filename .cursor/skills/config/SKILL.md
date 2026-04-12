---
name: config
description: Управление конфигурацией Freqtrade через override-механизм. Используй когда пользователь хочет изменить настройки бота, пары, размер позиции, добавить Telegram, изменить биржу, или говорит "настройки", "конфиг", "config", "параметры", "пары", "whitelist", "Telegram", "wallet", "кошелёк".
---

# Конфигурация Freqtrade

## Главное правило

**Не изменяй `user_data/config/config.json`** — это базовый конфиг, общий для всех.
Все изменения — через **override-файл**.

## Два режима работы

| Режим | Команда | Когда |
|-------|---------|-------|
| **Фоновый бот** | `docker compose up -d` | Бот работает непрерывно (dry-run или live) |
| **Разовая команда** | `docker compose run --rm freqtrade ...` | Бэктест, скачивание данных, hyperopt |

Эти режимы **могут работать параллельно** (`run --rm` создаёт отдельный контейнер).
Но если ты изменил конфиг и хочешь чтобы фоновый бот подхватил изменения — перезапусти его:
```bash
docker compose down && docker compose up -d
```

## Как работает override

Freqtrade мержит несколько `--config` файлов слева направо. Последний перезаписывает.

1. Создай `user_data/config/config.override.json` с нужными параметрами
2. Явно передай оба конфига при запуске:
   ```bash
   docker compose run --rm freqtrade backtesting \
     --config /freqtrade/user_data/config/config.json \
     --config /freqtrade/user_data/config/config.override.json \
     --strategy ИмяСтратегии
   ```

**ОБЯЗАТЕЛЬНО ДЛЯ ФЬЮЧЕРСОВ:** Если стратегия использует фьючерсы, в качестве первой (базовой) конфигурации **всегда** используй `/freqtrade/user_data/config/config_futures.json`. То же касается overrides: все настройки пар и размеров позиций применяй к этому файлу (помни про формат с `:USDT`).

Override НЕ подхватывается автоматически — всегда указывай оба `--config` явно.

### Применение override к фоновому боту

Если нужно запустить бот с override-настройками на постоянной основе,
нужно изменить `command` в `docker-compose.yml` (это защищённый файл —
запроси подтверждение у пользователя):

```yaml
command: >
  trade
  --config /freqtrade/user_data/config/config.json
  --config /freqtrade/user_data/config/config.override.json
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

### Настроить плечо (только для фьючерсов)
```json
{
    "exchange": {
        "max_leverage": 20.0
    }
}
```

### Настроить для бэктеста
```json
{
    "max_open_trades": 50,
    "stake_amount": "unlimited",
    "available_capital": 10000,
    "dry_run_wallet": 10000
}
```

### Включить Telegram

Telegram-токены — это секреты. Не помещай их в override-файл напрямую.
Вместо этого используй `.env`:

1. Добавь в `.env`:
   ```
   TELEGRAM_TOKEN=твой_токен
   TELEGRAM_CHAT_ID=твой_chat_id
   ```
2. В override-файле Freqtrade не поддерживает переменные окружения напрямую,
   поэтому Telegram настраивается на этапе VPS-деплоя с помощью агента.

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

⚠️ **Переход на live — только с ДВОЙНЫМ подтверждением пользователя.**

Порядок обязательный:

1. **Остановить dry-run бот:**
   ```bash
   docker compose down
   ```
2. Создать `.env` из шаблона:
   ```bash
   cp .env.example .env
   ```
3. Заполнить API-ключи Binance в `.env`
4. Создать override:
   ```json
   {
       "dry_run": false
   }
   ```
   API-ключи Freqtrade берёт из `.env` (настраивается на этапе VPS-деплоя).
5. Запустить с override:
   ```bash
   docker compose up -d
   ```
   (после добавления override-конфига в `command` docker-compose.yml)

## Частые ошибки

1. **Изменили config.json напрямую** → откатить: `git checkout user_data/config/config.json`
2. **Забыли `--config` для override** → override не применится
3. **Конфиг не подхватился фоновым ботом** → перезапусти: `docker compose down && docker compose up -d`
4. **JSON-синтаксис** → проверь запятые и скобки, trailing comma запрещена
5. **Секреты в override** → токены и ключи только в `.env`, не в JSON-файлах
