"""Core data models for NexPrice."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Product:
    """A thing the user wants to track, independent of where it is sold."""

    id: str
    title: str
    category: str = "produto"  # produto, pc, imovel, leilao, cupom
    notes: str = ""


@dataclass(frozen=True)
class Offer:
    """A product offered by one seller at one URL."""

    product_id: str
    site: str
    url: str
    currency: str = "BRL"


@dataclass(frozen=True)
class PriceObservation:
    """One price reading for an offer at a point in time."""

    product_id: str
    site: str
    price: float
    at: datetime
    available: bool = True
    extra: dict = field(default_factory=dict)
