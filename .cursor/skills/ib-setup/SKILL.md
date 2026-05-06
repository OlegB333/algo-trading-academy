---
name: ib-setup
description: Настройка и проверка интеграции с Interactive Brokers (TWS). Используй когда ученик просит "переключиться на акции", "работать с форексом", "скачать данные по акциям/фьючерсам", "подключить IB", "подключить Interactive Brokers", "торговать на фондовом рынке", или когда нужна проверка IB перед бэктестом/скачиванием данных с IB.
---

# Настройка Interactive Brokers (TWS)

## Концепция

Для работы с акциями, форексом и фьючерсами через Interactive Brokers используется
**TWS (Trader Workstation)** — официальный торговый терминал IB, установленный локально
на компьютере ученика. Freqtrade подключается к TWS через API.

> **Зачем TWS, а не Gateway?**
> TWS уже установлен у большинства трейдеров, не требует дополнительных Docker-контейнеров,
> и ученик видит свои позиции визуально в привычном интерфейсе.
> IB Gateway через Docker — альтернатива для удалённого VPS-деплоя (см. skill `deployment`).

## Правила

- Никогда не меняй базовый `docker-compose.yml` в рамках этого навыка.
- Не проси ученика вводить команды в терминал — делай всё сам.
- Если TWS не установлен — дай инструкцию и жди подтверждения.

---

## Алгоритм

### Шаг 1. Проверь, доступен ли порт TWS

Проверь порт 7497 (Paper Trading):

```bash
nc -z 127.0.0.1 7497 && echo "PORT_OPEN" || echo "PORT_CLOSED"
```

**Если порт открыт** → TWS запущен и API включён. Перейди сразу к Шагу 4 (проверка соединения).

**Если порт закрыт** → TWS не запущен или API не настроен. Перейди к Шагу 2.

---

### Шаг 2. Инструкция ученику (если TWS не готов)

Напиши ученику следующее (адаптируй под ситуацию):

---

> ⚠️ **Для работы с акциями, форексом и фьючерсами нужен терминал Interactive Brokers (TWS).**
>
> **Что потребуется:**
> 1. **Учётная запись Interactive Brokers** — если нет, зарегистрируйтесь на [interactivebrokers.com](https://www.interactivebrokers.com). Для обучения подойдёт бесплатный Paper Trading аккаунт.
> 2. **Установленный TWS** — скачайте с [interactivebrokers.com/en/trading/tws.php](https://www.interactivebrokers.com/en/trading/tws.php) и установите.
>
> **После установки — включите API в TWS:**
> 1. Запустите TWS и войдите в Paper Trading аккаунт
> 2. Откройте: `Edit` → `Global Configuration` → `API` → `Settings`
> 3. Поставьте галочку **"Enable ActiveX and Socket Clients"**
> 4. Убедитесь что Socket Port = **7497** (Paper Trading)
> 5. В "Trusted IP Addresses" убедитесь что есть **127.0.0.1**
> 6. Нажмите **OK** и **не закрывайте TWS**
>
> Напишите мне **«Готово»**, и я проверю соединение.

---

### Шаг 3. Повторная проверка после подтверждения

После того как ученик написал «Готово», проверь снова:

```bash
nc -z 127.0.0.1 7497 && echo "PORT_OPEN" || echo "PORT_CLOSED"
```

Если порт всё ещё закрыт — помоги диагностировать:
- TWS запущен и залогинен?
- Галочка "Enable ActiveX and Socket Clients" стоит?
- Socket Port = 7497?
- TWS не закрыт?

---

### Шаг 4. Запуск Freqtrade (только freqtrade, без Gateway)

Когда порт открыт — запускай **только** контейнер `freqtrade`, без `ib-gateway`:

```bash
docker compose -f docker-compose.ib.yml up -d freqtrade
```

> `ib-gateway` — это Docker-контейнер для удалённого VPS-деплоя без TWS.
> При локальной работе с TWS он не нужен и запускать его не следует.

### Шаг 5. Проверка статуса

```bash
docker compose -f docker-compose.ib.yml ps
```

Ожидай статуса `Up` только у контейнера `freqtrade-ib`.
Если контейнер не поднялся — проверь логи:
```bash
docker compose -f docker-compose.ib.yml logs freqtrade --tail 30
```

### Шаг 6. Ответ ученику

> ✅ **Freqtrade подключён к Interactive Brokers через TWS!**
>
> Теперь можно:
> - Скачивать данные по акциям, форексу и фьючерсам (`download-data`)
> - Запускать бэктесты на реальных рыночных данных IB
> - Запускать стратегии в dry-run режиме
>
> Интерфейс FreqUI: **http://localhost:8080**
>
> ⚠️ **Важно:** не закрывайте TWS пока работаете с ботом. Freqtrade держит постоянное соединение с терминалом.

---

## Порты TWS (справочно)

| Режим | Порт |
|-------|------|
| Paper Trading | **7497** |
| Live Trading | **7496** |

Конфиги проекта (`config_forex.json`, `config_futures.json`, `config_stocks.json`)
уже настроены на `host.docker.internal:7497` (Paper Trading).

---

## Альтернатива: IB Gateway через Docker (для VPS)

Если нужно запустить Freqtrade на удалённом сервере без TWS — используй
Docker-контейнер `ib-gateway` (`ghcr.io/gnzsnz/ib-gateway:stable`).
Подробнее — в skill `deployment`, раздел «IB на удалённом VPS».
