"""Price sources: each site is a source that reads a public product page it was given.

Rules (see docs/ARCHITECTURE.md): only pages the user asked for; respect robots.txt and
rate limits; prefer official price APIs/feeds when available; never bypass captchas.
"""

from nexprice.sources.base import PriceSource, SourceResult

__all__ = ["PriceSource", "SourceResult"]
