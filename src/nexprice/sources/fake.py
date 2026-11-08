"""A deterministic in-memory source for tests and demos (no network)."""

from __future__ import annotations

from nexprice.sources.base import SourceResult


class FakeSource:
    """Returns prices from a preset map. Used by tests and the offline demo."""

    site = "fake"

    def __init__(self, prices: dict[str, float]) -> None:
        self._prices = prices

    def fetch(self, url: str) -> SourceResult:
        price = self._prices.get(url)
        return SourceResult(
            site=self.site,
            url=url,
            price=price,
            currency="BRL",
            available=price is not None,
            title=url.rsplit("/", 1)[-1],
        )
