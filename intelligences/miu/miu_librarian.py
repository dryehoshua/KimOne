#!/usr/bin/env python3
"""MIU librarian storage helper.

This helper stores already-classified MIU learning into portable BIFROST
folders. It does not call an LLM. The filtering intelligence is defined in
prompts/miu_librarian.md; this script persists the result.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable


BIFROST = Path("/Users/dryehoshuapython/Documents/BIFROST")
MIU_MEMORY = BIFROST / "MEMORY" / "MIU"

CLASS_TO_FOLDER = {
    "stable_knowledge": "knowledge",
    "client_preference": "profiles",
    "operational_standard": "knowledge",
    "tool_instruction": "knowledge",
    "superseded_fact": "distilled",
    "transient_context": "learning_inbox",
}


def slug(value: str) -> str:
    text = re.sub(r"[^0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", "-", value or "").strip("-").lower()
    return text[:90] or "miu-card"


def today() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d")


def card_markdown(kind: str, domain: str, card: Dict[str, Any]) -> str:
    title = str(card.get("title") or kind).strip()
    content = str(card.get("content") or "").strip()
    confidence = card.get("confidence", "")
    source = card.get("source") or {}
    lines = [
        f"# {title}",
        "",
        f"- Tipo: {kind}",
        f"- Dominio: {domain or card.get('domain') or 'general'}",
        f"- Confianza: {confidence}",
        f"- Creado: {today()}",
        "",
        "## Knowledge",
        "",
        content or "_Sin contenido._",
    ]
    if isinstance(source, dict) and any(source.values()):
        lines.extend(["", "## Source"])
        for key, value in source.items():
            if value:
                lines.append(f"- {key}: {value}")
    if card.get("supersedes"):
        lines.extend(["", "## Supersedes"])
        for item in card.get("supersedes") or []:
            lines.append(f"- {item}")
    return "\n".join(lines).strip() + "\n"


def iter_cards(payload: Dict[str, Any]) -> Iterable[tuple[str, Dict[str, Any]]]:
    mapping = {
        "stable_knowledge": "stable_knowledge",
        "client_preferences": "client_preference",
        "operational_standards": "operational_standard",
        "tool_instructions": "tool_instruction",
        "superseded_facts": "superseded_fact",
        "transient_context": "transient_context",
    }
    for source_key, kind in mapping.items():
        for card in payload.get(source_key) or []:
            if isinstance(card, str):
                card = {"title": card[:80], "content": card}
            if isinstance(card, dict):
                yield kind, card


def store(payload: Dict[str, Any]) -> Dict[str, Any]:
    domain = str(payload.get("domain") or "general").strip() or "general"
    saved = []
    for kind, card in iter_cards(payload):
        folder_name = CLASS_TO_FOLDER.get(kind, "learning_inbox")
        folder = MIU_MEMORY / folder_name / slug(domain)
        folder.mkdir(parents=True, exist_ok=True)
        title = str(card.get("title") or kind)
        path = folder / f"{today()}-{slug(title)}.md"
        if path.exists():
            path = folder / f"{today()}-{slug(title)}-{dt.datetime.now().strftime('%H%M%S')}.md"
        path.write_text(card_markdown(kind, domain, card), encoding="utf-8")
        saved.append({"kind": kind, "domain": domain, "path": str(path)})
    inbox = MIU_MEMORY / "learning_inbox" / "raw"
    inbox.mkdir(parents=True, exist_ok=True)
    raw_path = inbox / f"{today()}-{dt.datetime.now().strftime('%H%M%S')}-librarian-payload.json"
    raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "saved": saved, "raw_payload": str(raw_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Store MIU librarian output into BIFROST.")
    parser.add_argument("payload", help="JSON librarian output or @/path/to/payload.json")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    raw = args.payload
    if raw.startswith("@"):
        raw = Path(raw[1:]).read_text(encoding="utf-8")
    payload = json.loads(raw)
    result = store(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
