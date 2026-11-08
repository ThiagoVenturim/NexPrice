# NexPrice

Find the best price across sites and expose fake discounts through real price history,
exposed over MCP so Claude and NexHub can use it.

Status: early development.

## Why

Looking for an item across many sites takes time. Around big sale events a store often
raises the price shortly before and brings it back to normal during the "sale", so the
advertised drop is not a real discount. NexPrice records the price history of each item
and judges the current price against the median of the period before the recent run-up,
not against the inflated peak.

## What it does

- Tracks a product across one or more offers (sites).
- Keeps a price history in SQLite.
- `assess_discount` / the `desconto_real` MCP tool classify the current price as a real
  discount, a suspicious (fake) one, or no discount.
- Exposes tools over MCP: `desconto_real`, `historico_preco` (more coming:
  `buscar_item`, `comparar_precos`, `criar_alerta`).

## Scope and ethics

Only fetch pages the user asked for. Respect robots.txt and rate limits. Prefer an
official price API or feed when a site offers one. Never bypass captchas. This follows
the portfolio's use policy: build to help people, never to harm.

## Install and test

```
python -m venv .venv
.venv/Scripts/pip install -e .[dev]
git config core.hooksPath .githooks
.venv/Scripts/python -m pytest
.venv/Scripts/ruff check .
python scripts/check_no_emoji.py
```

## Roadmap

- Real sources per site (built on changedetection.io / Scrapy patterns), starting with
  one or two sites plus an official-API source where available.
- Categories beyond general products: PCs (new and used), real estate, auctions, coupons.
- Charts of price history through askdash.
- Alerts and capture through Nextor; cards and control through NexHub.

See `docs/ARCHITECTURE.md`. Portuguese readme: `README.pt-BR.md`. License: MIT.
