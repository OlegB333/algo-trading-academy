---
name: risk
description: Настройка риск-менеджмента и защиты депозита в Freqtrade. Используй когда пользователь хочет настроить стоп-лосс, ограничить просадку, добавить протекции, рассчитать размер позиции, или говорит "риск", "стоп-лосс", "просадка", "drawdown", "защита", "протекции", "размер позиции", "мани-менеджмент", "ограничения".
---

# Риск-менеджмент в Freqtrade

## Уровни защиты

Freqtrade предлагает несколько слоёв защиты. Начни с базовых (1-3),
продвинутые (4-5) добавляй когда базовые освоены.

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

Автоматическое закрытие при достижении цели по времени.
Ключи — **минуты** (не свечи), значения — минимальная прибыль:
```python
minimal_roi = {
    "0": 0.04,     # +4% — закрыть в любой момент
    "600": 0.02,   # +2% через 600 минут (10 часов)
    "1200": 0.01,  # +1% через 1200 минут (20 часов)
    "2400": 0.0    # break-even через 2400 минут (40 часов)
}
```

> Ключи ROI всегда в минутах, независимо от таймфрейма стратегии.

### 3. Max open trades (уровень портфеля)

Ограничение одновременных позиций через config (или override):
```json
{
    "max_open_trades": 3,
    "stake_amount": 200
}
```

Правило: `max_open_trades × stake_amount` не должно превышать кошелёк.

---

### 4. Protections (продвинутый уровень)

Protections — это автоматические «предохранители», которые останавливают
торговлю при плохих условиях. Это продвинутый инструмент — добавляй только
после того как базовые stoploss/ROI настроены и протестированы.

Добавляются в стратегию:

```python
from freqtrade.strategy import IStrategy

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

| Депозит | Риск на сделку (2%) | Stoploss -10% | Размер позиции |
|---------|---------------------|---------------|----------------|
| 1000 | 20 USDT | -10% | 200 USDT |
| 5000 | 100 USDT | -10% | 1000 USDT |
| 10000 | 200 USDT | -5% | 4000 USDT |

Правило 1-2% — распространённый ориентир, но не универсальное правило.
Допустимый риск зависит от стратегии, win rate и личного комфорта.
Главное — определить свой лимит **до** запуска, а не после первого убытка.

## Бэктест с протекциями

```bash
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config/config.json \
  --strategy MyStrategy \
  --enable-protections \
  --timerange 20260105-20260405
```
*(Для фьючерсов не забудь подставить `config_futures.json`)*

Без `--enable-protections` протекции игнорируются в бэктесте.

## Частые ошибки

1. **Нет stoploss** → убыточная сделка может значительно сократить депозит
2. **Stoploss слишком тесный** (-1-2%) → выбивает из сделок рыночным шумом
3. **Забыл `--enable-protections`** → протекции не работают в бэктесте
4. **`stake_amount × max_open_trades > wallet`** → не хватит средств для всех позиций
5. **Протекции без бэктеста** → не проверили как они влияют на общий результат
6. **Навесил все protections сразу** → бот почти не торгует. Начни с одной, проверь
