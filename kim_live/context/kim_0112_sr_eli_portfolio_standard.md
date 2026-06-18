# KIM-0112 Sr Eli Portfolio Standard

Date: 2026-06-17 CST

This source note mirrors the BIFROST documentation for the Sr. Eli portfolio standard.

Implemented in Kim Live:

- `client_report` now returns structured `client_lines` for the WhatsApp-ready customer view.
- WhatsApp can compose `all`, `range`, `ids`, `symbols`, `state`, or `correction` scopes.
- `correction` requires an explicit selector and never falls back to sending the full portfolio.
- Balance is included by default only for full sends.
- Sensitive portfolio actions are confirmable: sell, execute pending, delete/remove, agglomerate/consolidate, split/separate.
- The confirmation modal sends `security_pin`, `security_phrase`, and `session_id`.
- Frontend portfolio panel has `Vista Cliente`, `Vista Tecnica`, and `Aglomeraciones`.
- Client lines are selectable, copyable, and can be sent by selected IDs or range.

Backend dry-runs passed:

- `client_report`: 21 client lines.
- `whatsapp_preview` range `A13-A21`: 9 messages, no balance.
- `whatsapp_preview` ids `A1,A3`: 2 messages.
- `correction` without ids/range/symbols: blocked.
- `send_whatsapp_report` dry-run supports range, pending state, and symbols.

Operational note:

The local Mac did not have `node`, so JS syntax was not checked with `node --check`; validate visually after runtime restart.
