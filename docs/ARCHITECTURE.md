# NexPrice architecture

NexPrice tracks the price history of items across sites and judges whether a current
price is a real discount. It is a Python package exposed over MCP, reusing portfolio
patterns (and, later, `faccoder-core` for model-backed features).

## Modules (`src/nexprice/`)
- `models.py`: `Product`, `Offer`, `PriceObservation` (dataclasses).
- `storage.py`: `Store` over SQLite (products, offers, observations). Parameterized SQL
  only; never string-built queries.
- `analysis.py`: `assess_discount` -> `DiscountVerdict`. Judges the current price against
  the median of the period before the recent run-up (`spike_days`), so an inflated-then-
  "discounted" price is flagged `is_suspicious`.
- `sources/`: one `PriceSource` per site. `base.py` is the protocol; `fake.py` is the
  deterministic test/demo source. Real sources come later.
- `mcp_server.py`: MCP tools (`desconto_real`, `historico_preco`, ...). Importing works
  without the optional `mcp` package so the core is usable directly.
- `cli.py`: small offline CLI (`nexprice assess`).

## Data model (SQLite)
- `products(id, title, category, notes)`
- `offers(product_id, site, url, currency)` PK (product_id, site)
- `observations(product_id, site, price, at, available)` PK (product_id, site, at)

## The fake-discount rule
Given the history within `window_days`, split into a baseline (older than `spike_days`)
and the recent period. `baseline_median` is the honest reference. The current price is a
real discount when it is at least `min_drop` below `baseline_median`. It is suspicious
when the advertised drop against the recent peak is big but the price is still at or above
the baseline. This is the core value and must stay deterministic and tested.

## Sources: rules
Only fetch pages the user asked for. Respect robots.txt and rate limits. Prefer an
official price API or feed over scraping when the site offers one. Never bypass captchas.
Each source caches and throttles. Reuse changedetection.io / Scrapy patterns for the
scraping layer rather than reinventing.

## Integrations (planned)
- askdash: price-history charts (send rows to the askdash reporting engine).
- Nextor: capture ("track this link"), alerts through the user's chosen channels.
- NexHub: price-watch agents as cards; control and scheduling.
- faccoder-core: optional model-backed matching (same item across sites) and summaries.

## Categories
One engine, several domains via `Product.category`: produto, pc, imovel, leilao, cupom.
A category may add fields later (e.g. imovel: area, bairro) without changing the core.

## Testing
`pytest` offline, no network (the `fake` source and in-memory SQLite). The discount rule
has explicit cases: stable-then-drop (real), inflate-then-restore (suspicious), flat
(none), empty (error).
