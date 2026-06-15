# KIM-0107 - IGNIS FINANCIALS Module And Local Clock

Date: 2026-06-15

## Summary

Finance work is now organized as `IGNIS FINANCIALS`, with a dedicated fundamentals tab and a local scheduler policy that does not depend on Codex automations.

## Changes

- Added standalone `Fundamentales` workspace tab.
- Moved the fundamentals panel out of Paper Broker into its own newsroom-style module.
- Added local clock status panel that reads `/api/local-clock`.
- Added `IGNIS_FINANCIALS` memory root constants in backend.
- Kept legacy Ignis portfolio data readable.
- Added `ignis_financials` provider alias for finance actions.
- Paused the Codex automation `revisar-tareas-de-telegram-kim`.

## Local Clock

Kim Live's internal scheduler runs inside the server process and checks due actions every 20 seconds.

This handles recurring actions such as:

- daily Ignis/Cosmos fundamental report at 9:00
- scheduled calls, SMS, WhatsApp, portfolio reports and other API bridge actions

It does not call Codex unless Dr. Yehoshua explicitly opens Codex and asks for software development work.

## Codex Automation Status

The Codex cron automation `revisar-tareas-de-telegram-kim` was paused to stop hourly token spend.

## Cosmos Direction

Use `IGNIS FINANCIALS` as the future module boundary for:

- portfolio operations
- news/fundamentals
- price validation
- paper broker
- client reports
- financial scheduler

