# IGNIS FINANCIALS Portfolio Skill

Use this skill whenever an agent works with Ignis Financials, Sr. Eli's portfolio, credit balances, pending orders, fills, sell/close actions, realized P/L, funding receipts, daily reports, fundamental reports or WhatsApp portfolio delivery.

## Non-Negotiable Contract

Financial truth is structured, not conversational.

Use this hierarchy:

1. Current runtime override and ledger.
2. IGNIS tool execution result.
3. Current-day operational memory.
4. Older chats, transcripts and WhatsApp as evidence only.

Never reconstruct the Sr. Eli portfolio from old chat text, memory summaries or WhatsApp snippets. Convert instructions into structured tool actions first.

## Canonical Paths

Runtime:

```text
/Users/dryehoshuapython/.kim_live/context/portfolio_report_overrides.json
/Users/dryehoshuapython/.kim_live/portfolio_ledger.sqlite
/Users/dryehoshuapython/.kim_live/kim_paper_broker.py
```

Repo:

```text
/Users/dryehoshuapython/Documents/BIFROST/repos/KimOne/kimtools/ignis_financials
/Users/dryehoshuapython/Documents/BIFROST/repos/KimOne/kim_live/context/portfolio_report_overrides.json
```

BIFROST memory:

```text
/Users/dryehoshuapython/Documents/BIFROST/MEMORY/IGNIS_FINANCIALS
/Users/dryehoshuapython/Documents/BIFROST/MEMORY/portfolios
```

## Tool Entry Point

From the KimOne repo:

```bash
python3 kimtools/ignis_financials/ignis_portfolio_tool.py <action> '<json>'
```

Important actions:

- `status`
- `summary`
- `client_report`
- `whatsapp_preview`
- `send_whatsapp_report`
- `fundamental_report`
- `record_funding`
- `execute_pending_order`
- `sell_position`
- `aggregate_order`
- `set_position`

Always preview before sending:

```bash
python3 kimtools/ignis_financials/ignis_portfolio_tool.py whatsapp_preview '{"send_scope":"all","force_refresh_prices":true}'
```

## Current Sr. Eli Standard

Current standard: `KIM-0148`.

The Sr. Eli portfolio currently has 30 visible live orders:

- 15 covered active positions.
- 0 bought-on-credit positions pending coverage.
- 15 pending-on-credit orders.

LAB is closed accounting-only after `KIM-0139`; never show LAB as live or pending.

Pending orders remain pending on credit until execution is explicitly confirmed by Dr. Yehoshua. Do not auto-fill pending paper orders simply because a market price crosses the limit when `no_auto_fill` or `requires_manual_fill_confirmation` is set.

## Current Final Pending Prices

Applied from WhatsApp in `KIM-0148`:

| Order | Price |
|---|---:|
| APT refuerzo | `0.504` |
| LUNC refuerzo | `0.0000522` |
| HYPE | `49.5` |
| SOL refuerzo | `54` |
| DOT refuerzo | `0.675` |
| FTT refuerzo | `0.18` |
| ZEC | `324` |
| WIF | `0.1107` |
| XLM | `0.1395` |
| AAVE | `68.67` |
| XRP refuerzo | `0.882` |
| HBAR refuerzo | `0.0603` |
| TRUMP refuerzo | `1.4742` |
| AVAX | `5.481` |
| WLD refuerzo | `0.315` |

## Balance De Crédito

Full reports must close with the structured `Balance de Crédito`.

Current shape:

- Fondeos totales.
- Profit actual generado.
- Total neto considerado.
- Total en firme asignado.
- Saldo disponible.
- Órdenes Compradas Cubiertas Completas.
- Órdenes Compradas A Crédito.
- Órdenes Pendientes A Crédito.
- Resumen.

Current pending-on-credit total: `27,000 USD`.

Do not use the phrase `pendientes de pago`; use `Órdenes Pendientes A Crédito`.

## WhatsApp Delivery

Default doctor WhatsApp target:

```text
whatsapp:+971585943726
```

Use `send_whatsapp_report` for portfolio report delivery. For a custom correction message, use the existing Twilio bridge, but still log what was sent.

Success evidence:

- Can say delivered only if Twilio status is `delivered` or `read`.
- If status is `sent`, `queued` or accepted-only, say pending verification.
- If `failed` or `undelivered`, report failure and error code.

For long portfolio reports:

- Send one line per message or safe chunks.
- Poll final Twilio status.
- Do not resend the whole portfolio when only a correction, range or balance is requested.

## Price And Root-9 Notes

Dr. Yehoshua sometimes requests prices aligned with digital root 9 as a `segula` / good-fortune rule.

When applying such prices:

1. Preserve the exact final price sent by the doctor if provided.
2. Record it as a structured pending-order price adjustment.
3. Do not execute any order.
4. Store a memory note under `MEMORY/IGNIS_FINANCIALS`.

## Before Any Write

1. Read current override/ledger.
2. Make a backup.
3. Apply only the requested structured changes.
4. Mirror runtime and repo override.
5. Validate with `whatsapp_preview`.
6. Commit repo changes.
7. Push if credentials work.
8. Leave a memory note under `MEMORY/IGNIS_FINANCIALS`.

## Red Flags

Stop and ask or inspect deeper if:

- The live order count changes unexpectedly.
- LAB appears as live/pending.
- Pending orders disappear from `Balance de Crédito`.
- A paper broker auto-fill appears without explicit doctor confirmation.
- WhatsApp says `sent` but not `delivered/read`.
- Kim claims action success without tool evidence.
