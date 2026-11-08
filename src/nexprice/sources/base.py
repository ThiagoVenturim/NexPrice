"""Base interface for a price source."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class SourceResult:
    site: str
    url: str
    price: float | None
    currency: str
    available: bool
    title: str = ""


@runtime_checkable
class PriceSource(Protocol):
    """A source knows how to read the current price of one offer page.

    Implementations must respect robots.txt and rate limits, only fetch pages the user
    asked for, and prefer an official API over scraping when the site offers one.
    """

    site: str

    def fetch(self, url: str) -> SourceResult:  # pragma: no cover - interface
        ...
