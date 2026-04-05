---
name: hyperopt
description: Автоматическая оптимизация параметров стратегии через Hyperopt в Freqtrade. Используй когда пользователь хочет оптимизировать стратегию, подобрать лучшие параметры, запустить машинный подбор, или говорит "hyperopt", "оптимизация", "подбор параметров", "эпохи", "epochs", "лучшие параметры", "автоматическая настройка".
---

# Hyperopt — автоматическая оптимизация параметров

## Когда использовать

Hyperopt — это **продвинутый инструмент**. Прежде чем запускать:

1. Стратегия должна работать и давать результат при ручном бэктесте
2. Ученик понимает что оптимизирует и зачем (Урок 3.13)
3. Данные скачаны за достаточный период

Hyperopt подбирает числовые параметры, но не создаёт логику стратегии.
Плохую стратегию оптимизация не спасёт — она лишь подгонит под историю (overfitting).

## Шаг 1: Подготовка стратегии

Добавь оптимизируемые параметры в стратегию:

```python
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter, CategoricalParameter

class MyStrategy(IStrategy):
    # Целые числа
    buy_rsi = IntParameter(low=10, high=40, default=30, space="buy", optimize=True)
    sell_rsi = IntParameter(low=60, high=90, default=70, space="sell", optimize=True)

    # Десятичные
    sl_percent = DecimalParameter(low=0.01, high=0.10, default=0.05,
                                   decimals=2, space="sell", optimize=True)

    # Категориальные
    ma_type = CategoricalParameter(["sma", "ema"],
                                    default="sma", space="buy", optimize=True)
```

В условиях используй `.value`: `self.buy_rsi.value`, не `self.buy_rsi`.

## Шаг 2: Запуск

```bash
docker compose run --rm freqtrade hyperopt \
  --config /freqtrade/user_data/config/config.json \
  --strategy MyStrategy \
  --hyperopt-loss SharpeHyperOptLoss \
  --spaces buy sell \
  --epochs 100 \
  --timerange 20260105-20260405
```

Если есть override:
```bash
docker compose run --rm freqtrade hyperopt \
  --config /freqtrade/user_data/config/config.json \
  --config /freqtrade/user_data/config/config.override.json \
  --strategy MyStrategy \
  --hyperopt-loss SharpeHyperOptLoss \
  --spaces buy sell \
  --epochs 100 \
  --timerange 20260105-20260405
```

## Параметры

| Параметр | Описание | Рекомендация |
|----------|----------|--------------|
| `--hyperopt-loss` | Целевая функция | `SharpeHyperOptLoss` для начала |
| `--spaces` | Что оптимизировать | `buy sell` — сигналы входа/выхода |
| `--epochs` | Количество итераций | 100-500 для начала |
| `--timerange` | Период данных | Не весь период — оставь часть для проверки |

### Loss-функции

| Функция | Оптимизирует | Когда использовать |
|---------|-------------|-------------------|
| `SharpeHyperOptLoss` | Sharpe ratio | Универсальный выбор |
| `SortinoHyperOptLoss` | Sortino ratio | Фокус на downside risk |
| `OnlyProfitHyperOptLoss` | Чистая прибыль | Агрессивный подход |
| `MaxDrawDownHyperOptLoss` | Мин. просадку | Консервативный подход |

### Spaces

| Space | Что оптимизирует |
|-------|-----------------|
| `buy` | Параметры со `space="buy"` |
| `sell` | Параметры со `space="sell"` |
| `roi` | Таблица minimal_roi |
| `stoploss` | Значение stoploss |
| `trailing` | Trailing stop параметры |

## Шаг 3: Применение результатов

Hyperopt выведет лучшие параметры. Скопируй их в стратегию:

```python
# Результат hyperopt:
buy_rsi = IntParameter(low=10, high=40, default=25, space="buy", optimize=True)
#                                         ^^^^^^^^ новое значение
```

## Ловушка: overfitting

Hyperopt может подогнать параметры под конкретный период. Защита:

1. **Разделяй данные**: оптимизируй на 70% периода, проверяй на оставшихся 30%
2. **Не гонись за идеальным результатом**: если hyperopt даёт +500% — это скорее всего подгонка
3. **Проверяй на другой паре**: хорошие параметры работают не только на одной паре
4. **Меньше параметров = лучше**: чем больше степеней свободы, тем выше риск overfitting

## Частые ошибки

1. **Нет параметров с `optimize=True`** → hyperopt ничего не оптимизирует
2. **Слишком широкие диапазоны** → нужно больше эпох, результат хуже
3. **Мало эпох** → hyperopt не успевает найти оптимум
4. **Весь период для оптимизации** → нечем проверить результат (out-of-sample)
