# IGNIS FINANCIALS Tool

## Purpose

`ignis_financials` is the portfolio and client-reporting tool for Kim Live, Ignis Financials and the future Cosmos module. It exists so Kim and any future AI agent can operate the Sr. Eli portfolio through one strict contract instead of reconstructing financial truth from chat history.

The tool is intentionally conservative: the structured ledger and override are the source of truth. Conversations, WhatsApp text and memory cards are evidence only after they are converted into a tool action and committed.

## Source Of Truth

Runtime source:

- `/Users/dryehoshuapython/.kim_live/server.py`
- `/Users/dryehoshuapython/.kim_live/context/portfolio_report_overrides.json`
- `/Users/dryehoshuapython/.kim_live/portfolio_ledger.sqlite`
- `/Users/dryehoshuapython/.kim_live/kim_paper_broker.py`

Repository source:

- `/Users/dryehoshuapython/Documents/BIFROST/repos/KimOne/kim_live/server.py`
- `/Users/dryehoshuapython/Documents/BIFROST/repos/KimOne/kim_live/context/portfolio_report_overrides.json`
- `/Users/dryehoshuapython/Documents/BIFROST/repos/KimOne/kimtools/ignis_financials`

Memory roots:

- `/Users/dryehoshuapython/Documents/BIFROST/MEMORY/IGNIS_FINANCIALS`
- `/Users/dryehoshuapython/Documents/BIFROST/MEMORY/portfolios/ignis_stock_financials`

## Tool Entry Point

Use:

```bash
python3 kimtools/ignis_financials/ignis_portfolio_tool.py <action> '<json-parameters>'
```

The wrapper loads the Kim Live runtime and calls:

```python
server.portfolio_cli(action, parameters)
```

Do not copy portfolio calculations into a second script. The wrapper is a stable interface; `server.portfolio_cli` remains the execution engine until Cosmos extracts the module.

## Current Standard

Current live standard: `KIM-0148`.

Rules:

- Sr. Eli reports contain `30` visible live orders after LAB closed:
  - `15` covered active positions.
  - `0` bought-on-credit positions pending coverage.
  - `15` pending-on-credit orders.
- LAB is closed accounting-only: entry `10.044`, stop loss `8.54`, net P/L `-291.13 USD`.
- Active bought-on-credit positions are now covered after the `2026-07-01` funding.
- Pending orders remain pending on credit until execution.
- Full portfolio reports must append the structured `Balance de Crédito` at the end.
- Long WhatsApp balance messages must be split into safe chunks and each chunk must be confirmed delivered.

## Skill Entry Point

Every agent that touches Ignis ledger, Sr. Eli portfolio, credit balance, funding, reports, WhatsApp portfolio delivery or market/fundamental reporting must first read:

```text
/Users/dryehoshuapython/Documents/BIFROST/kimtools/IGNIS_FINANCIALS/skills/SKILL.md
```

Repository mirror:

```text
/Users/dryehoshuapython/Documents/BIFROST/repos/KimOne/kimtools/ignis_financials/skills/SKILL.md
```

This skill is the operating contract for the tool. It separates Ignis financial state from Kim's general memory and prevents agents from rebuilding the portfolio from old conversation text.

## Actions

### Read / Preview

- `status`: tool and module status.
- `summary`: structured portfolio summary.
- `client_report`: client-ready report without sending.
- `whatsapp_preview`: exact WhatsApp messages before sending.
- `fundamental_report`: market/fundamental report for the portfolio.
- `fundamental_history`: stored fundamental reports.

### Write / Accounting

- `record_funding`: record funding, withdrawal or conversion.
- `execute_pending_order`: mark a pending order as executed.
- `sell_position`: close a position and register realized P/L.
- `aggregate_order`: consolidate compatible orders after confirmation.
- `set_position`: controlled manual position correction.

### Send

- `send_whatsapp_report`: send selected portfolio lines and, when scope is `all`, append the structured `Balance de Crédito`.

Recommended scopes:

- `all`: full portfolio plus Balance de Crédito.
- `accounting` + `accounting_section=balance`: Balance de Crédito only.
- `range`: a requested range such as `A13-A25`.
- `ids`: specific lines.
- `pending`: pending orders only.
- `active`: active positions only.

## Required Success Evidence

Kim may only say `enviado`, `actualizado`, `registrado` or `completado` when the tool returns verifiable evidence.

For portfolio/accounting writes:

- `ok=true`
- `provider="portfolio"`
- expected `action`
- changed ledger/override state, event id, change id or final transaction id

For WhatsApp sends:

- `ok=true`
- `execution_state="delivered"`
- `delivered_count == message_count`
- no `errors`

If Twilio returns only `queued`, `sent` or partial delivery, Kim must say `aceptado/pendiente de verificación`, not `entregado`.

## Balance De Crédito Standard

Every full Sr. Eli portfolio report must close with:

```text
Balance de Crédito

Fondeos totales: `... USD` / `... MXN`
Profit actual generado: `... USD`
Total neto considerado: `... USD`
Total en firme asignado: `... USD`
Saldo disponible: `... USD`

Resumen de cuenta de crédito

1. Órdenes Compradas Cubiertas Completas
2. Órdenes Compradas A Crédito
3. Órdenes Pendientes A Crédito

Resumen
Monto en firme asignado
Saldo disponible
Crédito por cubrir
Crédito pendiente por ejecutar
Crédito total actual
```

Current canonical values are read from `accounting.report_protocol` in `portfolio_report_overrides.json`; do not hardcode them in prompts.

## Safety Rules

- Never reconstruct the portfolio from old conversations, backups or memory summaries.
- Never report LAB as live or pending after `KIM-0139`.
- Never cover pending orders with funding until they execute.
- Never send all 30 lines again when the doctor asks only for a balance, correction, range or selection.
- Never say Twilio delivered a message unless Twilio confirms `delivered` or `read`.
- Never mutate accounting without an explicit doctor instruction or a confirmed tool action.
- Do not use Codex automation as the operating clock for this module. Kim Live local scheduler is responsible for daily runs.

## Daily Report

Daily Sr. Eli report expectation:

- Local time: `09:00 America/Mexico_City`.
- Refresh prices.
- Validate prices.
- Send full portfolio to the doctor’s Dubai WhatsApp.
- Append structured Balance de Crédito.
- Store send evidence and delivery status.

If any price is unvalidated, block the daily report and notify the doctor with the symbols that failed.

## Examples

Preview full report:

```bash
python3 kimtools/ignis_financials/ignis_portfolio_tool.py whatsapp_preview '{"send_scope":"all","force_refresh_prices":true}'
```

Send only Balance de Crédito:

```bash
python3 kimtools/ignis_financials/ignis_portfolio_tool.py send_whatsapp_report '{"send_scope":"accounting","accounting_section":"balance","force_refresh_prices":false}'
```

Record funding:

```bash
python3 kimtools/ignis_financials/ignis_portfolio_tool.py record_funding '{"id":"funding_YYYY_MM_DD","type":"funding","amount_mxn":50000,"amount_usd":2844,"concept":"Cobertura de crédito","occurred_at":"2026-06-23","confirm":true}'
```

Close a position:

```bash
python3 kimtools/ignis_financials/ignis_portfolio_tool.py sell_position '{"symbol":"LAB","entry_price":10.044,"sell_price":8.54,"invested_usd":1800,"confirm":true}'
```

## Cosmos Extraction Notes

Future Cosmos module boundaries:

- `portfolio_core`: ledger, positions, state transitions.
- `price_validation`: market providers and freshness rules.
- `client_reporting`: client-ready WhatsApp/report formatting.
- `credit_accounting`: fondeos, credit coverage, P/L, fee policy.
- `paper_broker`: simulated orders and alert integration.
- `scheduler_local_clock`: daily and timed jobs independent of Codex.
- `provider_connectors`: Twilio, WhatsApp, TradingView, CoinGecko/CoinMarketCap.
