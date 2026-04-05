---
name: backtest
description: Запуск и анализ бэктеста торговой стратегии Freqtrade. Используй когда пользователь хочет протестировать стратегию на исторических данных, проверить результаты, оценить прибыльность, сравнить стратегии, или говорит "бэктест", "backtest", "проверь стратегию", "прогони на исторических данных", "тестирование", "прибыльность", даже если не использует слово "бэктест" явно.
---

# Бэктест стратегии в Freqtrade

## Базовая команда

```bash
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config/config.json \
  --strategy ИмяСтратегии \
  --timerange YYYYMMDD-YYYYMMDD
```

Все пути внутри контейнера начинаются с `/freqtrade/`.

## Параметры

| Параметр | Описание | Пример |
|----------|----------|--------|
| `--strategy` | Имя класса стратегии | `SampleStrategy` |
| `--timerange` | Период тестирования | `20260101-20260401` |
| `--timeframe` | Таймфрейм (override стратегии) | `1h`, `5m`, `1d` |
| `--stake-amount` | Размер позиции | `100`, `unlimited` |
| `--max-open-trades` | Макс. одновременных сделок | `3` |
| `--strategy-list` | Сравнить несколько стратегий | `Strat1 Strat2` |
| `--enable-protections` | Включить протекции | — |

## Примеры

**Пример 1: Простой бэктест**
```bash
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config/config.json \
  --strategy SampleStrategy \
  --timerange 20260101-20260401
```

**Пример 2: Сравнение двух стратегий**
```bash
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config/config.json \
  --strategy-list SampleStrategy MyNewStrategy \
  --timerange 20260101-20260401
```

**Пример 3: С override-конфигом**
```bash
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config/config.json \
  --config /freqtrade/user_data/config/config.override.json \
  --strategy SampleStrategy \
  --timerange 20260101-20260401
```

## Чтение результатов

Ключевые метрики в выводе:

| Метрика | Что значит | Хорошо если |
|---------|------------|-------------|
| **Total profit %** | Общая прибыль | > 0% |
| **Sharpe** | Доходность/риск | > 1.0 |
| **Sortino** | Как Sharpe, но учитывает только downside | > 1.5 |
| **Max Drawdown** | Максимальная просадка | < 20% |
| **Profit factor** | Прибыль/убыток | > 1.5 |
| **Win Rate** | % выигрышных сделок | > 50% |
| **Avg Duration** | Средняя длительность сделки | Зависит от стратегии |
| **SQN** | System Quality Number | > 2.0 отлично |

## Предварительные условия

Перед запуском бэктеста убедись что:

1. **Данные скачаны** для нужных пар и таймфрейма:
   ```bash
   docker compose run --rm freqtrade download-data \
     --config /freqtrade/user_data/config/config.json \
     --pairs BTC/USDT ETH/USDT \
     --exchange binance \
     --days 90 -t 1h
   ```

2. **Стратегия существует** в `user_data/strategies/`

3. **Timerange покрыт данными** — если данных нет за указанный период, бэктест выдаст ошибку

## Hyperopt (оптимизация параметров)

Если стратегия содержит `IntParameter`/`DecimalParameter` с `optimize=True`:

```bash
docker compose run --rm freqtrade hyperopt \
  --config /freqtrade/user_data/config/config.json \
  --strategy ИмяСтратегии \
  --hyperopt-loss SharpeHyperOptLoss \
  --spaces buy sell \
  --epochs 100 \
  --timerange 20260101-20260401
```

Доступные loss-функции:
- `SharpeHyperOptLoss` — максимизирует Sharpe ratio (рекомендуется)
- `SortinoHyperOptLoss` — учитывает только downside volatility
- `OnlyProfitHyperOptLoss` — только прибыль
- `MaxDrawDownHyperOptLoss` — минимизирует просадку

## Частые ошибки

1. **Нет данных** → сначала `download-data`
2. **Timerange за пределами данных** → уменьшить диапазон
3. **Стратегия не найдена** → проверь имя класса внутри .py файла
4. **Мало сделок** → увеличь timerange или проверь условия входа
