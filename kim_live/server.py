#!/usr/bin/env python3
"""
Kim Live.

Local-only conversation capture server for BIFROST.
The browser handles OpenAI Realtime voice when configured, local dictation when
available, and BIFROST stores the transcript.
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import cgi
import datetime as dt
import hashlib
import html
import io
import json
import mimetypes
import pathlib
import re
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
RUNTIME_CALLS = RUNTIME_MEMORY_ROOT / "calls"
RUNTIME_UPLOADS = RUNTIME_MEMORY_ROOT / "uploads"
RUNTIME_RESEARCH = RUNTIME_MEMORY_ROOT / "research"
RUNTIME_MEMORY_ANALYTICS = RUNTIME_CONTEXT / "memory_analytics_latest.json"
RUNTIME_UPLOAD_INDEX = RUNTIME_CONTEXT / "uploaded_files_index.json"
RUNTIME_CALL_INDEX = RUNTIME_CONTEXT / "call_index.jsonl"
CONTEXT_MEMORY = BIFROST / "MEMORY" / "context" / "kim_context.md"
CONTEXT_SPEC = BIFROST / "docs" / "kim_live_context_memory_spec.md"
CLICKUP_INVENTORY = BIFROST / "kimtools" / "clickup" / "clickup_inventory.json"
RUNTIME_CLICKUP_INVENTORY = pathlib.Path("/Users/dryehoshuapython/.kim_telegram/clickup_inventory.json")
CLICKUP_TASKS_JSON = BIFROST / "MEMORY" / "context" / "clickup_open_tasks_latest.json"
CLICKUP_TASKS_MARKDOWN = BIFROST / "MEMORY" / "context" / "clickup_open_tasks_latest.md"
RUNTIME_CLICKUP_TASKS_JSON = RUNTIME_CONTEXT / "clickup_open_tasks_latest.json"
RUNTIME_CLICKUP_TASKS_MARKDOWN = RUNTIME_CONTEXT / "clickup_open_tasks_latest.md"
OPERATING_MODEL = BIFROST / "docs" / "operating_model.md"
NOTION_CLICKUP_EVAL = BIFROST / "docs" / "notion_vs_clickup_evaluation.md"
TELEGRAM_BRIDGE = pathlib.Path("/Users/dryehoshuapython/.kim_telegram/telegram_kim_bridge.py")
OPENAI_KEYCHAIN_SERVICE = "codex.openai.api_key"
KEYCHAIN_ACCOUNT = "dryehoshuapython"
HOST = "127.0.0.1"
PORT = 8765
OPENAI_API_BASE = "https://api.openai.com/v1"
REALTIME_MODEL = "gpt-realtime"
REALTIME_VOICE = "marin"
APP_VERSION = "1.4.0"
RESEARCH_MODEL_CANDIDATES = ["gpt-5.4-mini", "gpt-5.4", "gpt-5"]
DOCUMENT_MODEL_CANDIDATES = ["gpt-5.4-mini", "gpt-5.4", "gpt-5"]
MEMORY_DOCUMENTS = MEMORY_ROOT / "documents"
RUNTIME_DOCUMENTS = RUNTIME_MEMORY_ROOT / "documents"


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


def write_json(handler, payload, status=200):
    data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


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
        try:
            completed = subprocess.run(
                ["strings", handle.name],
                text=True,
                capture_output=True,
                timeout=30,
                check=True,
            )
            lines = [line.strip() for line in completed.stdout.splitlines() if len(line.strip()) > 4]
            return "\n".join(lines[:2500])
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
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
        "chars": len(text),
    }
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
        "extractor": extraction["extractor"],
        "mime": extraction["mime"],
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


def research_with_openai(query, transcript=""):
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


def realtime_session_config():
    local_context = context_brief()
    return {
        "session": {
            "type": "realtime",
            "model": REALTIME_MODEL,
            "instructions": (
                "Eres Kim, asistente personal de Dr Yehoshua. "
                "Habla en espanol mexicano con tono calido, directo y util. "
                "Responde breve en conversacion viva. Si el doctor te dicta una "
                "tarea, confirma la accion y sugiere guardarla o ejecutarla desde Kim Live. "
                "Si necesitas datos actuales, investigacion externa o verificacion en internet, "
                "di brevemente que vas a buscar y llama la herramienta kim_research_web. "
                "Si el doctor pide redactar una carta, propuesta, reporte o documento, llama "
                "kim_draft_document. Cuando el doctor suba archivos, usa los resumenes que aparecen "
                "en la conversacion activa como contexto. "
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


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            data = (APP_DIR / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
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
            if parsed.path == "/api/upload-memory-file":
                analysis = parse_upload(self)
                write_json(self, {"ok": True, "analysis": analysis})
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
                result = research_with_openai(body.get("query", ""), body.get("transcript", ""))
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
