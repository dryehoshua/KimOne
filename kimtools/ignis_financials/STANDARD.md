# IGNIS FINANCIALS Operating Standard

## Canonical Principle

Financial state is not conversational. It must be represented as structured events, positions and reports.

The hierarchy is:

1. Ledger / override JSON.
2. Tool execution result.
3. Current-day operational memory.
4. Older memory and conversation transcripts.

Older memory can explain why something happened, but it cannot override the ledger.

## Sr. Eli Report Standard

Every full portfolio report must include:

1. Active positions, ordered from largest loss to best result.
2. Pending orders after active positions.
3. Current validated price for every line.
4. Phrase: `Estamos por debajo...` or `Estamos en ganancia...`.
5. Structured `Balance de Crédito` as the final section.

The Balance de Crédito must include:

- Fondeos totales.
- Profit actual generado.
- Total neto considerado.
- Total en firme asignado.
- Saldo disponible.
- Órdenes Compradas Cubiertas Completas.
- Órdenes Compradas A Crédito.
- Órdenes Pendientes A Crédito.
- Summary values for credit and available balance.

## WhatsApp Standard

- Send portfolio lines individually.
- Split long balance messages into safe chunks.
- Verify Twilio status after sending.
- Report `delivered` only when Twilio status is `delivered` or `read`.
- If delivery is partial, report exactly which count delivered and do not claim success.

## Credit Standard

- Active positions can be covered by funding.
- Pending orders remain pending on credit until execution.
- Closed positions affect realized P/L and accounting, not live order count.
- LAB is closed after KIM-0139 and must not appear as live or pending.
- Current live standard is KIM-0148: 30 visible live orders, 15 covered active, 0 bought-on-credit pending coverage, 15 pending-on-credit.
- Final WhatsApp prices from KIM-0148 are canonical until Dr. Yehoshua issues a new structured change.

## Daily Automation Standard

The 09:00 report must run inside Kim Live's local scheduler, not Codex.

Before sending:

1. Refresh prices.
2. Validate all prices.
3. Block if any active or pending price is unvalidated.
4. Compose 30 live order lines.
5. Append Balance de Crédito.
6. Send by WhatsApp to the doctor.
7. Store delivery proof.
