"""Pluggable SQLAlchemy storage for products, offers and price history.

Defaults to local SQLite (zero configuration) and supports any SQLAlchemy-compatible
database URL configured via ``DB_URL`` in the environment or ``.env`` file (for example
``sqlite:///...``, ``postgresql+psycopg://...``, ``mysql+pymysql://...``,
``mssql+pyodbc://...``).
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import (
    Column,
     Engine,
    Float,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    event,
    text,
)
from sqlalchemy.engine import URL
from sqlalchemy.pool import StaticPool

from nexprice.models import Offer, PriceObservation, Product

DEFAULT_SQLITE_PATH = "nexprice.db"

metadata = MetaData()

products_table = Table(
    "products",
    metadata,
    Column("id", String(255), primary_key=True),
    Column("title", Text, nullable=False),
    Column("category", String(100), nullable=False),
    Column("notes", Text, nullable=False, server_default=""),
)

offers_table = Table(
    "offers",
    metadata,
    Column(
        "product_id",
        String(255),
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    Column("site", String(255), primary_key=True, nullable=False),
    Column("url", Text, nullable=False),
    Column("currency", String(16), nullable=False, server_default="BRL"),
)

observations_table = Table(
    "observations",
    metadata,
    Column("product_id", String(255), primary_key=True, nullable=False),
    Column("site", String(255), primary_key=True, nullable=False),
    Column("price", Float, nullable=False),
    Column("at", String(64), primary_key=True, nullable=False),
    Column("available", Integer, nullable=False, server_default="1"),
    Index("obs_by_product", "product_id", "at"),
)


def load_env_db_url(env_file: str | Path | None = ".env") -> str | None:
    """Read ``DB_URL`` from process environment or from a local ``.env`` file."""
    env_val = os.environ.get("DB_URL", "").strip()
    if env_val:
        return env_val
    if env_file is None:
        return None
    path = Path(env_file)
    if not path.is_file():
        return None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        key, sep, value = line.partition("=")
        if sep and key.strip() == "DB_URL":
            cleaned = value.strip().strip("'").strip('"').strip()
            if cleaned:
                return cleaned
    return None


def resolve_db_url(
    target: str | Path | None = None,
    *,
    env_file: str | Path | None = ".env",
) -> str:
    """Resolve a path, SQLAlchemy URL or ``DB_URL`` setting into a SQLAlchemy URL string."""
    raw = str(target).strip() if target is not None else ""
    if not raw:
        raw = load_env_db_url(env_file) or DEFAULT_SQLITE_PATH

    if raw == ":memory:":
        return "sqlite+pysqlite:///:memory:"

    if "://" in raw:
        if raw.startswith("postgres://"):
            return "postgresql+psycopg://" + raw[len("postgres://") :]
        return raw

    db_path = Path(raw).expanduser().resolve()
    return URL.create("sqlite+pysqlite", database=str(db_path)).render_as_string(
        hide_password=False
    )


def _enable_sqlite_foreign_keys(dbapi_connection: Any, _connection_record: Any) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


def build_engine(
    target: str | Path | None = None,
    *,
    env_file: str | Path | None = ".env",
) -> Engine:
    """Build a SQLAlchemy ``Engine`` for the given target or configured ``DB_URL``."""
    url = resolve_db_url(target, env_file=env_file)
    kwargs: dict[str, Any] = {}
    if url.startswith("sqlite"):
        if ":memory:" in url:
            kwargs["connect_args"] = {"check_same_thread": False}
            kwargs["poolclass"] = StaticPool
        engine = create_engine(url, **kwargs)
        event.listen(engine, "connect", _enable_sqlite_foreign_keys)
        return engine
    return create_engine(url, pool_pre_ping=True)


class Store:
    """Database-agnostic store backed by SQLAlchemy Core and parameterized queries."""

    def __init__(
        self,
        path: str | Path | None = None,
        *,
        engine: Engine | None = None,
        env_file: str | Path | None = ".env",
    ) -> None:
        if engine is not None:
            self.engine = engine
            self.url = engine.url.render_as_string(hide_password=False)
            if self.engine.dialect.name == "sqlite":
                event.listen(self.engine, "connect", _enable_sqlite_foreign_keys)
        else:
            self.url = resolve_db_url(path, env_file=env_file)
            self.engine = build_engine(self.url, env_file=env_file)
        metadata.create_all(self.engine, checkfirst=True)

    def __enter__(self) -> Store:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def add_product(self, product: Product) -> None:
        with self.engine.begin() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM products WHERE id = :id"),
                {"id": product.id},
            ).scalar()
            params = {
                "id": product.id,
                "title": product.title,
                "category": product.category,
                "notes": product.notes,
            }
            if exists:
                conn.execute(
                    text(
                        "UPDATE products SET title = :title, category = :category, "
                        "notes = :notes WHERE id = :id"
                    ),
                    params,
                )
            else:
                conn.execute(
                    text(
                        "INSERT INTO products (id, title, category, notes) "
                        "VALUES (:id, :title, :category, :notes)"
                    ),
                    params,
                )

    def add_offer(self, offer: Offer) -> None:
        with self.engine.begin() as conn:
            exists = conn.execute(
                text(
                    "SELECT 1 FROM offers "
                    "WHERE product_id = :product_id AND site = :site"
                ),
                {"product_id": offer.product_id, "site": offer.site},
            ).scalar()
            params = {
                "product_id": offer.product_id,
                "site": offer.site,
                "url": offer.url,
                "currency": offer.currency,
            }
            if exists:
                conn.execute(
                    text(
                        "UPDATE offers SET url = :url, currency = :currency "
                        "WHERE product_id = :product_id AND site = :site"
                    ),
                    params,
                )
            else:
                conn.execute(
                    text(
                        "INSERT INTO offers (product_id, site, url, currency) "
                        "VALUES (:product_id, :site, :url, :currency)"
                    ),
                    params,
                )

    def record(self, obs: PriceObservation) -> None:
        at_iso = obs.at.isoformat()
        with self.engine.begin() as conn:
            exists = conn.execute(
                text(
                    "SELECT 1 FROM observations "
                    "WHERE product_id = :product_id AND site = :site AND at = :at"
                ),
                {"product_id": obs.product_id, "site": obs.site, "at": at_iso},
            ).scalar()
            params = {
                "product_id": obs.product_id,
                "site": obs.site,
                "price": float(obs.price),
                "at": at_iso,
                "available": int(obs.available),
            }
            if exists:
                conn.execute(
                    text(
                        "UPDATE observations SET price = :price, available = :available "
                        "WHERE product_id = :product_id AND site = :site AND at = :at"
                    ),
                    params,
                )
            else:
                conn.execute(
                    text(
                        "INSERT INTO observations (product_id, site, price, at, available) "
                        "VALUES (:product_id, :site, :price, :at, :available)"
                    ),
                    params,
                )

    def history(self, product_id: str, site: str | None = None) -> list[PriceObservation]:
        with self.engine.connect() as conn:
            if site is None:
                rows = conn.execute(
                    text(
                        "SELECT product_id, site, price, at, available FROM observations "
                        "WHERE product_id = :product_id ORDER BY at"
                    ),
                    {"product_id": product_id},
                ).fetchall()
            else:
                rows = conn.execute(
                    text(
                        "SELECT product_id, site, price, at, available FROM observations "
                        "WHERE product_id = :product_id AND site = :site ORDER BY at"
                    ),
                    {"product_id": product_id, "site": site},
                ).fetchall()
        return [
            PriceObservation(
                r[0], r[1], float(r[2]), datetime.fromisoformat(r[3]), bool(r[4])
            )
            for r in rows
        ]

    def close(self) -> None:
        self.engine.dispose()
