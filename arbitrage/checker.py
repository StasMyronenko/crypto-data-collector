import sqlite3

DB_PATH = "metrics.db"
FEE_PER_LEG = 0.001  # Binance taker fee: 0.1%
TOTAL_FEES = 1 - (1 - FEE_PER_LEG) ** 3
MIN_PROFIT_THRESHOLD = 0.0005  # 0.05% minimum net profit


def get_latest_prices(conn: sqlite3.Connection) -> dict[str, dict]:
    """Return the most recent bid/ask for each pair."""
    rows = conn.execute("""
        SELECT pair, bid, ask FROM prices
        WHERE id IN (
            SELECT MAX(id) FROM prices GROUP BY pair
        )
    """).fetchall()
    return {row[0]: {"bid": row[1], "ask": row[2]} for row in rows}


def check_triangle(prices: dict[str, dict]) -> dict:
    """
    Triangle: USDT → BTC → ETH → USDT
      leg 1: buy  BTC  with USDT  → pay ask_BTCUSDT
      leg 2: buy  ETH  with BTC   → pay ask_ETHBTC
      leg 3: sell ETH  for  USDT  → receive bid_ETHUSDT
    """
    required = {"BTCUSDT", "ETHUSDT", "ETHBTC"}
    if not required.issubset(prices):
        return {"error": f"Missing pairs: {required - set(prices)}"}

    ask_btcusdt = prices["BTCUSDT"]["ask"]
    ask_ethbtc = prices["ETHBTC"]["ask"]
    bid_ethusdt = prices["ETHUSDT"]["bid"]

    # Starting with 1 USDT:
    btc_amount = 1.0 / ask_btcusdt
    eth_amount = btc_amount / ask_ethbtc
    usdt_back = eth_amount * bid_ethusdt

    gross_profit = usdt_back - 1.0
    net_profit = gross_profit - TOTAL_FEES
    profitable = net_profit > MIN_PROFIT_THRESHOLD

    return {
        "direction": "USDT→BTC→ETH→USDT",
        "gross_profit_pct": round(gross_profit * 100, 6),
        "fees_pct": round(TOTAL_FEES * 100, 4),
        "net_profit_pct": round(net_profit * 100, 6),
        "profitable": profitable,
    }


def check_reverse_triangle(prices: dict[str, dict]) -> dict:
    """
    Reverse triangle: USDT → ETH → BTC → USDT
      leg 1: buy  ETH  with USDT  → pay ask_ETHUSDT
      leg 2: sell ETH  for  BTC   → receive bid_ETHBTC
      leg 3: sell BTC  for  USDT  → receive bid_BTCUSDT
    """
    required = {"BTCUSDT", "ETHUSDT", "ETHBTC"}
    if not required.issubset(prices):
        return {"error": f"Missing pairs: {required - set(prices)}"}

    ask_ethusdt = prices["ETHUSDT"]["ask"]
    bid_ethbtc = prices["ETHBTC"]["bid"]
    bid_btcusdt = prices["BTCUSDT"]["bid"]

    eth_amount = 1.0 / ask_ethusdt
    btc_amount = eth_amount * bid_ethbtc
    usdt_back = btc_amount * bid_btcusdt

    gross_profit = usdt_back - 1.0
    net_profit = gross_profit - TOTAL_FEES
    profitable = net_profit > MIN_PROFIT_THRESHOLD

    return {
        "direction": "USDT→ETH→BTC→USDT",
        "gross_profit_pct": round(gross_profit * 100, 6),
        "fees_pct": round(TOTAL_FEES * 100, 4),
        "net_profit_pct": round(net_profit * 100, 6),
        "profitable": profitable,
    }


def run_check() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        prices = get_latest_prices(conn)
        if not prices:
            print("No price data in DB yet. Run the collector first.")
            return

        for result in [check_triangle(prices), check_reverse_triangle(prices)]:
            if "error" in result:
                print(f"[ERROR] {result['error']}")
                continue
            status = "PROFITABLE" if result["profitable"] else "not profitable"
            print(
                f"[{status}] {result['direction']}  "
                f"gross={result['gross_profit_pct']:+.4f}%  "
                f"fees={result['fees_pct']:.4f}%  "
                f"net={result['net_profit_pct']:+.4f}%"
            )
    finally:
        conn.close()
