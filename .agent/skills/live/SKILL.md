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

Dry-run включается по умолчанию. Переключение в live требует **двойного подтверждения** ученика.

## Предварительные условия

1. Стратегия протестирована через бэктест (skill `backtest`)
2. Результаты проанализированы учеником
3. Ученик явно просит запустить стратегию в торговлю

## Шаг 1: Создай override для переключения в trade mode

По умолчанию проект работает в **webserver mode** (бэктест + UI).
Для торговли нужно переключиться в **trade mode** через override.

Создай `docker-compose.override.yml`:

```yaml
services:
  freqtrade:
    command: >
      trade
      --logfile /freqtrade/user_data/logs/freqtrade.log
      --db-url sqlite:////freqtrade/user_data/tradesv3.sqlite
      --config /freqtrade/user_data/config/config.json
      --config /freqtrade/user_data/config/config.override.json
      --strategy ИмяСтратегии
```

Замени `ИмяСтратегии` на реальное имя стратегии ученика.

## Шаг 2: Создай config override (если нужно)

Для dry-run дополнительный конфиг не обязателен — `dry_run: true` уже стоит
в базовом `config.json`.

Для **live** — создай `user_data/config/config.override.json`:
```json
{
    "dry_run": false
}
```

## Шаг 3: Перезапусти

```bash
docker compose down && docker compose up -d
```

Проверь:
```bash
docker compose ps   # STATUS: healthy
docker compose logs --tail=20
```

## Шаг 4: Ответь ученику

Для dry-run:
> ✅ Стратегия **ИмяСтратегии** запущена в режиме dry-run.
> Бот торгует виртуальными деньгами на реальных рыночных данных.
> FreqUI: http://localhost:PORT
>
> Чтобы вернуться в webserver mode (бэктест), скажи "останови бота".

Для live:
> ⚠️ Стратегия **ИмяСтратегии** запущена в режиме LIVE.
> Бот торгует РЕАЛЬНЫМИ деньгами.
> FreqUI: http://localhost:PORT

## Переключение обратно в webserver

Когда ученик говорит "останови бота", "верни бэктест", "выключи торговлю":

1. Удали (или переименуй) `docker-compose.override.yml`
2. Перезапусти: `docker compose down && docker compose up -d`

Среда вернётся в webserver mode.

## Переключение Dry-run → Live

**Требуется двойное подтверждение.**

Перед переключением:
1. Объясни ученику риски: "Бот будет торговать реальными деньгами"
2. Попроси первое подтверждение
3. После первого "да" — скажи: "Подтверди ещё раз. Бот начнёт совершать реальные сделки на бирже."
4. Только после второго "да" — измени `config.override.json` на `"dry_run": false`

Без `.env` с API-ключами биржи live не заработает. Проверь что ключи настроены (skill `deployment`).

## Частые ошибки

1. **Override не подхватился** → `docker compose down && docker compose up -d` (не `restart`)
2. **Стратегия не найдена** → проверь имя класса в `.py` файле
3. **Live без API-ключей** → нужен `.env` с `EXCHANGE_KEY` и `EXCHANGE_SECRET`
4. **Забыл вернуть webserver** → после остановки бота удали override
