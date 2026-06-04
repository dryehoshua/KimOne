#!/usr/bin/env python3
"""Local BIFROST portfolio ledger for Kim.

This module keeps investment portfolio records in a small SQLite database plus
append-only JSONL audit files. It is intentionally local-first: no Notion,
ClickUp, or cloud service is required to preserve the portfolio history.
"""

import argparse
import datetime as dt
import json
import pathlib
import sqlite3
import uuid


BIFROST = pathlib.Path("/Users/dryehoshuapython/Documents/BIFROST")
ROOT = BIFROST / "MEMORY" / "portfolios"
DB_PATH = ROOT / "portfolio_ledger.sqlite"
CLIENT_PATH = (
    ROOT
    / "ignis_stock_financials"
    / "clientes"
    / "manejo_de_portafolios"
    / "sr_eli_2026"
)
AUDIT_DIR = ROOT / "audit"

DEFAULT_CLIENT_ID = "sr_eli"
DEFAULT_PORTFOLIO_ID = "sr_eli_2026"
DEFAULT_COMPANY = "Ignis Stock Financials"
DEFAULT_PORTFOLIO = "Sr. Eli 2026"
DEFAULT_WATCHLIST = [
    ("LUNCUSDT", "LUNC", "crypto", "BINANCE", "USDT"),
    ("DOGEUSDT", "DOGE", "crypto", "BINANCE", "USDT"),
    ("FTTUSDT", "FTT", "crypto", "BINANCE", "USDT"),
    ("AVAXUSDT", "AVAX", "crypto", "BINANCE", "USDT"),
    ("XLMUSDT", "XLM", "crypto", "BINANCE", "USDT"),
    ("HBARUSDT", "HBAR", "crypto", "BINANCE", "USDT"),
    ("ONDOUSDT", "ONDO", "crypto", "BINANCE", "USDT"),
    ("XRPUSDT", "XRP", "crypto", "BINANCE", "USDT"),
    ("TRXUSDT", "TRX", "crypto", "BINANCE", "USDT"),
    ("ADAUSDT", "ADA / Cardano", "crypto", "BINANCE", "USDT"),
    ("SHIBUSDT", "SHIB", "crypto", "BINANCE", "USDT"),
    ("ZECUSDT", "ZEC / Zcash", "crypto", "BINANCE", "USDT"),
    ("ICPUSDT", "ICP", "crypto", "BINANCE", "USDT"),
    ("DOTUSDT", "DOT", "crypto", "BINANCE", "USDT"),
    ("WLDUSDT", "WLD", "crypto", "BINANCE", "USDT"),
    ("APTUSDT", "APT", "crypto", "BINANCE", "USDT"),
    ("PEPEUSDT", "PEPE", "crypto", "BINANCE", "USDT"),
    ("TRUMPUSDT", "TRUMP", "crypto", "BINANCE", "USDT"),
]


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS clients (
  id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  company TEXT NOT NULL,
  created_at TEXT NOT NULL,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS portfolios (
  id TEXT PRIMARY KEY,
  client_id TEXT NOT NULL REFERENCES clients(id),
  company TEXT NOT NULL,
  name TEXT NOT NULL,
  base_currency TEXT NOT NULL DEFAULT 'USD',
  status TEXT NOT NULL DEFAULT 'active',
  folder_path TEXT NOT NULL,
  created_at TEXT NOT NULL,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS instruments (
  symbol TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  asset_type TEXT NOT NULL,
  venue TEXT,
  quote_currency TEXT,
  created_at TEXT NOT NULL,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS watchlist (
  portfolio_id TEXT NOT NULL REFERENCES portfolios(id),
  symbol TEXT NOT NULL REFERENCES instruments(symbol),
  thesis TEXT,
  priority INTEGER,
  status TEXT NOT NULL DEFAULT 'watching',
  created_at TEXT NOT NULL,
  PRIMARY KEY (portfolio_id, symbol)
);

CREATE TABLE IF NOT EXISTS positions (
  id TEXT PRIMARY KEY,
  portfolio_id TEXT NOT NULL REFERENCES portfolios(id),
  symbol TEXT NOT NULL,
  quantity REAL NOT NULL DEFAULT 0,
  average_cost REAL,
  currency TEXT NOT NULL DEFAULT 'USD',
  source TEXT NOT NULL DEFAULT 'manual',
  notes TEXT,
  updated_at TEXT NOT NULL,
  UNIQUE (portfolio_id, symbol)
);

CREATE TABLE IF NOT EXISTS transactions (
  id TEXT PRIMARY KEY,
  portfolio_id TEXT NOT NULL REFERENCES portfolios(id),
  occurred_at TEXT NOT NULL,
  symbol TEXT NOT NULL,
  side TEXT NOT NULL CHECK (side IN ('BUY', 'SELL', 'TRANSFER_IN', 'TRANSFER_OUT', 'ADJUSTMENT')),
  quantity REAL,
  price REAL,
  gross_amount REAL,
  fees REAL DEFAULT 0,
  currency TEXT NOT NULL DEFAULT 'USD',
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'final', 'void')),
  source TEXT NOT NULL DEFAULT 'manual',
  notes TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS order_aggregations (
  id TEXT PRIMARY KEY,
  portfolio_id TEXT NOT NULL REFERENCES portfolios(id),
  canonical_order TEXT NOT NULL,
  symbol TEXT NOT NULL,
  label TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  weighted_average_price REAL,
  total_quantity REAL,
  total_amount_usd REAL,
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE (portfolio_id, canonical_order)
);

CREATE TABLE IF NOT EXISTS order_aggregation_members (
  id TEXT PRIMARY KEY,
  aggregation_id TEXT NOT NULL REFERENCES order_aggregations(id),
  transaction_id TEXT REFERENCES transactions(id),
  member_order TEXT,
  source_order TEXT,
  role TEXT NOT NULL DEFAULT 'reinforcement',
  amount_usd REAL,
  price REAL,
  quantity REAL,
  include_in_average INTEGER NOT NULL DEFAULT 1,
  status TEXT NOT NULL DEFAULT 'active',
  notes TEXT,
  created_at TEXT NOT NULL,
  UNIQUE (aggregation_id, member_order)
);

CREATE TABLE IF NOT EXISTS market_consultations (
  id TEXT PRIMARY KEY,
  portfolio_id TEXT NOT NULL REFERENCES portfolios(id),
  consulted_at TEXT NOT NULL,
  symbol TEXT,
  interval TEXT,
  question TEXT,
  snapshot_json TEXT,
  analysis TEXT,
  decision TEXT,
  is_final INTEGER NOT NULL DEFAULT 0,
  source_call_id TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS final_changes (
  id TEXT PRIMARY KEY,
  portfolio_id TEXT NOT NULL REFERENCES portfolios(id),
  decided_at TEXT NOT NULL,
  change_type TEXT NOT NULL,
  summary TEXT NOT NULL,
  rationale TEXT,
  related_consultation_id TEXT,
  executed INTEGER NOT NULL DEFAULT 0,
  execution_ref TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS portfolio_snapshots (
  id TEXT PRIMARY KEY,
  portfolio_id TEXT NOT NULL REFERENCES portfolios(id),
  snapshot_at TEXT NOT NULL,
  total_value REAL,
  base_currency TEXT NOT NULL DEFAULT 'USD',
  snapshot_json TEXT,
  notes TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  portfolio_id TEXT NOT NULL REFERENCES portfolios(id),
  doc_type TEXT NOT NULL,
  title TEXT NOT NULL,
  path TEXT NOT NULL,
  created_at TEXT NOT NULL,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS audit_events (
  id TEXT PRIMARY KEY,
  at TEXT NOT NULL,
  actor TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload_json TEXT NOT NULL
);

CREATE VIEW IF NOT EXISTS latest_positions AS
SELECT p.portfolio_id, p.symbol, p.quantity, p.average_cost, p.currency, p.updated_at, i.display_name, i.asset_type, i.venue
FROM positions p
LEFT JOIN instruments i ON i.symbol = p.symbol;
"""


def now():
    return dt.datetime.now().isoformat(timespec="seconds")


def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def as_float(value):
    if value in (None, ""):
        return None
    return float(value)


def normalize_symbol(symbol):
    token = str(symbol or "").upper().strip()
    if token and not token.endswith("USDT") and token.isalpha():
        return f"{token}USDT"
    return token


def connect():
    ROOT.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def write_jsonl(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def audit(conn, event_type, payload, actor="Kim"):
    event = {
        "id": new_id("audit"),
        "at": now(),
        "actor": actor,
        "event_type": event_type,
        "payload": payload,
    }
    conn.execute(
        "INSERT INTO audit_events (id, at, actor, event_type, payload_json) VALUES (?, ?, ?, ?, ?)",
        (event["id"], event["at"], actor, event_type, json.dumps(payload, ensure_ascii=False)),
    )
    write_jsonl(AUDIT_DIR / f"{dt.datetime.now().strftime('%Y-%m')}.jsonl", event)
    return event


def init_db(_args=None):
    CLIENT_PATH.mkdir(parents=True, exist_ok=True)
    (CLIENT_PATH / "attachments").mkdir(exist_ok=True)
    conn = connect()
    with conn:
        conn.executescript(SCHEMA)
        stamp = now()
        conn.execute(
            """
            INSERT OR IGNORE INTO clients (id, display_name, company, created_at, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                DEFAULT_CLIENT_ID,
                "Sr. Eli",
                DEFAULT_COMPANY,
                stamp,
                "Cliente de manejo de portafolio registrado localmente en BIFROST.",
            ),
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO portfolios (id, client_id, company, name, base_currency, status, folder_path, created_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                DEFAULT_PORTFOLIO_ID,
                DEFAULT_CLIENT_ID,
                DEFAULT_COMPANY,
                DEFAULT_PORTFOLIO,
                "USD",
                "active",
                str(CLIENT_PATH),
                stamp,
                "Portafolio local creado por KIM-0036. Registrar solo cambios finales como operaciones finales.",
            ),
        )
        for symbol, display_name, asset_type, venue, quote in DEFAULT_WATCHLIST:
            conn.execute(
                """
                INSERT OR IGNORE INTO instruments (symbol, display_name, asset_type, venue, quote_currency, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (symbol, display_name, asset_type, venue, quote, stamp),
            )
            conn.execute(
                """
                INSERT OR IGNORE INTO watchlist (portfolio_id, symbol, thesis, priority, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (DEFAULT_PORTFOLIO_ID, symbol, "Universo inicial conversado para Sr. Eli.", None, "watching", stamp),
            )
        audit(conn, "init", {"portfolio_id": DEFAULT_PORTFOLIO_ID, "folder_path": str(CLIENT_PATH)})
    write_starter_files()
    return status_json()


def write_starter_files():
    profile = CLIENT_PATH / "portfolio_profile.md"
    if not profile.exists():
        profile.write_text(
            """# Sr. Eli 2026

Empresa: Ignis Stock Financials
Cliente: Sr. Eli
Base currency: USD
Estado: active

## Jerarquia

BIFROST > MEMORY > portfolios > ignis_stock_financials > clientes > manejo_de_portafolios > sr_eli_2026

## Regla operativa

- Las consultas, ideas y escenarios se guardan como `market_consultations`.
- Solo cuando el doctor diga "cambio final", "operacion final", "compra final", "venta final" o equivalente se registra como `final_change` y, si aplica, como `transaction` final.
- Las operaciones preliminares quedan en estado `draft`.
- Notion y ClickUp pueden usarse despues como espejos o tareas, pero BIFROST es la fuente local primaria para este portafolio.

## Universo inicial

LUNC, DOGE, FTT, AVAX, XLM, HBAR, ONDO, XRP, TRX, ADA/Cardano, SHIB, ZEC, ICP, DOT, WLD, APT, PEPE.
""",
            encoding="utf-8",
        )
    pending = CLIENT_PATH / "pending_inputs.md"
    if not pending.exists():
        pending.write_text(
            """# Pending Inputs

Estos datos se mencionaron en conversaciones previas y deben confirmarse antes de convertirse en transacciones finales:

- DOGE: referencia de inversion inicial conversada: 2554 USD.
- FTT: referencia de inversion inicial conversada: 2000 USD.
- LUNC: referencia de inversion inicial conversada: 1000 USD.
- Objetivo conversado: comparar o seleccionar monedas para un portafolio cercano a 1800 USD.

No registrar como operacion final hasta que el doctor confirme cantidades, precios, fecha y orden.
""",
            encoding="utf-8",
        )
    for name in [
        "market_consultations.jsonl",
        "final_changes.jsonl",
        "transactions.jsonl",
        "order_aggregations.jsonl",
        "positions.jsonl",
        "snapshots.jsonl",
    ]:
        path = CLIENT_PATH / name
        if not path.exists():
            path.write_text("", encoding="utf-8")


def status_json():
    conn = connect()
    with conn:
        counts = {}
        for table in [
            "clients",
            "portfolios",
            "instruments",
            "watchlist",
            "positions",
            "transactions",
            "order_aggregations",
            "order_aggregation_members",
            "market_consultations",
            "final_changes",
            "portfolio_snapshots",
        ]:
            counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        portfolio = conn.execute(
            "SELECT id, name, company, base_currency, status, folder_path FROM portfolios WHERE id = ?",
            (DEFAULT_PORTFOLIO_ID,),
        ).fetchone()
    return {
        "ok": True,
        "database": str(DB_PATH),
        "root": str(ROOT),
        "client_folder": str(CLIENT_PATH),
        "portfolio": {
            "id": portfolio[0],
            "name": portfolio[1],
            "company": portfolio[2],
            "base_currency": portfolio[3],
            "status": portfolio[4],
            "folder_path": portfolio[5],
        }
        if portfolio
        else None,
        "counts": counts,
    }


def portfolio_summary_json():
    init_db()
    conn = connect()
    with conn:
        final_rows = conn.execute(
            """
            SELECT id, symbol, side, quantity, price, gross_amount, currency, occurred_at, source, notes
            FROM transactions
            WHERE portfolio_id = ? AND status = 'final'
            ORDER BY occurred_at, created_at
            """,
            (DEFAULT_PORTFOLIO_ID,),
        ).fetchall()
        draft_rows = conn.execute(
            """
            SELECT id, symbol, side, quantity, price, gross_amount, currency, occurred_at, source, notes
            FROM transactions
            WHERE portfolio_id = ? AND status = 'draft'
            ORDER BY occurred_at, created_at
            """,
            (DEFAULT_PORTFOLIO_ID,),
        ).fetchall()
        position_rows = conn.execute(
            """
            SELECT symbol, quantity, average_cost, currency, updated_at, notes
            FROM positions
            WHERE portfolio_id = ?
            ORDER BY symbol
            """,
            (DEFAULT_PORTFOLIO_ID,),
        ).fetchall()
        aggregations = order_aggregations_json(conn, DEFAULT_PORTFOLIO_ID)
    final_transactions = [
        {
            "id": row[0],
            "symbol": row[1],
            "side": row[2],
            "quantity": row[3],
            "price": row[4],
            "gross_amount": row[5],
            "currency": row[6],
            "occurred_at": row[7],
            "source": row[8],
            "notes": row[9],
        }
        for row in final_rows
    ]
    draft_transactions = [
        {
            "id": row[0],
            "symbol": row[1],
            "side": row[2],
            "quantity": row[3],
            "price": row[4],
            "gross_amount": row[5],
            "currency": row[6],
            "occurred_at": row[7],
            "source": row[8],
            "notes": row[9],
        }
        for row in draft_rows
    ]
    positions = [
        {
            "symbol": row[0],
            "quantity": row[1],
            "average_cost": row[2],
            "currency": row[3],
            "updated_at": row[4],
            "notes": row[5],
        }
        for row in position_rows
    ]
    invested = sum(float(row["gross_amount"] or 0) for row in final_transactions if row["side"] == "BUY")
    pending_credit = sum(float(row["gross_amount"] or 0) for row in draft_transactions if row["side"] == "BUY")
    return {
        "ok": True,
        "portfolio_id": DEFAULT_PORTFOLIO_ID,
        "database": str(DB_PATH),
        "final_transaction_count": len(final_transactions),
        "draft_transaction_count": len(draft_transactions),
        "active_invested_usd": invested,
        "pending_credit_usd": pending_credit,
        "positions": positions,
        "final_transactions": final_transactions,
        "draft_transactions": draft_transactions,
        "order_aggregations": aggregations,
    }


def record_consultation(args):
    init_db()
    item = {
        "id": new_id("consult"),
        "portfolio_id": args.portfolio_id,
        "consulted_at": args.consulted_at or now(),
        "symbol": args.symbol,
        "interval": args.interval,
        "question": args.question,
        "snapshot_json": args.snapshot_json or "",
        "analysis": args.analysis or "",
        "decision": args.decision or "",
        "is_final": 1 if args.is_final else 0,
        "source_call_id": args.source_call_id or "",
        "created_at": now(),
    }
    conn = connect()
    with conn:
        conn.execute(
            """
            INSERT INTO market_consultations
            (id, portfolio_id, consulted_at, symbol, interval, question, snapshot_json, analysis, decision, is_final, source_call_id, created_at)
            VALUES (:id, :portfolio_id, :consulted_at, :symbol, :interval, :question, :snapshot_json, :analysis, :decision, :is_final, :source_call_id, :created_at)
            """,
            item,
        )
        audit(conn, "record_consultation", item)
    write_jsonl(CLIENT_PATH / "market_consultations.jsonl", item)
    return {"ok": True, "record": item, "database": str(DB_PATH)}


def record_final_change(args):
    init_db()
    item = {
        "id": new_id("change"),
        "portfolio_id": args.portfolio_id,
        "decided_at": args.decided_at or now(),
        "change_type": args.change_type,
        "summary": args.summary,
        "rationale": args.rationale or "",
        "related_consultation_id": args.related_consultation_id or "",
        "executed": 1 if args.executed else 0,
        "execution_ref": args.execution_ref or "",
        "created_at": now(),
    }
    conn = connect()
    with conn:
        conn.execute(
            """
            INSERT INTO final_changes
            (id, portfolio_id, decided_at, change_type, summary, rationale, related_consultation_id, executed, execution_ref, created_at)
            VALUES (:id, :portfolio_id, :decided_at, :change_type, :summary, :rationale, :related_consultation_id, :executed, :execution_ref, :created_at)
            """,
            item,
        )
        audit(conn, "record_final_change", item)
    write_jsonl(CLIENT_PATH / "final_changes.jsonl", item)
    return {"ok": True, "record": item, "database": str(DB_PATH)}


def parse_aggregation_members(args):
    raw = getattr(args, "members", None) or getattr(args, "members_json", None)
    if raw:
        if isinstance(raw, str):
            members = json.loads(raw)
        else:
            members = raw
        if not isinstance(members, list):
            raise ValueError("members debe ser una lista JSON.")
        return members
    member = {
        "member_order": getattr(args, "member_order", None),
        "source_order": getattr(args, "source_order", None),
        "transaction_id": getattr(args, "transaction_id", None),
        "role": getattr(args, "role", None) or "reinforcement",
        "amount_usd": getattr(args, "amount_usd", None),
        "price": getattr(args, "price", None),
        "quantity": getattr(args, "quantity", None),
        "include_in_average": getattr(args, "include_in_average", True),
        "status": getattr(args, "member_status", None) or "active",
        "notes": getattr(args, "member_notes", None) or getattr(args, "notes", None),
    }
    if not any(member.get(key) not in (None, "") for key in ("member_order", "transaction_id", "amount_usd", "price", "quantity")):
        return []
    return [member]


def load_transaction_for_member(conn, portfolio_id, transaction_id):
    if not transaction_id:
        return None
    return conn.execute(
        """
        SELECT id, symbol, side, quantity, price, gross_amount, status, source, notes
        FROM transactions
        WHERE id = ? AND portfolio_id = ?
        """,
        (transaction_id, portfolio_id),
    ).fetchone()


def coerce_member_payload(conn, portfolio_id, member):
    transaction_id = str(member.get("transaction_id") or "").strip() or None
    tx = load_transaction_for_member(conn, portfolio_id, transaction_id)
    amount = as_float(member.get("amount_usd") if member.get("amount_usd") not in (None, "") else member.get("gross_amount"))
    price = as_float(member.get("price"))
    quantity = as_float(member.get("quantity"))
    if tx:
        quantity = quantity if quantity is not None else as_float(tx[3])
        price = price if price is not None else as_float(tx[4])
        amount = amount if amount is not None else as_float(tx[5])
    if quantity is None and amount is not None and price not in (None, 0):
        quantity = amount / price
    if amount is None and quantity is not None and price is not None:
        amount = quantity * price
    include = member.get("include_in_average", True)
    if isinstance(include, str):
        include = include.strip().lower() not in {"0", "false", "no", "off"}
    return {
        "id": str(member.get("id") or "").strip() or new_id("aggmem"),
        "transaction_id": transaction_id,
        "member_order": str(member.get("member_order") or "").strip() or None,
        "source_order": str(member.get("source_order") or "").strip() or None,
        "role": str(member.get("role") or "reinforcement").strip() or "reinforcement",
        "amount_usd": amount,
        "price": price,
        "quantity": quantity,
        "include_in_average": 1 if include else 0,
        "status": str(member.get("status") or "active").strip().lower() or "active",
        "notes": str(member.get("notes") or "").strip(),
    }


def recalculate_order_aggregation(conn, aggregation_id):
    rows = conn.execute(
        """
        SELECT id, member_order, source_order, role, amount_usd, price, quantity, include_in_average, status, notes, transaction_id
        FROM order_aggregation_members
        WHERE aggregation_id = ?
        ORDER BY created_at, member_order
        """,
        (aggregation_id,),
    ).fetchall()
    total_amount = 0.0
    priced_amount = 0.0
    total_quantity = 0.0
    missing_pricing = []
    members = []
    for row in rows:
        amount = as_float(row[4])
        price = as_float(row[5])
        quantity = as_float(row[6])
        if amount is None and quantity is not None and price is not None:
            amount = quantity * price
        if quantity is None and amount is not None and price not in (None, 0):
            quantity = amount / price
        active = row[8] == "active" and bool(row[7])
        if active and amount is not None:
            total_amount += amount
        if active and amount is not None and quantity is not None and quantity > 0:
            priced_amount += amount
            total_quantity += quantity
        elif active:
            missing_pricing.append(row[1] or row[10] or row[0])
        members.append(
            {
                "id": row[0],
                "member_order": row[1],
                "source_order": row[2],
                "role": row[3],
                "amount_usd": amount,
                "price": price,
                "quantity": quantity,
                "include_in_average": bool(row[7]),
                "status": row[8],
                "notes": row[9],
                "transaction_id": row[10],
            }
        )
    weighted_average = None
    if not missing_pricing and total_quantity > 0:
        weighted_average = total_amount / total_quantity
    elif total_quantity > 0 and priced_amount > 0:
        weighted_average = priced_amount / total_quantity
    conn.execute(
        """
        UPDATE order_aggregations
        SET weighted_average_price = ?, total_quantity = ?, total_amount_usd = ?, updated_at = ?
        WHERE id = ?
        """,
        (weighted_average, total_quantity or None, total_amount or None, now(), aggregation_id),
    )
    return {
        "weighted_average_price": weighted_average,
        "total_quantity": total_quantity or None,
        "total_amount_usd": total_amount or None,
        "missing_pricing_members": missing_pricing,
        "members": members,
    }


def order_aggregations_json(conn, portfolio_id=DEFAULT_PORTFOLIO_ID):
    rows = conn.execute(
        """
        SELECT id, portfolio_id, canonical_order, symbol, label, status, weighted_average_price, total_quantity, total_amount_usd, notes, created_at, updated_at
        FROM order_aggregations
        WHERE portfolio_id = ?
        ORDER BY CAST(canonical_order AS REAL), canonical_order
        """,
        (portfolio_id,),
    ).fetchall()
    aggregations = []
    for row in rows:
        recalculated = recalculate_order_aggregation(conn, row[0])
        aggregations.append(
            {
                "id": row[0],
                "portfolio_id": row[1],
                "canonical_order": row[2],
                "symbol": row[3],
                "label": row[4],
                "status": row[5],
                "weighted_average_price": recalculated["weighted_average_price"],
                "total_quantity": recalculated["total_quantity"],
                "total_amount_usd": recalculated["total_amount_usd"],
                "missing_pricing_members": recalculated["missing_pricing_members"],
                "members": recalculated["members"],
                "notes": row[9],
                "created_at": row[10],
                "updated_at": now(),
            }
        )
    return aggregations


def aggregate_order(args):
    init_db()
    portfolio_id = getattr(args, "portfolio_id", None) or DEFAULT_PORTFOLIO_ID
    canonical_order = str(getattr(args, "canonical_order", None) or getattr(args, "order_id", None) or "").strip()
    symbol = normalize_symbol(getattr(args, "symbol", None))
    if not canonical_order:
        raise ValueError("Falta canonical_order para aglomerar la orden.")
    if not symbol:
        raise ValueError("Falta symbol para aglomerar la orden.")
    members = parse_aggregation_members(args)
    if not members:
        raise ValueError("Falta al menos un miembro/suborden para aglomerar.")
    stamp = now()
    aggregation_id = str(getattr(args, "aggregation_id", None) or "").strip() or new_id("agg")
    label = str(getattr(args, "label", None) or "").strip() or symbol
    status = str(getattr(args, "status", None) or "active").strip().lower() or "active"
    notes = str(getattr(args, "notes", None) or "").strip()
    conn = connect()
    with conn:
        existing = conn.execute(
            """
            SELECT id FROM order_aggregations
            WHERE portfolio_id = ? AND canonical_order = ?
            """,
            (portfolio_id, canonical_order),
        ).fetchone()
        if existing:
            aggregation_id = existing[0]
        conn.execute(
            """
            INSERT INTO order_aggregations
            (id, portfolio_id, canonical_order, symbol, label, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(portfolio_id, canonical_order) DO UPDATE SET
              symbol=excluded.symbol,
              label=excluded.label,
              status=excluded.status,
              notes=CASE
                WHEN excluded.notes IS NOT NULL AND excluded.notes != '' THEN excluded.notes
                ELSE order_aggregations.notes
              END,
              updated_at=excluded.updated_at
            """,
            (aggregation_id, portfolio_id, canonical_order, symbol, label, status, notes, stamp, stamp),
        )
        written_members = []
        for member in members:
            payload = coerce_member_payload(conn, portfolio_id, member)
            if not payload["member_order"]:
                payload["member_order"] = payload["source_order"] or payload["transaction_id"] or new_id("sub")
            payload["aggregation_id"] = aggregation_id
            payload["created_at"] = stamp
            conn.execute(
                """
                INSERT INTO order_aggregation_members
                (id, aggregation_id, transaction_id, member_order, source_order, role, amount_usd, price, quantity, include_in_average, status, notes, created_at)
                VALUES (:id, :aggregation_id, :transaction_id, :member_order, :source_order, :role, :amount_usd, :price, :quantity, :include_in_average, :status, :notes, :created_at)
                ON CONFLICT(aggregation_id, member_order) DO UPDATE SET
                  transaction_id=excluded.transaction_id,
                  source_order=excluded.source_order,
                  role=excluded.role,
                  amount_usd=excluded.amount_usd,
                  price=excluded.price,
                  quantity=excluded.quantity,
                  include_in_average=excluded.include_in_average,
                  status=excluded.status,
                  notes=excluded.notes
                """,
                payload,
            )
            written_members.append(payload)
        aggregate = recalculate_order_aggregation(conn, aggregation_id)
        record = {
            "id": aggregation_id,
            "portfolio_id": portfolio_id,
            "canonical_order": canonical_order,
            "symbol": symbol,
            "label": label,
            "status": status,
            "notes": notes,
            **aggregate,
        }
        audit(conn, "aggregate_order", record)
    write_jsonl(CLIENT_PATH / "order_aggregations.jsonl", record)
    return {"ok": True, "record": record, "members_written": written_members, "database": str(DB_PATH)}


def apply_final_transaction_to_position(conn, item):
    if item["status"] != "final" or item["side"] not in {"BUY", "SELL"}:
        return None
    quantity = float(item["quantity"] or 0)
    if quantity <= 0:
        return None
    current = conn.execute(
        """
        SELECT id, quantity, average_cost, currency, notes
        FROM positions
        WHERE portfolio_id = ? AND symbol = ?
        """,
        (item["portfolio_id"], item["symbol"]),
    ).fetchone()
    old_qty = float(current[1]) if current else 0.0
    old_avg = float(current[2]) if current and current[2] is not None else None
    if item["side"] == "BUY":
        new_qty = old_qty + quantity
        if item["price"] is not None:
            old_cost = old_qty * (old_avg if old_avg is not None else float(item["price"]))
            new_cost = quantity * float(item["price"])
            new_avg = (old_cost + new_cost) / new_qty if new_qty else float(item["price"])
        else:
            new_avg = old_avg
    else:
        new_qty = max(0.0, old_qty - quantity)
        new_avg = old_avg
    position = {
        "id": current[0] if current else new_id("pos"),
        "portfolio_id": item["portfolio_id"],
        "symbol": item["symbol"],
        "quantity": new_qty,
        "average_cost": new_avg,
        "currency": item["currency"],
        "source": f"transaction:{item['id']}",
        "notes": f"Auto position update from final {item['side']} transaction.",
        "updated_at": now(),
    }
    conn.execute(
        """
        INSERT INTO positions (id, portfolio_id, symbol, quantity, average_cost, currency, source, notes, updated_at)
        VALUES (:id, :portfolio_id, :symbol, :quantity, :average_cost, :currency, :source, :notes, :updated_at)
        ON CONFLICT(portfolio_id, symbol) DO UPDATE SET
          quantity=excluded.quantity,
          average_cost=excluded.average_cost,
          currency=excluded.currency,
          source=excluded.source,
          notes=excluded.notes,
          updated_at=excluded.updated_at
        """,
        position,
    )
    write_jsonl(CLIENT_PATH / "positions.jsonl", position)
    return position


def add_transaction(args):
    init_db()
    price = args.price
    gross_amount = args.gross_amount
    quantity = args.quantity
    if quantity is None and price not in (None, 0) and gross_amount not in (None, ""):
        quantity = float(gross_amount) / float(price)
    item = {
        "id": new_id("tx"),
        "portfolio_id": args.portfolio_id,
        "occurred_at": args.occurred_at or now(),
        "symbol": args.symbol.upper(),
        "side": args.side.upper(),
        "quantity": quantity,
        "price": price,
        "gross_amount": gross_amount,
        "fees": args.fees or 0,
        "currency": args.currency,
        "status": args.status,
        "source": args.source,
        "notes": args.notes or "",
        "created_at": now(),
    }
    conn = connect()
    with conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO instruments (symbol, display_name, asset_type, venue, quote_currency, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (item["symbol"], item["symbol"], "crypto", None, item["currency"], now()),
        )
        conn.execute(
            """
            INSERT INTO transactions
            (id, portfolio_id, occurred_at, symbol, side, quantity, price, gross_amount, fees, currency, status, source, notes, created_at)
            VALUES (:id, :portfolio_id, :occurred_at, :symbol, :side, :quantity, :price, :gross_amount, :fees, :currency, :status, :source, :notes, :created_at)
            """,
            item,
        )
        position = apply_final_transaction_to_position(conn, item)
        audit(conn, "add_transaction", item)
    write_jsonl(CLIENT_PATH / "transactions.jsonl", item)
    return {"ok": True, "record": item, "position": position, "database": str(DB_PATH)}


def cancel_transaction(args):
    init_db()
    portfolio_id = args.portfolio_id or DEFAULT_PORTFOLIO_ID
    transaction_id = getattr(args, "transaction_id", None)
    symbol = (getattr(args, "symbol", None) or "").upper()
    status = getattr(args, "status", None) or "draft"
    reason = getattr(args, "reason", None) or "Cancelado por instruccion del doctor."
    conn = connect()
    with conn:
        if transaction_id:
            row = conn.execute(
                """
                SELECT id, portfolio_id, symbol, side, quantity, price, gross_amount, fees, currency, status, source, notes, occurred_at, created_at
                FROM transactions
                WHERE id = ? AND portfolio_id = ?
                """,
                (transaction_id, portfolio_id),
            ).fetchone()
        else:
            if not symbol:
                raise ValueError("Falta symbol o transaction_id para cancelar transaccion.")
            row = conn.execute(
                """
                SELECT id, portfolio_id, symbol, side, quantity, price, gross_amount, fees, currency, status, source, notes, occurred_at, created_at
                FROM transactions
                WHERE portfolio_id = ? AND symbol = ? AND status = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (portfolio_id, symbol, status),
            ).fetchone()
        if not row:
            raise ValueError("No encontre transaccion para cancelar.")
        if row[9] == "void":
            record = {
                "id": row[0],
                "portfolio_id": row[1],
                "symbol": row[2],
                "status": row[9],
                "notes": row[11],
            }
            return {"ok": True, "record": record, "already_void": True, "database": str(DB_PATH)}
        updated_notes = (row[11] or "").strip()
        updated_notes = (updated_notes + "\n" if updated_notes else "") + f"VOID {now()}: {reason}"
        conn.execute(
            "UPDATE transactions SET status = 'void', notes = ? WHERE id = ?",
            (updated_notes, row[0]),
        )
        record = {
            "id": row[0],
            "portfolio_id": row[1],
            "symbol": row[2],
            "side": row[3],
            "quantity": row[4],
            "price": row[5],
            "gross_amount": row[6],
            "fees": row[7],
            "currency": row[8],
            "status": "void",
            "previous_status": row[9],
            "source": row[10],
            "notes": updated_notes,
            "occurred_at": row[12],
            "created_at": row[13],
            "voided_at": now(),
            "void_reason": reason,
        }
        audit(conn, "cancel_transaction", record)
    write_jsonl(CLIENT_PATH / "transactions.jsonl", record)
    return {"ok": True, "record": record, "database": str(DB_PATH)}


def replace_draft_order(args):
    init_db()
    portfolio_id = args.portfolio_id or DEFAULT_PORTFOLIO_ID
    old_symbol = (args.old_symbol or "").upper()
    new_symbol = (args.new_symbol or args.symbol or "").upper()
    if not old_symbol or not new_symbol:
        raise ValueError("Faltan old_symbol y new_symbol para reemplazar orden pendiente.")
    gross_amount = args.gross_amount
    price = args.price
    if gross_amount is None:
        raise ValueError("Falta gross_amount para la nueva orden.")
    if price in (None, 0, ""):
        raise ValueError("Falta price para la nueva orden.")
    reason = args.reason or f"Reemplazo de orden pendiente {old_symbol} -> {new_symbol}."
    cancelled = cancel_transaction(
        argparse.Namespace(
            portfolio_id=portfolio_id,
            transaction_id=getattr(args, "old_transaction_id", None),
            symbol=old_symbol,
            status="draft",
            reason=reason,
        )
    )
    new_order = add_transaction(
        argparse.Namespace(
            portfolio_id=portfolio_id,
            occurred_at=args.occurred_at or now(),
            symbol=new_symbol,
            side="BUY",
            quantity=getattr(args, "quantity", None),
            price=price,
            gross_amount=gross_amount,
            fees=getattr(args, "fees", 0) or 0,
            currency=args.currency or "USD",
            status=args.status or "draft",
            source=args.source or "kim_live_replace_order",
            notes=args.notes or reason,
        )
    )
    change = record_final_change(
        argparse.Namespace(
            portfolio_id=portfolio_id,
            decided_at=args.decided_at or now(),
            change_type="replace_pending_order",
            summary=args.summary or f"Se cancelo {old_symbol} pendiente y se sustituyo por {new_symbol} por {gross_amount} USD a {price}.",
            rationale=args.rationale or reason,
            related_consultation_id=getattr(args, "related_consultation_id", None),
            executed=0,
            execution_ref=new_order["record"]["id"],
        )
    )
    return {
        "ok": True,
        "cancelled": cancelled["record"],
        "replacement": new_order["record"],
        "final_change": change["record"],
        "database": str(DB_PATH),
    }


def set_position(args):
    init_db()
    item = {
        "id": new_id("pos"),
        "portfolio_id": args.portfolio_id,
        "symbol": args.symbol.upper(),
        "quantity": args.quantity,
        "average_cost": args.average_cost,
        "currency": args.currency,
        "source": args.source,
        "notes": args.notes or "",
        "updated_at": args.updated_at or now(),
    }
    conn = connect()
    with conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO instruments (symbol, display_name, asset_type, venue, quote_currency, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (item["symbol"], item["symbol"], "crypto", None, item["currency"], now()),
        )
        conn.execute(
            """
            INSERT INTO positions (id, portfolio_id, symbol, quantity, average_cost, currency, source, notes, updated_at)
            VALUES (:id, :portfolio_id, :symbol, :quantity, :average_cost, :currency, :source, :notes, :updated_at)
            ON CONFLICT(portfolio_id, symbol) DO UPDATE SET
              quantity=excluded.quantity,
              average_cost=excluded.average_cost,
              currency=excluded.currency,
              source=excluded.source,
              notes=excluded.notes,
              updated_at=excluded.updated_at
            """,
            item,
        )
        audit(conn, "set_position", item)
    write_jsonl(CLIENT_PATH / "positions.jsonl", item)
    return {"ok": True, "record": item, "database": str(DB_PATH)}


def print_json(payload):
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser():
    parser = argparse.ArgumentParser(description="BIFROST local portfolio ledger")
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init", help="Initialize Sr. Eli 2026 workspace")
    init_parser.set_defaults(func=init_db)

    status_parser = sub.add_parser("status", help="Show ledger status")
    status_parser.set_defaults(func=lambda _args: status_json())

    summary_parser = sub.add_parser("summary", help="Show portfolio summary")
    summary_parser.set_defaults(func=lambda _args: portfolio_summary_json())

    consult = sub.add_parser("record-consultation", help="Record a market consultation")
    consult.add_argument("--portfolio-id", default=DEFAULT_PORTFOLIO_ID)
    consult.add_argument("--consulted-at", default=None)
    consult.add_argument("--symbol", default=None)
    consult.add_argument("--interval", default=None)
    consult.add_argument("--question", default=None)
    consult.add_argument("--snapshot-json", default=None)
    consult.add_argument("--analysis", default=None)
    consult.add_argument("--decision", default=None)
    consult.add_argument("--is-final", action="store_true")
    consult.add_argument("--source-call-id", default=None)
    consult.set_defaults(func=record_consultation)

    change = sub.add_parser("record-final-change", help="Record a final portfolio change")
    change.add_argument("--portfolio-id", default=DEFAULT_PORTFOLIO_ID)
    change.add_argument("--decided-at", default=None)
    change.add_argument("--change-type", default="rebalance")
    change.add_argument("--summary", required=True)
    change.add_argument("--rationale", default=None)
    change.add_argument("--related-consultation-id", default=None)
    change.add_argument("--executed", action="store_true")
    change.add_argument("--execution-ref", default=None)
    change.set_defaults(func=record_final_change)

    tx = sub.add_parser("add-transaction", help="Add a draft/final transaction")
    tx.add_argument("--portfolio-id", default=DEFAULT_PORTFOLIO_ID)
    tx.add_argument("--occurred-at", default=None)
    tx.add_argument("--symbol", required=True)
    tx.add_argument("--side", required=True, choices=["BUY", "SELL", "TRANSFER_IN", "TRANSFER_OUT", "ADJUSTMENT"])
    tx.add_argument("--quantity", type=float, default=None)
    tx.add_argument("--price", type=float, default=None)
    tx.add_argument("--gross-amount", type=float, default=None)
    tx.add_argument("--fees", type=float, default=0)
    tx.add_argument("--currency", default="USD")
    tx.add_argument("--status", default="draft", choices=["draft", "final", "void"])
    tx.add_argument("--source", default="manual")
    tx.add_argument("--notes", default=None)
    tx.set_defaults(func=add_transaction)

    cancel = sub.add_parser("cancel-transaction", help="Mark a transaction as void")
    cancel.add_argument("--portfolio-id", default=DEFAULT_PORTFOLIO_ID)
    cancel.add_argument("--transaction-id", default=None)
    cancel.add_argument("--symbol", default=None)
    cancel.add_argument("--status", default="draft")
    cancel.add_argument("--reason", default=None)
    cancel.set_defaults(func=cancel_transaction)

    replace = sub.add_parser("replace-draft-order", help="Cancel one draft order and create a replacement")
    replace.add_argument("--portfolio-id", default=DEFAULT_PORTFOLIO_ID)
    replace.add_argument("--old-symbol", required=True)
    replace.add_argument("--old-transaction-id", default=None)
    replace.add_argument("--new-symbol", required=True)
    replace.add_argument("--occurred-at", default=None)
    replace.add_argument("--decided-at", default=None)
    replace.add_argument("--quantity", type=float, default=None)
    replace.add_argument("--price", type=float, required=True)
    replace.add_argument("--gross-amount", type=float, required=True)
    replace.add_argument("--fees", type=float, default=0)
    replace.add_argument("--currency", default="USD")
    replace.add_argument("--status", default="draft", choices=["draft", "final", "void"])
    replace.add_argument("--source", default="kim_live_replace_order")
    replace.add_argument("--notes", default=None)
    replace.add_argument("--summary", default=None)
    replace.add_argument("--rationale", default=None)
    replace.add_argument("--reason", default=None)
    replace.add_argument("--related-consultation-id", default=None)
    replace.set_defaults(func=replace_draft_order)

    aggregate = sub.add_parser("aggregate-order", help="Create or update a weighted order aggregation")
    aggregate.add_argument("--portfolio-id", default=DEFAULT_PORTFOLIO_ID)
    aggregate.add_argument("--canonical-order", required=True)
    aggregate.add_argument("--symbol", required=True)
    aggregate.add_argument("--label", default=None)
    aggregate.add_argument("--status", default="active")
    aggregate.add_argument("--notes", default=None)
    aggregate.add_argument("--members-json", dest="members", default=None)
    aggregate.add_argument("--member-order", default=None)
    aggregate.add_argument("--source-order", default=None)
    aggregate.add_argument("--transaction-id", default=None)
    aggregate.add_argument("--role", default="reinforcement")
    aggregate.add_argument("--amount-usd", type=float, default=None)
    aggregate.add_argument("--price", type=float, default=None)
    aggregate.add_argument("--quantity", type=float, default=None)
    aggregate.add_argument("--member-status", default="active")
    aggregate.add_argument("--member-notes", default=None)
    aggregate.add_argument("--exclude-from-average", dest="include_in_average", action="store_false")
    aggregate.set_defaults(func=aggregate_order, include_in_average=True)

    pos = sub.add_parser("set-position", help="Set current position")
    pos.add_argument("--portfolio-id", default=DEFAULT_PORTFOLIO_ID)
    pos.add_argument("--symbol", required=True)
    pos.add_argument("--quantity", type=float, required=True)
    pos.add_argument("--average-cost", type=float, default=None)
    pos.add_argument("--currency", default="USD")
    pos.add_argument("--source", default="manual")
    pos.add_argument("--notes", default=None)
    pos.add_argument("--updated-at", default=None)
    pos.set_defaults(func=set_position)

    return parser


def main():
    args = build_parser().parse_args()
    print_json(args.func(args))


if __name__ == "__main__":
    main()
