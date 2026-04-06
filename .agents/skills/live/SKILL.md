---
name: live
description: Запуск стратегии в торговлю (dry-run или live). Используй когда ученик просит запустить бота, включить торговлю, dry-run, live, "запусти стратегию на рынке".
---

# Запуск стратегии в торговлю

## Режимы

| Режим | Что происходит | Риск |
|-------|---------------|------|
| **Dry-run** (по умолчанию) | Торговля виртуальными деньгами на реальных данных | Нулевой |
| **Live** | Торговля реальными деньгами | ⚠️ Потеря капитала |

Dry-run включается по умолчанию (в базовом `config.json` стоит `dry_run: true`).
Переключение в live требует **двойного подтверждения** ученика.

## Предварительные условия

1. Стратегия протестирована через бэктест (skill `backtest`)
2. Результаты проанализированы учеником
3. Ученик явно просит запустить стратегию в торговлю
4. Прочитай `.project-context` — там `PORT` для ссылки на FreqUI

## Шаг 1: Добавь command в docker-compose.override.yml

По умолчанию проект работает в **webserver mode** (бэктест + UI).
Для торговли нужно добавить `command` в override.

**Важно:** `docker-compose.override.yml` может уже существовать (например, с портом).
Не перезаписывай весь файл — **добавь** или **обнови** только секцию `command`.

Если файл **не существует** — создай:
```yaml
services:
  freqtrade:
    command: >
      trade
      --logfile /freqtrade/user_data/logs/freqtrade.log
      --db-url sqlite:////freqtrade/user_data/tradesv3.sqlite
      --config /freqtrade/user_data/config/config.json
      --strategy ИмяСтратегии
```

Если файл **уже существует** (например, с портом) — добавь `command`:
```yaml
services:
  freqtrade:
    ports:
      - "127.0.0.1:8081:8080"   # ← уже было, не трогай
    command: >                    # ← добавь только это
      trade
      --logfile /freqtrade/user_data/logs/freqtrade.log
      --db-url sqlite:////freqtrade/user_data/tradesv3.sqlite
      --config /freqtrade/user_data/config/config.json
      --strategy ИмяСтратегии
```

Замени `ИмяСтратегии` на реальное имя стратегии ученика.

## Шаг 2: Config override (только для live!)

Для **dry-run** дополнительный конфиг **не нужен** — `dry_run: true` уже стоит
в базовом `config.json`. Пропусти этот шаг.

Для **live** — создай `user_data/config/config.override.json`:
```json
{
    "dry_run": false
}
```
И добавь `--config /freqtrade/user_data/config/config.override.json` в command.

## Шаг 3: Перезапусти

```bash
docker compose down && docker compose up -d
```

Дождись статуса `healthy` через `docker compose ps`.
Если контейнер не поднялся — покажи `docker compose logs --tail=20`.

## Шаг 4: Ответь ученику

Для dry-run:
> ✅ Стратегия **ИмяСтратегии** запущена в режиме dry-run.
> Бот торгует виртуальными деньгами на реальных данных.
> FreqUI: http://localhost:PORT
>
> Чтобы вернуться в режим бэктестов, скажи "останови бота".

Для live:
> ⚠️ Стратегия **ИмяСтратегии** запущена в режиме LIVE.
> Бот торгует РЕАЛЬНЫМИ деньгами.
> FreqUI: http://localhost:PORT

Подставь реальный PORT из `.project-context`.

## Переключение обратно в webserver

Когда ученик говорит "останови бота", "верни бэктест", "выключи торговлю":

1. **Убери только `command`** из `docker-compose.override.yml` (не удаляй файл — там может быть порт и другие настройки)
2. Если после удаления `command` файл стал пустым (нет других override) — можно удалить
3. Перезапусти: `docker compose down && docker compose up -d`

Среда вернётся в webserver mode.

## Переключение Dry-run → Live

**Требуется двойное подтверждение.**

1. Объясни ученику: "Бот будет торговать реальными деньгами. Подтвердите."
2. Первое "да" получено → "Подтвердите ещё раз. Бот начнёт совершать реальные сделки."
3. Второе "да" → создай `config.override.json` с `"dry_run": false` и добавь его в command

Без `.env` с API-ключами биржи live не заработает (skill `deployment`).

## Частые ошибки

1. **Перетёр override с портом** → всегда читай существующий файл перед изменением
2. **Стратегия не найдена** → проверь имя класса в `.py` файле
3. **Live без API-ключей** → нужен `.env` с `EXCHANGE_KEY` и `EXCHANGE_SECRET`
4. **Удалил весь override при остановке** → удаляй только `command`, не весь файл
