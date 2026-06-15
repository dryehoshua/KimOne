# KIM-0105 - Portfolio Manual Panel

Date: 2026-06-15

## Purpose

Kim Live now includes a manual control panel for the Sr. Eli portfolio inside the Paper Broker tab. The goal is to stop depending on Kim's natural-language interpretation for every correction.

## Current Canonical State

- A1 through A12 are active / in market.
- A13 and above are pending orders.
- The manual source of truth is `kim_live/context/portfolio_report_overrides.json`, mirrored to the runtime file in `.kim_live/context`.
- The panel edits that override file directly through `/api/portfolio`.

## New Portfolio API Actions

- `manual_orders`: lists editable manual entries.
- `normalize_manual_orders`: enforces A1-A12 as `active` and A13+ as `pending`.
- `update_manual_order`: edits an order entry, including entry price, amount, credit, symbol, label, state and source.
- `delete_manual_order`: removes a manual order entry.

## Frontend Controls

In the Paper Broker tab, the new `Portfolio Manual Sr. Eli` panel adds:

- `Normalizar estados`
- `Recargar porcentajes`
- `Copiar reporte`
- `Mandar WhatsApp`
- Per-order controls: `Copiar orden`, `Guardar edit`, `Eliminar`

## WhatsApp Delivery Rule

The portfolio WhatsApp sender now distinguishes:

- accepted by Twilio
- delivered/read by WhatsApp
- rejected/undelivered by WhatsApp

This avoids treating `queued` or `sent` as final delivery. The 2026-06-15 failed send to Dubai returned Twilio error `63016`, so future UI must show this as rejected rather than successful.

## Verification

- Backend syntax passes `python3 -m py_compile`.
- Frontend script passes Node `--check`.
- Runtime health reports Kim Live `1.5.76`.
- Authenticated `/api/portfolio manual_orders` reports 12 active and 9 pending.
- Authenticated `/api/portfolio client_report` generates 22 WhatsApp lines with zero unvalidated active symbols.
