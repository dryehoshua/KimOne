#!/usr/bin/env python3
"""Ignis portfolio module for Kim Live.

This module keeps Sr. Eli portfolio handling away from free-form chat logic.
It treats the portfolio as a structured operating ledger:
- manual_entries: open technical orders/lots
- closed_positions: realized P/L
- accounting.funding_conversions: deposits, withdrawals and conversions
- client_lines: derived A1..An report without gaps
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

DEFAULT_OVERRIDE_PATH = Path("/Users/dryehoshuapython/.kim_live/context/portfolio_report_overrides.json")
LIVE_STATES = {"active", "pending"}
CLOSED_STATES = {"sold", "closed", "cancelled", "canceled", "removed"}


def _float(value: Any, default: Optional[float] = None) -> Optional[float]:
    if value in (None, ""):
        return default
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return default


def _money(value: Any) -> str:
    number = _float(value)
    if number is None:
        return "N/D"
    return f"{number:.2f}".rstrip("0").rstrip(".")


def _price(value: Any) -> str:
    number = _float(value)
    if number is None:
        return "N/D"
    if abs(number) < 0.0001:
        return f"{number:.12f}".rstrip("0").rstrip(".")
    if abs(number) < 1:
        return f"{number:.8f}".rstrip("0").rstrip(".")
    return f"{number:.6f}".rstrip("0").rstrip(".")


def normalize_symbol(symbol: Any) -> str:
    token = str(symbol or "").upper().strip().replace("BINANCE:", "").replace("/", "").replace(" ", "")
    if token and token.isalpha() and not token.endswith("USDT"):
        token += "USDT"
    return token


def state_of(entry: Dict[str, Any]) -> str:
    state = str(entry.get("state") or "active").strip().lower()
    if state in {"executed", "filled", "market", "mercado", "en_mercado"}:
        return "active"
    if state in {"draft", "open", "pendiente"}:
        return "pending"
    if state in CLOSED_STATES:
        return state
    return state or "active"


class PortfolioInvariant:
    def __init__(self, severity: str, code: str, message: str, item: Dict[str, Any]):
        self.severity = severity
        self.code = code
        self.message = message
        self.item = item

    def as_dict(self) -> Dict[str, Any]:
        return {"severity": self.severity, "code": self.code, "message": self.message, "item": self.item}


class IgnisPortfolioModule:
    def __init__(self, override_path: Path = DEFAULT_OVERRIDE_PATH):
        self.override_path = Path(override_path)
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if not self.override_path.exists():
            return {"manual_entries": [], "closed_positions": [], "accounting": {}}
        return json.loads(self.override_path.read_text(encoding="utf-8"))

    def save(self) -> None:
        self.data["updated_at"] = datetime.now().isoformat(timespec="seconds")
        self.override_path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @property
    def manual_entries(self) -> List[Dict[str, Any]]:
        return [dict(item) for item in self.data.get("manual_entries") or [] if isinstance(item, dict)]

    @property
    def closed_positions(self) -> List[Dict[str, Any]]:
        return [dict(item) for item in self.data.get("closed_positions") or [] if isinstance(item, dict)]

    @property
    def accounting(self) -> Dict[str, Any]:
        return dict(self.data.get("accounting") or {})

    @property
    def suppressed_symbols(self) -> set[str]:
        return {normalize_symbol(item) for item in self.data.get("suppress_symbols") or [] if normalize_symbol(item)}

    def live_entries(self) -> List[Dict[str, Any]]:
        suppressed = self.suppressed_symbols
        rows = []
        for entry in self.manual_entries:
            symbol = normalize_symbol(entry.get("symbol"))
            state = state_of(entry)
            if state not in LIVE_STATES:
                continue
            if symbol in suppressed:
                continue
            row = dict(entry)
            row["symbol"] = symbol
            row["state"] = state
            rows.append(row)
        return sorted(rows, key=lambda item: (int(_float(item.get("order"), 999) or 999), normalize_symbol(item.get("symbol"))))

    def client_source_entries(self) -> List[Dict[str, Any]]:
        live = self.live_entries()
        grouped: List[Dict[str, Any]] = []
        consumed = set()
        for index, entry in enumerate(live):
            if index in consumed:
                continue
            symbol = normalize_symbol(entry.get("symbol"))
            state = state_of(entry)
            same = [entry]
            if state == "active":
                for other_index, other in enumerate(live[index + 1 :], start=index + 1):
                    if other_index in consumed:
                        continue
                    if state_of(other) == "active" and normalize_symbol(other.get("symbol")) == symbol:
                        same.append(other)
                        consumed.add(other_index)
            if len(same) == 1:
                grouped.append(dict(entry))
                continue
            total_amount = sum((_float(item.get("invested_usd"), 0) or 0) for item in same)
            total_credit = sum((_float(item.get("credit_usd"), 0) or 0) for item in same)
            quantity = 0.0
            for item in same:
                amount = _float(item.get("invested_usd"), 0) or 0
                price = _float(item.get("entry_price"), 0) or 0
                if amount and price:
                    quantity += amount / price
            weighted = (total_amount / quantity) if quantity else _float(entry.get("entry_price"))
            merged = dict(entry)
            merged["invested_usd"] = round(total_amount, 2)
            merged["credit_usd"] = round(total_credit, 2)
            merged["entry_price"] = weighted
            merged["label"] = str(entry.get("label") or symbol.replace("USDT", "/USDT"))
            merged["is_consolidated"] = True
            merged["split_members"] = [dict(item) for item in same]
            merged["notes"] = "Cliente consolidado desde tramos tecnicos: " + " | ".join(str(item.get("notes") or item.get("id") or item.get("order") or "") for item in same)
            grouped.append(merged)
        return grouped

    def client_lines(self) -> List[Dict[str, Any]]:
        lines = []
        for index, entry in enumerate(self.client_source_entries(), start=1):
            symbol = normalize_symbol(entry.get("symbol"))
            label = str(entry.get("label") or symbol.replace("USDT", "/USDT"))
            state = state_of(entry)
            credit = _float(entry.get("credit_usd"), 0) or 0
            amount_value = _float(entry.get("invested_usd"), 0) or 0
            if credit and credit < amount_value:
                credit_label = " (c parcial)"
            elif credit:
                credit_label = " (c)"
            else:
                credit_label = ""
            amount = _money(amount_value)
            entry_price = _price(entry.get("entry_price"))
            suffix = "pendiente" if state == "pending" else "en mercado"
            consolidated = " consolidada" if entry.get("is_consolidated") else ""
            line = f"A{index}. {label}{consolidated}: {amount} USD a {entry_price}{credit_label}. Estado: {suffix}."
            lines.append({
                "id": f"A{index}",
                "client_display_id": f"A{index}",
                "technical_order": entry.get("order"),
                "symbol": symbol,
                "label": label,
                "state": state,
                "invested_usd": amount_value,
                "entry_price": _float(entry.get("entry_price")),
                "credit_usd": credit,
                "message": line,
                "source_id": entry.get("id") or "",
                "notes": entry.get("notes") or "",
                "is_consolidated": bool(entry.get("is_consolidated")),
                "split_members": entry.get("split_members") or [],
            })
        return lines

    def cashflows(self) -> List[Dict[str, Any]]:
        rows = self.accounting.get("funding_conversions")
        return [dict(item) for item in rows if isinstance(item, dict)] if isinstance(rows, list) else []

    def accounting_summary(self) -> Dict[str, Any]:
        fee_rate = _float(self.accounting.get("operation_fee_rate"), 0.012) or 0.012
        cash_in = 0.0
        cash_out = 0.0
        conversion_volume = 0.0
        for event in self.cashflows():
            if str(event.get("status") or "confirmed").lower() != "confirmed":
                continue
            amount = _float(event.get("amount_usd"), 0) or 0
            event_type = str(event.get("type") or "funding").lower()
            conversion_volume += amount
            if event_type in {"withdrawal", "withdraw", "retiro", "cash_out"}:
                cash_out += amount
            else:
                cash_in += amount
        realized_gross = sum((_float(item.get("gross_pnl_usd"), 0) or 0) for item in self.closed_positions)
        realized_fee = sum((_float(item.get("fee_usd"), 0) or 0) for item in self.closed_positions)
        realized_net = sum((_float(item.get("net_pnl_usd"), 0) or 0) for item in self.closed_positions)
        active_total = sum((_float(item.get("invested_usd"), 0) or 0) for item in self.live_entries() if state_of(item) == "active")
        pending_total = sum((_float(item.get("invested_usd"), 0) or 0) for item in self.live_entries() if state_of(item) == "pending")
        return {
            "firm_capital_usd": _float(self.accounting.get("firm_capital_usd"), 0) or 0,
            "active_invested_usd": round(active_total, 2),
            "pending_orders_usd": round(pending_total, 2),
            "portfolio_total_usd": round(active_total + pending_total, 2),
            "cash_in_usd": round(cash_in, 2),
            "cash_out_usd": round(cash_out, 2),
            "net_cashflow_usd": round(cash_in - cash_out, 2),
            "cashflow_fee_usd": round(conversion_volume * fee_rate, 2),
            "realized_closed_count": len(self.closed_positions),
            "realized_gross_pnl_usd": round(realized_gross, 2),
            "realized_fee_usd": round(realized_fee, 2),
            "realized_net_pnl_usd": round(realized_net, 2),
            "operation_fee_rate": fee_rate,
        }

    def invariants(self) -> List[PortfolioInvariant]:
        findings: List[PortfolioInvariant] = []
        suppressed = self.suppressed_symbols
        for entry in self.manual_entries:
            symbol = normalize_symbol(entry.get("symbol"))
            state = state_of(entry)
            if not symbol:
                findings.append(PortfolioInvariant("error", "missing_symbol", "Orden sin simbolo.", entry))
            if state in LIVE_STATES and symbol in suppressed:
                findings.append(PortfolioInvariant("error", "suppressed_live", f"{symbol} esta suprimido pero sigue vivo.", entry))
            if state in LIVE_STATES and _float(entry.get("invested_usd")) in (None, 0):
                findings.append(PortfolioInvariant("error", "missing_amount", f"{symbol} no tiene monto invertido.", entry))
            if state in LIVE_STATES and _float(entry.get("entry_price")) in (None, 0):
                findings.append(PortfolioInvariant("error", "missing_entry", f"{symbol} no tiene precio de entrada.", entry))
        client_ids = [line["id"] for line in self.client_lines()]
        expected = [f"A{i}" for i in range(1, len(client_ids) + 1)]
        if client_ids != expected:
            findings.append(PortfolioInvariant("error", "client_id_gap", "La vista cliente tiene huecos o IDs desordenados.", {"client_ids": client_ids}))
        return findings

    def snapshot(self) -> Dict[str, Any]:
        findings = self.invariants()
        return {
            "ok": not any(item.severity == "error" for item in findings),
            "module": "ignis_financials.sr_eli.portfolio",
            "standard_version": self.data.get("standard_version"),
            "source": str(self.override_path),
            "client_lines": self.client_lines(),
            "technical_entries": self.live_entries(),
            "closed_positions": self.closed_positions,
            "cashflows": self.cashflows(),
            "accounting_summary": self.accounting_summary(),
            "invariants": [item.as_dict() for item in findings],
            "rules_tail": (self.data.get("doctor_rules") or [])[-12:],
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["snapshot", "validate"])
    parser.add_argument("--path", default=str(DEFAULT_OVERRIDE_PATH))
    args = parser.parse_args()
    module = IgnisPortfolioModule(Path(args.path))
    payload = module.snapshot()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
