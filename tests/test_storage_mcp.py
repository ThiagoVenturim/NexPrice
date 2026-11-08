"""Tests for storage round-trip and MCP tool functions."""

from datetime import datetime, timedelta

from nexprice.mcp_server import desconto_real, historico_preco
from nexprice.models import PriceObservation, Product
from nexprice.storage import Store


def _fill(store):
    store.add_product(Product("p1", "Caixa de som", "produto"))
    now = datetime(2026, 11, 8, 12, 0, 0)
    for d in (90, 60, 30):
        store.record(PriceObservation("p1", "loja", 100.0, now - timedelta(days=d)))
    store.record(PriceObservation("p1", "loja", 140.0, now - timedelta(days=5)))
    store.record(PriceObservation("p1", "loja", 100.0, now))


def test_storage_roundtrip():
    store = Store(":memory:")
    _fill(store)
    hist = store.history("p1")
    assert len(hist) == 5
    assert hist[0].price == 100.0
    store.close()


def test_mcp_desconto_real_flags_fake(tmp_path):
    db = str(tmp_path / "t.db")
    store = Store(db)
    _fill(store)
    store.close()
    out = desconto_real(db, "p1")
    assert out["ok"]
    assert out["is_suspicious"]
    assert not out["is_real_discount"]


def test_mcp_historico(tmp_path):
    db = str(tmp_path / "t.db")
    store = Store(db)
    _fill(store)
    store.close()
    rows = historico_preco(db, "p1")
    assert len(rows) == 5
