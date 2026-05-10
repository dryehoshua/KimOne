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
import hashlib
import html
import importlib.util
import io
import json
import mimetypes
import pathlib
import re
import shutil
import subprocess
import tempfile
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
CLICKUP_STRUCTURE_JSON = MEMORY_CONTEXT_DIR / "clickup_structure_latest.json"
RUNTIME_CLICKUP_STRUCTURE_JSON = RUNTIME_CONTEXT / "clickup_structure_latest.json"
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
KEYCHAIN_ACCOUNT = "dryehoshuapython"
HOST = "127.0.0.1"
PORT = 8765
OPENAI_API_BASE = "https://api.openai.com/v1"
CLICKUP_API_BASE = "https://api.clickup.com/api/v2"
NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
REALTIME_MODEL = "gpt-realtime"
REALTIME_VOICE = "marin"
PHONE_REPLY_MODEL_CANDIDATES = ["gpt-5.4-mini", "gpt-5.4", "gpt-5"]
APP_VERSION = "1.5.1"
RESEARCH_MODEL_CANDIDATES = ["gpt-5.4-mini", "gpt-5.4", "gpt-5"]
DOCUMENT_MODEL_CANDIDATES = ["gpt-5.4-mini", "gpt-5.4", "gpt-5"]
VISION_MODEL_CANDIDATES = ["gpt-5.4-mini", "gpt-5.4", "gpt-5"]
MEMORY_DOCUMENTS = MEMORY_ROOT / "documents"
RUNTIME_DOCUMENTS = RUNTIME_MEMORY_ROOT / "documents"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".heic", ".heif", ".tif", ".tiff", ".bmp"}


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
    return status


def api_json_request(base_url, path, headers, method="GET", payload=None, params=None, timeout=90):
    params = params or {}
    query = urllib.parse.urlencode({key: value for key, value in params.items() if value is not None})
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
    title = str(parameters.get("title") or parameters.get("name") or "").strip()
    if not title:
        raise ValueError("Falta title para crear pagina en Notion.")
    parent_page_id = str(parameters.get("parent_page_id") or "").strip()
    parent_database_id = str(parameters.get("parent_database_id") or parameters.get("database_id") or "").strip()
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
    children = notion_children_from_content(parameters.get("content") or parameters.get("body") or "")
    if children:
        payload["children"] = children
    if parameters.get("icon"):
        payload["icon"] = {"type": "emoji", "emoji": str(parameters.get("icon"))[:2]}
    return payload


def confirmation_preview(provider, action, summary, parameters):
    return {
        "ok": True,
        "requires_confirmation": True,
        "provider": provider,
        "action": action,
        "summary": summary,
        "parameters": parameters,
        "message": "Operacion preparada. Kim debe pedir confirmacion explicita antes de ejecutar con confirm=true.",
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
        name = str(parameters.get("name") or parameters.get("folder_name") or "").strip()
        if not name:
            raise ValueError("Falta name para crear Folder en ClickUp.")
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
        name = str(parameters.get("name") or parameters.get("list_name") or "").strip()
        if not name:
            raise ValueError("Falta name para crear List en ClickUp.")
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
        list_id = str(parameters.get("list_id") or "").strip()
        name = str(parameters.get("name") or "").strip()
        if not list_id or not name:
            raise ValueError("Faltan list_id y name para crear tarea en ClickUp.")
        payload = {"name": name}
        for key in ["description", "status", "priority", "due_date", "due_date_time"]:
            if parameters.get(key) not in (None, ""):
                payload[key] = parameters.get(key)
        if not confirm:
            return confirmation_preview("clickup", action, f"Crear tarea '{name}' en lista {list_id}.", payload)
        task = clickup_request(f"/list/{urllib.parse.quote(list_id)}/task", method="POST", payload=payload)
        return {"ok": True, "provider": "clickup", "action": action, "task": normalize_clickup_task(task), "confirmed": True}
    if action == "update_task":
        task_id = str(parameters.get("task_id") or "").strip()
        fields = dict(parameters.get("fields") or {})
        for key in ["name", "description", "status", "priority", "due_date", "due_date_time"]:
            if parameters.get(key) not in (None, ""):
                fields[key] = parameters.get(key)
        if not task_id or not fields:
            raise ValueError("Faltan task_id y fields para actualizar tarea en ClickUp.")
        if not confirm:
            return confirmation_preview("clickup", action, f"Actualizar tarea {task_id}.", {"task_id": task_id, "fields": fields})
        task = clickup_request(f"/task/{urllib.parse.quote(task_id)}", method="PUT", payload=fields)
        return {"ok": True, "provider": "clickup", "action": action, "task": normalize_clickup_task(task), "confirmed": True}
    if action == "comment_task":
        task_id = str(parameters.get("task_id") or "").strip()
        comment_text = str(parameters.get("comment_text") or parameters.get("text") or "").strip()
        if not task_id or not comment_text:
            raise ValueError("Faltan task_id y comment_text para comentar tarea en ClickUp.")
        payload = {"comment_text": comment_text}
        if not confirm:
            return confirmation_preview("clickup", action, f"Comentar tarea {task_id}.", {"task_id": task_id, "comment_text": comment_text})
        comment = clickup_request(f"/task/{urllib.parse.quote(task_id)}/comment", method="POST", payload=payload)
        return {"ok": True, "provider": "clickup", "action": action, "comment": comment, "confirmed": True}
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
        title = str(parameters.get("title") or parameters.get("name") or "").strip()
        parent = payload.get("parent", {})
        if not confirm:
            return confirmation_preview(
                "notion",
                action,
                f"Crear pagina '{title}' bajo {parent.get('type')} {parent.get(parent.get('type'), '')}.",
                payload,
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


def record_api_bridge_action(provider, action, parameters, result, session_id="", transcript=""):
    event = {
        "at": now_iso(),
        "session_id": session_id,
        "provider": provider,
        "action": action,
        "confirmed": bool(result.get("confirmed")) if isinstance(result, dict) else False,
        "requires_confirmation": bool(result.get("requires_confirmation")) if isinstance(result, dict) else False,
        "ok": bool(result.get("ok")) if isinstance(result, dict) else False,
        "parameters": parameters,
        "result_summary": brief(json.dumps(result, ensure_ascii=False), 900),
        "transcript_excerpt": brief(transcript, 900),
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
    if provider in {"status", "all"} or action in {"status_all", "bridge_status"}:
        result = {"ok": True, "provider": "all", "action": "status", "status": api_bridge_config_status(live=True)}
    elif provider == "clickup":
        result = run_clickup_bridge(action, parameters, confirm=confirm)
    elif provider == "notion":
        result = run_notion_bridge(action, parameters, confirm=confirm)
    else:
        raise ValueError("Proveedor no soportado. Usa clickup, notion o all/status.")
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
        result = module.add_transaction(
            ns(
                portfolio_id=parameters.get("portfolio_id") or module.DEFAULT_PORTFOLIO_ID,
                occurred_at=parameters.get("occurred_at"),
                symbol=parameters.get("symbol"),
                side=str(parameters.get("side")).upper(),
                quantity=parameters.get("quantity"),
                price=parameters.get("price"),
                gross_amount=parameters.get("gross_amount"),
                fees=parameters.get("fees") or 0,
                currency=parameters.get("currency") or "USD",
                status=parameters.get("status") or "draft",
                source=parameters.get("source") or "kim_live",
                notes=parameters.get("notes"),
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
        return save_call_record(
            {
                "session_id": session_id,
                "text": text,
                "started_at": started,
                "title": f"Twilio phone call {caller or 'unknown'}",
            }
        )
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
    params = params or {}
    base = twilio_public_base(handler)
    session_id = phone_session_id(params)
    caller = params.get("From", "")
    called = params.get("To", "")
    media_ws = twilio_media_ws_url(handler, params)
    append_memory(
        "phone_call_started",
        {
            "session_id": session_id,
            "caller": caller,
            "called": called,
            "transport": "twilio_media_streams",
            "media_ws_url": media_ws,
        },
    )
    query = urllib.parse.urlencode({"callSid": params.get("CallSid", ""), "from": caller, "to": called})
    separator = "&" if "?" in media_ws else "?"
    stream_url = media_ws + separator + query
    return twiml_response(
        f'<Connect><Stream url="{twiml_escape(stream_url)}" /></Connect>'
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
                "Si el doctor pide redactar una carta, propuesta, reporte o documento, llama "
                "kim_draft_document. Cuando el doctor suba archivos, usa los resumenes que aparecen "
                "en la conversacion activa como contexto. "
                "No digas que ves la camara, la pantalla o el iframe de TradingView si no recibiste "
                "una imagen o datos. Para mercado o grafica activa, usa kim_market_snapshot con EMAs "
                "personalizadas cuando el doctor las pida, incluyendo EMA34 por temporalidad, y analiza "
                "con esos datos cuantitativos; si hace falta lectura visual de velas, pide captura. "
                "Para ClickUp o Notion, usa kim_api_bridge: si faltan IDs de ClickUp, primero lista "
                "spaces, folders o lists antes de crear. Puedes preparar folders/lists/tareas de ClickUp "
                "y paginas de Notion; toda escritura requiere confirm=false, confirmacion explicita del "
                "doctor y luego confirm=true. "
                "Para portafolios de Ignis Stock Financials, usa kim_portfolio_record. Guarda consultas "
                "como record_consultation; solo registra record_final_change o add_transaction cuando el "
                "doctor diga que es cambio final, operacion final, compra final, venta final o equivalente. "
                "Para preguntas de memoria o contexto, usa kim_memory_router para decidir si debes consultar "
                "portafolio, tareas, clientes/CRM, voz remota o memoria general. No intentes cargar todo BIFROST. "
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
                        "Lee o modifica ClickUp/Notion desde Kim Live. Las operaciones de escritura "
                        "requieren confirmacion explicita del doctor y confirm=true."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "provider": {
                                "type": "string",
                                "description": "Proveedor: clickup, notion o all.",
                            },
                            "action": {
                                "type": "string",
                                "description": (
                                    "Accion. ClickUp: status, inventory, list_spaces, list_folders, "
                                    "list_lists, list_tasks, get_task, create_folder, create_list, "
                                    "create_task, update_task, comment_task. Notion: status, search, "
                                    "get_page, create_page, update_page_properties."
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
                    "description": "Obtiene datos OHLCV e indicadores cuantitativos del mercado activo para analizar tendencia, soportes, resistencias, momentum, volumen y riesgo.",
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
                                "description": "status, summary, init, record_consultation, record_final_change, add_transaction o set_position.",
                            },
                            "parameters": {
                                "type": "object",
                                "description": (
                                    "Campos de la accion. record_consultation acepta symbol, interval, question, "
                                    "snapshot_json, analysis, decision, is_final. record_final_change requiere summary. "
                                    "add_transaction requiere symbol y side."
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


def market_snapshot(symbol, interval, ema_periods=None):
    normalized = (symbol or "BINANCE:BTCUSDT").strip().upper().replace(" ", "")
    if ":" in normalized:
        exchange, ticker = normalized.split(":", 1)
    else:
        exchange, ticker = "BINANCE", normalized
    if exchange != "BINANCE":
        raise ValueError("Por ahora el snapshot cuantitativo soporta simbolos BINANCE, por ejemplo BINANCE:BTCUSDT.")
    binance_interval = interval_to_binance(interval)
    periods = sanitize_ema_periods(ema_periods)
    limit = min(1000, max(200, max(periods) * 5))
    query = urllib.parse.urlencode({"symbol": ticker, "interval": binance_interval, "limit": limit})
    request = urllib.request.Request(
        f"https://api.binance.com/api/v3/klines?{query}",
        headers={"User-Agent": "KimLive/1.4"},
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
    snapshot = {
        "symbol": f"{exchange}:{ticker}",
        "interval": interval or "D",
        "provider": "binance_klines",
        "candles": len(candles),
        "last_close": round_opt(last_close, 4),
        "trend": trend,
        "ema_periods": periods,
        "emas": {str(period): round_opt(value, 4) for period, value in ema_values.items()},
        "ema20": round_opt(ema20, 4),
        "ema34": round_opt(ema34, 4),
        "ema50": round_opt(ema50, 4),
        "rsi14": round_opt(rsi14, 2),
        "support20": round_opt(support20, 4),
        "resistance20": round_opt(resistance20, 4),
        "support50": round_opt(support50, 4),
        "resistance50": round_opt(resistance50, 4),
        "change_5": round_opt(pct_change(closes, 5), 2),
        "change_20": round_opt(pct_change(closes, 20), 2),
        "current_volume": round_opt(current_volume, 4),
        "avg_volume20": round_opt(avg_volume20, 4),
        "volume_ratio": round_opt(current_volume / avg_volume20 if avg_volume20 else None, 2),
    }
    snapshot["summary"] = (
        f"{snapshot['symbol']} {snapshot['interval']}: cierre {snapshot['last_close']}, "
        f"tendencia {snapshot['trend']}, EMA34 {snapshot['ema34']}, RSI14 {snapshot['rsi14']}, "
        f"soporte 20v {snapshot['support20']}, resistencia 20v {snapshot['resistance20']}, "
        f"volumen relativo {snapshot['volume_ratio']}x."
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
                result = portfolio_cli(body.get("action", "status"), body.get("parameters") or {})
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
                snapshot = market_snapshot(body.get("symbol", ""), body.get("interval", "D"), body.get("ema_periods"))
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
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Kim Live running at http://{HOST}:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
