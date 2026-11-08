"""SQLite storage for products, offers and price history."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from nexprice.models import Offer, PriceObservation, Product

_SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY, title TEXT NOT NULL, category TEXT NOT NULL, notes TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS offers (
    product_id TEXT NOT NULL, site TEXT NOT NULL, url TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'BRL',
    PRIMARY KEY (product_id, site),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS observations (
    product_id TEXT NOT NULL, site TEXT NOT NULL, price REAL NOT NULL,
    at TEXT NOT NULL, available INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (product_id, site, at)
);
CREATE INDEX IF NOT EXISTS obs_by_product ON observations (product_id, at);
"""


class Store:
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.conn = sqlite3.connect(str(path))
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(_SCHEMA)
        self.conn.commit()

    def add_product(self, product: Product) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO products (id, title, category, notes) VALUES (?, ?, ?, ?)",
            (product.id, product.title, product.category, product.notes),
        )
        self.conn.commit()

    def add_offer(self, offer: Offer) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO offers (product_id, site, url, currency) VALUES (?, ?, ?, ?)",
            (offer.product_id, offer.site, offer.url, offer.currency),
        )
        self.conn.commit()

    def record(self, obs: PriceObservation) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO observations (product_id, site, price, at, available) "
            "VALUES (?, ?, ?, ?, ?)",
            (obs.product_id, obs.site, obs.price, obs.at.isoformat(), int(obs.available)),
        )
        self.conn.commit()

    def history(self, product_id: str, site: str | None = None) -> list[PriceObservation]:
        if site is None:
            rows = self.conn.execute(
                "SELECT product_id, site, price, at, available FROM observations "
                "WHERE product_id = ? ORDER BY at",
                (product_id,),
            )
        else:
            rows = self.conn.execute(
                "SELECT product_id, site, price, at, available FROM observations "
                "WHERE product_id = ? AND site = ? ORDER BY at",
                (product_id, site),
            )
        return [
            PriceObservation(r[0], r[1], r[2], datetime.fromisoformat(r[3]), bool(r[4]))
            for r in rows.fetchall()
        ]

    def close(self) -> None:
        self.conn.close()
