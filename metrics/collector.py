import asyncio
import sqlite3
import time
from urllib.request import urlopen, Request
import json

DB_PATH = "metrics.db"
BINANCE_API = "https://api.binance.com/api/v3/ticker/bookTicker?symbol="
PAIRS = ["BTCUSDT", "ETHUSDT", "ETHBTC"]
POLL_INTERVAL = 5  # seconds


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            pair      TEXT    NOT NULL,
            bid       REAL    NOT NULL,
            ask       REAL    NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pair_ts ON prices (pair, timestamp)")
    conn.commit()


def fetch_ticker(symbol: str) -> dict:
    req = Request(BINANCE_API + symbol, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=5) as resp:
        return json.loads(resp.read())


def save_ticker(conn: sqlite3.Connection, symbol: str, bid: float, ask: float) -> None:
    conn.execute(
        "INSERT INTO prices (timestamp, pair, bid, ask) VALUES (?, ?, ?, ?)",
        (int(time.time()), symbol, bid, ask),
    )
    conn.commit()


async def collect_once(conn: sqlite3.Connection) -> None:
    for symbol in PAIRS:
        try:
            data = fetch_ticker(symbol)
            bid = float(data["bidPrice"])
            ask = float(data["askPrice"])
            save_ticker(conn, symbol, bid, ask)
            print(f"{symbol:10s}  bid={bid:.8f}  ask={ask:.8f}")
        except Exception as exc:
            print(f"[ERROR] {symbol}: {exc}")


async def run(poll_interval: int = POLL_INTERVAL) -> None:
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    print(f"Collecting metrics every {poll_interval}s. DB: {DB_PATH}\n")
    try:
        while True:
            print(f"--- {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
            await collect_once(conn)
            await asyncio.sleep(poll_interval)
    finally:
        conn.close()
