# Algo Trading Academy

Преднастроенная торговая система на базе [Freqtrade](https://www.freqtrade.io/).

## Быстрый старт

### Требования
- Docker Desktop ([Mac](https://docs.docker.com/docker-for-mac/install/) / [Linux](https://docs.docker.com/install/))
- Windows: только через [WSL2](https://docs.docker.com/docker-for-windows/wsl/)

### Запуск
```bash
git clone <repo-url>
cd algo-trading-academy
docker compose up -d
```

Откройте http://localhost:8080 — FreqUI готов.

**Логин:** `freqtrader` / **Пароль:** `freqtrader`

## Структура проекта
```
user_data/
├── config/config.json    — конфигурация (dry-run, Binance)
├── strategies/           — ваши стратегии
├── data/                 — исторические данные
├── logs/                 — логи бота
└── backtest_results/     — результаты бэктестов
```

## Основные команды
```bash
# Бэктест
docker compose run --rm freqtrade backtesting \
  --config user_data/config/config.json \
  --strategy SampleStrategy \
  --timerange 20240101-20240401

# Скачать данные
docker compose run --rm freqtrade download-data \
  --pairs BTC/USDT ETH/USDT \
  --exchange binance \
  --days 90 -t 1h

# Логи
docker compose logs -f

# Остановить
docker compose down
```
