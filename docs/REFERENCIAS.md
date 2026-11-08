# Referencias e diferencial do NexPrice

Projetos parecidos (open source e privados), o diferencial do NexPrice e o que melhorar com base neles. Pesquisa de 2026-11-08; verifique cada projeto antes de usar.

## Parecidos

### Open source
- **PriceBuddy** (jez500): self-hosted, compara precos entre lojas, grafico de tendencia e alertas (email, Telegram, Discord, ntfy).
- **changedetection.io**: monitora mudanca em qualquer pagina, com alertas e automacao de navegador; Apache 2.0. Bom motor de "vigiar pagina".
- **Discount Bandit**: price tracker multiusuario self-hosted.
- **Scrapy**: framework de scraping (um spider por site).
- Servidores **MCP de preco** (BestPrice, Forage, Amazon Product Search) que ja conectam no Claude.

### Privados / fechados
- **Keepa**, **CamelCamelCamel**: historico de preco da Amazon (referencias classicas).
- **Honey**, **ShopSavvy**, **idealo**, **Google Shopping**: comparadores/cupons fechados.

## Nosso diferencial
- **Foco em desmascarar desconto falso**: comparamos o preco atual com a mediana do periodo ANTES da alta recente (nao com o pico inflado). Esse "desconto_real" e o nucleo e ja esta implementado e testado.
- **Varias categorias no mesmo motor**: produtos, PCs novos/usados, imoveis, leiloes (Caixa/governo/bancos), cupons (issues #1 e #2).
- **MCP nativo**: nasce conectavel ao Claude e ao NexHub, nao so um app isolado.
- **Integra com o ecossistema**: Nextor captura links e avisa; askdash faz os graficos de historico.
- **Etica explicita**: preferir API/feed oficial, respeitar robots.txt e rate limit, nunca burlar captcha (casa com a politica do portfolio).

## O que melhorar aprendendo com eles
- **Historico longo e grafico** (Keepa/CamelCamel): guardar serie longa e mostrar grafico bonito (via askdash) e previsao de "vale a pena".
- **Muitos conectores** (idealo/Google Shopping): priorizar os sites com API/feed oficial primeiro, como o PriceBuddy faz, e so depois scraping.
- **Alertas ricos** (PriceBuddy): multiplos canais e regras por item (ja planejado via Nextor).
- **Reusar changedetection.io/Scrapy** como camada de coleta em vez de reinventar spiders.
- **Comunidade de precos**: historico compartilhado (anonimo) deixa o "desconto_real" mais forte, como os grandes tem.

## Sources
- https://www.alternativeto.net/software/pricebuddy/about/
- https://github.com/dgtlmoon/changedetection.io
- https://mcpservers.org/th/servers/thebestco/bestprice-mcp
- https://selfhostyourself.com/alternative-to/keepa
- https://shopsavvy.com/data/documentation/recipe-claude-code.md
