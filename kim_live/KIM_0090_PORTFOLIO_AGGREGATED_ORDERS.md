# KIM-0090 - Portfolio Aggregated Orders

Date: 2026-06-04

## Purpose

Kim must handle grouped portfolio orders without confusing reinforcements, corrections, and weighted-average updates with sells, withdrawals, or refunds.

## Canonical Rule

- The doctor decides which order ID survives.
- The surviving order keeps its visible identifier, for example `A9`.
- Reinforcements are stored as suborders, for example `9.1`, optionally linked to a source order like `13`.
- Weighted average entry price is calculated as:

```text
average_price = total_usd_cost / total_units
total_units = sum(amount_usd_i / price_i)
```

- A correction of amount, price, decimal zeros, or aggregation is not a sell, withdrawal, or refund.
- Only record a sell/withdrawal/refund if the doctor explicitly says sell, sold, withdraw, withdrawal, refund, or final sale.

## PEPE A9 Current Standard

- `9`: base PEPE, 1800 USD at `0.00000324`.
- `9.1`: reinforcement from source order `13`, 900 USD at `0.0000030016`.
- Total: 2700 USD.
- Total units: `855395640.843402`.
- Weighted average: `0.000003156434135364376`.
- Visible report: `A9. PEPE/USDT: total 2700 USD ... Aglomeracion: 9 + 9.1 desde 13.`

Credit treatment:

- Current visible credit for PEPE remains 1800 USD.
- The additional 900 USD is treated as firm/reinforcement unless the doctor gives a new explicit instruction.

## SOL Validation Fix

SOL was returning a Binance price but still showing as not validated because the validator requires two fresh sources. The missing piece was the CoinGecko symbol mapping.

Added mapping:

```python
"SOL": "solana"
```

Expected result:

- `SOLUSDT` validates with Binance + CoinGecko.
- `approved_for_client_report=true` when provider spread is inside tolerance.

## Implementation

- `portfolio_db.py`
  - Adds `order_aggregations`.
  - Adds `order_aggregation_members`.
  - Adds `aggregate_order`.
  - Adds `order_aggregations` to `portfolio_summary_json()`.

- `server.py`
  - Exposes `portfolio_cli("aggregate_order", ...)`.
  - Exposes `kim_portfolio_record(action="aggregate_order")`.
  - Applies aggregations to client reports.
  - Suppresses duplicate same-symbol pending rows when an active aggregation already absorbs them.
  - Bumps Kim Live to `1.5.68`.

- `context/portfolio_report_overrides.json`
  - Sets PEPE A9 to 2700 USD at weighted average `0.000003156434135364`.
  - Adds durable doctor rules for agglomerations and corrections.

## Validation

Runtime test from `.kim_live/server.py` returned:

```text
version 1.5.68
A9. PEPE/USDT: total 2700 USD a 0.000003156434 (c parcial). Aglomeracion: 9 + 9.1 desde 13.
A12. SOL/USDT: 1800 USD a 54. Precio actual validado. Distancia vs entrada about +29%.
pending symbols: NEARUSDT, SOLUSDT
```
