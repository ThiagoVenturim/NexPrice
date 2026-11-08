# NexPrice

Acha o melhor preco em varios sites e desmascara desconto falso usando o historico real
de precos, exposto por MCP para o Claude e o NexHub usarem.

Status: em desenvolvimento inicial.

## Por que

Procurar um item em varios sites toma tempo. Perto de grandes promocoes, a loja costuma
subir o preco pouco antes e voltar ao normal durante a "promocao", entao a queda
anunciada nao e desconto de verdade. O NexPrice guarda o historico de cada item e julga
o preco atual contra a mediana do periodo antes da alta recente, nao contra o pico
inflado.

## O que faz

- Acompanha um produto em uma ou mais ofertas (sites).
- Guarda o historico de precos em SQLite.
- `assess_discount` / a ferramenta MCP `desconto_real` classificam o preco atual como
  desconto real, suspeito (falso) ou sem desconto.
- Expoe ferramentas por MCP: `desconto_real`, `historico_preco` (em breve: `buscar_item`,
  `comparar_precos`, `criar_alerta`).

## Escopo e etica

So acessa paginas que a pessoa pediu. Respeita robots.txt e limites de taxa. Prefere API
ou feed oficial de preco quando o site oferece. Nunca burla captcha. Segue a politica de
uso do portfolio: construir para ajudar, nunca para o mal.

## Instalar e testar

```
python -m venv .venv
.venv/Scripts/pip install -e .[dev]
git config core.hooksPath .githooks
.venv/Scripts/python -m pytest
.venv/Scripts/ruff check .
python scripts/check_no_emoji.py
```

## Roteiro

- Fontes reais por site (no estilo changedetection.io / Scrapy), comecando por um ou dois
  sites e uma fonte de API oficial onde houver.
- Categorias alem de produtos: PCs (novos e usados), imoveis, leiloes, cupons.
- Graficos de historico pelo askdash.
- Alertas e captura pelo Nextor; cartoes e controle pelo NexHub.

Ver `docs/ARCHITECTURE.md`. Licenca: MIT.
