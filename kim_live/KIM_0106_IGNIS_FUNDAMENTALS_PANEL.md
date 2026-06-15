# KIM-0106 - Ignis Fundamentals Panel

Date: 2026-06-15

## Purpose

Kim Live now treats the Sr. Eli portfolio tooling as part of the future Ignis/Cosmos app. The Paper Broker tab includes a daily fundamental-news panel for the last 24 hours.

## Frontend

Added `Fundamentales Ignis 24h` inside the Paper Broker workspace.

Controls:

- `Historial`: reads prior fundamental reports.
- `Actualizar 24h`: generates a fresh daily fundamental report.
- `Buscar mas`: performs a broader 24h query for additional market-moving news.

The manual portfolio rows now show visible metrics after price refresh:

- current validated price
- client phrase / percent move

## Backend

Added portfolio action:

- `fundamental_history`

Updated scheduler executor:

- `portfolio/fundamental_report` can now run from Kim's internal scheduler.

The runtime scheduler has one recurring job:

- Label: `Ignis Cosmos fundamental 24h diario 09:00`
- First due: `2026-06-16T09:00:00-06:00`
- Recurrence: `daily`
- Provider/action: `portfolio/fundamental_report`

## WhatsApp Note

Twilio default sender is `+14057837532`, the Kim number ending in `7532`. The latest portfolio WhatsApp issue was not caused by using the Glam Homes number. Twilio returned WhatsApp delivery error `63016`.

## Recommended News/Data Providers

For Cosmos scale, use a mixed stack:

- Bloomberg/Reuters only if enterprise budget and licensing justify it.
- Financial Modeling Prep for economic calendar, general/stock/crypto news and structured endpoints.
- Finnhub for market news, fundamentals, economic data and alternative data.
- Alpha Vantage for news/sentiment and broad market data.
- CoinDesk Data API for crypto-specific news/data.
- Primary sources when available: Fed, BLS, Treasury, official project/company releases.

## Verification

- Runtime health reports `1.5.77`.
- `/api/portfolio fundamental_history` returns history.
- `/api/schedules` shows one pending daily Ignis/Cosmos fundamentals job at 09:00.
- Frontend contains the fundamentals panel and metric chips.
