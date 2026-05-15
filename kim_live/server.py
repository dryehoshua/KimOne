#!/usr/bin/env python3
"""
Kim Live.

Local-only conversation capture server for BIFROST.
The browser handles OpenAI Realtime voice when configured, local dictation when
available, and BIFROST stores the transcript.
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import cgi
import base64
import datetime as dt
import difflib
from email import policy
from email.header import decode_header, make_header
from email.message import EmailMessage
from email.parser import BytesParser
from email.utils import formataddr, getaddresses
import hashlib
import html
import imaplib
import importlib.util
import io
import json
import mimetypes
import pathlib
import re
import secrets
import shutil
import smtplib
import sqlite3
import subprocess
import tempfile
import threading
import time
import unicodedata
import urllib.parse
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile


APP_DIR = pathlib.Path(__file__).resolve().parent
BIFROST = pathlib.Path("/Users/dryehoshuapython/Documents/BIFROST")
MEMORY_INBOX = BIFROST / "MEMORY" / "inbox"
RUNTIME_MEMORY_ROOT = pathlib.Path("/Users/dryehoshuapython/.kim_live/MEMORY")
RUNTIME_MEMORY_INBOX = pathlib.Path("/Users/dryehoshuapython/.kim_live/MEMORY/inbox")
RUNTIME_CONTEXT = pathlib.Path("/Users/dryehoshuapython/.kim_live/context")
MEMORY_ROOT = BIFROST / "MEMORY"
MEMORY_CONTEXT_DIR = MEMORY_ROOT / "context"
MEMORY_CALLS = MEMORY_ROOT / "calls"
MEMORY_UPLOADS = MEMORY_ROOT / "uploads"
MEMORY_RESEARCH = MEMORY_ROOT / "research"
CRM_ROOT = BIFROST / "CRM"
CRM_DB = CRM_ROOT / "crm.sqlite"
CRM_CONTACTS_DIR = CRM_ROOT / "contacts"
CRM_COMPANIES_DIR = CRM_ROOT / "companies"
CRM_INTERACTIONS_DIR = CRM_ROOT / "interactions"
CRM_SCHEDULES_DIR = CRM_ROOT / "schedules"
RUNTIME_CRM_ROOT = RUNTIME_CONTEXT / "CRM"
ACTIVE_CRM_ROOT = None
ACTIVE_CRM_DB = None
MEMORY_ANALYTICS = MEMORY_CONTEXT_DIR / "memory_analytics_latest.json"
UPLOAD_INDEX = MEMORY_CONTEXT_DIR / "uploaded_files_index.json"
CALL_INDEX = MEMORY_CONTEXT_DIR / "call_index.jsonl"
RESEARCH_SOURCE_CACHE = MEMORY_CONTEXT_DIR / "research_sources_latest.json"
RUNTIME_CALLS = RUNTIME_MEMORY_ROOT / "calls"
RUNTIME_UPLOADS = RUNTIME_MEMORY_ROOT / "uploads"
RUNTIME_RESEARCH = RUNTIME_MEMORY_ROOT / "research"
RUNTIME_PHONE_CALLS = RUNTIME_MEMORY_ROOT / "phone_calls"
RUNTIME_MEMORY_ANALYTICS = RUNTIME_CONTEXT / "memory_analytics_latest.json"
RUNTIME_UPLOAD_INDEX = RUNTIME_CONTEXT / "uploaded_files_index.json"
RUNTIME_CALL_INDEX = RUNTIME_CONTEXT / "call_index.jsonl"
RUNTIME_RESEARCH_SOURCE_CACHE = RUNTIME_CONTEXT / "research_sources_latest.json"
CONTEXT_MEMORY = BIFROST / "MEMORY" / "context" / "kim_context.md"
CONTEXT_SPEC = BIFROST / "docs" / "kim_live_context_memory_spec.md"
CLICKUP_INVENTORY = BIFROST / "kimtools" / "clickup" / "clickup_inventory.json"
RUNTIME_CLICKUP_INVENTORY = pathlib.Path("/Users/dryehoshuapython/.kim_telegram/clickup_inventory.json")
CLICKUP_TASKS_JSON = BIFROST / "MEMORY" / "context" / "clickup_open_tasks_latest.json"
CLICKUP_TASKS_MARKDOWN = BIFROST / "MEMORY" / "context" / "clickup_open_tasks_latest.md"
RUNTIME_CLICKUP_TASKS_JSON = RUNTIME_CONTEXT / "clickup_open_tasks_latest.json"
RUNTIME_CLICKUP_TASKS_MARKDOWN = RUNTIME_CONTEXT / "clickup_open_tasks_latest.md"
API_BRIDGE_SPEC = BIFROST / "docs" / "kim_live_api_bridge_spec.md"
RUNTIME_API_BRIDGE_SPEC = RUNTIME_CONTEXT / "kim_live_api_bridge_spec.md"
API_BRIDGE_LOG = MEMORY_CONTEXT_DIR / "api_bridge_actions.jsonl"
RUNTIME_API_BRIDGE_LOG = RUNTIME_CONTEXT / "api_bridge_actions.jsonl"
API_PREPARED_ACTIONS = MEMORY_CONTEXT_DIR / "api_bridge_prepared_actions.json"
RUNTIME_API_PREPARED_ACTIONS = RUNTIME_CONTEXT / "api_bridge_prepared_actions.json"
TWILIO_SMS_LOG = MEMORY_CONTEXT_DIR / "twilio_sms_actions.jsonl"
RUNTIME_TWILIO_SMS_LOG = RUNTIME_CONTEXT / "twilio_sms_actions.jsonl"
TWILIO_CALL_LOG = MEMORY_CONTEXT_DIR / "twilio_call_actions.jsonl"
RUNTIME_TWILIO_CALL_LOG = RUNTIME_CONTEXT / "twilio_call_actions.jsonl"
TWILIO_CALL_CONTEXTS = MEMORY_CONTEXT_DIR / "twilio_call_contexts.json"
RUNTIME_TWILIO_CALL_CONTEXTS = RUNTIME_CONTEXT / "twilio_call_contexts.json"
CLICKUP_STRUCTURE_JSON = MEMORY_CONTEXT_DIR / "clickup_structure_latest.json"
RUNTIME_CLICKUP_STRUCTURE_JSON = RUNTIME_CONTEXT / "clickup_structure_latest.json"
MARKET_PRICE_VALIDATION_LOG = MEMORY_CONTEXT_DIR / "market_price_validations.jsonl"
RUNTIME_MARKET_PRICE_VALIDATION_LOG = RUNTIME_CONTEXT / "market_price_validations.jsonl"
HOSTINGER_MAIL_LOG = MEMORY_CONTEXT_DIR / "hostinger_mail_actions.jsonl"
RUNTIME_HOSTINGER_MAIL_LOG = RUNTIME_CONTEXT / "hostinger_mail_actions.jsonl"
PORTFOLIO_TOOL = APP_DIR / "portfolio_db.py"
MEMORY_ROUTER_LOG = MEMORY_CONTEXT_DIR / "memory_routes.jsonl"
RUNTIME_MEMORY_ROUTER_LOG = RUNTIME_CONTEXT / "memory_routes.jsonl"
TWILIO_MEDIA_WS_URL_FILE = RUNTIME_CONTEXT / "twilio_media_ws_url.txt"
OPERATING_MODEL = BIFROST / "docs" / "operating_model.md"
NOTION_CLICKUP_EVAL = BIFROST / "docs" / "notion_vs_clickup_evaluation.md"
TELEGRAM_BRIDGE = pathlib.Path("/Users/dryehoshuapython/.kim_telegram/telegram_kim_bridge.py")
OPENAI_KEYCHAIN_SERVICE = "codex.openai.api_key"
CLICKUP_KEYCHAIN_SERVICE = "codex.clickup.personal_token"
NOTION_KEYCHAIN_SERVICE = "codex.notion.integration_token"
PIPEDRIVE_KEYCHAIN_SERVICE = "codex.pipedrive.api_token"
PIPEDRIVE_COMPANY_DOMAIN_KEYCHAIN_SERVICE = "codex.pipedrive.company_domain"
GMAIL_CLIENT_ID_KEYCHAIN_SERVICE = "codex.google.gmail.client_id"
GMAIL_CLIENT_SECRET_KEYCHAIN_SERVICE = "codex.google.gmail.client_secret"
GMAIL_REFRESH_TOKEN_KEYCHAIN_SERVICE = "codex.google.gmail.refresh_token"
COINMARKETCAP_KEYCHAIN_SERVICE = "codex.coinmarketcap.api_key"
TWILIO_ACCOUNT_SID_KEYCHAIN_SERVICE = "codex.twilio.account_sid"
TWILIO_AUTH_TOKEN_KEYCHAIN_SERVICE = "codex.twilio.auth_token"
TWILIO_API_KEY_SID_KEYCHAIN_SERVICE = "codex.twilio.api_key_sid"
TWILIO_API_KEY_SECRET_KEYCHAIN_SERVICE = "codex.twilio.api_key_secret"
TWILIO_DEFAULT_FROM_NUMBER_KEYCHAIN_SERVICE = "codex.twilio.default_from_number"
SECURITY_VOICE_PHRASE_KEYCHAIN_SERVICE = "codex.kim.security.voice_phrase"
SECURITY_PIN_KEYCHAIN_SERVICE = "codex.kim.security.pin"
KEYCHAIN_ACCOUNT = "dryehoshuapython"
HOST = "127.0.0.1"
PORT = 8765
OPENAI_API_BASE = "https://api.openai.com/v1"
CLICKUP_API_BASE = "https://api.clickup.com/api/v2"
NOTION_API_BASE = "https://api.notion.com/v1"
PIPEDRIVE_API_BASE = "https://api.pipedrive.com/v1"
GOOGLE_OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_OAUTH_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1"
TWILIO_API_BASE = "https://api.twilio.com/2010-04-01"
GMAIL_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
GMAIL_OAUTH_STATE_FILE = RUNTIME_CONTEXT / "google_gmail_oauth_state.json"
NOTION_VERSION = "2022-06-28"
REALTIME_MODEL = "gpt-realtime"
REALTIME_VOICE = "marin"
PHONE_REPLY_MODEL_CANDIDATES = ["gpt-5.4-mini", "gpt-5.4", "gpt-5"]
APP_VERSION = "1.5.20"
RESEARCH_MODEL_CANDIDATES = ["gpt-5.4-mini", "gpt-5.4", "gpt-5"]
DOCUMENT_MODEL_CANDIDATES = ["gpt-5.4-mini", "gpt-5.4", "gpt-5"]
VISION_MODEL_CANDIDATES = ["gpt-5.4-mini", "gpt-5.4", "gpt-5"]
MEMORY_DOCUMENTS = MEMORY_ROOT / "documents"
RUNTIME_DOCUMENTS = RUNTIME_MEMORY_ROOT / "documents"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".heic", ".heif", ".tif", ".tiff", ".bmp"}
DEFAULT_HOSTINGER_MAILBOX = "founder@aipeople.io"
HOSTINGER_MAILBOXES = [
    DEFAULT_HOSTINGER_MAILBOX,
    "founder@aipeople.work",
    "business@aipeople.io",
    "business@tescaelements.com",
    "ceo@tescaelements.com",
]
HOSTINGER_MAILBOX_ALIASES = {
    "founder": DEFAULT_HOSTINGER_MAILBOX,
    "founder ai people": DEFAULT_HOSTINGER_MAILBOX,
    "aipeople": DEFAULT_HOSTINGER_MAILBOX,
    "ai people": DEFAULT_HOSTINGER_MAILBOX,
    "aipeople.io": DEFAULT_HOSTINGER_MAILBOX,
    "work": "founder@aipeople.work",
    "aipeople.work": "founder@aipeople.work",
    "business aipeople": "business@aipeople.io",
    "business ai people": "business@aipeople.io",
    "aipeople business": "business@aipeople.io",
    "ai people business": "business@aipeople.io",
    "business io": "business@aipeople.io",
    "business": "business@tescaelements.com",
    "tesca business": "business@tescaelements.com",
    "ceo": "ceo@tescaelements.com",
    "tesca": "ceo@tescaelements.com",
    "tesca ceo": "ceo@tescaelements.com",
}
HOSTINGER_MAILBOX_DISPLAY_NAMES = {
    DEFAULT_HOSTINGER_MAILBOX: "Dr. Yehoshua Rodriguez | AI People",
    "founder@aipeople.work": "Dr. Yehoshua Rodriguez | AI People",
    "business@aipeople.io": "AI People",
    "business@tescaelements.com": "Tesca Elements",
    "ceo@tescaelements.com": "Dr. Yehoshua Rodriguez | Tesca Elements",
}
KIM_EMAIL_SIGNATURE = "Kim Yan\nAugmented Intelligence Assistant, created by Dr. Yehoshua"
SCHEDULER_THREAD_STARTED = False
SCHEDULER_LOCK = threading.Lock()
SECURITY_AUTHORIZATIONS = MEMORY_CONTEXT_DIR / "kim_security_authorizations.json"
RUNTIME_SECURITY_AUTHORIZATIONS = RUNTIME_CONTEXT / "kim_security_authorizations.json"
SECURITY_AUTH_TTL_SECONDS = 15 * 60
SECURITY_SECRET_CACHE_SECONDS = 60
SECURITY_SECRET_CACHE = {"loaded_at": 0.0, "items": [], "loaded_once": False}
HOSTINGER_IMAP_HOST = "imap.hostinger.com"
HOSTINGER_IMAP_PORT = 993
HOSTINGER_SMTP_HOST = "smtp.hostinger.com"
HOSTINGER_SMTP_PORT = 465
MARKET_PRICE_MAX_AGE_SECONDS = 15 * 60
MARKET_PRICE_SPREAD_LIMIT_PCT = 2.0
COINGECKO_IDS_BY_SYMBOL = {
    "ADA": "cardano",
    "APT": "aptos",
    "AVAX": "avalanche-2",
    "BTC": "bitcoin",
    "DENT": "dent",
    "DOGE": "dogecoin",
    "DOT": "polkadot",
    "ETH": "ethereum",
    "FTT": "ftx-token",
    "HBAR": "hedera-hashgraph",
    "ICP": "internet-computer",
    "LUNC": "terra-luna",
    "ONDO": "ondo-finance",
    "PEPE": "pepe",
    "SHIB": "shiba-inu",
    "TRUMP": "official-trump",
    "TRX": "tron",
    "WLD": "worldcoin-wld",
    "XLM": "stellar",
    "XRP": "ripple",
    "ZEC": "zcash",
}


def today():
    return dt.datetime.now().strftime("%Y-%m-%d")


def now_iso():
    return dt.datetime.now().isoformat(timespec="seconds")


def daily_memory_path():
    now = dt.datetime.now()
    return MEMORY_ROOT / now.strftime("%Y") / now.strftime("%m") / f"{today()}.md"


def brief(text, limit=260):
    safe = (text or "").replace("\n", " ").strip()
    if len(safe) <= limit:
        return safe
    return safe[: limit - 1].rstrip() + "..."


def read_body(handler):
    length = int(handler.headers.get("Content-Length", "0") or "0")
    raw = handler.rfile.read(length).decode("utf-8") if length else "{}"
    return json.loads(raw or "{}")


def read_form(handler):
    length = int(handler.headers.get("Content-Length", "0") or "0")
    raw = handler.rfile.read(length).decode("utf-8", errors="replace") if length else ""
    content_type = handler.headers.get("Content-Type", "")
    if "application/json" in content_type:
        return json.loads(raw or "{}")
    parsed = urllib.parse.parse_qs(raw, keep_blank_values=True)
    return {key: values[-1] if values else "" for key, values in parsed.items()}


def write_json(handler, payload, status=200):
    data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def write_text(handler, text, status=200, content_type="text/plain; charset=utf-8"):
    data = (text or "").encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def write_xml(handler, text, status=200):
    write_text(handler, text, status=status, content_type="text/xml; charset=utf-8")


def append_memory(kind, payload):
    event = {"at": now_iso(), "kind": kind, **payload}
    try:
        MEMORY_INBOX.mkdir(parents=True, exist_ok=True)
        jsonl = MEMORY_INBOX / f"kim_live_{today()}.jsonl"
        with jsonl.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return jsonl
    except PermissionError:
        RUNTIME_MEMORY_INBOX.mkdir(parents=True, exist_ok=True)
        jsonl = RUNTIME_MEMORY_INBOX / f"kim_live_{today()}.jsonl"
        with jsonl.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return jsonl


def append_daily_note(text):
    path = daily_memory_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(f"# BIFROST Memory - {today()}\n", encoding="utf-8")
        with path.open("a", encoding="utf-8") as handle:
            handle.write("\nKim Live note\n")
            handle.write(f"- {now_iso()}: {text.strip()}\n")
    except PermissionError:
        runtime_path = RUNTIME_MEMORY_ROOT / "daily" / f"{today()}.md"
        runtime_path.parent.mkdir(parents=True, exist_ok=True)
        if not runtime_path.exists():
            runtime_path.write_text(f"# Runtime Kim Live Memory - {today()}\n", encoding="utf-8")
        with runtime_path.open("a", encoding="utf-8") as handle:
            handle.write("\nKim Live note\n")
            handle.write(f"- {now_iso()}: {text.strip()}\n")


def read_text_tail(path, limit=5000):
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except PermissionError:
        return ""
    except OSError:
        return ""
    if len(text) <= limit:
        return text.strip()
    return text[-limit:].strip()


def read_text_tail_any(paths, limit=5000):
    for path in paths:
        text = read_text_tail(path, limit=limit)
        if text:
            return text
    return ""


def write_json_file(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_json_file_any(paths, payload):
    last_error = None
    for path in paths:
        try:
            write_json_file(path, payload)
            return path
        except PermissionError as exc:
            last_error = exc
    if last_error:
        raise last_error
    return None


def read_json_file(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, PermissionError, json.JSONDecodeError):
        return default


def read_json_file_any(paths, default):
    for path in paths:
        payload = read_json_file(path, None)
        if payload is not None:
            return payload
    return default


def append_jsonl(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def append_jsonl_any(paths, payload):
    last_error = None
    for path in paths:
        try:
            append_jsonl(path, payload)
            return path
        except PermissionError as exc:
            last_error = exc
    if last_error:
        raise last_error
    return None


def write_json_file_both(primary, runtime, payload):
    written = []
    for path in [primary, runtime]:
        try:
            write_json_file(path, payload)
            written.append(str(path))
        except PermissionError:
            continue
    return written


def load_keychain_secret(service, required=True):
    try:
        completed = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-a",
                KEYCHAIN_ACCOUNT,
                "-s",
                service,
                "-w",
            ],
            text=True,
            capture_output=True,
            timeout=60,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        if not required:
            return ""
        detail = (exc.stderr or exc.stdout or "").strip()
        raise ValueError(f"No encontre credencial en Keychain para {service}.") from ValueError(detail)
    return completed.stdout.strip()


def load_keychain_secret_for_account(service, account, required=True):
    try:
        completed = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-a",
                account,
                "-s",
                service,
                "-w",
            ],
            text=True,
            capture_output=True,
            timeout=60,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        if not required:
            return ""
        detail = (exc.stderr or exc.stdout or "").strip()
        raise ValueError(f"No encontre credencial en Keychain para {service}/{account}.") from ValueError(detail)
    return completed.stdout.strip()


def store_keychain_secret(service, value):
    secret = (value or "").strip()
    if not secret:
        raise ValueError(f"No puedo guardar {service}: valor vacio.")
    subprocess.run(
        [
            "security",
            "add-generic-password",
            "-a",
            KEYCHAIN_ACCOUNT,
            "-s",
            service,
            "-w",
            secret,
            "-U",
        ],
        check=True,
        timeout=60,
    )
    return True


def normalize_security_text(value):
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    return text


def security_secret_candidates(force=False):
    now_ts = dt.datetime.now(dt.timezone.utc).timestamp()
    if not force and SECURITY_SECRET_CACHE.get("loaded_once"):
        return list(SECURITY_SECRET_CACHE.get("items") or [])
    candidates = []
    phrase = load_keychain_secret(SECURITY_VOICE_PHRASE_KEYCHAIN_SERVICE, required=False)
    if phrase:
        candidates.append({"method": "voice_phrase", "value": phrase})
    pin = load_keychain_secret(SECURITY_PIN_KEYCHAIN_SERVICE, required=False)
    if pin:
        candidates.append({"method": "pin", "value": pin})
    SECURITY_SECRET_CACHE["loaded_at"] = now_ts
    SECURITY_SECRET_CACHE["items"] = candidates
    SECURITY_SECRET_CACHE["loaded_once"] = True
    return candidates


def security_status(session_id=""):
    candidates = security_secret_candidates()
    active = security_authorization_is_active(session_id) if session_id else False
    return {
        "configured": bool(candidates),
        "authorized": bool(active),
        "methods": [item["method"] for item in candidates],
        "ttl_seconds": SECURITY_AUTH_TTL_SECONDS,
        "scope": "confirm_prepared y confirm=true para escrituras/API sensibles",
    }


def load_security_authorizations():
    merged = {}
    latest_updated = ""
    for path in [SECURITY_AUTHORIZATIONS, RUNTIME_SECURITY_AUTHORIZATIONS]:
        data = read_json_file(path, None)
        if not isinstance(data, dict):
            continue
        latest_updated = max(latest_updated, str(data.get("updated_at") or ""))
        for session_id, item in (data.get("sessions") or {}).items():
            if isinstance(item, dict):
                merged[str(session_id)] = item
    return {"updated_at": latest_updated or now_iso(), "sessions": merged}


def save_security_authorizations(state):
    now_ts = dt.datetime.now(dt.timezone.utc).timestamp()
    sessions = {}
    for session_id, item in (state.get("sessions") or {}).items():
        if float(item.get("expires_at_ts") or 0) > now_ts:
            sessions[str(session_id)] = item
    state = {"updated_at": now_iso(), "sessions": sessions}
    write_json_file_both(SECURITY_AUTHORIZATIONS, RUNTIME_SECURITY_AUTHORIZATIONS, state)
    return state


def security_session_key(session_id=""):
    value = str(session_id or "local").strip() or "local"
    return re.sub(r"[^A-Za-z0-9_.:-]+", "-", value)[:140]


def security_authorization_is_active(session_id=""):
    state = load_security_authorizations()
    item = (state.get("sessions") or {}).get(security_session_key(session_id))
    if not item:
        return False
    return float(item.get("expires_at_ts") or 0) > dt.datetime.now(dt.timezone.utc).timestamp()


def authorize_security_session(session_id="", method="voice_phrase"):
    now = dt.datetime.now(dt.timezone.utc)
    expires = now + dt.timedelta(seconds=SECURITY_AUTH_TTL_SECONDS)
    state = load_security_authorizations()
    state.setdefault("sessions", {})[security_session_key(session_id)] = {
        "authorized_at": now_iso(),
        "expires_at": expires.isoformat(),
        "expires_at_ts": expires.timestamp(),
        "method": method,
    }
    save_security_authorizations(state)
    append_memory(
        "security_authorized",
        {"session_id": security_session_key(session_id), "method": method, "expires_at": expires.isoformat()},
    )
    return {"authorized": True, "method": method, "expires_at": expires.isoformat()}


def security_authorization_from_input(parameters=None, transcript=""):
    parameters = parameters or {}
    texts = [(transcript or "")[-800:]]
    for key in [
        "authorization_phrase",
        "security_phrase",
        "voice_phrase",
        "frase_autorizacion",
        "authorization_pin",
        "security_pin",
        "pin",
    ]:
        if parameters.get(key):
            texts.append(str(parameters.get(key)))
    normalized_inputs = [normalize_security_text(text) for text in texts if str(text or "").strip()]
    compact_inputs = [re.sub(r"\s+", "", item) for item in normalized_inputs]
    for candidate in security_secret_candidates():
        secret = normalize_security_text(candidate.get("value"))
        if not secret:
            continue
        compact_secret = re.sub(r"\s+", "", secret)
        for normalized, compact in zip(normalized_inputs, compact_inputs):
            if secret and secret in normalized:
                return authorize_security_session(method=candidate["method"], session_id=parameters.get("session_id", ""))
            if compact_secret and compact_secret in compact:
                return authorize_security_session(method=candidate["method"], session_id=parameters.get("session_id", ""))
    return {"authorized": False}


def api_action_requires_security(provider, action, confirm=False):
    action = (action or "").strip().lower()
    if action in {"confirm_prepared", "execute_prepared", "confirm_last", "confirm_action", "confirmar_accion"}:
        return True
    return bool(confirm)


def ensure_api_security(provider, action, parameters=None, confirm=False, session_id="", transcript=""):
    if not api_action_requires_security(provider, action, confirm=confirm):
        return {"authorized": True, "required": False}
    if security_authorization_is_active(session_id):
        return {"authorized": True, "required": True, "cached": True}
    probe_parameters = dict(parameters or {})
    probe_parameters["session_id"] = session_id
    auth = security_authorization_from_input(probe_parameters, transcript=transcript)
    if auth.get("authorized"):
        auth["required"] = True
        return auth
    status = security_status(session_id=session_id)
    return {
        "authorized": False,
        "required": True,
        "configured": status["configured"],
        "methods": status["methods"],
        "ttl_seconds": status["ttl_seconds"],
    }


SENSITIVE_LOG_KEYS = {
    "api_key",
    "authorization",
    "authorization_phrase",
    "authorization_pin",
    "auth_token",
    "client_secret",
    "password",
    "pin",
    "security_phrase",
    "security_pin",
    "secret",
    "token",
    "voice_phrase",
}


def sanitize_for_log(value):
    if isinstance(value, dict):
        clean = {}
        for key, item in value.items():
            if str(key).lower() in SENSITIVE_LOG_KEYS:
                clean[key] = "[redacted]"
            else:
                clean[key] = sanitize_for_log(item)
        return clean
    if isinstance(value, list):
        return [sanitize_for_log(item) for item in value]
    return value


def sanitize_text_for_log(value):
    text = str(value or "")
    clean = text
    for candidate in security_secret_candidates():
        secret = str(candidate.get("value") or "").strip()
        if secret:
            clean = re.sub(re.escape(secret), "[redacted]", clean, flags=re.I)
    return clean


def text_tokens(text):
    return re.findall(r"[\wáéíóúñüÁÉÍÓÚÑÜ]+", (text or "").lower())


def detect_topics(text):
    tokens = set(text_tokens(text))
    rules = {
        "Tesca Elements": {"tesca", "neorgana", "forever", "aifa", "cybersecurity"},
        "ClickUp": {"clickup", "tarea", "tareas", "estatus", "deadline", "asignado"},
        "Notion": {"notion", "wiki", "base", "conocimiento"},
        "Memoria IA": {"memoria", "vector", "vectores", "embedding", "embeddings", "contexto"},
        "Investigacion web": {"internet", "online", "navegacion", "busqueda", "investigar"},
        "Archivos": {"archivo", "archivos", "documento", "carga", "subir"},
        "PipeDrive": {"pipedrive", "crm", "cliente", "clientes"},
        "AWS": {"aws", "nube", "servidor", "hosting"},
        "Vida personal": {"personal", "familia", "agenda", "cita"},
        "Torah y religion": {"torá", "tora", "religion", "religión", "hebreo"},
        "Aeronáutica": {"aeronautica", "aeronáutica", "avion", "avión"},
    }
    hits = []
    for name, keywords in rules.items():
        score = len(tokens & keywords)
        if score:
            hits.append({"name": name, "score": score})
    hits.sort(key=lambda item: (-item["score"], item["name"]))
    return hits[:8]


def stable_vector(text, dims=24):
    vector = [0.0] * dims
    for token in text_tokens(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = digest[0] % dims
        sign = 1 if digest[1] % 2 == 0 else -1
        vector[idx] += sign * (1 + min(len(token), 12) / 12)
    total = sum(abs(value) for value in vector) or 1.0
    return [round(value / total, 6) for value in vector]


def decode_text_bytes(data):
    for encoding in ["utf-8", "utf-16", "latin-1"]:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def extract_openxml_text(data):
    chunks = []
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for name in archive.namelist():
            if not name.endswith(".xml"):
                continue
            if not (
                name.startswith("word/")
                or name.startswith("ppt/")
                or name.startswith("xl/")
                or name == "xl/sharedStrings.xml"
            ):
                continue
            try:
                root = ET.fromstring(archive.read(name))
            except ET.ParseError:
                continue
            for node in root.iter():
                if node.text and node.text.strip():
                    chunks.append(node.text.strip())
    return "\n".join(chunks)


def extract_pdf_text(data):
    with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
        handle.write(data)
        handle.flush()
        for module_name in ["pypdf", "PyPDF2"]:
            try:
                completed = subprocess.run(
                    [
                        "python3",
                        "-c",
                        (
                            "import sys\n"
                            f"import {module_name} as pdf\n"
                            "reader = pdf.PdfReader(sys.argv[1])\n"
                            "print('\\n'.join((page.extract_text() or '') for page in reader.pages))\n"
                        ),
                        handle.name,
                    ],
                    text=True,
                    capture_output=True,
                    timeout=60,
                    check=True,
                )
                if completed.stdout.strip():
                    return completed.stdout
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                continue
        return ""


def extract_text_from_upload(data, filename):
    suffix = pathlib.Path(filename).suffix.lower()
    mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    text = ""
    method = "binary-fallback"
    if suffix in {".txt", ".md", ".markdown", ".csv", ".tsv", ".json", ".jsonl", ".xml", ".html", ".htm", ".log"}:
        text = decode_text_bytes(data)
        method = "plain-text"
        if suffix in {".html", ".htm"}:
            text = strip_tags(text)
    elif suffix in {".docx", ".pptx", ".xlsx"}:
        text = extract_openxml_text(data)
        method = "openxml"
    elif suffix == ".pdf":
        text = extract_pdf_text(data)
        method = "pdf"
    elif suffix in IMAGE_SUFFIXES:
        text = ""
        method = "image"
    elif suffix in {".rtf"}:
        text = re.sub(r"[{}\\][A-Za-z0-9*'-]* ?", " ", decode_text_bytes(data))
        method = "rtf-basic"
    else:
        decoded = decode_text_bytes(data)
        printable_ratio = sum(ch.isprintable() or ch.isspace() for ch in decoded[:6000]) / max(len(decoded[:6000]), 1)
        if printable_ratio > 0.78:
            text = decoded
            method = "text-guess"
    text = re.sub(r"\n{3,}", "\n\n", text or "").strip()
    return {
        "text": text[:650000],
        "extracted_chars": len(text),
        "extractor": method,
        "mime": mime,
    }


def meaningful_text(text):
    clean = re.sub(r"\s+", " ", text or "").strip()
    if len(clean) < 260:
        return False
    letters = sum(ch.isalpha() for ch in clean[:4000])
    spaces = sum(ch.isspace() for ch in clean[:4000])
    return letters > 140 and spaces > 25


def openai_upload_file(filename, data, purpose="user_data"):
    boundary = "----kimlive" + hashlib.sha256(f"{filename}{len(data)}{now_iso()}".encode()).hexdigest()[:24]
    mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    parts = [
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"purpose\"\r\n\r\n{purpose}\r\n".encode("utf-8"),
        (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"file\"; filename=\"{pathlib.Path(filename).name}\"\r\n"
            f"Content-Type: {mime}\r\n\r\n"
        ).encode("utf-8")
        + data
        + b"\r\n",
        f"--{boundary}--\r\n".encode("utf-8"),
    ]
    request = urllib.request.Request(
        f"{OPENAI_API_BASE}/files",
        data=b"".join(parts),
        headers={
            "Authorization": f"Bearer {load_openai_key()}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI file upload error {exc.code}: {brief(raw, 500)}") from exc


def openai_delete_file(file_id):
    if not file_id:
        return
    request = urllib.request.Request(
        f"{OPENAI_API_BASE}/files/{urllib.parse.quote(file_id)}",
        headers={"Authorization": f"Bearer {load_openai_key()}"},
        method="DELETE",
    )
    try:
        with urllib.request.urlopen(request, timeout=45):
            return
    except Exception:
        return


def analyze_file_with_openai(data, filename, extracted_text=""):
    uploaded = openai_upload_file(filename, data)
    file_id = uploaded.get("id")
    prompt = (
        "Analiza este archivo para la memoria de Kim Live. Si es PDF o imagen, aplica OCR visual. "
        "Extrae texto importante, describe imagenes, tablas, diagramas y estructura. "
        "Responde en español con: 1) lectura/OCR relevante, 2) resumen ejecutivo, "
        "3) puntos clave, 4) posibles tareas, 5) temas/categorias. "
        "No inventes contenido que no aparezca en el archivo."
    )
    if extracted_text and meaningful_text(extracted_text):
        prompt += "\n\nTexto local ya extraido para contrastar:\n" + extracted_text[:14000]
    payload = {
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_file", "file_id": file_id},
                ],
            }
        ],
        "max_output_tokens": 1800,
    }
    try:
        response, model = openai_response_with_fallback(VISION_MODEL_CANDIDATES, payload)
        return {
            "model": model,
            "file_id": file_id,
            "text": output_text_from_response(response),
        }
    finally:
        openai_delete_file(file_id)


def output_text_from_response(response):
    if response.get("output_text"):
        return response.get("output_text", "").strip()
    parts = []
    for item in response.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            text = content.get("text") or content.get("transcript")
            if text:
                parts.append(text)
    return "\n".join(parts).strip()


def source_annotations_from_response(response):
    sources = []
    seen = set()
    for item in response.get("output", []):
        for content in item.get("content", []):
            for annotation in content.get("annotations", []) or []:
                url = annotation.get("url") or annotation.get("uri")
                title = annotation.get("title") or url
                if url and url not in seen:
                    seen.add(url)
                    sources.append({"title": title, "url": url})
    return sources


def openai_response_with_fallback(model_candidates, payload):
    last_error = None
    for model in model_candidates:
        attempt = {**payload, "model": model}
        try:
            response = openai_json("/responses", payload=attempt, method="POST")
            return response, model
        except Exception as exc:
            last_error = exc
    if last_error:
        raise last_error
    raise RuntimeError("No hay modelos configurados para esta operacion.")


def local_extract_summary(text, filename="", limit=900):
    clean = re.sub(r"\s+", " ", text or "").strip()
    if not clean:
        return f"Guarde {filename}, pero no pude extraer texto legible automaticamente."
    sentences = re.split(r"(?<=[.!?])\s+", clean)
    summary = " ".join(sentences[:5]).strip() or clean
    return brief(summary, limit)


def summarize_uploaded_text(text, filename):
    if len((text or "").strip()) < 120:
        return local_extract_summary(text, filename)
    prompt = (
        "Resume este archivo para memoria de Kim Live. Responde en español. "
        "Devuelve: 1) resumen ejecutivo, 2) puntos importantes, 3) posibles tareas, "
        "4) temas/categorias. No inventes datos si el texto no los contiene.\n\n"
        f"Archivo: {filename}\n\nContenido:\n{text[:30000]}"
    )
    payload = {
        "input": prompt,
        "max_output_tokens": 900,
    }
    try:
        response, _ = openai_response_with_fallback(DOCUMENT_MODEL_CANDIDATES, payload)
        return output_text_from_response(response) or local_extract_summary(text, filename)
    except Exception:
        return local_extract_summary(text, filename)


def draft_document(instruction, source_text="", session_id=""):
    instruction = (instruction or "").strip()
    source_text = (source_text or "").strip()
    if len(instruction) < 3 and len(source_text) < 20:
        raise ValueError("Necesito una instruccion o una conversacion para redactar el documento.")
    prompt = (
        "Eres Kim, asistente ejecutiva de Dr. Yehoshua. Redacta un documento profesional "
        "en español mexicano, claro y listo para editar. Usa Markdown. Si faltan datos, "
        "incluye una seccion breve de supuestos o pendientes.\n\n"
        f"Instruccion:\n{instruction or 'Redacta un documento a partir de la conversacion.'}\n\n"
        f"Contexto/conversacion:\n{source_text[:50000]}"
    )
    response, model = openai_response_with_fallback(
        DOCUMENT_MODEL_CANDIDATES,
        {"input": prompt, "max_output_tokens": 2200},
    )
    text = output_text_from_response(response)
    if not text:
        raise RuntimeError("OpenAI no devolvio texto para el documento.")
    doc_id = "DOC-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    if session_id:
        doc_id = re.sub(r"[^A-Za-z0-9_-]+", "-", f"{session_id}-{doc_id}")
    docs_dir = MEMORY_DOCUMENTS / today()
    try:
        docs_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        docs_dir = RUNTIME_DOCUMENTS / today()
        docs_dir.mkdir(parents=True, exist_ok=True)
    path = docs_dir / f"{doc_id}.md"
    path.write_text(text, encoding="utf-8")
    payload = {
        "doc_id": doc_id,
        "path": str(path),
        "created_at": now_iso(),
        "model": model,
        "chars": len(text),
        "preview": brief(text, 600),
    }
    append_memory("document_drafted", payload)
    append_daily_note(f"Documento redactado desde Kim Live: {path}")
    return payload


def file_stats(path):
    try:
        stat = path.stat()
    except (FileNotFoundError, PermissionError):
        return None
    return {
        "path": str(path),
        "bytes": stat.st_size,
        "updated_at": dt.datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
    }


def count_tree_files(path):
    try:
        return [item for item in path.rglob("*") if item.is_file()]
    except (FileNotFoundError, PermissionError):
        return []


def load_call_entries(limit=12):
    entries = []
    lines = []
    for path in [CALL_INDEX, RUNTIME_CALL_INDEX]:
        try:
            lines.extend(path.read_text(encoding="utf-8").splitlines())
        except (FileNotFoundError, PermissionError):
            continue
    for line in lines[-limit:]:
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def load_upload_entries(limit=12):
    files = []
    for path in [UPLOAD_INDEX, RUNTIME_UPLOAD_INDEX]:
        data = read_json_file(path, {"files": []})
        files.extend(data.get("files", []))
    return files[-limit:]


def extract_principles(limit=18):
    text = read_text_tail_any([CONTEXT_MEMORY, RUNTIME_CONTEXT / "kim_context.md"], 14000)
    principles = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            cleaned = stripped[2:].strip()
            if 18 <= len(cleaned) <= 220:
                principles.append(cleaned)
    seen = []
    for item in principles:
        if item not in seen:
            seen.append(item)
    return seen[-limit:]


def memory_analytics():
    memory_files = count_tree_files(MEMORY_ROOT) + count_tree_files(RUNTIME_MEMORY_ROOT)
    docs_files = count_tree_files(BIFROST / "docs")
    context_files = count_tree_files(MEMORY_CONTEXT_DIR) + count_tree_files(RUNTIME_CONTEXT)
    upload_entries = load_upload_entries()
    call_entries = load_call_entries()
    corpus_parts = []
    for paths in [
        [CONTEXT_MEMORY, RUNTIME_CONTEXT / "kim_context.md"],
        [CLICKUP_TASKS_MARKDOWN, RUNTIME_CLICKUP_TASKS_MARKDOWN],
        [BIFROST / "README.md"],
        [BIFROST / "docs" / "operating_model.md"],
    ]:
        corpus_parts.append(read_text_tail_any(paths, 16000))
    for upload in upload_entries[-8:]:
        corpus_parts.append(upload.get("summary", ""))
    corpus = "\n".join(part for part in corpus_parts if part)
    topics = detect_topics(corpus)
    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "memory_bytes": sum(path.stat().st_size for path in memory_files if path.exists()),
        "memory_file_count": len(memory_files),
        "docs_file_count": len(docs_files),
        "context_file_count": len(context_files),
        "uploaded_file_count": len(upload_entries),
        "call_count": len(load_call_entries(limit=5000)),
        "topics": topics,
        "principles": extract_principles(),
        "recent_calls": call_entries,
        "recent_uploads": upload_entries,
        "tracked_files": [
            item for item in [
                file_stats(CONTEXT_MEMORY),
                file_stats(CLICKUP_TASKS_MARKDOWN),
                file_stats(BIFROST / "README.md"),
                file_stats(BIFROST / "docs" / "operating_model.md"),
            ] if item
        ],
    }
    write_json_file_any([MEMORY_ANALYTICS, RUNTIME_MEMORY_ANALYTICS], payload)
    return payload


def save_call_record(body):
    session_id = re.sub(r"[^A-Za-z0-9_-]+", "-", body.get("session_id") or f"CALL-{today()}")
    text = (body.get("text") or "").strip()
    started_at = body.get("started_at") or now_iso()
    title = (body.get("title") or "Kim Live call").strip()[:120]
    topics = detect_topics(text)
    summary = local_extract_summary(text, title, limit=1400)
    related_files = body.get("uploaded_files") or []
    research_sources = body.get("research_sources") or load_sources_for_session(session_id)
    call_number = len(load_call_entries(limit=5000)) + 1
    calls_dir = MEMORY_CALLS / today()
    try:
        calls_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        calls_dir = RUNTIME_CALLS / today()
        calls_dir.mkdir(parents=True, exist_ok=True)
    call_path = calls_dir / f"{session_id}.md"
    content = [
        f"# {session_id}",
        "",
        f"- Title: {title}",
        f"- Call number: {call_number}",
        f"- Started: {started_at}",
        f"- Saved: {now_iso()}",
        f"- Topics: {', '.join(item['name'] for item in topics) or 'Sin clasificar'}",
        f"- Related files: {len(related_files)}",
        f"- Research source groups: {len(research_sources)}",
        "",
        "## Summary",
        "",
        summary,
        "",
        "## Related Files",
        "",
        "\n".join(
            f"- {item.get('filename', 'archivo')}: {item.get('stored_path', '')}"
            for item in related_files
        ) or "- Ninguno",
        "",
        "## Sources Consulted",
        "",
        "\n".join(
            [
                f"### {idx + 1}. {item.get('query', 'Consulta')}\n"
                + "\n".join(
                    f"- {source.get('title') or source.get('url')}: {source.get('url')}"
                    for source in item.get("sources", [])
                )
                + (f"\n\nResumen: {item.get('answer_brief')}" if item.get("answer_brief") else "")
                for idx, item in enumerate(research_sources)
            ]
        ) or "- Ninguna fuente consultada en esta llamada.",
        "",
        "## Transcript",
        "",
        text or "(empty)",
        "",
    ]
    call_path.write_text("\n".join(content), encoding="utf-8")
    entry = {
        "session_id": session_id,
        "title": title,
        "call_number": call_number,
        "started_at": started_at,
        "saved_at": now_iso(),
        "path": str(call_path),
        "topics": topics,
        "summary": summary,
        "related_files": related_files,
        "research_sources": research_sources,
        "chars": len(text),
    }
    entry["memory_route"] = memory_router("save_call", text, session_id=session_id, call_entry=entry)["route"]
    append_jsonl_any([CALL_INDEX, RUNTIME_CALL_INDEX], entry)
    return call_path, entry


def parse_upload(handler):
    form = cgi.FieldStorage(
        fp=handler.rfile,
        headers=handler.headers,
        environ={
            "REQUEST_METHOD": "POST",
            "CONTENT_TYPE": handler.headers.get("Content-Type"),
            "CONTENT_LENGTH": handler.headers.get("Content-Length", "0"),
        },
    )
    file_item = form["file"] if "file" in form else None
    if file_item is None or not getattr(file_item, "filename", ""):
        raise ValueError("No encontre archivo para cargar.")
    raw_name = pathlib.Path(file_item.filename).name
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", raw_name)[:140] or "upload.bin"
    data = file_item.file.read()
    if len(data) > 20 * 1024 * 1024:
        raise ValueError("El archivo excede 20 MB para esta carga inicial.")
    upload_dir = MEMORY_UPLOADS / today()
    try:
        upload_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        upload_dir = RUNTIME_UPLOADS / today()
        upload_dir.mkdir(parents=True, exist_ok=True)
    target = upload_dir / safe_name
    if target.exists():
        stem = target.stem
        suffix = target.suffix
        target = upload_dir / f"{stem}-{dt.datetime.now().strftime('%H%M%S')}{suffix}"
    target.write_bytes(data)
    extraction = extract_text_from_upload(data, raw_name)
    text = extraction["text"]
    suffix = pathlib.Path(raw_name).suffix.lower()
    openai_file_analysis = None
    needs_openai_file_analysis = suffix == ".pdf" or suffix in IMAGE_SUFFIXES or not meaningful_text(text)
    if needs_openai_file_analysis:
        try:
            openai_file_analysis = analyze_file_with_openai(data, raw_name, extracted_text=text)
            if openai_file_analysis.get("text"):
                text = (text + "\n\n## OCR y vision de OpenAI\n\n" + openai_file_analysis["text"]).strip()
                extraction["extractor"] = extraction["extractor"] + "+openai-file-vision"
        except Exception as exc:
            openai_file_analysis = {"error": str(exc)}
    topics = detect_topics(text + " " + safe_name)
    summary = summarize_uploaded_text(text, raw_name)
    analysis = {
        "filename": raw_name,
        "stored_path": str(target),
        "uploaded_at": now_iso(),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "summary": summary,
        "text_preview": brief(text, 2200),
        "extracted_chars": extraction["extracted_chars"],
        "processed_chars": len(text),
        "extractor": extraction["extractor"],
        "mime": extraction["mime"],
        "openai_file_analysis": {
            key: value
            for key, value in (openai_file_analysis or {}).items()
            if key != "file_id"
        },
        "topics": topics,
        "local_vector_note": "Vector local ligero por hashing; embeddings semanticos externos quedan para fase posterior.",
        "local_vector": stable_vector(text + " " + safe_name),
    }
    analysis_path = target.with_suffix(target.suffix + ".analysis.json")
    write_json_file_any([analysis_path, RUNTIME_UPLOADS / today() / analysis_path.name], analysis)
    index_path = UPLOAD_INDEX
    try:
        index = read_json_file(index_path, {"files": []})
        index.setdefault("files", []).append({**analysis, "analysis_path": str(analysis_path)})
        write_json_file(index_path, index)
    except PermissionError:
        index_path = RUNTIME_UPLOAD_INDEX
        index = read_json_file(index_path, {"files": []})
        index.setdefault("files", []).append({**analysis, "analysis_path": str(RUNTIME_UPLOADS / today() / analysis_path.name)})
        write_json_file(index_path, index)
    append_memory("file_upload", {"filename": raw_name, "stored_path": str(target), "topics": topics})
    append_daily_note(f"Archivo cargado en memoria: {raw_name} -> {target}")
    return analysis


def strip_tags(value):
    value = re.sub(r"<[^>]+>", " ", value or "")
    return html.unescape(re.sub(r"\s+", " ", value)).strip()


def research_web(query):
    query = (query or "").strip()
    if len(query) < 3:
        raise ValueError("Escribe una busqueda mas especifica.")
    url = "https://duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 KimLive/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except Exception as exc:
        raise RuntimeError(f"No pude navegar la busqueda: {exc}") from exc
    blocks = re.findall(r'<div class="result.*?</div>\s*</div>', raw, flags=re.S)
    results = []
    for block in blocks[:8]:
        link = re.search(r'class="result__a" href="([^"]+)".*?>(.*?)</a>', block, flags=re.S)
        snippet = re.search(r'class="result__snippet".*?>(.*?)</a>|class="result__snippet".*?>(.*?)</div>', block, flags=re.S)
        if not link:
            continue
        href = html.unescape(link.group(1))
        if href.startswith("//duckduckgo.com/l/?"):
            parsed = urllib.parse.urlparse("https:" + href)
            params = urllib.parse.parse_qs(parsed.query)
            href = params.get("uddg", [href])[0]
        title = strip_tags(link.group(2))
        snippet_text = strip_tags((snippet.group(1) or snippet.group(2)) if snippet else "")
        results.append({"title": title, "url": href, "snippet": snippet_text})
    payload = {
        "query": query,
        "searched_at": now_iso(),
        "source": "DuckDuckGo HTML",
        "results": results,
    }
    path = MEMORY_RESEARCH / f"{today()}_research.jsonl"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        path = RUNTIME_RESEARCH / f"{today()}_research.jsonl"
    append_jsonl_any([path, RUNTIME_RESEARCH / f"{today()}_research.jsonl"], payload)
    append_memory("online_research", {"query": query, "result_count": len(results), "path": str(path)})
    append_daily_note(f"Busqueda web desde Kim Live: {query} ({len(results)} resultados)")
    return payload


def load_research_source_cache():
    for path in [RESEARCH_SOURCE_CACHE, RUNTIME_RESEARCH_SOURCE_CACHE]:
        data = read_json_file(path, None)
        if data:
            return data
    return {"updated_at": None, "items": []}


def update_research_source_cache(session_id, query, sources, answer, source_path):
    cache = load_research_source_cache()
    item = {
        "at": now_iso(),
        "session_id": session_id or "unknown-session",
        "query": query,
        "answer_brief": brief(answer, 900),
        "sources": sources or [],
        "research_path": source_path,
    }
    items = cache.get("items", [])
    items.append(item)
    payload = {
        "updated_at": now_iso(),
        "items": items[-240:],
    }
    write_json_file_both(RESEARCH_SOURCE_CACHE, RUNTIME_RESEARCH_SOURCE_CACHE, payload)
    return item


def load_sources_for_session(session_id, limit=40):
    if not session_id:
        return []
    cache = load_research_source_cache()
    items = [item for item in cache.get("items", []) if item.get("session_id") == session_id]
    return items[-limit:]


def research_with_openai(query, transcript="", session_id=""):
    query = (query or "").strip()
    if len(query) < 3:
        raise ValueError("Necesito una pregunta mas especifica para investigar.")
    local_context = context_brief(limit=2500)
    prompt = (
        "Investiga en internet como Kim Live para el Dr. Yehoshua. "
        "Responde en español, separa: respuesta ejecutiva, datos clave, fuentes y siguiente accion. "
        "Usa busqueda web cuando necesites datos actuales. No inventes fuentes.\n\n"
        f"Pregunta: {query}\n\n"
        f"Contexto BIFROST breve:\n{local_context}\n\n"
        f"Conversacion activa:\n{brief(transcript, 3500)}"
    )
    payload = {
        "input": prompt,
        "tools": [
            {
                "type": "web_search",
                "user_location": {
                    "type": "approximate",
                    "country": "MX",
                    "city": "Mexico City",
                    "timezone": "America/Mexico_City",
                },
            }
        ],
        "max_output_tokens": 1600,
    }
    try:
        response, model = openai_response_with_fallback(RESEARCH_MODEL_CANDIDATES, payload)
        answer = output_text_from_response(response)
        sources = source_annotations_from_response(response)
        source = f"OpenAI Responses web_search ({model})"
        if not answer:
            raise RuntimeError("OpenAI no devolvio respuesta de investigacion.")
        if not sources:
            fallback = research_web(query)
            sources = [{"title": item["title"], "url": item["url"]} for item in fallback.get("results", [])[:8]]
            source = source + " + DuckDuckGo source links"
    except Exception as exc:
        fallback = research_web(query)
        answer = (
            "No pude usar OpenAI web_search en este intento; use busqueda HTML local como respaldo. "
            "Resultados principales:\n"
            + "\n".join(
                f"- {item['title']}: {item['url']} {item.get('snippet', '')}"
                for item in fallback.get("results", [])[:5]
            )
        )
        sources = [{"title": item["title"], "url": item["url"]} for item in fallback.get("results", [])[:8]]
        source = f"DuckDuckGo fallback; OpenAI web_search error: {brief(str(exc), 240)}"
    payload = {
        "query": query,
        "session_id": session_id,
        "searched_at": now_iso(),
        "source": source,
        "answer": answer,
        "sources": sources,
        "topics": detect_topics(query + " " + answer),
    }
    path = MEMORY_RESEARCH / f"{today()}_research.jsonl"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        path = RUNTIME_RESEARCH / f"{today()}_research.jsonl"
    append_jsonl_any([path, RUNTIME_RESEARCH / f"{today()}_research.jsonl"], payload)
    append_memory("research_agent", {"query": query, "source_count": len(sources), "path": str(path)})
    append_daily_note(f"Investigacion asistida desde Kim Live: {query} ({len(sources)} fuentes)")
    payload["path"] = str(path)
    payload["source_cache_item"] = update_research_source_cache(session_id, query, sources, answer, str(path))
    return payload


def conversation_record_from_entry(entry):
    path = pathlib.Path(entry.get("path", ""))
    transcript = ""
    markdown = ""
    try:
        markdown = path.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError, OSError):
        pass
    if "## Transcript" in markdown:
        transcript = markdown.split("## Transcript", 1)[1].strip()
    return {
        **entry,
        "markdown": markdown,
        "transcript": transcript,
    }


def load_conversation(session_id):
    matches = [item for item in load_call_entries(limit=5000) if item.get("session_id") == session_id]
    if not matches:
        raise ValueError("No encontre esa conversacion en memoria.")
    return conversation_record_from_entry(matches[-1])


def latest_kim_live_notes(limit=6):
    path = MEMORY_INBOX / f"kim_live_{today()}.jsonl"
    if not path.exists():
        path = RUNTIME_MEMORY_INBOX / f"kim_live_{today()}.jsonl"
    notes = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (FileNotFoundError, PermissionError):
        return notes
    for line in lines[-limit:]:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        text = brief(event.get("text", ""), 900)
        notes.append(
            {
                "at": event.get("at"),
                "kind": event.get("kind"),
                "text": text,
            }
        )
    return notes


def clickup_context():
    data = None
    source = None
    for path in [CLICKUP_INVENTORY, RUNTIME_CLICKUP_INVENTORY, RUNTIME_CONTEXT / "clickup_inventory.json"]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            source = path
            break
        except (FileNotFoundError, PermissionError, json.JSONDecodeError):
            continue
    if data is None:
        return {"available": False, "summary": "ClickUp inventory not available."}
    raw_workspaces = data.get("workspaces") or data.get("teams") or []
    workspaces = []
    for workspace in raw_workspaces:
        spaces = []
        for space in workspace.get("spaces", [])[:8]:
            lists = [item.get("name") for item in space.get("lists", [])[:8] if item.get("name")]
            spaces.append({"name": space.get("name"), "lists": lists})
        workspaces.append({"name": workspace.get("name"), "spaces": spaces})
    return {
        "available": True,
        "source": str(source),
        "workspaces": workspaces,
        "summary": "ClickUp conectado como fuente de estructura, clientes y tareas.",
    }


def load_json_any(paths):
    for path in paths:
        try:
            return json.loads(path.read_text(encoding="utf-8")), path
        except (FileNotFoundError, PermissionError, json.JSONDecodeError):
            continue
    return None, None


def clickup_task_names_context(limit=3200, max_items=35):
    data, source = load_json_any([CLICKUP_TASKS_JSON, RUNTIME_CLICKUP_TASKS_JSON])
    if data:
        tasks = data.get("tasks", [])
        lines = [
            f"Snapshot ClickUp: {data.get('task_count', len(tasks))} tareas capturadas; fallas: {data.get('failure_count', 0)}.",
            f"Fuente: {source}",
            "Nombres exactos disponibles en la ultima consulta:",
        ]
        for task in tasks[:max_items]:
            location = " > ".join(
                item
                for item in [
                    task.get("team"),
                    task.get("space"),
                    task.get("folder"),
                    task.get("list"),
                ]
                if item
            )
            status = task.get("status") or "sin estatus"
            name = task.get("name") or "Sin nombre"
            lines.append(f"- {location}: [{status}] {name}")
        remaining = len(tasks) - max_items
        if remaining > 0:
            lines.append(f"- ... {remaining} tareas mas en el snapshot completo.")
        text = "\n".join(lines)
        if len(text) > limit:
            return text[:limit].rstrip() + "\n...[tareas truncadas]..."
        return text
    return read_text_tail_any([CLICKUP_TASKS_MARKDOWN, RUNTIME_CLICKUP_TASKS_MARKDOWN], limit=limit)


def api_bridge_config_status(live=False):
    clickup_configured = bool(load_keychain_secret(CLICKUP_KEYCHAIN_SERVICE, required=False))
    notion_configured = bool(load_keychain_secret(NOTION_KEYCHAIN_SERVICE, required=False))
    pipedrive_configured = bool(load_keychain_secret(PIPEDRIVE_KEYCHAIN_SERVICE, required=False))
    gmail_configured = gmail_oauth_configured()
    gmail_has_refresh = gmail_authorized()
    hostinger_status = hostinger_mail_status(live=False)
    status = {
        "clickup": {
            "configured": clickup_configured,
            "write_requires_confirmation": True,
            "capabilities": [
                "status",
                "inventory",
                "list_spaces",
                "list_folders",
                "list_lists",
                "list_tasks",
                "get_task",
                "create_folder",
                "create_list",
                "create_task",
                "update_task",
                "comment_task",
            ],
        },
        "notion": {
            "configured": notion_configured,
            "write_requires_confirmation": True,
            "capabilities": ["status", "search", "get_page", "create_page", "update_page_properties"],
            "note": (
                "Kim Live necesita un token de integracion Notion en Keychain para operar autonomamente. "
                "Codex Desktop tambien tiene acceso Notion por MCP, pero ese acceso no vive dentro del servidor local."
            ),
        },
        "pipedrive": {
            "configured": pipedrive_configured,
            "company_domain": load_keychain_secret(PIPEDRIVE_COMPANY_DOMAIN_KEYCHAIN_SERVICE, required=False),
            "write_requires_confirmation": True,
            "capabilities": [
                "status",
                "list_persons",
                "search_persons",
                "get_person",
                "upsert_person",
                "list_deals",
                "search_deals",
                "create_deal",
                "update_deal",
                "create_activity",
                "create_note",
            ],
        },
        "gmail": {
            "configured": gmail_configured,
            "authorized": gmail_has_refresh,
            "write_requires_confirmation": True,
            "scope": GMAIL_READONLY_SCOPE,
            "capabilities": ["status", "auth_url", "profile", "list_messages", "get_message"],
            "auth_url": "https://kim.aipeople.app/oauth/google/start",
            "mode": "readonly",
        },
        "hostinger_mail": hostinger_status,
        "twilio": twilio_status(live=False),
        "crm": crm_status(),
        "security": security_status(),
        "templates": api_bridge_templates(),
    }
    if live and clickup_configured:
        try:
            user = clickup_request("/user").get("user", {})
            status["clickup"]["user"] = {key: user.get(key) for key in ["id", "username", "email"]}
            status["clickup"]["live_ok"] = True
        except Exception as exc:
            status["clickup"]["live_ok"] = False
            status["clickup"]["error"] = brief(str(exc), 220)
    if live and notion_configured:
        try:
            result = notion_request("/users/me")
            bot = result.get("bot", {}) if isinstance(result, dict) else {}
            status["notion"]["user"] = {
                "id": result.get("id"),
                "name": result.get("name"),
                "workspace_name": bot.get("workspace_name"),
            }
            status["notion"]["live_ok"] = True
        except Exception as exc:
            status["notion"]["live_ok"] = False
            status["notion"]["error"] = brief(str(exc), 220)
    if live and pipedrive_configured:
        try:
            status["pipedrive"].update(pipedrive_status(live=True))
        except Exception as exc:
            status["pipedrive"]["live_ok"] = False
            status["pipedrive"]["error"] = brief(str(exc), 220)
    if live and gmail_configured:
        status["gmail"].update(gmail_status(live=gmail_has_refresh))
    if live:
        status["hostinger_mail"].update(hostinger_mail_status(live=True))
        status["twilio"].update(twilio_status(live=True))
    return status


def api_json_request(base_url, path, headers, method="GET", payload=None, params=None, timeout=90):
    params = params or {}
    query = urllib.parse.urlencode({key: value for key, value in params.items() if value is not None}, doseq=True)
    url = base_url + path + (f"?{query}" if query else "")
    data = None
    req_headers = dict(headers)
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        message = raw
        try:
            parsed = json.loads(raw)
            message = (
                parsed.get("err")
                or parsed.get("error")
                or parsed.get("message")
                or parsed.get("object")
                or raw
            )
        except json.JSONDecodeError:
            pass
        raise RuntimeError(f"API error {exc.code}: {message}") from exc
    if not raw:
        return {}
    return json.loads(raw)


def form_json_request(base_url, path, headers, method="POST", payload=None, params=None, timeout=90):
    params = params or {}
    query = urllib.parse.urlencode({key: value for key, value in params.items() if value is not None}, doseq=True)
    url = base_url + path + (f"?{query}" if query else "")
    data = None
    req_headers = dict(headers)
    if payload is not None:
        data = urllib.parse.urlencode(
            {key: value for key, value in payload.items() if value is not None},
            doseq=True,
        ).encode("utf-8")
        req_headers["Content-Type"] = "application/x-www-form-urlencoded"
    request = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        message = raw
        try:
            parsed = json.loads(raw)
            message = parsed.get("message") or parsed.get("error") or parsed.get("more_info") or raw
        except json.JSONDecodeError:
            pass
        raise RuntimeError(f"API error {exc.code}: {message}") from exc
    if not raw:
        return {}
    return json.loads(raw)


def clickup_request(path, method="GET", payload=None, params=None):
    token = load_keychain_secret(CLICKUP_KEYCHAIN_SERVICE)
    return api_json_request(
        CLICKUP_API_BASE,
        path,
        {"Authorization": token},
        method=method,
        payload=payload,
        params=params,
    )


def notion_request(path, method="GET", payload=None, params=None):
    token = load_keychain_secret(NOTION_KEYCHAIN_SERVICE)
    return api_json_request(
        NOTION_API_BASE,
        path,
        {
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
        },
        method=method,
        payload=payload,
        params=params,
    )


def pipedrive_request(path, method="GET", payload=None, params=None):
    params = dict(params or {})
    params["api_token"] = load_keychain_secret(PIPEDRIVE_KEYCHAIN_SERVICE)
    return api_json_request(
        PIPEDRIVE_API_BASE,
        path,
        {},
        method=method,
        payload=payload,
        params=params,
    )


def twilio_account_sid(required=True):
    return load_keychain_secret(TWILIO_ACCOUNT_SID_KEYCHAIN_SERVICE, required=required)


def twilio_auth_pair():
    api_key_sid = load_keychain_secret(TWILIO_API_KEY_SID_KEYCHAIN_SERVICE, required=False)
    api_key_secret = load_keychain_secret(TWILIO_API_KEY_SECRET_KEYCHAIN_SERVICE, required=False)
    if api_key_sid and api_key_secret:
        return api_key_sid, api_key_secret, "api_key"
    account_sid = twilio_account_sid(required=True)
    auth_token = load_keychain_secret(TWILIO_AUTH_TOKEN_KEYCHAIN_SERVICE)
    return account_sid, auth_token, "auth_token"


def twilio_default_from_number():
    return load_keychain_secret(TWILIO_DEFAULT_FROM_NUMBER_KEYCHAIN_SERVICE, required=False) or load_keychain_secret(
        "codex.twilio.from_number",
        required=False,
    )


def twilio_headers():
    username, password, auth_mode = twilio_auth_pair()
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token}", "X-Kim-Twilio-Auth-Mode": auth_mode}


def twilio_request(path, method="GET", payload=None, params=None, timeout=12):
    account_sid = twilio_account_sid(required=True)
    headers = twilio_headers()
    headers.pop("X-Kim-Twilio-Auth-Mode", None)
    base = f"{TWILIO_API_BASE}/Accounts/{urllib.parse.quote(account_sid)}"
    if method.upper() == "GET":
        return api_json_request(base, path, headers, method=method, params=params, timeout=timeout)
    return form_json_request(base, path, headers, method=method, payload=payload, params=params, timeout=timeout)


def normalize_phone_number(value):
    raw = str(value or "").strip()
    if raw.lower().startswith("whatsapp:"):
        return "whatsapp:" + normalize_phone_number(raw.split(":", 1)[1])
    if raw.startswith("+"):
        return "+" + re.sub(r"\D+", "", raw[1:])
    digits = re.sub(r"\D+", "", raw)
    return f"+{digits}" if digits else ""


def crm_id(prefix):
    return prefix + "-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S-") + secrets.token_hex(3).upper()


def crm_slug(value):
    text = unicodedata.normalize("NFKD", str(value or "").strip()).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return text[:80] or "sin-nombre"


def active_crm_root():
    return ACTIVE_CRM_ROOT or CRM_ROOT


def active_crm_db():
    return ACTIVE_CRM_DB or (active_crm_root() / "crm.sqlite")


def crm_connect():
    global ACTIVE_CRM_ROOT, ACTIVE_CRM_DB
    candidates = [active_crm_root()] if ACTIVE_CRM_ROOT else [CRM_ROOT, RUNTIME_CRM_ROOT]
    last_error = None
    for root in candidates:
        try:
            root.mkdir(parents=True, exist_ok=True)
            for folder in [
                root / "contacts" / "by_type",
                root / "companies",
                root / "interactions" / "calls",
                root / "interactions" / "sms",
                root / "schedules",
            ]:
                folder.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(root / "crm.sqlite")
            ACTIVE_CRM_ROOT = root
            ACTIVE_CRM_DB = root / "crm.sqlite"
            break
        except (sqlite3.DatabaseError, OSError, PermissionError) as exc:
            last_error = exc
            if root == RUNTIME_CRM_ROOT:
                raise
    else:
        raise last_error or RuntimeError("No pude abrir CRM local.")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS companies (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            company_type TEXT DEFAULT '',
            industry TEXT DEFAULT '',
            status TEXT DEFAULT 'active',
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS contacts (
            id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            phone_e164 TEXT UNIQUE,
            email TEXT,
            company_id TEXT,
            contact_type TEXT DEFAULT 'client',
            source TEXT DEFAULT 'kim_live',
            country TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(company_id) REFERENCES companies(id)
        );
        CREATE TABLE IF NOT EXISTS interactions (
            id TEXT PRIMARY KEY,
            contact_id TEXT,
            company_id TEXT,
            channel TEXT NOT NULL,
            direction TEXT NOT NULL,
            provider TEXT DEFAULT 'twilio',
            external_sid TEXT DEFAULT '',
            from_value TEXT DEFAULT '',
            to_value TEXT DEFAULT '',
            status TEXT DEFAULT '',
            body TEXT DEFAULT '',
            transcript_path TEXT DEFAULT '',
            metadata_json TEXT DEFAULT '{}',
            occurred_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(contact_id) REFERENCES contacts(id),
            FOREIGN KEY(company_id) REFERENCES companies(id)
        );
        CREATE TABLE IF NOT EXISTS scheduled_actions (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'pending',
            provider TEXT NOT NULL,
            action TEXT NOT NULL,
            due_at TEXT NOT NULL,
            timezone TEXT DEFAULT 'America/Mexico_City',
            contact_id TEXT,
            company_id TEXT,
            to_value TEXT DEFAULT '',
            from_value TEXT DEFAULT '',
            payload_json TEXT NOT NULL,
            result_json TEXT DEFAULT '',
            attempts INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            executed_at TEXT DEFAULT '',
            FOREIGN KEY(contact_id) REFERENCES contacts(id),
            FOREIGN KEY(company_id) REFERENCES companies(id)
        );
        CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone_e164);
        CREATE INDEX IF NOT EXISTS idx_interactions_sid ON interactions(external_sid);
        CREATE INDEX IF NOT EXISTS idx_scheduled_due ON scheduled_actions(status, due_at);
        """
    )
    conn.commit()
    return conn


def crm_write_readme():
    root = active_crm_root()
    root.mkdir(parents=True, exist_ok=True)
    readme = root / "README.md"
    if readme.exists():
        return
    readme.write_text(
        "# BIFROST CRM\n\n"
        "CRM local de Kim Live. La fuente estructurada es `crm.sqlite`.\n\n"
        "- `contacts/by_type/`: fichas Markdown exportadas por tipo de contacto.\n"
        "- `companies/`: espacio para expedientes por empresa.\n"
        "- `interactions/calls/`: llamadas y transcripciones relacionadas.\n"
        "- `interactions/sms/`: SMS/WhatsApp y respuestas.\n"
        "- `schedules/`: acciones programadas confirmadas.\n\n"
        "Regla: Kim puede preparar llamadas/SMS y programarlas, pero las acciones hacia terceros requieren confirmacion explicita.\n",
        encoding="utf-8",
    )


def crm_company_id(conn, name="", company_type="", industry="", notes=""):
    clean = str(name or "").strip()
    if not clean:
        return None
    now = now_iso()
    row = conn.execute("SELECT id FROM companies WHERE lower(name)=lower(?)", (clean,)).fetchone()
    if row:
        conn.execute(
            "UPDATE companies SET company_type=COALESCE(NULLIF(?, ''), company_type), industry=COALESCE(NULLIF(?, ''), industry), notes=COALESCE(NULLIF(?, ''), notes), updated_at=? WHERE id=?",
            (company_type or "", industry or "", notes or "", now, row["id"]),
        )
        return row["id"]
    company_id = crm_id("CO")
    conn.execute(
        "INSERT INTO companies (id, name, company_type, industry, notes, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (company_id, clean, company_type or "", industry or "", notes or "", now, now),
    )
    return company_id


def crm_export_contact(contact):
    contact_type = crm_slug(contact.get("contact_type") or "client")
    folder = active_crm_root() / "contacts" / "by_type" / contact_type
    folder.mkdir(parents=True, exist_ok=True)
    label = contact.get("display_name") or contact.get("phone_e164") or contact.get("email") or contact.get("id")
    path = folder / f"{crm_slug(label)}.md"
    text = (
        f"# {label}\n\n"
        f"- ID: {contact.get('id', '')}\n"
        f"- Tipo: {contact.get('contact_type', '')}\n"
        f"- Telefono: {contact.get('phone_e164', '')}\n"
        f"- Email: {contact.get('email', '')}\n"
        f"- Empresa ID: {contact.get('company_id', '')}\n"
        f"- Fuente: {contact.get('source', '')}\n"
        f"- Actualizado: {contact.get('updated_at', '')}\n\n"
        f"Notas:\n{contact.get('notes', '')}\n"
    )
    path.write_text(text, encoding="utf-8")
    return str(path)


def crm_upsert_contact(parameters=None, source="kim_live"):
    parameters = parameters or {}
    phone = normalize_phone_number(first_value(parameters, "phone", "phone_e164", "telefono", "to", "from", "recipient", default=""))
    email = str(first_value(parameters, "email", "correo", default="") or "").strip()
    display_name = str(first_value(parameters, "display_name", "name", "nombre", "client_name", "contact_name", default="") or "").strip()
    if not display_name:
        display_name = phone or email or "Contacto Kim"
    contact_type = str(first_value(parameters, "contact_type", "type", "tipo", default="client") or "client").strip().lower()
    company_name = str(first_value(parameters, "company", "company_name", "empresa", default="") or "").strip()
    notes = str(first_value(parameters, "notes", "note", "description", "body", default="") or "").strip()
    country = str(first_value(parameters, "country", "pais", default="") or "").strip()
    now = now_iso()
    with crm_connect() as conn:
        company_id = crm_company_id(
            conn,
            company_name,
            company_type=str(first_value(parameters, "company_type", "tipo_empresa", default="") or ""),
            industry=str(first_value(parameters, "industry", "industria", default="") or ""),
        )
        row = None
        if phone:
            row = conn.execute("SELECT * FROM contacts WHERE phone_e164=?", (phone,)).fetchone()
        if row is None and email:
            row = conn.execute("SELECT * FROM contacts WHERE lower(email)=lower(?)", (email,)).fetchone()
        if row:
            contact_id = row["id"]
            conn.execute(
                """
                UPDATE contacts
                SET display_name=COALESCE(NULLIF(?, ''), display_name),
                    phone_e164=COALESCE(NULLIF(?, ''), phone_e164),
                    email=COALESCE(NULLIF(?, ''), email),
                    company_id=COALESCE(?, company_id),
                    contact_type=COALESCE(NULLIF(?, ''), contact_type),
                    country=COALESCE(NULLIF(?, ''), country),
                    notes=CASE WHEN ? != '' AND instr(notes, ?) = 0 THEN trim(notes || char(10) || ?) ELSE notes END,
                    updated_at=?
                WHERE id=?
                """,
                (display_name, phone, email, company_id, contact_type, country, notes, notes, notes, now, contact_id),
            )
        else:
            contact_id = crm_id("CT")
            conn.execute(
                """
                INSERT INTO contacts (id, display_name, phone_e164, email, company_id, contact_type, source, country, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (contact_id, display_name, phone or None, email or None, company_id, contact_type, source, country, notes, now, now),
            )
        conn.commit()
        contact = dict(conn.execute("SELECT * FROM contacts WHERE id=?", (contact_id,)).fetchone())
    crm_write_readme()
    contact["markdown_path"] = crm_export_contact(contact)
    return contact


def crm_find_contact_by_phone(phone):
    phone = normalize_phone_number(phone)
    if not phone:
        return None
    with crm_connect() as conn:
        row = conn.execute("SELECT * FROM contacts WHERE phone_e164=?", (phone,)).fetchone()
        return dict(row) if row else None


def crm_record_interaction(channel, direction, from_value="", to_value="", status="", body="", external_sid="", transcript_path="", metadata=None, contact_hint=None):
    metadata = metadata or {}
    contact_hint = contact_hint or {}
    counterparty = from_value if direction == "inbound" else to_value
    contact = crm_find_contact_by_phone(counterparty)
    if not contact and counterparty:
        contact = crm_upsert_contact(
            {
                "phone": counterparty,
                "display_name": contact_hint.get("display_name") or counterparty or "Contacto Twilio",
                "contact_type": contact_hint.get("contact_type") or "client",
                "company": contact_hint.get("company") or "",
                "notes": contact_hint.get("notes") or "Contacto creado automaticamente por interaccion Twilio.",
            },
            source="twilio",
        )
    contact = contact or {}
    interaction_id = crm_id("IN")
    now = now_iso()
    with crm_connect() as conn:
        conn.execute(
            """
            INSERT INTO interactions
            (id, contact_id, company_id, channel, direction, provider, external_sid, from_value, to_value, status, body, transcript_path, metadata_json, occurred_at, created_at)
            VALUES (?, ?, ?, ?, ?, 'twilio', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                interaction_id,
                contact.get("id"),
                contact.get("company_id"),
                channel,
                direction,
                external_sid or "",
                from_value or "",
                to_value or "",
                status or "",
                body or "",
                transcript_path or "",
                json.dumps(metadata, ensure_ascii=False),
                metadata.get("occurred_at") or now,
                now,
            ),
        )
        conn.commit()
    return {"id": interaction_id, "contact_id": contact.get("id"), "contact": contact}


def crm_status():
    with crm_connect() as conn:
        crm_write_readme()
        return {
            "ok": True,
            "provider": "crm",
            "database": str(active_crm_db()),
            "root": str(active_crm_root()),
            "preferred_root": str(CRM_ROOT),
            "fallback_active": active_crm_root() != CRM_ROOT,
            "contacts": conn.execute("SELECT count(*) AS c FROM contacts").fetchone()["c"],
            "companies": conn.execute("SELECT count(*) AS c FROM companies").fetchone()["c"],
            "interactions": conn.execute("SELECT count(*) AS c FROM interactions").fetchone()["c"],
            "scheduled_actions": conn.execute("SELECT count(*) AS c FROM scheduled_actions").fetchone()["c"],
        }


def crm_list_contacts(parameters=None):
    parameters = parameters or {}
    limit = int(first_value(parameters, "limit", default=25) or 25)
    contact_type = str(first_value(parameters, "contact_type", "type", "tipo", default="") or "").strip().lower()
    query = str(first_value(parameters, "query", "q", "search", default="") or "").strip().lower()
    sql = "SELECT * FROM contacts"
    clauses = []
    values = []
    if contact_type:
        clauses.append("contact_type=?")
        values.append(contact_type)
    if query:
        clauses.append("(lower(display_name) LIKE ? OR phone_e164 LIKE ? OR lower(email) LIKE ?)")
        like = f"%{query}%"
        values.extend([like, like, like])
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY updated_at DESC LIMIT ?"
    values.append(max(1, min(limit, 100)))
    with crm_connect() as conn:
        return {"ok": True, "provider": "crm", "action": "list_contacts", "contacts": [dict(row) for row in conn.execute(sql, values).fetchall()]}


def twilio_number_summary(item):
    capabilities = item.get("capabilities") or {}
    return {
        "sid": item.get("sid"),
        "phone_number": item.get("phone_number"),
        "friendly_name": item.get("friendly_name"),
        "capabilities": {
            "voice": bool(capabilities.get("voice")),
            "sms": bool(capabilities.get("sms")),
            "mms": bool(capabilities.get("mms")),
        },
        "voice_url": item.get("voice_url"),
        "sms_url": item.get("sms_url"),
    }


def twilio_list_numbers(parameters=None):
    parameters = parameters or {}
    limit = int(first_value(parameters, "limit", "page_size", default=50) or 50)
    data = twilio_request("/IncomingPhoneNumbers.json", params={"PageSize": max(1, min(limit, 100))})
    numbers = [twilio_number_summary(item) for item in data.get("incoming_phone_numbers", [])]
    default_from = twilio_default_from_number()
    return {
        "ok": True,
        "provider": "twilio",
        "action": "list_numbers",
        "default_from_number": default_from,
        "numbers": numbers,
        "count": len(numbers),
    }


def twilio_status(live=False):
    account_sid = twilio_account_sid(required=False)
    has_auth_token = bool(load_keychain_secret(TWILIO_AUTH_TOKEN_KEYCHAIN_SERVICE, required=False))
    has_api_key = bool(load_keychain_secret(TWILIO_API_KEY_SID_KEYCHAIN_SERVICE, required=False)) and bool(
        load_keychain_secret(TWILIO_API_KEY_SECRET_KEYCHAIN_SERVICE, required=False)
    )
    status = {
        "configured": bool(account_sid and (has_auth_token or has_api_key)),
        "account_sid_suffix": account_sid[-6:] if account_sid else "",
        "auth_modes": {
            "auth_token": has_auth_token,
            "api_key": has_api_key,
        },
        "default_from_number": twilio_default_from_number(),
        "write_requires_confirmation": True,
        "capabilities": [
            "status",
            "list_numbers",
            "send_sms",
            "send_whatsapp",
            "call_phone",
            "schedule_call",
            "schedule_sms",
            "call_report",
            "latest_call",
            "list_calls",
        ],
    }
    if live and status["configured"]:
        try:
            account = twilio_request(".json")
            status["account"] = {
                "status": account.get("status"),
                "type": account.get("type"),
                "friendly_name": account.get("friendly_name"),
            }
            status["numbers"] = twilio_list_numbers().get("numbers", [])
            status["live_ok"] = True
        except Exception as exc:
            status["live_ok"] = False
            status["error"] = brief(str(exc), 260)
    return status


def twilio_message_preview(parameters, channel="sms"):
    to = normalize_phone_number(first_value(parameters, "to", "recipient", "phone", "telefono", "destinatario"))
    body = str(first_value(parameters, "body", "message", "text", "content", "mensaje") or "").strip()
    from_number = normalize_phone_number(first_value(parameters, "from", "from_number", "sender", default=twilio_default_from_number()))
    messaging_service_sid = str(first_value(parameters, "messaging_service_sid", "service_sid", default="") or "").strip()
    if channel == "whatsapp":
        if to and not to.startswith("whatsapp:"):
            to = f"whatsapp:{to}"
        if from_number and not from_number.startswith("whatsapp:"):
            from_number = f"whatsapp:{from_number}"
    if not to:
        raise ValueError("Falta destinatario to para Twilio.")
    if not body:
        raise ValueError("Falta body/message para Twilio.")
    if not from_number and not messaging_service_sid:
        raise ValueError("Falta from_number o messaging_service_sid para Twilio.")
    return {
        "to": to,
        "from": from_number,
        "messaging_service_sid": messaging_service_sid,
        "body_preview": brief(body, 600),
        "body_length": len(body),
        "channel": channel,
    }


def twilio_send_message(parameters, confirm=False, channel="sms"):
    parameters = parameters or {}
    preview = twilio_message_preview(parameters, channel=channel)
    payload = {
        "To": preview["to"],
        "Body": str(first_value(parameters, "body", "message", "text", "content", "mensaje") or "").strip(),
    }
    status_callback = str(first_value(parameters, "status_callback", "callback_url", default="https://kim.aipeople.app/twilio/status") or "").strip()
    if status_callback:
        payload["StatusCallback"] = status_callback
    if preview["messaging_service_sid"]:
        payload["MessagingServiceSid"] = preview["messaging_service_sid"]
    else:
        payload["From"] = preview["from"]
    action = "send_whatsapp" if channel == "whatsapp" else "send_sms"
    if not confirm:
        return confirmation_preview(
            "twilio",
            action,
            f"Enviar {channel.upper()} Twilio a {preview['to']}.",
            preview,
            execution_parameters={**parameters, "channel": channel, "from_number": preview["from"]},
        )
    result = twilio_request("/Messages.json", method="POST", payload=payload)
    event = {
        "ok": True,
        "provider": "twilio",
        "action": action,
        "channel": channel,
        "sid": result.get("sid"),
        "status": result.get("status"),
        "to": result.get("to"),
        "from": result.get("from"),
        "error_code": result.get("error_code"),
        "error_message": result.get("error_message"),
        "confirmed": True,
        "sent_at": now_iso(),
    }
    append_jsonl_any([TWILIO_SMS_LOG, RUNTIME_TWILIO_SMS_LOG], event)
    append_memory("twilio_message_sent", event)
    crm_record_interaction(
        "whatsapp" if channel == "whatsapp" else "sms",
        "outbound",
        from_value=event.get("from", ""),
        to_value=event.get("to", ""),
        status=event.get("status", ""),
        body=payload.get("Body", ""),
        external_sid=event.get("sid", ""),
        metadata=event,
    )
    return event


def twilio_add_query_param(url, key, value):
    if not value:
        return url
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    query[key] = [str(value)]
    return urllib.parse.urlunparse(parsed._replace(query=urllib.parse.urlencode(query, doseq=True)))


def twilio_call_context_id():
    return "CTX-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S-") + secrets.token_hex(3).upper()


def load_twilio_call_context_state():
    state = {"contexts": {}}
    for path in [TWILIO_CALL_CONTEXTS, RUNTIME_TWILIO_CALL_CONTEXTS]:
        payload = read_json_file(path, {})
        if not isinstance(payload, dict):
            continue
        contexts = payload.get("contexts", {})
        if isinstance(contexts, dict):
            state["contexts"].update(contexts)
        if payload.get("updated_at"):
            state["updated_at"] = payload.get("updated_at")
    state.setdefault("contexts", {})
    return state


def save_twilio_call_context_state(state):
    state["updated_at"] = now_iso()
    last_error = None
    wrote = False
    for path in [TWILIO_CALL_CONTEXTS, RUNTIME_TWILIO_CALL_CONTEXTS]:
        try:
            write_json_file(path, state)
            wrote = True
        except (PermissionError, OSError) as exc:
            last_error = exc
    if not wrote and last_error:
        raise last_error


def normalize_call_context_value(value):
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value).strip()


def parse_json_object_from_text(text):
    text = (text or "").strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        return {}
    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def synthesize_twilio_context_from_transcript(explicit, transcript):
    transcript = (transcript or "").strip()
    if not transcript:
        return explicit
    missing = [key for key in ["contact_name", "call_context", "objective", "questions", "report_to_doctor"] if not explicit.get(key)]
    if not missing:
        return explicit
    prompt = (
        "Extrae contexto operativo para una llamada telefonica de Kim Live. "
        "Responde SOLO un JSON valido, sin markdown. No inventes datos: si no aparece, usa string vacio. "
        "Campos: contact_name, relationship, company, call_context, objective, instructions, "
        "questions, message_to_deliver, report_to_doctor, success_criteria, tone.\n\n"
        "El objetivo es que Kim pueda llamar a una tercera persona con contexto y despues reportar al doctor "
        "que se dijo y que respondio la persona.\n\n"
        f"Conversacion activa:\n{brief(transcript, 7000)}"
    )
    try:
        response, model = openai_response_with_fallback(PHONE_REPLY_MODEL_CANDIDATES, {"input": prompt, "max_output_tokens": 700})
        parsed = parse_json_object_from_text(output_text_from_response(response))
        for key in [
            "contact_name",
            "relationship",
            "company",
            "call_context",
            "objective",
            "instructions",
            "questions",
            "message_to_deliver",
            "report_to_doctor",
            "success_criteria",
            "tone",
        ]:
            if not explicit.get(key) and parsed.get(key):
                explicit[key] = normalize_call_context_value(parsed.get(key))
        append_memory(
            "twilio_call_context_synthesized",
            {"model": model, "missing_before": missing, "filled": [key for key in missing if explicit.get(key)]},
        )
    except Exception as exc:
        append_memory("twilio_call_context_synthesis_error", {"error": brief(str(exc), 500)})
    return explicit


def twilio_context_from_parameters(parameters, preview, transcript=""):
    parameters = parameters or {}
    transcript = transcript or str(first_value(parameters, "_conversation_transcript", "transcript", default="") or "")
    explicit = {
        "contact_name": first_value(parameters, "contact_name", "client_name", "name", "nombre", default=""),
        "relationship": first_value(parameters, "relationship", "relacion", "role", "rol", default=""),
        "company": first_value(parameters, "company", "empresa", default=""),
        "call_context": first_value(parameters, "call_context", "context", "client_context", "contexto", default=""),
        "objective": first_value(parameters, "objective", "goal", "mission", "objetivo", "mision", default=""),
        "instructions": first_value(parameters, "instructions", "instruction", "prompt", "instrucciones", default=""),
        "questions": first_value(parameters, "questions", "preguntas", "ask", "asks", default=""),
        "message_to_deliver": first_value(parameters, "message_to_deliver", "message", "mensaje", "script", default=""),
        "report_to_doctor": first_value(parameters, "report_to_doctor", "report", "reporte", "return_with", default=""),
        "success_criteria": first_value(parameters, "success_criteria", "criterio_exito", "desired_outcome", default=""),
        "tone": first_value(parameters, "tone", "tono", default=""),
    }
    explicit = {key: normalize_call_context_value(value) for key, value in explicit.items()}
    transcript_excerpt = brief(sanitize_text_for_log(transcript), 3200) if transcript else ""
    if transcript_excerpt:
        explicit = synthesize_twilio_context_from_transcript(explicit, transcript)
    has_context = any(value for key, value in explicit.items() if key != "tone") or bool(transcript_excerpt)
    if not has_context:
        return {}
    if not explicit.get("tone"):
        explicit["tone"] = "amable, natural y profesional"
    context = {
        "id": twilio_call_context_id(),
        "status": "prepared",
        "created_at": now_iso(),
        "to": preview.get("to", ""),
        "from": preview.get("from", ""),
        "source": "kim_live_twilio",
        **explicit,
    }
    if transcript_excerpt:
        context["conversation_excerpt"] = transcript_excerpt
    return context


def store_twilio_call_context(context):
    if not context:
        return ""
    state = load_twilio_call_context_state()
    state["contexts"][context["id"]] = context
    save_twilio_call_context_state(state)
    append_memory("twilio_call_context_prepared", {"context_id": context["id"], "to": context.get("to"), "objective": brief(context.get("objective") or context.get("instructions") or context.get("call_context"), 240)})
    return context["id"]


def update_twilio_call_context(context_id="", call_sid="", updates=None):
    updates = updates or {}
    state = load_twilio_call_context_state()
    context = state.get("contexts", {}).get(context_id or "")
    if not context and call_sid:
        for item in state.get("contexts", {}).values():
            if item.get("call_sid") == call_sid:
                context = item
                context_id = item.get("id")
                break
    if not context:
        return None
    context.update({key: value for key, value in updates.items() if value is not None})
    if call_sid:
        context["call_sid"] = call_sid
    context["updated_at"] = now_iso()
    state["contexts"][context_id] = context
    save_twilio_call_context_state(state)
    return context


def load_twilio_call_context(call_sid="", context_id=""):
    state = load_twilio_call_context_state()
    if context_id and context_id in state.get("contexts", {}):
        return state["contexts"][context_id]
    if call_sid:
        for context in state.get("contexts", {}).values():
            if context.get("call_sid") == call_sid:
                return context
    return {}


def complete_twilio_call_context(call_sid="", context_id="", transcript_path="", summary="", status="completed"):
    return update_twilio_call_context(
        context_id=context_id,
        call_sid=call_sid,
        updates={
            "status": status,
            "transcript_path": transcript_path,
            "summary": brief(summary, 1200),
            "completed_at": now_iso(),
        },
    )


def call_transcript_from_text(text):
    text = (text or "").strip()
    marker = "\n## Transcript\n"
    if marker in text:
        return text.split(marker, 1)[1].strip()
    return text


def twilio_context_for_entry(entry, text="", contexts=None):
    contexts = contexts or []
    haystack = "\n".join(
        [
            json.dumps(entry, ensure_ascii=False),
            text or "",
        ]
    )
    entry_path = str(entry.get("path") or "")
    for context in contexts:
        if context.get("transcript_path") and str(context.get("transcript_path")) == entry_path:
            return context
        if context.get("id") and context.get("id") in haystack:
            return context
        if context.get("call_sid") and context.get("call_sid") in haystack:
            return context
    return {}


def twilio_call_report(parameters=None):
    parameters = parameters or {}
    raw_limit = first_value(parameters, "limit", "count", default=1)
    try:
        limit = max(1, min(int(raw_limit or 1), 10))
    except (TypeError, ValueError):
        limit = 1
    call_sid = str(first_value(parameters, "call_sid", "sid", "callSid", default="") or "").strip()
    context_id = str(first_value(parameters, "context_id", "kim_context_id", default="") or "").strip()
    phone = normalize_phone_number(first_value(parameters, "phone", "to", "from", "telefono", "recipient", default=""))
    contact_query = str(first_value(parameters, "contact_name", "client_name", "name", "query", default="") or "").strip().lower()
    state = load_twilio_call_context_state()
    contexts = list(state.get("contexts", {}).values())
    filters = {
        "call_sid": call_sid,
        "context_id": context_id,
        "phone": phone,
        "contact_name": contact_query,
    }
    has_filter = any(filters.values())
    calls = []
    seen = set()
    for entry in reversed(load_call_entries(limit=5000)):
        entry_key = (entry.get("session_id"), entry.get("path"))
        if entry_key in seen:
            continue
        seen.add(entry_key)
        path_text = entry.get("path") or ""
        text = read_text_tail(pathlib.Path(path_text), limit=60000) if path_text else ""
        context = twilio_context_for_entry(entry, text=text, contexts=contexts)
        is_twilio_entry = bool(context) or "Canal: Twilio" in text or "\nCallSid:" in text or "Twilio Media Stream" in text
        haystack = "\n".join(
            [
                json.dumps(entry, ensure_ascii=False),
                json.dumps(context, ensure_ascii=False),
                text,
            ]
        )
        normalized_haystack = haystack.lower()
        if not is_twilio_entry:
            continue
        if call_sid and call_sid not in haystack:
            continue
        if context_id and context_id not in haystack:
            continue
        if phone and phone not in haystack:
            continue
        if contact_query and contact_query not in normalized_haystack:
            continue
        transcript = call_transcript_from_text(text)
        calls.append(
            {
                "session_id": entry.get("session_id", ""),
                "call_number": entry.get("call_number"),
                "title": entry.get("title", ""),
                "started_at": entry.get("started_at", ""),
                "saved_at": entry.get("saved_at", ""),
                "path": entry.get("path", ""),
                "summary": entry.get("summary", ""),
                "transcript_excerpt": brief(transcript, 9000),
                "call_sid": context.get("call_sid") or call_sid,
                "context_id": context.get("id") or context_id,
                "to": context.get("to", ""),
                "from": context.get("from", ""),
                "status": context.get("status", ""),
                "contact_name": context.get("contact_name", ""),
                "objective": context.get("objective", ""),
                "report_to_doctor": context.get("report_to_doctor", ""),
                "call_context": brief(context.get("call_context", ""), 1000),
            }
        )
        if len(calls) >= limit:
            break
    if not calls and has_filter:
        for context in reversed(contexts):
            haystack = json.dumps(context, ensure_ascii=False)
            normalized_haystack = haystack.lower()
            if call_sid and call_sid != context.get("call_sid"):
                continue
            if context_id and context_id != context.get("id"):
                continue
            if phone and phone not in haystack:
                continue
            if contact_query and contact_query not in normalized_haystack:
                continue
            transcript_path = context.get("transcript_path", "")
            text = read_text_tail(pathlib.Path(transcript_path), limit=60000) if transcript_path else ""
            calls.append(
                {
                    "session_id": pathlib.Path(transcript_path).stem if transcript_path else "",
                    "path": transcript_path,
                    "summary": context.get("summary", ""),
                    "transcript_excerpt": brief(call_transcript_from_text(text), 9000),
                    "call_sid": context.get("call_sid", ""),
                    "context_id": context.get("id", ""),
                    "to": context.get("to", ""),
                    "from": context.get("from", ""),
                    "status": context.get("status", ""),
                    "contact_name": context.get("contact_name", ""),
                    "objective": context.get("objective", ""),
                    "report_to_doctor": context.get("report_to_doctor", ""),
                    "call_context": brief(context.get("call_context", ""), 1000),
                }
            )
            if len(calls) >= limit:
                break
    return {
        "ok": bool(calls),
        "provider": "twilio",
        "action": "call_report",
        "filters": {key: value for key, value in filters.items() if value},
        "calls": calls,
        "message": "Reporte de llamada encontrado." if calls else "No encontre llamadas que coincidan en BIFROST/MEMORY/calls.",
    }


def twilio_call_preview(parameters):
    to = normalize_phone_number(first_value(parameters, "to", "recipient", "phone", "telefono", "destinatario"))
    from_number = normalize_phone_number(first_value(parameters, "from", "from_number", "sender", default=twilio_default_from_number()))
    url = str(first_value(parameters, "url", "voice_url", "twiml_url", default="https://kim.aipeople.app/twilio/voice") or "").strip()
    status_callback = str(first_value(parameters, "status_callback", "callback_url", default="https://kim.aipeople.app/twilio/status") or "").strip()
    if not to:
        raise ValueError("Falta destinatario to para llamada Twilio.")
    if not from_number:
        raise ValueError("Falta from_number para llamada Twilio.")
    if not url:
        raise ValueError("Falta url/voice_url para llamada Twilio.")
    return {
        "to": to,
        "from": from_number,
        "url": url,
        "status_callback": status_callback,
        "timeout": int(first_value(parameters, "timeout", default=35) or 35),
    }


def twilio_start_call(parameters, confirm=False):
    parameters = parameters or {}
    preview = twilio_call_preview(parameters)
    call_context = twilio_context_from_parameters(parameters, preview)
    if not confirm:
        preview_with_context = dict(preview)
        execution_parameters = {**parameters, "from_number": preview["from"], "url": preview["url"]}
        if call_context:
            preview_with_context["call_context"] = {
                "contact_name": call_context.get("contact_name"),
                "objective": brief(call_context.get("objective") or call_context.get("instructions") or call_context.get("call_context"), 500),
                "report_to_doctor": brief(call_context.get("report_to_doctor"), 300),
            }
            for key in [
                "contact_name",
                "relationship",
                "company",
                "call_context",
                "objective",
                "instructions",
                "questions",
                "message_to_deliver",
                "report_to_doctor",
                "success_criteria",
                "tone",
            ]:
                if call_context.get(key):
                    execution_parameters[key] = call_context[key]
        return confirmation_preview(
            "twilio",
            "call_phone",
            f"Llamar por Twilio a {preview['to']} desde {preview['from']}.",
            preview_with_context,
            execution_parameters=execution_parameters,
        )
    context_id = store_twilio_call_context(call_context)
    call_url = twilio_add_query_param(preview["url"], "kim_context_id", context_id)
    payload = {
        "To": preview["to"],
        "From": preview["from"],
        "Url": call_url,
        "Timeout": str(preview["timeout"]),
    }
    if preview["status_callback"]:
        payload["StatusCallback"] = preview["status_callback"]
        payload["StatusCallbackEvent"] = ["initiated", "ringing", "answered", "completed"]
    result = twilio_request("/Calls.json", method="POST", payload=payload)
    event = {
        "ok": True,
        "provider": "twilio",
        "action": "call_phone",
        "sid": result.get("sid"),
        "status": result.get("status"),
        "to": result.get("to"),
        "from": result.get("from"),
        "direction": result.get("direction"),
        "context_id": context_id,
        "confirmed": True,
        "started_at": now_iso(),
    }
    if context_id:
        update_twilio_call_context(
            context_id=context_id,
            call_sid=result.get("sid", ""),
            updates={
                "status": result.get("status") or "queued",
                "to": result.get("to") or preview["to"],
                "from": result.get("from") or preview["from"],
                "call_url": call_url,
            },
        )
    append_jsonl_any([TWILIO_CALL_LOG, RUNTIME_TWILIO_CALL_LOG], event)
    append_memory("twilio_call_started", event)
    crm_record_interaction(
        "call",
        "outbound",
        from_value=event.get("from", ""),
        to_value=event.get("to", ""),
        status=event.get("status", ""),
        external_sid=event.get("sid", ""),
        metadata=event,
        contact_hint={
            "display_name": call_context.get("contact_name") if call_context else "",
            "company": call_context.get("company") if call_context else "",
            "notes": call_context.get("relationship") if call_context else "",
        },
    )
    return event


def parse_due_at(parameters=None):
    parameters = parameters or {}
    for key in ["delay_seconds", "in_seconds", "seconds"]:
        value = first_value(parameters, key, default="")
        if value not in (None, ""):
            return (dt.datetime.now() + dt.timedelta(seconds=int(float(value)))).isoformat(timespec="seconds")
    for key in ["delay_minutes", "in_minutes", "minutes"]:
        value = first_value(parameters, key, default="")
        if value not in (None, ""):
            return (dt.datetime.now() + dt.timedelta(minutes=float(value))).isoformat(timespec="seconds")
    raw = str(first_value(parameters, "due_at", "scheduled_at", "run_at", "datetime", "date_time", "cuando", default="") or "").strip()
    if not raw:
        date_value = str(first_value(parameters, "date", "fecha", default="") or "").strip()
        time_value = str(first_value(parameters, "time", "hora", default="") or "").strip()
        raw = f"{date_value}T{time_value}" if date_value and time_value else date_value
    if not raw:
        raise ValueError("Falta due_at/scheduled_at o delay_minutes para programar la accion.")
    raw = raw.replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError("No pude interpretar la fecha/hora programada. Usa ISO, por ejemplo 2026-05-14T09:30:00.") from exc
    return parsed.isoformat(timespec="seconds")


def due_at_is_ready(due_at):
    parsed = dt.datetime.fromisoformat(str(due_at).replace("Z", "+00:00"))
    now = dt.datetime.now(parsed.tzinfo) if parsed.tzinfo else dt.datetime.now()
    return parsed <= now


def schedule_twilio_action(action, parameters=None, confirm=False):
    parameters = dict(parameters or {})
    target_action = "call_phone" if action in {"schedule_call", "programar_llamada", "agendar_llamada"} else "send_sms"
    due_at = parse_due_at(parameters)
    if target_action == "call_phone":
        preview = twilio_call_preview(parameters)
        summary = f"Programar llamada a {preview['to']} para {due_at}."
    else:
        preview = twilio_message_preview(parameters, channel="sms")
        summary = f"Programar SMS a {preview['to']} para {due_at}."
    if not confirm:
        return confirmation_preview(
            "twilio",
            action,
            summary,
            {**preview, "due_at": due_at, "target_action": target_action},
            execution_parameters={**parameters, "due_at": due_at, "target_action": target_action},
        )
    contact = crm_upsert_contact(
        {
            "phone": preview.get("to"),
            "display_name": first_value(parameters, "contact_name", "name", "client_name", "nombre", default=preview.get("to")),
            "company": first_value(parameters, "company", "empresa", default=""),
            "contact_type": first_value(parameters, "contact_type", "tipo", default="client"),
            "notes": "Contacto asociado a accion Twilio programada.",
        },
        source="twilio_schedule",
    )
    schedule_id = crm_id("SC")
    now = now_iso()
    payload = {**parameters, "due_at": due_at, "target_action": target_action}
    with crm_connect() as conn:
        conn.execute(
            """
            INSERT INTO scheduled_actions
            (id, status, provider, action, due_at, timezone, contact_id, company_id, to_value, from_value, payload_json, created_at, updated_at)
            VALUES (?, 'pending', 'twilio', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                schedule_id,
                target_action,
                due_at,
                str(first_value(parameters, "timezone", "tz", default="America/Mexico_City") or "America/Mexico_City"),
                contact.get("id"),
                contact.get("company_id"),
                preview.get("to"),
                preview.get("from"),
                json.dumps(payload, ensure_ascii=False),
                now,
                now,
            ),
        )
        conn.commit()
    event = {
        "ok": True,
        "provider": "twilio",
        "action": action,
        "scheduled_action_id": schedule_id,
        "target_action": target_action,
        "due_at": due_at,
        "contact_id": contact.get("id"),
        "confirmed": True,
    }
    append_memory("twilio_action_scheduled", event)
    return event


def due_scheduled_actions(limit=10):
    with crm_connect() as conn:
        rows = [dict(row) for row in conn.execute("SELECT * FROM scheduled_actions WHERE status='pending' ORDER BY due_at ASC LIMIT ?", (limit,)).fetchall()]
    return [row for row in rows if due_at_is_ready(row["due_at"])]


def update_scheduled_action(schedule_id, status, result=None):
    now = now_iso()
    with crm_connect() as conn:
        conn.execute(
            "UPDATE scheduled_actions SET status=?, result_json=?, attempts=attempts+1, updated_at=?, executed_at=? WHERE id=?",
            (status, json.dumps(result or {}, ensure_ascii=False), now, now if status in {"done", "failed"} else "", schedule_id),
        )
        conn.commit()


def execute_scheduled_action(row):
    payload = json.loads(row.get("payload_json") or "{}")
    payload["from_number"] = payload.get("from_number") or row.get("from_value") or twilio_default_from_number()
    if row.get("action") == "call_phone":
        result = twilio_start_call(payload, confirm=True)
    elif row.get("action") == "send_sms":
        result = twilio_send_message(payload, confirm=True, channel="sms")
    else:
        raise ValueError(f"Accion programada no soportada: {row.get('action')}")
    update_scheduled_action(row["id"], "done" if result.get("ok") else "failed", result)
    return result


def scheduler_loop():
    while True:
        try:
            for row in due_scheduled_actions():
                try:
                    update_scheduled_action(row["id"], "running", {"started_at": now_iso()})
                    execute_scheduled_action(row)
                except Exception as exc:
                    update_scheduled_action(row["id"], "failed", {"error": brief(str(exc), 800)})
                    append_memory("scheduled_action_error", {"id": row.get("id"), "error": brief(str(exc), 800)})
        except Exception as exc:
            append_memory("scheduler_loop_error", {"error": brief(str(exc), 800)})
        time.sleep(20)


def start_scheduler_once():
    global SCHEDULER_THREAD_STARTED
    with SCHEDULER_LOCK:
        if SCHEDULER_THREAD_STARTED:
            return
        crm_write_readme()
        crm_connect().close()
        thread = threading.Thread(target=scheduler_loop, daemon=True, name="kim-scheduler")
        thread.start()
        SCHEDULER_THREAD_STARTED = True


def run_twilio_bridge(action, parameters, confirm=False):
    action = (action or "").strip().lower()
    parameters = parameters or {}
    if action in {"status", "me"}:
        return {"ok": True, "provider": "twilio", "action": action, "status": twilio_status(live=True)}
    if action in {"list_numbers", "numbers", "incoming_numbers", "phone_numbers"}:
        return twilio_list_numbers(parameters)
    if action in {"send_sms", "sms", "text_message", "mensaje_sms"}:
        return twilio_send_message(parameters, confirm=confirm, channel="sms")
    if action in {"send_whatsapp", "whatsapp", "whatsapp_message"}:
        return twilio_send_message(parameters, confirm=confirm, channel="whatsapp")
    if action in {"call_phone", "call", "make_call", "llamar", "llamada"}:
        return twilio_start_call(parameters, confirm=confirm)
    if action in {"schedule_call", "programar_llamada", "agendar_llamada", "schedule_sms", "programar_sms", "agendar_sms"}:
        return schedule_twilio_action(action, parameters, confirm=confirm)
    if action in {"call_report", "latest_call", "list_calls", "get_call", "call_summary", "call_history", "reporte_llamada", "ultima_llamada"}:
        if action in {"latest_call", "ultima_llamada"}:
            parameters = {**parameters, "limit": 1}
        return twilio_call_report(parameters)
    raise ValueError(f"Accion Twilio no soportada: {action}")


def run_crm_bridge(action, parameters, confirm=False):
    action = (action or "").strip().lower()
    parameters = parameters or {}
    if action in {"status", "estado"}:
        return crm_status()
    if action in {"list_contacts", "contacts", "clientes", "contactos", "search_contacts"}:
        return crm_list_contacts(parameters)
    if action in {"upsert_contact", "create_contact", "save_contact", "guardar_contacto", "crear_contacto"}:
        preview = {
            "display_name": first_value(parameters, "display_name", "name", "nombre", "client_name", "contact_name", default=""),
            "phone": normalize_phone_number(first_value(parameters, "phone", "telefono", "to", "from", default="")),
            "email": first_value(parameters, "email", "correo", default=""),
            "company": first_value(parameters, "company", "empresa", default=""),
            "contact_type": first_value(parameters, "contact_type", "tipo", default="client"),
        }
        if not confirm:
            return confirmation_preview("crm", action, f"Guardar contacto CRM {preview.get('display_name') or preview.get('phone') or preview.get('email')}.", preview, execution_parameters=parameters)
        contact = crm_upsert_contact(parameters, source="kim_live")
        return {"ok": True, "provider": "crm", "action": action, "contact": contact, "confirmed": True}
    if action in {"record_note", "note", "nota"}:
        body = str(first_value(parameters, "body", "note", "notes", "text", "content", default="") or "").strip()
        phone = normalize_phone_number(first_value(parameters, "phone", "telefono", "to", "from", default=""))
        if not body:
            raise ValueError("Falta body/note para registrar nota CRM.")
        if not confirm:
            return confirmation_preview("crm", action, f"Registrar nota CRM para {phone or 'contacto'}.", {"phone": phone, "body": brief(body, 500)}, execution_parameters=parameters)
        interaction = crm_record_interaction("note", "internal", from_value="kim", to_value=phone, body=body, status="recorded", metadata={"source": "kim_live"})
        return {"ok": True, "provider": "crm", "action": action, "interaction": interaction, "confirmed": True}
    raise ValueError(f"Accion CRM no soportada: {action}")


def pipedrive_value_list(value):
    if not value:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    rows = value if isinstance(value, list) else [value]
    result = []
    for item in rows:
        if isinstance(item, dict):
            candidate = item.get("value") or item.get("email") or item.get("phone") or ""
        else:
            candidate = str(item or "")
        candidate = str(candidate or "").strip()
        if candidate:
            result.append(candidate)
    return result


def normalize_pipedrive_person(item):
    item = item or {}
    org = item.get("org_id") if isinstance(item.get("org_id"), dict) else {}
    owner = item.get("owner_id") if isinstance(item.get("owner_id"), dict) else {}
    phones = pipedrive_value_list(item.get("phone"))
    emails = pipedrive_value_list(item.get("email"))
    return {
        "id": item.get("id"),
        "name": item.get("name") or "",
        "email": emails[0] if emails else "",
        "emails": emails,
        "phone": phones[0] if phones else "",
        "phones": phones,
        "organization": org.get("name") if org else item.get("org_name", ""),
        "organization_id": org.get("value") or item.get("org_id") if not isinstance(item.get("org_id"), dict) else org.get("value"),
        "owner": owner.get("name") if owner else "",
        "add_time": item.get("add_time", ""),
        "update_time": item.get("update_time", ""),
        "visible_to": item.get("visible_to", ""),
    }


def normalize_pipedrive_deal(item):
    item = item or {}
    person = item.get("person_id") if isinstance(item.get("person_id"), dict) else {}
    org = item.get("org_id") if isinstance(item.get("org_id"), dict) else {}
    return {
        "id": item.get("id"),
        "title": item.get("title") or "",
        "status": item.get("status") or "",
        "value": item.get("value"),
        "currency": item.get("currency"),
        "person_name": person.get("name") if person else item.get("person_name", ""),
        "person_id": person.get("value") if person else item.get("person_id", ""),
        "organization": org.get("name") if org else item.get("org_name", ""),
        "organization_id": org.get("value") if org else item.get("org_id", ""),
        "pipeline_id": item.get("pipeline_id", ""),
        "stage_id": item.get("stage_id", ""),
        "add_time": item.get("add_time", ""),
        "update_time": item.get("update_time", ""),
    }


def pipedrive_status(live=False):
    status = {
        "configured": bool(load_keychain_secret(PIPEDRIVE_KEYCHAIN_SERVICE, required=False)),
        "company_domain": load_keychain_secret(PIPEDRIVE_COMPANY_DOMAIN_KEYCHAIN_SERVICE, required=False),
        "write_requires_confirmation": True,
        "capabilities": [
            "status",
            "list_persons",
            "search_persons",
            "get_person",
            "upsert_person",
            "list_deals",
            "search_deals",
            "create_deal",
            "update_deal",
            "create_activity",
            "create_note",
        ],
    }
    if live and status["configured"]:
        payload = pipedrive_request("/users/me")
        data = payload.get("data") or {}
        company_domain = data.get("company_domain") or status.get("company_domain")
        if company_domain and company_domain != status.get("company_domain"):
            try:
                store_keychain_secret(PIPEDRIVE_COMPANY_DOMAIN_KEYCHAIN_SERVICE, company_domain)
            except Exception:
                pass
            status["company_domain"] = company_domain
        status["user"] = {key: data.get(key) for key in ["id", "name", "email", "locale"]}
        status["company"] = {key: data.get(key) for key in ["company_id", "company_name", "company_domain"]}
        status["live_ok"] = bool(payload.get("success"))
    return status


def pipedrive_payload_data(payload):
    if not isinstance(payload, dict):
        return None
    if payload.get("success") is False:
        raise RuntimeError(payload.get("error") or "Pipedrive devolvio success=false.")
    return payload.get("data")


def pipedrive_person_id_from_local_contact(contact):
    if not contact:
        return ""
    notes = str(contact.get("notes") or "")
    match = re.search(r"\bPipedrive\s+person_id=(\d+)\b", notes, flags=re.IGNORECASE)
    return match.group(1) if match else ""


def pipedrive_person_candidates(term="", limit=25):
    term = str(term or "").strip()
    limit = max(1, min(int(limit or 25), 100))
    people = []
    normalized_phone = normalize_phone_number(term)
    if normalized_phone:
        local_contact = crm_find_contact_by_phone(normalized_phone)
        person_id = pipedrive_person_id_from_local_contact(local_contact)
        if person_id:
            try:
                payload = pipedrive_request(f"/persons/{urllib.parse.quote(str(person_id))}")
                person = normalize_pipedrive_person(pipedrive_payload_data(payload) or {})
                if person.get("id"):
                    people.append(person)
            except Exception:
                pass
        if local_contact and local_contact.get("display_name"):
            try:
                search = pipedrive_request(
                    "/persons/search",
                    params={"term": local_contact.get("display_name"), "fields": "name,email,phone", "limit": limit},
                )
                items = ((search.get("data") or {}).get("items") or [])
                people.extend(normalize_pipedrive_person((item.get("item") if isinstance(item, dict) else item) or {}) for item in items)
            except Exception:
                pass
    if term:
        search = pipedrive_request("/persons/search", params={"term": term, "fields": "name,email,phone", "limit": limit})
        items = ((search.get("data") or {}).get("items") or [])
        people.extend(normalize_pipedrive_person((item.get("item") if isinstance(item, dict) else item) or {}) for item in items)
    if not term or len(people) < limit:
        listed = pipedrive_request("/persons", params={"start": 0, "limit": limit})
        people.extend(normalize_pipedrive_person(item) for item in (listed.get("data") or []))
    seen = {}
    for person in people:
        if person.get("id") and person.get("id") not in seen:
            seen[person["id"]] = person
    return list(seen.values())[:limit]


def pipedrive_person_score(person, term):
    term_norm = normalize_security_text(term)
    if not term_norm:
        return 0
    fields = [
        person.get("name", ""),
        person.get("email", ""),
        person.get("phone", ""),
        " ".join(person.get("emails") or []),
        " ".join(person.get("phones") or []),
    ]
    best = 0
    for value in fields:
        value_norm = normalize_security_text(value)
        if not value_norm:
            continue
        if term_norm in value_norm or value_norm in term_norm:
            best = max(best, 1.0)
        best = max(best, difflib.SequenceMatcher(None, term_norm, value_norm).ratio())
    return round(best, 3)


def pipedrive_search_persons(parameters=None):
    parameters = parameters or {}
    term = str(first_value(parameters, "term", "query", "q", "search", "name", "contact_name", "client_name", default="") or "").strip()
    phone = normalize_phone_number(first_value(parameters, "phone", "telefono", "to", "from", default=""))
    email = str(first_value(parameters, "email", "correo", default="") or "").strip()
    lookup = phone or email or term
    limit = int(first_value(parameters, "limit", default=25) or 25)
    people = pipedrive_person_candidates(lookup, limit=limit)
    if lookup:
        scored = []
        for person in people:
            score = max(pipedrive_person_score(person, lookup), pipedrive_person_score(person, term))
            scored.append({**person, "match_score": score})
        people = sorted(scored, key=lambda item: item.get("match_score", 0), reverse=True)
    return {
        "ok": True,
        "provider": "pipedrive",
        "action": "search_persons",
        "query": lookup,
        "count": len(people[:limit]),
        "persons": people[:limit],
    }


def pipedrive_find_person_id(parameters=None, required=False):
    parameters = parameters or {}
    person_id = str(first_value(parameters, "person_id", "id", "pipedrive_person_id", default="") or "").strip()
    if person_id:
        return person_id, {"source": "provided", "person_id": person_id}
    search = pipedrive_search_persons(parameters)
    persons = search.get("persons") or []
    confident = [person for person in persons if person.get("match_score", 0) >= 0.82]
    if len(confident) == 1:
        return str(confident[0]["id"]), {"source": "search", "person": confident[0], "candidates": persons[:5]}
    if persons and not required:
        return "", {"source": "candidates", "candidates": persons[:5]}
    if required:
        raise ValueError("No encontre una persona unica en Pipedrive. Usa person_id o confirma una coincidencia.")
    return "", {"source": "not_found", "candidates": persons[:5]}


def pipedrive_find_organization_id(parameters=None):
    parameters = parameters or {}
    org_id = str(first_value(parameters, "org_id", "organization_id", "empresa_id", default="") or "").strip()
    if org_id:
        return org_id
    org_name = str(first_value(parameters, "organization", "organization_name", "org_name", "company", "empresa", default="") or "").strip()
    if not org_name:
        return ""
    result = pipedrive_request("/organizations/search", params={"term": org_name, "fields": "name", "limit": 5})
    items = ((result.get("data") or {}).get("items") or [])
    if len(items) == 1:
        item = items[0].get("item") or {}
        return str(item.get("id") or "")
    return ""


def pipedrive_get_person(parameters=None):
    parameters = parameters or {}
    person_id, _scope = pipedrive_find_person_id(parameters, required=True)
    payload = pipedrive_request(f"/persons/{urllib.parse.quote(str(person_id))}")
    return {"ok": True, "provider": "pipedrive", "action": "get_person", "person": normalize_pipedrive_person(pipedrive_payload_data(payload) or {})}


def pipedrive_upsert_person(parameters=None, confirm=False):
    parameters = parameters or {}
    name = str(first_value(parameters, "name", "display_name", "contact_name", "client_name", "nombre", default="") or "").strip()
    email = str(first_value(parameters, "email", "correo", default="") or "").strip()
    phone = normalize_phone_number(first_value(parameters, "phone", "telefono", "mobile", "to", "from", default=""))
    if not name:
        name = email or phone or "Contacto Pipedrive"
    org_id = pipedrive_find_organization_id(parameters)
    payload = {"name": name}
    if email:
        payload["email"] = email
    if phone:
        payload["phone"] = phone
    if org_id:
        payload["org_id"] = org_id
    person_id, scope = pipedrive_find_person_id({**parameters, "name": name, "email": email, "phone": phone}, required=False)
    preview = {"person_id": person_id, "match": scope, "payload": payload}
    if not confirm:
        summary = f"{'Actualizar' if person_id else 'Crear'} persona Pipedrive: {name}."
        return confirmation_preview("pipedrive", "upsert_person", summary, preview, execution_parameters=parameters)
    if person_id:
        result = pipedrive_request(f"/persons/{urllib.parse.quote(str(person_id))}", method="PUT", payload=payload)
        action = "update_person"
    else:
        result = pipedrive_request("/persons", method="POST", payload=payload)
        action = "create_person"
    person = normalize_pipedrive_person(pipedrive_payload_data(result) or {})
    local_contact = crm_upsert_contact(
        {
            "display_name": person.get("name") or name,
            "email": person.get("email") or email,
            "phone": person.get("phone") or phone,
            "company": person.get("organization") or first_value(parameters, "company", "empresa", default=""),
            "contact_type": first_value(parameters, "contact_type", "tipo", default="client"),
            "notes": f"Pipedrive person_id={person.get('id')}. " + str(first_value(parameters, "notes", "note", default="") or ""),
        },
        source="pipedrive",
    )
    return {"ok": True, "provider": "pipedrive", "action": action, "person": person, "local_contact": local_contact, "confirmed": True}


def pipedrive_list_deals(parameters=None):
    parameters = parameters or {}
    term = str(first_value(parameters, "term", "query", "q", "search", "title", default="") or "").strip()
    limit = max(1, min(int(first_value(parameters, "limit", default=25) or 25), 100))
    if term:
        payload = pipedrive_request("/deals/search", params={"term": term, "fields": "title,person_name,org_name", "limit": limit})
        items = ((payload.get("data") or {}).get("items") or [])
        deals = [normalize_pipedrive_deal((item.get("item") if isinstance(item, dict) else item) or {}) for item in items]
    else:
        payload = pipedrive_request("/deals", params={"start": 0, "limit": limit})
        deals = [normalize_pipedrive_deal(item) for item in (payload.get("data") or [])]
    return {"ok": True, "provider": "pipedrive", "action": "list_deals", "query": term, "count": len(deals), "deals": deals[:limit]}


def pipedrive_create_deal(parameters=None, confirm=False):
    parameters = parameters or {}
    title = str(first_value(parameters, "title", "name", "deal_title", "subject", default="") or "").strip()
    if not title:
        title = generated_title("Deal Pipedrive")
    person_id, person_scope = pipedrive_find_person_id(parameters, required=False)
    org_id = pipedrive_find_organization_id(parameters)
    payload = {"title": title}
    if person_id:
        payload["person_id"] = person_id
    if org_id:
        payload["org_id"] = org_id
    for key in ["value", "currency", "pipeline_id", "stage_id", "status"]:
        value = first_value(parameters, key, default="")
        if value not in ("", None):
            payload[key] = value
    if not confirm:
        return confirmation_preview("pipedrive", "create_deal", f"Crear deal Pipedrive: {title}.", {"payload": payload, "person_match": person_scope}, execution_parameters=parameters)
    result = pipedrive_request("/deals", method="POST", payload=payload)
    return {"ok": True, "provider": "pipedrive", "action": "create_deal", "deal": normalize_pipedrive_deal(pipedrive_payload_data(result) or {}), "confirmed": True}


def pipedrive_update_deal(parameters=None, confirm=False):
    parameters = parameters or {}
    deal_id = str(first_value(parameters, "deal_id", "id", "pipedrive_deal_id", default="") or "").strip()
    if not deal_id:
        raise ValueError("Falta deal_id para actualizar deal Pipedrive.")
    fields = parameters.get("fields") if isinstance(parameters.get("fields"), dict) else {}
    payload = dict(fields)
    for key in ["title", "value", "currency", "pipeline_id", "stage_id", "status", "person_id", "org_id"]:
        value = first_value(parameters, key, default="")
        if value not in ("", None):
            payload[key] = value
    if not payload:
        raise ValueError("Faltan campos para actualizar deal Pipedrive.")
    if not confirm:
        return confirmation_preview("pipedrive", "update_deal", f"Actualizar deal Pipedrive {deal_id}.", {"deal_id": deal_id, "fields": payload}, execution_parameters=parameters)
    result = pipedrive_request(f"/deals/{urllib.parse.quote(str(deal_id))}", method="PUT", payload=payload)
    return {"ok": True, "provider": "pipedrive", "action": "update_deal", "deal": normalize_pipedrive_deal(pipedrive_payload_data(result) or {}), "confirmed": True}


def pipedrive_create_activity(parameters=None, confirm=False):
    parameters = parameters or {}
    subject = str(first_value(parameters, "subject", "title", "name", "asunto", default="") or "").strip()
    if not subject:
        subject = generated_title("Actividad Pipedrive")
    person_id, person_scope = pipedrive_find_person_id(parameters, required=False)
    org_id = pipedrive_find_organization_id(parameters)
    payload = {
        "subject": subject,
        "type": str(first_value(parameters, "type", "activity_type", "tipo", default="call") or "call").strip(),
    }
    if person_id:
        payload["person_id"] = person_id
    if org_id:
        payload["org_id"] = org_id
    for key in ["deal_id", "due_date", "due_time", "duration", "note", "location"]:
        value = first_value(parameters, key, default="")
        if value not in ("", None):
            payload[key] = value
    if not confirm:
        return confirmation_preview("pipedrive", "create_activity", f"Crear actividad Pipedrive: {subject}.", {"payload": payload, "person_match": person_scope}, execution_parameters=parameters)
    result = pipedrive_request("/activities", method="POST", payload=payload)
    return {"ok": True, "provider": "pipedrive", "action": "create_activity", "activity": pipedrive_payload_data(result), "confirmed": True}


def pipedrive_create_note(parameters=None, confirm=False):
    parameters = parameters or {}
    content = str(first_value(parameters, "content", "body", "note", "notes", "text", "message", default="") or "").strip()
    if not content:
        raise ValueError("Falta content/body para crear nota Pipedrive.")
    person_id, person_scope = pipedrive_find_person_id(parameters, required=False)
    org_id = pipedrive_find_organization_id(parameters)
    payload = {"content": content}
    if person_id:
        payload["person_id"] = person_id
    if org_id:
        payload["org_id"] = org_id
    deal_id = str(first_value(parameters, "deal_id", "pipedrive_deal_id", default="") or "").strip()
    if deal_id:
        payload["deal_id"] = deal_id
    if not confirm:
        return confirmation_preview("pipedrive", "create_note", f"Crear nota Pipedrive para {person_id or org_id or deal_id or 'CRM'}.", {"payload": payload, "person_match": person_scope}, execution_parameters=parameters)
    result = pipedrive_request("/notes", method="POST", payload=payload)
    return {"ok": True, "provider": "pipedrive", "action": "create_note", "note": pipedrive_payload_data(result), "confirmed": True}


def run_pipedrive_bridge(action, parameters, confirm=False):
    action = (action or "").strip().lower()
    parameters = parameters or {}
    if action in {"status", "me"}:
        return {"ok": True, "provider": "pipedrive", "action": action, "status": pipedrive_status(live=True)}
    if action in {"list_persons", "persons", "contacts", "contactos", "search_persons", "search_contacts", "buscar_personas"}:
        return pipedrive_search_persons(parameters)
    if action in {"get_person", "person", "contact", "get_contact"}:
        return pipedrive_get_person(parameters)
    if action in {"upsert_person", "save_person", "create_person", "update_person", "save_contact", "upsert_contact"}:
        return pipedrive_upsert_person(parameters, confirm=confirm)
    if action in {"list_deals", "search_deals", "deals", "oportunidades"}:
        return pipedrive_list_deals(parameters)
    if action in {"create_deal", "add_deal", "crear_deal", "crear_oportunidad"}:
        return pipedrive_create_deal(parameters, confirm=confirm)
    if action in {"update_deal", "actualizar_deal"}:
        return pipedrive_update_deal(parameters, confirm=confirm)
    if action in {"create_activity", "add_activity", "activity", "actividad", "crear_actividad"}:
        return pipedrive_create_activity(parameters, confirm=confirm)
    if action in {"create_note", "add_note", "note", "nota", "crear_nota"}:
        return pipedrive_create_note(parameters, confirm=confirm)
    raise ValueError(f"Accion Pipedrive no soportada: {action}")


def oauth_form_request(url, payload, timeout=90):
    data = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        message = raw
        try:
            parsed = json.loads(raw)
            message = parsed.get("error_description") or parsed.get("error") or raw
        except json.JSONDecodeError:
            pass
        raise RuntimeError(f"OAuth error {exc.code}: {message}") from exc
    return json.loads(raw or "{}")


def gmail_oauth_configured():
    return bool(load_keychain_secret(GMAIL_CLIENT_ID_KEYCHAIN_SERVICE, required=False)) and bool(
        load_keychain_secret(GMAIL_CLIENT_SECRET_KEYCHAIN_SERVICE, required=False)
    )


def gmail_authorized():
    return bool(load_keychain_secret(GMAIL_REFRESH_TOKEN_KEYCHAIN_SERVICE, required=False))


def gmail_exchange_code(code, redirect_uri):
    client_id = load_keychain_secret(GMAIL_CLIENT_ID_KEYCHAIN_SERVICE)
    client_secret = load_keychain_secret(GMAIL_CLIENT_SECRET_KEYCHAIN_SERVICE)
    token = oauth_form_request(
        GOOGLE_OAUTH_TOKEN_URL,
        {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
    )
    refresh_token = token.get("refresh_token")
    if refresh_token:
        store_keychain_secret(GMAIL_REFRESH_TOKEN_KEYCHAIN_SERVICE, refresh_token)
    return token


def gmail_access_token():
    client_id = load_keychain_secret(GMAIL_CLIENT_ID_KEYCHAIN_SERVICE)
    client_secret = load_keychain_secret(GMAIL_CLIENT_SECRET_KEYCHAIN_SERVICE)
    refresh_token = load_keychain_secret(GMAIL_REFRESH_TOKEN_KEYCHAIN_SERVICE)
    token = oauth_form_request(
        GOOGLE_OAUTH_TOKEN_URL,
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
    )
    access_token = token.get("access_token")
    if not access_token:
        raise RuntimeError("Google no devolvio access_token al refrescar Gmail.")
    return access_token


def gmail_request(path, method="GET", payload=None, params=None):
    return api_json_request(
        GMAIL_API_BASE,
        path,
        {"Authorization": f"Bearer {gmail_access_token()}"},
        method=method,
        payload=payload,
        params=params,
    )


def gmail_status(live=False):
    status = {
        "configured": gmail_oauth_configured(),
        "authorized": gmail_authorized(),
        "write_requires_confirmation": True,
        "scope": GMAIL_READONLY_SCOPE,
        "capabilities": ["status", "auth_url", "profile", "list_messages", "get_message"],
        "auth_url": "https://kim.aipeople.app/oauth/google/start",
        "mode": "readonly",
    }
    if live and status["authorized"]:
        try:
            status["profile"] = gmail_request("/users/me/profile")
            status["live_ok"] = True
        except Exception as exc:
            status["live_ok"] = False
            status["error"] = brief(str(exc), 220)
    return status


def gmail_header(headers, name):
    wanted = (name or "").lower()
    for header in headers or []:
        if str(header.get("name") or "").lower() == wanted:
            return header.get("value") or ""
    return ""


def gmail_decode_body(data):
    if not data:
        return ""
    padded = data + "=" * (-len(data) % 4)
    try:
        return base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8", errors="replace")
    except Exception:
        return ""


def gmail_extract_text_from_payload(payload):
    if not payload:
        return ""
    mime = payload.get("mimeType") or ""
    body = payload.get("body") or {}
    if mime.startswith("text/plain") and body.get("data"):
        return gmail_decode_body(body.get("data"))
    parts = payload.get("parts") or []
    plain = []
    html_parts = []
    for part in parts:
        text = gmail_extract_text_from_payload(part)
        if not text:
            continue
        if (part.get("mimeType") or "").startswith("text/html"):
            html_parts.append(text)
        else:
            plain.append(text)
    if plain:
        return "\n\n".join(plain)
    if html_parts:
        clean = re.sub(r"<(br|p|div|li|tr|h[1-6])[^>]*>", "\n", "\n".join(html_parts), flags=re.I)
        clean = re.sub(r"<[^>]+>", " ", clean)
        return html.unescape(re.sub(r"\s+\n", "\n", re.sub(r"[ \t]+", " ", clean))).strip()
    return ""


def gmail_normalize_message(message, include_body=False):
    payload = message.get("payload") or {}
    headers = payload.get("headers") or []
    row = {
        "id": message.get("id"),
        "thread_id": message.get("threadId"),
        "label_ids": message.get("labelIds") or [],
        "snippet": message.get("snippet"),
        "from": gmail_header(headers, "From"),
        "to": gmail_header(headers, "To"),
        "subject": gmail_header(headers, "Subject"),
        "date": gmail_header(headers, "Date"),
    }
    if include_body:
        row["body_text"] = brief(gmail_extract_text_from_payload(payload), 6000)
    return row


def gmail_list_messages(parameters):
    parameters = parameters or {}
    max_results = min(max(int(parameters.get("max_results") or parameters.get("limit") or 10), 1), 25)
    params = {
        "maxResults": max_results,
        "q": str(parameters.get("query") or parameters.get("q") or "").strip() or None,
        "includeSpamTrash": str(bool(parameters.get("include_spam_trash", False))).lower(),
    }
    label_ids = parameters.get("label_ids") or parameters.get("labelIds")
    if isinstance(label_ids, str) and label_ids.strip():
        params["labelIds"] = label_ids.strip()
    result = gmail_request("/users/me/messages", params=params)
    messages = []
    for item in (result.get("messages") or [])[:max_results]:
        msg = gmail_request(
            f"/users/me/messages/{urllib.parse.quote(item['id'])}",
            params={
                "format": "metadata",
                "metadataHeaders": ["From", "To", "Subject", "Date"],
            },
        )
        messages.append(gmail_normalize_message(msg, include_body=False))
    return {
        "ok": True,
        "provider": "gmail",
        "action": "list_messages",
        "query": params.get("q") or "",
        "count": len(messages),
        "messages": messages,
        "next_page_token": result.get("nextPageToken"),
    }


def gmail_get_message(parameters):
    parameters = parameters or {}
    message_id = str(parameters.get("message_id") or parameters.get("id") or "").strip()
    if not message_id:
        raise ValueError("Falta message_id para leer correo Gmail.")
    fmt = "full" if parameters.get("include_body", True) else "metadata"
    params = {"format": fmt}
    if fmt == "metadata":
        params["metadataHeaders"] = ["From", "To", "Subject", "Date"]
    message = gmail_request(f"/users/me/messages/{urllib.parse.quote(message_id)}", params=params)
    return {
        "ok": True,
        "provider": "gmail",
        "action": "get_message",
        "message": gmail_normalize_message(message, include_body=(fmt == "full")),
    }


def hostinger_mail_slug(mailbox):
    return re.sub(r"[^a-z0-9]+", "_", str(mailbox or "").strip().lower()).strip("_")


def hostinger_known_mailboxes():
    seen = {}
    for mailbox in HOSTINGER_MAILBOXES:
        account = str(mailbox or "").strip().lower()
        if account:
            seen[account] = True
    return list(seen.keys())


def resolve_hostinger_mailbox(mailbox=None):
    value = str(mailbox or "").strip().lower()
    if not value:
        return DEFAULT_HOSTINGER_MAILBOX
    normalized = re.sub(r"[\s_-]+", " ", value).strip()
    if value in HOSTINGER_MAILBOX_ALIASES:
        return HOSTINGER_MAILBOX_ALIASES[value]
    if normalized in HOSTINGER_MAILBOX_ALIASES:
        return HOSTINGER_MAILBOX_ALIASES[normalized]
    if "@" in value:
        return value
    return DEFAULT_HOSTINGER_MAILBOX


def hostinger_mail_password_service(mailbox):
    return f"codex.hostinger_mail.{hostinger_mail_slug(mailbox)}.password"


def hostinger_mail_config(mailbox=None):
    account = resolve_hostinger_mailbox(mailbox)
    return {
        "account": account,
        "imap_host": HOSTINGER_IMAP_HOST,
        "imap_port": HOSTINGER_IMAP_PORT,
        "smtp_host": HOSTINGER_SMTP_HOST,
        "smtp_port": HOSTINGER_SMTP_PORT,
        "password_service": hostinger_mail_password_service(account),
    }


def hostinger_mail_password(mailbox=None):
    config = hostinger_mail_config(mailbox)
    account = config["account"]
    services = [
        config["password_service"],
        f"codex.hostinger_mail.{account}.password",
    ]
    for service in services:
        secret = load_keychain_secret_for_account(service, account, required=False)
        if secret:
            return secret
    for service in services:
        secret = load_keychain_secret(service, required=False)
        if secret:
            return secret
    raise ValueError(f"No encontre password Hostinger para {account} en Keychain.")


def hostinger_mail_configured(mailbox=None):
    try:
        return bool(hostinger_mail_password(mailbox))
    except Exception:
        return False


def hostinger_single_mail_status(live=False, mailbox=None):
    config = hostinger_mail_config(mailbox)
    configured = hostinger_mail_configured(config["account"])
    status = {
        "configured": configured,
        "authorized": configured,
        "mailbox": config["account"],
        "imap": f"{config['imap_host']}:{config['imap_port']}",
        "smtp": f"{config['smtp_host']}:{config['smtp_port']}",
    }
    if live and configured:
        try:
            with hostinger_imap_connection(config["account"], readonly=True) as mail:
                mail.select("INBOX", readonly=True)
                typ, data = mail.uid("search", None, "ALL")
                ids = data[0].split() if typ == "OK" and data else []
                status["live_ok"] = True
                status["inbox_count"] = len(ids)
        except Exception as exc:
            status["live_ok"] = False
            status["error"] = brief(str(exc), 220)
    return status


def hostinger_mail_status(live=False, mailbox=None):
    selected = resolve_hostinger_mailbox(mailbox)
    accounts = []
    for account in hostinger_known_mailboxes():
        accounts.append(hostinger_single_mail_status(live=(live and account == selected), mailbox=account))
    selected_status = next((item for item in accounts if item.get("mailbox") == selected), hostinger_single_mail_status(live=live, mailbox=selected))
    return {
        "configured": any(item.get("configured") for item in accounts),
        "authorized": bool(selected_status.get("authorized")),
        "mailboxes": hostinger_known_mailboxes(),
        "default_mailbox": DEFAULT_HOSTINGER_MAILBOX,
        "selected_mailbox": selected,
        "aliases": HOSTINGER_MAILBOX_ALIASES,
        "imap": f"{HOSTINGER_IMAP_HOST}:{HOSTINGER_IMAP_PORT}",
        "smtp": f"{HOSTINGER_SMTP_HOST}:{HOSTINGER_SMTP_PORT}",
        "write_requires_confirmation": True,
        "capabilities": [
            "status",
            "list_mailboxes",
            "switch_mailbox",
            "list_folders",
            "list_messages",
            "search_messages",
            "get_message",
            "draft_email",
            "draft_reply",
            "send_email",
            "reply_email",
            "move_message",
            "mark_spam",
            "move_to_trash",
            "archive_message",
        ],
        "mode": "imap_smtp",
        "accounts": accounts,
        **{key: value for key, value in selected_status.items() if key in {"live_ok", "inbox_count", "error"}},
    }


class HostingerImapSession:
    def __init__(self, mailbox):
        self.config = hostinger_mail_config(mailbox)
        self.mail = None

    def __enter__(self):
        self.mail = imaplib.IMAP4_SSL(
            self.config["imap_host"],
            self.config["imap_port"],
            timeout=25,
        )
        self.mail.login(self.config["account"], hostinger_mail_password(self.config["account"]))
        return self.mail

    def __exit__(self, exc_type, exc, tb):
        if not self.mail:
            return False
        try:
            self.mail.close()
        except Exception:
            pass
        try:
            self.mail.logout()
        except Exception:
            pass
        return False


def hostinger_imap_connection(mailbox=None, readonly=True):
    return HostingerImapSession(mailbox or DEFAULT_HOSTINGER_MAILBOX)


def hostinger_mailbox_from_parameters(parameters=None):
    return resolve_hostinger_mailbox(
        first_value(parameters or {}, "mailbox", "account", "from", "sender", "selected_mailbox", "active_mailbox")
    )


def hostinger_default_subject(mailbox=None, reply=False):
    account = resolve_hostinger_mailbox(mailbox)
    if "aipeople" in account:
        return "Respuesta AI People" if reply else "Seguimiento AI People"
    if "tescaelements" in account:
        return "Respuesta Tesca Elements" if reply else "Seguimiento Tesca Elements"
    return "Respuesta" if reply else "Seguimiento"


def hostinger_display_name(mailbox=None, parameters=None):
    explicit = str(
        first_value(parameters or {}, "from_name", "sender_name", "display_name", "nombre_remitente")
        or ""
    ).strip()
    if explicit:
        return explicit
    return HOSTINGER_MAILBOX_DISPLAY_NAMES.get(resolve_hostinger_mailbox(mailbox), "")


def boolish(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "si", "on"}


def hostinger_signature_disabled(parameters=None):
    return boolish(
        first_value(
            parameters or {},
            "no_signature",
            "omit_signature",
            "skip_signature",
            "sin_firma",
            "omitir_firma",
            default=False,
        )
    )


def hostinger_signature_text(parameters=None):
    if hostinger_signature_disabled(parameters):
        return ""
    custom = first_value(parameters or {}, "signature", "firma", "email_signature", "email_firma", default="")
    if isinstance(custom, bool):
        custom = ""
    custom = str(custom or "").strip()
    if custom.lower() in {"none", "no", "sin firma", "omit", "omitir"}:
        return ""
    return custom or KIM_EMAIL_SIGNATURE


def hostinger_body_has_signature(value):
    normalized = strip_html_text(str(value or "")).lower()
    return (
        "kim yan" in normalized
        or "augmented intelligence assistant" in normalized
        or "created by dr. yehoshua" in normalized
    )


def hostinger_apply_signature_to_text(value, parameters=None):
    body = str(value or "").rstrip()
    signature = hostinger_signature_text(parameters)
    if not signature or hostinger_body_has_signature(body):
        return body
    separator = "\n\n-- \n" if body else ""
    return f"{body}{separator}{signature}"


def hostinger_apply_signature_to_html(value, parameters=None):
    html_body = str(value or "").rstrip()
    signature = hostinger_signature_text(parameters)
    if not signature or hostinger_body_has_signature(html_body):
        return html_body
    signature_html = "<br>".join(html.escape(line) for line in signature.splitlines())
    block = f"<br><br><p>--<br>{signature_html}</p>"
    return f"{html_body}{block}" if html_body else f"<p>{signature_html}</p>"


def decode_mail_header(value):
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return str(value)


def strip_html_text(value):
    clean = re.sub(r"<(br|p|div|li|tr|h[1-6])[^>]*>", "\n", value or "", flags=re.I)
    clean = re.sub(r"<[^>]+>", " ", clean)
    clean = html.unescape(clean)
    clean = re.sub(r"[ \t]+", " ", clean)
    clean = re.sub(r"\n\s+\n", "\n\n", clean)
    return clean.strip()


def parse_imap_folder_line(line):
    raw = line.decode("utf-8", errors="replace") if isinstance(line, bytes) else str(line or "")
    flags_match = re.match(r"\(([^)]*)\)", raw)
    flags = flags_match.group(1).split() if flags_match else []
    name = ""
    quoted = re.search(r'"([^"]+)"\s*$', raw)
    if quoted:
        name = quoted.group(1)
    else:
        parts = raw.rsplit(" ", 1)
        name = parts[-1].strip() if parts else raw.strip()
    return {"name": name.strip('"'), "flags": flags, "raw": raw}


def imap_folder_arg(name):
    safe = str(name or "").replace("\\", "\\\\").replace('"', '\\"')
    return f'"{safe}"'


def first_value(mapping, *keys, default=""):
    if not isinstance(mapping, dict):
        return default
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return value
    return default


def merge_missing(target, updates):
    for key, value in (updates or {}).items():
        if value not in (None, "") and target.get(key) in (None, ""):
            target[key] = value
    return target


def generated_title(prefix="Kim"):
    return f"{prefix} {now_iso()}"


def hostinger_extract_body(message):
    plain_parts = []
    html_parts = []
    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            disposition = str(part.get_content_disposition() or "").lower()
            if disposition == "attachment":
                continue
            try:
                payload = part.get_content()
            except Exception:
                payload = ""
            if not isinstance(payload, str):
                continue
            if content_type == "text/plain":
                plain_parts.append(payload)
            elif content_type == "text/html":
                html_parts.append(strip_html_text(payload))
    else:
        try:
            payload = message.get_content()
        except Exception:
            payload = ""
        if isinstance(payload, str):
            if message.get_content_type() == "text/html":
                html_parts.append(strip_html_text(payload))
            else:
                plain_parts.append(payload)
    text = "\n\n".join(part.strip() for part in plain_parts if part and part.strip())
    if not text:
        text = "\n\n".join(part.strip() for part in html_parts if part and part.strip())
    return brief(text, 9000)


def hostinger_normalize_message(uid, message, include_body=False):
    row = {
        "id": str(uid),
        "uid": str(uid),
        "from": decode_mail_header(message.get("From", "")),
        "to": decode_mail_header(message.get("To", "")),
        "cc": decode_mail_header(message.get("Cc", "")),
        "subject": decode_mail_header(message.get("Subject", "")),
        "date": decode_mail_header(message.get("Date", "")),
        "message_id": decode_mail_header(message.get("Message-ID", "")),
        "in_reply_to": decode_mail_header(message.get("In-Reply-To", "")),
        "references": decode_mail_header(message.get("References", "")),
    }
    if include_body:
        row["body_text"] = hostinger_extract_body(message)
    return row


def imap_search_criteria(parameters):
    parameters = parameters or {}
    if parameters.get("raw_criteria"):
        raw = parameters.get("raw_criteria")
        if isinstance(raw, list):
            return [str(item) for item in raw]
        return [str(raw)]
    criteria = ["UNSEEN" if parameters.get("unread") else "ALL"]
    sender = str(parameters.get("from") or parameters.get("sender") or "").strip()
    subject = str(parameters.get("subject") or "").strip()
    since = str(parameters.get("since") or parameters.get("since_date") or "").strip()
    before = str(parameters.get("before") or parameters.get("before_date") or "").strip()
    keyword = str(parameters.get("query") or parameters.get("q") or "").strip()
    if sender:
        criteria.extend(["FROM", f'"{sender}"'])
    if subject:
        criteria.extend(["SUBJECT", f'"{subject}"'])
    if since:
        criteria.extend(["SINCE", since])
    if before:
        criteria.extend(["BEFORE", before])
    if keyword:
        criteria.extend(["TEXT", f'"{keyword}"'])
    return criteria


def hostinger_fetch_message(mail, uid, include_body=False):
    fetch_mode = "(BODY.PEEK[])" if include_body else "(BODY.PEEK[HEADER])"
    typ, data = mail.uid("fetch", str(uid), fetch_mode)
    if typ != "OK" or not data:
        raise RuntimeError(f"IMAP no devolvio mensaje {uid}.")
    raw = b""
    for item in data:
        if isinstance(item, tuple):
            raw += item[1]
    if not raw:
        raise RuntimeError(f"Mensaje {uid} sin contenido.")
    message = BytesParser(policy=policy.default).parsebytes(raw)
    return hostinger_normalize_message(uid, message, include_body=include_body)


def hostinger_list_folders(parameters):
    parameters = parameters or {}
    mailbox = hostinger_mailbox_from_parameters(parameters)
    with hostinger_imap_connection(mailbox, readonly=True) as mail:
        typ, data = mail.list()
    if typ != "OK":
        raise RuntimeError("IMAP list fallo.")
    folders = [parse_imap_folder_line(line) for line in (data or [])]
    return {
        "ok": True,
        "provider": "hostinger_mail",
        "action": "list_folders",
        "mailbox": mailbox,
        "folders": folders,
    }


def hostinger_folder_for_purpose(mailbox, purpose, explicit=""):
    explicit = str(explicit or "").strip()
    if explicit:
        return explicit
    folders = hostinger_list_folders({"mailbox": mailbox}).get("folders") or []
    purpose = str(purpose or "").strip().lower()
    needles = {
        "spam": ["\\junk", "junk", "spam", "correo no deseado"],
        "trash": ["\\trash", "trash", "deleted", "papelera"],
        "archive": ["archive", "archivo"],
    }.get(purpose, [])
    for folder in folders:
        haystack = " ".join(folder.get("flags") or []).lower() + " " + str(folder.get("name") or "").lower()
        if any(needle in haystack for needle in needles):
            return folder.get("name")
    raise ValueError(f"No encontre carpeta destino para {purpose} en {mailbox}. Usa list_folders o pasa target_folder.")


def normalize_message_ids(parameters):
    raw = first_value(parameters, "message_ids", "uids", "ids", "message_id", "uid", "id")
    if isinstance(raw, list):
        values = raw
    else:
        values = re.split(r"[,\s]+", str(raw or ""))
    ids = [str(value).strip() for value in values if str(value).strip()]
    if not ids:
        raise ValueError("Falta message_id/uid para mover correo.")
    return ids


def hostinger_move_message(parameters, confirm=False, purpose="custom"):
    parameters = parameters or {}
    mailbox = hostinger_mailbox_from_parameters(parameters)
    source_folder = str(first_value(parameters, "folder", "source_folder", default="INBOX") or "INBOX").strip()
    message_ids = normalize_message_ids(parameters)
    target_folder = hostinger_folder_for_purpose(
        mailbox,
        purpose,
        explicit=first_value(parameters, "target_folder", "destination_folder", "to_folder"),
    )
    action_name = {
        "spam": "mark_spam",
        "trash": "move_to_trash",
        "archive": "archive_message",
    }.get(purpose, "move_message")
    execution_parameters = {
        "mailbox": mailbox,
        "folder": source_folder,
        "message_ids": message_ids,
        "target_folder": target_folder,
    }
    if not confirm:
        return confirmation_preview(
            "hostinger_mail",
            action_name,
            f"Mover {len(message_ids)} correo(s) de {mailbox}/{source_folder} a {target_folder}.",
            execution_parameters,
        )
    moved = []
    failed = []
    method = "MOVE"
    with hostinger_imap_connection(mailbox, readonly=False) as mail:
        mail.select(source_folder, readonly=False)
        target_arg = imap_folder_arg(target_folder)
        for uid in message_ids:
            typ, data = mail.uid("MOVE", uid, target_arg)
            if typ != "OK":
                method = "COPY_DELETE_EXPUNGE"
                copy_typ, copy_data = mail.uid("COPY", uid, target_arg)
                if copy_typ == "OK":
                    store_typ, _store_data = mail.uid("STORE", uid, "+FLAGS", "(\\Deleted)")
                    if store_typ == "OK":
                        moved.append(uid)
                    else:
                        failed.append({"uid": uid, "error": f"STORE fallo: {store_typ}"})
                else:
                    failed.append({"uid": uid, "error": f"MOVE/COPY fallo: {typ}; {copy_typ}", "data": brief(str(data or copy_data), 180)})
            else:
                moved.append(uid)
        if method == "COPY_DELETE_EXPUNGE" and moved:
            mail.expunge()
    result = {
        "ok": not failed,
        "provider": "hostinger_mail",
        "action": action_name,
        "mailbox": mailbox,
        "source_folder": source_folder,
        "target_folder": target_folder,
        "message_ids": message_ids,
        "moved": moved,
        "failed": failed,
        "method": method,
        "confirmed": True,
        "moved_at": now_iso(),
    }
    append_jsonl_any([HOSTINGER_MAIL_LOG, RUNTIME_HOSTINGER_MAIL_LOG], result)
    append_memory("hostinger_mail_moved", result)
    return result


def hostinger_list_messages(parameters):
    parameters = parameters or {}
    mailbox = hostinger_mailbox_from_parameters(parameters)
    folder = str(parameters.get("folder") or "INBOX").strip() or "INBOX"
    limit = min(max(int(parameters.get("max_results") or parameters.get("limit") or 10), 1), 50)
    with hostinger_imap_connection(mailbox, readonly=True) as mail:
        mail.select(folder, readonly=True)
        typ, data = mail.uid("search", None, *imap_search_criteria(parameters))
        if typ != "OK":
            raise RuntimeError("IMAP search fallo.")
        ids = data[0].split() if data else []
        selected = list(reversed(ids[-limit:]))
        messages = [hostinger_fetch_message(mail, uid.decode("ascii"), include_body=False) for uid in selected]
    return {
        "ok": True,
        "provider": "hostinger_mail",
        "action": "list_messages",
        "mailbox": mailbox,
        "folder": folder,
        "count": len(messages),
        "total_matches": len(ids),
        "messages": messages,
    }


def hostinger_switch_mailbox(parameters):
    parameters = parameters or {}
    mailbox = hostinger_mailbox_from_parameters(parameters)
    result = {
        "ok": True,
        "provider": "hostinger_mail",
        "action": "switch_mailbox",
        "selected_mailbox": mailbox,
        "default_mailbox": DEFAULT_HOSTINGER_MAILBOX,
        "mailboxes": hostinger_known_mailboxes(),
        "aliases": HOSTINGER_MAILBOX_ALIASES,
        "message": f"Mailbox activo cambiado a {mailbox}. Las siguientes consultas deben usar selected_mailbox o mailbox={mailbox}.",
    }
    append_memory("hostinger_mail_switched", result)
    append_jsonl_any([HOSTINGER_MAIL_LOG, RUNTIME_HOSTINGER_MAIL_LOG], result)
    return result


def hostinger_get_message(parameters):
    parameters = parameters or {}
    mailbox = hostinger_mailbox_from_parameters(parameters)
    folder = str(parameters.get("folder") or "INBOX").strip() or "INBOX"
    uid = str(parameters.get("message_id") or parameters.get("uid") or parameters.get("id") or "").strip()
    if not uid:
        raise ValueError("Falta message_id/uid para leer correo Hostinger.")
    with hostinger_imap_connection(mailbox, readonly=True) as mail:
        mail.select(folder, readonly=True)
        message = hostinger_fetch_message(mail, uid, include_body=True)
    return {
        "ok": True,
        "provider": "hostinger_mail",
        "action": "get_message",
        "mailbox": mailbox,
        "folder": folder,
        "message": message,
    }


def normalize_email_recipients(value):
    if isinstance(value, list):
        raw = ", ".join(str(item) for item in value)
    else:
        raw = str(value or "")
    addresses = [addr for _name, addr in getaddresses([raw]) if addr]
    return addresses


def hostinger_email_preview(parameters, mailbox):
    to = normalize_email_recipients(first_value(parameters, "to", "recipient", "recipients", "email", "client_email", "destinatario"))
    cc = normalize_email_recipients(first_value(parameters, "cc", "copy"))
    bcc = normalize_email_recipients(first_value(parameters, "bcc", "blind_copy"))
    subject = str(first_value(parameters, "subject", "title", "name", "asunto") or "").strip()
    body = str(first_value(parameters, "body", "text", "content", "message", "description", "cuerpo") or "").strip()
    from_name = hostinger_display_name(mailbox, parameters)
    from_header = formataddr((from_name, mailbox)) if from_name else mailbox
    if not to:
        raise ValueError("Falta destinatario to para enviar correo.")
    if not subject:
        raise ValueError("Falta subject para enviar correo.")
    if not body and not parameters.get("html"):
        raise ValueError("Falta body/text para enviar correo.")
    return {
        "from": mailbox,
        "from_name": from_name,
        "from_header": from_header,
        "to": to,
        "cc": cc,
        "bcc": bcc,
        "subject": subject,
        "body_preview": brief(body or strip_html_text(str(parameters.get("html") or "")), 600),
    }


def hostinger_apply_email_template(parameters, mailbox=None, reply=False):
    data = dict(parameters or {})
    mailbox = resolve_hostinger_mailbox(
        mailbox or first_value(data, "mailbox", "from", "account", "sender", "selected_mailbox", "active_mailbox")
    )
    message_id = str(first_value(data, "message_id", "uid", "id", "reply_to_message_id") or "").strip()
    original = None
    if reply and message_id:
        try:
            original = hostinger_get_message({"mailbox": mailbox, "message_id": message_id}).get("message") or {}
        except Exception as exc:
            data["template_warning"] = f"No pude leer mensaje original {message_id}: {brief(str(exc), 180)}"
    if original:
        if not normalize_email_recipients(data.get("to")):
            data["to"] = original.get("from")
        subject = str(first_value(data, "subject", "title", "name", "asunto") or "").strip()
        if not subject:
            original_subject = str(original.get("subject") or "").strip()
            fallback = hostinger_default_subject(mailbox, reply=True)
            data["subject"] = original_subject if original_subject.lower().startswith("re:") else f"Re: {original_subject or fallback}"
        merge_missing(
            data,
            {
                "in_reply_to": original.get("message_id"),
                "references": " ".join(part for part in [original.get("references"), original.get("message_id")] if part),
            },
        )
    if not str(first_value(data, "subject", "title", "name", "asunto") or "").strip():
        data["subject"] = hostinger_default_subject(mailbox, reply=reply)
    body = str(first_value(data, "body", "text", "content", "message", "description", "cuerpo") or "").strip()
    if body:
        data["body"] = hostinger_apply_signature_to_text(body, data)
    elif data.get("html"):
        data["body"] = hostinger_apply_signature_to_text(strip_html_text(str(data.get("html") or "")), data)
    if data.get("html"):
        data["html"] = hostinger_apply_signature_to_html(data.get("html"), data)
    return data


def hostinger_send_email(parameters, confirm=False, reply=False):
    parameters = parameters or {}
    mailbox = hostinger_mailbox_from_parameters(parameters)
    parameters = hostinger_apply_email_template(parameters, mailbox=mailbox, reply=reply)
    preview = hostinger_email_preview(parameters, mailbox)
    if not confirm:
        execution_parameters = {
            "mailbox": mailbox,
            "from_name": preview["from_name"],
            "to": preview["to"],
            "cc": preview["cc"],
            "bcc": preview["bcc"],
            "subject": preview["subject"],
            "body": str(first_value(parameters, "body", "text", "content", "message", "description", "cuerpo") or ""),
        }
        for key in ["html", "in_reply_to", "references"]:
            if parameters.get(key):
                execution_parameters[key] = parameters.get(key)
        prepared = confirmation_preview(
            "hostinger_mail",
            "reply_email" if reply else "send_email",
            f"Enviar correo desde {mailbox} a {', '.join(preview['to'])}: {preview['subject']}",
            execution_parameters,
        )
        prepared["preview"] = preview
        prepared["confirm_payload"] = {
            "provider": "hostinger_mail",
            "action": "reply_email" if reply else "send_email",
            "parameters": execution_parameters,
            "confirm": True,
        }
        return prepared
    msg = EmailMessage()
    msg["From"] = preview["from_header"]
    msg["To"] = ", ".join(preview["to"])
    if preview["cc"]:
        msg["Cc"] = ", ".join(preview["cc"])
    msg["Subject"] = preview["subject"]
    if parameters.get("in_reply_to"):
        msg["In-Reply-To"] = str(parameters.get("in_reply_to"))
    if parameters.get("references"):
        msg["References"] = str(parameters.get("references"))
    body = str(first_value(parameters, "body", "text", "content", "message", "description", "cuerpo") or "")
    html_body = parameters.get("html")
    msg.set_content(body or strip_html_text(str(html_body or "")))
    if html_body:
        msg.add_alternative(str(html_body), subtype="html")
    config = hostinger_mail_config(mailbox)
    recipients = preview["to"] + preview["cc"] + preview["bcc"]
    with smtplib.SMTP_SSL(config["smtp_host"], config["smtp_port"], timeout=25) as server:
        server.login(mailbox, hostinger_mail_password(mailbox))
        refused = server.send_message(msg, from_addr=mailbox, to_addrs=recipients)
    result = {
        "ok": not bool(refused),
        "provider": "hostinger_mail",
        "action": "reply_email" if reply else "send_email",
        "mailbox": mailbox,
        "from_name": preview["from_name"],
        "to": preview["to"],
        "cc": preview["cc"],
        "bcc_count": len(preview["bcc"]),
        "subject": preview["subject"],
        "refused": refused,
        "confirmed": True,
        "sent_at": now_iso(),
    }
    append_jsonl_any([HOSTINGER_MAIL_LOG, RUNTIME_HOSTINGER_MAIL_LOG], result)
    append_memory("hostinger_mail_sent", result)
    return result


def hostinger_draft_email(parameters, reply=False):
    parameters = parameters or {}
    mailbox = hostinger_mailbox_from_parameters(parameters)
    parameters = hostinger_apply_email_template(parameters, mailbox=mailbox, reply=reply)
    preview = hostinger_email_preview(parameters, mailbox)
    return {
        "ok": True,
        "provider": "hostinger_mail",
        "action": "draft_reply" if reply else "draft_email",
        "mailbox": mailbox,
        "draft": {
            **preview,
            "body": str(first_value(parameters, "body", "text", "content", "message", "description", "cuerpo") or ""),
            **({"html": parameters.get("html")} if parameters.get("html") else {}),
        },
        "message": "Borrador preparado. Si el doctor pidio enviar, usa send_email primero con confirm=false y luego con confirm=true tras confirmacion explicita.",
    }


def run_hostinger_mail_bridge(action, parameters, confirm=False):
    action = (action or "").strip().lower()
    parameters = parameters or {}
    if action in {"status", "me"}:
        return {
            "ok": True,
            "provider": "hostinger_mail",
            "action": action,
            "status": hostinger_mail_status(
                live=True,
                mailbox=first_value(parameters, "mailbox", "account", "from", "sender", "selected_mailbox", "active_mailbox"),
            ),
        }
    if action in {"list_mailboxes", "mailboxes"}:
        return {
            "ok": True,
            "provider": "hostinger_mail",
            "action": action,
            "mailboxes": hostinger_known_mailboxes(),
            "default_mailbox": DEFAULT_HOSTINGER_MAILBOX,
            "aliases": HOSTINGER_MAILBOX_ALIASES,
        }
    if action in {"switch_mailbox", "select_mailbox", "set_mailbox", "use_mailbox", "change_mailbox"}:
        return hostinger_switch_mailbox(parameters)
    if action in {"list_folders", "folders"}:
        return hostinger_list_folders(parameters)
    if action in {"list_messages", "list_emails", "inbox", "search", "search_messages"}:
        return hostinger_list_messages(parameters)
    if action in {"get_message", "read_message", "read_email"}:
        return hostinger_get_message(parameters)
    if action in {"move_message", "move_email", "move_to_folder"}:
        return hostinger_move_message(parameters, confirm=confirm, purpose="custom")
    if action in {"mark_spam", "mark_as_spam", "spam", "junk", "move_to_spam"}:
        return hostinger_move_message(parameters, confirm=confirm, purpose="spam")
    if action in {"move_to_trash", "trash_email", "delete_email", "delete_message", "basura", "eliminar_correo"}:
        return hostinger_move_message(parameters, confirm=confirm, purpose="trash")
    if action in {"archive_message", "archive_email", "archive", "archivar"}:
        return hostinger_move_message(parameters, confirm=confirm, purpose="archive")
    if action in {"draft_email", "draft"}:
        return hostinger_draft_email(parameters, reply=False)
    if action in {"draft_reply"}:
        return hostinger_draft_email(parameters, reply=True)
    if action in {"send_email", "send"}:
        return hostinger_send_email(parameters, confirm=confirm, reply=False)
    if action in {"reply_email", "reply"}:
        return hostinger_send_email(parameters, confirm=confirm, reply=True)
    raise ValueError(f"Accion Hostinger Mail no soportada: {action}")


def normalize_clickup_task(task):
    status = task.get("status") or {}
    return {
        "id": task.get("id"),
        "name": task.get("name"),
        "status": status.get("status") if isinstance(status, dict) else status,
        "url": task.get("url"),
        "assignees": [person.get("username") or person.get("email") for person in task.get("assignees", [])],
        "due_date": task.get("due_date"),
        "priority": task.get("priority"),
    }


def normalize_clickup_space(space, team=None):
    team = team or {}
    return {
        "id": space.get("id"),
        "name": space.get("name"),
        "team_id": team.get("id"),
        "team_name": team.get("name"),
        "private": space.get("private"),
        "multiple_assignees": space.get("multiple_assignees"),
        "archived": space.get("archived"),
    }


def normalize_clickup_list(item):
    folder = item.get("folder") or {}
    space = item.get("space") or {}
    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "content": item.get("content"),
        "task_count": item.get("task_count"),
        "archived": item.get("archived"),
        "folder_id": folder.get("id") if isinstance(folder, dict) else None,
        "folder_name": folder.get("name") if isinstance(folder, dict) else None,
        "space_id": space.get("id") if isinstance(space, dict) else None,
        "space_name": space.get("name") if isinstance(space, dict) else None,
    }


def normalize_clickup_folder(folder):
    return {
        "id": folder.get("id"),
        "name": folder.get("name"),
        "hidden": folder.get("hidden"),
        "archived": folder.get("archived"),
        "task_count": folder.get("task_count"),
        "lists": [normalize_clickup_list(item) for item in folder.get("lists", [])],
    }


def clickup_list_spaces(parameters=None):
    parameters = parameters or {}
    raw_team_id = str(parameters.get("team_id") or "").strip()
    if raw_team_id:
        teams = [{"id": raw_team_id, "name": parameters.get("team_name")}]
    else:
        teams = clickup_request("/team").get("teams", [])
    spaces = []
    failures = []
    for team in teams:
        team_id = str(team.get("id") or "").strip()
        if not team_id:
            continue
        try:
            payload = clickup_request(
                f"/team/{urllib.parse.quote(team_id)}/space",
                params={"archived": str(bool(parameters.get("archived", False))).lower()},
            )
            spaces.extend(normalize_clickup_space(space, team) for space in payload.get("spaces", []))
        except Exception as exc:
            failures.append({"team_id": team_id, "team_name": team.get("name"), "error": brief(str(exc), 260)})
    snapshot = {"updated_at": now_iso(), "spaces": spaces, "failures": failures}
    write_json_file(CLICKUP_STRUCTURE_JSON, snapshot)
    write_json_file(RUNTIME_CLICKUP_STRUCTURE_JSON, snapshot)
    return spaces, failures


def clickup_find_space(parameters):
    space_id = str(parameters.get("space_id") or "").strip()
    if space_id:
        return {"id": space_id, "name": parameters.get("space_name")}
    space_name = str(parameters.get("space_name") or parameters.get("space") or "").strip().lower()
    if not space_name:
        raise ValueError("Falta space_id o space_name para ubicar el Space de ClickUp.")
    spaces, _failures = clickup_list_spaces(parameters)
    exact = [space for space in spaces if str(space.get("name") or "").strip().lower() == space_name]
    if exact:
        return exact[0]
    partial = [space for space in spaces if space_name in str(space.get("name") or "").strip().lower()]
    if len(partial) == 1:
        return partial[0]
    team_matches = [space for space in spaces if str(space.get("team_name") or "").strip().lower() == space_name]
    if team_matches:
        available = ", ".join(space.get("name") or space.get("id") for space in team_matches[:20])
        raise ValueError(
            f"'{parameters.get('space_name') or parameters.get('space')}' es un workspace/equipo de ClickUp, no un Space. "
            f"Usa space_name con uno de estos Spaces: {available}"
        )
    available = ", ".join(space.get("name") or space.get("id") for space in spaces[:12])
    raise ValueError(f"No encontre un Space unico para '{space_name}'. Disponibles: {available}")


def clickup_list_folders_for_space(space_id, archived=False):
    payload = clickup_request(
        f"/space/{urllib.parse.quote(str(space_id))}/folder",
        params={"archived": str(bool(archived)).lower()},
    )
    return [normalize_clickup_folder(folder) for folder in payload.get("folders", [])]


def clickup_find_folder(parameters):
    folder_id = str(parameters.get("folder_id") or "").strip()
    if folder_id:
        return {"id": folder_id, "name": parameters.get("folder_name")}
    folder_name = str(parameters.get("folder_name") or parameters.get("folder") or "").strip().lower()
    if not folder_name:
        raise ValueError("Falta folder_id o folder_name para ubicar el Folder de ClickUp.")
    space = clickup_find_space(parameters)
    folders = clickup_list_folders_for_space(space["id"], archived=bool(parameters.get("archived", False)))
    exact = [folder for folder in folders if str(folder.get("name") or "").strip().lower() == folder_name]
    if exact:
        exact[0]["space_id"] = space["id"]
        exact[0]["space_name"] = space.get("name")
        return exact[0]
    partial = [folder for folder in folders if folder_name in str(folder.get("name") or "").strip().lower()]
    if len(partial) == 1:
        partial[0]["space_id"] = space["id"]
        partial[0]["space_name"] = space.get("name")
        return partial[0]
    available = ", ".join(folder.get("name") or folder.get("id") for folder in folders[:12])
    raise ValueError(f"No encontre un Folder unico para '{folder_name}'. Disponibles: {available}")


def clickup_list_all_lists_for_space(space_id, archived=False):
    lists = []
    folderless = clickup_request(
        f"/space/{urllib.parse.quote(str(space_id))}/list",
        params={"archived": str(bool(archived)).lower()},
    )
    lists.extend(normalize_clickup_list(item) for item in folderless.get("lists", []))
    for folder in clickup_list_folders_for_space(space_id, archived=archived):
        for item in folder.get("lists", []):
            row = dict(item)
            row["folder_id"] = folder.get("id")
            row["folder_name"] = folder.get("name")
            lists.append(row)
    return lists


def clickup_find_list(parameters):
    list_id = str(parameters.get("list_id") or "").strip()
    if list_id:
        return {"id": list_id, "name": parameters.get("list_name") or parameters.get("list")}
    list_name = str(first_value(parameters, "list_name", "list", "target_list") or "").strip().lower()
    if not list_name:
        raise ValueError("Falta list_id o list_name para ubicar List en ClickUp.")
    folder_id = str(parameters.get("folder_id") or "").strip()
    if folder_id:
        payload = clickup_request(
            f"/folder/{urllib.parse.quote(folder_id)}/list",
            params={"archived": str(bool(parameters.get("archived", False))).lower()},
        )
        lists = [normalize_clickup_list(item) for item in payload.get("lists", [])]
    elif parameters.get("folder_name") or parameters.get("folder"):
        folder = clickup_find_folder(parameters)
        lists = folder.get("lists", [])
    else:
        space = clickup_find_space(parameters)
        lists = clickup_list_all_lists_for_space(space["id"], archived=bool(parameters.get("archived", False)))
    exact = [item for item in lists if str(item.get("name") or "").strip().lower() == list_name]
    if exact:
        return exact[0]
    partial = [item for item in lists if list_name in str(item.get("name") or "").strip().lower()]
    if len(partial) == 1:
        return partial[0]
    available = ", ".join(item.get("name") or item.get("id") for item in lists[:20])
    raise ValueError(f"No encontre una List unica para '{list_name}'. Disponibles: {available}")


def clickup_task_name(parameters):
    name = str(first_value(parameters, "name", "title", "subject", "task_name", "task", "asunto") or "").strip()
    if name:
        return name
    source = str(first_value(parameters, "description", "body", "content", "message", "notes", "summary") or "").strip()
    return brief(source, 90) if source else generated_title("Tarea Kim")


def clickup_task_description(parameters):
    return str(first_value(parameters, "description", "body", "content", "message", "notes", "summary", "text") or "").strip()


def clickup_resolve_task_list(parameters, confirm=False):
    list_id = str(parameters.get("list_id") or "").strip()
    if list_id:
        return list_id, {"list_id": list_id, "source": "provided"}, []
    try:
        found = clickup_find_list(parameters)
        return str(found["id"]), {"list": found, "source": "matched"}, []
    except Exception as exc:
        lookup_error = brief(str(exc), 220)
    space = clickup_find_space(parameters)
    list_name = str(first_value(parameters, "list_name", "list", "target_list") or "Kim Inbox").strip() or "Kim Inbox"
    if not confirm:
        return "", {"space": space, "list_name": list_name, "source": "planned_create", "lookup_error": lookup_error}, [
            f"Crear lista '{list_name}' directa en Space {space.get('name') or space.get('id')} antes de crear la tarea."
        ]
    created = clickup_request(f"/space/{urllib.parse.quote(str(space['id']))}/list", method="POST", payload={"name": list_name})
    normalized = normalize_clickup_list(created)
    return str(created.get("id")), {"list": normalized, "source": "created", "lookup_error": lookup_error}, [
        f"Lista '{list_name}' creada en Space {space.get('name') or space.get('id')}."
    ]


def clickup_snapshot_tasks(limit=20):
    data, source = load_json_any([CLICKUP_TASKS_JSON, RUNTIME_CLICKUP_TASKS_JSON])
    if not data:
        return {"ok": True, "mode": "snapshot", "source": None, "tasks": [], "message": "No hay snapshot local de tareas."}
    tasks = data.get("tasks", [])[: int(limit or 20)]
    rows = [
        {
            "id": item.get("id"),
            "name": item.get("name"),
            "status": item.get("status"),
            "team": item.get("team"),
            "space": item.get("space"),
            "folder": item.get("folder"),
            "list": item.get("list"),
            "url": item.get("url"),
        }
        for item in tasks
    ]
    return {"ok": True, "mode": "snapshot", "source": str(source), "tasks": rows, "count": data.get("task_count", len(rows))}


def clickup_task_id_from_url(value):
    text = str(value or "").strip()
    if not text:
        return ""
    match = re.search(r"/t/([A-Za-z0-9_-]+)", text)
    return match.group(1) if match else ""


def clickup_find_task(parameters):
    task_id = str(first_value(parameters, "task_id", "id", "clickup_task_id") or "").strip()
    if task_id:
        return task_id, {"source": "provided", "task_id": task_id}
    task_id = clickup_task_id_from_url(first_value(parameters, "task_url", "url", "link"))
    if task_id:
        return task_id, {"source": "url", "task_id": task_id}
    task_name = str(first_value(parameters, "task_name", "task", "name", "title", "subject") or "").strip().lower()
    if not task_name:
        raise ValueError("Falta task_id, task_url o task_name para ubicar la tarea de ClickUp.")
    list_id = str(parameters.get("list_id") or "").strip()
    if not list_id:
        found = clickup_find_list(parameters)
        list_id = str(found["id"])
    payload = clickup_request(
        f"/list/{urllib.parse.quote(list_id)}/task",
        params={"include_closed": "true", "subtasks": "true", "page": 0},
    )
    tasks = [normalize_clickup_task(task) for task in payload.get("tasks", [])]
    exact = [task for task in tasks if str(task.get("name") or "").strip().lower() == task_name]
    partial = [task for task in tasks if task_name in str(task.get("name") or "").strip().lower()]
    matches = exact or partial
    if len(matches) == 1 and matches[0].get("id"):
        return str(matches[0]["id"]), {"source": "name_lookup", "list_id": list_id, "task": matches[0]}
    available = ", ".join(task.get("name") or task.get("id") for task in tasks[:20])
    raise ValueError(f"No encontre una tarea unica para '{task_name}'. Disponibles en la lista: {available}")


def notion_rich_text(text):
    return [{"type": "text", "text": {"content": str(text or "")[:2000]}}]


def notion_children_from_content(content):
    blocks = []
    for chunk in re.split(r"\n\s*\n", str(content or "").strip())[:30]:
        clean = chunk.strip()
        if not clean:
            continue
        blocks.append(
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": notion_rich_text(clean)},
            }
        )
    return blocks


def build_notion_create_page_payload(parameters):
    parameters = dict(parameters or {})
    title = str(first_value(parameters, "title", "name", "subject", "asunto", "page_title") or "").strip()
    if not title:
        source_text = str(first_value(parameters, "content", "body", "text", "message", "description", "summary") or "").strip()
        title = brief(source_text, 80) if source_text else generated_title("Nota Kim")
    parent_page_id = str(first_value(parameters, "parent_page_id", "page_id", "parent_id", "notion_page_id") or "").strip()
    parent_database_id = str(first_value(parameters, "parent_database_id", "database_id", "parent_database", "notion_database_id") or "").strip()
    if parent_page_id:
        parent = {"type": "page_id", "page_id": parent_page_id}
        properties = {"title": {"title": notion_rich_text(title)}}
    elif parent_database_id:
        title_property = str(parameters.get("title_property") or "Name").strip()
        parent = {"type": "database_id", "database_id": parent_database_id}
        properties = {title_property: {"title": notion_rich_text(title)}}
    else:
        raise ValueError("Falta parent_page_id o parent_database_id; Notion exige un padre para crear paginas.")
    payload = {"parent": parent, "properties": properties}
    children = notion_children_from_content(first_value(parameters, "content", "body", "text", "message", "description", "summary") or "")
    if children:
        payload["children"] = children
    if parameters.get("icon"):
        payload["icon"] = {"type": "emoji", "emoji": str(parameters.get("icon"))[:2]}
    return payload


def confirmation_preview(provider, action, summary, parameters, execution_parameters=None):
    execution_parameters = execution_parameters if execution_parameters is not None else parameters
    return {
        "ok": True,
        "requires_confirmation": True,
        "provider": provider,
        "action": action,
        "summary": summary,
        "parameters": parameters,
        "confirm_payload": {
            "provider": provider,
            "action": action,
            "parameters": execution_parameters,
            "confirm": True,
        },
        "message": "Operacion preparada. Kim debe pedir confirmacion explicita antes de ejecutar con confirm=true.",
    }


def load_prepared_action_state():
    merged = {}
    cleared_ids = set()
    latest_updated = ""
    sources = []
    for path in [API_PREPARED_ACTIONS, RUNTIME_API_PREPARED_ACTIONS]:
        data = read_json_file(path, None)
        if not isinstance(data, dict):
            continue
        sources.append(data)
        latest_updated = max(latest_updated, str(data.get("updated_at") or ""))
        for action_id in data.get("cleared_action_ids") or []:
            if str(action_id or "").strip():
                cleared_ids.add(str(action_id))
    for data in sources:
        for item in data.get("actions") or []:
            if not isinstance(item, dict):
                continue
            action_id = str(item.get("id") or "").strip()
            if action_id and action_id not in cleared_ids:
                merged[action_id] = item
    if not merged:
        return {"updated_at": latest_updated or now_iso(), "actions": [], "cleared_action_ids": sorted(cleared_ids)[-240:]}
    actions = sorted(merged.values(), key=lambda item: str(item.get("prepared_at") or item.get("resolved_at") or ""))
    return {"updated_at": latest_updated or now_iso(), "actions": actions, "cleared_action_ids": sorted(cleared_ids)[-240:]}


def save_prepared_action_state(state):
    state["updated_at"] = now_iso()
    state["actions"] = list(state.get("actions") or [])[-120:]
    state["cleared_action_ids"] = list(dict.fromkeys(str(item) for item in (state.get("cleared_action_ids") or []) if str(item))) [-240:]
    write_json_file_both(API_PREPARED_ACTIONS, RUNTIME_API_PREPARED_ACTIONS, state)
    return state


def store_prepared_action(result, session_id="", transcript=""):
    confirm_payload = result.get("confirm_payload") if isinstance(result, dict) else None
    if not confirm_payload:
        return None
    state = load_prepared_action_state()
    action_id = "ACT-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S-") + secrets.token_hex(3).upper()
    item = {
        "id": action_id,
        "status": "prepared",
        "prepared_at": now_iso(),
        "session_id": session_id,
        "provider": confirm_payload.get("provider") or result.get("provider"),
        "action": confirm_payload.get("action") or result.get("action"),
        "summary": result.get("summary") or "",
        "confirm_payload": confirm_payload,
        "preview": result.get("preview"),
        "transcript_excerpt": brief(sanitize_text_for_log(transcript), 900),
    }
    state["actions"].append(item)
    save_prepared_action_state(state)
    return item


def pending_prepared_actions(session_id=""):
    actions = load_prepared_action_state().get("actions", [])
    rows = [item for item in actions if item.get("status") == "prepared"]
    if session_id:
        rows = [item for item in rows if item.get("session_id") == session_id]
    rows = rows[-12:]
    return [
        {
            "id": item.get("id"),
            "prepared_at": item.get("prepared_at"),
            "session_id": item.get("session_id"),
            "provider": item.get("provider"),
            "action": item.get("action"),
            "summary": item.get("summary"),
            "preview": item.get("preview"),
        }
        for item in rows
    ]


def find_prepared_action(action_id="", session_id=""):
    actions = load_prepared_action_state().get("actions", [])
    if action_id:
        for item in reversed(actions):
            if str(item.get("id")) == str(action_id):
                return item
        raise ValueError(f"No encontre accion preparada {action_id}.")
    candidates = [item for item in actions if item.get("status") == "prepared"]
    if session_id:
        scoped = [item for item in candidates if item.get("session_id") == session_id]
        if scoped:
            candidates = scoped
    if not candidates:
        raise ValueError("No hay acciones preparadas pendientes de confirmar.")
    return candidates[-1]


def mark_prepared_action(action_id, status, result=None):
    state = load_prepared_action_state()
    for item in state.get("actions", []):
        if str(item.get("id")) == str(action_id):
            item["status"] = status
            item["resolved_at"] = now_iso()
            if result is not None:
                item["result_summary"] = brief(json.dumps(result, ensure_ascii=False), 1200)
            save_prepared_action_state(state)
            return item
    return None


def clear_prepared_action(action_id):
    state = load_prepared_action_state()
    before = len(state.get("actions", []))
    state["actions"] = [item for item in state.get("actions", []) if str(item.get("id")) != str(action_id)]
    state.setdefault("cleared_action_ids", []).append(str(action_id))
    if len(state.get("actions", [])) != before:
        save_prepared_action_state(state)
        return True
    save_prepared_action_state(state)
    return False


def execute_prepared_action(action_id="", session_id="", transcript=""):
    item = find_prepared_action(action_id, session_id=session_id)
    payload = item.get("confirm_payload") or {}
    if item.get("status") != "prepared":
        raise ValueError(f"La accion {item.get('id')} ya no esta pendiente; estado={item.get('status')}.")
    result = run_api_bridge(
        payload.get("provider", ""),
        payload.get("action", ""),
        payload.get("parameters") or {},
        confirm=True,
        session_id=session_id or item.get("session_id", ""),
        transcript=transcript,
    )
    mark_prepared_action(item.get("id"), "confirmed" if result.get("ok") else "failed", result)
    if result.get("ok"):
        clear_prepared_action(item.get("id"))
    result["prepared_action_id"] = item.get("id")
    result["prepared_action_status"] = "confirmed" if result.get("ok") else "failed"
    return result


def agent_action_defaults(action, parameters):
    data = dict(parameters or {})
    action = (action or "").strip().lower()
    if action in {"send_email", "send_mail", "email", "correo", "enviar_correo", "mandar_correo"}:
        if not first_value(data, "subject", "title", "name", "asunto"):
            data["subject"] = hostinger_default_subject(hostinger_mailbox_from_parameters(data), reply=False)
        if not first_value(data, "body", "text", "content", "message", "description", "cuerpo"):
            data["body"] = data.get("notes") or "Mensaje enviado desde Kim Live."
        return "hostinger_mail", "send_email", data
    if action in {"reply_email", "reply", "responder_correo"}:
        return "hostinger_mail", "reply_email", data
    if action in {"mark_spam", "spam", "junk", "correo_basura", "mover_spam"}:
        return "hostinger_mail", "mark_spam", data
    if action in {"move_to_trash", "delete_email", "trash_email", "eliminar_correo", "basura"}:
        return "hostinger_mail", "move_to_trash", data
    if action in {"archive_email", "archive_message", "archivar_correo"}:
        return "hostinger_mail", "archive_message", data
    if action in {"send_sms", "sms", "text_message", "mensaje_sms", "mandar_sms"}:
        return "twilio", "send_sms", data
    if action in {"send_whatsapp", "whatsapp", "whatsapp_message", "mandar_whatsapp"}:
        return "twilio", "send_whatsapp", data
    if action in {"call_phone", "call", "make_call", "llamar", "llamada"}:
        return "twilio", "call_phone", data
    if action in {"call_report", "latest_call", "get_call", "call_summary", "reporte_llamada", "ultima_llamada"}:
        return "twilio", "call_report", data
    if action in {"schedule_call", "programar_llamada", "agendar_llamada"}:
        return "twilio", "schedule_call", data
    if action in {"schedule_sms", "programar_sms", "agendar_sms"}:
        return "twilio", "schedule_sms", data
    if action in {"save_contact", "create_contact", "upsert_contact", "guardar_contacto", "crear_contacto"}:
        return "crm", "upsert_contact", data
    if action in {"create_task", "add_task", "task", "tarea", "registrar_tarea", "crear_tarea"}:
        if not first_value(data, "name", "title", "subject", "task_name", "task", "asunto"):
            data["name"] = generated_title("Tarea Kim")
        if not first_value(data, "space_name", "space", "workspace", "team_space") and not data.get("list_id"):
            data["space_name"] = "Neorgana"
            data["list_name"] = first_value(data, "list_name", "list", "target_list", default="Kim Inbox") or "Kim Inbox"
            data["routing_note"] = "Default operativo KIM-0047: sin destino explicito, Kim usa Neorgana / Kim Inbox."
        return "clickup", "create_task", data
    if action in {"update_task", "change_task", "cambiar_tarea", "actualizar_tarea"}:
        return "clickup", "update_task", data
    if action in {"comment_task", "comentario_tarea", "comentar_tarea"}:
        return "clickup", "comment_task", data
    if action in {"create_page", "note", "nota", "notion_note", "crear_nota"}:
        if not first_value(data, "title", "name", "subject", "asunto", "page_title"):
            data["title"] = generated_title("Nota Kim")
        return "notion", "create_page", data
    return "", action, data


def api_bridge_templates():
    return {
        "agent_action": {
            "description": "Accion de alto nivel para que Kim escriba por API sin reconstruir JSON complicado.",
            "actions": [
                "send_email",
                "reply_email",
                "send_sms",
                "send_whatsapp",
                "call_phone",
                "call_report",
                "schedule_call",
                "schedule_sms",
                "save_contact",
                "mark_spam",
                "move_to_trash",
                "archive_email",
                "create_task",
                "update_task",
                "comment_task",
                "create_page",
                "pipedrive_upsert_person",
                "pipedrive_create_deal",
                "pipedrive_create_activity",
                "pipedrive_create_note",
            ],
            "confirmation": "Toda escritura devuelve prepared_action_id. El doctor confirma con action=confirm_prepared o el boton del frontend.",
            "security": "Desde 1.5.11, ejecutar una accion preparada o confirm=true requiere frase de autorizacion o PIN si estan configurados.",
            "examples": [
                {
                    "provider": "all",
                    "action": "send_email",
                    "parameters": {"to": "doctor@example.com", "subject": "Seguimiento", "body": "Mensaje completo."},
                    "confirm": False,
                },
                {
                    "provider": "all",
                    "action": "create_task",
                    "parameters": {"space_name": "Neorgana", "list_name": "Kim Inbox", "title": "Llamar cliente", "body": "Notas de la tarea."},
                    "confirm": False,
                },
                {
                    "provider": "all",
                    "action": "send_sms",
                    "parameters": {"to": "+525500000000", "body": "Mensaje de prueba de Kim Live."},
                    "confirm": False,
                },
                {
                    "provider": "all",
                    "action": "schedule_call",
                    "parameters": {"to": "+525500000000", "contact_name": "Cliente", "delay_minutes": 30},
                    "confirm": False,
                },
            ],
        },
        "crm": {
            "status": {
                "rule": "Valida la base local en BIFROST/CRM sin modificar datos.",
            },
            "list_contacts": {
                "optional": ["query", "contact_type", "limit"],
                "rule": "Consulta clientes/contactos guardados en BIFROST/CRM antes de llamar, mandar SMS o registrar notas.",
            },
            "upsert_contact": {
                "required": ["display_name or phone or email"],
                "aliases": {
                    "display_name": ["name", "nombre", "client_name", "contact_name"],
                    "phone": ["telefono", "to", "mobile", "celular"],
                    "email": ["correo", "mail"],
                    "company": ["empresa", "organization", "organizacion"],
                    "contact_type": ["tipo", "client_type", "categoria"],
                    "notes": ["nota", "body", "description"],
                },
                "defaults": {
                    "contact_type": "client",
                },
                "rule": "Preparar con confirm=false. Guardar o actualizar contactos requiere confirmacion explicita y queda exportado como Markdown en BIFROST/CRM.",
            },
            "record_note": {
                "required": ["body"],
                "aliases": {
                    "body": ["note", "nota", "message", "content"],
                    "phone": ["telefono", "to", "client_phone"],
                },
                "rule": "Registra una nota interna asociada al contacto si se conoce telefono o correo.",
            },
        },
        "pipedrive": {
            "status": {
                "rule": "Valida token, usuario y empresa de Pipedrive sin modificar datos.",
            },
            "search_persons": {
                "optional": ["term", "query", "name", "email", "phone", "limit"],
                "aliases": {
                    "term": ["query", "q", "search", "name", "contact_name", "client_name"],
                    "phone": ["telefono", "to", "from"],
                    "email": ["correo"],
                },
                "rule": "Usa busqueda flexible antes de afirmar que no existe un contacto. Devuelve match_score y candidatos cercanos.",
            },
            "upsert_person": {
                "required": ["name or email or phone"],
                "aliases": {
                    "name": ["display_name", "contact_name", "client_name", "nombre"],
                    "phone": ["telefono", "mobile", "to", "from"],
                    "email": ["correo"],
                    "organization": ["company", "empresa", "org_name"],
                    "notes": ["note", "description", "body"],
                },
                "rule": "Preparar con confirm=false. Al confirmar crea/actualiza persona en Pipedrive y sincroniza contacto local BIFROST CRM.",
            },
            "create_deal": {
                "required": ["title"],
                "aliases": {
                    "title": ["name", "deal_title", "subject"],
                    "person_id": ["contact_id", "pipedrive_person_id"],
                    "organization": ["company", "empresa", "org_name"],
                },
                "rule": "Preparar con confirm=false. Puede ligar person_id/org_id si Kim los conoce o buscar persona antes.",
            },
            "create_activity": {
                "required": ["subject"],
                "aliases": {
                    "subject": ["title", "name", "asunto"],
                    "type": ["activity_type", "tipo"],
                    "due_date": ["date", "fecha"],
                    "due_time": ["time", "hora"],
                    "note": ["body", "description", "notes"],
                },
                "defaults": {"type": "call"},
                "rule": "Preparar con confirm=false. Usar para seguimiento, llamadas, reuniones y tareas comerciales.",
            },
            "create_note": {
                "required": ["content"],
                "aliases": {
                    "content": ["body", "note", "notes", "text", "message"],
                    "person_id": ["contact_id", "pipedrive_person_id"],
                    "deal_id": ["pipedrive_deal_id"],
                },
                "rule": "Preparar con confirm=false. Usar para registrar contexto comercial o resumen de llamada en Pipedrive.",
            },
        },
        "twilio": {
            "status": {
                "rule": "Valida credenciales Twilio, cuenta y numeros sin enviar mensajes.",
            },
            "list_numbers": {
                "rule": "Lista numeros comprados/asignados a la cuenta y sus capacidades voice/sms/mms.",
            },
            "send_sms": {
                "required": ["to", "body"],
                "aliases": {
                    "to": ["recipient", "phone", "telefono", "destinatario"],
                    "from": ["from_number", "sender"],
                    "body": ["message", "text", "content", "mensaje"],
                    "messaging_service_sid": ["service_sid"],
                },
                "defaults": {
                    "from": twilio_default_from_number() or "numero Twilio con capacidad SMS",
                },
                "rule": "Preparar con confirm=false. Enviar SMS requiere confirmacion explicita y luego confirm_prepared o confirm=true.",
            },
            "send_whatsapp": {
                "required": ["to", "body", "from or messaging_service_sid"],
                "rule": "Usa formato whatsapp:+numero. Requiere sender WhatsApp aprobado o sandbox Twilio; preparar con confirm=false.",
            },
            "call_phone": {
                "required": ["to"],
                "aliases": {
                    "to": ["recipient", "phone", "telefono", "destinatario"],
                    "from": ["from_number", "sender"],
                    "url": ["voice_url", "twiml_url"],
                    "contact_name": ["client_name", "name", "nombre"],
                    "call_context": ["context", "client_context", "contexto"],
                    "objective": ["goal", "mission", "objetivo", "mision"],
                    "questions": ["preguntas", "ask", "asks"],
                    "report_to_doctor": ["report", "reporte", "return_with"],
                },
                "defaults": {
                    "from": twilio_default_from_number() or "numero Twilio con capacidad Voice",
                    "url": "https://kim.aipeople.app/twilio/voice",
                },
                "rule": "Preparar con confirm=false. Si el doctor pide llamar a una tercera persona, SIEMPRE incluye contact_name, relationship, call_context, objective, questions y report_to_doctor. Llamar requiere confirmacion explicita; la conversacion se guarda en BIFROST/MEMORY/calls y BIFROST/CRM.",
            },
            "call_report": {
                "optional": ["call_sid", "context_id", "phone", "contact_name", "limit"],
                "aliases": {
                    "call_sid": ["sid", "callSid"],
                    "context_id": ["kim_context_id"],
                    "phone": ["to", "from", "telefono", "recipient"],
                    "contact_name": ["client_name", "name", "query"],
                },
                "rule": "Lee transcripciones y contexto guardados en BIFROST/MEMORY/calls. Usa latest_call sin filtros para reportar la ultima llamada.",
            },
            "schedule_call": {
                "required": ["to", "due_at or delay_minutes"],
                "aliases": {
                    "due_at": ["scheduled_at", "run_at", "datetime", "cuando"],
                    "delay_minutes": ["minutes", "minutos", "en_minutos"],
                },
                "rule": "Preparar con confirm=false. Al confirmar, queda en BIFROST/CRM/scheduled_actions y el scheduler local la ejecuta cuando venza.",
            },
            "schedule_sms": {
                "required": ["to", "body", "due_at or delay_minutes"],
                "rule": "Preparar con confirm=false. Al confirmar, queda programado en la base local CRM.",
            },
        },
        "hostinger_mail": {
            "send_email": {
                "required": ["to", "subject", "body"],
                "mailboxes": hostinger_known_mailboxes(),
                "default_mailbox": DEFAULT_HOSTINGER_MAILBOX,
                "mailbox_aliases": HOSTINGER_MAILBOX_ALIASES,
                "aliases": {
                    "mailbox": ["from", "account", "sender", "selected_mailbox", "active_mailbox"],
                    "from_name": ["sender_name", "display_name", "nombre_remitente"],
                    "to": ["recipient", "email", "client_email", "destinatario"],
                    "subject": ["title", "name", "asunto"],
                    "body": ["text", "content", "message", "description", "cuerpo"],
                    "signature": ["firma", "email_signature", "email_firma"],
                    "no_signature": ["omit_signature", "skip_signature", "sin_firma", "omitir_firma"],
                },
                "defaults": {
                    "from_name": HOSTINGER_MAILBOX_DISPLAY_NAMES,
                    "subject": "Se genera por marca: AI People o Tesca Elements.",
                    "signature": KIM_EMAIL_SIGNATURE,
                },
                "example": {
                    "provider": "hostinger_mail",
                    "action": "send_email",
                    "parameters": {
                        "to": "cliente@example.com",
                        "subject": "Seguimiento Tesca Elements",
                        "body": "Mensaje completo.",
                    },
                    "confirm": False,
                },
                "rule": "Si el doctor dice manda/envia, usa send_email, no draft_email. El servidor agrega firma Kim Yan automaticamente salvo no_signature=true. Luego usa confirm_payload con confirm=true.",
            },
            "switch_mailbox": {
                "required": ["mailbox"],
                "aliases": {
                    "mailbox": ["from", "account", "sender", "selected_mailbox", "active_mailbox"],
                },
                "rule": "Usa switch_mailbox cuando el doctor pida cambiar de buzon. Responde con selected_mailbox y luego continua con list_messages, get_message o send_email usando ese buzon.",
            },
            "reply_email": {
                "required": ["message_id", "body"],
                "aliases": {
                    "mailbox": ["from", "account", "sender", "selected_mailbox", "active_mailbox"],
                    "from_name": ["sender_name", "display_name", "nombre_remitente"],
                    "message_id": ["uid", "id", "reply_to_message_id"],
                    "body": ["text", "content", "message", "description", "cuerpo"],
                    "subject": ["title", "name", "asunto"],
                    "signature": ["firma", "email_signature", "email_firma"],
                    "no_signature": ["omit_signature", "skip_signature", "sin_firma", "omitir_firma"],
                },
                "defaults": {
                    "to": "se toma del From del mensaje original",
                    "subject": "Re: asunto original",
                    "in_reply_to": "Message-ID original",
                    "signature": KIM_EMAIL_SIGNATURE,
                },
            },
            "message_hygiene": {
                "actions": ["list_folders", "move_message", "mark_spam", "move_to_trash", "archive_message"],
                "required": ["mailbox", "message_id or message_ids"],
                "aliases": {
                    "mailbox": ["from", "account", "sender", "selected_mailbox", "active_mailbox"],
                    "message_ids": ["uids", "ids", "message_id", "uid", "id"],
                    "target_folder": ["destination_folder", "to_folder"],
                },
                "rule": "Mover correos a Junk/Trash/Archive siempre requiere confirm=false, confirmacion del doctor y luego confirm_prepared. No hay borrado permanente automatico.",
            },
        },
        "clickup": {
            "create_task": {
                "required": ["space_name or list_id", "name"],
                "aliases": {
                    "name": ["title", "subject", "task_name", "task", "asunto"],
                    "description": ["body", "content", "message", "notes", "summary", "text"],
                    "list_name": ["list", "target_list"],
                    "space_name": ["space", "workspace", "team_space"],
                },
                "defaults": {
                    "name": "se genera desde description o 'Tarea Kim <timestamp>'",
                    "list_name": "Kim Inbox si hay space_name y no se indica lista",
                },
                "rule": "space_name debe ser un Space real, no el workspace/equipo. Si el doctor dice Tesca Elements, primero lista spaces y elige Neorgana, Equibio, Client Follow-up, etc. Si falta list_id pero hay space_name, el bridge busca list_name o prepara crear la lista antes de la tarea.",
            },
            "create_list": {
                "required": ["space_name", "name"],
                "aliases": {
                    "name": ["list_name", "list", "title", "subject", "project"],
                    "space_name": ["space", "workspace"],
                },
            },
            "create_folder": {
                "required": ["space_name", "name"],
                "aliases": {
                    "name": ["folder_name", "folder", "title", "client", "client_name", "project"],
                    "space_name": ["space", "workspace"],
                },
            },
        },
        "notion": {
            "create_page": {
                "required": ["parent_page_id or parent_database_id", "title"],
                "aliases": {
                    "title": ["name", "subject", "asunto", "page_title"],
                    "content": ["body", "text", "message", "description", "summary"],
                    "parent_page_id": ["page_id", "parent_id", "notion_page_id"],
                    "parent_database_id": ["database_id", "parent_database", "notion_database_id"],
                },
                "defaults": {
                    "title": "se genera desde content o 'Nota Kim <timestamp>'",
                    "title_property": "Name para bases de datos",
                },
                "rule": "Si falta parent, Kim debe buscar/leer el destino antes de crear; si falta title, el bridge lo genera.",
            },
        },
    }


def api_bridge_self_test():
    tests = []

    def run_case(name, func):
        try:
            result = func()
            tests.append({"name": name, "ok": bool(result.get("ok", True)), "result": result})
        except Exception as exc:
            tests.append({"name": name, "ok": False, "error": brief(str(exc), 500)})

    run_case(
        "templates_available",
        lambda: {"ok": True, "providers": sorted(api_bridge_templates().keys())},
    )
    run_case(
        "hostinger_send_alias_dry_run",
        lambda: run_hostinger_mail_bridge(
            "send_email",
            {
                "recipient": "doctoryehoshua@gmail.com",
                "title": "Kim API template dry run",
                "content": "Dry run sin envio real.",
            },
            confirm=False,
        ),
    )
    run_case(
        "hostinger_reply_template_dry_run",
        lambda: run_hostinger_mail_bridge(
            "reply_email",
            {
                "message_id": (hostinger_list_messages({"limit": 1}).get("messages") or [{"uid": "1"}])[0]["uid"],
                "content": "Dry run de respuesta con message_id.",
            },
            confirm=False,
        ),
    )
    run_case(
        "notion_title_alias_dry_run",
        lambda: run_notion_bridge(
            "create_page",
            {
                "parent_page_id": "test-parent",
                "subject": "Prueba template Notion",
                "body": "Dry run sin escritura.",
            },
            confirm=False,
        ),
    )
    run_case(
        "clickup_task_template_dry_run",
        lambda: run_clickup_bridge(
            "create_task",
            {
                "space_name": "Neorgana",
                "list_name": "Kim API Dry Run",
                "title": "Prueba template ClickUp",
                "content": "Dry run sin crear lista ni tarea.",
            },
            confirm=False,
        ),
    )
    run_case(
        "clickup_workspace_guardrail",
        lambda: run_clickup_bridge(
            "create_task",
            {
                "space_name": "Tesca Elements",
                "list_name": "Nueva",
                "title": "Debe explicar workspace vs Space",
                "content": "Dry run de guardrail.",
            },
            confirm=False,
        ),
    )
    ok = all(item.get("ok") for item in tests[:-1]) and not tests[-1].get("ok")
    return {
        "ok": ok,
        "provider": "all",
        "action": "self_test",
        "mode": "dry_run_no_write",
        "tests": tests,
        "message": "Self-test de templates ejecutado desde Kim API bridge; no se enviaron correos ni se crearon objetos.",
    }


def run_clickup_bridge(action, parameters, confirm=False):
    action = (action or "").strip().lower()
    parameters = parameters or {}
    if action in {"status", "me"}:
        status = api_bridge_config_status(live=True)["clickup"]
        return {"ok": True, "provider": "clickup", "action": action, "status": status}
    if action == "inventory":
        teams = clickup_request("/team").get("teams", [])
        return {
            "ok": True,
            "provider": "clickup",
            "action": action,
            "teams": [{"id": team.get("id"), "name": team.get("name")} for team in teams],
        }
    if action in {"list_spaces", "spaces"}:
        spaces, failures = clickup_list_spaces(parameters)
        return {
            "ok": True,
            "provider": "clickup",
            "action": action,
            "spaces": spaces,
            "failures": failures,
            "count": len(spaces),
        }
    if action in {"list_folders", "folders"}:
        space = clickup_find_space(parameters)
        folders = clickup_list_folders_for_space(space["id"], archived=bool(parameters.get("archived", False)))
        return {
            "ok": True,
            "provider": "clickup",
            "action": action,
            "space": space,
            "folders": folders,
            "count": len(folders),
        }
    if action in {"list_lists", "lists"}:
        folder_id = str(parameters.get("folder_id") or "").strip()
        folder = None
        if not folder_id and (parameters.get("folder_name") or parameters.get("folder")):
            folder = clickup_find_folder(parameters)
            folder_id = str(folder["id"])
        if folder_id:
            payload = clickup_request(
                f"/folder/{urllib.parse.quote(folder_id)}/list",
                params={"archived": str(bool(parameters.get("archived", False))).lower()},
            )
            scope = {"folder_id": folder_id, "folder_name": folder.get("name") if folder else parameters.get("folder_name")}
        else:
            space = clickup_find_space(parameters)
            payload = clickup_request(
                f"/space/{urllib.parse.quote(str(space['id']))}/list",
                params={"archived": str(bool(parameters.get("archived", False))).lower()},
            )
            scope = {"space_id": space["id"], "space_name": space.get("name"), "folderless": True}
        lists = [normalize_clickup_list(item) for item in payload.get("lists", [])]
        return {
            "ok": True,
            "provider": "clickup",
            "action": action,
            "scope": scope,
            "lists": lists,
            "count": len(lists),
        }
    if action in {"list_tasks", "tasks"}:
        list_id = str(parameters.get("list_id") or "").strip()
        limit = int(parameters.get("limit") or 20)
        if not list_id:
            return clickup_snapshot_tasks(limit=limit)
        payload = clickup_request(
            f"/list/{urllib.parse.quote(list_id)}/task",
            params={
                "include_closed": str(bool(parameters.get("include_closed", False))).lower(),
                "subtasks": "true",
                "page": 0,
            },
        )
        return {
            "ok": True,
            "provider": "clickup",
            "action": action,
            "list_id": list_id,
            "tasks": [normalize_clickup_task(task) for task in payload.get("tasks", [])[:limit]],
        }
    if action == "get_task":
        task_id = str(parameters.get("task_id") or "").strip()
        if not task_id:
            raise ValueError("Falta task_id para leer tarea de ClickUp.")
        task = clickup_request(f"/task/{urllib.parse.quote(task_id)}")
        return {"ok": True, "provider": "clickup", "action": action, "task": normalize_clickup_task(task), "raw": task}
    if action == "create_folder":
        space = clickup_find_space(parameters)
        name = str(first_value(parameters, "name", "folder_name", "folder", "title", "client", "client_name", "project") or "").strip()
        if not name:
            name = generated_title("Folder Kim")
        payload = {"name": name}
        if not confirm:
            return confirmation_preview(
                "clickup",
                action,
                f"Crear Folder '{name}' en Space {space.get('name') or space.get('id')}.",
                {"space_id": space["id"], **payload},
            )
        folder = clickup_request(f"/space/{urllib.parse.quote(str(space['id']))}/folder", method="POST", payload=payload)
        return {
            "ok": True,
            "provider": "clickup",
            "action": action,
            "folder": normalize_clickup_folder(folder),
            "confirmed": True,
        }
    if action == "create_list":
        name = str(first_value(parameters, "name", "list_name", "list", "title", "subject", "project") or "").strip()
        if not name:
            name = generated_title("List Kim")
        payload = {"name": name}
        for key in ["content", "due_date", "due_date_time", "priority", "assignee", "status"]:
            if parameters.get(key) not in (None, ""):
                payload[key] = parameters.get(key)
        folder_id = str(parameters.get("folder_id") or "").strip()
        folder = None
        if not folder_id and (parameters.get("folder_name") or parameters.get("folder")):
            folder = clickup_find_folder(parameters)
            folder_id = str(folder["id"])
        if folder_id:
            endpoint = f"/folder/{urllib.parse.quote(folder_id)}/list"
            scope = {"folder_id": folder_id, "folder_name": folder.get("name") if folder else parameters.get("folder_name")}
            summary = f"Crear List '{name}' dentro del Folder {scope.get('folder_name') or folder_id}."
        else:
            space = clickup_find_space(parameters)
            endpoint = f"/space/{urllib.parse.quote(str(space['id']))}/list"
            scope = {"space_id": space["id"], "space_name": space.get("name"), "folderless": True}
            summary = f"Crear List '{name}' directa en el Space {space.get('name') or space.get('id')}."
        if not confirm:
            return confirmation_preview("clickup", action, summary, {**scope, **payload})
        created = clickup_request(endpoint, method="POST", payload=payload)
        return {
            "ok": True,
            "provider": "clickup",
            "action": action,
            "list": normalize_clickup_list(created),
            "scope": scope,
            "confirmed": True,
        }
    if action == "create_task":
        name = clickup_task_name(parameters)
        list_id, list_scope, planned_steps = clickup_resolve_task_list(parameters, confirm=confirm)
        payload = {"name": name}
        description = clickup_task_description(parameters)
        if description:
            payload["description"] = description
        for key in ["description", "status", "priority", "due_date", "due_date_time"]:
            if parameters.get(key) not in (None, ""):
                payload[key] = parameters.get(key)
        if not confirm:
            execution_parameters = dict(parameters)
            execution_parameters.update({"name": name})
            if description and not execution_parameters.get("description"):
                execution_parameters["description"] = description
            if list_id:
                execution_parameters["list_id"] = list_id
            elif list_scope.get("list_name"):
                execution_parameters["list_name"] = list_scope["list_name"]
                execution_parameters["space_id"] = (list_scope.get("space") or {}).get("id")
                execution_parameters["space_name"] = (list_scope.get("space") or {}).get("name")
            preview = {"payload": payload, "list_id": list_id, "list_scope": list_scope, "planned_steps": planned_steps}
            target = list_id or f"nueva lista {list_scope.get('list_name')}"
            return confirmation_preview(
                "clickup",
                action,
                f"Crear tarea '{name}' en {target}.",
                preview,
                execution_parameters=execution_parameters,
            )
        task = clickup_request(f"/list/{urllib.parse.quote(list_id)}/task", method="POST", payload=payload)
        return {
            "ok": True,
            "provider": "clickup",
            "action": action,
            "task": normalize_clickup_task(task),
            "list_scope": list_scope,
            "planned_steps": planned_steps,
            "confirmed": True,
        }
    if action == "update_task":
        task_id, task_scope = clickup_find_task(parameters)
        fields = dict(parameters.get("fields") or {})
        for key in ["name", "description", "status", "priority", "due_date", "due_date_time"]:
            if parameters.get(key) not in (None, ""):
                fields[key] = parameters.get(key)
        if not task_id or not fields:
            raise ValueError("Faltan task_id y fields para actualizar tarea en ClickUp.")
        if not confirm:
            return confirmation_preview("clickup", action, f"Actualizar tarea {task_id}.", {"task_id": task_id, "fields": fields, "task_scope": task_scope})
        task = clickup_request(f"/task/{urllib.parse.quote(task_id)}", method="PUT", payload=fields)
        return {"ok": True, "provider": "clickup", "action": action, "task": normalize_clickup_task(task), "task_scope": task_scope, "confirmed": True}
    if action == "comment_task":
        task_id, task_scope = clickup_find_task(parameters)
        comment_text = str(first_value(parameters, "comment_text", "text", "body", "content", "message", "description") or "").strip()
        if not task_id or not comment_text:
            raise ValueError("Faltan task_id y comment_text para comentar tarea en ClickUp.")
        payload = {"comment_text": comment_text}
        if not confirm:
            return confirmation_preview("clickup", action, f"Comentar tarea {task_id}.", {"task_id": task_id, "comment_text": comment_text, "task_scope": task_scope})
        comment = clickup_request(f"/task/{urllib.parse.quote(task_id)}/comment", method="POST", payload=payload)
        return {"ok": True, "provider": "clickup", "action": action, "comment": comment, "task_scope": task_scope, "confirmed": True}
    raise ValueError(f"Accion ClickUp no soportada: {action}")


def run_notion_bridge(action, parameters, confirm=False):
    action = (action or "").strip().lower()
    parameters = parameters or {}
    if action in {"status", "me"}:
        return {"ok": True, "provider": "notion", "action": action, "status": api_bridge_config_status(live=True)["notion"]}
    if not load_keychain_secret(NOTION_KEYCHAIN_SERVICE, required=False):
        return {
            "ok": False,
            "provider": "notion",
            "action": action,
            "configured": False,
            "message": (
                "Notion no tiene token de integracion en Keychain. "
                f"Guarda uno como service={NOTION_KEYCHAIN_SERVICE}, account={KEYCHAIN_ACCOUNT}, "
                "o usa Codex Desktop MCP para tareas Notion mientras conectamos la API directa."
            ),
        }
    if action == "search":
        query = str(parameters.get("query") or "").strip()
        page_size = min(int(parameters.get("page_size") or 10), 20)
        result = notion_request("/search", method="POST", payload={"query": query, "page_size": page_size})
        rows = []
        for item in result.get("results", []):
            rows.append(
                {
                    "id": item.get("id"),
                    "object": item.get("object"),
                    "url": item.get("url"),
                    "created_time": item.get("created_time"),
                    "last_edited_time": item.get("last_edited_time"),
                }
            )
        return {"ok": True, "provider": "notion", "action": action, "results": rows}
    if action == "get_page":
        page_id = str(parameters.get("page_id") or "").strip()
        if not page_id:
            raise ValueError("Falta page_id para leer pagina de Notion.")
        page = notion_request(f"/pages/{urllib.parse.quote(page_id)}")
        return {"ok": True, "provider": "notion", "action": action, "page": page}
    if action == "create_page":
        payload = build_notion_create_page_payload(parameters)
        title = str(first_value(parameters, "title", "name", "subject", "asunto", "page_title") or "").strip()
        if not title:
            title = brief(str(first_value(parameters, "content", "body", "text", "message", "description", "summary") or ""), 80) or "Nota Kim"
        parent = payload.get("parent", {})
        if not confirm:
            return confirmation_preview(
                "notion",
                action,
                f"Crear pagina '{title}' bajo {parent.get('type')} {parent.get(parent.get('type'), '')}.",
                payload,
                execution_parameters=parameters,
            )
        page = notion_request("/pages", method="POST", payload=payload)
        return {"ok": True, "provider": "notion", "action": action, "page": page, "confirmed": True}
    if action == "update_page_properties":
        page_id = str(parameters.get("page_id") or "").strip()
        properties = parameters.get("properties") or {}
        if not page_id or not properties:
            raise ValueError("Faltan page_id y properties para actualizar Notion.")
        payload = {"properties": properties}
        if not confirm:
            return confirmation_preview("notion", action, f"Actualizar propiedades de pagina {page_id}.", payload)
        page = notion_request(f"/pages/{urllib.parse.quote(page_id)}", method="PATCH", payload=payload)
        return {"ok": True, "provider": "notion", "action": action, "page": page, "confirmed": True}
    raise ValueError(f"Accion Notion no soportada: {action}")


def run_gmail_bridge(action, parameters, confirm=False):
    action = (action or "").strip().lower()
    parameters = parameters or {}
    if action in {"status", "me"}:
        return {"ok": True, "provider": "gmail", "action": action, "status": gmail_status(live=True)}
    if action in {"auth_url", "authorize", "connect"}:
        return {
            "ok": True,
            "provider": "gmail",
            "action": action,
            "auth_url": "https://kim.aipeople.app/oauth/google/start",
            "message": "Abre auth_url y autoriza Gmail. Despues Kim podra leer correos en modo solo lectura.",
        }
    if not gmail_oauth_configured():
        return {
            "ok": False,
            "provider": "gmail",
            "action": action,
            "configured": False,
            "message": "Faltan client_id/client_secret de Google Gmail en Keychain.",
        }
    if not gmail_authorized():
        return {
            "ok": False,
            "provider": "gmail",
            "action": action,
            "authorized": False,
            "auth_url": "https://kim.aipeople.app/oauth/google/start",
            "message": "Gmail esta configurado pero falta autorizacion OAuth del doctor.",
        }
    if action in {"profile", "get_profile"}:
        return {"ok": True, "provider": "gmail", "action": action, "profile": gmail_request("/users/me/profile")}
    if action in {"list_messages", "list_emails", "inbox", "search"}:
        return gmail_list_messages(parameters)
    if action in {"get_message", "read_message", "read_email"}:
        return gmail_get_message(parameters)
    raise ValueError(f"Accion Gmail no soportada: {action}")


def record_api_bridge_action(provider, action, parameters, result, session_id="", transcript=""):
    event = {
        "at": now_iso(),
        "session_id": session_id,
        "provider": provider,
        "action": action,
        "confirmed": bool(result.get("confirmed")) if isinstance(result, dict) else False,
        "requires_confirmation": bool(result.get("requires_confirmation")) if isinstance(result, dict) else False,
        "ok": bool(result.get("ok")) if isinstance(result, dict) else False,
        "parameters": sanitize_for_log(parameters),
        "result_summary": brief(json.dumps(result, ensure_ascii=False), 900),
        "transcript_excerpt": brief(sanitize_text_for_log(transcript), 900),
    }
    append_jsonl_any([API_BRIDGE_LOG, RUNTIME_API_BRIDGE_LOG], event)
    append_memory("api_bridge_action", event)
    append_daily_note(
        f"Kim API bridge: {provider}/{action}; ok={event['ok']}; "
        f"confirmed={event['confirmed']}; requires_confirmation={event['requires_confirmation']}"
    )
    return event


def run_api_bridge(provider, action, parameters=None, confirm=False, session_id="", transcript=""):
    provider = (provider or "").strip().lower()
    action = (action or "").strip().lower()
    parameters = parameters or {}
    if action in {"templates", "template_catalog", "schemas"}:
        result = {"ok": True, "provider": provider or "all", "action": action, "templates": api_bridge_templates()}
    elif action in {"self_test", "test_templates", "template_self_test"}:
        result = api_bridge_self_test()
    elif action in {"pending_actions", "prepared_actions", "acciones_pendientes"}:
        result = {
            "ok": True,
            "provider": "all",
            "action": "pending_actions",
            "actions": pending_prepared_actions(session_id=session_id),
        }
    elif action in {"security_status", "auth_status", "authorization_status"}:
        result = {"ok": True, "provider": "all", "action": action, "security": security_status(session_id=session_id)}
    elif action in {"confirm_prepared", "execute_prepared", "confirm_last", "confirm_action", "confirmar_accion"}:
        security = ensure_api_security(provider, action, parameters, confirm=True, session_id=session_id, transcript=transcript)
        if not security.get("authorized"):
            result = {
                "ok": False,
                "provider": provider or "all",
                "action": action,
                "requires_security_phrase": True,
                "security": security,
                "message": "Accion sensible bloqueada. Di la frase de autorizacion o escribe el PIN y vuelve a confirmar.",
            }
            record = record_api_bridge_action(provider or result.get("provider"), action or result.get("action"), parameters, result, session_id, transcript)
            result["action_log"] = record
            return result
        result = execute_prepared_action(
            action_id=str(first_value(parameters, "prepared_action_id", "action_id", "id") or "").strip(),
            session_id=session_id,
            transcript=transcript,
        )
    elif (action in {"status_all", "bridge_status"} or provider == "status" or (provider in {"", "all"} and action == "status") or (provider == "all" and not action)):
        result = {"ok": True, "provider": "all", "action": "status", "status": api_bridge_config_status(live=True)}
    elif provider == "clickup":
        security = ensure_api_security(provider, action, parameters, confirm=confirm, session_id=session_id, transcript=transcript)
        if not security.get("authorized"):
            result = {
                "ok": False,
                "provider": provider,
                "action": action,
                "requires_security_phrase": True,
                "security": security,
                "message": "Accion sensible bloqueada. Di la frase de autorizacion o escribe el PIN y vuelve a confirmar.",
            }
            record = record_api_bridge_action(provider or result.get("provider"), action or result.get("action"), parameters, result, session_id, transcript)
            result["action_log"] = record
            return result
        result = run_clickup_bridge(action, parameters, confirm=confirm)
    elif provider == "notion":
        security = ensure_api_security(provider, action, parameters, confirm=confirm, session_id=session_id, transcript=transcript)
        if not security.get("authorized"):
            result = {
                "ok": False,
                "provider": provider,
                "action": action,
                "requires_security_phrase": True,
                "security": security,
                "message": "Accion sensible bloqueada. Di la frase de autorizacion o escribe el PIN y vuelve a confirmar.",
            }
            record = record_api_bridge_action(provider or result.get("provider"), action or result.get("action"), parameters, result, session_id, transcript)
            result["action_log"] = record
            return result
        result = run_notion_bridge(action, parameters, confirm=confirm)
    elif provider in {"hostinger", "hostinger_mail", "tesca_mail", "business_mail", "imap", "smtp"}:
        security = ensure_api_security(provider, action, parameters, confirm=confirm, session_id=session_id, transcript=transcript)
        if not security.get("authorized"):
            result = {
                "ok": False,
                "provider": provider,
                "action": action,
                "requires_security_phrase": True,
                "security": security,
                "message": "Accion sensible bloqueada. Di la frase de autorizacion o escribe el PIN y vuelve a confirmar.",
            }
            record = record_api_bridge_action(provider or result.get("provider"), action or result.get("action"), parameters, result, session_id, transcript)
            result["action_log"] = record
            return result
        result = run_hostinger_mail_bridge(action, parameters, confirm=confirm)
    elif provider in {"email", "mail", "correo"} and hostinger_mail_configured():
        security = ensure_api_security(provider, action, parameters, confirm=confirm, session_id=session_id, transcript=transcript)
        if not security.get("authorized"):
            result = {
                "ok": False,
                "provider": provider,
                "action": action,
                "requires_security_phrase": True,
                "security": security,
                "message": "Accion sensible bloqueada. Di la frase de autorizacion o escribe el PIN y vuelve a confirmar.",
            }
            record = record_api_bridge_action(provider or result.get("provider"), action or result.get("action"), parameters, result, session_id, transcript)
            result["action_log"] = record
            return result
        result = run_hostinger_mail_bridge(action, parameters, confirm=confirm)
    elif provider in {"gmail", "google_mail"}:
        result = run_gmail_bridge(action, parameters, confirm=confirm)
    elif provider in {"pipedrive", "pipe_drive", "pd"}:
        security = ensure_api_security(provider, action, parameters, confirm=confirm, session_id=session_id, transcript=transcript)
        if not security.get("authorized"):
            result = {
                "ok": False,
                "provider": provider,
                "action": action,
                "requires_security_phrase": True,
                "security": security,
                "message": "Accion sensible bloqueada. Di la frase de autorizacion o escribe el PIN y vuelve a confirmar.",
            }
            record = record_api_bridge_action(provider or result.get("provider"), action or result.get("action"), parameters, result, session_id, transcript)
            result["action_log"] = record
            return result
        result = run_pipedrive_bridge(action, parameters, confirm=confirm)
    elif provider in {"crm", "bifrost_crm", "clients", "clientes", "contacts", "contactos"}:
        security = ensure_api_security(provider, action, parameters, confirm=confirm, session_id=session_id, transcript=transcript)
        if not security.get("authorized"):
            result = {
                "ok": False,
                "provider": provider,
                "action": action,
                "requires_security_phrase": True,
                "security": security,
                "message": "Accion sensible bloqueada. Di la frase de autorizacion o escribe el PIN y vuelve a confirmar.",
            }
            record = record_api_bridge_action(provider or result.get("provider"), action or result.get("action"), parameters, result, session_id, transcript)
            result["action_log"] = record
            return result
        result = run_crm_bridge(action, parameters, confirm=confirm)
    elif provider in {"twilio", "sms", "phone", "telefono", "whatsapp"}:
        if action in {"call_phone", "call", "make_call", "llamar", "llamada", "schedule_call", "programar_llamada", "agendar_llamada"} and transcript:
            parameters = dict(parameters or {})
            parameters.setdefault("_conversation_transcript", transcript)
        security = ensure_api_security(provider, action, parameters, confirm=confirm, session_id=session_id, transcript=transcript)
        if not security.get("authorized"):
            result = {
                "ok": False,
                "provider": provider,
                "action": action,
                "requires_security_phrase": True,
                "security": security,
                "message": "Accion sensible bloqueada. Di la frase de autorizacion o escribe el PIN y vuelve a confirmar.",
            }
            record = record_api_bridge_action(provider or result.get("provider"), action or result.get("action"), parameters, result, session_id, transcript)
            result["action_log"] = record
            return result
        result = run_twilio_bridge(action, parameters, confirm=confirm)
    elif provider in {"all", "auto", "kim", "agent"}:
        target_provider, target_action, target_parameters = agent_action_defaults(action, parameters)
        if not target_provider:
            raise ValueError("No pude inferir proveedor para esta accion. Usa send_email, create_task, update_task, comment_task, create_page, call_phone, schedule_call, schedule_sms, save_contact o pipedrive.")
        result = run_api_bridge(
            target_provider,
            target_action,
            target_parameters,
            confirm=confirm,
            session_id=session_id,
            transcript=transcript,
        )
        result["agent_routing"] = {"from_provider": provider, "from_action": action, "to_provider": target_provider, "to_action": target_action}
        return result
    else:
        raise ValueError("Proveedor no soportado. Usa clickup, notion, pipedrive, gmail, hostinger_mail, twilio, crm o all/status.")
    if isinstance(result, dict) and result.get("requires_confirmation") and result.get("confirm_payload"):
        prepared = store_prepared_action(result, session_id=session_id, transcript=transcript)
        if prepared:
            result["prepared_action_id"] = prepared["id"]
            result["prepared_action_status"] = prepared["status"]
    record = record_api_bridge_action(provider or result.get("provider"), action or result.get("action"), parameters, result, session_id, transcript)
    result["action_log"] = record
    return result


def copy_tree_files(src, dst):
    if not src.exists():
        return {"copied": [], "failed": []}
    copied = []
    failed = []
    for path in src.rglob("*"):
        target = dst / path.relative_to(src)
        if path.is_dir():
            try:
                target.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                failed.append({"path": str(target), "error": brief(str(exc), 180)})
        else:
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
                copied.append(str(target))
            except OSError as exc:
                failed.append({"path": str(target), "error": brief(str(exc), 180)})
    return {"copied": copied, "failed": failed}


def configure_portfolio_module(module):
    runtime_root = RUNTIME_MEMORY_ROOT / "portfolios"
    bifrost_root = MEMORY_ROOT / "portfolios"
    runtime_db = runtime_root / "portfolio_ledger.sqlite"
    bifrost_db = bifrost_root / "portfolio_ledger.sqlite"
    if bifrost_db.exists() and (
        not runtime_db.exists() or bifrost_db.stat().st_mtime > runtime_db.stat().st_mtime
    ):
        copy_tree_files(bifrost_root, runtime_root)
    module.ROOT = runtime_root
    module.DB_PATH = runtime_db
    module.CLIENT_PATH = (
        runtime_root
        / "ignis_stock_financials"
        / "clientes"
        / "manejo_de_portafolios"
        / "sr_eli_2026"
    )
    module.AUDIT_DIR = runtime_root / "audit"
    return runtime_root, bifrost_root


def sync_portfolio_runtime_to_bifrost(runtime_root, bifrost_root):
    sync = copy_tree_files(runtime_root, bifrost_root)
    return {
        "runtime_root": str(runtime_root),
        "bifrost_root": str(bifrost_root),
        "copied_files": len(sync["copied"]),
        "failed_files": sync["failed"][:5],
    }


def portfolio_cli(action, parameters=None):
    action = (action or "status").strip().lower()
    parameters = parameters or {}
    mutating_action = action in {
        "init",
        "record_consultation",
        "record_market_consultation",
        "record_final_change",
        "add_transaction",
        "cancel_transaction",
        "replace_draft_order",
        "set_position",
    }
    spec = importlib.util.spec_from_file_location("kim_portfolio_db", PORTFOLIO_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    runtime_root, bifrost_root = configure_portfolio_module(module)

    def ns(**values):
        return type("PortfolioArgs", (), values)()

    if action == "status":
        try:
            result = module.status_json()
        except Exception as exc:
            if "no such table" not in str(exc).lower():
                raise
            result = module.init_db()
    elif action == "summary":
        result = module.portfolio_summary_json()
    elif action == "init":
        result = module.init_db()
    elif action in {"record_consultation", "record_market_consultation"}:
        snapshot = parameters.get("snapshot_json")
        if isinstance(snapshot, (dict, list)):
            snapshot = json.dumps(snapshot, ensure_ascii=False)
        result = module.record_consultation(
            ns(
                portfolio_id=parameters.get("portfolio_id") or module.DEFAULT_PORTFOLIO_ID,
                consulted_at=parameters.get("consulted_at"),
                symbol=parameters.get("symbol"),
                interval=parameters.get("interval"),
                question=parameters.get("question"),
                snapshot_json=snapshot,
                analysis=parameters.get("analysis"),
                decision=parameters.get("decision"),
                is_final=bool(parameters.get("is_final")),
                source_call_id=parameters.get("source_call_id"),
            )
        )
    elif action == "record_final_change":
        if not parameters.get("summary"):
            raise ValueError("Falta summary para registrar un cambio final.")
        result = module.record_final_change(
            ns(
                portfolio_id=parameters.get("portfolio_id") or module.DEFAULT_PORTFOLIO_ID,
                decided_at=parameters.get("decided_at"),
                change_type=parameters.get("change_type") or "rebalance",
                summary=parameters.get("summary"),
                rationale=parameters.get("rationale"),
                related_consultation_id=parameters.get("related_consultation_id"),
                executed=bool(parameters.get("executed")),
                execution_ref=parameters.get("execution_ref"),
            )
        )
    elif action == "add_transaction":
        if not parameters.get("symbol") or not parameters.get("side"):
            raise ValueError("Faltan symbol y side para registrar transaccion.")
        gross_amount = parameters.get("gross_amount")
        if gross_amount in (None, ""):
            gross_amount = parameters.get("amount") or parameters.get("usd_amount")
        result = module.add_transaction(
            ns(
                portfolio_id=parameters.get("portfolio_id") or module.DEFAULT_PORTFOLIO_ID,
                occurred_at=parameters.get("occurred_at"),
                symbol=parameters.get("symbol"),
                side=str(parameters.get("side")).upper(),
                quantity=parameters.get("quantity"),
                price=parameters.get("price"),
                gross_amount=gross_amount,
                fees=parameters.get("fees") or 0,
                currency=parameters.get("currency") or "USD",
                status=parameters.get("status") or "draft",
                source=parameters.get("source") or "kim_live",
                notes=parameters.get("notes"),
            )
        )
    elif action == "cancel_transaction":
        result = module.cancel_transaction(
            ns(
                portfolio_id=parameters.get("portfolio_id") or module.DEFAULT_PORTFOLIO_ID,
                transaction_id=parameters.get("transaction_id") or parameters.get("id"),
                symbol=parameters.get("symbol"),
                status=parameters.get("status") or "draft",
                reason=parameters.get("reason") or parameters.get("notes"),
            )
        )
    elif action == "replace_draft_order":
        gross_amount = parameters.get("gross_amount")
        if gross_amount in (None, ""):
            gross_amount = parameters.get("amount") or parameters.get("usd_amount")
        result = module.replace_draft_order(
            ns(
                portfolio_id=parameters.get("portfolio_id") or module.DEFAULT_PORTFOLIO_ID,
                old_symbol=parameters.get("old_symbol") or parameters.get("cancel_symbol"),
                old_transaction_id=parameters.get("old_transaction_id"),
                new_symbol=parameters.get("new_symbol") or parameters.get("symbol"),
                symbol=parameters.get("symbol"),
                occurred_at=parameters.get("occurred_at"),
                decided_at=parameters.get("decided_at"),
                quantity=parameters.get("quantity"),
                price=parameters.get("price"),
                gross_amount=gross_amount,
                fees=parameters.get("fees") or 0,
                currency=parameters.get("currency") or "USD",
                status=parameters.get("status") or "draft",
                source=parameters.get("source") or "kim_live_replace_order",
                notes=parameters.get("notes"),
                summary=parameters.get("summary"),
                rationale=parameters.get("rationale"),
                reason=parameters.get("reason"),
                related_consultation_id=parameters.get("related_consultation_id"),
            )
        )
    elif action == "set_position":
        if not parameters.get("symbol") or parameters.get("quantity") in (None, ""):
            raise ValueError("Faltan symbol y quantity para registrar posicion.")
        result = module.set_position(
            ns(
                portfolio_id=parameters.get("portfolio_id") or module.DEFAULT_PORTFOLIO_ID,
                symbol=parameters.get("symbol"),
                quantity=parameters.get("quantity"),
                average_cost=parameters.get("average_cost"),
                currency=parameters.get("currency") or "USD",
                source=parameters.get("source") or "kim_live",
                notes=parameters.get("notes"),
                updated_at=parameters.get("updated_at"),
            )
        )
    else:
        raise ValueError("Accion de portafolio no soportada.")
    result["sync"] = (
        sync_portfolio_runtime_to_bifrost(runtime_root, bifrost_root)
        if mutating_action
        else {
            "runtime_root": str(runtime_root),
            "bifrost_root": str(bifrost_root),
            "copied_files": 0,
            "failed_files": [],
            "skipped": "read_only_action",
        }
    )
    result["runtime_database"] = str(module.DB_PATH)
    result["bifrost_database"] = str(bifrost_root / "portfolio_ledger.sqlite")
    append_memory("portfolio_action", {"action": action, "result": brief(json.dumps(result, ensure_ascii=False), 1200)})
    append_daily_note(f"Kim portfolio: {action}; ok={result.get('ok')}; db={result.get('database')}")
    return result


MEMORY_DOMAIN_KEYWORDS = {
    "ignis_portfolio": [
        "ignis",
        "sr eli",
        "señor eli",
        "senor eli",
        "eli",
        "portafolio",
        "portfolio",
        "usdt",
        "ftt",
        "xrp",
        "ada",
        "cardano",
        "doge",
        "lunc",
        "pepe",
        "avax",
        "trump",
        "dot",
        "compra",
        "venta",
        "orden",
        "fondeado",
        "credito",
        "crédito",
        "ganancia",
        "perdida",
        "pérdida",
    ],
    "tasks_ops": [
        "tarea",
        "pendiente",
        "clickup",
        "asigna",
        "ejecuta",
        "seguimiento",
        "neorgana",
        "equibio",
        "tesca",
        "forever homes",
    ],
    "crm_clients": [
        "cliente",
        "prospecto",
        "pipedrive",
        "inversionista",
        "follow-up",
        "correo",
        "email",
        "llamada cliente",
    ],
    "remote_voice": [
        "twilio",
        "telefono",
        "teléfono",
        "llamada",
        "celular",
        "url",
        "aws",
        "nube",
        "zoom",
    ],
}


def classify_memory_text(text):
    normalized = (text or "").lower()
    scores = {}
    for domain, keywords in MEMORY_DOMAIN_KEYWORDS.items():
        scores[domain] = sum(1 for keyword in keywords if keyword in normalized)
    ranked = [item for item in sorted(scores.items(), key=lambda item: item[1], reverse=True) if item[1] > 0]
    domain = ranked[0][0] if ranked else "general"
    confidence = min(0.98, 0.35 + (ranked[0][1] * 0.08)) if ranked else 0.35
    sources = {
        "general": [
            str(CONTEXT_MEMORY),
            str(CALL_INDEX),
            str(MEMORY_INBOX),
        ],
        "ignis_portfolio": [
            str(MEMORY_ROOT / "portfolios" / "portfolio_ledger.sqlite"),
            str(RUNTIME_MEMORY_ROOT / "portfolios" / "portfolio_ledger.sqlite"),
            str(MEMORY_ROOT / "portfolios" / "ignis_stock_financials" / "clientes" / "manejo_de_portafolios" / "sr_eli_2026"),
            str(MEMORY_CALLS),
        ],
        "tasks_ops": [
            str(CLICKUP_TASKS_JSON),
            str(CLICKUP_TASKS_MARKDOWN),
            str(API_BRIDGE_LOG),
        ],
        "crm_clients": [
            str(MEMORY_CONTEXT_DIR / "pipedrive_context_latest.json"),
            str(CONTEXT_MEMORY),
        ],
        "remote_voice": [
            str(BIFROST / "docs" / "kim_0033_aws_remote_execution_plan.md"),
            str(CONTEXT_MEMORY),
        ],
    }
    save_policy = {
        "ignis_portfolio": "Guardar en portfolio ledger si hay consulta, orden, posicion, cambio final o snapshot; tambien guardar llamada en calls.",
        "tasks_ops": "Guardar como tarea o contexto operativo; ClickUp es espejo/API cuando funcione.",
        "crm_clients": "Guardar como contexto CRM/PipeDrive y memoria general.",
        "remote_voice": "Guardar como decision/arquitectura de acceso remoto.",
        "general": "Guardar en memoria contextual general.",
    }
    return {
        "domain": domain,
        "confidence": round(confidence, 2),
        "scores": scores,
        "ranked": ranked,
        "sources": sources.get(domain, sources["general"]),
        "save_policy": save_policy.get(domain, save_policy["general"]),
    }


def memory_router(action="classify", text="", session_id="", call_entry=None):
    route = classify_memory_text(text)
    payload = {
        "at": now_iso(),
        "action": action or "classify",
        "session_id": session_id,
        "route": route,
        "call_path": (call_entry or {}).get("path"),
        "text_excerpt": brief(text, 900),
    }
    if route["domain"] == "ignis_portfolio":
        try:
            payload["portfolio"] = portfolio_cli("summary", {})
        except Exception as exc:
            payload["portfolio_error"] = brief(str(exc), 300)
        portfolio_route_log = MEMORY_ROOT / "portfolios" / "ignis_stock_financials" / "clientes" / "manejo_de_portafolios" / "sr_eli_2026" / "conversation_routes.jsonl"
        append_jsonl_any([portfolio_route_log, RUNTIME_MEMORY_ROOT / "portfolios" / "sr_eli_2026_conversation_routes.jsonl"], payload)
    append_jsonl_any([MEMORY_ROUTER_LOG, RUNTIME_MEMORY_ROUTER_LOG], payload)
    return payload


def context_brief(limit=9000):
    parts = [
        "Identidad: Dr. Yehoshua trabaja con Kim como interfaz verbal y Codex como ejecutor.",
        "Arquitectura: BIFROST es el traje local; Notion es memoria/base de conocimiento; ClickUp es ejecucion/proyectos; Telegram notifica; Codex ejecuta.",
        "Objetivo operativo: Kim Live debe conversar con memoria local, consultar contexto, compilar tareas y enviarlas a Codex al cerrar conversacion.",
    ]
    context_text = read_text_tail_any([CONTEXT_MEMORY, RUNTIME_CONTEXT / "kim_context.md"], 2200)
    if context_text:
        parts.append("Memoria contextual:\n" + context_text)
    eval_text = read_text_tail_any([NOTION_CLICKUP_EVAL, RUNTIME_CONTEXT / "notion_vs_clickup_evaluation.md"], 1200)
    if eval_text:
        parts.append("Criterio Notion/ClickUp:\n" + eval_text)
    latest = latest_kim_live_notes(limit=3)
    if latest:
        parts.append(
            "Notas recientes de Kim Live:\n"
            + "\n".join(f"- {item['at']} {item['kind']}: {item['text']}" for item in latest)
        )
    recent_calls = load_call_entries(limit=4)
    if recent_calls:
        parts.append(
            "Conversaciones recientes:\n"
            + "\n".join(
                f"- {item.get('session_id')}: {brief(item.get('summary') or item.get('title'), 240)}"
                for item in recent_calls[-4:]
            )
        )
    recent_uploads = load_upload_entries(limit=4)
    if recent_uploads:
        parts.append(
            "Archivos recientes:\n"
            + "\n".join(
                f"- {item.get('filename')}: {brief(item.get('summary'), 220)}"
                for item in recent_uploads[-4:]
            )
        )
    clickup = clickup_context()
    if clickup.get("available"):
        names = []
        for workspace in clickup.get("workspaces", [])[:4]:
            names.append(workspace.get("name") or "")
        parts.append("ClickUp workspaces detectados: " + ", ".join(name for name in names if name))
    task_names = clickup_task_names_context()
    if task_names:
        parts.append("Memoria de nombres de tareas ClickUp:\n" + task_names)
    api_spec = read_text_tail_any([API_BRIDGE_SPEC, RUNTIME_API_BRIDGE_SPEC], 1600)
    if api_spec:
        parts.append("Kim API bridge:\n" + api_spec)
    parts.append(
        "Kim API templates obligatorios: usa kim_api_bridge action=templates si dudas del formato. "
        "Correo Hostinger usa send_email/reply_email para enviar; ClickUp create_task acepta title/subject/body y resuelve list_id desde space_name/list_name; "
        "Notion create_page acepta subject/title/body y genera title si falta; Twilio latest_call/call_report lee transcripciones guardadas."
    )
    text = "\n\n".join(parts)
    if len(text) > limit:
        return text[:limit].rstrip() + "\n...[contexto truncado]..."
    return text


def load_context_bundle():
    sources = []
    for path in [
        CONTEXT_MEMORY,
        daily_memory_path(),
        OPERATING_MODEL,
        NOTION_CLICKUP_EVAL,
        CLICKUP_INVENTORY,
        CLICKUP_TASKS_JSON,
        CLICKUP_TASKS_MARKDOWN,
        RUNTIME_CLICKUP_TASKS_JSON,
        RUNTIME_CLICKUP_TASKS_MARKDOWN,
        API_BRIDGE_SPEC,
        API_BRIDGE_LOG,
    ]:
        sources.append(
            {
                "path": str(path),
                "exists": path.exists(),
                "updated_at": dt.datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
                if path.exists()
                else None,
            }
        )
    return {
        "ok": True,
        "generated_at": now_iso(),
        "brief": context_brief(),
        "latest_kim_live_notes": latest_kim_live_notes(),
        "clickup": clickup_context(),
        "api_bridge": api_bridge_config_status(live=False),
        "research_sources": load_research_source_cache().get("items", [])[-12:],
        "sources": sources,
    }


def speak(text):
    safe = " ".join((text or "").split())[:500]
    if not safe:
        return
    subprocess.Popen(["say", "-v", "Paulina", safe])


def enqueue_task(text):
    safe = " ".join((text or "").split())
    if not safe:
        raise ValueError("Primero escribe o dicta una instruccion en el cuadro.")
    try:
        completed = subprocess.run(
            [str(TELEGRAM_BRIDGE), "enqueue", f"Kim Live: {safe}", "--notify"],
            text=True,
            capture_output=True,
            timeout=120,
            check=True,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Telegram tardo demasiado en crear la tarea.") from exc
    except subprocess.CalledProcessError as exc:
        detail = brief(exc.stderr or exc.stdout or str(exc))
        raise RuntimeError(f"No pude crear la tarea en Telegram: {detail}") from exc
    return completed.stdout.strip()


def store_openai_key(api_key):
    key = (api_key or "").strip()
    if not key.startswith(("sk-", "sk-proj-")) or len(key) < 40:
        raise ValueError("La API key no parece tener formato valido de OpenAI.")
    subprocess.run(
        [
            "security",
            "add-generic-password",
            "-a",
            KEYCHAIN_ACCOUNT,
            "-s",
            OPENAI_KEYCHAIN_SERVICE,
            "-w",
            key,
            "-U",
        ],
        check=True,
        timeout=60,
    )
    return True


def load_openai_key():
    try:
        completed = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-a",
                KEYCHAIN_ACCOUNT,
                "-s",
                OPENAI_KEYCHAIN_SERVICE,
                "-w",
            ],
            text=True,
            capture_output=True,
            timeout=60,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise ValueError(
            "No encuentro la API key de OpenAI en Keychain. "
            "Abre /setup-openai-key para guardarla."
        ) from ValueError(detail)
    key = completed.stdout.strip()
    if not key:
        raise ValueError("La API key de OpenAI esta vacia en Keychain.")
    return key


def twiml_escape(value):
    return html.escape(str(value or ""), quote=False)


def twiml_response(inner):
    return '<?xml version="1.0" encoding="UTF-8"?><Response>' + inner + "</Response>"


def twilio_public_base(handler):
    proto = handler.headers.get("X-Forwarded-Proto") or "https"
    host = handler.headers.get("X-Forwarded-Host") or handler.headers.get("Host") or "localhost"
    return f"{proto}://{host}"


def twilio_media_ws_url(handler, params=None):
    try:
        configured = TWILIO_MEDIA_WS_URL_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        configured = ""
    if configured:
        return configured
    base = twilio_public_base(handler)
    return base.replace("https://", "wss://").replace("http://", "ws://") + "/twilio/media"


def gmail_oauth_redirect_uri(handler):
    return twilio_public_base(handler).rstrip("/") + "/oauth/google/callback"


def gmail_oauth_start_url(handler):
    if not gmail_oauth_configured():
        raise ValueError("Faltan client_id/client_secret de Gmail en Keychain.")
    state = secrets.token_urlsafe(32)
    redirect_uri = gmail_oauth_redirect_uri(handler)
    write_json_file(GMAIL_OAUTH_STATE_FILE, {"state": state, "redirect_uri": redirect_uri, "created_at": now_iso()})
    params = {
        "client_id": load_keychain_secret(GMAIL_CLIENT_ID_KEYCHAIN_SERVICE),
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": GMAIL_READONLY_SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
        "state": state,
    }
    return GOOGLE_OAUTH_AUTH_URL + "?" + urllib.parse.urlencode(params)


def gmail_oauth_callback(handler, parsed):
    params = urllib.parse.parse_qs(parsed.query)
    if params.get("error"):
        error = html.escape((params.get("error_description") or params.get("error") or ["OAuth cancelado"])[0])
        write_text(
            handler,
            f"<h1>Gmail no autorizado</h1><p>{error}</p>",
            status=400,
            content_type="text/html; charset=utf-8",
        )
        return
    code = (params.get("code") or [""])[0]
    state = (params.get("state") or [""])[0]
    expected, _ = load_json_any([GMAIL_OAUTH_STATE_FILE])
    expected = expected or {}
    if not code or not state or state != expected.get("state"):
        write_text(
            handler,
            "<h1>Gmail OAuth invalido</h1><p>El estado OAuth no coincide. Vuelve a iniciar autorizacion desde Kim Live.</p>",
            status=400,
            content_type="text/html; charset=utf-8",
        )
        return
    redirect_uri = expected.get("redirect_uri") or gmail_oauth_redirect_uri(handler)
    token = gmail_exchange_code(code, redirect_uri)
    has_refresh = bool(token.get("refresh_token")) or gmail_authorized()
    append_memory("gmail_oauth_authorized", {"authorized": has_refresh, "scope": GMAIL_READONLY_SCOPE})
    append_daily_note("KIM-0040 Gmail OAuth autorizado en modo solo lectura.")
    profile = {}
    if has_refresh:
        try:
            profile = gmail_request("/users/me/profile")
        except Exception as exc:
            profile = {"error": brief(str(exc), 220)}
    write_text(
        handler,
        "<h1>Gmail conectado con Kim Live</h1>"
        "<p>Autorizacion completada en modo solo lectura. Ya puedes volver a Kim Live y pedirle a Kim que lea correos.</p>"
        f"<pre>{html.escape(json.dumps(profile, ensure_ascii=False, indent=2))}</pre>",
        content_type="text/html; charset=utf-8",
    )


def phone_session_id(params):
    sid = params.get("CallSid") or params.get("call_sid")
    if sid:
        return re.sub(r"[^A-Za-z0-9_-]+", "-", f"PHONE-{sid}")
    return "PHONE-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def kim_phone_reply(user_text, caller="", called="", session_id=""):
    clean = (user_text or "").strip()
    if not clean:
        return "No alcance a escuchar la instruccion. Repitemela en una frase breve, por favor."
    route = memory_router("classify", clean, session_id=session_id)
    prompt = (
        "Eres Kim Live hablando por telefono con Dr Yehoshua. "
        "Responde en espanol mexicano, con una frase breve y accionable, idealmente menor a 45 palabras. "
        "Si la instruccion requiere trabajo largo, confirma que la guardaras para ejecucion en Kim Live/Codex. "
        "No inventes que ya hiciste acciones externas si solo las estas recibiendo por telefono.\n\n"
        f"Caller: {caller}\nCalled: {called}\nSession: {session_id}\n"
        f"Ruta de memoria detectada: {route.get('route', {}).get('domain')}\n\n"
        f"Usuario dijo:\n{clean}"
    )
    try:
        response, model = openai_response_with_fallback(
            PHONE_REPLY_MODEL_CANDIDATES,
            {"input": prompt, "max_output_tokens": 180},
        )
        reply = output_text_from_response(response)
        if not reply:
            raise RuntimeError("Respuesta vacia.")
    except Exception as exc:
        reply = (
            "Te escuche. Guardo esta instruccion en memoria local y la revisamos en Kim Live. "
            "Hubo un problema generando respuesta inteligente en este momento."
        )
        append_memory("phone_reply_error", {"session_id": session_id, "error": brief(str(exc), 500)})
    append_memory(
        "phone_turn",
        {
            "session_id": session_id,
            "caller": caller,
            "called": called,
            "user_text": clean,
            "reply": reply,
        },
    )
    append_daily_note(f"Kim telefono: {brief(clean, 140)} -> {brief(reply, 180)}")
    return brief(reply, 680)


def append_twilio_call_record(params, user_text="", reply_text=""):
    session_id = phone_session_id(params)
    caller = params.get("From", "")
    called = params.get("To", "")
    call_sid = params.get("CallSid", "")
    started = params.get("Timestamp") or now_iso()
    text = (
        "Canal: Twilio phone call\n"
        f"CallSid: {call_sid}\n"
        f"From: {caller}\n"
        f"To: {called}\n\n"
        "Dr. Yehoshua: "
        + ((user_text or "").strip() or "(sin voz capturada)")
        + "\n"
        "Kim: "
        + ((reply_text or "").strip() or "(sin respuesta todavia)")
    )
    try:
        result = save_call_record(
            {
                "session_id": session_id,
                "text": text,
                "started_at": started,
                "title": f"Twilio phone call {caller or 'unknown'}",
            }
        )
        call_path, _entry = result
        crm_record_interaction(
            "call",
            "inbound" if caller and caller != twilio_default_from_number() else "outbound",
            from_value=caller,
            to_value=called,
            status="transcribed",
            body=user_text,
            external_sid=call_sid,
            transcript_path=str(call_path),
            metadata={"reply": reply_text, "session_id": session_id},
        )
        return result
    except Exception as exc:
        phone_dir = RUNTIME_PHONE_CALLS / today()
        phone_dir.mkdir(parents=True, exist_ok=True)
        path = phone_dir / f"{session_id}.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "at": now_iso(),
                        "session_id": session_id,
                        "call_sid": call_sid,
                        "from": caller,
                        "to": called,
                        "user_text": user_text,
                        "reply": reply_text,
                        "save_error": brief(str(exc), 500),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
        append_memory("twilio_call_record_fallback", {"session_id": session_id, "path": str(path)})
        return path, None


def twilio_voice_twiml(handler, params=None):
    params = dict(params or {})
    query_params = {key: values[-1] for key, values in urllib.parse.parse_qs(urllib.parse.urlparse(handler.path).query).items()}
    params.update({key: value for key, value in query_params.items() if value and key not in params})
    base = twilio_public_base(handler)
    session_id = phone_session_id(params)
    caller = params.get("From", "")
    called = params.get("To", "")
    context_id = params.get("kim_context_id", "")
    call_context = load_twilio_call_context(call_sid=params.get("CallSid", ""), context_id=context_id)
    media_ws = twilio_media_ws_url(handler, params)
    append_memory(
        "phone_call_started",
        {
            "session_id": session_id,
            "caller": caller,
            "called": called,
            "context_id": context_id,
            "has_call_context": bool(call_context),
            "transport": "twilio_media_streams",
            "media_ws_url": media_ws,
        },
    )
    stream_params = (
        f'<Parameter name="callSid" value="{twiml_escape(params.get("CallSid", ""))}" />'
        f'<Parameter name="from" value="{twiml_escape(caller)}" />'
        f'<Parameter name="to" value="{twiml_escape(called)}" />'
        f'<Parameter name="kim_context_id" value="{twiml_escape(context_id)}" />'
    )
    query = urllib.parse.urlencode({"callSid": params.get("CallSid", ""), "from": caller, "to": called, "kim_context_id": context_id})
    separator = "&" if "?" in media_ws else "?"
    stream_url = media_ws + separator + query
    return twiml_response(
        f'<Connect><Stream url="{twiml_escape(stream_url)}">{stream_params}</Stream></Connect>'
    )


def twilio_gather_twiml(handler, params):
    base = twilio_public_base(handler)
    session_id = phone_session_id(params)
    user_text = params.get("SpeechResult", "")
    caller = params.get("From", "")
    called = params.get("To", "")
    reply = kim_phone_reply(user_text, caller=caller, called=called, session_id=session_id)
    append_twilio_call_record(params, user_text=user_text, reply_text=reply)
    action = f"{base}/twilio/gather"
    again = "Puedes decir otra instruccion, o colgar si terminamos."
    return twiml_response(
        f'<Say language="es-MX" voice="Polly.Mia">{twiml_escape(reply)}</Say>'
        f'<Gather input="speech" language="es-MX" speechTimeout="auto" timeout="6" '
        f'action="{twiml_escape(action)}" method="POST">'
        f'<Say language="es-MX" voice="Polly.Mia">{twiml_escape(again)}</Say>'
        "</Gather>"
        '<Say language="es-MX" voice="Polly.Mia">Listo doctor. Corto la llamada y dejo memoria local.</Say>'
    )


def twilio_status_callback(params):
    event = {
        "at": now_iso(),
        "provider": "twilio",
        "kind": "status_callback",
        "call_sid": params.get("CallSid", ""),
        "message_sid": params.get("MessageSid", "") or params.get("SmsSid", ""),
        "from": params.get("From", ""),
        "to": params.get("To", ""),
        "call_status": params.get("CallStatus", ""),
        "message_status": params.get("MessageStatus", "") or params.get("SmsStatus", ""),
        "duration": params.get("CallDuration", ""),
        "error_code": params.get("ErrorCode", ""),
        "error_message": params.get("ErrorMessage", ""),
    }
    append_jsonl_any([TWILIO_CALL_LOG, RUNTIME_TWILIO_CALL_LOG], event)
    append_memory("twilio_status_callback", event)
    if event.get("call_sid"):
        update_twilio_call_context(
            call_sid=event.get("call_sid", ""),
            updates={
                "twilio_status": event.get("call_status", ""),
                "duration": event.get("duration", ""),
                "error_code": event.get("error_code", ""),
                "error_message": event.get("error_message", ""),
            },
        )
        crm_record_interaction(
            "call_status",
            "callback",
            from_value=event.get("from", ""),
            to_value=event.get("to", ""),
            status=event.get("call_status", ""),
            external_sid=event.get("call_sid", ""),
            metadata=event,
        )
    if event.get("message_sid"):
        crm_record_interaction(
            "sms_status",
            "callback",
            from_value=event.get("from", ""),
            to_value=event.get("to", ""),
            status=event.get("message_status", ""),
            external_sid=event.get("message_sid", ""),
            metadata=event,
        )
    return event


def twilio_sms_twiml(params):
    event = {
        "at": now_iso(),
        "provider": "twilio",
        "kind": "inbound_sms",
        "message_sid": params.get("MessageSid", "") or params.get("SmsSid", ""),
        "from": params.get("From", ""),
        "to": params.get("To", ""),
        "body": params.get("Body", ""),
        "num_media": params.get("NumMedia", ""),
    }
    append_jsonl_any([TWILIO_SMS_LOG, RUNTIME_TWILIO_SMS_LOG], event)
    append_memory("twilio_inbound_sms", event)
    crm_record_interaction(
        "sms",
        "inbound",
        from_value=event.get("from", ""),
        to_value=event.get("to", ""),
        status="received",
        body=event.get("body", ""),
        external_sid=event.get("message_sid", ""),
        metadata=event,
    )
    return twiml_response("")


def realtime_session_config():
    local_context = context_brief()
    return {
        "session": {
            "type": "realtime",
            "model": REALTIME_MODEL,
            "instructions": (
                "Eres Kim, asistente personal de Dr Yehoshua. "
                "Habla siempre en femenino, en espanol mexicano, con tono calido, directo y util. "
                "Responde breve en conversacion viva. Si el doctor te dicta una "
                "tarea, confirma la accion y sugiere guardarla o ejecutarla desde Kim Live. "
                "Si necesitas datos actuales, investigacion externa o verificacion en internet, "
                "di brevemente que vas a buscar y llama la herramienta kim_research_web. "
                "Cuando uses investigacion web, conserva fuentes para anexarlas al reporte de llamada. "
                "Para reportes del Sr. Eli o cualquier reporte a cliente, NO uses precios recordados, "
                "precios de reportes anteriores ni cierres historicos como si fueran actuales. Antes de "
                "redactar cifras de precio actual llama kim_market_snapshot y solo usa current_price si "
                "current_price_validation.approved_for_client_report=true. Si no hay al menos dos fuentes "
                "frescas en rango, di que el precio no quedo validado y pide verificacion manual. "
                "Si el doctor pide redactar una carta, propuesta, reporte o documento, llama "
                "kim_draft_document. Cuando el doctor suba archivos, usa los resumenes que aparecen "
                "en la conversacion activa como contexto. "
                "No digas que ves la camara, la pantalla o el iframe de TradingView si no recibiste "
                "una imagen o datos. Para mercado o grafica activa, usa kim_market_snapshot con EMAs "
                "personalizadas cuando el doctor las pida, incluyendo EMA34 por temporalidad, y analiza "
                "con esos datos cuantitativos; si hace falta lectura visual de velas, pide captura. "
                "Para ClickUp, Notion, Pipedrive o correo, usa kim_api_bridge. Si dudas del formato, llama action=templates; "
                "para probar plantillas sin escribir ni enviar, llama action=self_test. "
                "y usa el template exacto. Si faltan IDs de ClickUp, primero lista spaces/folders/lists o pasa "
                "space_name/list_name; el bridge puede resolver list_id o preparar crear una lista con confirmacion. "
                "Si el doctor te pide actuar de forma directa, puedes usar provider=all con action send_email, "
                "create_task, update_task, comment_task, create_page, mark_spam, move_to_trash o archive_email; "
                "el servidor enruta a la API correcta. "
                "No digas que falta subject/title/list_id sin haber llamado la herramienta: el bridge genera "
                "subjects/titles por defecto y crea/prepara Kim Inbox cuando falta lista. "
                "Puedes preparar folders/lists/tareas de ClickUp "
                "y paginas de Notion; toda escritura requiere confirm=false, confirmacion explicita del "
                "doctor y luego confirm=true o confirm_prepared usando prepared_action_id. Desde Kim Live 1.5.11, "
                "si la confirmacion devuelve requires_security_phrase, pide la frase o PIN del doctor y vuelve a confirmar. "
                "Para correo institucional Hostinger, usa kim_api_bridge "
                "con provider hostinger_mail: status, list_messages, search_messages, get_message, draft_email, "
                "draft_reply, send_email, reply_email, switch_mailbox, list_folders, mark_spam, move_to_trash o archive_email. "
                "Si el doctor dice mandar, enviar, responder o confirmar envio, "
                "usa send_email/reply_email; usa draft_email solo cuando pida explicitamente un borrador. "
                "Todo correo Hostinger se firma automaticamente como Kim Yan, Augmented Intelligence Assistant, created by Dr. Yehoshua; "
                "si el doctor pide una firma distinta, pasa parameters.signature; si pide omitirla, pasa no_signature=true. "
                "Puede mandar desde founder@aipeople.io, founder@aipeople.work, business@tescaelements.com o "
                "ceo@tescaelements.com; si el doctor dice founder, aipeople, business, ceo o tesca, pasa ese alias "
                "en parameters.mailbox o parameters.from. Si el doctor pide cambiar de buzon, usa switch_mailbox y luego conserva "
                "selected_mailbox en las siguientes acciones. "
                "Para correo basura, primero identifica el UID con list_messages/search_messages y prepara mark_spam "
                "o move_to_trash; no borres permanentemente. "
                "Para llamadas, SMS y WhatsApp usa provider twilio: status, list_numbers, send_sms, send_whatsapp, "
                "call_phone, call_report, latest_call, schedule_call o schedule_sms. SMS/WhatsApp/llamadas siempre se preparan con confirm=false "
                "y requieren confirmacion explicita antes de ejecutar. Si llamas a una tercera persona, no basta con to: "
                "debes pasar contact_name, relationship, call_context, objective, questions/report_to_doctor y cualquier mensaje "
                "que el doctor quiera transmitir; ese contexto se inyecta al prompt telefonico. "
                "Si el doctor pregunta que paso en una llamada o pide resumen/transcripcion, llama provider=twilio action=latest_call "
                "o action=call_report con phone/call_sid/context_id antes de responder. "
                "para clientes/contactos usa provider crm: status, list_contacts, upsert_contact o record_note. "
                "Antes de llamar o escribir a un cliente, consulta CRM si tienes duda y guarda contactos relevantes en BIFROST/CRM. "
                "si Twilio responde 401, pide Auth Token correcto o API Key SID que empieza con SK. "
                "Si falta subject/title/name, usa un subject claro segun la conversacion. Enviar correo siempre requiere confirm=false, "
                "confirmacion explicita del doctor y luego confirm_prepared o confirm=true. Para Gmail, usa provider gmail en modo "
                "solo lectura: status, profile, list_messages o get_message. Si falta autorizacion OAuth, "
                "entrega el link de autorizacion y no inventes correos. "
                "Para portafolios de Ignis Stock Financials, usa kim_portfolio_record. Guarda consultas "
                "como record_consultation; solo registra record_final_change o add_transaction cuando el "
                "doctor diga que es cambio final, operacion final, compra final, venta final o equivalente. "
                "Para cancelar o sustituir una orden pendiente, usa replace_draft_order o cancel_transaction; "
                "no intentes simular una cancelacion creando varias notas sueltas. "
                "Para preguntas de memoria o contexto, usa kim_memory_router para decidir si debes consultar "
                "portafolio, tareas, clientes/CRM, voz remota o memoria general. No intentes cargar todo BIFROST. "
                "Para seguimiento comercial en Pipedrive, usa provider=pipedrive: search_persons/list_persons antes de decir que no existe un contacto; "
                "upsert_person, create_deal, create_activity y create_note requieren confirm=false y luego confirm_prepared. "
                "Cuando una API responda, reporta si confirmo, que cambio y donde quedo guardado. "
                "Usa la memoria local siguiente como contexto de trabajo; si falta algo, dilo "
                "con claridad y propon que Codex lo consulte o actualice.\n\n"
                f"MEMORIA LOCAL BIFROST:\n{local_context}"
            ),
            "tools": [
                {
                    "type": "function",
                    "name": "kim_research_web",
                    "description": "Investiga en internet con OpenAI web_search, guarda fuentes en BIFROST y devuelve una respuesta con fuentes.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Pregunta exacta o tema que Kim debe investigar.",
                            }
                        },
                        "required": ["query"],
                    },
                },
                {
                    "type": "function",
                    "name": "kim_draft_document",
                    "description": "Redacta un documento profesional en Markdown usando la conversacion activa como contexto.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "instruction": {
                                "type": "string",
                                "description": "Tipo de documento y objetivo de redaccion.",
                            }
                        },
                        "required": ["instruction"],
                    },
                },
                {
                    "type": "function",
                    "name": "kim_api_bridge",
                    "description": (
                        "Lee o modifica ClickUp/Notion/Pipedrive, lee Gmail, maneja correo Hostinger, CRM local, prepara Twilio llamadas/SMS/WhatsApp y consulta reportes/transcripciones de llamadas desde Kim Live. Las operaciones de escritura "
                        "requieren confirmacion explicita del doctor y confirm=true."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "provider": {
                                "type": "string",
                                "description": "Proveedor: clickup, notion, pipedrive, gmail, hostinger_mail, twilio, crm o all.",
                            },
                            "action": {
                                "type": "string",
                                "description": (
                                    "Accion. ClickUp: status, inventory, list_spaces, list_folders, "
                                    "list_lists, list_tasks, get_task, create_folder, create_list, "
                                    "create_task, update_task, comment_task. Notion: status, search, "
                                    "get_page, create_page, update_page_properties. Templates: templates, self_test. Gmail: status, auth_url, "
                                    "profile, list_messages, get_message. Hostinger Mail: status, list_mailboxes, "
                                    "list_folders, list_messages, search_messages, get_message, draft_email, draft_reply, "
                                    "send_email, reply_email, move_message, mark_spam, move_to_trash, archive_message. "
                                    "Pipedrive: status, search_persons, list_persons, get_person, upsert_person, list_deals, create_deal, update_deal, create_activity, create_note. "
                                    "Twilio: status, list_numbers, send_sms, send_whatsapp, call_phone, call_report, latest_call, schedule_call, schedule_sms. "
                                    "CRM: status, list_contacts, upsert_contact, record_note."
                                ),
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Parametros concretos de la accion.",
                            },
                            "confirm": {
                                "type": "boolean",
                                "description": "true solo despues de confirmacion explicita del doctor.",
                            },
                        },
                        "required": ["provider", "action"],
                    },
                },
                {
                    "type": "function",
                    "name": "kim_market_snapshot",
                    "description": "Obtiene datos OHLCV, precio actual validado por multiples fuentes e indicadores cuantitativos del mercado activo para reportes y analisis.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Simbolo TradingView/Binance, por ejemplo BINANCE:BTCUSDT.",
                            },
                            "interval": {
                                "type": "string",
                                "description": "Temporalidad: 15, 60, 240, D o W.",
                            },
                            "ema_periods": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Periodos EMA a calcular, por ejemplo [20,34,50].",
                            },
                            "providers": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Fuentes de precio a comparar: binance, coinmarketcap, coingecko.",
                            },
                        },
                    },
                },
                {
                    "type": "function",
                    "name": "kim_portfolio_record",
                    "description": "Registra o consulta el portafolio Sr. Eli 2026 en BIFROST local.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "status, summary, init, record_consultation, record_final_change, add_transaction, cancel_transaction, replace_draft_order o set_position.",
                            },
                            "parameters": {
                                "type": "object",
                                "description": (
                                    "Campos de la accion. record_consultation acepta symbol, interval, question, "
                                    "snapshot_json, analysis, decision, is_final. record_final_change requiere summary. "
                                    "add_transaction requiere symbol y side. cancel_transaction acepta transaction_id o symbol. "
                                    "replace_draft_order requiere old_symbol, new_symbol, price y gross_amount."
                                ),
                            },
                        },
                        "required": ["action"],
                    },
                },
                {
                    "type": "function",
                    "name": "kim_memory_router",
                    "description": "Clasifica una pregunta o conversacion y devuelve la fuente de memoria correcta para responder o guardar.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "classify o retrieve.",
                            },
                            "text": {
                                "type": "string",
                                "description": "Pregunta, instruccion o resumen de conversacion a clasificar.",
                            },
                        },
                        "required": ["text"],
                    },
                },
            ],
            "tool_choice": "auto",
            "audio": {
                "input": {
                    "noise_reduction": {
                        "type": "near_field",
                    },
                    "transcription": {
                        "model": "gpt-4o-mini-transcribe",
                        "language": "es",
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 650,
                    },
                },
                "output": {
                    "voice": REALTIME_VOICE,
                },
            },
        },
    }


def openai_json(path, payload=None, method="GET"):
    data = None
    headers = {
        "Authorization": f"Bearer {load_openai_key()}",
    }
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        f"{OPENAI_API_BASE}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        message = raw
        try:
            parsed = json.loads(raw)
            message = parsed.get("error", {}).get("message") or raw
        except json.JSONDecodeError:
            pass
        raise RuntimeError(f"OpenAI API error {exc.code}: {message}") from exc
    return json.loads(raw or "{}")


def interval_to_binance(value):
    mapping = {
        "15": "15m",
        "60": "1h",
        "240": "4h",
        "D": "1d",
        "W": "1w",
    }
    return mapping.get(str(value or "D").upper(), "1d")


def ema(values, period):
    if not values:
        return None
    alpha = 2 / (period + 1)
    current = values[0]
    for value in values[1:]:
        current = value * alpha + current * (1 - alpha)
    return current


def rsi(values, period=14):
    if len(values) <= period:
        return None
    gains = []
    losses = []
    for index in range(1, len(values)):
        delta = values[index] - values[index - 1]
        gains.append(max(delta, 0))
        losses.append(abs(min(delta, 0)))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def pct_change(values, periods):
    if len(values) <= periods or values[-periods - 1] == 0:
        return None
    return ((values[-1] / values[-periods - 1]) - 1) * 100


def round_opt(value, digits=2):
    if value is None:
        return None
    return round(float(value), digits)


def price_digits(value):
    if value is None:
        return 4
    magnitude = abs(float(value))
    if magnitude >= 100:
        return 2
    if magnitude >= 1:
        return 4
    if magnitude >= 0.01:
        return 6
    if magnitude >= 0.0001:
        return 8
    return 12


def round_price(value):
    if value is None:
        return None
    return round(float(value), price_digits(value))


def format_price(value):
    if value is None:
        return None
    digits = price_digits(value)
    text = f"{float(value):.{digits}f}"
    return text.rstrip("0").rstrip(".") if "." in text else text


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def epoch_seconds(value):
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = dt.datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.timestamp()
    except ValueError:
        return None


def normalize_crypto_ticker(symbol):
    normalized = (symbol or "BINANCE:BTCUSDT").strip().upper().replace(" ", "")
    if ":" in normalized:
        exchange, ticker = normalized.split(":", 1)
    else:
        exchange, ticker = "BINANCE", normalized
    quote = "USD"
    base = ticker
    for candidate in ["USDT", "USDC", "BUSD", "USD"]:
        if ticker.endswith(candidate) and len(ticker) > len(candidate):
            base = ticker[: -len(candidate)]
            quote = "USD" if candidate in {"USDT", "USDC", "BUSD"} else candidate
            break
    return exchange, ticker, base, quote


def provider_price(name, price, fetched_at=None, updated_at=None, stale_after=MARKET_PRICE_MAX_AGE_SECONDS, extra=None):
    fetched_epoch = epoch_seconds(fetched_at) or utc_now().timestamp()
    updated_epoch = epoch_seconds(updated_at) or fetched_epoch
    age_seconds = max(0, utc_now().timestamp() - updated_epoch)
    return {
        "provider": name,
        "price": float(price),
        "price_display": format_price(price),
        "fetched_at": dt.datetime.fromtimestamp(fetched_epoch, tz=dt.timezone.utc).isoformat(),
        "updated_at": dt.datetime.fromtimestamp(updated_epoch, tz=dt.timezone.utc).isoformat(),
        "age_seconds": round_opt(age_seconds, 1),
        "fresh": age_seconds <= stale_after,
        **(extra or {}),
    }


def fetch_binance_spot_price(ticker):
    payload = api_json_request(
        "https://api.binance.com",
        "/api/v3/ticker/price",
        {},
        params={"symbol": ticker},
        timeout=20,
    )
    price = payload.get("price")
    if price is None:
        raise RuntimeError("Binance no devolvio precio spot.")
    return provider_price("binance_spot", price, extra={"symbol": ticker})


def fetch_coingecko_price(base):
    coin_id = COINGECKO_IDS_BY_SYMBOL.get(base)
    if not coin_id:
        raise RuntimeError(f"No tengo CoinGecko API ID para {base}.")
    payload = api_json_request(
        "https://api.coingecko.com",
        "/api/v3/simple/price",
        {},
        params={
            "ids": coin_id,
            "vs_currencies": "usd",
            "include_last_updated_at": "true",
            "precision": "full",
        },
        timeout=20,
    )
    item = payload.get(coin_id) or {}
    price = item.get("usd")
    if price is None:
        raise RuntimeError(f"CoinGecko no devolvio precio USD para {coin_id}.")
    return provider_price(
        "coingecko",
        price,
        updated_at=item.get("last_updated_at"),
        stale_after=MARKET_PRICE_MAX_AGE_SECONDS,
        extra={"coin_id": coin_id, "symbol": base},
    )


def fetch_coinmarketcap_price(base):
    api_key = load_keychain_secret(COINMARKETCAP_KEYCHAIN_SERVICE, required=False)
    if not api_key:
        raise RuntimeError("Falta API key de CoinMarketCap en Keychain.")
    payload = api_json_request(
        "https://pro-api.coinmarketcap.com",
        "/v3/cryptocurrency/quotes/latest",
        {"X-CMC_PRO_API_KEY": api_key},
        params={"symbol": base, "convert": "USD"},
        timeout=20,
    )
    data = payload.get("data") or {}
    row = {}
    if isinstance(data, list):
        matches = [item for item in data if str(item.get("symbol", "")).upper() == base]
        row = (matches or data or [{}])[0]
    elif isinstance(data, dict):
        rows = data.get(base) or data.get(base.upper())
        if isinstance(rows, list):
            row = rows[0] if rows else {}
        elif isinstance(rows, dict):
            row = rows
        else:
            values = list(data.values())
            row = values[0] if values and isinstance(values[0], dict) else {}
    quote = (row.get("quote") or {}).get("USD") or {}
    price = quote.get("price")
    if price is None:
        raise RuntimeError(f"CoinMarketCap no devolvio precio USD para {base}.")
    return provider_price(
        "coinmarketcap",
        price,
        updated_at=quote.get("last_updated") or row.get("last_updated"),
        stale_after=MARKET_PRICE_MAX_AGE_SECONDS,
        extra={"symbol": base, "cmc_id": row.get("id"), "name": row.get("name")},
    )


def validate_market_prices(symbol, providers=None):
    exchange, ticker, base, quote = normalize_crypto_ticker(symbol)
    requested = providers or ["binance", "coinmarketcap", "coingecko"]
    provider_calls = {
        "binance": lambda: fetch_binance_spot_price(ticker),
        "coinmarketcap": lambda: fetch_coinmarketcap_price(base),
        "coingecko": lambda: fetch_coingecko_price(base),
    }
    prices = []
    failures = []
    for provider in requested:
        key = str(provider or "").strip().lower()
        call = provider_calls.get(key)
        if not call:
            failures.append({"provider": key, "error": "Proveedor no soportado."})
            continue
        try:
            prices.append(call())
        except Exception as exc:
            failures.append({"provider": key, "error": brief(str(exc), 260)})
    fresh_prices = [item for item in prices if item.get("fresh") and item.get("price") is not None]
    values = [float(item["price"]) for item in fresh_prices]
    min_price = min(values) if values else None
    max_price = max(values) if values else None
    reference = sum(values) / len(values) if values else None
    spread_pct = ((max_price - min_price) / reference * 100) if reference and min_price is not None else None
    approved = len(fresh_prices) >= 2 and (spread_pct is not None and spread_pct <= MARKET_PRICE_SPREAD_LIMIT_PCT)
    status = "validated" if approved else "needs_review"
    if len(fresh_prices) < 2:
        status = "insufficient_fresh_sources"
    elif spread_pct is not None and spread_pct > MARKET_PRICE_SPREAD_LIMIT_PCT:
        status = "provider_spread_too_wide"
    validation = {
        "ok": bool(prices),
        "symbol": f"{exchange}:{ticker}",
        "base": base,
        "quote": quote,
        "checked_at": utc_now().isoformat(),
        "max_age_seconds": MARKET_PRICE_MAX_AGE_SECONDS,
        "spread_limit_pct": MARKET_PRICE_SPREAD_LIMIT_PCT,
        "providers": prices,
        "failures": failures,
        "fresh_provider_count": len(fresh_prices),
        "reference_price": round_opt(reference, 12),
        "reference_price_display": format_price(reference),
        "min_price": round_opt(min_price, 12),
        "min_price_display": format_price(min_price),
        "max_price": round_opt(max_price, 12),
        "max_price_display": format_price(max_price),
        "spread_pct": round_opt(spread_pct, 4),
        "status": status,
        "approved_for_client_report": approved,
        "client_report_rule": (
            "Usar este precio en reportes del Sr. Eli solo si approved_for_client_report=true; "
            "si es false, reportar que el precio no quedo validado y pedir verificacion manual."
        ),
    }
    append_jsonl_any([MARKET_PRICE_VALIDATION_LOG, RUNTIME_MARKET_PRICE_VALIDATION_LOG], validation)
    append_memory("market_price_validation", validation)
    return validation


def sanitize_ema_periods(periods):
    if periods is None or periods == "":
        raw = [20, 34, 50]
    elif isinstance(periods, str):
        raw = re.split(r"[,;\s]+", periods.strip())
    elif isinstance(periods, (list, tuple)):
        raw = periods
    else:
        raw = [periods]
    clean = []
    for value in raw:
        try:
            period = int(value)
        except (TypeError, ValueError):
            continue
        if 2 <= period <= 300 and period not in clean:
            clean.append(period)
    for baseline in [20, 34, 50]:
        if baseline not in clean:
            clean.append(baseline)
    return sorted(clean)


def market_snapshot(symbol, interval, ema_periods=None, providers=None):
    exchange, ticker, _base, _quote = normalize_crypto_ticker(symbol)
    if exchange != "BINANCE":
        raise ValueError("Por ahora el snapshot cuantitativo soporta simbolos BINANCE, por ejemplo BINANCE:BTCUSDT.")
    binance_interval = interval_to_binance(interval)
    periods = sanitize_ema_periods(ema_periods)
    limit = min(1000, max(200, max(periods) * 5))
    query = urllib.parse.urlencode({"symbol": ticker, "interval": binance_interval, "limit": limit})
    request = urllib.request.Request(
        f"https://api.binance.com/api/v3/klines?{query}",
        headers={"User-Agent": f"KimLive/{APP_VERSION}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            candles = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Binance error {exc.code}: {brief(raw, 400)}") from exc
    if not isinstance(candles, list) or len(candles) < 30:
        raise RuntimeError("No recibi suficientes velas para analizar el mercado.")
    closes = [float(item[4]) for item in candles]
    highs = [float(item[2]) for item in candles]
    lows = [float(item[3]) for item in candles]
    volumes = [float(item[5]) for item in candles]
    last_close = closes[-1]
    ema_values = {}
    for period in periods:
        lookback = min(len(closes), max(period * 5, period + 20))
        ema_values[period] = ema(closes[-lookback:], period)
    ema20 = ema_values.get(20)
    ema34 = ema_values.get(34)
    ema50 = ema_values.get(50)
    rsi14 = rsi(closes[-80:], 14)
    support20 = min(lows[-20:])
    resistance20 = max(highs[-20:])
    support50 = min(lows[-50:])
    resistance50 = max(highs[-50:])
    avg_volume20 = sum(volumes[-20:]) / 20
    current_volume = volumes[-1]
    trend = "lateral"
    if ema20 and ema50:
        if last_close > ema20 > ema50:
            trend = "alcista"
        elif last_close < ema20 < ema50:
            trend = "bajista"
    validation = validate_market_prices(f"{exchange}:{ticker}", providers=providers)
    snapshot = {
        "symbol": f"{exchange}:{ticker}",
        "interval": interval or "D",
        "provider": "binance_klines",
        "candles": len(candles),
        "last_close": round_price(last_close),
        "last_close_display": format_price(last_close),
        "current_price": validation.get("reference_price"),
        "current_price_display": validation.get("reference_price_display"),
        "current_price_validation": validation,
        "trend": trend,
        "ema_periods": periods,
        "emas": {str(period): round_price(value) for period, value in ema_values.items()},
        "ema_displays": {str(period): format_price(value) for period, value in ema_values.items()},
        "ema20": round_price(ema20),
        "ema34": round_price(ema34),
        "ema50": round_price(ema50),
        "ema20_display": format_price(ema20),
        "ema34_display": format_price(ema34),
        "ema50_display": format_price(ema50),
        "rsi14": round_opt(rsi14, 2),
        "support20": round_price(support20),
        "support20_display": format_price(support20),
        "resistance20": round_price(resistance20),
        "resistance20_display": format_price(resistance20),
        "support50": round_price(support50),
        "support50_display": format_price(support50),
        "resistance50": round_price(resistance50),
        "resistance50_display": format_price(resistance50),
        "change_5": round_opt(pct_change(closes, 5), 2),
        "change_20": round_opt(pct_change(closes, 20), 2),
        "current_volume": round_opt(current_volume, 4),
        "avg_volume20": round_opt(avg_volume20, 4),
        "volume_ratio": round_opt(current_volume / avg_volume20 if avg_volume20 else None, 2),
    }
    snapshot["summary"] = (
        f"{snapshot['symbol']} {snapshot['interval']}: precio validado {snapshot['current_price_display']}, "
        f"cierre vela {snapshot['last_close_display']}, "
        f"tendencia {snapshot['trend']}, EMA34 {snapshot['ema34_display']}, RSI14 {snapshot['rsi14']}, "
        f"soporte 20v {snapshot['support20_display']}, resistencia 20v {snapshot['resistance20_display']}, "
        f"volumen relativo {snapshot['volume_ratio']}x, validacion precio "
        f"{validation.get('status')} con {validation.get('fresh_provider_count')} fuentes frescas."
    )
    append_memory("market_snapshot", snapshot)
    return snapshot


def multipart_field(boundary, name, value, content_type=None):
    header = f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\""
    if content_type:
        header += f"\r\nContent-Type: {content_type}"
    return (header + "\r\n\r\n" + value + "\r\n").encode("utf-8")


def openai_realtime_call(offer_sdp):
    boundary = "----kimrealtime" + hashlib.sha256(f"{len(offer_sdp)}{now_iso()}".encode()).hexdigest()[:24]
    session = json.dumps(realtime_session_config()["session"], ensure_ascii=False)
    data = b"".join(
        [
            multipart_field(boundary, "sdp", offer_sdp, "application/sdp"),
            multipart_field(boundary, "session", session, "application/json"),
            f"--{boundary}--\r\n".encode("utf-8"),
        ]
    )
    request = urllib.request.Request(
        f"{OPENAI_API_BASE}/realtime/calls",
        data=data,
        headers={
            "Authorization": f"Bearer {load_openai_key()}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "OpenAI-Safety-Identifier": "dr-yehoshua-kim-live-local",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        message = raw
        try:
            parsed = json.loads(raw)
            message = parsed.get("error", {}).get("message") or raw
        except json.JSONDecodeError:
            pass
        raise RuntimeError(f"OpenAI Realtime SDP error {exc.code}: {message}") from exc


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            data = (APP_DIR / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if parsed.path == "/setup-openai-key":
            data = (APP_DIR / "setup-openai-key.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if parsed.path == "/oauth/google/start":
            try:
                url = gmail_oauth_start_url(self)
            except Exception as exc:
                write_text(
                    self,
                    f"<h1>No pude iniciar Gmail OAuth</h1><p>{html.escape(str(exc))}</p>",
                    status=500,
                    content_type="text/html; charset=utf-8",
                )
                return
            self.send_response(302)
            self.send_header("Location", url)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        if parsed.path == "/oauth/google/callback":
            gmail_oauth_callback(self, parsed)
            return
        if parsed.path == "/api/status":
            write_json(
                self,
                {
                    "ok": True,
                    "version": APP_VERSION,
                    "mode": "Kim Live + Realtime",
                    "memory_inbox": str(MEMORY_INBOX),
                    "runtime_memory_inbox": str(RUNTIME_MEMORY_INBOX),
                    "telegram_bridge": str(TELEGRAM_BRIDGE),
                    "openai_realtime": True,
                    "realtime_model": REALTIME_MODEL,
                    "realtime_voice": REALTIME_VOICE,
                },
            )
            return
        if parsed.path == "/twilio/voice":
            params = {key: values[-1] for key, values in urllib.parse.parse_qs(parsed.query).items()}
            write_xml(self, twilio_voice_twiml(self, params))
            return
        if parsed.path == "/twilio/status":
            params = {key: values[-1] for key, values in urllib.parse.parse_qs(parsed.query).items()}
            twilio_status_callback(params)
            write_text(self, "", content_type="text/plain; charset=utf-8")
            return
        if parsed.path == "/twilio/health":
            write_json(self, {"ok": True, "service": "kim_twilio", "version": APP_VERSION})
            return
        if parsed.path == "/api/openai-status":
            model = openai_json(f"/models/{REALTIME_MODEL}")
            write_json(
                self,
                {
                    "ok": True,
                    "configured": True,
                    "model": model.get("id", REALTIME_MODEL),
                    "realtime_voice": REALTIME_VOICE,
                },
            )
            return
        if parsed.path == "/api/context":
            write_json(self, load_context_bundle())
            return
        if parsed.path == "/api/api-bridge/status":
            write_json(self, {"ok": True, "status": api_bridge_config_status(live=True)})
            return
        if parsed.path == "/api/gmail/status":
            write_json(self, {"ok": True, "status": gmail_status(live=True)})
            return
        if parsed.path == "/api/conversations":
            entries = list(reversed(load_call_entries(limit=80)))
            write_json(
                self,
                {
                    "ok": True,
                    "conversations": [
                        {
                            "session_id": item.get("session_id"),
                            "title": item.get("title"),
                            "call_number": item.get("call_number"),
                            "started_at": item.get("started_at"),
                            "saved_at": item.get("saved_at"),
                            "summary": item.get("summary"),
                            "topics": item.get("topics", []),
                            "chars": item.get("chars"),
                            "path": item.get("path"),
                        }
                        for item in entries
                    ],
                },
            )
            return
        if parsed.path == "/api/conversation":
            params = urllib.parse.parse_qs(parsed.query)
            session_id = (params.get("session_id") or [""])[0]
            write_json(self, {"ok": True, "conversation": load_conversation(session_id)})
            return
        if parsed.path == "/api/memory-analytics":
            write_json(self, memory_analytics())
            return
        if parsed.path == "/api/realtime-token":
            token = openai_json(
                "/realtime/client_secrets",
                payload=realtime_session_config(),
                method="POST",
            )
            append_memory(
                "realtime_token_minted",
                {"model": REALTIME_MODEL, "voice": REALTIME_VOICE},
            )
            write_json(self, token)
            return
        self.send_error(404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        try:
            if parsed.path == "/twilio/voice":
                params = read_form(self)
                write_xml(self, twilio_voice_twiml(self, params))
                return
            if parsed.path == "/twilio/gather":
                params = read_form(self)
                write_xml(self, twilio_gather_twiml(self, params))
                return
            if parsed.path == "/twilio/status":
                params = read_form(self)
                twilio_status_callback(params)
                write_text(self, "", content_type="text/plain; charset=utf-8")
                return
            if parsed.path == "/twilio/sms":
                params = read_form(self)
                write_xml(self, twilio_sms_twiml(params))
                return
            if parsed.path == "/api/upload-memory-file":
                analysis = parse_upload(self)
                write_json(self, {"ok": True, "analysis": analysis})
                return
            if parsed.path == "/api/realtime-call":
                length = int(self.headers.get("Content-Length", "0") or "0")
                offer_sdp = self.rfile.read(length).decode("utf-8", errors="replace")
                if not offer_sdp.startswith("v=0"):
                    write_text(self, "SDP invalido recibido por Kim Live.", status=400)
                    return
                answer_sdp = openai_realtime_call(offer_sdp)
                append_memory(
                    "realtime_call_started",
                    {"model": REALTIME_MODEL, "voice": REALTIME_VOICE, "transport": "unified"},
                )
                write_text(self, answer_sdp, content_type="application/sdp")
                return
            if parsed.path == "/api/client-log":
                body = read_body(self)
                append_memory(
                    "client_log",
                    {
                        "stage": brief(body.get("stage", ""), 80),
                        "detail": brief(json.dumps(body.get("detail", {}), ensure_ascii=False), 1200),
                    },
                )
                write_json(self, {"ok": True})
                return
            body = read_body(self)
            if parsed.path == "/api/say":
                text = body.get("text", "")
                speak(text)
                append_memory("spoken_reply", {"text": text})
                write_json(self, {"ok": True})
                return
            if parsed.path == "/api/save":
                text = body.get("text", "")
                path = append_memory("conversation_note", {"text": text})
                call_path = None
                call_entry = None
                if body.get("session_id"):
                    call_path, call_entry = save_call_record(body)
                append_daily_note(text)
                write_json(
                    self,
                    {
                        "ok": True,
                        "saved_to": str(path),
                        "call_saved_to": str(call_path) if call_path else None,
                        "call": call_entry,
                    },
                )
                return
            if parsed.path == "/api/execute":
                text = body.get("text", "")
                path = append_memory("execution_request", {"text": text})
                result = enqueue_task(text)
                write_json(self, {"ok": True, "saved_to": str(path), "task": result})
                return
            if parsed.path == "/api/research":
                result = research_web(body.get("query", ""))
                write_json(self, {"ok": True, "research": result})
                return
            if parsed.path == "/api/research-agent":
                result = research_with_openai(
                    body.get("query", ""),
                    body.get("transcript", ""),
                    body.get("session_id", ""),
                )
                write_json(self, {"ok": True, "research": result})
                return
            if parsed.path == "/api/draft-document":
                result = draft_document(
                    body.get("instruction", ""),
                    body.get("text", ""),
                    body.get("session_id", ""),
                )
                write_json(self, {"ok": True, "document": result})
                return
            if parsed.path == "/api/api-bridge":
                result = run_api_bridge(
                    body.get("provider", ""),
                    body.get("action", ""),
                    body.get("parameters") or {},
                    confirm=bool(body.get("confirm", False)),
                    session_id=body.get("session_id", ""),
                    transcript=body.get("transcript", ""),
                )
                write_json(self, {"ok": True, "result": result})
                return
            if parsed.path == "/api/portfolio":
                try:
                    result = portfolio_cli(body.get("action", "status"), body.get("parameters") or {})
                except Exception as exc:
                    result = {
                        "ok": False,
                        "action": body.get("action", "status"),
                        "error": str(exc),
                        "message": "No pude guardar en portafolio; revisa campos requeridos y usa replace_draft_order para sustituciones.",
                    }
                    append_memory("portfolio_error", result)
                write_json(self, {"ok": True, "result": result})
                return
            if parsed.path == "/api/memory-router":
                result = memory_router(
                    body.get("action", "classify"),
                    body.get("text", ""),
                    session_id=body.get("session_id", ""),
                )
                write_json(self, {"ok": True, "result": result})
                return
            if parsed.path == "/api/market-snapshot":
                snapshot = market_snapshot(
                    body.get("symbol", ""),
                    body.get("interval", "D"),
                    body.get("ema_periods"),
                    providers=body.get("providers"),
                )
                write_json(self, {"ok": True, "snapshot": snapshot})
                return
            if parsed.path == "/api/store-openai-key":
                store_openai_key(body.get("api_key", ""))
                append_memory("credential_update", {"service": OPENAI_KEYCHAIN_SERVICE})
                write_json(self, {"ok": True, "service": OPENAI_KEYCHAIN_SERVICE})
                return
            self.send_error(404)
        except Exception as exc:
            write_json(self, {"ok": False, "error": str(exc)}, status=500)

    def log_message(self, fmt, *args):
        stamp = now_iso()
        print(f"{stamp} {self.address_string()} {fmt % args}", flush=True)


def main():
    MEMORY_INBOX.mkdir(parents=True, exist_ok=True)
    start_scheduler_once()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Kim Live running at http://{HOST}:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
