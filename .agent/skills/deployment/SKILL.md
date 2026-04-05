---
name: deployment
description: Деплой Freqtrade-бота на VPS-сервер. Используй когда пользователь хочет перенести бота на сервер, настроить VPS, запустить в продакшен, или говорит "сервер", "VPS", "деплой", "deployment", "продакшен", "удалённый сервер", "SSH", "запустить 24/7".
---

# Деплой на VPS

## Обзор

Локальная разработка → VPS dry-run → VPS live. Каждый шаг — с проверкой.

## Шаг 1: Подключение к серверу

```bash
ssh user@YOUR_SERVER_IP
```

## Шаг 2: Установка Docker

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
# Перелогиниться для применения группы
exit
ssh user@YOUR_SERVER_IP
docker --version
```

## Шаг 3: Клонирование репозитория

```bash
git clone YOUR_REPO_URL algo-trading-academy
cd algo-trading-academy
```

## Шаг 4: Настройка .env

На VPS `.env` нужен для API-ключей и Telegram:
```bash
cp .env.example .env
nano .env
```

Заполни: `EXCHANGE_KEY`, `EXCHANGE_SECRET`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`

## Шаг 5: Безопасность VPS

Базовый минимум:
```bash
# Обновления
sudo apt update && sudo apt upgrade -y

# Firewall: только SSH и нужные порты
sudo ufw allow OpenSSH
sudo ufw enable

# НЕ открывай 8080 наружу — FreqUI через SSH-туннель
```

Доступ к FreqUI на VPS — через SSH-туннель с локального Mac:
```bash
ssh -L 8080:localhost:8080 user@YOUR_SERVER_IP
# Теперь http://localhost:8080 на твоём Mac → FreqUI на VPS
```

## Шаг 6: Dry-run на VPS

```bash
docker compose up -d
docker compose logs -f --tail 20
```

Проверь:
- Контейнер `healthy`
- Бот торгует виртуально
- FreqUI доступен через SSH-туннель

Погоняй dry-run минимум 24-48 часов перед переходом на live.

## Шаг 7: Переход на live

⚠️ **Только с ДВОЙНЫМ подтверждением пользователя.**

1. Останови dry-run: `docker compose down`
2. Создай override:
   ```json
   {
       "dry_run": false
   }
   ```
3. Добавь override в `command` docker-compose.yml
4. Запусти: `docker compose up -d`
5. Проверь первые сделки в FreqUI и Telegram

## Обновление стратегии на VPS

```bash
cd algo-trading-academy
git pull origin main
docker compose restart
```

Или для полного перезапуска:
```bash
docker compose down
docker compose up -d
```

## Мониторинг

### Логи
```bash
docker compose logs -f --tail 50
```

### Здоровье контейнера
```bash
docker compose ps
# STATUS: Up (healthy)
```

### Ресурсы сервера
```bash
docker stats freqtrade
htop
```

## API-ключи биржи

При создании API-ключей на Binance:
- ✅ Включи: Spot Trading
- ❌ Выключи: Withdraw (вывод средств)
- ✅ Включи: IP Whitelist (IP твоего VPS)

Никогда не создавай ключи с правом вывода.

## Частые ошибки

1. **Открыл 8080 наружу** → любой может видеть и управлять ботом. Только SSH-туннель
2. **API-ключ с правом вывода** → при компрометации теряешь всё
3. **Не протестировал dry-run на VPS** → сразу live = проблемы
4. **Забыл `.env`** → бот стартует в dry-run (безопасно, но не то что хотел)
5. **Не настроил firewall** → VPS уязвим
