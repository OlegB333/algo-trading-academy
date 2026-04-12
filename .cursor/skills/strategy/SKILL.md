---
name: strategy
description: Создание и модификация торговых стратегий Freqtrade. Используй когда пользователь хочет создать новую стратегию, изменить существующую, добавить индикаторы, настроить условия входа/выхода, или говорит "стратегия", "сигнал", "индикатор", "вход", "выход", даже если не использует технические термины.
---

# Создание и редактирование стратегий Freqtrade

## Расположение

Все стратегии хранятся в `user_data/strategies/`. Каждая стратегия — отдельный `.py` файл.
В этом проекте придерживаемся ЖЕСТКОГО правила: имя класса совпадает с именем файла (без `.py`), и само имя строится по одному из двух шаблонов:
1. **`ИмяСтратегии_Тикер_Таймфрейм.py`** (для узких стратегий под один актив, например: `BollingerBreakout_GC_30m.py` → `class BollingerBreakout_GC_30m(IStrategy)`).
2. **`ИмяСтратегии_Рынок_Таймфрейм.py`** (если стратегия универсальная на корзину активов, например: `TrendFollower_Spot_15m.py` → `class TrendFollower_Spot_15m(IStrategy)`).

**Обязательно:** каждая стратегия должна содержать `plot_config` — это позволяет ученику видеть индикаторы на графике в FreqUI. Без `plot_config` в UI видна только цена и сделки, но не логика стратегии.

## Спот или Фьючерсы?

Если ученик просит создать стратегию для **фьючерсов**, ты должен:
1. В самой стратегии установить `can_short = True`.
2. Обязательно добавить метод настройки РАБОЧЕГО плеча (иначе биржа не позволит открыть позицию, либо возьмёт дефолт 1.0):
   ```python
   def leverage(self, pair: str, current_time: 'datetime', current_rate: float,
                proposed_leverage: float, max_leverage: float, entry_tag: str, side: str,
                **kwargs) -> float:
       return 5.0  # Например, всегда торгуем с 5x плечом
   ```
3. При последующем запуске бэктеста использовать специальный фьючерсный конфиг: `--config /freqtrade/user_data/config/config_crypto_futures.json` (или `config_futures.json` для IBKR).

## Связь с данными

Значение `timeframe` в стратегии должно совпадать с таймфреймом скачанных данных.
Стартовый набор проекта — 1h. Если стратегия использует другой таймфрейм,
сначала скачай данные (см. skill `data`).

## Перед изменением

Перед перезаписью существующей стратегии — сделай бэкап:
```bash
cp user_data/strategies/MyStrategy.py user_data/strategies/MyStrategy.py.bak
```
Расширение `.bak` важно — Freqtrade загружает только `.py` файлы,
поэтому бэкап не подхватится как стратегия. Мелкие правки бэкапа не требуют — git отследит.

## Шаблон стратегии

```python
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
from technical import qtpylib

class MyStrategyName(IStrategy):
    """Краткое описание стратегии."""

    INTERFACE_VERSION = 3
    can_short = False  # True только для futures

    # Таймфрейм — должен совпадать с данными в user_data/data/
    timeframe = "1h"

    # ROI — минимальная цель прибыли по времени
    # Ключ = количество свечей (зависит от timeframe)
    minimal_roi = {
        "0": 0.04,    # 4% сразу после входа
        "10": 0.02,   # 2% через 10 свечей (10ч при 1h)
        "20": 0.01,   # 1% через 20 свечей (20ч при 1h)
        "40": 0.0     # break-even через 40 свечей
    }

    # Стоп-лосс
    stoploss = -0.10  # -10%

    # Trailing stop (опционально)
    trailing_stop = False

    # Сколько свечей нужно для прогрева индикаторов
    startup_candle_count = 200

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Рассчитай индикаторы. Вызывается для каждой свечи."""
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["sma_20"] = ta.SMA(dataframe, timeperiod=20)
        dataframe["sma_50"] = ta.SMA(dataframe, timeperiod=50)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Условия входа в позицию."""
        dataframe.loc[
            (
                (dataframe["rsi"] < 30) &
                (dataframe["sma_20"] > dataframe["sma_50"]) &
                (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Условия выхода из позиции."""
        dataframe.loc[
            (
                (dataframe["rsi"] > 70) &
                (dataframe["volume"] > 0)
            ),
            "exit_long",
        ] = 1
        return dataframe

    # Визуализация индикаторов в FreqUI
    plot_config = {
        "main_plot": {
            "sma_20": {"color": "#2196F3"},
            "sma_50": {"color": "#FF9800"},
        },
        "subplots": {
            "RSI": {
                "rsi": {"color": "#9C27B0"},
            }
        }
    }
```

## Доступные индикаторы

Образ Freqtrade содержит ta-lib и technical. Основные:

### Трендовые
- `ta.SMA(dataframe, timeperiod=N)` — Simple Moving Average
- `ta.EMA(dataframe, timeperiod=N)` — Exponential Moving Average
- `ta.TEMA(dataframe, timeperiod=N)` — Triple EMA
- `ta.BBANDS(dataframe)` — Bollinger Bands → upper, middle, lower
- `qtpylib.bollinger_bands(...)` — альтернативный расчёт BB

### Осцилляторы
- `ta.RSI(dataframe, timeperiod=14)` — Relative Strength Index
- `ta.MACD(dataframe)` → macd, macdsignal, macdhist
- `ta.STOCH(dataframe)` → slowk, slowd
- `ta.ADX(dataframe)` — Average Directional Index
- `ta.MFI(dataframe)` — Money Flow Index
- `ta.CCI(dataframe)` — Commodity Channel Index

### Утилиты
- `qtpylib.crossed_above(series1, series2)` — пересечение вверх
- `qtpylib.crossed_below(series1, series2)` — пересечение вниз
- `ta.SAR(dataframe)` — Parabolic SAR
- `ta.ATR(dataframe)` — Average True Range

## Частые ошибки

1. **Забыли `& (dataframe["volume"] > 0)`** — Freqtrade требует volume > 0
2. **Имя класса ≠ имя файла** — стратегия не найдётся
3. **`can_short = True` на spot** — ошибка, short только для futures
4. **Маленький `startup_candle_count`** — индикаторы считают NaN на первых свечах
5. **Отступы в populate_entry/exit** — методы должны быть внутри класса (4 пробела)
6. **Таймфрейм стратегии ≠ данные** — бэктест упадёт или будет пустым

---

## Hyperopt-параметры (продвинутый этап)

После того как базовая стратегия работает и протестирована, можно добавить
автоматическую оптимизацию параметров.

Добавь импорт и параметры в стратегию:
```python
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter, CategoricalParameter

class MyStrategy(IStrategy):
    # Целые числа
    buy_rsi = IntParameter(low=10, high=40, default=30, space="buy", optimize=True)
    sell_rsi = IntParameter(low=60, high=90, default=70, space="sell", optimize=True)

    # Десятичные
    buy_threshold = DecimalParameter(low=0.01, high=0.10, default=0.05,
                                      decimals=2, space="buy", optimize=True)

    # Категориальные
    buy_signal = CategoricalParameter(["rsi", "macd", "bb"],
                                       default="rsi", space="buy", optimize=True)
```

Использование в условиях: `self.buy_rsi.value` (не `self.buy_rsi`).

Запуск оптимизации — см. skill `backtest`, секция Hyperopt.
