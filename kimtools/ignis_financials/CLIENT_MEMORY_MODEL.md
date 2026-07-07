# IGNIS Client Memory Model

## Purpose

IGNIS is a multi-client financial tool. It must keep each client's portfolio,
ledger, reporting style and movement history isolated from Kim's general memory
and from every other client.

The first active client is `sr_eli`. Future clients must get their own client
folder, manifest and ledger files before any portfolio work begins.

## Non-Negotiable Rule

Portfolio truth belongs only to IGNIS.

Do not store portfolio state in general Kim memory, CRM notes, ClickUp tasks,
WhatsApp chat summaries or free-form transcripts. Those sources can provide
evidence, but the official state exists only after a structured IGNIS event is
written to the client ledger or current runtime override.

## Client Registry

Portable registry:

```text
/Users/dryehoshuapython/Documents/BIFROST/MEMORY/IGNIS_FINANCIALS/clients/client_registry.json
```

Each client entry must define:

- `client_id`: stable slug, for example `sr_eli`.
- `display_name`: human-readable name.
- `status`: `active`, `paused` or `archived`.
- `portfolio_ids`: one or more portfolio slugs.
- `canonical_runtime_sources`: live runtime files used by Kim Live.
- `canonical_memory_sources`: portable BIFROST files for migration.
- `legacy_compatible_sources`: old paths that can be read as evidence.
- `reporting_rules`: client-specific language, format and delivery rules.

## Per-Client Folder

Required folder shape:

```text
MEMORY/IGNIS_FINANCIALS/clients/<client_id>/
  README.md
  client_manifest.json
  ledger_events.jsonl
  funding_events.jsonl
  positions.jsonl
  snapshots.jsonl
  reporting_rules.md
  whatsapp_delivery.jsonl
  audit/
  attachments/
```

For legacy clients, a manifest may point to existing paths instead of moving
files. Do not move established runtime files unless the tool code has been
updated and tested.

## Sr. Eli Canonical Context

Client id:

```text
sr_eli
```

Current live state is still read from:

```text
/Users/dryehoshuapython/.kim_live/context/portfolio_report_overrides.json
/Users/dryehoshuapython/.kim_live/portfolio_ledger.sqlite
```

Portable client manifest:

```text
/Users/dryehoshuapython/Documents/BIFROST/MEMORY/IGNIS_FINANCIALS/clients/sr_eli/client_manifest.json
```

Existing portable portfolio folder:

```text
/Users/dryehoshuapython/Documents/BIFROST/MEMORY/IGNIS_FINANCIALS/portfolios/clientes/manejo_de_portafolios/sr_eli_2026
```

Legacy/compatibility folder:

```text
/Users/dryehoshuapython/Documents/BIFROST/MEMORY/portfolios/ignis_stock_financials/clientes/manejo_de_portafolios/sr_eli_2026
```

Runtime memory folder:

```text
/Users/dryehoshuapython/.kim_live/MEMORY/portfolios/ignis_stock_financials/clientes/manejo_de_portafolios/sr_eli_2026
```

These folders are not interchangeable. The manifest declares which one is live,
which one is portable and which one is legacy evidence.

## Access Sequence

Before an agent reads or writes a portfolio:

1. Resolve the client through `client_registry.json`.
2. Read that client's `client_manifest.json`.
3. Read current runtime override/ledger for live state.
4. Read client reporting rules.
5. Use IGNIS tool actions for previews, writes and sends.
6. Record the result in the client's ledger/audit trail.

If the client cannot be resolved, stop and ask for the client identity. Never
fall back to another client's portfolio.

## Write Contract

Every portfolio mutation must become a structured event:

- `funding_received`
- `credit_covered`
- `order_created`
- `order_updated`
- `order_executed`
- `order_consolidated`
- `position_closed`
- `fee_recorded`
- `realized_pnl_recorded`
- `report_sent`
- `manual_correction`

Each event must include:

- `event_id`
- `client_id`
- `portfolio_id`
- `occurred_at`
- `source`
- `requested_by`
- `confirmed_by`
- `before`
- `after`
- `evidence`
- `tool_result`

## Reporting Contract

Client-facing reports must use the client's reporting rules, not a generic
portfolio prompt. For Sr. Eli:

- Use `refuerzo`, not `expansion`.
- Keep visible order ids compact as `A1...An`.
- Show the structured `Balance de Credito` at the end of full reports.
- Do not show removed/closed positions as active.
- Pending-on-credit orders stay pending until execution is explicitly confirmed.

## Migration Contract

When Kim moves to another machine or a new project:

1. Copy the BIFROST folder.
2. Open `kimtools/IGNIS_FINANCIALS/README.md`.
3. Open this file.
4. Open `clients/client_registry.json`.
5. Open the target client's manifest.
6. Reconnect runtime secrets and provider credentials.
7. Validate with a read-only `whatsapp_preview` before any send or write.
