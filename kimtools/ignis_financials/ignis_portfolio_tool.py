#!/usr/bin/env python3
"""Stable CLI wrapper for the Kim Live Ignis Financials portfolio tool.

This file intentionally delegates calculations and side effects to
`server.portfolio_cli`. It is a tool boundary for agents, not a second
portfolio engine.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict


DEFAULT_RUNTIME = Path("/Users/dryehoshuapython/.kim_live")

READ_ACTIONS = {
    "status",
    "summary",
    "client_report",
    "whatsapp_preview",
    "fundamental_report",
    "fundamental_history",
}
WRITE_ACTIONS = {
    "record_funding",
    "record_funding_event",
    "execute_pending_order",
    "sell_position",
    "aggregate_order",
    "set_position",
}
SEND_ACTIONS = {
    "send_whatsapp_report",
}
ALLOWED_ACTIONS = READ_ACTIONS | WRITE_ACTIONS | SEND_ACTIONS


def runtime_dir() -> Path:
    return Path(os.environ.get("KIM_LIVE_RUNTIME", str(DEFAULT_RUNTIME))).expanduser()


def load_server_module():
    runtime = runtime_dir()
    if not (runtime / "server.py").exists():
        raise RuntimeError(f"Kim Live runtime server.py not found at {runtime}")
    sys.path.insert(0, str(runtime))
    import server  # type: ignore

    return server


def parse_parameters(raw: str | None) -> Dict[str, Any]:
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON parameters: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("Parameters must be a JSON object.")
    return value


def verify_success_contract(action: str, result: Dict[str, Any]) -> Dict[str, Any]:
    evidence = {
        "action": action,
        "ok": bool(result.get("ok")),
        "contract_ok": False,
        "reason": "",
    }
    if action in SEND_ACTIONS:
        message_count = int(result.get("message_count") or 0)
        delivered_count = int(result.get("delivered_count") or 0)
        errors = result.get("errors") or []
        execution_state = str(result.get("execution_state") or "")
        evidence["contract_ok"] = (
            bool(result.get("ok"))
            and execution_state == "delivered"
            and message_count > 0
            and delivered_count == message_count
            and not errors
        )
        evidence["reason"] = (
            "delivered"
            if evidence["contract_ok"]
            else f"delivery_not_complete state={execution_state} delivered={delivered_count}/{message_count}"
        )
        return evidence
    if action in WRITE_ACTIONS:
        result_text = json.dumps(result, ensure_ascii=False)
        has_evidence = any(
            token in result_text
            for token in ("change_", "tx_", "funding_", "event", "final_change", "transaction")
        )
        evidence["contract_ok"] = bool(result.get("ok")) and has_evidence
        evidence["reason"] = "committed" if evidence["contract_ok"] else "missing_write_evidence"
        return evidence
    evidence["contract_ok"] = bool(result.get("ok"))
    evidence["reason"] = "read_ok" if evidence["contract_ok"] else "read_failed"
    return evidence


def run(action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    normalized = action.strip()
    if normalized not in ALLOWED_ACTIONS:
        raise SystemExit(f"Unsupported action: {action}")
    server = load_server_module()
    result = server.portfolio_cli(normalized, parameters)
    if not isinstance(result, dict):
        result = {"ok": False, "error": "portfolio_cli returned non-object", "raw": result}
    result.setdefault("tool", "ignis_financials.portfolio")
    result["success_contract"] = verify_success_contract(normalized, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="IGNIS FINANCIALS portfolio tool wrapper.")
    parser.add_argument("action", choices=sorted(ALLOWED_ACTIONS))
    parser.add_argument("parameters", nargs="?", help="JSON object with action parameters.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()
    result = run(args.action, parse_parameters(args.parameters))
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0 if result.get("success_contract", {}).get("contract_ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
