---
name: deployment
description: Деплой Freqtrade-бота на VPS-сервер. Используй когда пользователь хочет перенести бота на сервер, настроить VPS, запустить в продакшен, или говорит "сервер", "VPS", "деплой", "deployment", "продакшен", "удалённый сервер", "SSH", "запустить 24/7".
---

# Деплой на VPS

## Обзор

Деплой состоит из двух этапов. Первый — обязательный, второй — только по
явному решению пользователя:

1. **VPS dry-run** — бот работает 24/7 на сервере, торгует виртуально
2. **VPS live** — переключение на реальные деньги (отдельный шаг, позже)

## Часть 1: VPS dry-run

### 1.1 Подключение к серверу

```bash
ssh user@YOUR_SERVER_IP
```

### 1.2 Установка Docker

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
# Перелогиниться для применения группы
exit
ssh user@YOUR_SERVER_IP
```

Проверь что всё установилось:
```bash
docker --version
docker compose version
```

Обе команды должны вернуть версии. Если `docker compose version` не работает —
плагин `docker-compose-plugin` не установился, повтори `apt install`.

### 1.3 Клонирование репозитория

```bash
git clone YOUR_REPO_URL algo-trading-academy
cd algo-trading-academy
```

### 1.4 Безопасность VPS

Базовый минимум:
```bash
# Обновления
sudo apt update && sudo apt upgrade -y

# Firewall: только SSH
sudo ufw allow OpenSSH
sudo ufw enable
```

НЕ открывай порт 8080 наружу. FreqUI доступен через SSH-туннель
с локального Mac:
```bash
# На ЛОКАЛЬНОМ Mac:
ssh -L 8080:localhost:8080 user@YOUR_SERVER_IP
# Теперь http://localhost:8080 → FreqUI на VPS
```

### 1.5 Запуск dry-run

```bash
docker compose up -d
docker compose ps      # STATUS: Up (healthy)
docker compose logs -f --tail 20
```

Проверь:
- [ ] Контейнер `healthy`
- [ ] Бот торгует виртуально (видно в логах)
- [ ] FreqUI доступен через SSH-туннель
- [ ] Стратегия видна в UI

**Погоняй dry-run минимум 24-48 часов** перед любыми решениями о live.

### 1.6 Мониторинг

```bash
# Логи бота
docker compose logs -f --tail 50

# Здоровье контейнера
docker compose ps

# Ресурсы (Docker встроенный)
docker stats freqtrade
```

### 1.7 Обновление стратегии на VPS

```bash
cd algo-trading-academy
docker compose down
git pull origin main
docker compose up -d
```

Всегда `down → pull → up`. Команда `restart` может не подхватить изменения
в конфигах, образе или compose-файле.

---

## Часть 2: Переход на live

⚠️ **Только с ДВОЙНЫМ подтверждением пользователя.**
Это отдельный этап, не продолжение dry-run.

### 2.1 Подготовка .env

На VPS создай `.env` из шаблона:
```bash
cp .env.example .env
nano .env
```

Обязательные для live:
```bash
EXCHANGE_KEY=твой_api_key
EXCHANGE_SECRET=твой_api_secret
```

Опциональные (можно позже):
```bash
TELEGRAM_TOKEN=токен_бота
TELEGRAM_CHAT_ID=id_чата
```

### 2.2 API-ключи биржи

При создании API-ключей на Binance:
- ✅ Включи: Spot Trading
- ❌ Выключи: Withdraw (вывод средств)
- ✅ Включи: IP Whitelist (IP твоего VPS)

Никогда не создавай ключи с правом вывода.

### 2.3 Override для live

Создай `user_data/config/config.override.json`:
```json
{
    "dry_run": false
}
```

### 2.4 Переключение

```bash
# 1. Остановить dry-run
docker compose down

# 2. Запустить с override
# Для этого нужно добавить --config в command docker-compose.yml
# Это защищённый файл → запроси подтверждение у пользователя
```

Чтобы фоновый бот (`up -d`) использовал override, нужно изменить `command`
в `docker-compose.yml`. Это защищённый файл — объясни пользователю зачем
и получи подтверждение перед изменением.

Добавить в command:
```yaml
command: >
  trade
  --logfile /freqtrade/user_data/logs/freqtrade.log
  --db-url sqlite:////freqtrade/user_data/tradesv3.sqlite
  --config /freqtrade/user_data/config/config.json
  --config /freqtrade/user_data/config/config.override.json
  --strategy ИмяСтратегии
```

### 2.5 Запуск и проверка

```bash
docker compose up -d
docker compose logs -f --tail 20
```

Проверь первые сделки в FreqUI и Telegram (если настроен).

## Частые ошибки

1. **Открыл 8080 наружу** → любой может видеть и управлять ботом. Только SSH-туннель
2. **API-ключ с правом вывода** → при компрометации теряешь всё
3. **Сразу в live без dry-run на VPS** → непроверенная среда = проблемы
4. **`docker compose restart` вместо `down + up`** → может не подхватить изменения
5. **Забыл `docker compose version` после установки** → compose plugin может не стоять
6. **Смешал обязательные и опциональные секреты в .env** → биржевые ключи ≠ Telegram
