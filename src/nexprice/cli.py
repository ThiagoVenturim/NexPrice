"""Small CLI for NexPrice (offline-friendly)."""

from __future__ import annotations

import argparse
import sys

from nexprice.analysis import assess_discount
from nexprice.storage import Store


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="nexprice", description="Track prices and spot fake discounts."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_assess = sub.add_parser(
        "assess", help="Assess a product's current price against its history."
    )
    p_assess.add_argument("--db", required=True)
    p_assess.add_argument("--product", required=True)
    p_assess.add_argument("--site", default=None)

    args = parser.parse_args(argv)

    if args.cmd == "assess":
        store = Store(args.db)
        hist = store.history(args.product, args.site)
        if not hist:
            print("sem historico para esse produto")
            return 4
        verdict = assess_discount(hist)
        print(verdict.reason)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
