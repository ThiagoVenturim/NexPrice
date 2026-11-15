"""Tests for SQLite and generic SQLAlchemy storage, DB_URL config and MCP tools."""

from datetime import datetime, timedelta

from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import StaticPool

from nexprice.cli import main as cli_main
from nexprice.mcp_server import desconto_real, historico_preco
from nexprice.models import Offer, PriceObservation, Product
from nexprice.storage import Store, load_env_db_url, resolve_db_url


def _fill(store: Store) -> None:
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


def test_sqlalchemy_generic_engine_smoke():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with Store(engine=engine) as store:
        tables = set(inspect(store.engine).get_table_names())
        assert {"products", "offers", "observations"}.issubset(tables)

        # Upsert product, offer and observation (including characters that would break unparameterized SQL)
        store.add_product(Product("p'1;--", "Monitor 27' IPS", "pc", "nota inicial"))
        store.add_product(Product("p'1;--", "Monitor 27' 4K", "pc", "nota atualizada"))
        store.add_offer(Offer("p'1;--", "loja-a", "https://example.com/a", "BRL"))
        store.add_offer(Offer("p'1;--", "loja-a", "https://example.com/a2", "USD"))

        t0 = datetime(2026, 11, 1, 10, 0, 0)
        store.record(PriceObservation("p'1;--", "loja-a", 1500.0, t0, available=True))
        store.record(PriceObservation("p'1;--", "loja-a", 1399.5, t0, available=False))
        store.record(PriceObservation("p'1;--", "loja-b", 1450.0, t0, available=True))

        hist_all = store.history("p'1;--")
        assert len(hist_all) == 2

        hist_a = store.history("p'1;--", site="loja-a")
        assert len(hist_a) == 1
        assert hist_a[0].price == 1399.5
        assert hist_a[0].available is False


def test_db_url_from_dotenv_and_env(tmp_path, monkeypatch):
    monkeypatch.delenv("DB_URL", raising=False)
    db_file = tmp_path / "from_dotenv.db"
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        f"# comment\nDB_URL='sqlite+pysqlite:///{db_file.as_posix()}'\n",
        encoding="utf-8",
    )

    loaded = load_env_db_url(dotenv)
    assert loaded == f"sqlite+pysqlite:///{db_file.as_posix()}"

    with Store(env_file=dotenv) as store:
        _fill(store)

    # Environment variable takes precedence over .env file
    env_db = tmp_path / "from_env.db"
    monkeypatch.setenv("DB_URL", f"sqlite+pysqlite:///{env_db.as_posix()}")
    assert resolve_db_url(env_file=dotenv) == f"sqlite+pysqlite:///{env_db.as_posix()}"

    # Normalization of postgres:// scheme to SQLAlchemy psycopg driver
    assert (
        resolve_db_url("postgres://u:p@localhost:5432/nexprice")
        == "postgresql+psycopg://u:p@localhost:5432/nexprice"
    )


def test_cli_uses_db_url_when_flag_omitted(tmp_path, monkeypatch, capsys):
    db_file = tmp_path / "cli.db"
    monkeypatch.setenv("DB_URL", f"sqlite+pysqlite:///{db_file.as_posix()}")
    with Store() as store:
        _fill(store)

    rc = cli_main(["assess", "--product", "p1"])
    assert rc == 0
    captured = capsys.readouterr()
    assert captured.out.strip() != ""


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
