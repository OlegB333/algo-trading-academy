---
name: risk
description: Настройка риск-менеджмента и защиты депозита в Freqtrade. Используй когда пользователь хочет настроить стоп-лосс, ограничить просадку, добавить протекции, рассчитать размер позиции, или говорит "риск", "стоп-лосс", "просадка", "drawdown", "защита", "протекции", "размер позиции", "мани-менеджмент", "ограничения".
---

# Риск-менеджмент в Freqtrade

## Уровни защиты

Freqtrade предлагает несколько слоёв защиты. Каждый следующий — страховка
на случай если предыдущий не сработал.

### 1. Stoploss (уровень сделки)

```python
class MyStrategy(IStrategy):
    stoploss = -0.10  # -10% от цены входа
```

Виды stoploss:
```python
# Фиксированный
stoploss = -0.10

# Trailing — следует за ценой
trailing_stop = True
trailing_stop_positive = 0.01      # Активировать при +1% profit
trailing_stop_positive_offset = 0.03  # Начать трейлить при +3%
trailing_only_offset_is_reached = True
```

### 2. ROI (уровень сделки)

Автоматическое закрытие при достижении цели:
```python
minimal_roi = {
    "0": 0.04,    # +4% — закрыть сразу
    "10": 0.02,   # +2% через 10 свечей
    "20": 0.01,   # +1% через 20 свечей
    "40": 0.0     # break-even через 40 свечей
}
```

### 3. Max open trades (уровень портфеля)

Ограничение одновременных позиций через config (или override):
```json
{
    "max_open_trades": 3,
    "stake_amount": 200
}
```

Правило: `max_open_trades × stake_amount` не должно превышать кошелёк.

### 4. Protections (уровень системы)

Protections автоматически останавливают торговлю при плохих условиях.
Добавляются в стратегию:

```python
from freqtrade.strategy import IStrategy
from datetime import timedelta

class MyStrategy(IStrategy):

    @property
    def protections(self):
        return [
            # Стоп после N убыточных сделок подряд
            {
                "method": "StoplossGuard",
                "lookback_period_candles": 24,
                "trade_limit": 3,
                "stop_duration_candles": 12,
                "only_per_pair": False
            },
            # Остановка если drawdown превышен
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": 48,
                "max_allowed_drawdown": 0.2,  # 20%
                "stop_duration_candles": 24,
                "trade_limit": 1
            },
            # Кулдаун после каждой сделки
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 2
            }
        ]
```

### 5. Глобальные лимиты (уровень config)

В `config.override.json`:
```json
{
    "max_open_trades": 3,
    "tradable_balance_ratio": 0.5,
    "stake_amount": 200
}
```

`tradable_balance_ratio: 0.5` — использовать только 50% депозита.

## Расчёт размера позиции

Формула: `Риск на сделку = Размер позиции × |Stoploss|`

| Депозит | Макс. риск на сделку (2%) | Stoploss -10% | Размер позиции |
|---------|--------------------------|---------------|----------------|
| 1000 | 20 USDT | -10% | 200 USDT |
| 5000 | 100 USDT | -10% | 1000 USDT |
| 10000 | 200 USDT | -5% | 4000 USDT |

Рекомендация: риск на одну сделку ≤ 1-2% от депозита.

## Бэктест с протекциями

```bash
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config/config.json \
  --strategy MyStrategy \
  --enable-protections \
  --timerange 20260105-20260405
```

Без `--enable-protections` протекции игнорируются в бэктесте.

## Частые ошибки

1. **Нет stoploss** → одна сделка может съесть весь депозит
2. **Stoploss слишком тесный** (-1-2%) → выбивает из сделок шумом
3. **Забыл `--enable-protections`** → протекции не работают в бэктесте
4. **`stake_amount × max_open_trades > wallet`** → не хватит средств для всех позиций
5. **Протекции без бэктеста** → не проверили как они влияют на результат
