# Hummingbot: автоматизована крипто-торгівля

---

## Слайд 1 — Що таке Hummingbot?

- Open-source фреймворк для алгоритмічної торгівлі (Python)
- Підтримує 40+ бірж: Binance, Coinbase, Kraken, Uniswap та інші
- Стратегії: маркет-мейкінг, арбітраж, TWAP, grid trading
- GitHub: hummingbot/hummingbot (Apache 2.0)
- Активна спільнота + HBOT токен для governance

---

## Слайд 2 — Архітектура

```
┌─────────────────────────────────────┐
│           Strategy Layer            │  ← ваша логіка
├─────────────────────────────────────┤
│         Hummingbot Core             │  ← ордер-менеджер, event loop
├────────────────┬────────────────────┤
│  CEX Connector │  DEX Connector     │  ← REST + WebSocket
│  (Binance, ...) │ (Uniswap, ...)   │
└────────────────┴────────────────────┘
```

- **Connector** — абстракція над API біржі (REST polling + WS стріми)
- **OrderBook** — локальний стан книги ордерів у пам'яті
- **Strategy** — отримує події, приймає рішення, виставляє ордери

---

## Слайд 3 — Арбітраж — основний сценарій

### Трикутний арбітраж (в рамках однієї біржі)

```
USDT → BTC → ETH → USDT
```

1. Купити BTC за USDT
2. Купити ETH за BTC
3. Продати ETH за USDT
4. Профіт = різниця між implied і реальним курсом (мінус комісії)

### Умова прибутковості

```
implied_rate = (1 / ask_BTCUSDT) * (1 / ask_ETHBTC) * bid_ETHUSDT
net_profit = implied_rate - 1 - fees (3 × 0.1% = 0.3%)
```

Якщо `net_profit > 0` → можна робити коло.

---

## Слайд 4 — Конфігурація та запуск Hummingbot

### Встановлення

```bash
# Docker (рекомендовано)
docker run -it hummingbot/hummingbot

# або з source
git clone https://github.com/hummingbot/hummingbot
conda env create -f setup/environment.yml
./start
```

### Підключення до Binance

```bash
hummingbot> connect binance
Enter your Binance API key: ***
Enter your Binance secret key: ***
```

### Запуск стратегії

```bash
hummingbot> create --script triangular_arb.py
hummingbot> start
```

### Paper trading

```bash
hummingbot> paper_trade   # безпечне тестування без реальних коштів
```

---

## Слайд 5 — Що ми будуємо

### Roadmap

```
[Phase 1] Збір метрик
  └── Підключення до Binance (REST/WS)
  └── Polling пар: BTC/USDT, ETH/USDT, ETH/BTC кожні N сек
  └── Зберігання в SQLite: timestamp, pair, bid, ask

[Phase 2] Перевірка прибутковості
  └── Завантаження останніх цін з БД
  └── Розрахунок implied rate для трикутника
  └── Логування можливостей (spread > threshold + fees)

[Phase 3] Виконання (майбутнє)
  └── Автоматичне виставлення ордерів через Hummingbot
  └── Round-trip моніторинг + звітність
```

### Технологічний стек

| Компонент | Технологія |
|-----------|-----------|
| Підключення до біржі | Hummingbot connector / Binance REST API |
| Зберігання даних | SQLite (`metrics.db`) |
| Мова | Python 3.10+ |
| Планувальник | asyncio |

---

## Слайд 6 — Демо структура коду

```
bot-1/
├── main.py                  # точка входу, запуск event loop
├── metrics/
│   └── collector.py         # збір і збереження цін з Binance
├── arbitrage/
│   └── checker.py           # перевірка прибутковості трикутника
└── metrics.db               # SQLite база (автоствоюється)
```

---

## Слайд 7 — Висновок

- Hummingbot — зрілий інструмент для автоматизованої торгівлі
- Низький поріг входу: конфіги + готові стратегії
- Розширюваний: власні скрипти на Python
- Наш план: metrics → profitability check → live execution
- Наступний крок: запустити збір даних і подивитися на реальні спреди

**Питання?**
