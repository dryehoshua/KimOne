# KIM-0104 Portfolio Price Refresh And Sources

Date: 2026-06-15

## Problem

The Sr. Eli portfolio WhatsApp flow could block or produce "precio actual no validado" when CoinGecko returned `429 rate limit`. The portfolio guard was correct to block unvalidated reports, but the provider set was too fragile.

## Fix

- Added explicit market price cache clearing through `portfolio/refresh_prices`.
- `send_whatsapp_report` now requests a price refresh by default.
- Added public exchange price providers:
  - Binance spot
  - MEXC spot
  - Bybit spot
  - KuCoin spot
- Default portfolio validation providers are now `binance`, `mexc`, `bybit`.
- CoinGecko and CoinMarketCap remain optional, not required for this portfolio path.
- Fundamental report rules now require news from the last 24 hours, with follow-up from older stories only when the story is still moving markets today.

## Validation

- Runtime version: `1.5.75`.
- Validated 12 active positions and 9 pending orders.
- Sent 22 WhatsApp messages to the doctor control number:
  - 21 order lines
  - 1 balance line
- Twilio send result: `22/22` queued, no errors.
- Provider set used: `binance`, `mexc`, `bybit`.

## Current Canonical Portfolio Shape

- Active positions: 12.
- Pending orders: 9.
- Total visible orders: 21.
- Suppressed/closed: GOAT and ZEC must not reappear.
- Closed positions include ZEC and FTT A13 sale.

## ONDO Note

Memory contains an older May 14 instruction where AVAX was changed to ONDO at `0.324`. The current KIM-0101 override, dated June 10/11, has AVAX A17 and ONDO A20 as separate pending credit orders. Do not overwrite the June standard using the older May note unless the doctor explicitly confirms a newer substitution.
