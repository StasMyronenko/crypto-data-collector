import asyncio
import sys

from metrics.collector import run as run_collector
from arbitrage.checker import run_check


def usage() -> None:
    print("Usage: python main.py [collect|check]")
    print("  collect  — start polling Binance prices and saving to metrics.db")
    print("  check    — evaluate triangular arbitrage profitability from stored prices")


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "collect"

    if cmd == "collect":
        asyncio.run(run_collector())
    elif cmd == "check":
        run_check()
    else:
        usage()


if __name__ == "__main__":
    main()
