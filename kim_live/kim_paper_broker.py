#!/usr/bin/env python3
"""Local simulated paper broker for Kim portfolio workflows.

This module intentionally does not control TradingView Paper Trading. It keeps a
local, auditable paper order book that Kim can evaluate with validated prices.
"""

from __future__ import annotations

import json
import pathlib
import secrets
from datetime import datetime, timezone


ROOT = pathlib.Path("/Users/dryehoshuapython/.kim_live/MEMORY/portfolios")
DEFAULT_PORTFOLIO_ID = "sr_eli_2026"
DEFAULT_CLIENT_ID = "sr_eli"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def broker_dir() -> pathlib.Path:
    return (
        ROOT
        / "ignis_stock_financials"
        / "clientes"
        / "manejo_de_portafolios"
        / DEFAULT_PORTFOLIO_ID
        / "paper_trading"
    )


def state_path() -> pathlib.Path:
    return broker_dir() / "paper_orders.json"


def audit_path() -> pathlib.Path:
    return broker_dir() / "paper_audit.jsonl"


def snapshot_path() -> pathlib.Path:
    return broker_dir() / "latest_snapshot.json"


def normalize_symbol(value: str) -> str:
    token = str(value or "").upper().strip().replace(" ", "")
    if ":" in token:
        token = token.split(":", 1)[1]
    if token and token.isalpha() and not token.endswith("USDT"):
        token = f"{token}USDT"
    return token


def as_float(value, default=None):
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def boolish(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "si", "sí", "y", "ok"}


def read_state() -> dict:
    path = state_path()
    if not path.exists():
        return {
            "version": "KIM-PAPER-1",
            "portfolio_id": DEFAULT_PORTFOLIO_ID,
            "client_id": DEFAULT_CLIENT_ID,
            "orders": [],
            "alerts": [],
            "updated_at": utc_now_iso(),
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    data.setdefault("version", "KIM-PAPER-1")
    data.setdefault("portfolio_id", DEFAULT_PORTFOLIO_ID)
    data.setdefault("client_id", DEFAULT_CLIENT_ID)
    data.setdefault("orders", [])
    data.setdefault("alerts", [])
    data.setdefault("updated_at", utc_now_iso())
    return data


def write_state(state: dict) -> dict:
    state["updated_at"] = utc_now_iso()
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    snapshot_path().write_text(json.dumps(status_from_state(state), ensure_ascii=False, indent=2), encoding="utf-8")
    return state


def audit(event_type: str, payload: dict) -> None:
    row = {"at": utc_now_iso(), "event": event_type, **(payload or {})}
    path = audit_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def new_id(prefix: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{stamp}-{secrets.token_hex(3).upper()}"


def order_quantity(amount_usd: float, limit_price: float) -> float:
    if not amount_usd or not limit_price:
        return 0.0
    return round(float(amount_usd) / float(limit_price), 10)


def order_crossed(side: str, market_price: float, limit_price: float) -> bool:
    side = str(side or "").upper()
    if market_price in (None, "") or limit_price in (None, ""):
        return False
    market = float(market_price)
    limit = float(limit_price)
    if side == "BUY":
        return market <= limit
    if side == "SELL":
        return market >= limit
    return False


def status_from_state(state: dict) -> dict:
    orders = [order for order in state.get("orders", []) if isinstance(order, dict)]
    alerts = [alert for alert in state.get("alerts", []) if isinstance(alert, dict)]
    buckets = {"pending": [], "filled": [], "cancelled": [], "error": []}
    for order in orders:
        buckets.setdefault(str(order.get("status") or "pending"), []).append(order)
    return {
        "ok": True,
        "provider": "paper_broker",
        "portfolio_id": state.get("portfolio_id") or DEFAULT_PORTFOLIO_ID,
        "client_id": state.get("client_id") or DEFAULT_CLIENT_ID,
        "updated_at": state.get("updated_at"),
        "counts": {key: len(value) for key, value in buckets.items()},
        "pending": buckets.get("pending", []),
        "filled": buckets.get("filled", []),
        "cancelled": buckets.get("cancelled", []),
        "errors": buckets.get("error", []),
        "alerts": alerts[-50:],
        "paths": {
            "state": str(state_path()),
            "audit": str(audit_path()),
            "snapshot": str(snapshot_path()),
        },
    }


def status(_args=None) -> dict:
    return status_from_state(read_state())


def preview_order(args: dict) -> dict:
    args = args or {}
    symbol = normalize_symbol(args.get("symbol") or args.get("ticker") or args.get("asset"))
    side = str(args.get("side") or "BUY").upper().strip()
    if side not in {"BUY", "SELL"}:
        raise ValueError("side debe ser BUY o SELL.")
    amount_usd = as_float(
        args.get("amount_usd")
        or args.get("gross_amount")
        or args.get("usd_amount")
        or args.get("amount")
        or args.get("monto_usd")
    )
    limit_price = as_float(args.get("limit_price") or args.get("price") or args.get("entry_price") or args.get("precio_entrada"))
    if not symbol:
        raise ValueError("Falta symbol para la orden paper.")
    if amount_usd in (None, 0):
        raise ValueError("Falta amount_usd/gross_amount para la orden paper.")
    if limit_price in (None, 0):
        raise ValueError("Falta limit_price/price para la orden paper.")
    return {
        "symbol": symbol,
        "side": side,
        "amount_usd": round(float(amount_usd), 2),
        "limit_price": float(limit_price),
        "quantity": order_quantity(float(amount_usd), float(limit_price)),
        "portfolio_id": args.get("portfolio_id") or DEFAULT_PORTFOLIO_ID,
        "client_id": args.get("client_id") or DEFAULT_CLIENT_ID,
        "client_name": args.get("client_name") or "Sr. Eli",
        "source": args.get("source") or "kim_live",
        "notes": args.get("notes") or args.get("rationale") or args.get("summary") or "",
    }


def place_order(args: dict) -> dict:
    preview = preview_order(args or {})
    state = read_state()
    order_id = str((args or {}).get("order_id") or new_id("KPB"))
    for existing in state.get("orders", []):
        if isinstance(existing, dict) and existing.get("order_id") == order_id:
            return {
                "ok": True,
                "provider": "paper_broker",
                "action": "place_order",
                "deduped": True,
                "order": existing,
                "message": f"Orden paper {order_id} ya existia; no se duplico.",
            }
    order = {
        "order_id": order_id,
        "status": "pending",
        "created_at": utc_now_iso(),
        "confirmed": boolish((args or {}).get("confirm") or (args or {}).get("confirmed")),
        **preview,
    }
    for optional_key in ("source_portfolio_pending_id", "portfolio_pending_snapshot", "report_order", "external_ref"):
        if (args or {}).get(optional_key) not in (None, ""):
            order[optional_key] = (args or {}).get(optional_key)
    state.setdefault("orders", []).append(order)
    write_state(state)
    audit("place_order", {"order": order})
    return {
        "ok": True,
        "provider": "paper_broker",
        "action": "place_order",
        "order": order,
        "message": f"Orden paper {order_id} registrada como pending.",
    }


def find_pending_order(state: dict, args: dict):
    order_id = str(args.get("order_id") or args.get("id") or "").strip()
    symbol = normalize_symbol(args.get("symbol") or args.get("ticker") or args.get("asset"))
    for order in state.get("orders", []):
        if not isinstance(order, dict) or order.get("status") != "pending":
            continue
        if order_id and order.get("order_id") == order_id:
            return order
        if symbol and order.get("symbol") == symbol:
            return order
    return None


def cancel_order(args: dict) -> dict:
    args = args or {}
    state = read_state()
    order = find_pending_order(state, args)
    if not order:
        raise ValueError("No encontre una orden paper pendiente para cancelar.")
    order["status"] = "cancelled"
    order["cancelled_at"] = utc_now_iso()
    order["cancel_reason"] = args.get("reason") or args.get("notes") or "Cancelada por instruccion del doctor."
    order["cancel_confirmed"] = boolish(args.get("confirm") or args.get("confirmed"))
    write_state(state)
    audit("cancel_order", {"order_id": order.get("order_id"), "order": order})
    return {
        "ok": True,
        "provider": "paper_broker",
        "action": "cancel_order",
        "order": order,
        "message": f"Orden paper {order.get('order_id')} cancelada.",
    }


def record_alert(args: dict) -> dict:
    args = args or {}
    state = read_state()
    alert = {
        "alert_id": str(args.get("alert_id") or new_id("TVA")),
        "received_at": utc_now_iso(),
        "provider": args.get("provider") or "tradingview",
        "symbol": normalize_symbol(args.get("symbol") or args.get("ticker") or args.get("asset")),
        "price": as_float(args.get("price") or args.get("close") or args.get("last")),
        "message": args.get("message") or args.get("text") or "",
        "raw": args.get("raw") if isinstance(args.get("raw"), dict) else args,
    }
    state.setdefault("alerts", []).append(alert)
    write_state(state)
    audit("tradingview_alert", {"alert": alert})
    return {"ok": True, "provider": "paper_broker", "action": "record_alert", "alert": alert}


def evaluate_orders(args: dict) -> dict:
    args = args or {}
    state = read_state()
    raw_prices = args.get("prices") or {}
    if not isinstance(raw_prices, dict):
        raw_prices = {}
    symbol_filter = normalize_symbol(args.get("symbol") or "")
    filled = []
    evaluated = []
    for order in state.get("orders", []):
        if not isinstance(order, dict) or order.get("status") != "pending":
            continue
        symbol = normalize_symbol(order.get("symbol"))
        if symbol_filter and symbol != symbol_filter:
            continue
        price_payload = raw_prices.get(symbol) or raw_prices.get(symbol.replace("USDT", "")) or {}
        if isinstance(price_payload, (int, float, str)):
            price_payload = {"price": price_payload}
        market_price = as_float(
            price_payload.get("price")
            or price_payload.get("market_price")
            or price_payload.get("reference_price")
            or price_payload.get("current_price")
        )
        validation = price_payload.get("validation") if isinstance(price_payload.get("validation"), dict) else price_payload
        approved = bool(price_payload.get("approved", True))
        if isinstance(validation, dict) and "approved_for_client_report" in validation:
            approved = bool(validation.get("approved_for_client_report"))
        crossed = approved and order_crossed(order.get("side"), market_price, order.get("limit_price"))
        evaluated.append(
            {
                "order_id": order.get("order_id"),
                "symbol": symbol,
                "side": order.get("side"),
                "limit_price": order.get("limit_price"),
                "market_price": market_price,
                "approved": approved,
                "crossed": crossed,
            }
        )
        if not crossed:
            continue
        fill_price = float(order.get("limit_price"))
        order["status"] = "filled"
        order["filled_at"] = utc_now_iso()
        order["fill_price"] = fill_price
        order["market_price_at_fill"] = market_price
        order["fill_source"] = args.get("trigger") or "kim_price_watcher"
        order["fill_rule"] = "BUY market_price <= limit_price; SELL market_price >= limit_price"
        order["price_validation"] = validation
        order["alert_id"] = args.get("alert_id") or price_payload.get("alert_id")
        order["portfolio_transaction"] = {
            "portfolio_id": order.get("portfolio_id") or DEFAULT_PORTFOLIO_ID,
            "symbol": symbol,
            "side": order.get("side"),
            "quantity": order.get("quantity"),
            "price": fill_price,
            "gross_amount": order.get("amount_usd"),
            "fees": 0,
            "currency": "USD",
            "status": "final",
            "source": "kim_paper_broker_fill",
            "notes": (
                f"Fill simulado Kim Paper Broker {order.get('order_id')}; "
                f"mercado validado {market_price}, limite {order.get('limit_price')}."
            ),
        }
        filled.append(order)
    write_state(state)
    if filled:
        audit(
            "evaluate_orders_filled",
            {
                "trigger": args.get("trigger") or "kim_price_watcher",
                "filled_order_ids": [order.get("order_id") for order in filled],
                "evaluated": evaluated,
            },
        )
    return {
        "ok": True,
        "provider": "paper_broker",
        "action": "evaluate_orders",
        "trigger": args.get("trigger") or "kim_price_watcher",
        "evaluated": evaluated,
        "filled_orders": filled,
        "filled_count": len(filled),
    }


def attach_sync_result(args: dict) -> dict:
    args = args or {}
    order_id = str(args.get("order_id") or "").strip()
    state = read_state()
    matched = None
    for order in state.get("orders", []):
        if isinstance(order, dict) and order.get("order_id") == order_id:
            matched = order
            break
    if not matched:
        raise ValueError("No encontre order_id para adjuntar resultado de sync.")
    matched["portfolio_sync"] = args.get("portfolio_sync") or {}
    matched["portfolio_sync_at"] = utc_now_iso()
    write_state(state)
    audit("portfolio_sync_attached", {"order_id": order_id, "portfolio_sync": matched["portfolio_sync"]})
    return {"ok": True, "provider": "paper_broker", "action": "attach_sync_result", "order": matched}


def cli(action: str, args=None) -> dict:
    action = (action or "status").strip().lower()
    args = args or {}
    if action in {"status", "list", "summary"}:
        return status(args)
    if action in {"preview", "preview_order"}:
        return {"ok": True, "provider": "paper_broker", "action": "preview", "preview": preview_order(args)}
    if action in {"place_order", "place", "buy", "sell"}:
        return place_order(args)
    if action in {"cancel_order", "cancel"}:
        return cancel_order(args)
    if action in {"record_alert", "webhook_alert", "tradingview_alert"}:
        return record_alert(args)
    if action in {"evaluate", "evaluate_orders", "mark_filled", "sync"}:
        return evaluate_orders(args)
    if action in {"attach_sync_result", "portfolio_sync"}:
        return attach_sync_result(args)
    raise ValueError(f"Accion paper broker no soportada: {action}")
