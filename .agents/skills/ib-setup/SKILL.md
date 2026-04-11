---
name: ib-setup
description: Запуск и проверка продвинутого модуля Interactive Brokers. Используй когда ученик просит "переключиться на акции", добавить поддержу интеректив брокерс, "запустить IB", "торговать на фондовом рынке, форекс" или "подключить IB Gateway".
---

# Запуск модуля Interactive Brokers

## Правила

- Модуль IB запускается **строго через отдельный файл**: `docker-compose.ib.yml`.
- Никогда не меняй базовый `docker-compose.yml` в рамках этого навыка.
- Для работы шлюза **обязательно** нужны `TWS_USERID` и `TWS_PASSWORD` в файле `.env`. Без них не запускай.

## Алгоритм

### 1. Проверка .env файла

Проверь наличие файла `.env` и переменных для IB:
- `TWS_USERID`
- `TWS_PASSWORD`

Если их нет, остановись и попроси ученика добавить:
> ⚠️ Для работы шлюза Interactive Brokers требуются логин и пароль данные от вашего аккаунта https://www.interactivebrokers.co.uk/
> Добавьте в файл `.env` переменные `TWS_USERID` и `TWS_PASSWORD`.

### 2. Запуск контейнеров

```bash
docker compose -f docker-compose.ib.yml up -d
```

### 3. Проверка статуса

```bash
docker compose -f docker-compose.ib.yml ps
```
Ожидай статуса `healthy` у контейнера `ib-gateway` (это занимает до 30 секунд). 
Убедись, что `freqtrade-ib` в статусе `Up` и не ушел в циклический `Restarting`.

Если `freqtrade-ib` перезагружается, проверь логи:
```bash
docker compose -f docker-compose.ib.yml logs freqtrade --tail 20
```

### 4. Ответ ученику

> ✅ Интеграция с Interactive Brokers успешно запущена!
> 
> Шлюз IB Gateway подключен, бот работает. 
> Интерфейс FreqUI доступен на `http://localhost:8080`.
> 
> *Заметка:* Бот запущен в режиме `dry-run`. В логах вы можете увидеть предупреждение "API interface is currently in Read-Only mode" – это нормально для безопасного режима.
