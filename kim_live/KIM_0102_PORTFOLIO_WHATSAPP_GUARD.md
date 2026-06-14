# KIM-0102 Portfolio WhatsApp Guard

## Context

The Sr. Eli portfolio WhatsApp flow must always send the portfolio report to the doctor's Dubai WhatsApp control number:

- `whatsapp:+971585943726`

Portfolio reports are operational messages for the doctor, so this recipient bypasses the Pipedrive proactive-recipient guard. Client/prospect outbound messaging still requires Pipedrive registration unless it is an inbound WhatsApp reply.

## Rules

- Send one message per order, plus one final balance message.
- Do not group multiple portfolio orders into compact chunks.
- Do not send a portfolio report if any active position contains an unvalidated price.
- Do not send a portfolio report if any line says `precio actual no validado` or `sin porcentaje validado`.
- Generate fresh prices before sending. Binance spot may be used as the direct source; CoinGecko should confirm when available.
- Pending orders are not P/L. Phrase pending orders as distance from current price to entry and mark them as `sigue pendiente` unless price has crossed the entry.

## Fixes In 1.5.72

- Doctor Dubai WhatsApp control number no longer waits on Pipedrive lookup.
- `send_whatsapp_report` no longer mutates the saved portfolio standard before validation.
- `send_whatsapp_report` blocks real sends when prices are unvalidated unless explicitly overridden.
- KIM-0101 portfolio standard was restored after a bad unvalidated report attempt.
