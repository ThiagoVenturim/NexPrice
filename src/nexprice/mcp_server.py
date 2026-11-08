"""MCP server exposing NexPrice to Claude and NexHub.

Tools: buscar_item, comparar_precos, historico_preco, desconto_real, criar_alerta.
This module wires the tools to the core (analysis + storage). The MCP transport is
optional; if the `mcp` package is not installed, importing this module still works so
the core can be used directly.
"""

from __future__ import annotations

from nexprice.analysis import assess_discount
from nexprice.storage import Store


def desconto_real(db_path: str, product_id: str, site: str | None = None) -> dict:
    """Return whether the current price is a real discount or a suspicious one."""
    store = Store(db_path)
    try:
        hist = store.history(product_id, site)
        if not hist:
            return {"ok": False, "error": "sem historico"}
        v = assess_discount(hist)
        return {
            "ok": True,
            "current": v.current,
            "baseline_median": v.baseline_median,
            "is_real_discount": v.is_real_discount,
            "is_suspicious": v.is_suspicious,
            "reason": v.reason,
            "samples": v.sample_size,
        }
    finally:
        store.close()


def historico_preco(db_path: str, product_id: str, site: str | None = None) -> list[dict]:
    """Return the recorded price history for a product."""
    store = Store(db_path)
    try:
        return [
            {"site": o.site, "price": o.price, "at": o.at.isoformat(), "available": o.available}
            for o in store.history(product_id, site)
        ]
    finally:
        store.close()


def build_server():  # pragma: no cover - requires the optional mcp package
    """Build the MCP server. Call only when the `mcp` extra is installed."""
    from mcp.server.fastmcp import FastMCP

    server = FastMCP("nexprice")
    server.tool()(desconto_real)
    server.tool()(historico_preco)
    return server
