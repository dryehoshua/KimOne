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
import hmac
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
from zoneinfo import ZoneInfo


APP_DIR = pathlib.Path(__file__).resolve().parent
BIFROST = pathlib.Path("/Users/dryehoshuapython/Documents/BIFROST")
RUNTIME_ASSETS = APP_DIR / "assets"
MEMORY_INBOX = BIFROST / "MEMORY" / "inbox"
RUNTIME_MEMORY_ROOT = pathlib.Path("/Users/dryehoshuapython/.kim_live/MEMORY")
RUNTIME_MEMORY_INBOX = pathlib.Path("/Users/dryehoshuapython/.kim_live/MEMORY/inbox")
RUNTIME_CONTEXT = pathlib.Path("/Users/dryehoshuapython/.kim_live/context")
MEMORY_ROOT = BIFROST / "MEMORY"
MEMORY_CONTEXT_DIR = MEMORY_ROOT / "context"
MEMORY_CALLS = MEMORY_ROOT / "calls"
MEMORY_UPLOADS = MEMORY_ROOT / "uploads"
MEMORY_RESEARCH = MEMORY_ROOT / "research"
MEMORY_KNOWLEDGE = MEMORY_ROOT / "knowledge"
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
FILE_KNOWLEDGE_INDEX = MEMORY_CONTEXT_DIR / "file_knowledge_index.json"
FILE_KNOWLEDGE_INDEX_MD = MEMORY_CONTEXT_DIR / "file_knowledge_index.md"
CALL_INDEX = MEMORY_CONTEXT_DIR / "call_index.jsonl"
RESEARCH_SOURCE_CACHE = MEMORY_CONTEXT_DIR / "research_sources_latest.json"
RUNTIME_CALLS = RUNTIME_MEMORY_ROOT / "calls"
RUNTIME_UPLOADS = RUNTIME_MEMORY_ROOT / "uploads"
RUNTIME_RESEARCH = RUNTIME_MEMORY_ROOT / "research"
RUNTIME_KNOWLEDGE = RUNTIME_MEMORY_ROOT / "knowledge"
RUNTIME_PHONE_CALLS = RUNTIME_MEMORY_ROOT / "phone_calls"
RUNTIME_MEMORY_ANALYTICS = RUNTIME_CONTEXT / "memory_analytics_latest.json"
RUNTIME_UPLOAD_INDEX = RUNTIME_CONTEXT / "uploaded_files_index.json"
RUNTIME_FILE_KNOWLEDGE_INDEX = RUNTIME_CONTEXT / "file_knowledge_index.json"
RUNTIME_FILE_KNOWLEDGE_INDEX_MD = RUNTIME_CONTEXT / "file_knowledge_index.md"
RUNTIME_CALL_INDEX = RUNTIME_CONTEXT / "call_index.jsonl"
RUNTIME_RESEARCH_SOURCE_CACHE = RUNTIME_CONTEXT / "research_sources_latest.json"
SITE_AUTH_SESSIONS = RUNTIME_CONTEXT / "site_auth_sessions.json"
SITE_LEADS = BIFROST / "CRM" / "leads" / "kim_site_leads.jsonl"
RUNTIME_SITE_LEADS = RUNTIME_CONTEXT / "site_leads.jsonl"
BIFROST_EXPORT_DIR = RUNTIME_CONTEXT / "exports"
BIFROST_EXPORT_TOKENS = RUNTIME_CONTEXT / "bifrost_export_tokens.json"
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
WHATSAPP_THREAD_DIR = MEMORY_ROOT / "whatsapp_threads"
RUNTIME_WHATSAPP_THREAD_DIR = RUNTIME_MEMORY_ROOT / "whatsapp_threads"
WHATSAPP_THREAD_INDEX = MEMORY_CONTEXT_DIR / "whatsapp_thread_index.json"
RUNTIME_WHATSAPP_THREAD_INDEX = RUNTIME_CONTEXT / "whatsapp_thread_index.json"
WHATSAPP_CLICKUP_OUTBOX = MEMORY_CONTEXT_DIR / "whatsapp_clickup_outbox.jsonl"
RUNTIME_WHATSAPP_CLICKUP_OUTBOX = RUNTIME_CONTEXT / "whatsapp_clickup_outbox.jsonl"
VOICE_PROFILE_FILE = MEMORY_CONTEXT_DIR / "kim_voice_profile.json"
RUNTIME_VOICE_PROFILE_FILE = RUNTIME_CONTEXT / "kim_voice_profile.json"
WHATSAPP_MEDIA_DIR = MEMORY_ROOT / "whatsapp_media"
RUNTIME_WHATSAPP_MEDIA_DIR = RUNTIME_MEMORY_ROOT / "whatsapp_media"
WHATSAPP_PUBLIC_AUDIO_DIR = RUNTIME_ASSETS / "whatsapp_audio"
WHATSAPP_PUBLIC_AUDIO_PATH_PREFIX = "/media/whatsapp_audio"
SELLER_KNOWLEDGE_DIR = MEMORY_ROOT / "knowledge" / "seller"
RUNTIME_SELLER_KNOWLEDGE_DIR = RUNTIME_MEMORY_ROOT / "knowledge" / "seller"
SELLER_CONTEXT_PACK = SELLER_KNOWLEDGE_DIR / "seller_context_pack.json"
RUNTIME_SELLER_CONTEXT_PACK = RUNTIME_SELLER_KNOWLEDGE_DIR / "seller_context_pack.json"
DOCTOR_AVAILABILITY = MEMORY_CONTEXT_DIR / "doctor_availability.json"
RUNTIME_DOCTOR_AVAILABILITY = RUNTIME_CONTEXT / "doctor_availability.json"
TWILIO_CALL_LOG = MEMORY_CONTEXT_DIR / "twilio_call_actions.jsonl"
RUNTIME_TWILIO_CALL_LOG = RUNTIME_CONTEXT / "twilio_call_actions.jsonl"
TWILIO_REALTIME_SYNC_QUEUE = MEMORY_CONTEXT_DIR / "twilio_realtime_sync_queue.jsonl"
RUNTIME_TWILIO_REALTIME_SYNC_QUEUE = RUNTIME_CONTEXT / "twilio_realtime_sync_queue.jsonl"
TWILIO_REALTIME_HEALTH = MEMORY_CONTEXT_DIR / "twilio_realtime_health.json"
RUNTIME_TWILIO_REALTIME_HEALTH = RUNTIME_CONTEXT / "twilio_realtime_health.json"
KIM_LIVE_NOTIFICATIONS = MEMORY_CONTEXT_DIR / "kim_live_notifications.jsonl"
RUNTIME_KIM_LIVE_NOTIFICATIONS = RUNTIME_CONTEXT / "kim_live_notifications.jsonl"
TWILIO_CALL_CONTEXTS = MEMORY_CONTEXT_DIR / "twilio_call_contexts.json"
RUNTIME_TWILIO_CALL_CONTEXTS = RUNTIME_CONTEXT / "twilio_call_contexts.json"
EXTERNAL_CALL_CONTEXT_BLOCKS = MEMORY_CONTEXT_DIR / "external_call_context_blocks.json"
RUNTIME_EXTERNAL_CALL_CONTEXT_BLOCKS = RUNTIME_CONTEXT / "external_call_context_blocks.json"
EXTERNAL_CALL_CONTEXT_BLOCKS_DIR = MEMORY_CALLS / "_context_blocks"
RUNTIME_EXTERNAL_CALL_CONTEXT_BLOCKS_DIR = RUNTIME_CALLS / "_context_blocks"
PERSON_CONTEXT_INDEX = MEMORY_CONTEXT_DIR / "person_context_index.json"
RUNTIME_PERSON_CONTEXT_INDEX = RUNTIME_CONTEXT / "person_context_index.json"
PERSON_CONTEXT_DIR = MEMORY_ROOT / "person_contexts"
RUNTIME_PERSON_CONTEXT_DIR = RUNTIME_MEMORY_ROOT / "person_contexts"
TWILIO_PIPEDRIVE_CALL_SYNC = MEMORY_CONTEXT_DIR / "twilio_pipedrive_call_sync.json"
RUNTIME_TWILIO_PIPEDRIVE_CALL_SYNC = RUNTIME_CONTEXT / "twilio_pipedrive_call_sync.json"
PIPEDRIVE_PHONE_INDEX = MEMORY_CONTEXT_DIR / "pipedrive_phone_index.json"
RUNTIME_PIPEDRIVE_PHONE_INDEX = RUNTIME_CONTEXT / "pipedrive_phone_index.json"
CLICKUP_STRUCTURE_JSON = MEMORY_CONTEXT_DIR / "clickup_structure_latest.json"
RUNTIME_CLICKUP_STRUCTURE_JSON = RUNTIME_CONTEXT / "clickup_structure_latest.json"
CLICKUP_OPERATION_MAP = MEMORY_CONTEXT_DIR / "clickup_operation_map.json"
RUNTIME_CLICKUP_OPERATION_MAP = RUNTIME_CONTEXT / "clickup_operation_map.json"
BIFROST_FILE_INDEX = MEMORY_CONTEXT_DIR / "bifrost_file_index.json"
RUNTIME_BIFROST_FILE_INDEX = RUNTIME_CONTEXT / "bifrost_file_index.json"
NOTION_DEFAULT_PARENT = MEMORY_CONTEXT_DIR / "notion_default_parent.json"
RUNTIME_NOTION_DEFAULT_PARENT = RUNTIME_CONTEXT / "notion_default_parent.json"
NOTION_ACCESS_INVENTORY = MEMORY_CONTEXT_DIR / "notion_access_inventory.md"
RUNTIME_NOTION_ACCESS_INVENTORY = RUNTIME_CONTEXT / "notion_access_inventory.md"
NOTION_OUTBOX_DIR = MEMORY_ROOT / "notion_outbox"
RUNTIME_NOTION_OUTBOX_DIR = RUNTIME_MEMORY_ROOT / "notion_outbox"
ZOOM_MEETINGS_LOG = MEMORY_CONTEXT_DIR / "zoom_meetings.jsonl"
RUNTIME_ZOOM_MEETINGS_LOG = RUNTIME_CONTEXT / "zoom_meetings.jsonl"
ZOOM_TRANSCRIPTS_DIR = MEMORY_ROOT / "zoom_transcripts"
RUNTIME_ZOOM_TRANSCRIPTS_DIR = RUNTIME_MEMORY_ROOT / "zoom_transcripts"
ZOOM_TRANSCRIPTS_LOG = MEMORY_CONTEXT_DIR / "zoom_transcripts.jsonl"
RUNTIME_ZOOM_TRANSCRIPTS_LOG = RUNTIME_CONTEXT / "zoom_transcripts.jsonl"
MARKET_PRICE_VALIDATION_LOG = MEMORY_CONTEXT_DIR / "market_price_validations.jsonl"
RUNTIME_MARKET_PRICE_VALIDATION_LOG = RUNTIME_CONTEXT / "market_price_validations.jsonl"
HOSTINGER_MAIL_LOG = MEMORY_CONTEXT_DIR / "hostinger_mail_actions.jsonl"
RUNTIME_HOSTINGER_MAIL_LOG = RUNTIME_CONTEXT / "hostinger_mail_actions.jsonl"
GOOGLE_MAPS_LOG = MEMORY_CONTEXT_DIR / "google_maps_actions.jsonl"
RUNTIME_GOOGLE_MAPS_LOG = RUNTIME_CONTEXT / "google_maps_actions.jsonl"
KIM_PRODUCT_BACKLOG_JSON = MEMORY_CONTEXT_DIR / "kim_product_backlog.json"
RUNTIME_KIM_PRODUCT_BACKLOG_JSON = RUNTIME_CONTEXT / "kim_product_backlog.json"
KIM_PRODUCT_BACKLOG_MD = MEMORY_CONTEXT_DIR / "kim_product_backlog.md"
RUNTIME_KIM_PRODUCT_BACKLOG_MD = RUNTIME_CONTEXT / "kim_product_backlog.md"
KIM_PRODUCT_BACKLOG_SPEC = BIFROST / "docs" / "kim_live_whatsapp_sales_backlog.md"
PORTFOLIO_TOOL = APP_DIR / "portfolio_db.py"
PAPER_BROKER_TOOL = APP_DIR / "kim_paper_broker.py"
PORTFOLIO_REPORT_OVERRIDES = APP_DIR / "context" / "portfolio_report_overrides.json"
RUNTIME_PORTFOLIO_REPORT_OVERRIDES = RUNTIME_CONTEXT / "portfolio_report_overrides.json"
IGNIS_FINANCIALS_ROOT = MEMORY_ROOT / "IGNIS_FINANCIALS"
RUNTIME_IGNIS_FINANCIALS_ROOT = RUNTIME_MEMORY_ROOT / "IGNIS_FINANCIALS"
LEGACY_PORTFOLIO_SR_ELI_MEMORY_DIR = MEMORY_ROOT / "portfolios" / "ignis_stock_financials" / "clientes" / "manejo_de_portafolios" / "sr_eli_2026"
PORTFOLIO_SR_ELI_MEMORY_DIR = IGNIS_FINANCIALS_ROOT / "portfolios" / "clientes" / "manejo_de_portafolios" / "sr_eli_2026"
RUNTIME_PORTFOLIO_SR_ELI_MEMORY_DIR = RUNTIME_IGNIS_FINANCIALS_ROOT / "portfolios" / "sr_eli_2026"
PORTFOLIO_SR_ELI_STANDARD_JSON = PORTFOLIO_SR_ELI_MEMORY_DIR / "portfolio_a_standard.json"
RUNTIME_PORTFOLIO_SR_ELI_STANDARD_JSON = RUNTIME_PORTFOLIO_SR_ELI_MEMORY_DIR / "portfolio_a_standard.json"
PORTFOLIO_SR_ELI_STANDARD_MD = PORTFOLIO_SR_ELI_MEMORY_DIR / "portfolio_a_standard.md"
RUNTIME_PORTFOLIO_SR_ELI_STANDARD_MD = RUNTIME_PORTFOLIO_SR_ELI_MEMORY_DIR / "portfolio_a_standard.md"
PORTFOLIO_SR_ELI_FUNDAMENTAL_LOG = PORTFOLIO_SR_ELI_MEMORY_DIR / "fundamental_reports.jsonl"
RUNTIME_PORTFOLIO_SR_ELI_FUNDAMENTAL_LOG = RUNTIME_PORTFOLIO_SR_ELI_MEMORY_DIR / "fundamental_reports.jsonl"
TRADINGVIEW_WEBHOOK_CONFIG = MEMORY_CONTEXT_DIR / "tradingview_webhook.json"
RUNTIME_TRADINGVIEW_WEBHOOK_CONFIG = RUNTIME_CONTEXT / "tradingview_webhook.json"
MEMORY_ROUTER_LOG = MEMORY_CONTEXT_DIR / "memory_routes.jsonl"
RUNTIME_MEMORY_ROUTER_LOG = RUNTIME_CONTEXT / "memory_routes.jsonl"
TWILIO_MEDIA_WS_URL_FILE = RUNTIME_CONTEXT / "twilio_media_ws_url.txt"
OPERATING_MODEL = BIFROST / "docs" / "operating_model.md"
NOTION_CLICKUP_EVAL = BIFROST / "docs" / "notion_vs_clickup_evaluation.md"
INBOUND_CALL_PRIVACY_SPEC = BIFROST / "docs" / "kim_live_inbound_privacy_spec.md"
RUNTIME_INBOUND_CALL_PRIVACY_SPEC = RUNTIME_CONTEXT / "kim_live_inbound_privacy_spec.md"
MULTITENANT_AGENT_PLAN = BIFROST / "docs" / "kim_multitenant_agent_plan.md"
RUNTIME_MULTITENANT_AGENT_PLAN = RUNTIME_CONTEXT / "kim_multitenant_agent_plan.md"
TELEGRAM_BRIDGE = pathlib.Path("/Users/dryehoshuapython/.kim_telegram/telegram_kim_bridge.py")
OPENAI_KEYCHAIN_SERVICE = "codex.openai.api_key"
CLICKUP_KEYCHAIN_SERVICE = "codex.clickup.personal_token"
NOTION_KEYCHAIN_SERVICE = "codex.notion.integration_token"
PIPEDRIVE_KEYCHAIN_SERVICE = "codex.pipedrive.api_token"
PIPEDRIVE_COMPANY_DOMAIN_KEYCHAIN_SERVICE = "codex.pipedrive.company_domain"
GMAIL_CLIENT_ID_KEYCHAIN_SERVICE = "codex.google.gmail.client_id"
GMAIL_CLIENT_SECRET_KEYCHAIN_SERVICE = "codex.google.gmail.client_secret"
GMAIL_REFRESH_TOKEN_KEYCHAIN_SERVICE = "codex.google.gmail.refresh_token"
GOOGLE_MAPS_API_KEYCHAIN_SERVICE = "codex.google.maps.api_key"
ZOOM_ACCOUNT_ID_KEYCHAIN_SERVICE = "codex.zoom.account_id"
ZOOM_CLIENT_ID_KEYCHAIN_SERVICE = "codex.zoom.client_id"
ZOOM_CLIENT_SECRET_KEYCHAIN_SERVICE = "codex.zoom.client_secret"
ZOOM_REFRESH_TOKEN_KEYCHAIN_SERVICE = "codex.zoom.refresh_token"
ZOOM_DEFAULT_HOST_KEYCHAIN_SERVICE = "codex.zoom.default_host"
COINMARKETCAP_KEYCHAIN_SERVICE = "codex.coinmarketcap.api_key"
TWILIO_ACCOUNT_SID_KEYCHAIN_SERVICE = "codex.twilio.account_sid"
TWILIO_AUTH_TOKEN_KEYCHAIN_SERVICE = "codex.twilio.auth_token"
TWILIO_API_KEY_SID_KEYCHAIN_SERVICE = "codex.twilio.api_key_sid"
TWILIO_API_KEY_SECRET_KEYCHAIN_SERVICE = "codex.twilio.api_key_secret"
TWILIO_DEFAULT_FROM_NUMBER_KEYCHAIN_SERVICE = "codex.twilio.default_from_number"
SECURITY_VOICE_PHRASE_KEYCHAIN_SERVICE = "codex.kim.security.voice_phrase"
SECURITY_PIN_KEYCHAIN_SERVICE = "codex.kim.security.pin"
SITE_ACCESS_CODE_KEYCHAIN_SERVICE = "codex.kim.site_access_code"
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
GOOGLE_MAPS_GEOCODING_BASE = "https://maps.googleapis.com"
GOOGLE_PLACES_API_BASE = "https://places.googleapis.com"
GOOGLE_ROUTES_API_BASE = "https://routes.googleapis.com"
TWILIO_API_BASE = "https://api.twilio.com/2010-04-01"
ZOOM_OAUTH_TOKEN_URL = "https://zoom.us/oauth/token"
ZOOM_API_BASE = "https://api.zoom.us/v2"
GMAIL_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
GMAIL_OAUTH_STATE_FILE = RUNTIME_CONTEXT / "google_gmail_oauth_state.json"
ZOOM_OAUTH_STATE_FILE = RUNTIME_CONTEXT / "zoom_oauth_state.json"
NOTION_VERSION = "2022-06-28"
REALTIME_MODEL = "gpt-realtime"
REALTIME_VOICE = "coral"
PHONE_REPLY_MODEL_CANDIDATES = ["gpt-5.4-mini", "gpt-5.4", "gpt-5"]
APP_VERSION = "1.5.82"
VERSION_MEMORY_BASELINE_NOTES = [
    ("1.5.61", "fuente actual de KimOne en esta Mac; usar esta como version viva del backend."),
    ("1.5.48", "aislamiento de contexto en llamadas Twilio para no mezclar contactos o hilos."),
    ("1.5.43", "reconstruccion completa de transcripciones, mejoras del scheduler local y ajustes de UX."),
]
DEFAULT_SCHEDULER_TIMEZONE = "America/Mexico_City"
DOCTOR_DUBAI_WHATSAPP_NUMBER = "+971585943726"
DOCTOR_DUBAI_WHATSAPP_TO = f"whatsapp:{DOCTOR_DUBAI_WHATSAPP_NUMBER}"
KEYCHAIN_READ_TIMEOUT = 8
RESEARCH_MODEL_CANDIDATES = ["gpt-5.4-mini", "gpt-5.4", "gpt-5"]
DOCUMENT_MODEL_CANDIDATES = ["gpt-5.4-mini", "gpt-5.4", "gpt-5"]
VISION_MODEL_CANDIDATES = ["gpt-5.4-mini", "gpt-5.4", "gpt-5"]
OPENAI_TRANSCRIBE_MODEL_CANDIDATES = ["gpt-4o-mini-transcribe", "gpt-4o-transcribe"]
OPENAI_SPEECH_MODEL_CANDIDATES = ["gpt-4o-mini-tts", "tts-1"]
WHATSAPP_REPLY_VOICE = "coral"
TWILIO_POLLY_VOICE = "Polly.Mia"
REALTIME_COMPATIBLE_VOICES = {"alloy", "ash", "ballad", "coral", "echo", "sage", "shimmer", "verse", "marin", "cedar"}
KIM_VOICE_OPTIONS = [
    {"id": "coral", "label": "Coral", "mood": "mas aguda, alegre y luminosa", "recommended": True},
    {"id": "nova", "label": "Nova", "mood": "joven, clara y brillante; TTS/WhatsApp, no siempre Realtime"},
    {"id": "shimmer", "label": "Shimmer", "mood": "suave y eterea"},
    {"id": "sage", "label": "Sage", "mood": "calmada, madura y serena"},
    {"id": "marin", "label": "Marin", "mood": "calida y cercana"},
    {"id": "verse", "label": "Verse", "mood": "expresiva y teatral"},
    {"id": "alloy", "label": "Alloy", "mood": "neutral y estable"},
]
KIM_VOICE_STYLE = (
    "Voz femenina, clara, alegre y seductora profesional: habla con calidez, seguridad, ritmo vivo pero elegante, "
    "brillo vocal y sonrisa audible. Debe sonar cercana y magnetica, nunca vulgar, exagerada, infantil ni invasiva. "
    "En contextos de clientes conserva autoridad ejecutiva y discrecion."
)
KIM_TTS_INSTRUCTIONS = (
    "Speak as Kim: a feminine, warm, elegant, subtly seductive professional assistant. "
    "Use a bright, cheerful, slightly higher feminine delivery, confident pacing, a soft smile in the voice, and natural Mexican Spanish cadence. "
    "Keep it tasteful, executive, intimate but not sexual, and never exaggerated."
)
MEMORY_DOCUMENTS = MEMORY_ROOT / "documents"
RUNTIME_DOCUMENTS = RUNTIME_MEMORY_ROOT / "documents"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".heic", ".heif", ".tif", ".tiff", ".bmp"}
PUBLIC_ASSETS = {
    "/assets/kim/kim_whatsapp_avatar_korean_digital.png": [
        RUNTIME_ASSETS / "kim" / "kim_whatsapp_avatar_korean_digital.png",
        BIFROST / "assets" / "kim" / "kim_whatsapp_avatar_korean_digital.png",
    ],
}
INBOUND_CALL_SERVICE_SUMMARY = (
    "informacion general de servicios, seguimiento de pendientes propios, llamadas con contexto, "
    "coordinacion de correos y documentos, CRM, tareas, agentes de IA y empleados de IA, automatizacion con IA, "
    "atencion telefonica, reportes, servicio al cliente, clasificacion de proveedores/clientes/buyer personas, "
    "marketing automation avanzado, procesamiento de datos, memoria operativa, "
    "consultoria tecnologica y empresarial en branding, procesos y desarrollo humano, analisis financiero, "
    "operacion de portafolios, hedge fund, venture capital y recepcion para clientes o interesados en "
    "Tesca Elements, Ignis, Ai People y otros proyectos del Dr. Yehoshua"
)
AI_PEOPLE_SALES_POSITIONING = (
    "Ai People ayuda a empresas a implementar agentes y empleados de IA que atienden llamadas, correos, "
    "reportes, CRM, servicio al cliente, seguimiento comercial, analisis de datos y automatizacion de procesos. "
    "La tecnologia puede operar localmente en la maquina del cliente, en infraestructura administrada por Ai People "
    "o en una arquitectura privada segun seguridad, presupuesto y complejidad."
)
AI_PEOPLE_SALES_PLAYBOOK = (
    "Actua como vendedora consultiva profesional. Primero escucha y valida con empatia. Despues pregunta cual es "
    "el dolor operativo o comercial mas importante. Profundiza con tacto: que costo tiene seguir igual, que se pierde "
    "en tiempo, dinero, clientes o control, y que soluciones han probado que no resolvieron el problema. Luego conecta "
    "ese dolor con un resultado aspiracional: como se veria una operacion con un empleado de IA que responde, recuerda, "
    "documenta y ejecuta. Cierra buscando el siguiente paso: una cita con el Dr. Yehoshua si hay interes real."
)
AI_PEOPLE_DISCOVERY_FLOW = (
    "Captura nombre, empresa, rol, industria, proceso que duele, urgencia, herramientas actuales, soluciones previas, "
    "impacto economico aproximado, resultado ideal, presupuesto o rango si la conversacion lo permite, correo/telefono "
    "de contacto y dos horarios preferidos con zona horaria para una cita. No digas que la cita quedo agendada hasta "
    "que exista confirmacion de calendario; por ahora di que dejaras la solicitud lista para el doctor."
)
AI_PEOPLE_COMMERCIAL_GUARDRAILS = (
    "Precios orientativos: implementaciones basicas de agente o funcion suelen iniciar en USD 3k-5k; infraestructura "
    "completa suele ubicarse en USD 10k-20k segun complejidad; una arquitectura privada/local con modelo propio o equipo "
    "dedicado puede rondar USD 30k o mas. Puede existir cuota mensual por operacion, modelos y soporte. ROI objetivo "
    "frecuente: recuperar valor en 3-6 meses cuando el proceso esta bien elegido, pero nunca lo prometas como garantia. "
    "Para inversionistas, Ignis, portafolios, deuda o dinero de terceros, no prometas rendimientos ni tranquilices con "
    "frases absolutas; registra detalles y escala al Dr. Yehoshua."
)
REMOTE_SECRETARY_BRIDGE_POLICY = (
    "Kim debe operar como secretaria y puente remoto hacia Kim Live. Para el Dr. Yehoshua, WhatsApp, SMS y llamadas "
    "son canales de control operativo: recibir instrucciones, guardar contexto, notificar Kim Live y preparar acciones "
    "sin afirmar ejecucion externa si no existe resultado confirmado. Para terceros, Kim solo usa el hilo propio del "
    "contacto: puede preguntar disponibilidad publica, tomar recados, orientar clientes, desarrollar relacion comercial, "
    "explicar ofertas y servicios de AI People, Tesca Elements e Ignis, y proponer cita o seguimiento. Nunca debe revelar "
    "agenda privada, memoria de otros contactos, datos de clientes/inversionistas, portafolios privados ni tareas internas "
    "del doctor. Si el contacto no esta identificado, primero pide nombre, empresa y necesidad."
)
INBOUND_RELATIONSHIP_GOODWILL_POLICY = (
    "Cada inbound de terceros debe desarrollar relacion comercial o buen nombre para Dr. Yehoshua, Tesca Elements, "
    "Ignis Financials/iGNIS SF y AI People. Kim debe dejar a la persona mejor orientada, escuchada y con una percepcion "
    "profesional del grupo. Debe descubrir necesidad, cuidar reputacion, mencionar capacidades publicas pertinentes, "
    "proponer un siguiente paso suave y registrar lo que contestaron. Si la persona no compra hoy, debe quedar una "
    "relacion educada y retomable. Kim no presiona ni exagera; construye confianza, claridad y continuidad."
)
WHATSAPP_SALES_PR_MEETING_PLAYBOOK = (
    "WhatsApp ventas/RP: Kim debe construir relacion antes de vender. Usa rapport breve, escucha activa, preguntas "
    "consultivas, espejo del dolor, contraste del costo de seguir igual y una propuesta clara de siguiente paso. "
    "Objetivo comercial principal: lograr una reunion diagnostica con el Dr. Yehoshua cuando haya interes real. "
    "Debe capturar nombre, empresa, rol, correo, telefono, zona horaria, dolor principal, urgencia, herramientas actuales, "
    "resultado deseado y dos horarios posibles. Puede preparar Zoom con provider zoom/create_meeting y confirm=false "
    "solo si ya hay horario claro; si falta dato, lo pide con elegancia. Nunca inventa liga Zoom ni cita confirmada "
    "sin join_url/resultado API. Para terceros, todo seguimiento queda en su hilo aislado y CRM."
)
DOCTOR_CONTEXT_NAME_HINTS = (
    "dr yehoshua",
    "dr. yehoshua",
    "doctor yehoshua",
    "doctor joshua",
    "dr yehoshua rodriguez",
    "yehoshua rodriguez",
)
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
SCHEDULER_THREAD_REF = None
SCHEDULER_LOCK = threading.Lock()
SCHEDULER_STALE_RUNNING_SECONDS = 15 * 60
SECURITY_AUTHORIZATIONS = MEMORY_CONTEXT_DIR / "kim_security_authorizations.json"
RUNTIME_SECURITY_AUTHORIZATIONS = RUNTIME_CONTEXT / "kim_security_authorizations.json"
SECURITY_AUTH_TTL_SECONDS = 15 * 60
SECURITY_SECRET_CACHE_SECONDS = 60
SECURITY_SECRET_CACHE = {"loaded_at": 0.0, "items": [], "loaded_once": False}
BIFROST_EXPORT_TTL_SECONDS = 30 * 60
BIFROST_EXPORT_MAX_DOWNLOADS = 5
BIFROST_EXPORT_SKIP_NAMES = {".DS_Store", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
BIFROST_EXPORT_SKIP_SUFFIXES = {".pyc", ".pyo"}
HOSTINGER_IMAP_HOST = "imap.hostinger.com"
HOSTINGER_IMAP_PORT = 993
HOSTINGER_SMTP_HOST = "smtp.hostinger.com"
HOSTINGER_SMTP_PORT = 465
MARKET_PRICE_MAX_AGE_SECONDS = 15 * 60
MARKET_PRICE_SPREAD_LIMIT_PCT = 2.0
MARKET_PRICE_BATCH_CACHE_TTL_SECONDS = 90
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
    "HYPE": "hyperliquid",
    "ICP": "internet-computer",
    "LUNC": "terra-luna",
    "NEAR": "near",
    "ONDO": "ondo-finance",
    "PEPE": "pepe",
    "SHIB": "shiba-inu",
    "SOL": "solana",
    "SUI": "sui",
    "TRUMP": "official-trump",
    "TRX": "tron",
    "WLD": "worldcoin-wld",
    "XLM": "stellar",
    "XRP": "ripple",
    "ZEC": "zcash",
}
COINGECKO_BATCH_PRICE_CACHE = {"key": "", "loaded_at": 0.0, "items": {}}
COINMARKETCAP_BATCH_PRICE_CACHE = {"key": "", "loaded_at": 0.0, "items": {}}
ZOOM_TOKEN_CACHE = {"access_token": "", "api_url": ZOOM_API_BASE, "expires_at": 0.0, "scope": ""}


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
    try:
        handler.send_response(status)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.send_header("Content-Length", str(len(data)))
        handler.end_headers()
        handler.wfile.write(data)
    except (BrokenPipeError, ConnectionResetError):
        return


def write_text(handler, text, status=200, content_type="text/plain; charset=utf-8"):
    data = (text or "").encode("utf-8")
    try:
        handler.send_response(status)
        handler.send_header("Content-Type", content_type)
        handler.send_header("Cache-Control", "no-store")
        handler.send_header("Content-Length", str(len(data)))
        handler.end_headers()
        handler.wfile.write(data)
    except (BrokenPipeError, ConnectionResetError):
        return


def write_xml(handler, text, status=200):
    write_text(handler, text, status=status, content_type="text/xml; charset=utf-8")


def write_file_response(handler, path, content_type=None, cache_control="public, max-age=3600"):
    candidates = path if isinstance(path, (list, tuple)) else [path]
    selected_path = None
    data = None
    for candidate in candidates:
        candidate_path = pathlib.Path(candidate)
        try:
            if not candidate_path.exists() or not candidate_path.is_file():
                continue
            data = candidate_path.read_bytes()
            selected_path = candidate_path
            break
        except OSError:
            continue
    if selected_path is None or data is None:
        handler.send_error(404)
        return
    try:
        handler.send_response(200)
        handler.send_header("Content-Type", content_type or mimetypes.guess_type(selected_path.name)[0] or "application/octet-stream")
        handler.send_header("Cache-Control", cache_control)
        handler.send_header("Content-Length", str(len(data)))
        handler.end_headers()
        handler.wfile.write(data)
    except (BrokenPipeError, ConnectionResetError):
        return


def public_kim_asset_candidates(path_value):
    name = pathlib.PurePosixPath(urllib.parse.unquote(path_value)).name
    if not re.fullmatch(r"[A-Za-z0-9_.-]+\.(png|jpg|jpeg|webp|gif)", name, flags=re.I):
        return []
    return [
        RUNTIME_ASSETS / "kim" / name,
        APP_DIR / "assets" / "kim" / name,
        BIFROST / "assets" / "kim" / name,
    ]


def parse_cookie_header(value):
    cookies = {}
    for part in str(value or "").split(";"):
        if "=" not in part:
            continue
        key, raw = part.split("=", 1)
        cookies[key.strip()] = urllib.parse.unquote(raw.strip())
    return cookies


def cookie_token(handler):
    return parse_cookie_header(handler.headers.get("Cookie", "")).get("kim_live_access", "")


def token_hash(token):
    return hashlib.sha256(str(token or "").encode("utf-8")).hexdigest()


def load_site_auth_state():
    state = read_json_file(SITE_AUTH_SESSIONS, {"sessions": {}})
    if not isinstance(state, dict):
        state = {"sessions": {}}
    state.setdefault("sessions", {})
    return state


def save_site_auth_state(state):
    SITE_AUTH_SESSIONS.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = now_iso()
    write_json_file(SITE_AUTH_SESSIONS, state)


def site_access_code():
    return (
        load_keychain_secret(SITE_ACCESS_CODE_KEYCHAIN_SERVICE, required=False)
        or load_keychain_secret(SECURITY_PIN_KEYCHAIN_SERVICE, required=False)
    )


def site_auth_status(handler):
    token = cookie_token(handler)
    if not token:
        return {"authenticated": False}
    state = load_site_auth_state()
    now = dt.datetime.now()
    changed = False
    for digest, item in list((state.get("sessions") or {}).items()):
        expires_at = str(item.get("expires_at") or "")
        try:
            expired = dt.datetime.fromisoformat(expires_at) <= now
        except ValueError:
            expired = True
        if expired:
            state["sessions"].pop(digest, None)
            changed = True
    digest = token_hash(token)
    item = (state.get("sessions") or {}).get(digest)
    if changed:
        save_site_auth_state(state)
    if not item:
        return {"authenticated": False}
    return {
        "authenticated": True,
        "label": item.get("label") or "Kim operator",
        "expires_at": item.get("expires_at") or "",
    }


def site_auth_is_valid(handler):
    return bool(site_auth_status(handler).get("authenticated"))


def send_auth_cookie(handler, token="", max_age=86400):
    parts = [
        "kim_live_access=" + urllib.parse.quote(token or ""),
        "Path=/",
        "HttpOnly",
        "SameSite=Lax",
        f"Max-Age={max_age}",
    ]
    handler.send_header("Set-Cookie", "; ".join(parts))


def create_site_session(handler, label=""):
    token = secrets.token_urlsafe(32)
    expires = dt.datetime.now() + dt.timedelta(hours=18)
    state = load_site_auth_state()
    state.setdefault("sessions", {})[token_hash(token)] = {
        "label": brief(label or "Kim operator", 80),
        "created_at": now_iso(),
        "expires_at": expires.isoformat(timespec="seconds"),
        "ip": handler.client_address[0] if handler.client_address else "",
    }
    save_site_auth_state(state)
    return token, expires


def login_site_user(handler, body):
    code = str(body.get("access_code") or body.get("code") or "").strip()
    label = str(body.get("name") or body.get("email") or "Kim operator").strip()
    expected = site_access_code()
    if not expected:
        append_memory("site_login_blocked", {"reason": "missing_site_access_code"})
        return None, {"ok": False, "error": "No hay codigo de acceso configurado en Keychain."}, 503
    if not hmac.compare_digest(code, expected):
        append_memory("site_login_failed", {"label": brief(label, 80), "ip": handler.client_address[0] if handler.client_address else ""})
        return None, {"ok": False, "error": "Codigo de acceso incorrecto."}, 401
    token, expires = create_site_session(handler, label=label)
    append_memory("site_login_ok", {"label": brief(label, 80), "expires_at": expires.isoformat(timespec="seconds")})
    return token, {"ok": True, "authenticated": True, "label": label, "expires_at": expires.isoformat(timespec="seconds")}, 200


def record_public_lead(handler, body):
    lead = {
        "at": now_iso(),
        "ip": handler.client_address[0] if handler.client_address else "",
        "name": brief(body.get("name", ""), 140),
        "email": brief(body.get("email", ""), 180),
        "company": brief(body.get("company", ""), 180),
        "interest": brief(body.get("interest", ""), 400),
        "source": "kim_aipeople_landing",
    }
    if not lead["email"] and not lead["name"]:
        raise ValueError("Deja al menos nombre o correo para solicitar acceso.")
    append_jsonl_any([SITE_LEADS, RUNTIME_SITE_LEADS], lead)
    append_memory("site_access_request", {key: lead[key] for key in ["name", "email", "company", "interest"]})
    return lead


def is_public_get_path(path):
    return path in {"/", "/index.html", "/api/auth/status", "/twilio/health"} or path.startswith("/twilio/")


def is_public_post_path(path):
    return path in {"/api/auth/login", "/api/auth/logout", "/api/public-lead", "/api/tradingview/webhook"} or path.startswith("/twilio/")


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


def run_background_task(name, fn, *args, **kwargs):
    def runner():
        try:
            fn(*args, **kwargs)
        except Exception as exc:
            append_memory("background_task_error", {"task": name, "error": brief(str(exc), 800)})

    thread = threading.Thread(target=runner, daemon=True, name=name)
    thread.start()
    return thread


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
        except (PermissionError, OSError) as exc:
            last_error = exc
    if last_error:
        raise last_error
    return None


def write_text_file(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_text_file_any(paths, text):
    last_error = None
    for path in paths:
        try:
            write_text_file(path, text)
            return path
        except (PermissionError, OSError) as exc:
            last_error = exc
    if last_error:
        raise last_error
    return None


def write_bytes_file(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data or b"")


def write_bytes_file_both(primary, runtime, data):
    written = []
    for path in [primary, runtime]:
        try:
            write_bytes_file(path, data)
            written.append(str(path))
        except (PermissionError, OSError):
            continue
    return written


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


def voice_option(value):
    voice_id = str(value or "").strip().lower()
    for item in KIM_VOICE_OPTIONS:
        if item.get("id") == voice_id:
            return item
    return next((item for item in KIM_VOICE_OPTIONS if item.get("id") == WHATSAPP_REPLY_VOICE), KIM_VOICE_OPTIONS[0])


def payload_updated_at_ts(payload):
    if not isinstance(payload, dict):
        return 0.0
    raw = str(payload.get("updated_at") or "").strip()
    if not raw:
        return 0.0
    try:
        parsed = dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return 0.0
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.timestamp()


def newest_json_payload(paths):
    candidates = []
    for index, path in enumerate(paths):
        payload = read_json_file(path, None)
        if isinstance(payload, dict) and payload:
            score = payload_updated_at_ts(payload)
            if not score:
                try:
                    score = path.stat().st_mtime
                except OSError:
                    score = 0.0
            candidates.append((score, -index, payload))
    if not candidates:
        return {}
    candidates.sort(reverse=True)
    return candidates[0][2]


def load_voice_profile():
    payload = newest_json_payload([VOICE_PROFILE_FILE, RUNTIME_VOICE_PROFILE_FILE])
    if not isinstance(payload, dict):
        payload = {}
    selected = voice_option(payload.get("voice") or WHATSAPP_REPLY_VOICE)
    realtime_voice = selected["id"] if selected["id"] in REALTIME_COMPATIBLE_VOICES else REALTIME_VOICE
    profile = {
        "voice": selected["id"],
        "label": selected.get("label", selected["id"]),
        "mood": selected.get("mood", ""),
        "tts_voice": selected["id"],
        "realtime_voice": realtime_voice,
        "fallback_realtime_voice": REALTIME_VOICE,
        "twilio_fallback_voice": TWILIO_POLLY_VOICE,
        "style": str(payload.get("style") or KIM_VOICE_STYLE),
        "tts_instructions": str(payload.get("tts_instructions") or KIM_TTS_INSTRUCTIONS),
        "updated_at": payload.get("updated_at") or "",
    }
    return profile


def save_voice_profile(payload):
    payload = payload or {}
    selected = voice_option(payload.get("voice"))
    profile = load_voice_profile()
    profile.update(
        {
            "voice": selected["id"],
            "label": selected.get("label", selected["id"]),
            "mood": selected.get("mood", ""),
            "tts_voice": selected["id"],
            "realtime_voice": selected["id"] if selected["id"] in REALTIME_COMPATIBLE_VOICES else REALTIME_VOICE,
            "style": str(payload.get("style") or profile.get("style") or KIM_VOICE_STYLE),
            "tts_instructions": str(payload.get("tts_instructions") or profile.get("tts_instructions") or KIM_TTS_INSTRUCTIONS),
            "updated_at": now_iso(),
        }
    )
    write_json_file_both(VOICE_PROFILE_FILE, RUNTIME_VOICE_PROFILE_FILE, profile)
    append_memory("kim_voice_profile_updated", {"voice": profile["voice"], "realtime_voice": profile["realtime_voice"], "mood": profile["mood"]})
    return profile


def active_voice_profile():
    return load_voice_profile()


def active_realtime_voice():
    return active_voice_profile().get("realtime_voice") or REALTIME_VOICE


def active_tts_voice():
    return active_voice_profile().get("tts_voice") or WHATSAPP_REPLY_VOICE


def active_voice_style():
    return active_voice_profile().get("style") or KIM_VOICE_STYLE


def active_tts_instructions():
    return active_voice_profile().get("tts_instructions") or KIM_TTS_INSTRUCTIONS


def load_seller_context_pack_payload():
    payload = newest_json_payload([SELLER_CONTEXT_PACK, RUNTIME_SELLER_CONTEXT_PACK])
    return payload if isinstance(payload, dict) else {}


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
        except (PermissionError, OSError) as exc:
            last_error = exc
    if last_error:
        raise last_error
    return None


def write_jsonl(path, entries):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in entries:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")


def upsert_jsonl_any(paths, payload, key="session_id"):
    record_key = str(payload.get(key) or "").strip()
    if not record_key:
        return append_jsonl_any(paths, payload)
    last_error = None
    for path in paths:
        try:
            entries = []
            try:
                for line in path.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            except FileNotFoundError:
                entries = []
            filtered = [item for item in entries if str(item.get(key) or "").strip() != record_key]
            filtered.append(payload)
            write_jsonl(path, filtered)
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
        except (PermissionError, OSError):
            continue
    return written


def write_text_file_both(primary, runtime, text):
    written = []
    for path in [primary, runtime]:
        try:
            write_text_file(path, text)
            written.append(str(path))
        except (PermissionError, OSError):
            continue
    return written


def default_kim_product_backlog_payload():
    return {
        "updated_at": now_iso(),
        "version": "2026-06-04",
        "source_tasks": ["KIM-0088", "KIM-0089"],
        "product": "Kim Live / AI People",
        "focus": "Ventas y seguimiento inteligente por WhatsApp con supervision del doctor.",
        "doctor_requests": [
            "Guardar backlog de desarrollo Kim Live como fuente operativa durable.",
            "Priorizar ventas en WhatsApp con reportes y criterio para pedir permiso antes del siguiente contacto.",
            "Preparar seguimiento por franjas horarias para no sobre-contactar clientes.",
            "Mantener Zoom, correo, mapas y frontend como siguientes integraciones del producto.",
        ],
        "follow_up_windows": [
            {"label": "morning_review", "time_hint": "morning", "goal": "revisar pendientes comerciales y decidir a quien escribir primero"},
            {"label": "afternoon_review", "time_hint": "14:00", "goal": "segundo pase de seguimiento con clientes activos"},
            {"label": "evening_review", "time_hint": "18:00", "goal": "ultimo reporte del dia y propuesta del siguiente contacto"},
        ],
        "priorities": [
            {
                "id": "whatsapp_sales_followup",
                "priority": 1,
                "status": "active",
                "title": "Ventas y seguimiento por WhatsApp",
                "summary": "Kim debe atender clientes, resumir interes, recomendar proximo contacto y pedir aprobacion antes de ejecutar seguimiento sensible.",
                "deliverables": [
                    "reporte por contacto con interes, ultimo mensaje y siguiente paso sugerido",
                    "hilo conductor por cliente sin mezclar contextos",
                    "tecnicas basicas de venta consultiva y permiso explicito para follow-up",
                ],
                "next_safe_step": "Conectar backlog de producto con resumen de hilos WhatsApp y seller context pack.",
            },
            {
                "id": "gmail_cleanup_and_triage",
                "priority": 2,
                "status": "planned",
                "title": "Limpieza y revision de correo",
                "summary": "Leer ultimos correos, priorizar, y preparar limpieza segura antes de cualquier borrado o movimiento a papelera.",
                "deliverables": [
                    "resumen de correos recientes",
                    "cola de correos sugeridos para archivar o borrar con confirmacion",
                ],
                "next_safe_step": "Activar lectura Gmail/Hostinger y definir flujo de confirmacion para limpieza.",
            },
            {
                "id": "zoom_meeting_ops",
                "priority": 3,
                "status": "in_progress",
                "title": "Zoom para agenda comercial",
                "summary": "Kim debe poder preparar reuniones y dejarlas listas cuando haya horario confirmado.",
                "deliverables": [
                    "crear reunion con host y join_url validos",
                    "registrar reunion en memoria y reportes",
                ],
                "next_safe_step": "Aprovechar el bridge Zoom ya presente para amarrarlo al flujo comercial.",
            },
            {
                "id": "scheduled_tasks_for_doctor",
                "priority": 4,
                "status": "planned",
                "title": "Pendientes con horario y ritmo diario",
                "summary": "Asignar tareas a Kim en horarios concretos para crear cadencia operativa.",
                "deliverables": [
                    "tareas recurrentes confirmadas",
                    "bitacora de ejecucion y estado",
                ],
                "next_safe_step": "Aterrizar plantillas de scheduler para reportes y follow-up comercial.",
            },
            {
                "id": "maps_campaigns_and_mobility",
                "priority": 5,
                "status": "queued",
                "title": "Mapas, campanas y movilidad",
                "summary": "Ubicacion, distancias, campañas y futuro puente con transporte bajo confirmacion humana.",
                "deliverables": [
                    "consulta de ubicacion y distancias",
                    "contexto de campaña por zona",
                ],
                "next_safe_step": "Definir capa de lectura y analitica antes de cualquier automatizacion externa.",
            },
            {
                "id": "figma_frontend_and_prompt",
                "priority": 6,
                "status": "queued",
                "title": "Frontend de agentes en Figma y prompt de producto",
                "summary": "Diseño operativo de agentes y consolidacion del prompt base de Kim.",
                "deliverables": [
                    "estructura visual del frontend",
                    "prompt operativo mantenible",
                ],
                "next_safe_step": "Bajar requisitos de UX y vistas del operador antes de diseño.",
            },
        ],
        "notes": [
            "SMS sigue limitado como canal de respuesta; el enfoque activo es WhatsApp y reporteria.",
            "No hacer compras, transporte ni borrados destructivos sin confirmacion humana.",
            "Las integraciones externas deben operar con privacidad por contacto y memoria aislada.",
        ],
    }


def render_kim_product_backlog_markdown(payload):
    payload = payload or default_kim_product_backlog_payload()
    lines = [
        "# Kim Live backlog operativo",
        "",
        f"Actualizado: {payload.get('updated_at') or now_iso()}",
        f"Producto: {payload.get('product') or 'Kim Live'}",
        f"Foco actual: {payload.get('focus') or ''}",
        "",
        "## Prioridades",
    ]
    for item in payload.get("priorities") or []:
        lines.append(
            f"- P{item.get('priority', '?')} [{item.get('status') or 'planned'}] {item.get('title')}: {item.get('summary')}"
        )
        next_step = item.get("next_safe_step")
        if next_step:
            lines.append(f"  Siguiente paso seguro: {next_step}")
    windows = payload.get("follow_up_windows") or []
    if windows:
        lines.extend(["", "## Ventanas de seguimiento"])
        for item in windows:
            lines.append(f"- {item.get('label')}: {item.get('time_hint')} -> {item.get('goal')}")
    doctor_requests = payload.get("doctor_requests") or []
    if doctor_requests:
        lines.extend(["", "## Solicitudes del doctor"])
        for item in doctor_requests:
            lines.append(f"- {item}")
    notes = payload.get("notes") or []
    if notes:
        lines.extend(["", "## Guardrails"])
        for item in notes:
            lines.append(f"- {item}")
    return "\n".join(lines).strip() + "\n"


def load_kim_product_backlog_payload():
    payload = newest_json_payload([KIM_PRODUCT_BACKLOG_JSON, RUNTIME_KIM_PRODUCT_BACKLOG_JSON])
    if isinstance(payload, dict) and payload.get("priorities"):
        return payload
    payload = default_kim_product_backlog_payload()
    write_json_file_both(KIM_PRODUCT_BACKLOG_JSON, RUNTIME_KIM_PRODUCT_BACKLOG_JSON, payload)
    write_text_file_both(KIM_PRODUCT_BACKLOG_MD, RUNTIME_KIM_PRODUCT_BACKLOG_MD, render_kim_product_backlog_markdown(payload))
    return payload


def kim_product_backlog_summary(payload=None, limit=6):
    payload = payload or load_kim_product_backlog_payload()
    priorities = []
    for item in (payload.get("priorities") or [])[:limit]:
        priorities.append(
            {
                "id": item.get("id"),
                "priority": item.get("priority"),
                "status": item.get("status"),
                "title": item.get("title"),
                "summary": item.get("summary"),
                "next_safe_step": item.get("next_safe_step"),
            }
        )
    top = priorities[0] if priorities else {}
    return {
        "updated_at": payload.get("updated_at") or now_iso(),
        "focus": payload.get("focus") or "",
        "top_priority": top.get("title") or "",
        "top_priority_status": top.get("status") or "",
        "follow_up_windows": payload.get("follow_up_windows") or [],
        "priorities": priorities,
        "source_tasks": payload.get("source_tasks") or [],
        "paths": {
            "json": str(KIM_PRODUCT_BACKLOG_JSON),
            "markdown": str(KIM_PRODUCT_BACKLOG_MD),
            "spec": str(KIM_PRODUCT_BACKLOG_SPEC),
        },
    }


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
            timeout=KEYCHAIN_READ_TIMEOUT,
            check=True,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        if not required:
            return ""
        detail = (getattr(exc, "stderr", "") or getattr(exc, "stdout", "") or "").strip()
        if isinstance(exc, subprocess.TimeoutExpired):
            detail = f"Keychain no respondio en {KEYCHAIN_READ_TIMEOUT}s."
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
            timeout=KEYCHAIN_READ_TIMEOUT,
            check=True,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        if not required:
            return ""
        detail = (getattr(exc, "stderr", "") or getattr(exc, "stdout", "") or "").strip()
        if isinstance(exc, subprocess.TimeoutExpired):
            detail = f"Keychain no respondio en {KEYCHAIN_READ_TIMEOUT}s."
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


def security_secret_matches(provided, expected):
    provided_text = str(provided or "").strip()
    expected_text = str(expected or "").strip()
    if not provided_text or not expected_text:
        return False
    if hmac.compare_digest(provided_text, expected_text):
        return True
    provided_norm = normalize_security_text(provided_text)
    expected_norm = normalize_security_text(expected_text)
    if provided_norm and expected_norm and hmac.compare_digest(provided_norm, expected_norm):
        return True
    provided_compact = re.sub(r"\s+", "", provided_norm)
    expected_compact = re.sub(r"\s+", "", expected_norm)
    return bool(provided_compact and expected_compact and hmac.compare_digest(provided_compact, expected_compact))


def validate_bifrost_export_authorization(pin="", phrase=""):
    expected_pin = load_keychain_secret(SECURITY_PIN_KEYCHAIN_SERVICE, required=False)
    expected_phrase = load_keychain_secret(SECURITY_VOICE_PHRASE_KEYCHAIN_SERVICE, required=False)
    if not expected_pin or not expected_phrase:
        append_memory(
            "bifrost_export_blocked",
            {
                "reason": "missing_security_secrets",
                "has_pin": bool(expected_pin),
                "has_phrase": bool(expected_phrase),
            },
        )
        raise ValueError("Falta configurar PIN o frase de seguridad en Keychain.")
    if not security_secret_matches(pin, expected_pin) or not security_secret_matches(phrase, expected_phrase):
        append_memory("bifrost_export_denied", {"reason": "invalid_pin_or_phrase"})
        raise ValueError("PIN o frase de seguridad incorrectos.")
    return True


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


def multipart_escape(value):
    return str(value or "").replace("\\", "\\\\").replace('"', '\\"')


def openai_audio_transcribe(filename, data, content_type=""):
    if not data:
        raise RuntimeError("No hay audio para transcribir.")
    safe_name = pathlib.Path(filename or "whatsapp-audio.ogg").name
    mime = content_type or mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
    last_error = None
    for model in OPENAI_TRANSCRIBE_MODEL_CANDIDATES:
        boundary = "----kimliveaudio" + hashlib.sha256(f"{safe_name}{len(data)}{model}{now_iso()}".encode()).hexdigest()[:24]
        parts = [
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\n{model}\r\n".encode("utf-8"),
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"language\"\r\n\r\nes\r\n".encode("utf-8"),
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"response_format\"\r\n\r\njson\r\n".encode("utf-8"),
            (
                f"--{boundary}\r\n"
                f"Content-Disposition: form-data; name=\"file\"; filename=\"{multipart_escape(safe_name)}\"\r\n"
                f"Content-Type: {mime}\r\n\r\n"
            ).encode("utf-8")
            + data
            + b"\r\n",
            f"--{boundary}--\r\n".encode("utf-8"),
        ]
        request = urllib.request.Request(
            f"{OPENAI_API_BASE}/audio/transcriptions",
            data=b"".join(parts),
            headers={
                "Authorization": f"Bearer {load_openai_key()}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace") or "{}")
            transcript = str(payload.get("text") or "").strip()
            if transcript:
                return {"text": transcript, "model": model, "payload": payload}
            last_error = RuntimeError("Transcripcion vacia.")
        except Exception as exc:
            last_error = exc
    if last_error:
        raise last_error
    raise RuntimeError("No hay modelos de transcripcion configurados.")


def openai_audio_speech(text, voice=None):
    clean = re.sub(r"\s+", " ", text or "").strip()
    if not clean:
        raise RuntimeError("No hay texto para generar audio.")
    last_error = None
    selected_voice = voice or active_tts_voice()
    for model in OPENAI_SPEECH_MODEL_CANDIDATES:
        payload = {
            "model": model,
            "voice": selected_voice,
            "input": brief(clean, 1800),
            "response_format": "mp3",
            "speed": 0.95,
        }
        if not model.startswith("tts-1"):
            payload["instructions"] = active_tts_instructions()
        request = urllib.request.Request(
            f"{OPENAI_API_BASE}/audio/speech",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {load_openai_key()}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = response.read()
            if data:
                return {"data": data, "model": model, "voice": payload["voice"], "content_type": "audio/mpeg"}
            last_error = RuntimeError("Audio TTS vacio.")
        except Exception as exc:
            last_error = exc
    if last_error:
        raise last_error
    raise RuntimeError("No hay modelos TTS configurados.")


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


def file_knowledge_domain(analysis):
    haystack = normalize_security_text(
        " ".join(
            [
                str(analysis.get("filename") or ""),
                str(analysis.get("summary") or ""),
                " ".join(str(item.get("name") or item) for item in analysis.get("topics", []) if item),
            ]
        )
    )
    if "tesca" in haystack:
        return "tesca"
    rules = [
        ("tesca", {"tesca", "elements", "elemental", "compliance", "corporate", "arquitectura", "diagnostic", "diagnostico"}),
        ("ai_people", {"aipeople", "people", "kim", "employee", "asistente", "agente"}),
        ("ignis", {"ignis", "portfolio", "portafolio", "hedge", "venture", "financial"}),
        ("crm", {"cliente", "clientes", "pipedrive", "lead", "sales"}),
        ("legal", {"contrato", "contract", "nda", "legal", "jurisdiccion"}),
        ("operaciones", {"operacion", "operaciones", "process", "proceso", "clickup", "notion"}),
    ]
    best_domain = "general"
    best_score = 0
    for domain, keywords in rules:
        score = sum(1 for keyword in keywords if keyword in haystack)
        if score > best_score:
            best_domain = domain
            best_score = score
    return best_domain


def file_knowledge_card_paths(analysis):
    filename = str(analysis.get("filename") or "archivo")
    uploaded_at = str(analysis.get("uploaded_at") or today())
    uploaded_date = uploaded_at[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", uploaded_at) else today()
    domain = analysis.get("knowledge_domain") or file_knowledge_domain(analysis)
    sha = str(analysis.get("sha256") or "")[:8]
    slug = knowledge_slug(pathlib.Path(filename).stem)
    suffix = f"-{sha}" if sha else ""
    rel = pathlib.Path(domain) / "files" / f"{uploaded_date}-{slug}{suffix}.md"
    return MEMORY_KNOWLEDGE / rel, RUNTIME_KNOWLEDGE / rel


def file_knowledge_card_markdown(analysis, analysis_path=""):
    filename = str(analysis.get("filename") or "archivo")
    domain = analysis.get("knowledge_domain") or file_knowledge_domain(analysis)
    topics = analysis.get("topics") or []
    topic_names = [str(item.get("name") or item) for item in topics if item]
    summary = str(analysis.get("summary") or "").strip()
    text_preview = str(analysis.get("text_preview") or "").strip()
    source_path = str(analysis.get("stored_path") or "")
    return "\n".join(
        [
            f"# {pathlib.Path(filename).stem}",
            "",
            f"- Tipo: file_knowledge_card",
            f"- Dominio: {domain}",
            f"- Archivo original: {filename}",
            f"- Ruta fuente: {source_path}",
            f"- Analisis JSON: {analysis_path}",
            f"- Subido: {analysis.get('uploaded_at') or ''}",
            f"- Actualizado: {now_iso()}",
            f"- SHA256: {analysis.get('sha256') or ''}",
            f"- Extractor: {analysis.get('extractor') or ''}",
            f"- Caracteres procesados: {analysis.get('processed_chars') or analysis.get('extracted_chars') or 0}",
            f"- Temas: {', '.join(topic_names) or 'Sin clasificar'}",
            "",
            "## Regla De Uso",
            "",
            "Esta ficha es memoria durable de un archivo cargado. Kim debe consultarla antes de pedirle al doctor que repita informacion ya contenida en el archivo. La ruta fuente y el analisis JSON son la fuente primaria; esta ficha es una sintesis operacional.",
            "",
            "## Sintesis",
            "",
            summary or "Sin resumen disponible.",
            "",
            "## Extracto Base",
            "",
            brief(text_preview, 3000) or "Sin texto extraido disponible.",
            "",
        ]
    )


def load_file_knowledge_index():
    data = read_json_file_any([FILE_KNOWLEDGE_INDEX, RUNTIME_FILE_KNOWLEDGE_INDEX], {"files": []})
    if not isinstance(data, dict):
        data = {"files": []}
    data.setdefault("files", [])
    return data


def write_file_knowledge_markdown_index(index):
    entries = index.get("files", [])
    lines = [
        "# File Knowledge Index",
        "",
        f"- Updated: {index.get('updated_at') or now_iso()}",
        f"- Files: {len(entries)}",
        "",
        "Kim debe usar este indice para ubicar fichas durables de archivos cargados antes de pedir informacion repetida.",
        "",
    ]
    for item in sorted(entries, key=lambda row: (row.get("domain") or "", row.get("filename") or "")):
        lines.extend(
            [
                f"## {item.get('filename') or 'archivo'}",
                "",
                f"- Domain: {item.get('domain') or 'general'}",
                f"- Uploaded: {item.get('uploaded_at') or ''}",
                f"- Source: {item.get('stored_path') or ''}",
                f"- Card: {item.get('knowledge_card_path') or ''}",
                f"- Analysis: {item.get('analysis_path') or ''}",
                f"- Topics: {', '.join(item.get('topic_names') or []) or 'Sin clasificar'}",
                "",
                brief(item.get("summary") or "", 700),
                "",
            ]
        )
    text = "\n".join(lines).rstrip() + "\n"
    write_text_file_both(FILE_KNOWLEDGE_INDEX_MD, RUNTIME_FILE_KNOWLEDGE_INDEX_MD, text)


def update_file_knowledge_index(analysis, card_path="", analysis_path=""):
    index = load_file_knowledge_index()
    topics = analysis.get("topics") or []
    topic_names = [str(item.get("name") or item) for item in topics if item]
    entry = {
        "filename": analysis.get("filename") or "",
        "domain": analysis.get("knowledge_domain") or file_knowledge_domain(analysis),
        "uploaded_at": analysis.get("uploaded_at") or "",
        "stored_path": analysis.get("stored_path") or "",
        "analysis_path": str(analysis_path or analysis.get("analysis_path") or ""),
        "knowledge_card_path": str(card_path or analysis.get("knowledge_card_path") or ""),
        "sha256": analysis.get("sha256") or "",
        "summary": brief(analysis.get("summary") or "", 1200),
        "topic_names": topic_names,
        "processed_chars": analysis.get("processed_chars") or analysis.get("extracted_chars") or 0,
        "updated_at": now_iso(),
    }
    files = index.setdefault("files", [])
    entry_key = entry["sha256"] or entry["stored_path"] or entry["filename"]
    deduped = []
    replaced = False
    for item in files:
        item_key = item.get("sha256") or item.get("stored_path") or item.get("filename")
        if item_key == entry_key:
            deduped.append(entry)
            replaced = True
        else:
            deduped.append(item)
    if not replaced:
        deduped.append(entry)
    index["files"] = deduped
    by_domain = {}
    for item in deduped:
        by_domain.setdefault(item.get("domain") or "general", []).append(item.get("filename") or "archivo")
    index["by_domain"] = {key: sorted(value) for key, value in sorted(by_domain.items())}
    index["updated_at"] = now_iso()
    write_json_file_both(FILE_KNOWLEDGE_INDEX, RUNTIME_FILE_KNOWLEDGE_INDEX, index)
    write_file_knowledge_markdown_index(index)
    return entry


def store_file_knowledge_card(analysis, analysis_path=""):
    domain = file_knowledge_domain(analysis)
    analysis["knowledge_domain"] = domain
    primary_path, runtime_path = file_knowledge_card_paths(analysis)
    markdown = file_knowledge_card_markdown(analysis, analysis_path=str(analysis_path or ""))
    written = write_text_file_both(primary_path, runtime_path, markdown)
    card_path = written[0] if written else str(primary_path)
    analysis["knowledge_card_path"] = card_path
    update_file_knowledge_index(analysis, card_path=card_path, analysis_path=str(analysis_path or ""))
    return card_path


def load_file_knowledge_entries(limit=8):
    index = load_file_knowledge_index()
    files = index.get("files", [])
    if not isinstance(files, list):
        return []
    return files[-limit:]


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


def version_memory_snapshot():
    lines = [
        f"Version viva actual confirmada por backend: {APP_VERSION}.",
        "Si memoria vieja menciona 1.5.43, 1.5.45 u otra anterior, tratarla como hito historico y no como estado vigente.",
        "No responder con una version mas baja si el backend ya expone una version mas nueva.",
        "Hitos confirmados:",
    ]
    for version, note in VERSION_MEMORY_BASELINE_NOTES:
        lines.append(f"- v{version}: {note}")
    return "\n".join(lines)


def memory_analytics():
    memory_files = count_tree_files(MEMORY_ROOT) + count_tree_files(RUNTIME_MEMORY_ROOT)
    docs_files = count_tree_files(BIFROST / "docs")
    context_files = count_tree_files(MEMORY_CONTEXT_DIR) + count_tree_files(RUNTIME_CONTEXT)
    upload_entries = load_upload_entries()
    file_knowledge_entries = load_file_knowledge_entries(limit=5000)
    call_entries = load_call_entries()
    corpus_parts = []
    for paths in [
        [CONTEXT_MEMORY, RUNTIME_CONTEXT / "kim_context.md"],
        [CLICKUP_TASKS_MARKDOWN, RUNTIME_CLICKUP_TASKS_MARKDOWN],
        [BIFROST / "README.md"],
        [BIFROST / "docs" / "operating_model.md"],
        [MULTITENANT_AGENT_PLAN, RUNTIME_MULTITENANT_AGENT_PLAN],
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
        "file_knowledge_count": len(file_knowledge_entries),
        "call_count": len(load_call_entries(limit=5000)),
        "topics": topics,
        "principles": extract_principles(),
        "recent_calls": call_entries,
        "recent_uploads": upload_entries,
        "recent_file_knowledge": file_knowledge_entries[-8:],
        "tracked_files": [
            item for item in [
                file_stats(CONTEXT_MEMORY),
                file_stats(CLICKUP_TASKS_MARKDOWN),
                file_stats(BIFROST / "README.md"),
                file_stats(BIFROST / "docs" / "operating_model.md"),
                file_stats(MULTITENANT_AGENT_PLAN),
            ] if item
        ],
    }
    write_json_file_any([MEMORY_ANALYTICS, RUNTIME_MEMORY_ANALYTICS], payload)
    return payload


def save_call_record(body):
    session_id = re.sub(r"[^A-Za-z0-9_-]+", "-", body.get("session_id") or f"CALL-{today()}")
    text = (body.get("text") or "").strip()
    started_at = body.get("started_at") or now_iso()
    call_date = str(body.get("date") or started_at or today())[:10]
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", call_date):
        call_date = today()
    title = (body.get("title") or "Kim Live call").strip()[:120]
    topics = detect_topics(text)
    summary = local_extract_summary(text, title, limit=1400)
    related_files = body.get("uploaded_files") or []
    research_sources = body.get("research_sources") or load_sources_for_session(session_id)
    existing_entries = load_call_entries(limit=5000)
    existing_entry = next((item for item in reversed(existing_entries) if item.get("session_id") == session_id), None)
    known_sessions = {item.get("session_id") for item in existing_entries if item.get("session_id")}
    call_number = existing_entry.get("call_number") if existing_entry else len(known_sessions) + 1
    calls_dir = MEMORY_CALLS / call_date
    try:
        calls_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        calls_dir = RUNTIME_CALLS / call_date
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
    try:
        call_path.write_text("\n".join(content), encoding="utf-8")
    except OSError as exc:
        if getattr(exc, "errno", None) not in {1, 13, 30}:
            raise
        calls_dir = RUNTIME_CALLS / call_date
        calls_dir.mkdir(parents=True, exist_ok=True)
        call_path = calls_dir / f"{session_id}.md"
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
    upsert_jsonl_any([CALL_INDEX, RUNTIME_CALL_INDEX], entry)
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
    try:
        store_file_knowledge_card(analysis, analysis_path=analysis_path)
    except Exception as exc:
        analysis["knowledge_error"] = brief(str(exc), 700)
    write_json_file_any([analysis_path, RUNTIME_UPLOADS / today() / analysis_path.name], analysis)
    index_path = UPLOAD_INDEX
    try:
        index = read_json_file(index_path, {"files": []})
        index.setdefault("files", []).append({**analysis, "analysis_path": str(analysis_path)})
        write_json_file(index_path, index)
    except (PermissionError, OSError):
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


def transcript_from_markdown(markdown):
    if "## Transcript" in markdown:
        return markdown.split("## Transcript", 1)[1].strip()
    return markdown.strip()


def load_conversation(session_id):
    matches = [item for item in load_call_entries(limit=5000) if item.get("session_id") == session_id]
    if not matches:
        raise ValueError("No encontre esa conversacion en memoria.")
    return conversation_record_from_entry(matches[-1])


def discover_call_memory_entries(limit=800):
    entries = []
    seen_paths = set()
    seen_keys = set()
    for item in load_call_entries(limit=10000):
        path = str(item.get("path") or "")
        key = path or str(item.get("session_id") or "")
        if key and key in seen_keys:
            continue
        if key:
            seen_keys.add(key)
        if path:
            seen_paths.add(path)
        entries.append(item)
    files = []
    for root in [MEMORY_CALLS, RUNTIME_CALLS]:
        try:
            files.extend(root.rglob("*.md"))
        except (FileNotFoundError, PermissionError, OSError):
            continue
    files = sorted(files, key=lambda item: item.stat().st_mtime if item.exists() else 0, reverse=True)
    for path in files[:limit]:
        path_str = str(path)
        if path_str in seen_paths:
            continue
        seen_paths.add(path_str)
        session_id = path.stem
        try:
            markdown = path.read_text(encoding="utf-8")
        except (FileNotFoundError, PermissionError, OSError):
            markdown = ""
        title = session_id
        if markdown.startswith("# "):
            title = markdown.splitlines()[0].lstrip("# ").strip() or session_id
        entries.append(
            {
                "session_id": session_id,
                "title": title,
                "path": path_str,
                "saved_at": dt.datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
                "summary": "",
                "topics": [],
            }
        )
    return entries


def memory_search_terms(query):
    normalized = normalize_security_text(query)
    return [term for term in normalized.split() if len(term) >= 3]


def score_memory_text(query, title="", summary="", transcript=""):
    phrase = normalize_security_text(query)
    terms = memory_search_terms(query)
    haystack = normalize_security_text(" ".join([title or "", summary or "", transcript or ""]))
    if not phrase and not terms:
        return 1
    score = 0
    if phrase and phrase in haystack:
        score += 12
    title_norm = normalize_security_text(title)
    summary_norm = normalize_security_text(summary)
    for term in terms:
        if term in title_norm:
            score += 5
        if term in summary_norm:
            score += 3
        if term in haystack:
            score += 1
    return score


def transcript_snippet(transcript, query, max_chars=1600):
    text = (transcript or "").strip()
    if len(text) <= max_chars:
        return text
    lower = text.lower()
    candidates = []
    query_lower = str(query or "").strip().lower()
    if query_lower:
        candidates.append(query_lower)
    candidates.extend(re.findall(r"[A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ]{3,}", str(query or "")))
    idx = -1
    for candidate in candidates:
        idx = lower.find(candidate.lower())
        if idx >= 0:
            break
    if idx < 0:
        idx = 0
    start = max(0, idx - max_chars // 3)
    end = min(len(text), start + max_chars)
    start = max(0, end - max_chars)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    return prefix + text[start:end].strip() + suffix


def bifrost_search_roots():
    return [
        MEMORY_KNOWLEDGE,
        MEMORY_CONTEXT_DIR,
        MEMORY_CALLS,
        MEMORY_DOCUMENTS,
        PERSON_CONTEXT_DIR,
        MEMORY_ROOT / "portfolios",
        CRM_ROOT,
        BIFROST / "docs",
        RUNTIME_KNOWLEDGE,
        RUNTIME_CONTEXT,
        RUNTIME_CALLS,
        RUNTIME_DOCUMENTS,
        RUNTIME_PERSON_CONTEXT_DIR,
        RUNTIME_MEMORY_ROOT / "portfolios",
    ]


BIFROST_SEARCH_SUFFIXES = {".md", ".txt", ".json", ".jsonl", ".csv", ".tsv"}
BIFROST_SEARCH_MAX_BYTES = 1_400_000


def iter_bifrost_search_files():
    seen = set()
    for root in bifrost_search_roots():
        try:
            if not root.exists():
                continue
            paths = root.rglob("*") if root.is_dir() else [root]
            for path in paths:
                try:
                    if not path.is_file():
                        continue
                    if path.suffix.lower() not in BIFROST_SEARCH_SUFFIXES:
                        continue
                    path_key = str(path.resolve())
                    if path_key in seen:
                        continue
                    size = path.stat().st_size
                    if size <= 0 or size > BIFROST_SEARCH_MAX_BYTES:
                        continue
                    seen.add(path_key)
                    yield path, size
                except (FileNotFoundError, PermissionError, OSError):
                    continue
        except (FileNotFoundError, PermissionError, OSError):
            continue


def score_bifrost_file(query, path, text):
    phrase = normalize_security_text(query)
    terms = memory_search_terms(query)
    path_norm = normalize_security_text(str(path))
    text_norm = normalize_security_text(text)
    if not phrase and not terms:
        return 1
    score = 0
    if phrase and phrase in path_norm:
        score += 12
    if phrase and phrase in text_norm:
        score += 8
    for term in terms:
        if term in path_norm:
            score += 5
        if term in text_norm:
            score += 1
    portfolio_terms = {"eli", "portafolio", "portfolio", "ignis", "usdt"}
    if any(term in terms for term in portfolio_terms) and "portfolio" in path_norm:
        score += 4
    return score


def search_bifrost_files(query="", limit=8, max_chars=1600):
    query = str(query or "").strip()
    limit = max(1, min(int(limit or 8), 20))
    max_chars = max(400, min(int(max_chars or 1600), 6000))
    results = []
    for path, size in iter_bifrost_search_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except (FileNotFoundError, PermissionError, OSError):
            continue
        score = score_bifrost_file(query, path, text)
        if query and score <= 0:
            continue
        title = path.stem
        if text.startswith("# "):
            title = text.splitlines()[0].lstrip("# ").strip() or title
        results.append(
            {
                "path": str(path),
                "title": title,
                "score": score,
                "bytes": size,
                "updated_at": dt.datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
                "snippet": transcript_snippet(text, query, max_chars=max_chars),
            }
        )
    results = sorted(results, key=lambda item: (item.get("score", 0), item.get("updated_at") or ""), reverse=True)
    payload = {
        "ok": True,
        "provider": "memory",
        "action": "search_bifrost_files",
        "query": query,
        "count": len(results[:limit]),
        "results": results[:limit],
    }
    write_json_file_any([BIFROST_FILE_INDEX, RUNTIME_BIFROST_FILE_INDEX], {
        "updated_at": now_iso(),
        "query": query,
        "result_count": payload["count"],
        "top_paths": [item.get("path") for item in payload["results"]],
    })
    return payload


def search_memory_transcripts(query="", session_id="", limit=6, max_chars=1600):
    query = str(query or "").strip()
    session_id = str(session_id or "").strip()
    limit = max(1, min(int(limit or 6), 20))
    max_chars = max(400, min(int(max_chars or 1600), 6000))
    file_payload = search_bifrost_files(query, limit=max(6, limit), max_chars=max_chars)
    if session_id:
        record = load_conversation(session_id)
        transcript = record.get("transcript") or transcript_from_markdown(record.get("markdown", ""))
        return {
            "ok": True,
            "provider": "memory",
            "action": "search_transcripts",
            "query": query,
            "count": 1,
            "results": [
                {
                    "session_id": record.get("session_id"),
                    "title": record.get("title"),
                    "saved_at": record.get("saved_at"),
                    "path": record.get("path"),
                    "score": 999,
                    "summary": record.get("summary", ""),
                    "snippet": transcript_snippet(transcript, query, max_chars=max_chars),
                    "chars": len(transcript),
                }
            ],
            "file_count": file_payload.get("count", 0),
            "file_results": file_payload.get("results", []),
            "rule": "Usa transcript y file_results como fuentes primarias; los resumenes son derivados.",
        }
    results = []
    for entry in discover_call_memory_entries():
        record = conversation_record_from_entry(entry)
        transcript = record.get("transcript") or transcript_from_markdown(record.get("markdown", ""))
        if not transcript:
            continue
        score = score_memory_text(query, record.get("title", ""), record.get("summary", ""), transcript)
        if query and score <= 0:
            continue
        results.append(
            {
                "session_id": record.get("session_id"),
                "title": record.get("title"),
                "saved_at": record.get("saved_at"),
                "path": record.get("path"),
                "score": score,
                "summary": record.get("summary", ""),
                "snippet": transcript_snippet(transcript, query, max_chars=max_chars),
                "chars": len(transcript),
            }
        )
    results = sorted(results, key=lambda item: (item.get("score", 0), item.get("saved_at") or ""), reverse=True)
    payload = {
        "ok": True,
        "provider": "memory",
        "action": "search_transcripts",
        "query": query,
        "count": len(results[:limit]),
        "results": results[:limit],
        "file_count": file_payload.get("count", 0),
        "file_results": file_payload.get("results", []),
        "rule": "Usa estos snippets literales y file_results de BIFROST como fuente primaria; los resumenes son derivados.",
    }
    append_memory("memory_transcript_search", {"query": query, "count": payload["count"], "top_paths": [item.get("path") for item in payload["results"][:3]]})
    return payload


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


def clickup_inventory_payload():
    for path in [CLICKUP_INVENTORY, RUNTIME_CLICKUP_INVENTORY, RUNTIME_CONTEXT / "clickup_inventory.json"]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload, path
        except (FileNotFoundError, PermissionError, OSError, json.JSONDecodeError):
            continue
    return {}, None


def clickup_inventory_rows():
    payload, source = clickup_inventory_payload()
    rows = []
    for workspace in payload.get("workspaces") or payload.get("teams") or []:
        team_name = workspace.get("name") or ""
        team_id = workspace.get("id") or ""
        for space in workspace.get("spaces", []) or []:
            space_name = space.get("name") or ""
            space_id = space.get("id") or ""
            for item in space.get("lists", []) or []:
                rows.append(
                    {
                        "team_name": team_name,
                        "team_id": team_id,
                        "space_name": space_name,
                        "space_id": space_id,
                        "folder_name": item.get("folder_name") or item.get("folder") or "",
                        "folder_id": item.get("folder_id") or "",
                        "list_name": item.get("name") or "",
                        "list_id": item.get("id") or "",
                        "source": str(source) if source else "",
                    }
                )
    return rows


def clickup_operation_catalog():
    rows = clickup_inventory_rows()

    def find(team="", space="", list_name=""):
        team_norm = normalize_security_text(team)
        space_norm = normalize_security_text(space)
        list_norm = normalize_security_text(list_name)
        for row in rows:
            if team_norm and normalize_security_text(row.get("team_name")) != team_norm:
                continue
            if space_norm and normalize_security_text(row.get("space_name")) != space_norm:
                continue
            if list_norm and normalize_security_text(row.get("list_name")) != list_norm:
                continue
            return row
        return {}

    routes = [
        {
            "id": "kim_product_system",
            "label": "Kim Live / AI People producto",
            "keywords": ["kim", "kim live", "codex", "bifrost", "api", "bug", "error", "frontend", "runtime", "github", "memoria", "contexto", "telegram", "voice", "voz", "twilio"],
            "row": find("Ai people", "Products", "Kim Live"),
            "rule": "bugs, mejoras de Kim, integraciones, memoria, telefonia y producto AI People.",
        },
        {
            "id": "ai_spirits_product",
            "label": "AI Spirits",
            "keywords": ["ai spirits", "spirit", "agente visual", "avatar", "video", "expresarse"],
            "row": find("Ai people", "Products", "AI Spirits"),
            "rule": "producto AI Spirits o expresion visual de agentes.",
        },
        {
            "id": "client_followup",
            "label": "AI People Client Follow-up",
            "keywords": ["cliente", "prospecto", "follow up", "seguimiento", "pipedrive", "crm", "venta", "deal", "trato", "llamada cliente", "isaac", "inversionista", "oficina"],
            "row": find("Ai people", "Client Follow-up", "PASIV"),
            "rule": "seguimiento comercial cuando no hay una lista de cliente mas especifica.",
        },
        {
            "id": "ignis_investor",
            "label": "Ignis investor follow-up",
            "keywords": ["ignis", "portafolio", "portfolio", "eli", "inversion", "inversión", "crypto", "usdt", "khalil", "orden", "credito", "crédito"],
            "row": find("Ignis Stock Financials", "Investor follow-up", "Khalil"),
            "rule": "seguimiento comercial de inversiones; el ledger local sigue siendo fuente primaria del portafolio.",
        },
        {
            "id": "neorgana_commercial",
            "label": "Tesca / Neorgana Commercial",
            "keywords": ["neorgana", "tesca", "comercial", "propuesta", "cliente tesca"],
            "row": find("Tesca Elements", "Neorgana", "Commercial"),
            "rule": "pendientes comerciales de Neorgana/Tesca.",
        },
        {
            "id": "tesca_operations",
            "label": "Tesca operations",
            "keywords": ["aifa", "seo", "webpage", "campaña", "campaign", "dr ahmed", "taskspur"],
            "row": find("Tesca Elements", "Quotation & Kick Off projects", "AIFA Cybersecurity"),
            "rule": "operacion de proyectos Tesca cuando el texto no da una lista exacta.",
        },
        {
            "id": "personal_scheduled",
            "label": "Dr Y scheduled",
            "keywords": ["personal", "shabat", "recordatorio", "agenda", "casa", "familia", "doctor yoshua mexico"],
            "row": find("Dr Y", "Personal Life", "Scheduled"),
            "rule": "temas personales programados del doctor.",
        },
    ]
    fallback = find("Ai people", "Products", "Kim Live") or find("Tesca Elements", "Neorgana", "Commercial") or (rows[0] if rows else {})
    return {"routes": routes, "fallback": fallback, "rows": rows}


def clickup_route_from_context(parameters):
    data = parameters or {}
    text = " ".join(
        str(first_value(data, key, default="") or "")
        for key in ["name", "title", "subject", "task_name", "description", "body", "content", "message", "notes", "summary", "text", "space_name", "list_name", "company", "contact_name"]
    )
    text_norm = normalize_security_text(text)
    catalog = clickup_operation_catalog()
    for row in catalog.get("rows", []):
        list_norm = normalize_security_text(row.get("list_name"))
        space_norm = normalize_security_text(row.get("space_name"))
        if list_norm and len(list_norm) >= 4 and list_norm in text_norm:
            return {**row, "route_id": "explicit_list_match", "route_label": f"Lista mencionada: {row.get('list_name')}", "route_rule": "El texto menciono una lista/proyecto existente.", "score": 99}
        if space_norm and len(space_norm) >= 5 and space_norm in text_norm and row.get("list_id"):
            return {**row, "route_id": "explicit_space_match", "route_label": f"Space mencionado: {row.get('space_name')}", "route_rule": "El texto menciono un Space existente; se usa su primera lista disponible.", "score": 80}
    best = None
    best_score = 0
    for route in catalog.get("routes", []):
        score = sum(1 for keyword in route.get("keywords", []) if normalize_security_text(keyword) in text_norm)
        row = route.get("row") or {}
        if score > best_score and row.get("list_id"):
            best = route
            best_score = score
    if not best:
        best = {"id": "fallback", "label": "Fallback operativo", "row": catalog.get("fallback") or {}, "rule": "fallback seguro para no pedir IDs al doctor."}
    row = best.get("row") or {}
    return {**row, "route_id": best.get("id"), "route_label": best.get("label"), "route_rule": best.get("rule"), "score": best_score}


def clickup_apply_operational_defaults(parameters, force=False):
    data = dict(parameters or {})
    existing_list_id = str(data.get("list_id") or "").strip()
    existing_space = str(first_value(data, "space_name", "space", "workspace", "team_space", default="") or "").strip()
    existing_list = str(first_value(data, "list_name", "list", "target_list", default="") or "").strip()
    workspace_names = {normalize_security_text(row.get("team_name")) for row in clickup_inventory_rows() if row.get("team_name")}
    semantic_space_is_workspace = normalize_security_text(existing_space) in workspace_names
    should_route = force or not existing_list_id and (not existing_space or semantic_space_is_workspace or not existing_list)
    if not should_route:
        return data
    route = clickup_route_from_context(data)
    if not existing_list_id and route.get("list_id"):
        data["list_id"] = route["list_id"]
    if route.get("list_name") and (force or not existing_list or semantic_space_is_workspace):
        data["list_name"] = route["list_name"]
    if route.get("space_name") and (force or not existing_space or semantic_space_is_workspace):
        data["space_name"] = route["space_name"]
    if route.get("team_name") and not data.get("team_name"):
        data["team_name"] = route["team_name"]
    data["routing_note"] = (
        f"Ruta ClickUp automatica {route.get('route_id')}: {route.get('route_label')} -> "
        f"{route.get('team_name')} / {route.get('space_name')} / {route.get('list_name')}. "
        f"{route.get('route_rule')}"
    )
    return data


def write_clickup_operation_map_snapshot():
    catalog = clickup_operation_catalog()
    payload = {
        "updated_at": now_iso(),
        "purpose": "Mapa operativo para convertir voice-of-customer en estructura ClickUp sin pedir IDs.",
        "rule": "BIFROST/CRM conservan contexto; ClickUp recibe tareas ejecutables; Pipedrive recibe relaciones comerciales.",
        "routes": [
            {
                "id": route.get("id"),
                "label": route.get("label"),
                "rule": route.get("rule"),
                "keywords": route.get("keywords"),
                "team_name": (route.get("row") or {}).get("team_name"),
                "space_name": (route.get("row") or {}).get("space_name"),
                "list_name": (route.get("row") or {}).get("list_name"),
                "list_id": (route.get("row") or {}).get("list_id"),
            }
            for route in catalog.get("routes", [])
        ],
        "fallback": catalog.get("fallback") or {},
        "available_lists": catalog.get("rows")[:200],
    }
    written = write_json_file_both(CLICKUP_OPERATION_MAP, RUNTIME_CLICKUP_OPERATION_MAP, payload)
    return written[0] if written else ""


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
    zoom_status_data = zoom_status(live=False)
    google_maps_status_data = google_maps_status(live=False)
    gmail_configured = gmail_oauth_configured()
    gmail_has_refresh = gmail_authorized()
    hostinger_status = hostinger_mail_status(live=False)
    backlog = kim_product_backlog_summary()
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
                "sync_persons",
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
        "google_maps": google_maps_status_data,
        "zoom": zoom_status_data,
        "hostinger_mail": hostinger_status,
        "twilio": twilio_status(live=False),
        "scheduler": {
            "configured": True,
            "runs_inside": "Kim Live launchd service",
            "default_timezone": DEFAULT_SCHEDULER_TIMEZONE,
            "write_requires_confirmation": True,
            "capabilities": ["schedule_action", "list_schedules", "cancel_schedule"],
        },
        "crm": crm_status(),
        "security": security_status(),
        "product_backlog": backlog,
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
        status["zoom"].update(zoom_status(live=True))
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


def google_maps_api_key(required=True):
    key = load_keychain_secret(GOOGLE_MAPS_API_KEYCHAIN_SERVICE, required=False)
    if key:
        return key.strip()
    credential_paths = [
        BIFROST / "APIs Cred" / "maps api.rtf",
        BIFROST / "APIs Cred" / "google maps api.rtf",
        BIFROST / "APIs Cred" / "google_maps_api_key.txt",
    ]
    for path in credential_paths:
        if not path.exists():
            continue
        try:
            raw = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        match = re.search(r"(AIza[0-9A-Za-z_\-]{20,})", raw)
        if match:
            return match.group(1).strip()
    if required:
        raise ValueError(f"No encontre API key de Google Maps en Keychain ({GOOGLE_MAPS_API_KEYCHAIN_SERVICE}) ni en BIFROST/APIs Cred.")
    return ""


def google_maps_status(live=False):
    configured = bool(google_maps_api_key(required=False))
    status = {
        "ok": True,
        "configured": configured,
        "provider": "google_maps",
        "write_requires_confirmation": False,
        "billing_note": "Las consultas de Google Maps pueden generar cargos pequenos segun la cuenta/proyecto.",
        "keychain_service": GOOGLE_MAPS_API_KEYCHAIN_SERVICE,
        "capabilities": [
            "status",
            "validate_key",
            "find_place",
            "text_search",
            "geocode",
            "reverse_geocode",
            "route_distance",
            "timezone",
        ],
        "required_google_apis": [
            "Places API (New)",
            "Geocoding API",
            "Routes API",
            "Time Zone API",
        ],
    }
    if live and configured:
        try:
            probe = google_maps_geocode({"address": "Mexico City, Mexico"})
            status["live_ok"] = bool(probe.get("ok"))
            status["live_probe"] = {
                "formatted_address": ((probe.get("results") or [{}])[0]).get("formatted_address", ""),
                "place_id": ((probe.get("results") or [{}])[0]).get("place_id", ""),
            }
        except Exception as exc:
            status["live_ok"] = False
            status["live_error"] = brief(str(exc), 360)
    return status


def google_maps_log(action, parameters, result):
    record = {
        "at": now_iso(),
        "provider": "google_maps",
        "action": action,
        "parameters": sanitize_for_log(parameters),
        "ok": bool(result.get("ok")),
        "summary": brief(str(result.get("summary") or result.get("message") or ""), 800),
    }
    append_jsonl_any([GOOGLE_MAPS_LOG, RUNTIME_GOOGLE_MAPS_LOG], record)
    append_memory("google_maps_action", record)
    return record


def google_maps_location_dict(raw):
    if not isinstance(raw, dict):
        return None
    lat = raw.get("lat")
    lng = raw.get("lng")
    if lat is None or lng is None:
        lat = (raw.get("latitude") if raw.get("latitude") is not None else raw.get("lat"))
        lng = (raw.get("longitude") if raw.get("longitude") is not None else raw.get("lng"))
    if lat is None or lng is None:
        return None
    return {"latitude": float(lat), "longitude": float(lng)}


def google_maps_parse_latlng(value):
    if isinstance(value, dict):
        return google_maps_location_dict(value)
    text = str(value or "").strip()
    if not text:
        return None
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)", text)
    if not match:
        return None
    return {"latitude": float(match.group(1)), "longitude": float(match.group(2))}


def google_maps_place_item(place):
    display_name = place.get("displayName") or {}
    location = place.get("location") or {}
    return {
        "id": place.get("id", ""),
        "place_id": place.get("id", ""),
        "name": display_name.get("text") or place.get("name", ""),
        "formatted_address": place.get("formattedAddress", ""),
        "location": google_maps_location_dict(location),
        "google_maps_uri": place.get("googleMapsUri", ""),
        "website_uri": place.get("websiteUri", ""),
        "phone": place.get("nationalPhoneNumber") or place.get("internationalPhoneNumber") or "",
        "rating": place.get("rating"),
        "user_rating_count": place.get("userRatingCount"),
        "business_status": place.get("businessStatus", ""),
        "types": place.get("types") or [],
    }


def google_maps_find_place(parameters=None):
    parameters = dict(parameters or {})
    query = str(first_value(parameters, "query", "text", "q", "place", "business", "name", "lugar", default="") or "").strip()
    if not query:
        raise ValueError("Falta query/text para buscar lugares en Google Maps.")
    max_results = int(float(first_value(parameters, "max_results", "limit", default=5) or 5))
    payload = {
        "textQuery": query,
        "languageCode": str(first_value(parameters, "language", "language_code", default="es") or "es"),
        "maxResultCount": max(1, min(max_results, 20)),
    }
    location = google_maps_parse_latlng(first_value(parameters, "location", "near", "latlng", default=""))
    if location:
        radius = float(first_value(parameters, "radius_meters", "radius", default=5000) or 5000)
        payload["locationBias"] = {"circle": {"center": location, "radius": max(1.0, min(radius, 50000.0))}}
    region = str(first_value(parameters, "region_code", "region", "country", default="") or "").strip().upper()
    if region:
        payload["regionCode"] = region
    field_mask = ",".join(
        [
            "places.id",
            "places.displayName",
            "places.formattedAddress",
            "places.location",
            "places.googleMapsUri",
            "places.websiteUri",
            "places.nationalPhoneNumber",
            "places.internationalPhoneNumber",
            "places.rating",
            "places.userRatingCount",
            "places.businessStatus",
            "places.types",
        ]
    )
    response = api_json_request(
        GOOGLE_PLACES_API_BASE,
        "/v1/places:searchText",
        {
            "X-Goog-Api-Key": google_maps_api_key(),
            "X-Goog-FieldMask": field_mask,
        },
        method="POST",
        payload=payload,
        timeout=30,
    )
    places = [google_maps_place_item(place) for place in response.get("places") or []]
    return {
        "ok": True,
        "provider": "google_maps",
        "action": "find_place",
        "query": query,
        "count": len(places),
        "places": places,
        "summary": f"Google Maps encontro {len(places)} resultado(s) para: {query}.",
    }


def google_maps_geocode(parameters=None):
    parameters = dict(parameters or {})
    address = str(first_value(parameters, "address", "query", "q", "direccion", "dirección", default="") or "").strip()
    latlng = google_maps_parse_latlng(first_value(parameters, "latlng", "location", default=""))
    if not address and not latlng:
        raise ValueError("Falta address o latlng para geocoding.")
    params = {
        "key": google_maps_api_key(),
        "language": str(first_value(parameters, "language", default="es") or "es"),
    }
    action = "reverse_geocode" if latlng and not address else "geocode"
    if action == "reverse_geocode":
        params["latlng"] = f"{latlng['latitude']},{latlng['longitude']}"
    else:
        params["address"] = address
        region = str(first_value(parameters, "region", "country", default="") or "").strip()
        if region:
            params["region"] = region
    response = api_json_request(GOOGLE_MAPS_GEOCODING_BASE, "/maps/api/geocode/json", {}, params=params, timeout=30)
    status = response.get("status")
    results = []
    for item in response.get("results") or []:
        geometry = item.get("geometry") or {}
        location = geometry.get("location") or {}
        results.append(
            {
                "formatted_address": item.get("formatted_address", ""),
                "place_id": item.get("place_id", ""),
                "location": {"latitude": location.get("lat"), "longitude": location.get("lng")},
                "location_type": geometry.get("location_type", ""),
                "types": item.get("types") or [],
            }
        )
    return {
        "ok": status == "OK",
        "provider": "google_maps",
        "action": action,
        "status": status,
        "error_message": response.get("error_message", ""),
        "results": results,
        "summary": f"Geocoding {status}; {len(results)} resultado(s).",
    }


def google_maps_route_distance(parameters=None):
    parameters = dict(parameters or {})
    origin = str(first_value(parameters, "origin", "from", "origen", default="") or "").strip()
    destination = str(first_value(parameters, "destination", "to", "destino", default="") or "").strip()
    if not origin or not destination:
        raise ValueError("Faltan origin y destination para calcular ruta.")
    mode = str(first_value(parameters, "travel_mode", "mode", "modo", default="DRIVE") or "DRIVE").strip().upper()
    mode_map = {"DRIVING": "DRIVE", "CAR": "DRIVE", "WALKING": "WALK", "BICYCLING": "BICYCLE", "TRANSIT": "TRANSIT"}
    mode = mode_map.get(mode, mode)
    payload = {
        "origin": {"address": origin},
        "destination": {"address": destination},
        "travelMode": mode if mode in {"DRIVE", "WALK", "BICYCLE", "TRANSIT", "TWO_WHEELER"} else "DRIVE",
        "languageCode": str(first_value(parameters, "language", default="es") or "es"),
        "units": str(first_value(parameters, "units", default="METRIC") or "METRIC").upper(),
    }
    if payload["travelMode"] == "DRIVE":
        payload["routingPreference"] = str(first_value(parameters, "routing_preference", default="TRAFFIC_AWARE") or "TRAFFIC_AWARE").upper()
    response = api_json_request(
        GOOGLE_ROUTES_API_BASE,
        "/directions/v2:computeRoutes",
        {
            "X-Goog-Api-Key": google_maps_api_key(),
            "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.staticDuration,routes.description,routes.localizedValues,routes.routeLabels,routes.warnings",
        },
        method="POST",
        payload=payload,
        timeout=35,
    )
    routes = []
    for route in response.get("routes") or []:
        distance_m = route.get("distanceMeters")
        duration_seconds = None
        duration = str(route.get("duration") or "")
        if duration.endswith("s"):
            try:
                duration_seconds = float(duration[:-1])
            except ValueError:
                duration_seconds = None
        routes.append(
            {
                "distance_meters": distance_m,
                "distance_km": round_opt((float(distance_m) / 1000) if distance_m is not None else None, 2),
                "duration": duration,
                "duration_minutes": round_opt((duration_seconds / 60) if duration_seconds is not None else None, 1),
                "static_duration": route.get("staticDuration", ""),
                "description": route.get("description", ""),
                "localized_values": route.get("localizedValues") or {},
                "route_labels": route.get("routeLabels") or [],
                "warnings": route.get("warnings") or [],
            }
        )
    best = routes[0] if routes else {}
    return {
        "ok": bool(routes),
        "provider": "google_maps",
        "action": "route_distance",
        "origin": origin,
        "destination": destination,
        "travel_mode": payload["travelMode"],
        "routes": routes,
        "summary": (
            f"Ruta {origin} -> {destination}: {best.get('distance_km')} km, "
            f"{best.get('duration_minutes')} min aprox."
        )
        if best
        else "Google Routes no devolvio rutas.",
    }


def google_maps_timezone(parameters=None):
    parameters = dict(parameters or {})
    location = google_maps_parse_latlng(first_value(parameters, "location", "latlng", default=""))
    if not location:
        address = str(first_value(parameters, "address", "query", "q", default="") or "").strip()
        if not address:
            raise ValueError("Falta location/latlng o address para consultar timezone.")
        geocoded = google_maps_geocode({"address": address})
        first = (geocoded.get("results") or [{}])[0]
        location = google_maps_location_dict(first.get("location") or {})
    timestamp = int(float(first_value(parameters, "timestamp", "time", default=time.time()) or time.time()))
    response = api_json_request(
        GOOGLE_MAPS_GEOCODING_BASE,
        "/maps/api/timezone/json",
        {},
        params={
            "key": google_maps_api_key(),
            "location": f"{location['latitude']},{location['longitude']}",
            "timestamp": timestamp,
            "language": str(first_value(parameters, "language", default="es") or "es"),
        },
        timeout=30,
    )
    return {
        "ok": response.get("status") == "OK",
        "provider": "google_maps",
        "action": "timezone",
        "status": response.get("status"),
        "error_message": response.get("errorMessage") or response.get("error_message", ""),
        "location": location,
        "time_zone_id": response.get("timeZoneId", ""),
        "time_zone_name": response.get("timeZoneName", ""),
        "raw_offset": response.get("rawOffset"),
        "dst_offset": response.get("dstOffset"),
        "summary": f"Timezone: {response.get('timeZoneId', '')} {response.get('timeZoneName', '')}".strip(),
    }


def run_google_maps_bridge(action, parameters=None, confirm=False):
    action = (action or "status").strip().lower()
    parameters = dict(parameters or {})
    if action in {"status", "config", "health"}:
        result = google_maps_status(live=boolish(first_value(parameters, "live", "test", default=False)))
    elif action in {"validate_key", "test", "self_test"}:
        result = google_maps_status(live=True)
    elif action in {"find_place", "text_search", "search_place", "places_search", "buscar_lugar", "buscar_empresa"}:
        result = google_maps_find_place(parameters)
    elif action in {"geocode", "geocode_address", "address_lookup", "validar_direccion", "validar_dirección"}:
        result = google_maps_geocode(parameters)
    elif action in {"reverse_geocode", "reverse_address"}:
        result = google_maps_geocode({**parameters, "address": ""})
    elif action in {"route_distance", "route", "directions", "distance", "distancia", "ruta"}:
        result = google_maps_route_distance(parameters)
    elif action in {"timezone", "time_zone", "zona_horaria"}:
        result = google_maps_timezone(parameters)
    else:
        raise ValueError("Accion Google Maps no soportada. Usa status, validate_key, find_place, geocode, route_distance o timezone.")
    result["log"] = google_maps_log(action, parameters, result)
    return result


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


def zoom_client_configured():
    return bool(load_keychain_secret(ZOOM_CLIENT_ID_KEYCHAIN_SERVICE, required=False)) and bool(
        load_keychain_secret(ZOOM_CLIENT_SECRET_KEYCHAIN_SERVICE, required=False)
    )


def zoom_s2s_configured():
    return zoom_client_configured() and bool(load_keychain_secret(ZOOM_ACCOUNT_ID_KEYCHAIN_SERVICE, required=False))


def zoom_authorized():
    return bool(load_keychain_secret(ZOOM_REFRESH_TOKEN_KEYCHAIN_SERVICE, required=False))


def zoom_api_base_from_token_payload(payload=None):
    raw = str((payload or {}).get("api_url") or "https://api.zoom.us").rstrip("/")
    return raw if raw.endswith("/v2") else raw + "/v2"


def zoom_token_request(payload):
    client_id = load_keychain_secret(ZOOM_CLIENT_ID_KEYCHAIN_SERVICE)
    client_secret = load_keychain_secret(ZOOM_CLIENT_SECRET_KEYCHAIN_SERVICE)
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
    return form_json_request(
        "https://zoom.us",
        "/oauth/token",
        {"Authorization": f"Basic {basic}", "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
        payload=payload,
        timeout=30,
    )


def zoom_access_token(force=False):
    now_ts = time.time()
    cached = ZOOM_TOKEN_CACHE.get("access_token") or ""
    if cached and not force and float(ZOOM_TOKEN_CACHE.get("expires_at") or 0) > now_ts + 60:
        return {
            "access_token": cached,
            "api_url": ZOOM_TOKEN_CACHE.get("api_url") or ZOOM_API_BASE,
            "scope": ZOOM_TOKEN_CACHE.get("scope") or "",
            "mode": ZOOM_TOKEN_CACHE.get("mode") or "unknown",
            "cached": True,
        }
    refresh_token = load_keychain_secret(ZOOM_REFRESH_TOKEN_KEYCHAIN_SERVICE, required=False)
    mode = "user_oauth"
    if refresh_token:
        token_payload = zoom_token_request({"grant_type": "refresh_token", "refresh_token": refresh_token})
        if token_payload.get("refresh_token"):
            store_keychain_secret(ZOOM_REFRESH_TOKEN_KEYCHAIN_SERVICE, token_payload["refresh_token"])
    elif zoom_s2s_configured():
        mode = "server_to_server_oauth"
        token_payload = zoom_token_request(
            {
                "grant_type": "account_credentials",
                "account_id": load_keychain_secret(ZOOM_ACCOUNT_ID_KEYCHAIN_SERVICE),
            }
        )
    else:
        raise ValueError("Zoom no esta autorizado. Abre https://kim.aipeople.app/oauth/zoom/start despues de configurar Client ID, Client Secret, Redirect URL y scopes.")
    access_token = token_payload.get("access_token") or ""
    if not access_token:
        raise ValueError("Zoom no devolvio access_token.")
    expires_in = int(token_payload.get("expires_in") or 3600)
    api_url = zoom_api_base_from_token_payload(token_payload)
    ZOOM_TOKEN_CACHE.update(
        {
            "access_token": access_token,
            "api_url": api_url,
            "expires_at": now_ts + max(60, expires_in - 60),
            "scope": token_payload.get("scope") or "",
            "mode": mode,
        }
    )
    return {"access_token": access_token, "api_url": api_url, "scope": token_payload.get("scope") or "", "mode": mode, "cached": False}


def zoom_request(path, method="GET", payload=None, params=None, token=None):
    token = token or zoom_access_token()
    return api_json_request(
        token.get("api_url") or ZOOM_API_BASE,
        path,
        {"Authorization": f"Bearer {token['access_token']}"},
        method=method,
        payload=payload,
        params=params,
    )


def normalize_zoom_user(item):
    item = item or {}
    return {
        "id": item.get("id"),
        "email": item.get("email"),
        "first_name": item.get("first_name"),
        "last_name": item.get("last_name"),
        "display_name": " ".join(part for part in [item.get("first_name"), item.get("last_name")] if part).strip(),
        "type": item.get("type"),
        "status": item.get("status"),
    }


def zoom_oauth_redirect_uri(handler):
    public_base = load_keychain_secret("codex.kim.public_base_url", required=False) or "https://kim.aipeople.app"
    return public_base.rstrip("/") + "/oauth/zoom/callback"


def zoom_oauth_start_url(handler):
    if not zoom_client_configured():
        raise ValueError("Faltan Client ID o Client Secret de Zoom en Keychain.")
    state = secrets.token_urlsafe(32)
    redirect_uri = zoom_oauth_redirect_uri(handler)
    write_json_file(ZOOM_OAUTH_STATE_FILE, {"state": state, "redirect_uri": redirect_uri, "created_at": now_iso()})
    params = {
        "client_id": load_keychain_secret(ZOOM_CLIENT_ID_KEYCHAIN_SERVICE),
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "state": state,
    }
    return "https://zoom.us/oauth/authorize?" + urllib.parse.urlencode(params)


def zoom_oauth_callback(handler, parsed):
    params = urllib.parse.parse_qs(parsed.query)
    if params.get("error"):
        error = html.escape((params.get("error_description") or params.get("error") or ["OAuth cancelado"])[0])
        write_text(
            handler,
            f"<h1>Zoom no autorizado</h1><p>{error}</p>",
            status=400,
            content_type="text/html; charset=utf-8",
        )
        return
    code = (params.get("code") or [""])[0]
    state = (params.get("state") or [""])[0]
    expected, _ = load_json_any([ZOOM_OAUTH_STATE_FILE])
    expected = expected or {}
    if not code or not state or state != expected.get("state"):
        write_text(
            handler,
            "<h1>Zoom OAuth invalido</h1><p>El estado OAuth no coincide. Vuelve a iniciar autorizacion desde Kim Live.</p>",
            status=400,
            content_type="text/html; charset=utf-8",
        )
        return
    redirect_uri = expected.get("redirect_uri") or zoom_oauth_redirect_uri(handler)
    try:
        token = zoom_token_request({"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri})
        if token.get("refresh_token"):
            store_keychain_secret(ZOOM_REFRESH_TOKEN_KEYCHAIN_SERVICE, token["refresh_token"])
        ZOOM_TOKEN_CACHE.update({"access_token": "", "expires_at": 0.0})
        profile = {}
        try:
            live_token = zoom_access_token(force=True)
            profile = normalize_zoom_user(zoom_request("/users/me", token=live_token))
        except Exception as exc:
            profile = {"error": brief(str(exc), 300)}
        append_memory("zoom_oauth_authorized", {"authorized": bool(token.get("refresh_token")), "profile": profile})
        append_daily_note("Zoom OAuth autorizado para Kim Live.")
        write_text(
            handler,
            "<h1>Zoom conectado con Kim Live</h1>"
            "<p>Kim ya puede preparar y crear reuniones Zoom con confirmacion del doctor.</p>"
            f"<pre>{html.escape(json.dumps(profile, ensure_ascii=False, indent=2))}</pre>",
            content_type="text/html; charset=utf-8",
        )
    except Exception as exc:
        write_text(
            handler,
            f"<h1>No pude conectar Zoom</h1><p>{html.escape(str(exc))}</p>"
            "<p>Revisa que el Client Secret sea el de esta misma app y que el Redirect URL coincida exactamente.</p>",
            status=500,
            content_type="text/html; charset=utf-8",
        )


def zoom_list_users(parameters=None):
    parameters = parameters or {}
    token = zoom_access_token()
    if token.get("mode") == "user_oauth":
        return {"ok": True, "provider": "zoom", "action": "list_users", "mode": "user_oauth", "users": [normalize_zoom_user(zoom_request("/users/me", token=token))]}
    page_size = min(max(int(first_value(parameters, "page_size", "limit", default=30) or 30), 1), 100)
    payload = zoom_request(
        "/users",
        params={
            "status": first_value(parameters, "status", default="active"),
            "page_size": page_size,
            "next_page_token": first_value(parameters, "next_page_token", "cursor", default=""),
        },
        token=token,
    )
    return {
        "ok": True,
        "provider": "zoom",
        "action": "list_users",
        "mode": token.get("mode"),
        "users": [normalize_zoom_user(item) for item in payload.get("users", [])],
        "page_count": payload.get("page_count"),
        "total_records": payload.get("total_records"),
        "next_page_token": payload.get("next_page_token"),
    }


def zoom_resolve_host(parameters=None, token=None):
    parameters = parameters or {}
    token = token or zoom_access_token()
    if token.get("mode") == "user_oauth":
        return {"host": "me", "source": "user_oauth_me"}
    explicit = str(first_value(parameters, "host_user_id", "host_id", "host_email", "user_id", "user", "email", default="") or "").strip()
    if explicit:
        return {"host": explicit, "source": "parameters"}
    configured = load_keychain_secret(ZOOM_DEFAULT_HOST_KEYCHAIN_SERVICE, required=False)
    if configured:
        return {"host": configured, "source": "keychain_default_host"}
    users = zoom_list_users({"page_size": 1, "status": "active"}).get("users") or []
    if not users:
        raise ValueError("Zoom no devolvio usuarios activos para seleccionar host.")
    user = users[0]
    return {"host": user.get("id") or user.get("email"), "source": "first_active_user", "user": user}


def zoom_parse_start(parameters=None):
    parameters = parameters or {}
    timezone_name = scheduler_timezone_name(parameters)
    raw = first_value(parameters, "start_at", "start_time", "due_at", "scheduled_at", "datetime", "cuando", default="")
    if not raw:
        raise ValueError("Falta start_at/start_time para crear la reunion Zoom.")
    start_iso = parse_due_at({"due_at": raw, "timezone": timezone_name})
    parsed = parse_scheduled_datetime(start_iso, timezone_name)
    return {"start_time": parsed.strftime("%Y-%m-%dT%H:%M:%S"), "timezone": timezone_name, "parsed": parsed}


def zoom_meeting_duration(parameters=None, parsed_start=None):
    parameters = parameters or {}
    explicit = first_value(parameters, "duration", "duration_minutes", "minutes", "duracion", default="")
    if explicit not in (None, ""):
        return max(1, int(float(explicit)))
    end_raw = first_value(parameters, "end_at", "end_time", "ends_at", default="")
    if end_raw and parsed_start:
        timezone_name = scheduler_timezone_name(parameters)
        end_iso = parse_due_at({"due_at": end_raw, "timezone": timezone_name})
        end_dt = parse_scheduled_datetime(end_iso, timezone_name)
        return max(1, int((end_dt - parsed_start).total_seconds() // 60))
    return 30


def zoom_create_meeting_payload(parameters=None):
    parameters = parameters or {}
    start = zoom_parse_start(parameters)
    duration = zoom_meeting_duration(parameters, parsed_start=start["parsed"])
    topic = str(first_value(parameters, "topic", "title", "subject", "name", "asunto", default="Reunion con Dr. Yehoshua") or "").strip()
    agenda = str(first_value(parameters, "agenda", "description", "content", "body", "objective", "objetivo", default="") or "").strip()
    settings = dict(parameters.get("settings") or {})
    settings.setdefault("waiting_room", True)
    settings.setdefault("join_before_host", False)
    settings.setdefault("approval_type", 2)
    settings.setdefault("registrants_email_notification", True)
    payload = {"topic": topic, "type": int(first_value(parameters, "type", "meeting_type_id", default=2) or 2), "start_time": start["start_time"], "duration": duration, "timezone": start["timezone"], "agenda": agenda, "settings": settings}
    password = str(first_value(parameters, "password", "passcode", default="") or "").strip()
    if password:
        payload["password"] = password
    return payload


def zoom_safe_meeting_result(meeting):
    meeting = meeting or {}
    return {
        "id": meeting.get("id"),
        "uuid": meeting.get("uuid"),
        "host_id": meeting.get("host_id"),
        "host_email": meeting.get("host_email"),
        "topic": meeting.get("topic"),
        "type": meeting.get("type"),
        "status": meeting.get("status"),
        "start_time": meeting.get("start_time"),
        "duration": meeting.get("duration"),
        "timezone": meeting.get("timezone"),
        "join_url": meeting.get("join_url"),
        "password": meeting.get("password"),
        "created_at": meeting.get("created_at"),
    }


def zoom_record_meeting(parameters, host, meeting):
    record = {
        "at": now_iso(),
        "provider": "zoom",
        "action": "create_meeting",
        "host": host,
        "parameters": sanitize_for_log(parameters),
        "meeting": zoom_safe_meeting_result(meeting),
    }
    append_jsonl_any([ZOOM_MEETINGS_LOG, RUNTIME_ZOOM_MEETINGS_LOG], record)
    append_memory("zoom_meeting_created", {"meeting_id": record["meeting"].get("id"), "topic": record["meeting"].get("topic"), "start_time": record["meeting"].get("start_time"), "join_url": record["meeting"].get("join_url")})
    return record


def zoom_human_start_time(meeting, parameters=None):
    parameters = parameters or {}
    timezone_name = str(first_value(parameters, "timezone", "tz", "zona_horaria", default=meeting.get("timezone") or DEFAULT_SCHEDULER_TIMEZONE) or DEFAULT_SCHEDULER_TIMEZONE)
    raw = str(meeting.get("start_time") or first_value(parameters, "start_at", "start_time", "datetime", "cuando", default="") or "").strip()
    if not raw:
        return ""
    try:
        if raw.endswith("Z"):
            parsed = dt.datetime.fromisoformat(raw[:-1] + "+00:00").astimezone(ZoneInfo(timezone_name))
        else:
            parsed = dt.datetime.fromisoformat(raw)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=ZoneInfo(timezone_name))
            else:
                parsed = parsed.astimezone(ZoneInfo(timezone_name))
        return parsed.strftime("%Y-%m-%d %H:%M") + f" {timezone_name}"
    except Exception:
        return f"{raw} {timezone_name}".strip()


def zoom_invitation_subject(meeting, parameters=None):
    parameters = parameters or {}
    explicit = str(first_value(parameters, "invite_subject", "email_subject", "subject", "asunto", default="") or "").strip()
    if explicit:
        return explicit
    topic = str(meeting.get("topic") or first_value(parameters, "topic", "title", "name", default="Reunion Zoom") or "Reunion Zoom").strip()
    return f"Invitacion Zoom: {topic}"


def zoom_invitation_text(meeting, parameters=None):
    parameters = parameters or {}
    meeting = meeting or {}
    greeting = str(first_value(parameters, "greeting", "saludo", default="Hola,") or "").strip()
    intro = str(
        first_value(
            parameters,
            "invite_intro",
            "intro",
            "message_intro",
            default="Te comparto la invitacion para nuestra reunion con el Dr. Yehoshua.",
        )
        or ""
    ).strip()
    topic = str(meeting.get("topic") or first_value(parameters, "topic", "title", "name", default="Reunion Zoom") or "Reunion Zoom").strip()
    start = zoom_human_start_time(meeting, parameters)
    duration = meeting.get("duration") or first_value(parameters, "duration", "duration_minutes", "minutes", default="")
    agenda = str(meeting.get("agenda") or first_value(parameters, "agenda", "description", "objective", "objetivo", default="") or "").strip()
    join_url = str(meeting.get("join_url") or "").strip()
    lines = [greeting, "", intro, "", f"Reunion: {topic}"]
    if start:
        lines.append(f"Fecha y hora: {start}")
    if duration:
        lines.append(f"Duracion: {duration} minutos")
    if agenda:
        lines.append(f"Objetivo: {agenda}")
    if join_url:
        lines.extend(["", f"Link de Zoom: {join_url}"])
    if meeting.get("id"):
        lines.append(f"Meeting ID: {meeting.get('id')}")
    if meeting.get("password"):
        lines.append(f"Passcode: {meeting.get('password')}")
    closing = str(first_value(parameters, "closing", "cierre", default="Quedo atenta por si necesitas ajustar algo.") or "").strip()
    if closing:
        lines.extend(["", closing])
    signature = str(first_value(parameters, "signature", "firma", default="Kim Yan\nAI People") or "").strip()
    if signature and not boolish(parameters.get("no_signature")):
        lines.extend(["", signature])
    return "\n".join(lines).strip()


def zoom_invite_recipients(parameters=None):
    parameters = parameters or {}
    raw_whatsapp = first_value(parameters, "whatsapp_to", "to_whatsapp", "phone", "telefono", "whatsapp", default="")
    raw_email = first_value(parameters, "email_to", "to_email", "email", "correo", default="")
    raw_to = first_value(parameters, "to", "recipient", "recipients", "destinatario", default="")
    whatsapp_values = []
    email_values = []
    if isinstance(raw_whatsapp, list):
        whatsapp_values.extend(raw_whatsapp)
    elif raw_whatsapp:
        whatsapp_values.extend(re.split(r"[,;\s]+", str(raw_whatsapp)))
    if isinstance(raw_email, list):
        email_values.extend(raw_email)
    elif raw_email:
        email_values.extend(re.split(r"[,;\s]+", str(raw_email)))
    if raw_to:
        raw_items = raw_to if isinstance(raw_to, list) else re.split(r"[,;\s]+", str(raw_to))
        for item in raw_items:
            text = str(item or "").strip()
            if not text:
                continue
            if "@" in text:
                email_values.append(text)
            elif re.search(r"\d", text):
                whatsapp_values.append(text)
    email_values = list(dict.fromkeys(addr for addr in normalize_email_recipients(email_values) if addr))
    whatsapp_values = list(dict.fromkeys(normalize_phone_number(value) for value in whatsapp_values if normalize_phone_number(value)))
    return {"whatsapp": whatsapp_values, "email": email_values}


def zoom_invite_preview(parameters=None):
    parameters = parameters or {}
    payload = zoom_create_meeting_payload(parameters)
    recipients = zoom_invite_recipients(parameters)
    channels = []
    if recipients["whatsapp"]:
        channels.append("WhatsApp")
    if recipients["email"]:
        channels.append("email")
    return {
        "meeting_payload": payload,
        "recipients": recipients,
        "channels": channels,
        "will_send": bool(channels),
    }


def zoom_requires_authorization_result(action="create_and_send_invite"):
    return {
        "ok": False,
        "provider": "zoom",
        "action": action,
        "requires_authorization": True,
        "auth_url": "https://kim.aipeople.app/oauth/zoom/start",
        "status": zoom_status(live=False),
        "message": "Zoom esta configurado, pero falta autorizar la cuenta. Abre el auth_url, inicia sesion en Zoom y acepta los permisos.",
    }


def zoom_create_meeting(parameters=None, confirm=False):
    parameters = parameters or {}
    if not zoom_authorized() and not zoom_s2s_configured():
        return zoom_requires_authorization_result("create_meeting")
    token = zoom_access_token()
    host = zoom_resolve_host(parameters, token=token)
    payload = zoom_create_meeting_payload(parameters)
    preview = {"host": host, "payload": payload}
    if not confirm:
        return confirmation_preview(
            "zoom",
            "create_meeting",
            f"Crear reunion Zoom '{payload.get('topic')}' para {payload.get('start_time')} {payload.get('timezone')}.",
            preview,
            execution_parameters=parameters,
        )
    meeting = zoom_request(f"/users/{urllib.parse.quote(str(host['host']))}/meetings", method="POST", payload=payload, token=token)
    safe = zoom_safe_meeting_result(meeting)
    record = zoom_record_meeting(parameters, host, meeting)
    return {"ok": True, "provider": "zoom", "action": "create_meeting", "meeting": safe, "join_url": safe.get("join_url"), "meeting_log": record, "confirmed": True}


def zoom_create_and_send_invite(parameters=None, confirm=False):
    parameters = parameters or {}
    if not zoom_authorized() and not zoom_s2s_configured():
        return zoom_requires_authorization_result("create_and_send_invite")
    preview = zoom_invite_preview(parameters)
    if not confirm:
        summary = f"Crear reunion Zoom '{preview['meeting_payload'].get('topic')}'"
        if preview["channels"]:
            summary += " y enviar invitacion por " + " y ".join(preview["channels"])
        else:
            summary += " y devolver invitacion lista para copiar"
        prepared = confirmation_preview(
            "zoom",
            "create_and_send_invite",
            summary + ".",
            preview,
            execution_parameters=parameters,
        )
        prepared["preview"] = preview
        return prepared
    meeting_result = zoom_create_meeting(parameters, confirm=True)
    if not meeting_result.get("ok"):
        return meeting_result
    meeting = meeting_result.get("meeting") or {}
    invite_text = zoom_invitation_text(meeting, parameters)
    subject = zoom_invitation_subject(meeting, parameters)
    recipients = zoom_invite_recipients(parameters)
    deliveries = []
    failures = []
    for phone in recipients["whatsapp"]:
        try:
            delivery = run_twilio_bridge(
                "send_whatsapp",
                {
                    "to": phone,
                    "body": invite_text,
                    "contact_name": first_value(parameters, "contact_name", "client_name", "name", default="Invitado Zoom"),
                    "relationship": first_value(parameters, "relationship", default="meeting_invitee"),
                    "company": first_value(parameters, "company", "empresa", default="AI People"),
                    "context_id": first_value(parameters, "context_id", default=f"ZOOM-{meeting.get('id') or today()}"),
                },
                confirm=True,
            )
            deliveries.append(delivery)
        except Exception as exc:
            failures.append({"channel": "whatsapp", "to": phone, "error": brief(str(exc), 500)})
    if recipients["email"]:
        try:
            delivery = run_hostinger_mail_bridge(
                "send_email",
                {
                    "mailbox": first_value(parameters, "mailbox", "from", "sender", default=""),
                    "to": recipients["email"],
                    "subject": subject,
                    "body": invite_text,
                    "from_name": first_value(parameters, "from_name", default="Kim Yan"),
                },
                confirm=True,
            )
            deliveries.append(delivery)
        except Exception as exc:
            failures.append({"channel": "email", "to": recipients["email"], "error": brief(str(exc), 500)})
    result = {
        "ok": not failures,
        "provider": "zoom",
        "action": "create_and_send_invite",
        "meeting": meeting,
        "join_url": meeting.get("join_url"),
        "invite_subject": subject,
        "invite_text": invite_text,
        "recipients": recipients,
        "deliveries": deliveries,
        "failures": failures,
        "meeting_log": meeting_result.get("meeting_log"),
        "confirmed": True,
    }
    append_jsonl_any([ZOOM_MEETINGS_LOG, RUNTIME_ZOOM_MEETINGS_LOG], {"at": now_iso(), "provider": "zoom", "action": "create_and_send_invite", "result": sanitize_for_log(result)})
    append_memory("zoom_invite_sent", {"meeting_id": meeting.get("id"), "topic": meeting.get("topic"), "recipients": recipients, "failures": failures})
    return result


def zoom_encode_meeting_id(meeting_id):
    raw = str(meeting_id or "").strip()
    if not raw:
        raise ValueError("Falta meeting_id/meeting_uuid para consultar transcript de Zoom.")
    encoded = urllib.parse.quote(raw, safe="")
    if raw.startswith("/") or "//" in raw:
        encoded = urllib.parse.quote(encoded, safe="")
    return encoded


def zoom_transcript_meeting_id(parameters=None):
    parameters = parameters or {}
    value = first_value(parameters, "meeting_id", "meetingId", "meeting_uuid", "uuid", "id", "recording_id", default="")
    if not value:
        raise ValueError("Falta meeting_id o meeting_uuid para consultar transcript de Zoom.")
    return str(value).strip()


def zoom_download_bytes(download_url, token=None):
    token = token or zoom_access_token()
    headers = {"Authorization": f"Bearer {token['access_token']}", "User-Agent": f"KimLive/{APP_VERSION}"}
    request = urllib.request.Request(download_url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        if exc.code not in {401, 403}:
            raise
    separator = "&" if "?" in download_url else "?"
    fallback_url = f"{download_url}{separator}access_token={urllib.parse.quote(token['access_token'])}"
    request = urllib.request.Request(fallback_url, headers={"User-Agent": f"KimLive/{APP_VERSION}"}, method="GET")
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def zoom_file_text(data):
    raw = data or b""
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def zoom_clean_transcript_text(raw_text):
    text = str(raw_text or "").replace("\r\n", "\n").replace("\r", "\n")
    cleaned = []
    skip_next_setting = False
    timestamp_re = re.compile(r"^\s*(?:\d{1,2}:)?\d{2}:\d{2}\.\d{3}\s+-->\s+(?:\d{1,2}:)?\d{2}:\d{2}\.\d{3}")
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if cleaned and cleaned[-1]:
                cleaned.append("")
            continue
        if line.upper().startswith("WEBVTT") or line.startswith("NOTE"):
            continue
        if timestamp_re.search(line):
            skip_next_setting = True
            continue
        if skip_next_setting and re.match(r"^(align|position|size|line):", line, flags=re.I):
            continue
        skip_next_setting = False
        if re.fullmatch(r"\d+", line):
            continue
        line = re.sub(r"<v\s+([^>]+)>", r"\1: ", line)
        line = re.sub(r"</v>", "", line)
        line = re.sub(r"<[^>]+>", "", line)
        line = html.unescape(line)
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            cleaned.append(line)
    compact = "\n".join(cleaned)
    compact = re.sub(r"\n{3,}", "\n\n", compact)
    return compact.strip()


def zoom_transcript_candidates(payload):
    candidates = []

    def add_candidate(item, source):
        if not isinstance(item, dict):
            return
        download_url = item.get("download_url") or item.get("transcript_download_url") or item.get("url") or item.get("downloadUrl")
        if not download_url:
            return
        file_type = str(item.get("file_type") or item.get("file_extension") or item.get("recording_type") or item.get("type") or "").upper()
        name = str(item.get("file_name") or item.get("name") or item.get("id") or "").strip()
        score = 0
        if "TRANSCRIPT" in file_type or "TRANSCRIPT" in name.upper():
            score += 20
        if "VTT" in file_type or name.lower().endswith(".vtt") or ".vtt" in download_url.lower():
            score += 10
        if "CC" in file_type or "CHAT" in file_type:
            score -= 5
        candidates.append({"source": source, "score": score, "metadata": item, "download_url": download_url})

    if isinstance(payload, dict):
        add_candidate(payload, "direct")
        for key in ("transcript_files", "transcripts", "recording_files", "files"):
            for item in payload.get(key) or []:
                add_candidate(item, key)
    elif isinstance(payload, list):
        for item in payload:
            add_candidate(item, "list")
    return sorted(candidates, key=lambda item: item.get("score", 0), reverse=True)


def zoom_fetch_transcript_file(meeting_id, token=None):
    token = token or zoom_access_token()
    encoded = zoom_encode_meeting_id(meeting_id)
    errors = []
    for path in (f"/meetings/{encoded}/transcript", f"/meetings/{encoded}/recordings"):
        try:
            payload = zoom_request(path, token=token)
            candidates = zoom_transcript_candidates(payload)
            if candidates:
                candidate = candidates[0]
                candidate["api_path"] = path
                candidate["api_payload"] = payload
                return candidate
        except Exception as exc:
            errors.append({"path": path, "error": brief(str(exc), 500)})
    return {"error": "Zoom no devolvio transcript para esa reunion.", "errors": errors}


def zoom_transcript_paths(meeting_id, suffix):
    safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(meeting_id or "meeting")).strip("_") or "meeting"
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"zoom_transcript_{safe_id}_{stamp}{suffix}"
    return ZOOM_TRANSCRIPTS_DIR / filename, RUNTIME_ZOOM_TRANSCRIPTS_DIR / filename


def zoom_store_transcript(meeting_id, raw_bytes, raw_text, clean_text, metadata):
    raw_suffix = ".vtt" if "WEBVTT" in (raw_text or "")[:80].upper() else ".txt"
    raw_primary, raw_runtime = zoom_transcript_paths(meeting_id, raw_suffix)
    txt_primary, txt_runtime = zoom_transcript_paths(meeting_id, ".txt")
    raw_written = write_bytes_file_both(raw_primary, raw_runtime, raw_bytes)
    txt_written = []
    for path in (txt_primary, txt_runtime):
        try:
            write_text_file(path, clean_text)
            txt_written.append(str(path))
        except (PermissionError, OSError):
            continue
    record = {
        "at": now_iso(),
        "provider": "zoom",
        "action": "get_transcript",
        "meeting_id": meeting_id,
        "raw_paths": raw_written,
        "text_paths": txt_written,
        "char_count": len(clean_text or ""),
        "metadata": sanitize_for_log(metadata),
    }
    append_jsonl_any([ZOOM_TRANSCRIPTS_LOG, RUNTIME_ZOOM_TRANSCRIPTS_LOG], record)
    append_memory("zoom_transcript_saved", {"meeting_id": meeting_id, "text_paths": txt_written, "char_count": record["char_count"]})
    return record


def zoom_fetch_transcript(parameters=None):
    parameters = parameters or {}
    if not zoom_authorized() and not zoom_s2s_configured():
        return zoom_requires_authorization_result("get_transcript")
    token = zoom_access_token()
    meeting_id = zoom_transcript_meeting_id(parameters)
    candidate = zoom_fetch_transcript_file(meeting_id, token=token)
    if candidate.get("error"):
        return {
            "ok": False,
            "provider": "zoom",
            "action": "get_transcript",
            "meeting_id": meeting_id,
            "message": (
                "No encontre transcript descargable para esa reunion. Zoom solo lo entrega si la reunion tuvo cloud recording "
                "con audio transcript habilitado y el OAuth tiene permisos de lectura de recording/transcript."
            ),
            "errors": candidate.get("errors") or [],
        }
    raw_bytes = zoom_download_bytes(candidate["download_url"], token=token)
    raw_text = zoom_file_text(raw_bytes)
    clean_text = zoom_clean_transcript_text(raw_text) or raw_text.strip()
    record = zoom_store_transcript(meeting_id, raw_bytes, raw_text, clean_text, candidate)
    return {
        "ok": True,
        "provider": "zoom",
        "action": "get_transcript",
        "meeting_id": meeting_id,
        "char_count": len(clean_text),
        "transcript_text": clean_text if len(clean_text) <= 6000 else clean_text[:6000].rstrip() + "\n\n[Transcript completo guardado en BIFROST.]",
        "text_paths": record.get("text_paths") or [],
        "raw_paths": record.get("raw_paths") or [],
        "metadata": sanitize_for_log(candidate.get("metadata") or {}),
        "log": record,
    }


def zoom_transcript_summary_text(transcript_text, parameters=None):
    parameters = parameters or {}
    text = str(transcript_text or "").strip()
    if not text:
        return "No hay transcript legible para resumir."
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    keywords = (
        "acuerdo",
        "pendiente",
        "siguiente",
        "tarea",
        "enviar",
        "mandar",
        "confirmar",
        "agenda",
        "reunion",
        "reunión",
        "cliente",
        "precio",
        "propuesta",
        "next",
        "follow",
    )
    useful = []
    for line in lines:
        if any(keyword in line.lower() for keyword in keywords):
            useful.append(line)
        if len(useful) >= 8:
            break
    opening = lines[:5]
    if useful:
        bullets = "\n".join(f"- {brief(item, 260)}" for item in useful)
    else:
        bullets = "\n".join(f"- {brief(item, 260)}" for item in opening[:6])
    title = str(first_value(parameters, "summary_title", "title", "topic", default="Resumen de reunion Zoom") or "Resumen de reunion Zoom").strip()
    return (
        f"{title}\n\n"
        "Resumen local de Kim:\n"
        f"{bullets}\n\n"
        "Nota: este resumen fue generado localmente desde el transcript guardado en BIFROST; si necesitas sintesis profunda con IA, pide resumen AI explicitamente."
    ).strip()


def zoom_transcript_delivery_body(fetch_result, parameters=None):
    parameters = parameters or {}
    send_type = str(first_value(parameters, "send_type", "content_type", "tipo", default="summary") or "summary").strip().lower()
    transcript = str(fetch_result.get("transcript_text") or "").strip()
    if send_type in {"full", "transcript", "transcripcion", "transcripción", "complete", "completo"}:
        text = transcript
        if len(text) > 50000:
            text = text[:50000].rstrip() + "\n\n[Transcript completo guardado en BIFROST; recortado para envio.]"
    else:
        text = zoom_transcript_summary_text(transcript, parameters)
    paths = fetch_result.get("text_paths") or []
    if paths:
        text += "\n\nBIFROST transcript: " + paths[0]
    return text.strip(), send_type


def zoom_send_transcript(parameters=None, confirm=False):
    parameters = parameters or {}
    if not zoom_authorized() and not zoom_s2s_configured():
        return zoom_requires_authorization_result("send_transcript")
    fetch_result = zoom_fetch_transcript(parameters)
    if not fetch_result.get("ok"):
        return fetch_result
    body, send_type = zoom_transcript_delivery_body(fetch_result, parameters)
    subject = str(first_value(parameters, "subject", "email_subject", "asunto", default="Resumen de reunion Zoom") or "Resumen de reunion Zoom").strip()
    recipients = zoom_invite_recipients(parameters)
    preview_body = body
    if recipients["whatsapp"] and len(preview_body) > 1400:
        preview_body = brief(preview_body, 1400)
    preview = {
        "meeting_id": fetch_result.get("meeting_id"),
        "send_type": send_type,
        "recipients": recipients,
        "subject": subject,
        "body_preview": preview_body,
        "text_paths": fetch_result.get("text_paths") or [],
    }
    if not confirm:
        prepared = confirmation_preview(
            "zoom",
            "send_transcript",
            f"Enviar {send_type} de Zoom por " + (" y ".join(channel for channel, values in {"WhatsApp": recipients["whatsapp"], "email": recipients["email"]}.items() if values) or "canal pendiente") + ".",
            preview,
            execution_parameters=parameters,
        )
        prepared["preview"] = preview
        return prepared
    deliveries = []
    failures = []
    for phone in recipients["whatsapp"]:
        whatsapp_body = body if len(body) <= 1400 else brief(body, 1400)
        try:
            deliveries.append(
                run_twilio_bridge(
                    "send_whatsapp",
                    {
                        "to": phone,
                        "body": whatsapp_body,
                        "contact_name": first_value(parameters, "contact_name", "client_name", "name", default="Invitado Zoom"),
                        "relationship": first_value(parameters, "relationship", default="meeting_transcript_recipient"),
                        "company": first_value(parameters, "company", "empresa", default="AI People"),
                        "context_id": first_value(parameters, "context_id", default=f"ZOOM-TRANSCRIPT-{fetch_result.get('meeting_id') or today()}"),
                    },
                    confirm=True,
                )
            )
        except Exception as exc:
            failures.append({"channel": "whatsapp", "to": phone, "error": brief(str(exc), 500)})
    if recipients["email"]:
        try:
            deliveries.append(
                run_hostinger_mail_bridge(
                    "send_email",
                    {
                        "mailbox": first_value(parameters, "mailbox", "from", "sender", default=""),
                        "to": recipients["email"],
                        "subject": subject,
                        "body": body,
                        "from_name": first_value(parameters, "from_name", default="Kim Yan"),
                    },
                    confirm=True,
                )
            )
        except Exception as exc:
            failures.append({"channel": "email", "to": recipients["email"], "error": brief(str(exc), 500)})
    result = {
        "ok": not failures,
        "provider": "zoom",
        "action": "send_transcript",
        "meeting_id": fetch_result.get("meeting_id"),
        "send_type": send_type,
        "recipients": recipients,
        "deliveries": deliveries,
        "failures": failures,
        "text_paths": fetch_result.get("text_paths") or [],
        "confirmed": True,
    }
    append_jsonl_any([ZOOM_TRANSCRIPTS_LOG, RUNTIME_ZOOM_TRANSCRIPTS_LOG], {"at": now_iso(), "provider": "zoom", "action": "send_transcript", "result": sanitize_for_log(result)})
    append_memory("zoom_transcript_sent", {"meeting_id": result.get("meeting_id"), "recipients": recipients, "failures": failures})
    return result


def zoom_list_meetings(parameters=None):
    parameters = parameters or {}
    token = zoom_access_token()
    host = zoom_resolve_host(parameters, token=token)
    payload = zoom_request(
        f"/users/{urllib.parse.quote(str(host['host']))}/meetings",
        params={
            "type": first_value(parameters, "type", default="scheduled"),
            "page_size": min(max(int(first_value(parameters, "page_size", "limit", default=30) or 30), 1), 100),
            "next_page_token": first_value(parameters, "next_page_token", "cursor", default=""),
        },
        token=token,
    )
    return {
        "ok": True,
        "provider": "zoom",
        "action": "list_meetings",
        "host": host,
        "meetings": [zoom_safe_meeting_result(item) for item in payload.get("meetings", [])],
        "next_page_token": payload.get("next_page_token"),
        "page_count": payload.get("page_count"),
        "total_records": payload.get("total_records"),
    }


def zoom_status(live=False):
    has_account = bool(load_keychain_secret(ZOOM_ACCOUNT_ID_KEYCHAIN_SERVICE, required=False))
    has_client_id = bool(load_keychain_secret(ZOOM_CLIENT_ID_KEYCHAIN_SERVICE, required=False))
    has_client_secret = bool(load_keychain_secret(ZOOM_CLIENT_SECRET_KEYCHAIN_SERVICE, required=False))
    has_refresh = zoom_authorized()
    status = {
        "configured": has_client_id and has_client_secret,
        "authorized": has_refresh,
        "server_to_server_configured": has_account and has_client_id and has_client_secret,
        "has_account_id": has_account,
        "has_client_id": has_client_id,
        "has_client_secret": has_client_secret,
        "write_requires_confirmation": True,
        "capabilities": ["status", "auth_url", "list_users", "list_meetings", "create_meeting", "create_and_send_invite", "get_transcript", "send_transcript"],
        "auth_type": "user_oauth_or_server_to_server_oauth",
        "auth_url": "https://kim.aipeople.app/oauth/zoom/start",
        "docs": "https://developers.zoom.us/api-hub/",
    }
    if live and status["configured"]:
        try:
            token = zoom_access_token(force=True)
            status["live_ok"] = True
            status["mode"] = token.get("mode")
            status["scope_preview"] = brief(token.get("scope") or "", 240)
            status["default_host"] = zoom_resolve_host({}, token=token)
        except Exception as exc:
            status["live_ok"] = False
            status["error"] = brief(str(exc), 500)
    return status


def run_zoom_bridge(action, parameters, confirm=False):
    action = (action or "").strip().lower()
    parameters = parameters or {}
    if action in {"status", "me"}:
        return {"ok": True, "provider": "zoom", "action": action, "status": zoom_status(live=True)}
    if action in {"auth_url", "authorize", "connect"}:
        return {"ok": True, "provider": "zoom", "action": action, "auth_url": "https://kim.aipeople.app/oauth/zoom/start"}
    if action in {"list_users", "users"}:
        return zoom_list_users(parameters)
    if action in {"list_meetings", "meetings", "upcoming_meetings"}:
        return zoom_list_meetings(parameters)
    if action in {
        "create_and_send_invite",
        "create_invite",
        "send_invite",
        "send_invitation",
        "crear_y_enviar_invitacion",
        "crear_y_mandar_invitacion",
        "zoom_invite",
        "zoom_invitation",
        "agendar_y_enviar_zoom",
        "mandar_invitacion_zoom",
    }:
        return zoom_create_and_send_invite(parameters, confirm=confirm)
    if action in {"get_transcript", "fetch_transcript", "transcript", "meeting_transcript", "transcripcion", "transcripción"}:
        return zoom_fetch_transcript(parameters)
    if action in {
        "send_transcript",
        "send_summary",
        "resend_transcript",
        "forward_transcript",
        "meeting_summary",
        "reenviar_transcript",
        "reenviar_transcripción",
        "reenviar_resumen",
        "mandar_resumen",
        "mandar_transcript",
    }:
        return zoom_send_transcript(parameters, confirm=confirm)
    if action in {"create_meeting", "schedule_meeting", "meeting", "agendar_reunion", "agendar_reunión", "crear_reunion", "crear_reunión", "zoom_meeting"}:
        return zoom_create_meeting(parameters, confirm=confirm)
    raise ValueError(f"Accion Zoom no soportada: {action}")


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


def phone_digits(value):
    raw = str(value or "").strip()
    if raw.lower().startswith("whatsapp:"):
        raw = raw.split(":", 1)[1]
    return re.sub(r"\D+", "", raw)


def twilio_lookup_phone_number(value):
    phone = normalize_phone_number(value)
    if phone.lower().startswith("whatsapp:"):
        return normalize_phone_number(phone.split(":", 1)[1])
    return phone


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


def crm_candidate_roots():
    roots = [CRM_ROOT, RUNTIME_CRM_ROOT]
    def score(root):
        db = root / "crm.sqlite"
        try:
            return db.stat().st_mtime
        except OSError:
            return 0
    return sorted(roots, key=score, reverse=True)


def crm_connect():
    global ACTIVE_CRM_ROOT, ACTIVE_CRM_DB
    candidates = [active_crm_root()] if ACTIVE_CRM_ROOT else crm_candidate_roots()
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
    contact_id = str(contact.get("id") or "").strip()
    if contact_id:
        root = active_crm_root() / "contacts" / "by_type"
        for existing in root.glob("*/*.md"):
            if existing == path:
                continue
            try:
                existing_text = existing.read_text(encoding="utf-8")
            except OSError:
                continue
            if f"- ID: {contact_id}\n" not in existing_text:
                continue
            try:
                existing.unlink()
            except OSError:
                pass
    return str(path)


def crm_upsert_contact(parameters=None, source="kim_live"):
    parameters = parameters or {}
    phone = normalize_phone_number(first_value(parameters, "phone", "phone_e164", "telefono", "to", "from", "recipient", default=""))
    email = str(first_value(parameters, "email", "correo", default="") or "").strip()
    display_name = str(first_value(parameters, "display_name", "name", "nombre", "client_name", "contact_name", default="") or "").strip()
    insert_display_name = display_name or phone or email or "Contacto Kim"
    contact_type = str(first_value(parameters, "contact_type", "type", "tipo", default="") or "").strip().lower()
    insert_contact_type = contact_type or "client"
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
        if row is None and display_name:
            matches = conn.execute(
                "SELECT * FROM contacts WHERE lower(display_name)=lower(?) ORDER BY updated_at DESC LIMIT 2",
                (display_name,),
            ).fetchall()
            if len(matches) == 1:
                row = matches[0]
        if row:
            contact_id = row["id"]
            conn.execute(
                """
                UPDATE contacts
                SET display_name=CASE WHEN ? != '' THEN ? ELSE display_name END,
                    phone_e164=COALESCE(NULLIF(?, ''), phone_e164),
                    email=COALESCE(NULLIF(?, ''), email),
                    company_id=COALESCE(?, company_id),
                    contact_type=CASE WHEN ? != '' THEN ? ELSE contact_type END,
                    country=COALESCE(NULLIF(?, ''), country),
                    notes=CASE WHEN ? != '' AND instr(notes, ?) = 0 THEN trim(notes || char(10) || ?) ELSE notes END,
                    updated_at=?
                WHERE id=?
                """,
                (display_name, display_name, phone, email, company_id, contact_type, contact_type, country, notes, notes, notes, now, contact_id),
            )
        else:
            contact_id = crm_id("CT")
            conn.execute(
                """
                INSERT INTO contacts (id, display_name, phone_e164, email, company_id, contact_type, source, country, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (contact_id, insert_display_name, phone or None, email or None, company_id, insert_contact_type, source, country, notes, now, now),
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
            "action": "status",
            "database": str(active_crm_db()),
            "root": str(active_crm_root()),
            "preferred_root": str(CRM_ROOT),
            "fallback_active": active_crm_root() != CRM_ROOT,
            "contacts": conn.execute("SELECT count(*) AS c FROM contacts").fetchone()["c"],
            "companies": conn.execute("SELECT count(*) AS c FROM companies").fetchone()["c"],
            "interactions": conn.execute("SELECT count(*) AS c FROM interactions").fetchone()["c"],
            "scheduled_actions": conn.execute("SELECT count(*) AS c FROM scheduled_actions").fetchone()["c"],
            "capabilities": [
                "status",
                "list_contacts",
                "person_context",
                "doctor_pending_report",
                "upsert_contact",
                "record_note",
            ],
        }


DOCTOR_PENDING_TOPIC_RULES = [
    {
        "id": "pending_rhythm",
        "title": "Ritmo diario y micromanagement",
        "patterns": ["8 30 de la manana", "8 30", "10 de la noche", "10 30", "saturarme", "micromanagement", "pendientes"],
        "summary": "Entregar reporte diario de pendientes, prueba nocturna y bloques de trabajo saturados para el doctor.",
    },
    {
        "id": "mail_triage",
        "title": "Filtro diario de correo",
        "patterns": ["correos", "correo", "spam", "oportunidades", "bandejas de entrada"],
        "summary": "Revisar inbox, limpiar spam y resaltar oportunidades comerciales o alertas relevantes.",
    },
    {
        "id": "linkedin_presence",
        "title": "LinkedIn y reputacion",
        "patterns": ["linkedin", "imagen", "contactos", "mandarle un mensaje", "presencia"],
        "summary": "Usar LinkedIn para prospectar, enriquecer contactos y mejorar imagen profesional.",
    },
    {
        "id": "landing_and_seo",
        "title": "Landing personal y SEO",
        "patterns": ["landing page", "pagina informativa", "seo", "mejor pagina"],
        "summary": "Dar seguimiento a la pagina personal, SEO tecnico y la coordinacion con la agencia.",
    },
    {
        "id": "product_bolillo",
        "title": "Producto bolillo: tarjeta IA",
        "patterns": ["producto bolillo", "tarjeta de presentacion", "tarjeta de ia", "qr", "microproblema", "business model", "competencia"],
        "summary": "Validar la tarjeta de presentacion con IA como producto inicial, competencia y modelo de negocio.",
    },
    {
        "id": "figma_and_frontend",
        "title": "Figma e interfaz Kim",
        "patterns": ["figma", "frontend", "manita de gato"],
        "summary": "Conectar diseño/Figma con la mejora del frontend y la experiencia operativa de Kim.",
    },
]


def read_jsonl_entries(path, limit=0):
    entries = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                raw = line.strip()
                if not raw:
                    continue
                try:
                    entries.append(json.loads(raw))
                except json.JSONDecodeError:
                    continue
    except (FileNotFoundError, PermissionError, OSError):
        return []
    if limit and limit > 0:
        return entries[-limit:]
    return entries


def recent_memory_inbox_paths(days=3):
    roots = [MEMORY_INBOX, RUNTIME_MEMORY_INBOX]
    paths = []
    seen = set()
    for offset in range(max(1, int(days or 1))):
        day_value = (dt.date.today() - dt.timedelta(days=offset)).isoformat()
        file_name = f"kim_live_{day_value}.jsonl"
        chosen = None
        for root in roots:
            candidate = root / file_name
            if candidate.exists():
                chosen = candidate
                break
        if chosen:
            key = str(chosen.resolve())
            if key not in seen:
                paths.append(chosen)
                seen.add(key)
    return paths


def load_recent_memory_events(days=3, kinds=None, limit=400):
    allowed = {str(item).strip() for item in (kinds or []) if str(item).strip()}
    rows = []
    for path in recent_memory_inbox_paths(days=days):
        for entry in read_jsonl_entries(path):
            if allowed and entry.get("kind") not in allowed:
                continue
            rows.append(entry)
    rows.sort(key=lambda item: str(item.get("at") or ""))
    if limit and len(rows) > limit:
        rows = rows[-limit:]
    return rows


def doctor_pending_topics(events):
    recent_texts = []
    for item in events:
        text = ""
        if item.get("kind") == "conversation_note":
            text = str(item.get("text") or "")
        elif item.get("kind") == "execution_request":
            text = str(item.get("text") or "")
        elif item.get("kind") == "api_bridge_action":
            text = str(item.get("transcript_excerpt") or "")
        text = text.strip()
        if text:
            recent_texts.append({"at": item.get("at") or "", "text": text, "normalized": normalize_security_text(text)})
    combined = "\n".join(item["normalized"] for item in recent_texts[-6:])
    topics = []
    for rule in DOCTOR_PENDING_TOPIC_RULES:
        if not any(pattern in combined for pattern in rule["patterns"]):
            continue
        evidence = ""
        for item in reversed(recent_texts):
            if any(pattern in item["normalized"] for pattern in rule["patterns"]):
                evidence = brief(item["text"], 220)
                break
        topics.append(
            {
                "id": rule["id"],
                "title": rule["title"],
                "summary": rule["summary"],
                "evidence": evidence,
            }
        )
    return topics


def doctor_pending_schedules(limit=6):
    with crm_connect() as conn:
        rows = [
            dict(row)
            for row in conn.execute(
                "SELECT id, status, provider, action, due_at, timezone, payload_json FROM scheduled_actions WHERE status='pending' ORDER BY due_at ASC LIMIT ?",
                (max(1, min(int(limit or 6), 20)),),
            ).fetchall()
        ]
    schedules = []
    for row in rows:
        payload = {}
        try:
            payload = json.loads(row.get("payload_json") or "{}")
        except json.JSONDecodeError:
            payload = {}
        target_parameters = payload.get("_target_parameters") if isinstance(payload.get("_target_parameters"), dict) else {}
        follow_up_action = target_parameters.get("follow_up_action") if isinstance(target_parameters, dict) else {}
        schedules.append(
            {
                "id": row.get("id"),
                "provider": payload.get("_target_provider") or row.get("provider") or "",
                "action": payload.get("_target_action") or row.get("action") or "",
                "due_at": row.get("due_at") or "",
                "timezone": row.get("timezone") or "",
                "recurrence": payload.get("_recurrence") or "",
                "label": payload.get("_schedule_label") or "",
                "follow_up_action": follow_up_action.get("target_action", "") if isinstance(follow_up_action, dict) else "",
            }
        )
    return schedules


def doctor_pending_whatsapp_threads(limit=5):
    payload = read_json_file_any([WHATSAPP_THREAD_INDEX, RUNTIME_WHATSAPP_THREAD_INDEX], {"threads": []})
    rows = []
    for item in payload.get("threads") or []:
        if not isinstance(item, dict):
            continue
        open_items = int(item.get("open_items") or 0)
        if open_items <= 0:
            continue
        rows.append(
            {
                "thread_id": item.get("thread_id") or "",
                "display_name": item.get("display_name") or item.get("phone") or "",
                "phone": item.get("phone") or "",
                "open_items": open_items,
                "latest_at": item.get("latest_at") or "",
            }
        )
    rows.sort(key=lambda item: (item.get("latest_at") or "", item.get("open_items") or 0), reverse=True)
    return rows[: max(1, min(int(limit or 5), 10))]


def doctor_pending_report(parameters=None):
    parameters = parameters or {}
    lookback_days = max(1, min(int(first_value(parameters, "days", "lookback_days", default=3) or 3), 14))
    event_limit = max(10, min(int(first_value(parameters, "event_limit", default=120) or 120), 500))
    events = load_recent_memory_events(
        days=lookback_days,
        kinds={"conversation_note", "execution_request", "api_bridge_action", "kim_action_scheduled", "kim_recurring_action_rescheduled"},
        limit=event_limit,
    )
    topics = doctor_pending_topics(events)
    whatsapp_rows = doctor_pending_whatsapp_threads(limit=5)
    schedules = doctor_pending_schedules(limit=8)
    schedule_titles = [item for item in schedules if item.get("provider") == "crm" and item.get("action") == "doctor_pending_report"]
    lines = [
        f"Pendientes Kim ({now_iso()}): {len(topics)} frente(s), {len(whatsapp_rows)} hilo(s) WhatsApp accionables, {len(schedules)} accion(es) programadas pendientes.",
    ]
    if topics:
        lines.append("Frentes prioritarios:")
        for index, item in enumerate(topics[:6], start=1):
            lines.append(f"{index}. {item['title']}: {item['summary']}")
    else:
        lines.append("No detecte frentes priorizados recientes en memoria conversacional.")
    if whatsapp_rows:
        lines.append("WhatsApp accionable:")
        for item in whatsapp_rows[:3]:
            lines.append(f"- {item['display_name']} | open_items={item['open_items']} | ultimo={item['latest_at']}")
    if schedules:
        lines.append("Proximas acciones programadas:")
        for item in schedules[:4]:
            recurrence = f" | repite={item['recurrence']}" if item.get("recurrence") else ""
            lines.append(f"- {item['provider']}/{item['action']} @ {item['due_at']}{recurrence}")
    if not schedule_titles:
        lines.append("Alerta: no existe aun una rutina diaria activa de crm/doctor_pending_report.")
    summary = "\n".join(lines)
    return {
        "ok": True,
        "provider": "crm",
        "action": "doctor_pending_report",
        "generated_at": now_iso(),
        "lookback_days": lookback_days,
        "priority_count": len(topics),
        "topics": topics,
        "actionable_whatsapp_threads": whatsapp_rows,
        "pending_schedules": schedules,
        "has_daily_doctor_pending_schedule": bool(schedule_titles),
        "summary": summary,
        "message": summary,
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
            "sync_call_attempts",
            "whatsapp_report",
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
    media_raw = first_value(parameters, "media_url", "mediaUrl", "MediaUrl", "image_url", "imageUrl", default=None)
    media_urls = media_raw if isinstance(media_raw, list) else ([media_raw] if media_raw else [])
    media_urls = [str(item).strip() for item in media_urls if str(item or "").strip()]
    content_sid = str(first_value(parameters, "content_sid", "ContentSid", "template_sid", default="") or "").strip()
    content_variables_raw = first_value(parameters, "content_variables", "ContentVariables", "template_variables", default=None)
    if isinstance(content_variables_raw, (dict, list)):
        content_variables = json.dumps(content_variables_raw, ensure_ascii=False)
    else:
        content_variables = str(content_variables_raw or "").strip()
    from_number = normalize_phone_number(first_value(parameters, "from", "from_number", "sender", default=twilio_default_from_number()))
    messaging_service_sid = str(first_value(parameters, "messaging_service_sid", "service_sid", default="") or "").strip()
    if channel == "whatsapp":
        if to and not to.startswith("whatsapp:"):
            to = f"whatsapp:{to}"
        if from_number and not from_number.startswith("whatsapp:"):
            from_number = f"whatsapp:{from_number}"
    if not to:
        raise ValueError("Falta destinatario to para Twilio.")
    if not body and not content_sid:
        raise ValueError("Falta body/message o content_sid/template_sid para Twilio.")
    if not from_number and not messaging_service_sid:
        raise ValueError("Falta from_number o messaging_service_sid para Twilio.")
    allow_unknown_contact = boolish(
        first_value(
            parameters or {},
            "allow_unknown_contact",
            "allow_unregistered_recipient",
            "allow_ad_hoc_recipient",
            default=False,
        )
    )
    crm_lookup_phone = twilio_lookup_phone_number(to)
    doctor_control_recipient = crm_lookup_phone == DOCTOR_DUBAI_WHATSAPP_NUMBER
    recipient_contact = crm_find_contact_by_phone(crm_lookup_phone) if crm_lookup_phone else {}
    recipient_contact = recipient_contact or {}
    if doctor_control_recipient:
        pipedrive_guard = {
            "registered": True,
            "reason": "doctor_control_recipient",
            "message": "Destino de control del Dr. Yehoshua; no requiere validacion Pipedrive.",
            "person": {},
            "candidates": [],
        }
    else:
        pipedrive_guard = pipedrive_registered_person_for_phone(crm_lookup_phone)
    whatsapp_unknown_inbound_reply = channel == "whatsapp" and allow_unknown_contact
    if not pipedrive_guard.get("registered") and not doctor_control_recipient and not whatsapp_unknown_inbound_reply:
        append_memory(
            "twilio_message_blocked_unregistered_pipedrive",
            {
                "to": crm_lookup_phone,
                "channel": channel,
                "reason": pipedrive_guard.get("reason"),
                "message": pipedrive_guard.get("message"),
                "candidate_names": [item.get("name") for item in pipedrive_guard.get("candidates") or []],
            },
        )
        raise ValueError(
            f"{pipedrive_guard.get('message')} "
            "Regla activa: Kim solo puede enviar SMS, llamadas o WhatsApp proactivo a personas registradas en Pipedrive. "
            "WhatsApp inbound iniciado por el usuario puede responderse con contexto publico y aislado. "
            "Primero crea/sincroniza la persona en Pipedrive y vuelve a intentar."
        )
    recipient_label = (
        recipient_contact.get("display_name")
        or ("Dr. Yehoshua (Dubai control)" if doctor_control_recipient else "")
        or crm_lookup_phone
        or to
    )
    pipedrive_person = pipedrive_guard.get("person") or {}
    preferred_pipedrive_id = str(first_value(parameters, "pipedrive_person_id", "person_id", default="") or "").strip()
    if preferred_pipedrive_id:
        for candidate in [pipedrive_person, *list(pipedrive_guard.get("candidates") or [])]:
            if str((candidate or {}).get("id") or "") == preferred_pipedrive_id:
                pipedrive_person = candidate or pipedrive_person
                break
    if pipedrive_person.get("name"):
        recipient_label = pipedrive_person.get("name")
    return {
        "to": to,
        "from": from_number,
        "messaging_service_sid": messaging_service_sid,
        "content_sid": content_sid,
        "content_variables": content_variables,
        "body_preview": brief(body, 600),
        "body_length": len(body),
        "media_urls": media_urls,
        "channel": channel,
        "crm_lookup_phone": crm_lookup_phone,
        "recipient_label": recipient_label,
        "recipient_contact": {
            "id": recipient_contact.get("id"),
            "display_name": recipient_contact.get("display_name"),
            "phone_e164": recipient_contact.get("phone_e164"),
            "contact_type": recipient_contact.get("contact_type"),
        } if recipient_contact else {},
        "pipedrive_required": not doctor_control_recipient and not whatsapp_unknown_inbound_reply,
        "pipedrive_recipient": pipedrive_person,
        "pipedrive_match": {
            "registered": pipedrive_guard.get("registered"),
            "reason": pipedrive_guard.get("reason"),
            "message": pipedrive_guard.get("message"),
        },
        "allow_unknown_contact": allow_unknown_contact,
        "whatsapp_unknown_inbound_reply": whatsapp_unknown_inbound_reply,
        "doctor_control_recipient": doctor_control_recipient,
    }


def record_outbound_context_expansion(parameters, preview, event, channel="sms"):
    parameters = parameters or {}
    body_preview = preview.get("body_preview") or brief(first_value(parameters, "body", "message", "text", "content", "mensaje", default=""), 500)
    explicit_context_id = str(first_value(parameters, "context_id", "kim_context_id", "context_block_id", default="") or "").strip()
    context_id = twilio_context_block_id({"context_id": explicit_context_id or f"EXPAND-{event.get('sid') or secrets.token_hex(4).upper()}"})
    label = str(first_value(parameters, "contact_name", "client_name", "name", "nombre", default=preview.get("recipient_label") or preview.get("to")) or "").strip()
    context = {
        "id": context_id,
        "context_block_id": context_id,
        "status": "messaged",
        "created_at": now_iso(),
        "source": "kim_live_context_expansion",
        "direction": "outbound",
        "channel": channel,
        "context_scope": "single_contact",
        "workflow_target": "crm_then_memory",
        "to": preview.get("to", ""),
        "from": preview.get("from", ""),
        "contact_name": label,
        "relationship": first_value(parameters, "relationship", "relacion", "role", "rol", default="client"),
        "company": first_value(parameters, "company", "empresa", default=""),
        "objective": first_value(
            parameters,
            "objective",
            "goal",
            "objetivo",
            default=f"Mantener hilo de seguimiento con {label or preview.get('to')}.",
        ),
        "call_context": (
            "Expansion de campo de informacion humana: Kim envio o registro un recordatorio/mensaje saliente "
            f"por {channel.upper()} para sembrar continuidad con esta persona. "
            f"Mensaje enviado: {body_preview}. "
            "Si esta persona llama despues, Kim debe responder desde este hilo propio, no desde memoria general, "
            "y continuar el seguimiento con privacidad por contacto."
        ),
        "instructions": (
            "Si el contacto llama, saluda por nombre si esta identificado, explica que tienes el seguimiento previo, "
            "confirma que es la persona correcta y continua solo con sus asuntos propios. No reveles contexto de terceros."
        ),
        "questions": first_value(parameters, "questions", "preguntas", default="Pregunta si ya pudo revisar el mensaje y que necesita para avanzar."),
        "message_to_deliver": body_preview,
        "report_to_doctor": "Guardar respuesta, estado del seguimiento, objeciones y siguiente paso recomendado.",
        "success_criteria": "El hilo del contacto queda listo para una llamada entrante futura con contexto propio.",
        "next_step_hint": first_value(parameters, "next_step_hint", "followup_hint", default=body_preview),
        "last_outbound_channel": channel,
        "last_sms_sid": event.get("sid", ""),
        "last_sms_status": event.get("status", ""),
        "last_sms_body_preview": body_preview,
        "last_sms_at": event.get("sent_at") or now_iso(),
    }
    store_twilio_call_context(context)
    append_memory(
        "human_information_field_expanded",
        {
            "context_id": context_id,
            "channel": channel,
            "to": preview.get("to", ""),
            "contact_name": label,
            "summary": brief(context["call_context"], 400),
        },
    )
    return context_id


def twilio_send_message(parameters, confirm=False, channel="sms"):
    parameters = parameters or {}
    preview = twilio_message_preview(parameters, channel=channel)
    context_id = str(first_value(parameters, "context_id", "kim_context_id", "context_block_id", default="") or "").strip()
    call_sid = str(first_value(parameters, "call_sid", default="") or "").strip()
    payload = {
        "To": preview["to"],
    }
    if preview.get("content_sid"):
        payload["ContentSid"] = preview["content_sid"]
        if preview.get("content_variables"):
            payload["ContentVariables"] = preview["content_variables"]
    else:
        payload["Body"] = str(first_value(parameters, "body", "message", "text", "content", "mensaje") or "").strip()
    for media_url in preview.get("media_urls") or []:
        payload.setdefault("MediaUrl", []).append(media_url)
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
            f"Enviar {channel.upper()} Twilio a {preview['recipient_label']}.",
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
        "context_id": context_id,
        "call_sid": call_sid,
        "recipient_label": preview.get("recipient_label", ""),
        "recipient_contact_id": (preview.get("recipient_contact") or {}).get("id", ""),
        "pipedrive_person_id": (preview.get("pipedrive_recipient") or {}).get("id", ""),
        "pipedrive_person_name": (preview.get("pipedrive_recipient") or {}).get("name", ""),
        "content_sid": preview.get("content_sid", ""),
        "media_urls": preview.get("media_urls") or [],
        "error_code": result.get("error_code"),
        "error_message": result.get("error_message"),
        "confirmed": True,
        "sent_at": now_iso(),
    }
    if not context_id and not call_sid:
        context_id = record_outbound_context_expansion(parameters, preview, event, channel=channel)
        event["context_id"] = context_id
    append_jsonl_any([TWILIO_SMS_LOG, RUNTIME_TWILIO_SMS_LOG], event)
    append_memory("twilio_message_sent", event)
    if context_id or call_sid:
        update_twilio_call_context(
            context_id=context_id,
            call_sid=call_sid,
            updates={
                "last_outbound_channel": channel,
                "last_sms_sid": result.get("sid", ""),
                "last_sms_status": result.get("status", ""),
                "last_sms_body_preview": preview.get("body_preview", ""),
                "last_sms_at": event["sent_at"],
            },
        )
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


def twilio_context_block_id(parameters=None):
    parameters = parameters or {}
    explicit = first_value(parameters, "context_block_id", "context_id", "kim_context_id", default="")
    explicit = re.sub(r"[^A-Za-z0-9_-]+", "-", str(explicit or "").strip()).strip("-")
    return explicit or twilio_call_context_id()


def twilio_context_scope(context):
    explicit = str(context.get("context_scope") or "").strip().lower()
    if explicit in {"bulk", "campaign", "mass"}:
        return "bulk_campaign"
    if explicit in {"single", "single_contact", "one_to_one"}:
        return "single_contact"
    if context.get("parent_context_id") or context.get("campaign_label"):
        return "bulk_campaign"
    return "single_contact"


def twilio_context_tags(context):
    tags = ["external_call", "phone"]
    scope = twilio_context_scope(context)
    tags.append(scope)
    if context.get("parent_context_id"):
        tags.append("child_context")
    if context.get("report_to_doctor"):
        tags.append("report_back")
    if context.get("workflow_target"):
        tags.append(str(context.get("workflow_target")))
    status = str(context.get("status") or "").strip().lower()
    if status:
        tags.append(f"status:{status}")
    unique = []
    seen = set()
    for tag in tags:
        clean = re.sub(r"[^a-z0-9:_-]+", "-", str(tag or "").strip().lower()).strip("-")
        if not clean or clean in seen:
            continue
        seen.add(clean)
        unique.append(clean)
    return unique


def load_external_call_context_block_state():
    state = {"blocks": {}}
    for path in [EXTERNAL_CALL_CONTEXT_BLOCKS, RUNTIME_EXTERNAL_CALL_CONTEXT_BLOCKS]:
        payload = read_json_file(path, {})
        if not isinstance(payload, dict):
            continue
        blocks = payload.get("blocks", {})
        if isinstance(blocks, dict):
            state["blocks"].update(blocks)
        if payload.get("updated_at"):
            state["updated_at"] = payload.get("updated_at")
    state.setdefault("blocks", {})
    return state


def save_external_call_context_block_state(state):
    state["updated_at"] = now_iso()
    last_error = None
    wrote = False
    for path in [EXTERNAL_CALL_CONTEXT_BLOCKS, RUNTIME_EXTERNAL_CALL_CONTEXT_BLOCKS]:
        try:
            write_json_file(path, state)
            wrote = True
        except (PermissionError, OSError) as exc:
            last_error = exc
    if not wrote and last_error:
        raise last_error


def external_call_context_block_markdown(block):
    attempts = block.get("attempts") or []
    lines = [
        f"# {block.get('block_id') or block.get('id') or 'CTX'}",
        "",
        f"- Title: {block.get('title') or block.get('contact_name') or block.get('to') or 'External Call'}",
        f"- Status: {block.get('status') or 'prepared'}",
        f"- Scope: {block.get('scope') or 'single_contact'}",
        f"- Workflow: {block.get('workflow_target') or 'pipedrive_then_clickup'}",
        f"- Tags: {', '.join(block.get('tags') or []) or 'external_call, phone'}",
        f"- Created: {block.get('created_at') or ''}",
        f"- Updated: {block.get('updated_at') or ''}",
    ]
    if block.get("parent_context_id"):
        lines.append(f"- Parent block: {block.get('parent_context_id')}")
    if block.get("campaign_label"):
        lines.append(f"- Campaign: {block.get('campaign_label')}")
    if block.get("source_session_id"):
        lines.append(f"- Source session: {block.get('source_session_id')}")
    lines.extend(
        [
            "",
            "## Context",
            "",
            f"- Contact: {block.get('contact_name') or ''}",
            f"- Company: {block.get('company') or ''}",
            f"- Relationship: {block.get('relationship') or ''}",
            f"- To: {block.get('to') or ''}",
            f"- From: {block.get('from') or ''}",
            f"- Objective: {block.get('objective') or ''}",
            f"- Call context: {block.get('call_context') or ''}",
            f"- Questions: {block.get('questions') or ''}",
            f"- Message to deliver: {block.get('message_to_deliver') or ''}",
            f"- Report to doctor: {block.get('report_to_doctor') or ''}",
            f"- Success criteria: {block.get('success_criteria') or ''}",
            f"- Next step hint: {block.get('next_step_hint') or ''}",
            "",
            "## Attempts",
            "",
        ]
    )
    if attempts:
        for item in attempts[-20:]:
            lines.append(
                f"- {item.get('at') or ''} | {item.get('status') or ''} | "
                f"{item.get('call_sid') or 'sin-call-sid'} | to={item.get('to') or ''}"
            )
    else:
        lines.append("- Sin intentos registrados todavia.")
    if block.get("summary"):
        lines.extend(["", "## Latest Summary", "", block.get("summary") or ""])
    if any(block.get(key) for key in ["last_outbound_channel", "last_sms_sid", "last_sms_status", "last_sms_body_preview", "last_sms_at"]):
        lines.extend(
            [
                "",
                "## Latest Follow-up Sync",
                "",
                f"- Channel: {block.get('last_outbound_channel') or ''}",
                f"- Message SID: {block.get('last_sms_sid') or ''}",
                f"- Status: {block.get('last_sms_status') or ''}",
                f"- Sent at: {block.get('last_sms_at') or ''}",
                f"- Body preview: {block.get('last_sms_body_preview') or ''}",
            ]
        )
    if block.get("transcript_path"):
        lines.extend(["", "## Transcript Path", "", f"- {block.get('transcript_path')}"])
    return "\n".join(lines).strip() + "\n"


def sync_external_call_context_block(context):
    context = context or {}
    block_id = str(context.get("context_block_id") or context.get("id") or "").strip()
    if not block_id:
        return {}
    state = load_external_call_context_block_state()
    current = dict(state.get("blocks", {}).get(block_id) or {})
    attempts = [item for item in current.get("attempts", []) if isinstance(item, dict)]
    call_sid = str(context.get("call_sid") or "").strip()
    status = str(
        context.get("twilio_status")
        or context.get("last_call_status")
        or context.get("status")
        or current.get("status")
        or "prepared"
    ).strip()
    if call_sid:
        attempt = {
            "call_sid": call_sid,
            "status": status,
            "to": context.get("to") or current.get("to") or "",
            "from": context.get("from") or current.get("from") or "",
            "at": context.get("last_status_at") or context.get("updated_at") or now_iso(),
            "transcript_path": context.get("transcript_path") or "",
        }
        replaced = False
        for index, item in enumerate(attempts):
            if item.get("call_sid") == call_sid:
                attempts[index] = {**item, **attempt}
                replaced = True
                break
        if not replaced:
            attempts.append(attempt)
    block = {
        **current,
        "block_id": block_id,
        "id": block_id,
        "title": current.get("title") or context.get("campaign_label") or context.get("contact_name") or context.get("to") or block_id,
        "status": status,
        "scope": twilio_context_scope(context),
        "channel": context.get("channel") or current.get("channel") or "phone",
        "tags": twilio_context_tags(context),
        "workflow_target": context.get("workflow_target") or current.get("workflow_target") or "pipedrive_then_clickup",
        "parent_context_id": context.get("parent_context_id") or current.get("parent_context_id") or "",
        "campaign_label": context.get("campaign_label") or current.get("campaign_label") or "",
        "source_session_id": context.get("source_session_id") or current.get("source_session_id") or "",
        "contact_name": context.get("contact_name") or current.get("contact_name") or "",
        "company": context.get("company") or current.get("company") or "",
        "relationship": context.get("relationship") or current.get("relationship") or "",
        "to": context.get("to") or current.get("to") or "",
        "from": context.get("from") or current.get("from") or "",
        "objective": context.get("objective") or current.get("objective") or "",
        "call_context": context.get("call_context") or current.get("call_context") or "",
        "instructions": context.get("instructions") or current.get("instructions") or "",
        "questions": context.get("questions") or current.get("questions") or "",
        "message_to_deliver": context.get("message_to_deliver") or current.get("message_to_deliver") or "",
        "report_to_doctor": context.get("report_to_doctor") or current.get("report_to_doctor") or "",
        "success_criteria": context.get("success_criteria") or current.get("success_criteria") or "",
        "next_step_hint": context.get("next_step_hint") or current.get("next_step_hint") or "",
        "last_outbound_channel": context.get("last_outbound_channel") or current.get("last_outbound_channel") or "",
        "last_sms_sid": context.get("last_sms_sid") or current.get("last_sms_sid") or "",
        "last_sms_status": context.get("last_sms_status") or current.get("last_sms_status") or "",
        "last_sms_body_preview": context.get("last_sms_body_preview") or current.get("last_sms_body_preview") or "",
        "last_sms_at": context.get("last_sms_at") or current.get("last_sms_at") or "",
        "call_sid": call_sid or current.get("call_sid") or "",
        "transcript_path": context.get("transcript_path") or current.get("transcript_path") or "",
        "summary": context.get("summary") or current.get("summary") or "",
        "attempt_count": len(attempts),
        "attempts": attempts,
        "created_at": current.get("created_at") or context.get("created_at") or now_iso(),
        "updated_at": now_iso(),
    }
    state["blocks"][block_id] = block
    save_external_call_context_block_state(state)
    markdown = external_call_context_block_markdown(block)
    write_text_file_any(
        [
            EXTERNAL_CALL_CONTEXT_BLOCKS_DIR / f"{block_id}.md",
            RUNTIME_EXTERNAL_CALL_CONTEXT_BLOCKS_DIR / f"{block_id}.md",
        ],
        markdown,
    )
    try:
        build_person_context_index()
    except Exception as exc:
        append_memory("person_context_index_error", {"error": brief(str(exc), 500), "context_block_id": block_id})
    return block


def queue_twilio_realtime_sync(context, trigger="context_update", changed_fields=None):
    context = context or {}
    context_id = str(context.get("id") or context.get("context_block_id") or "").strip()
    call_sid = str(context.get("call_sid") or "").strip()
    if not context_id and not call_sid:
        return {}
    event = {
        "event_id": "RTSYNC-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S-") + secrets.token_hex(3).upper(),
        "at": now_iso(),
        "trigger": str(trigger or "context_update").strip() or "context_update",
        "context_id": context_id,
        "call_sid": call_sid,
        "status": str(context.get("status") or "").strip(),
        "contact_name": str(context.get("contact_name") or "").strip(),
        "changed_fields": sorted({str(item).strip() for item in (changed_fields or []) if str(item).strip()}),
    }
    append_jsonl_any([TWILIO_REALTIME_SYNC_QUEUE, RUNTIME_TWILIO_REALTIME_SYNC_QUEUE], event)
    return event


def person_context_key(name="", phone="", email=""):
    clean_name = str(name or "").strip()
    clean_phone = normalize_phone_number(phone)
    clean_email = str(email or "").strip().lower()
    if clean_name and not clean_name.startswith("+"):
        return "person:" + crm_slug(clean_name)
    if clean_phone:
        return "phone:" + clean_phone
    if clean_email:
        return "email:" + clean_email
    return "person:sin-identificar"


def person_context_title(record):
    return record.get("display_name") or record.get("name") or next(iter(record.get("phones", [])), "") or record.get("key", "Persona")


def ensure_person_context(index, name="", phone="", email=""):
    key = person_context_key(name=name, phone=phone, email=email)
    record = index.setdefault(
        key,
        {
            "key": key,
            "display_name": str(name or "").strip() or str(phone or email or "Persona sin identificar"),
            "phones": [],
            "emails": [],
            "companies": [],
            "contact_ids": [],
            "contact_types": [],
            "sources": [],
            "notes": [],
            "context_blocks": [],
            "interactions": [],
            "scheduled_actions": [],
            "latest_status": "",
            "latest_interaction_at": "",
            "next_step_hint": "",
        },
    )
    if name and (not record.get("display_name") or record.get("display_name", "").startswith("+")):
        record["display_name"] = str(name).strip()
    phone = normalize_phone_number(phone)
    if phone and phone not in record["phones"]:
        record["phones"].append(phone)
    email = str(email or "").strip().lower()
    if email and email not in record["emails"]:
        record["emails"].append(email)
    return record


def compact_unique(items, limit=20):
    output = []
    for item in items or []:
        if item in (None, ""):
            continue
        clean = str(item).strip()
        if clean and clean not in output:
            output.append(clean)
        if len(output) >= limit:
            break
    return output


def person_context_markdown(record):
    title = person_context_title(record)
    lines = [
        f"# {title}",
        "",
        f"- Key: {record.get('key')}",
        f"- Updated: {record.get('updated_at') or now_iso()}",
        f"- Phones: {', '.join(record.get('phones') or []) or 'N/A'}",
        f"- Emails: {', '.join(record.get('emails') or []) or 'N/A'}",
        f"- Companies: {', '.join(record.get('companies') or []) or 'N/A'}",
        f"- Contact IDs: {', '.join(record.get('contact_ids') or []) or 'N/A'}",
        f"- Contact types: {', '.join(record.get('contact_types') or []) or 'N/A'}",
        f"- Latest status: {record.get('latest_status') or 'N/A'}",
        f"- Latest interaction: {record.get('latest_interaction_at') or 'N/A'}",
        f"- Next step hint: {record.get('next_step_hint') or 'N/A'}",
        "",
        "## Notes",
        "",
    ]
    notes = compact_unique(record.get("notes", []), limit=10)
    lines.extend([f"- {note}" for note in notes] or ["- Sin notas consolidadas."])
    lines.extend(["", "## Context Blocks", ""])
    blocks = sorted(record.get("context_blocks") or [], key=lambda item: item.get("updated_at") or item.get("created_at") or "", reverse=True)
    if blocks:
        for block in blocks[:30]:
            lines.append(
                f"- {block.get('block_id')} | {block.get('status') or ''} | "
                f"{block.get('objective') or block.get('call_context') or ''} | attempts={block.get('attempt_count', 0)}"
            )
    else:
        lines.append("- Sin context blocks.")
    lines.extend(["", "## Interactions", ""])
    interactions = sorted(record.get("interactions") or [], key=lambda item: item.get("occurred_at") or item.get("created_at") or "", reverse=True)
    if interactions:
        for item in interactions[:40]:
            target = item.get("transcript_path") or item.get("external_sid") or ""
            lines.append(f"- {item.get('occurred_at') or ''} | {item.get('channel')} | {item.get('status')} | {target}")
    else:
        lines.append("- Sin interacciones registradas.")
    lines.extend(["", "## Scheduled Actions", ""])
    scheduled = sorted(record.get("scheduled_actions") or [], key=lambda item: item.get("due_at") or "", reverse=True)
    if scheduled:
        for item in scheduled[:20]:
            lines.append(f"- {item.get('due_at')} | {item.get('status')} | {item.get('action')} | attempts={item.get('attempts')}")
    else:
        lines.append("- Sin acciones programadas pendientes o historicas.")
    return "\n".join(lines).strip() + "\n"


def build_person_context_index():
    index = {}
    contacts_by_id = {}
    contacts_by_phone = {}
    contacts_by_name = {}

    def contact_by_name_hint(name):
        return {}

    try:
        with crm_connect() as conn:
            contacts = [
                dict(row)
                for row in conn.execute(
                    """
                    SELECT c.*, co.name AS company_name
                    FROM contacts c
                    LEFT JOIN companies co ON co.id = c.company_id
                    ORDER BY c.updated_at DESC
                    """
                ).fetchall()
            ]
            for contact in contacts:
                record = ensure_person_context(
                    index,
                    name=contact.get("display_name"),
                    phone=contact.get("phone_e164"),
                    email=contact.get("email"),
                )
                contacts_by_id[contact.get("id")] = contact
                phone = normalize_phone_number(contact.get("phone_e164"))
                if phone:
                    contacts_by_phone[phone] = contact
                name_key = normalize_security_text(contact.get("display_name"))
                if name_key:
                    contacts_by_name[name_key] = contact
                for key, target in [
                    ("id", "contact_ids"),
                    ("contact_type", "contact_types"),
                    ("source", "sources"),
                    ("company_name", "companies"),
                    ("notes", "notes"),
                ]:
                    value = contact.get(key)
                    if value and value not in record[target]:
                        record[target].append(value)

            def contact_by_name_hint(name):
                clean_name = normalize_security_text(name)
                if not clean_name:
                    return {}
                if contacts_by_name.get(clean_name):
                    return contacts_by_name[clean_name]
                terms = person_context_match_terms(clean_name)
                best_score = 0
                best_contact = {}
                for contact in contacts_by_id.values():
                    haystack = normalize_security_text(
                        " ".join(
                            str(contact.get(key) or "")
                            for key in ["display_name", "email", "company_name", "contact_type", "notes"]
                        )
                    )
                    compact_haystack = re.sub(r"[^a-z0-9]+", "", haystack)
                    consonant_haystack = re.sub(r"[aeiou]+", "", compact_haystack)
                    score = 0
                    for term in terms:
                        if not term:
                            continue
                        if term == normalize_security_text(contact.get("display_name")):
                            score += 25
                        elif term in haystack:
                            score += 12 if " " in term else 7
                        elif term in compact_haystack:
                            score += 6
                        elif len(term) >= 2 and term in consonant_haystack:
                            score += 4
                    if score > best_score:
                        best_score = score
                        best_contact = contact
                return best_contact if best_score >= 6 else {}

            interactions = [
                dict(row)
                for row in conn.execute(
                    "SELECT * FROM interactions ORDER BY occurred_at DESC LIMIT 1200"
                ).fetchall()
            ]
            for item in interactions:
                contact = contacts_by_id.get(item.get("contact_id")) or {}
                phone = item.get("to_value") if item.get("direction") == "outbound" else item.get("from_value")
                phone = normalize_phone_number(phone)
                if not contact and phone:
                    contact = contacts_by_phone.get(phone) or {}
                record = ensure_person_context(
                    index,
                    name=contact.get("display_name") or phone,
                    phone=contact.get("phone_e164") or phone,
                    email=contact.get("email"),
                )
                slim = {
                    "id": item.get("id"),
                    "channel": item.get("channel"),
                    "direction": item.get("direction"),
                    "provider": item.get("provider"),
                    "external_sid": item.get("external_sid"),
                    "status": item.get("status"),
                    "from": item.get("from_value"),
                    "to": item.get("to_value"),
                    "body": brief(item.get("body") or "", 500),
                    "transcript_path": item.get("transcript_path"),
                    "occurred_at": item.get("occurred_at"),
                    "created_at": item.get("created_at"),
                }
                record["interactions"].append(slim)
                if not record.get("latest_interaction_at") or str(item.get("occurred_at") or "") > str(record.get("latest_interaction_at") or ""):
                    record["latest_interaction_at"] = item.get("occurred_at") or ""
                    record["latest_status"] = item.get("status") or ""
            scheduled = [
                dict(row)
                for row in conn.execute(
                    "SELECT * FROM scheduled_actions ORDER BY due_at DESC LIMIT 300"
                ).fetchall()
            ]
            for item in scheduled:
                payload = parse_json_object_from_text(item.get("payload_json") or "")
                target_parameters = payload.get("_target_parameters") if isinstance(payload.get("_target_parameters"), dict) else {}
                scheduled_name = first_value(target_parameters, "contact_name", "client_name", "name", "nombre", default="")
                named_contact = contact_by_name_hint(scheduled_name) if scheduled_name else {}
                contact = named_contact or contacts_by_id.get(item.get("contact_id")) or contacts_by_phone.get(normalize_phone_number(item.get("to_value"))) or {}
                record_phone = contact.get("phone_e164") or ("" if named_contact else item.get("to_value"))
                record = ensure_person_context(
                    index,
                    name=contact.get("display_name") or scheduled_name or item.get("to_value"),
                    phone=record_phone,
                    email=contact.get("email"),
                )
                record["scheduled_actions"].append(
                    {
                        "id": item.get("id"),
                        "status": item.get("status"),
                        "action": item.get("action"),
                        "due_at": item.get("due_at"),
                        "attempts": item.get("attempts"),
                        "to": item.get("to_value"),
                    }
                )
    except Exception as exc:
        append_memory("person_context_crm_warning", {"error": brief(str(exc), 500)})
    state = load_external_call_context_block_state()
    for block in state.get("blocks", {}).values():
        phone = normalize_phone_number(block.get("to"))
        block_name = str(block.get("contact_name") or "").strip()
        named_contact = contact_by_name_hint(block_name) if block_name else {}
        phone_contact = contacts_by_phone.get(phone) or {}
        contact = named_contact or phone_contact
        record_phone = contact.get("phone_e164") or ("" if named_contact else phone)
        record = ensure_person_context(
            index,
            name=contact.get("display_name") or block_name or phone,
            phone=record_phone,
            email=contact.get("email"),
        )
        if block.get("company") and block.get("company") not in record["companies"]:
            record["companies"].append(block.get("company"))
        if block.get("next_step_hint") and not record.get("next_step_hint"):
            record["next_step_hint"] = block.get("next_step_hint")
        record["context_blocks"].append(
            {
                "block_id": block.get("block_id") or block.get("id"),
                "status": block.get("status"),
                "scope": block.get("scope"),
                "workflow_target": block.get("workflow_target"),
                "objective": brief(block.get("objective") or "", 500),
                "call_context": brief(block.get("call_context") or "", 500),
                "next_step_hint": brief(block.get("next_step_hint") or "", 300),
                "attempt_count": block.get("attempt_count", len(block.get("attempts") or [])),
                "transcript_path": block.get("transcript_path"),
                "created_at": block.get("created_at"),
                "updated_at": block.get("updated_at"),
            }
        )
        if not record.get("latest_interaction_at") or str(block.get("updated_at") or "") > str(record.get("latest_interaction_at") or ""):
            record["latest_interaction_at"] = block.get("updated_at") or ""
            record["latest_status"] = block.get("status") or record.get("latest_status") or ""
    people = []
    for record in index.values():
        record["phones"] = compact_unique(record.get("phones", []), limit=10)
        record["emails"] = compact_unique(record.get("emails", []), limit=10)
        record["companies"] = compact_unique(record.get("companies", []), limit=10)
        record["contact_ids"] = compact_unique(record.get("contact_ids", []), limit=10)
        record["contact_types"] = compact_unique(record.get("contact_types", []), limit=8)
        record["sources"] = compact_unique(record.get("sources", []), limit=8)
        record["notes"] = compact_unique(record.get("notes", []), limit=20)
        record["updated_at"] = now_iso()
        slug = crm_slug(person_context_title(record))
        record["markdown_path"] = str(PERSON_CONTEXT_DIR / f"{slug}.md")
        markdown = person_context_markdown(record)
        written = write_text_file_both(PERSON_CONTEXT_DIR / f"{slug}.md", RUNTIME_PERSON_CONTEXT_DIR / f"{slug}.md", markdown)
        if written:
            record["markdown_path"] = written[0]
        people.append(record)
    payload = {
        "updated_at": now_iso(),
        "count": len(people),
        "purpose": "Indice por persona: contacto, CRM, Pipedrive mirror, llamadas, context blocks, transcripts e intentos.",
        "rule": "Antes de llamar o responder por una persona, Kim debe consultar este indice y luego los transcripts/context blocks citados.",
        "people": sorted(people, key=lambda item: (item.get("latest_interaction_at") or "", item.get("display_name") or ""), reverse=True),
    }
    write_json_file_both(PERSON_CONTEXT_INDEX, RUNTIME_PERSON_CONTEXT_INDEX, payload)
    return payload


def load_person_context_people(rebuild=False):
    payload = read_json_file_any([PERSON_CONTEXT_INDEX, RUNTIME_PERSON_CONTEXT_INDEX], {})
    people = payload.get("people") if isinstance(payload, dict) else None
    if people:
        return people
    if rebuild:
        try:
            return build_person_context_index().get("people", [])
        except Exception as exc:
            append_memory("person_context_index_reload_error", {"error": brief(str(exc), 500)})
    return []


def person_context_record_for_phone(phone, rebuild=False):
    normalized = normalize_phone_number(phone)
    if not normalized:
        return {}
    for record in load_person_context_people(rebuild=rebuild):
        phones = [normalize_phone_number(item) for item in record.get("phones") or []]
        if normalized in phones:
            return record
    return {}


def person_context_match_terms(value):
    normalized = normalize_security_text(value)
    compact = re.sub(r"[^a-z0-9]+", "", normalized)
    consonants = re.sub(r"[aeiou]+", "", compact)
    terms = [normalized, compact, consonants]
    alias_map = {
        "nomi": ["naomi", "naomi rodriguez"],
        "naomi": ["nomi"],
        "dr y": ["dr yehoshua", "yehoshua", "doctor yehoshua"],
        "dr ye": ["dr yehoshua", "yehoshua", "doctor yehoshua"],
    }
    for alias in alias_map.get(normalized, []):
        alias_normalized = normalize_security_text(alias)
        alias_compact = re.sub(r"[^a-z0-9]+", "", alias_normalized)
        alias_consonants = re.sub(r"[aeiou]+", "", alias_compact)
        terms.extend([alias_normalized, alias_compact, alias_consonants])
    return [term for term in compact_unique(terms, limit=12) if term]


def person_context_record_blob(record):
    parts = [
        record.get("key"),
        person_context_title(record),
        " ".join(record.get("phones") or []),
        " ".join(record.get("emails") or []),
        " ".join(record.get("companies") or []),
        " ".join(record.get("contact_types") or []),
        " ".join(record.get("notes") or []),
    ]
    for block in record.get("context_blocks") or []:
        parts.extend(
            [
                block.get("block_id"),
                block.get("objective"),
                block.get("call_context"),
                block.get("next_step_hint"),
                block.get("status"),
            ]
        )
    for item in record.get("interactions") or []:
        parts.extend([item.get("body"), item.get("external_sid"), item.get("status"), item.get("channel")])
    return normalize_security_text(" ".join(str(part or "") for part in parts))


def person_context_score(record, query):
    query_terms = person_context_match_terms(query)
    if not query_terms:
        return 0
    blob = person_context_record_blob(record)
    compact_blob = re.sub(r"[^a-z0-9]+", "", blob)
    consonant_blob = re.sub(r"[aeiou]+", "", compact_blob)
    title = normalize_security_text(person_context_title(record))
    query_norm = normalize_security_text(query)
    query_phone = normalize_phone_number(query)
    company_terms = [normalize_security_text(company) for company in record.get("companies") or []]
    email_terms = [normalize_security_text(email) for email in record.get("emails") or []]
    phone_terms = [normalize_phone_number(phone) for phone in record.get("phones") or []]
    score = 0
    if query_norm and query_norm == title:
        score += 90
    if query_phone and query_phone in phone_terms:
        score += 100
    if query_norm and query_norm in email_terms:
        score += 90
    if query_norm and query_norm in company_terms:
        score += 42
    for term in query_terms:
        if not term:
            continue
        if term == title:
            score += 70
        elif term and term in title:
            score += 36
        elif term and any(term == company for company in company_terms):
            score += 32
        elif term and any(term in company for company in company_terms):
            score += 18
        elif term and any(term == email for email in email_terms):
            score += 36
        elif term and any(term in email for email in email_terms):
            score += 18
        elif query_phone and query_phone in phone_terms:
            score += 80
        elif term and term in blob:
            score += 6 if " " in term else 3
        elif term and term in compact_blob:
            score += 3
        elif len(term) >= 2 and term in consonant_blob:
            score += 2
    return score


def find_person_context_records(query="", limit=5, rebuild=False):
    query = str(query or "").strip()
    people = load_person_context_people(rebuild=rebuild)
    if not query:
        return people[:limit]
    scored = []
    for record in people:
        score = person_context_score(record, query)
        if score > 0:
            scored.append((score, record))
    if not scored and not rebuild:
        return find_person_context_records(query=query, limit=limit, rebuild=True)
    scored.sort(key=lambda item: (item[0], item[1].get("latest_interaction_at") or ""), reverse=True)
    return [record for _, record in scored[: max(1, min(int(limit or 5), 20))]]


def person_context_transcript_reports(record, limit=5):
    seen = set()
    reports = []
    candidates = []
    for block in record.get("context_blocks") or []:
        if block.get("transcript_path"):
            candidates.append(
                {
                    "kind": "context_block",
                    "status": block.get("status"),
                    "path": block.get("transcript_path"),
                    "at": block.get("updated_at") or block.get("created_at"),
                    "label": block.get("block_id"),
                }
            )
        for attempt in block.get("attempts") or []:
            if attempt.get("transcript_path"):
                candidates.append(
                    {
                        "kind": "call_attempt",
                        "status": attempt.get("status"),
                        "path": attempt.get("transcript_path"),
                        "at": attempt.get("at"),
                        "label": attempt.get("call_sid"),
                    }
                )
    for item in record.get("interactions") or []:
        if item.get("transcript_path"):
            candidates.append(
                {
                    "kind": item.get("channel") or "interaction",
                    "status": item.get("status"),
                    "path": item.get("transcript_path"),
                    "at": item.get("occurred_at") or item.get("created_at"),
                    "label": item.get("external_sid") or item.get("id"),
                }
            )
        elif item.get("body"):
            candidates.append(
                {
                    "kind": item.get("channel") or "interaction",
                    "status": item.get("status"),
                    "body": item.get("body"),
                    "at": item.get("occurred_at") or item.get("created_at"),
                    "label": item.get("external_sid") or item.get("id"),
                }
            )
    candidates.sort(key=lambda item: item.get("at") or "", reverse=True)
    for item in candidates:
        key = item.get("path") or item.get("label") or item.get("body")
        if not key or key in seen:
            continue
        seen.add(key)
        report = {key: item.get(key) for key in ["kind", "status", "path", "at", "label", "body"] if item.get(key)}
        if item.get("path"):
            path = pathlib.Path(item["path"])
            text = read_text_tail(path, limit=18000)
            if text:
                report["excerpt"] = brief(text, 1800)
        reports.append(report)
        if len(reports) >= limit:
            break
    return reports


def person_context_supervision_payload(query="", limit=1):
    try:
        requested_limit = int(limit or 1)
    except (TypeError, ValueError):
        requested_limit = 1
    requested_limit = max(1, min(requested_limit, 10))
    records = find_person_context_records(query=query, limit=requested_limit, rebuild=True)
    people = []
    for record in records:
        title = person_context_title(record)
        markdown_path = record.get("markdown_path") or str(PERSON_CONTEXT_DIR / f"{crm_slug(title)}.md")
        markdown = read_text_tail(pathlib.Path(markdown_path), limit=18000) if markdown_path else ""
        pending = person_context_pending_briefs(record, limit=5)
        calls = person_context_transcript_reports(record, limit=6)
        mode_prompt = (
            f"Modo {title}: carga solo el hilo propio de {title}. "
            "Usa CRM, context blocks, interacciones, transcripts y notas de esta ficha antes de contestar. "
            "Si el doctor esta simulando una llamada, atiende como Kim con este contexto de persona; "
            "no reveles datos de terceros ni pendientes generales del doctor. "
            "Si falta informacion, dilo y registra que debe actualizarse la ficha."
        )
        people.append(
            {
                "key": record.get("key"),
                "display_name": title,
                "phones": record.get("phones") or [],
                "emails": record.get("emails") or [],
                "companies": record.get("companies") or [],
                "contact_ids": record.get("contact_ids") or [],
                "contact_types": record.get("contact_types") or [],
                "latest_status": record.get("latest_status"),
                "latest_interaction_at": record.get("latest_interaction_at"),
                "next_step_hint": record.get("next_step_hint"),
                "pending": pending,
                "context_blocks": (record.get("context_blocks") or [])[:10],
                "interactions": (record.get("interactions") or [])[:12],
                "calls": calls,
                "markdown_path": markdown_path,
                "markdown_excerpt": brief(markdown, 2200),
                "mode_prompt": mode_prompt,
            }
        )
    active_person = people[0] if people else None
    candidate_summaries = [
        {
            "display_name": item.get("display_name"),
            "phones": item.get("phones") or [],
            "companies": item.get("companies") or [],
            "latest_interaction_at": item.get("latest_interaction_at"),
        }
        for item in people[1:]
    ]
    payload = {
        "ok": True,
        "provider": "crm",
        "action": "person_context",
        "query": query,
        "count": len(people),
        "active_person": active_person,
        "active_context_id": active_person.get("key") if active_person else "",
        "candidate_summaries": candidate_summaries,
        "people": people,
        "strict_mode": bool(active_person),
        "rule": (
            "Usa active_person como unico hilo conductor autorizado. "
            "No mezcles terceros ni candidatos secundarios salvo que el doctor pida comparar o cambiar de persona. "
            "Si necesitas otro hilo, llama de nuevo person_context con el nombre o telefono exacto."
        ),
    }
    append_memory(
        "person_context_supervision",
        {"query": query, "count": len(people), "people": [item.get("display_name") for item in people]},
    )
    return payload


def person_context_is_doctor(record):
    if not record:
        return False
    if str(record.get("key") or "").strip() == "person:dr-yehoshua":
        return True
    title = person_context_title(record).strip().lower()
    return any(hint in title for hint in DOCTOR_CONTEXT_NAME_HINTS)


def person_context_pending_briefs(record, limit=4):
    if not record:
        return []
    pending = []
    seen = set()
    blocks = sorted(
        record.get("context_blocks") or [],
        key=lambda item: item.get("updated_at") or item.get("created_at") or "",
        reverse=True,
    )
    for block in blocks:
        status = str(block.get("status") or "").strip().lower()
        if status in {"completed", "transcribed"}:
            continue
        text = block.get("next_step_hint") or block.get("objective") or block.get("call_context") or ""
        clean = brief(re.sub(r"\s+", " ", str(text).strip()), 220)
        if clean and clean not in seen:
            pending.append(clean)
            seen.add(clean)
        if len(pending) >= limit:
            return pending
    scheduled = sorted(
        record.get("scheduled_actions") or [],
        key=lambda item: item.get("due_at") or "",
        reverse=True,
    )
    for item in scheduled:
        status = str(item.get("status") or "").strip().lower()
        if status in {"done", "completed", "cancelled", "canceled"}:
            continue
        clean = brief(f"{item.get('action') or ''} {item.get('due_at') or ''}".strip(), 220)
        if clean and clean not in seen:
            pending.append(clean)
            seen.add(clean)
        if len(pending) >= limit:
            return pending
    for note in record.get("notes") or []:
        clean = brief(re.sub(r"\s+", " ", str(note).strip()), 220)
        if clean and clean not in seen:
            pending.append(clean)
            seen.add(clean)
        if len(pending) >= min(limit, 2):
            break
    return pending[:limit]


def markdown_title_from_text(text, fallback="Knowledge"):
    for line in str(text or "").splitlines():
        clean = line.strip()
        if clean.startswith("# "):
            return clean[2:].strip()
    return fallback


def markdown_section_summary(text, heading="## Sintesis", limit=360):
    lines = str(text or "").splitlines()
    capture = False
    collected = []
    for line in lines:
        clean = line.strip()
        if clean.lower() == heading.lower():
            capture = True
            continue
        if capture and clean.startswith("## "):
            break
        if capture and clean:
            collected.append(clean)
    if not collected:
        for line in lines:
            clean = line.strip()
            if clean and not clean.startswith("#") and not clean.startswith("- "):
                collected.append(clean)
            if len(" ".join(collected)) >= limit:
                break
    return brief(" ".join(collected), limit)


def person_context_search_terms(record):
    terms = []
    title = person_context_title(record)
    if title:
        terms.append(title)
        parts = [part for part in normalize_security_text(title).split() if len(part) >= 4]
        terms.extend(parts[:3])
    for company in record.get("companies") or []:
        if company:
            terms.append(company)
    for phone in record.get("phones") or []:
        clean = normalize_phone_number(phone)
        if clean:
            terms.append(clean)
            terms.append(clean[-8:])
    return [term for term in compact_unique(terms, limit=10) if str(term).strip()]


def person_context_knowledge_briefs(record, limit=4):
    if not record:
        return []
    terms = person_context_search_terms(record)
    if not terms:
        return []
    roots = [MEMORY_KNOWLEDGE, RUNTIME_KNOWLEDGE]
    scored = []
    seen_paths = set()
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.md"):
            if str(path) in seen_paths:
                continue
            seen_paths.add(str(path))
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            haystack = f"{path.name}\n{text}".lower()
            score = 0
            for term in terms:
                clean = str(term or "").strip().lower()
                if clean and clean in haystack:
                    score += 3 if " " in clean or clean.startswith("+") else 1
            if score <= 0:
                continue
            scored.append(
                {
                    "score": score,
                    "title": markdown_title_from_text(text, fallback=path.stem.replace("-", " ").title()),
                    "summary": markdown_section_summary(text),
                    "path": str(path),
                }
            )
    scored.sort(key=lambda item: (item["score"], item["path"]), reverse=True)
    output = []
    for item in scored:
        if item["summary"]:
            output.append({key: item[key] for key in ["title", "summary", "path"]})
        if len(output) >= limit:
            break
    return output


def format_knowledge_briefs_for_prompt(briefs, limit=900):
    if not briefs:
        return "Sin knowledge cards especificas encontradas para este contacto."
    text = "; ".join(f"{item.get('title')}: {item.get('summary')}" for item in briefs)
    return brief(text, limit)


def twilio_inbound_caller_profile(caller="", called=""):
    normalized_caller = normalize_phone_number(caller)
    record = person_context_record_for_phone(normalized_caller)
    if not record and normalized_caller:
        record = person_context_record_for_phone(normalized_caller, rebuild=True)
    display_name = person_context_title(record) if record else (normalized_caller or "Llamante")
    companies = ", ".join(compact_unique(record.get("companies", []), limit=3)) if record else ""
    relationship = ", ".join(compact_unique(record.get("contact_types", []), limit=3)) if record else ""
    pending_briefs = person_context_pending_briefs(record, limit=3)
    knowledge_briefs = person_context_knowledge_briefs(record, limit=4)
    return {
        "caller": normalized_caller,
        "called": normalize_phone_number(called),
        "key": record.get("key", "") if record else "",
        "display_name": display_name,
        "known_contact": bool(record),
        "is_doctor": person_context_is_doctor(record),
        "company_summary": companies,
        "relationship_summary": relationship,
        "pending_briefs": pending_briefs,
        "pending_summary": "; ".join(pending_briefs),
        "knowledge_briefs": knowledge_briefs,
        "knowledge_summary": format_knowledge_briefs_for_prompt(knowledge_briefs),
        "service_summary": INBOUND_CALL_SERVICE_SUMMARY,
        "sales_positioning": AI_PEOPLE_SALES_POSITIONING,
        "sales_playbook": AI_PEOPLE_SALES_PLAYBOOK,
        "sales_discovery_flow": AI_PEOPLE_DISCOVERY_FLOW,
        "commercial_guardrails": AI_PEOPLE_COMMERCIAL_GUARDRAILS,
        "remote_secretary_bridge_policy": REMOTE_SECRETARY_BRIDGE_POLICY,
        "inbound_relationship_goodwill_policy": INBOUND_RELATIONSHIP_GOODWILL_POLICY,
        "whatsapp_sales_pr_meeting_playbook": WHATSAPP_SALES_PR_MEETING_PLAYBOOK,
        "privacy_summary": (
            "No compartir tareas de terceros ni pendientes generales del doctor sin identidad clara; "
            "solo dar contexto del propio llamante."
        ),
    }


def twilio_inbound_caller_label(profile=None):
    profile = profile or {}
    if profile.get("is_doctor"):
        return "Dr. Yehoshua"
    return profile.get("display_name") or "Llamante"


def twilio_label_looks_like_phone(label):
    raw = str(label or "").strip()
    normalized = normalize_phone_number(raw)
    return bool(normalized and normalized == raw)


def twilio_inbound_call_context(caller="", called="", call_sid="", profile=None):
    profile = profile or twilio_inbound_caller_profile(caller, called)
    caller_number = profile.get("caller") or normalize_phone_number(caller)
    called_number = profile.get("called") or normalize_phone_number(called)
    is_doctor = bool(profile.get("is_doctor"))
    label = twilio_inbound_caller_label(profile)
    known = bool(profile.get("known_contact")) and not twilio_label_looks_like_phone(label)
    pending = profile.get("pending_summary") or "Sin pendientes sintetizados todavia."
    knowledge_summary = profile.get("knowledge_summary") or "Sin knowledge cards especificas encontradas para este contacto."
    if is_doctor:
        objective = "Atender al Dr. Yehoshua como linea directa de Kim Live y puente remoto de instrucciones operativas."
        instructions = (
            "Saluda como Kim de forma natural. Puedes asumir que el interlocutor es el doctor si el numero coincide. "
            "Este canal debe funcionar aunque el doctor no este frente a la computadora: recibe instrucciones, tareas, "
            "contexto, recados y solicitudes de seguimiento; registralas en memoria local, notifica Kim Live y prepara "
            "acciones cuando corresponda. Si algo requiere ejecucion fuera de la llamada, confirma que quedara registrado "
            "o preparado, pero no afirmes que ya se ejecuto si no existe resultado confirmado por API o scheduler."
        )
        questions = "Pregunta que necesita ejecutar o revisar ahora."
    elif known:
        objective = (
            f"Atender llamada entrante de {label}; actuar como secretaria del Dr. Yehoshua, confirmar identidad, "
            "responder sobre pendientes propios y orientar sobre Tesca Elements, Ignis, Ai People u otros frentes cuando sea informacion general."
        )
        instructions = (
            f"Si el numero ya esta vinculado a {label}, saluda por su nombre y continua el hilo de la conversacion anterior. "
            f"Usa su hilo propio de BIFROST antes de contestar: {knowledge_summary}. "
            f"Primera frase recomendada: 'Hola, {label}, habla Kim, asistente del Dr. Yehoshua. Me da gusto saludarte de nuevo. "
            "¿Continuamos con lo que teniamos pendiente o en que puedo ayudarte hoy?'. "
            f"Confirma con suavidad que hablas con {label} si el contexto lo requiere. No reveles datos sensibles hasta que la persona "
            "se identifique razonablemente. Puedes mencionar pendientes propios ya vinculados a ese numero, pero no "
            "compartas tareas de terceros ni pendientes generales del doctor. Si pregunta por otra persona, indica "
            "que por confidencialidad solo puedes revisar asuntos propios o registrar la solicitud para el doctor. "
            "Si llama como cliente, proveedor, inversionista o interesado en Tesca Elements, Ignis, Ai People u otro proyecto, atiende "
            "como recepcion ejecutiva: toma datos, detecta necesidad, explica lo general sin inventar y propone siguiente paso. "
            "Los temas comerciales permitidos incluyen automatizacion con IA, consultoria tecnologica y empresarial, branding, "
            "procesos, desarrollo humano, analisis financiero, operacion de portafolios, hedge fund y venture capital. "
            f"Si hay interes en Ai People, usa este posicionamiento: {AI_PEOPLE_SALES_POSITIONING} "
            f"Usa este playbook comercial: {AI_PEOPLE_SALES_PLAYBOOK} "
            f"Flujo de discovery: {AI_PEOPLE_DISCOVERY_FLOW} "
            f"Guardrails comerciales: {AI_PEOPLE_COMMERCIAL_GUARDRAILS}"
        )
        questions = (
            "Confirma nombre completo, empresa, rol, motivo de llamada y proyecto de interes. Si hay interes comercial, "
            "pregunta por dolor, costo de seguir igual, soluciones ya probadas, resultado ideal y dos horarios para hablar con el doctor."
        )
    else:
        objective = (
            "Atender llamada entrante de numero no identificado como secretaria del Dr. Yehoshua; identificar si es cliente, "
            "proveedor, inversionista o interesado en Tesca Elements, Ignis o Ai People, y registrar la solicitud."
        )
        instructions = (
            "Presentate como Kim, asistente del Dr. Yehoshua. Si el numero no esta identificado, inicia con un saludo breve: "
            "'Hola, habla Kim, asistente del Dr. Yehoshua. En Ai People ayudamos a empresas con automatizacion con IA, "
            "consultoria tecnologica, procesos, branding y analisis financiero. ¿Te puedo preguntar tu nombre?'. "
            "Cuando la persona diga su nombre, respondelo con naturalidad y profesionalismo, por ejemplo: "
            "'Mucho gusto, Jorge; es un placer atenderte. Para ubicarte bien, ¿que problema operativo o comercial te gustaria resolver con IA?'. "
            "No compartas contexto privado. Pide empresa o relacion con el doctor y motivo de llamada solo despues de tener el nombre. "
            "Puedes dar informacion general de servicios. Si pregunta por Tesca Elements, Ignis, Ai People u otros proyectos, contesta de forma general y profesional, sin inventar detalles "
            "ni prometer acciones no autorizadas. Puedes describir a grandes rasgos automatizacion con IA, consultoria tecnologica "
            "y empresarial, branding, procesos, desarrollo humano, analisis financiero, operacion de portafolios, hedge fund y venture capital. "
            f"Si hay interes en Ai People, usa este posicionamiento: {AI_PEOPLE_SALES_POSITIONING} "
            f"Usa este playbook comercial: {AI_PEOPLE_SALES_PLAYBOOK} "
            f"Flujo de discovery: {AI_PEOPLE_DISCOVERY_FLOW} "
            f"Guardrails comerciales: {AI_PEOPLE_COMMERCIAL_GUARDRAILS} "
            "Si solicita datos sensibles, ofrece registrar la solicitud para revision del doctor."
        )
        questions = (
            "Primero pregunta el nombre. Despues pregunta empresa, rol, proyecto de interes y motivo de llamada. "
            "Si es prospecto de Ai People, pregunta cual es su dolor mas importante, que pasa si siguen igual seis meses, "
            "que soluciones han probado, como se veria el resultado ideal, y dos horarios para una cita con el Dr. Yehoshua."
        )
    context_id = twilio_context_block_id({"context_id": f"INBOUND-{call_sid}" if call_sid else ""})
    return {
        "id": context_id,
        "context_block_id": context_id,
        "status": "prepared",
        "created_at": now_iso(),
        "source": "kim_live_twilio_inbound",
        "direction": "inbound",
        "context_scope": "single_contact",
        "workflow_target": "crm_then_memory",
        "call_sid": call_sid or "",
        "from": caller_number,
        "to": called_number,
        "contact_name": label if known or is_doctor else "",
        "relationship": profile.get("relationship_summary") or ("doctor" if is_doctor else ""),
        "company": profile.get("company_summary") or "",
        "call_context": (
            f"Llamada entrante desde {caller_number or caller}. "
            f"Perfil reconocido: {label if known or is_doctor else 'no identificado'}. "
            f"Pendientes propios disponibles: {pending}. "
            f"Hilo BIFROST propio del llamante: {knowledge_summary}. "
            f"Servicios generales permitidos: {profile.get('service_summary') or INBOUND_CALL_SERVICE_SUMMARY}. "
            f"Posicionamiento Ai People: {profile.get('sales_positioning') or AI_PEOPLE_SALES_POSITIONING}. "
            f"Playbook comercial: {profile.get('sales_playbook') or AI_PEOPLE_SALES_PLAYBOOK}. "
            f"Discovery comercial: {profile.get('sales_discovery_flow') or AI_PEOPLE_DISCOVERY_FLOW}. "
            f"Guardrails comerciales: {profile.get('commercial_guardrails') or AI_PEOPLE_COMMERCIAL_GUARDRAILS}."
            f" Politica secretaria/puente: {profile.get('remote_secretary_bridge_policy') or REMOTE_SECRETARY_BRIDGE_POLICY}."
            f" Politica relacion/buen nombre: {profile.get('inbound_relationship_goodwill_policy') or INBOUND_RELATIONSHIP_GOODWILL_POLICY}."
        ),
        "objective": objective,
        "instructions": instructions,
        "questions": questions,
        "message_to_deliver": "",
        "report_to_doctor": (
            "Guardar transcript, numero entrante, identidad declarada, empresa, rol, dolor, urgencia, soluciones previas, "
            "resultado deseado, presupuesto/rango si surgio, objeciones, horarios propuestos y siguiente paso recomendado."
        ),
        "success_criteria": (
            "La persona fue atendida sin revelar informacion de terceros; quedo memoria de la llamada y del seguimiento."
        ),
        "tone": "amable, natural, profesional y cuidadoso con privacidad",
        "next_step_hint": "Registrar seguimiento en CRM/memoria; escalar al doctor si hay solicitud sensible.",
        "inbound_caller_profile": profile,
    }


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


def twilio_recent_transcript_window(transcript, max_lines=18, max_chars=2400):
    lines = [str(line or "").rstrip() for line in str(transcript or "").splitlines() if str(line or "").strip()]
    if not lines:
        return ""
    window = "\n".join(lines[-max_lines:]).strip()
    if len(window) <= max_chars:
        return window
    return window[-max_chars:].lstrip()


def twilio_names_compatible(expected, actual):
    left = normalize_security_text(expected)
    right = normalize_security_text(actual)
    if not left or not right:
        return False
    if left == right or left in right or right in left:
        return True
    compact_left = re.sub(r"[^a-z0-9]+", "", left)
    compact_right = re.sub(r"[^a-z0-9]+", "", right)
    if compact_left and compact_right and (compact_left in compact_right or compact_right in compact_left):
        return True
    return bool(set(person_context_match_terms(left)) & set(person_context_match_terms(right)))


def twilio_report_request_looks_like_outcome(text):
    normalized = normalize_security_text(text)
    if not normalized:
        return False
    request_markers = ["reportar", "informar", "decir", "compartir", "registrar", "guardar", "anotar"]
    outcome_markers = ["confirmo que", "respondio que", "dijo que", "sugirio que", "confirmaron que", "respondieron que"]
    return any(marker in normalized for marker in outcome_markers) and not any(marker in normalized for marker in request_markers)


def twilio_report_request_fallback(contact_name="", questions="", objective=""):
    label = contact_name or "la persona"
    question_text = normalize_call_context_value(questions)
    objective_text = normalize_call_context_value(objective)
    if question_text:
        return f"Reportar al doctor exactamente que se dijo y que respondio {label} a: {question_text}"
    if objective_text:
        return f"Reportar al doctor exactamente que se dijo y que respondio {label} respecto a: {brief(objective_text, 220)}"
    return f"Reportar al doctor exactamente que se dijo y que respondio {label}."


def synthesize_twilio_context_from_transcript(explicit, transcript, expected_contact_name="", expected_phone=""):
    transcript = twilio_recent_transcript_window(transcript)
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
        "que se dijo y que respondio la persona.\n"
        "Usa SOLO el tramo mas reciente y pertinente. Ignora hilos anteriores de otras personas.\n"
        f"Destinatario esperado segun CRM/telefono: {expected_contact_name or '(sin resolver)'}\n"
        f"Telefono objetivo: {expected_phone or '(sin telefono)'}\n\n"
        f"Conversacion reciente:\n{brief(transcript, 3200)}"
    )
    try:
        response, model = openai_response_with_fallback(PHONE_REPLY_MODEL_CANDIDATES, {"input": prompt, "max_output_tokens": 700})
        parsed = parse_json_object_from_text(output_text_from_response(response))
        parsed_name = normalize_call_context_value(parsed.get("contact_name"))
        if expected_contact_name and parsed_name and not twilio_names_compatible(expected_contact_name, parsed_name):
            append_memory(
                "twilio_call_context_name_guard",
                {
                    "expected_contact_name": expected_contact_name,
                    "parsed_contact_name": parsed_name,
                },
            )
            parsed["contact_name"] = expected_contact_name
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
    recipient_contact = preview.get("recipient_contact") if isinstance(preview.get("recipient_contact"), dict) else {}
    expected_contact_name = normalize_call_context_value(
        recipient_contact.get("display_name") or preview.get("recipient_label") or preview.get("crm_lookup_phone") or preview.get("to")
    )
    expected_phone = preview.get("crm_lookup_phone") or preview.get("to") or ""
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
        "parent_context_id": first_value(parameters, "parent_context_id", "parent_block_id", "context_parent_id", default=""),
        "campaign_label": first_value(parameters, "campaign_label", "context_group", "group_name", "campaign", default=""),
        "context_scope": first_value(parameters, "context_scope", "scope", default=""),
        "next_step_hint": first_value(parameters, "next_step_hint", "post_response_action", "followup_hint", default=""),
        "workflow_target": first_value(parameters, "workflow_target", "post_call_workflow", default=""),
        "source_session_id": first_value(parameters, "source_session_id", "session_id", default=""),
    }
    explicit = {key: normalize_call_context_value(value) for key, value in explicit.items()}
    transcript_excerpt = brief(sanitize_text_for_log(transcript), 3200) if transcript else ""
    has_context_signal = any(
        value
        for key, value in explicit.items()
        if key not in {"tone", "contact_name", "relationship", "company"}
    ) or bool(transcript_excerpt)
    if not has_context_signal:
        return {}
    if expected_contact_name and not explicit.get("contact_name"):
        explicit["contact_name"] = expected_contact_name
    if recipient_contact.get("contact_type") and not explicit.get("relationship"):
        explicit["relationship"] = normalize_call_context_value(recipient_contact.get("contact_type"))
    company_name = recipient_contact.get("company") or recipient_contact.get("company_name") or ""
    if company_name and not explicit.get("company"):
        explicit["company"] = normalize_call_context_value(company_name)
    if transcript_excerpt:
        explicit = synthesize_twilio_context_from_transcript(
            explicit,
            transcript,
            expected_contact_name=expected_contact_name,
            expected_phone=expected_phone,
        )
    if expected_contact_name and explicit.get("contact_name") and not twilio_names_compatible(expected_contact_name, explicit.get("contact_name")):
        append_memory(
            "twilio_call_context_contact_guard",
            {
                "expected_contact_name": expected_contact_name,
                "actual_contact_name": explicit.get("contact_name"),
                "phone": expected_phone,
            },
        )
        explicit["contact_name"] = expected_contact_name
    if (not explicit.get("report_to_doctor")) or twilio_report_request_looks_like_outcome(explicit.get("report_to_doctor")):
        explicit["report_to_doctor"] = twilio_report_request_fallback(
            contact_name=explicit.get("contact_name") or expected_contact_name,
            questions=explicit.get("questions"),
            objective=explicit.get("objective"),
        )
    if not explicit.get("tone"):
        explicit["tone"] = "amable, natural y profesional"
    if not explicit.get("workflow_target"):
        explicit["workflow_target"] = "pipedrive_then_clickup"
    context_id = twilio_context_block_id(parameters)
    context = {
        "id": context_id,
        "context_block_id": context_id,
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
    sync_external_call_context_block(context)
    queue_twilio_realtime_sync(context, trigger="context_prepared", changed_fields=sorted(context.keys()))
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
    before = dict(context)
    changed_fields = []
    for key, value in updates.items():
        if value is None:
            continue
        if before.get(key) != value:
            changed_fields.append(key)
        context[key] = value
    if call_sid:
        if before.get("call_sid") != call_sid:
            changed_fields.append("call_sid")
        context["call_sid"] = call_sid
    context["updated_at"] = now_iso()
    state["contexts"][context_id] = context
    save_twilio_call_context_state(state)
    sync_external_call_context_block(context)
    if changed_fields:
        queue_twilio_realtime_sync(context, trigger="context_updated", changed_fields=changed_fields)
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


TWILIO_TERMINAL_CALL_STATUSES = {"completed", "no-answer", "busy", "failed", "canceled", "cancelled"}
TWILIO_CALL_STATUS_ORDER = {
    "queued": 10,
    "initiated": 20,
    "ringing": 30,
    "answered": 40,
    "in-progress": 50,
    "completed": 90,
    "no-answer": 90,
    "busy": 90,
    "failed": 90,
    "canceled": 90,
    "cancelled": 90,
}


def twilio_call_attempt_session_id(call_sid):
    return re.sub(r"[^A-Za-z0-9_-]+", "-", f"PHONE-{call_sid or 'unknown'}")


def twilio_event_time_value(event):
    return str(event.get("at") or event.get("started_at") or event.get("sent_at") or event.get("created_at") or "")


def twilio_parse_event_time(value):
    raw = str(value or "").replace("Z", "+00:00")
    if not raw:
        return dt.datetime.min
    try:
        parsed = dt.datetime.fromisoformat(raw)
    except ValueError:
        return dt.datetime.min
    if parsed.tzinfo:
        parsed = parsed.astimezone().replace(tzinfo=None)
    return parsed


def twilio_event_status(event):
    return str(event.get("call_status") or event.get("status") or event.get("message_status") or "").strip().lower()


def twilio_call_status_is_terminal(status):
    return str(status or "").strip().lower() in TWILIO_TERMINAL_CALL_STATUSES


def twilio_event_sort_key(event):
    status = twilio_event_status(event)
    return (
        twilio_parse_event_time(twilio_event_time_value(event)),
        TWILIO_CALL_STATUS_ORDER.get(status, 0),
    )


def twilio_read_call_events(call_sid):
    call_sid = str(call_sid or "").strip()
    if not call_sid:
        return []
    events = []
    for path in [TWILIO_CALL_LOG, RUNTIME_TWILIO_CALL_LOG]:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (FileNotFoundError, PermissionError, OSError):
            continue
        for line in lines:
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            sid = event.get("call_sid") or event.get("sid")
            if sid != call_sid:
                continue
            normalized = dict(event)
            normalized["call_sid"] = call_sid
            if not normalized.get("at") and normalized.get("started_at"):
                normalized["at"] = normalized.get("started_at")
            normalized["_source_path"] = str(path)
            events.append(normalized)
    deduped = {}
    for event in events:
        key = (
            twilio_event_time_value(event),
            event.get("kind") or event.get("action"),
            twilio_event_status(event),
            event.get("to") or "",
            event.get("from") or "",
        )
        deduped[key] = event
    return sorted(deduped.values(), key=twilio_event_sort_key)


def twilio_latest_call_event(call_sid, fallback_event=None):
    events = twilio_read_call_events(call_sid)
    if fallback_event:
        fallback = dict(fallback_event)
        fallback["call_sid"] = fallback.get("call_sid") or fallback.get("sid") or call_sid
        events.append(fallback)
    if not events:
        return {}
    return sorted(events, key=twilio_event_sort_key)[-1]


def twilio_existing_call_entry(call_sid):
    session_id = twilio_call_attempt_session_id(call_sid)
    for entry in reversed(load_call_entries(limit=5000)):
        if entry.get("session_id") == session_id:
            return entry
    return {}


def twilio_existing_call_text(call_sid):
    entry = twilio_existing_call_entry(call_sid)
    path = pathlib.Path(entry.get("path") or "")
    return read_text_tail(path, limit=90000) if str(path) else ""


def twilio_call_record_has_realtime_transcript(call_sid):
    text = twilio_existing_call_text(call_sid)
    return "Twilio Media Streams + OpenAI Realtime" in text and "Sin audio de Media Stream registrado" not in text


def twilio_status_history(call_sid):
    history = []
    for event in twilio_read_call_events(call_sid):
        status = twilio_event_status(event)
        if not status:
            continue
        history.append(
            {
                "at": twilio_event_time_value(event),
                "status": status,
                "kind": event.get("kind") or event.get("action") or "",
                "from": event.get("from", ""),
                "to": event.get("to", ""),
                "duration": event.get("duration", ""),
                "error_code": event.get("error_code", ""),
                "error_message": event.get("error_message", ""),
            }
        )
    return history


def twilio_call_attempt_context_from_event(event, call_context=None):
    event = event or {}
    call_sid = event.get("call_sid") or event.get("sid") or ""
    context_id = event.get("context_id") or event.get("kim_context_id") or ""
    context = dict(call_context or load_twilio_call_context(call_sid=call_sid, context_id=context_id) or {})
    to_number = normalize_phone_number(event.get("to") or context.get("to") or "")
    from_number = normalize_phone_number(event.get("from") or context.get("from") or "")
    if not context:
        contact = crm_find_contact_by_phone(to_number) or crm_find_contact_by_phone(from_number) or {}
        context = {
            "id": context_id,
            "call_sid": call_sid,
            "to": to_number,
            "from": from_number,
            "contact_name": contact.get("display_name") or "",
            "company": contact.get("company") or "",
            "relationship": contact.get("contact_type") or "",
            "source": "twilio_status_callback",
        }
    if to_number and not context.get("to"):
        context["to"] = to_number
    if from_number and not context.get("from"):
        context["from"] = from_number
    if call_sid:
        context["call_sid"] = call_sid
    return context


def twilio_history_markdown(history):
    if not history:
        return "- Sin callbacks Twilio registrados."
    lines = []
    for item in history:
        status = item.get("status") or "unknown"
        detail = []
        if item.get("duration"):
            detail.append(f"duration={item.get('duration')}s")
        if item.get("error_code"):
            detail.append(f"error={item.get('error_code')}")
        suffix = f" ({', '.join(detail)})" if detail else ""
        lines.append(f"- {item.get('at') or 'sin-fecha'}: {status} via {item.get('kind') or 'twilio'}{suffix}")
    return "\n".join(lines)


def twilio_context_markdown(context):
    rows = [
        ("Context ID", context.get("id", "")),
        ("Context block", context.get("context_block_id", "")),
        ("Parent block", context.get("parent_context_id", "")),
        ("Campaign", context.get("campaign_label", "")),
        ("Scope", context.get("context_scope", "") or twilio_context_scope(context)),
        ("Workflow target", context.get("workflow_target", "") or "pipedrive_then_clickup"),
        ("Contact", context.get("contact_name", "")),
        ("Company", context.get("company", "")),
        ("Relationship", context.get("relationship", "")),
        ("Objective", context.get("objective", "")),
        ("Instructions", context.get("instructions", "")),
        ("Questions", context.get("questions", "")),
        ("Message to deliver", context.get("message_to_deliver", "")),
        ("Report to doctor", context.get("report_to_doctor", "")),
        ("Success criteria", context.get("success_criteria", "")),
        ("Next step hint", context.get("next_step_hint", "")),
    ]
    lines = [f"- {label}: {brief(str(value), 1200)}" for label, value in rows if value]
    return "\n".join(lines) if lines else "- Sin contexto explicito capturado."


def twilio_call_attempt_markdown(event, context, history):
    call_sid = event.get("call_sid") or event.get("sid") or context.get("call_sid") or ""
    status = twilio_event_status(event) or context.get("status") or "unknown"
    from_number = normalize_phone_number(event.get("from") or context.get("from") or "")
    to_number = normalize_phone_number(event.get("to") or context.get("to") or "")
    duration = event.get("duration") or context.get("duration") or ""
    error_code = event.get("error_code") or context.get("error_code") or ""
    error_message = event.get("error_message") or context.get("error_message") or ""
    terminal_note = (
        "Este intento llego a un estado terminal sin audio util de Media Stream."
        if twilio_call_status_is_terminal(status) and status != "completed"
        else "Este registro se crea desde el inicio para que Kim recuerde el intento aunque todavia no haya transcripcion."
    )
    lines = [
        "Canal: Twilio call attempt/status ledger",
        f"CallSid: {call_sid}",
        f"From: {from_number}",
        f"To: {to_number}",
        f"Status actual: {status}",
    ]
    if duration:
        lines.append(f"Duration seconds: {duration}")
    if error_code or error_message:
        lines.append(f"Twilio error: {error_code} {error_message}".strip())
    lines.extend(
        [
            "",
            "## Call Context",
            "",
            twilio_context_markdown(context),
            "",
            "## Status History",
            "",
            twilio_history_markdown(history),
            "",
            "## Transcript",
            "",
            f"Sin audio de Media Stream registrado. Estado Twilio: {status}. {terminal_note}",
            "",
        ]
    )
    return "\n".join(lines)


def load_twilio_pipedrive_sync_state():
    state = {"calls": {}}
    for path in [TWILIO_PIPEDRIVE_CALL_SYNC, RUNTIME_TWILIO_PIPEDRIVE_CALL_SYNC]:
        payload = read_json_file(path, {})
        if not isinstance(payload, dict):
            continue
        calls = payload.get("calls", {})
        if isinstance(calls, dict):
            state["calls"].update(calls)
        if payload.get("updated_at"):
            state["updated_at"] = payload.get("updated_at")
    state.setdefault("calls", {})
    return state


def save_twilio_pipedrive_sync_state(state):
    state["updated_at"] = now_iso()
    last_error = None
    wrote = False
    for path in [TWILIO_PIPEDRIVE_CALL_SYNC, RUNTIME_TWILIO_PIPEDRIVE_CALL_SYNC]:
        try:
            write_json_file(path, state)
            wrote = True
        except (PermissionError, OSError) as exc:
            last_error = exc
    if not wrote and last_error:
        raise last_error


def twilio_seconds_to_pipedrive_duration(value):
    try:
        seconds = max(0, int(float(value or 0)))
    except (TypeError, ValueError):
        return ""
    hours = seconds // 3600
    minutes = max(1 if seconds else 0, (seconds % 3600 + 59) // 60)
    return f"{hours:02d}:{minutes:02d}" if seconds else ""


def twilio_pipedrive_note(event, context, attempt_path, history):
    status = twilio_event_status(event) or context.get("status") or ""
    parts = [
        f"Kim Live Twilio call attempt",
        f"CallSid: {event.get('call_sid') or event.get('sid') or context.get('call_sid') or ''}",
        f"Status: {status}",
        f"From: {event.get('from') or context.get('from') or ''}",
        f"To: {event.get('to') or context.get('to') or ''}",
    ]
    if context.get("contact_name"):
        parts.append(f"Contact: {context.get('contact_name')}")
    if context.get("context_block_id") or context.get("id"):
        parts.append(f"Context block: {context.get('context_block_id') or context.get('id')}")
    if context.get("objective"):
        parts.append(f"Objective: {context.get('objective')}")
    if context.get("report_to_doctor"):
        parts.append(f"Report requested: {context.get('report_to_doctor')}")
    if attempt_path:
        parts.append(f"BIFROST call memory: {attempt_path}")
    parts.append("Status history:")
    for item in history[-10:]:
        parts.append(f"- {item.get('at')}: {item.get('status')}")
    return "\n".join(parts)


def sync_twilio_call_attempt_to_pipedrive(event, context, attempt_path="", history=None):
    call_sid = event.get("call_sid") or event.get("sid") or context.get("call_sid") or ""
    if not call_sid:
        return {"ok": False, "skipped": "missing_call_sid"}
    if not pipedrive_status(live=False).get("configured"):
        return {"ok": False, "skipped": "pipedrive_not_configured"}
    history = history if history is not None else twilio_status_history(call_sid)
    status = twilio_event_status(event) or context.get("status") or "unknown"
    state = load_twilio_pipedrive_sync_state()
    current = state["calls"].get(call_sid, {})
    contact_name = context.get("contact_name") or context.get("to") or event.get("to") or call_sid
    subject = f"Kim call: {contact_name} - {status}"[:250]
    occurred = twilio_parse_event_time(twilio_event_time_value(event) or now_iso())
    note = twilio_pipedrive_note(event, context, attempt_path, history)
    payload = {
        "subject": subject,
        "type": "call",
        "done": 1 if twilio_call_status_is_terminal(status) else 0,
        "note": note,
    }
    if occurred != dt.datetime.min:
        payload["due_date"] = occurred.strftime("%Y-%m-%d")
        payload["due_time"] = occurred.strftime("%H:%M")
    duration = twilio_seconds_to_pipedrive_duration(event.get("duration") or context.get("duration"))
    if duration:
        payload["duration"] = duration
    person_params = {
        "phone": event.get("to") or context.get("to") or event.get("from") or context.get("from"),
        "contact_name": context.get("contact_name") or "",
        "name": context.get("contact_name") or "",
    }
    try:
        person_id, person_scope = pipedrive_find_person_id(person_params, required=False)
        if person_id:
            payload["person_id"] = person_id
    except Exception as exc:
        person_scope = {"source": "error", "error": brief(str(exc), 300)}
    try:
        if current.get("activity_id"):
            response = pipedrive_request(
                f"/activities/{urllib.parse.quote(str(current['activity_id']))}",
                method="PUT",
                payload=payload,
            )
            activity = pipedrive_payload_data(response) or {}
            activity_id = activity.get("id") or current.get("activity_id")
            action = "updated"
        else:
            response = pipedrive_request("/activities", method="POST", payload=payload)
            activity = pipedrive_payload_data(response) or {}
            activity_id = activity.get("id")
            action = "created"
        state["calls"][call_sid] = {
            **current,
            "activity_id": activity_id,
            "last_status": status,
            "last_attempt_path": attempt_path,
            "last_synced_at": now_iso(),
            "person_scope": person_scope,
        }
        save_twilio_pipedrive_sync_state(state)
        append_memory("twilio_pipedrive_call_sync", {"call_sid": call_sid, "status": status, "activity_id": activity_id, "action": action})
        return {"ok": True, "provider": "pipedrive", "action": action, "activity_id": activity_id, "status": status}
    except Exception as exc:
        state["calls"][call_sid] = {
            **current,
            "last_status": status,
            "last_attempt_path": attempt_path,
            "last_error": brief(str(exc), 800),
            "last_error_at": now_iso(),
        }
        try:
            save_twilio_pipedrive_sync_state(state)
        except Exception:
            pass
        append_memory("twilio_pipedrive_call_sync_error", {"call_sid": call_sid, "status": status, "error": brief(str(exc), 800)})
        return {"ok": False, "provider": "pipedrive", "error": brief(str(exc), 800), "status": status}


def record_twilio_call_attempt(event, call_context=None, force=False):
    event = dict(event or {})
    call_sid = event.get("call_sid") or event.get("sid") or ""
    if not call_sid:
        return {"ok": False, "skipped": "missing_call_sid"}
    latest = twilio_latest_call_event(call_sid, event) or event
    status = twilio_event_status(latest) or twilio_event_status(event) or "unknown"
    context = twilio_call_attempt_context_from_event(latest, call_context=call_context)
    history = twilio_status_history(call_sid)
    started_at = (history[0].get("at") if history else twilio_event_time_value(latest)) or now_iso()
    updates = {
        "status": "transcribed" if context.get("status") == "transcribed" else status,
        "twilio_status": status,
        "last_call_status": status,
        "duration": latest.get("duration") or context.get("duration", ""),
        "error_code": latest.get("error_code") or context.get("error_code", ""),
        "error_message": latest.get("error_message") or context.get("error_message", ""),
        "last_status_at": twilio_event_time_value(latest) or now_iso(),
    }
    if twilio_call_status_is_terminal(status):
        updates["context_consumed_at"] = updates["last_status_at"]
        updates["context_invalidated_at"] = updates["last_status_at"]
    if context.get("id"):
        updated = update_twilio_call_context(context_id=context.get("id"), call_sid=call_sid, updates=updates)
        if updated:
            context = updated
    existing = twilio_existing_call_entry(call_sid)
    has_realtime_transcript = twilio_call_record_has_realtime_transcript(call_sid)
    if has_realtime_transcript:
        attempt_path = existing.get("path", "")
    else:
        text = twilio_call_attempt_markdown(latest, context, history)
        title_contact = context.get("contact_name") or context.get("to") or latest.get("to") or call_sid
        call_path, entry = save_call_record(
            {
                "session_id": twilio_call_attempt_session_id(call_sid),
                "title": f"Twilio call attempt - {title_contact}",
                "started_at": started_at,
                "date": str(started_at)[:10],
                "text": text,
            }
        )
        attempt_path = str(call_path)
        if context.get("id"):
            updated = update_twilio_call_context(
                context_id=context.get("id"),
                call_sid=call_sid,
                updates={
                    "transcript_path": attempt_path,
                    "summary": brief(entry.get("summary", ""), 1200),
                    "status": status,
                    "twilio_status": status,
                },
            )
            if updated:
                context = updated
    should_record = force or twilio_call_status_is_terminal(status) or status in {"queued", "in-progress"}
    crm_interaction = {}
    if should_record:
        crm_interaction = crm_record_interaction(
            "call_attempt",
            "outbound",
            from_value=latest.get("from") or context.get("from", ""),
            to_value=latest.get("to") or context.get("to", ""),
            status=status,
            body=twilio_pipedrive_note(latest, context, attempt_path, history),
            external_sid=call_sid,
            transcript_path=attempt_path,
            metadata={**latest, "attempt_path": attempt_path, "status_history": history},
            contact_hint={
                "display_name": context.get("contact_name", ""),
                "company": context.get("company", ""),
                "notes": context.get("relationship", ""),
            },
        )
    pipedrive_sync = {}
    if should_record:
        pipedrive_sync = sync_twilio_call_attempt_to_pipedrive(latest, context, attempt_path=attempt_path, history=history)
    append_memory(
        "twilio_call_attempt_recorded",
        {
            "call_sid": call_sid,
            "status": status,
            "path": attempt_path,
            "has_realtime_transcript": has_realtime_transcript,
            "pipedrive_ok": pipedrive_sync.get("ok"),
        },
    )
    return {
        "ok": True,
        "call_sid": call_sid,
        "status": status,
        "path": attempt_path,
        "has_realtime_transcript": has_realtime_transcript,
        "crm_interaction": crm_interaction,
        "pipedrive_sync": pipedrive_sync,
    }


def twilio_reconcile_call_attempts(parameters=None):
    parameters = parameters or {}
    raw_limit = first_value(parameters, "limit", "count", default=25)
    try:
        limit = max(1, min(int(raw_limit or 25), 200))
    except (TypeError, ValueError):
        limit = 25
    since = str(first_value(parameters, "since", "from_date", "desde", default="") or "").strip()
    since_dt = twilio_parse_event_time(since) if since else dt.datetime.min
    grouped = {}
    for path in [TWILIO_CALL_LOG, RUNTIME_TWILIO_CALL_LOG]:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (FileNotFoundError, PermissionError, OSError):
            continue
        for line in lines:
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            call_sid = event.get("call_sid") or event.get("sid")
            if not call_sid:
                continue
            event_dt = twilio_parse_event_time(twilio_event_time_value(event))
            if event_dt < since_dt:
                continue
            grouped.setdefault(call_sid, []).append(event)
    ordered = sorted(
        grouped,
        key=lambda sid: twilio_event_sort_key(twilio_latest_call_event(sid, grouped[sid][-1] if grouped[sid] else {})),
        reverse=True,
    )
    results = []
    for call_sid in ordered[:limit]:
        latest = twilio_latest_call_event(call_sid, grouped[call_sid][-1] if grouped[call_sid] else {})
        try:
            results.append(record_twilio_call_attempt(latest, force=False))
        except Exception as exc:
            error = {"ok": False, "call_sid": call_sid, "error": brief(str(exc), 800)}
            append_memory("twilio_call_attempt_reconcile_error", error)
            results.append(error)
    return {
        "ok": True,
        "provider": "twilio",
        "action": "sync_call_attempts",
        "since": since,
        "count": len(results),
        "recorded": sum(1 for item in results if item.get("ok")),
        "pipedrive_synced": sum(1 for item in results if (item.get("pipedrive_sync") or {}).get("ok")),
        "results": results,
    }


def call_transcript_from_text(text):
    text = (text or "").strip()
    marker = "\n## Transcript\n"
    if marker in text:
        return text.split(marker, 1)[1].strip()
    return text


def twilio_detect_outbound_recipient_mismatch(transcript_lines, call_context=None):
    call_context = call_context or {}
    if not call_context or call_context.get("direction") == "inbound":
        return {}
    expected_contact_name = str(call_context.get("contact_name") or "").strip()
    if not expected_contact_name:
        return {}
    lines = [str(line or "").strip() for line in (transcript_lines or []) if str(line or "").strip()]
    if not lines:
        return {}
    transcript_text = "\n".join(lines)
    normalized = normalize_security_text(transcript_text)
    actual_contact_name = ""
    for line in lines:
        if not line.lower().startswith("dr. yehoshua:"):
            continue
        match = re.search(
            r"yo soy (?:la\s+señorita|la\s+senorita|la\s+señora|la\s+senora|el\s+señor|el\s+senor)?\s*([^.,;:!?]+)",
            line,
            flags=re.I,
        )
        if match:
            actual_contact_name = match.group(1).strip()
            break
    if actual_contact_name and twilio_names_compatible(expected_contact_name, actual_contact_name):
        return {}
    mismatch_markers = [
        "equivocada",
        "llamada de error",
        "no te puedo ayudar",
        "yo soy la senorita",
        "yo soy la senora",
        "yo soy el senor",
    ]
    if actual_contact_name:
        return {
            "expected_contact_name": expected_contact_name,
            "actual_contact_name": actual_contact_name,
            "reason": "caller_identifies_as_different_person",
        }
    if any(marker in normalized for marker in mismatch_markers):
        return {
            "expected_contact_name": expected_contact_name,
            "actual_contact_name": "",
            "reason": "conversation_indicates_wrong_recipient",
        }
    return {}


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
        entry_call_sid = context.get("call_sid") or call_sid
        if not entry_call_sid and str(entry.get("session_id") or "").startswith("PHONE-"):
            entry_call_sid = str(entry.get("session_id")).replace("PHONE-", "", 1)
        entry_status = context.get("twilio_status") or context.get("last_call_status") or context.get("status", "")
        attempt_without_media = (
            "Sin audio de Media Stream registrado" in text
            or "Sin audio de Media Stream registrado" in transcript
            or bool(entry_call_sid and twilio_call_status_is_terminal(entry_status) and not twilio_call_record_has_realtime_transcript(entry_call_sid))
        )
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
                "call_sid": entry_call_sid,
                "context_id": context.get("id") or context_id,
                "to": context.get("to", ""),
                "from": context.get("from", ""),
                "status": entry_status,
                "status_history": twilio_status_history(entry_call_sid) if entry_call_sid else [],
                "attempt_without_media_stream": attempt_without_media,
                "contact_name": context.get("contact_name", ""),
                "objective": context.get("objective", ""),
                "report_to_doctor": context.get("report_to_doctor", ""),
                "call_context": brief(context.get("call_context", ""), 1000),
                "delivery_outcome": context.get("delivery_outcome", ""),
                "delivery_note": context.get("delivery_note", ""),
                "context_block_id": context.get("context_block_id") or context.get("id", ""),
                "parent_context_id": context.get("parent_context_id", ""),
                "campaign_label": context.get("campaign_label", ""),
                "workflow_target": context.get("workflow_target", "") or "pipedrive_then_clickup",
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
            context_call_sid = context.get("call_sid", "")
            history = twilio_status_history(context_call_sid) if context_call_sid else []
            transcript_excerpt = brief(call_transcript_from_text(text), 9000)
            if not transcript_excerpt and context_call_sid:
                transcript_excerpt = brief(
                    f"Sin audio de Media Stream registrado. Estado Twilio: {context.get('twilio_status') or context.get('last_call_status') or context.get('status') or 'unknown'}.",
                    9000,
                )
            calls.append(
                {
                    "session_id": pathlib.Path(transcript_path).stem if transcript_path else "",
                    "path": transcript_path,
                    "summary": context.get("summary", ""),
                    "transcript_excerpt": transcript_excerpt,
                    "call_sid": context_call_sid,
                    "context_id": context.get("id", ""),
                    "to": context.get("to", ""),
                    "from": context.get("from", ""),
                    "status": context.get("twilio_status") or context.get("last_call_status") or context.get("status", ""),
                    "status_history": history,
                    "attempt_without_media_stream": bool(context_call_sid and not text),
                    "contact_name": context.get("contact_name", ""),
                    "objective": context.get("objective", ""),
                    "report_to_doctor": context.get("report_to_doctor", ""),
                    "call_context": brief(context.get("call_context", ""), 1000),
                    "context_block_id": context.get("context_block_id") or context.get("id", ""),
                    "parent_context_id": context.get("parent_context_id", ""),
                    "campaign_label": context.get("campaign_label", ""),
                    "workflow_target": context.get("workflow_target", "") or "pipedrive_then_clickup",
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
    allow_unknown_contact = boolish(
        first_value(
            parameters or {},
            "allow_unknown_contact",
            "allow_unregistered_recipient",
            "allow_ad_hoc_recipient",
            default=False,
        )
    )
    crm_lookup_phone = twilio_lookup_phone_number(to)
    recipient_contact = crm_find_contact_by_phone(crm_lookup_phone) if crm_lookup_phone else {}
    if crm_lookup_phone and not allow_unknown_contact and not recipient_contact:
        raise ValueError(
            f"El destinatario {crm_lookup_phone} no esta registrado en CRM local. "
            "Guardalo o sincronizalo primero antes de llamar."
        )
    recipient_label = recipient_contact.get("display_name") or crm_lookup_phone or to
    return {
        "to": to,
        "from": from_number,
        "url": url,
        "status_callback": status_callback,
        "timeout": int(first_value(parameters, "timeout", default=35) or 35),
        "crm_lookup_phone": crm_lookup_phone,
        "recipient_label": recipient_label,
        "recipient_contact": {
            "id": recipient_contact.get("id"),
            "display_name": recipient_contact.get("display_name"),
            "phone_e164": recipient_contact.get("phone_e164"),
            "contact_type": recipient_contact.get("contact_type"),
            "company": recipient_contact.get("company") or recipient_contact.get("company_name"),
            "notes": recipient_contact.get("notes"),
        } if recipient_contact else {},
        "allow_unknown_contact": allow_unknown_contact,
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
                "context_block_id": call_context.get("context_block_id") or call_context.get("id"),
                "contact_name": call_context.get("contact_name"),
                "objective": brief(call_context.get("objective") or call_context.get("instructions") or call_context.get("call_context"), 500),
                "report_to_doctor": brief(call_context.get("report_to_doctor"), 300),
            }
            for key in [
                "context_block_id",
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
                "parent_context_id",
                "campaign_label",
                "context_scope",
                "next_step_hint",
                "workflow_target",
                "source_session_id",
            ]:
                if call_context.get(key):
                    execution_parameters[key] = call_context[key]
        return confirmation_preview(
            "twilio",
            "call_phone",
            f"Llamar por Twilio a {preview['recipient_label']} desde {preview['from']}.",
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
    try:
        attempt = record_twilio_call_attempt(event, call_context=call_context, force=True)
        event["attempt_record"] = {
            "path": attempt.get("path", ""),
            "status": attempt.get("status", ""),
            "pipedrive_sync": attempt.get("pipedrive_sync", {}),
        }
    except Exception as exc:
        event["attempt_record_error"] = brief(str(exc), 800)
        append_memory("twilio_call_attempt_start_error", {"call_sid": event.get("sid", ""), "error": event["attempt_record_error"]})
    return event


SPANISH_WEEKDAYS = {
    "lunes": 0,
    "monday": 0,
    "martes": 1,
    "tuesday": 1,
    "miercoles": 2,
    "miércoles": 2,
    "wednesday": 2,
    "jueves": 3,
    "thursday": 3,
    "viernes": 4,
    "friday": 4,
    "sabado": 5,
    "sábado": 5,
    "saturday": 5,
    "domingo": 6,
    "sunday": 6,
}


def scheduler_timezone_name(parameters=None):
    parameters = parameters or {}
    raw = str(first_value(parameters, "timezone", "tz", "zona_horaria", default=DEFAULT_SCHEDULER_TIMEZONE) or DEFAULT_SCHEDULER_TIMEZONE).strip()
    aliases = {
        "cdmx": "America/Mexico_City",
        "mexico": "America/Mexico_City",
        "mexico city": "America/Mexico_City",
        "ciudad de mexico": "America/Mexico_City",
        "dubai": "Asia/Dubai",
        "uae": "Asia/Dubai",
        "utc": "UTC",
    }
    normalized = normalize_security_text(raw)
    return aliases.get(normalized, raw or DEFAULT_SCHEDULER_TIMEZONE)


def scheduler_zone(parameters=None):
    name = scheduler_timezone_name(parameters)
    try:
        return ZoneInfo(name)
    except Exception:
        return ZoneInfo(DEFAULT_SCHEDULER_TIMEZONE)


def scheduler_now(parameters=None):
    return dt.datetime.now(scheduler_zone(parameters))


def scheduler_parse_iso(raw, zone):
    text = str(raw or "").strip()
    if not text:
        return None
    candidate = text.replace("Z", "+00:00")
    if re.match(r"^\d{4}-\d{2}-\d{2}\s+\d", candidate):
        candidate = candidate.replace(" ", "T", 1)
    try:
        parsed = dt.datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=zone)
    return parsed.astimezone(zone)


def scheduler_parse_date(raw, base):
    text = str(raw or "").strip().lower()
    normalized = normalize_security_text(text)
    if "pasado manana" in normalized or "pasado maniana" in normalized or "day after tomorrow" in normalized:
        return base.date() + dt.timedelta(days=2)
    if "manana" in normalized or "tomorrow" in normalized:
        return base.date() + dt.timedelta(days=1)
    if "hoy" in normalized or "today" in normalized:
        return base.date()
    for word, weekday in SPANISH_WEEKDAYS.items():
        if normalize_security_text(word) in normalized.split():
            delta = (weekday - base.weekday()) % 7
            if delta == 0 and any(token in normalized for token in ["proximo", "siguiente", "next"]):
                delta = 7
            return base.date() + dt.timedelta(days=delta)
    match = re.search(r"\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b", text)
    if match:
        return dt.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    match = re.search(r"\b(\d{1,2})[-/](\d{1,2})(?:[-/](\d{2,4}))?\b", text)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3) or base.year)
        if year < 100:
            year += 2000
        return dt.date(year, month, day)
    return None


def scheduler_parse_time(raw, base, date_was_explicit=False):
    text = str(raw or "").strip().lower()
    normalized = normalize_security_text(text)
    if "mediodia" in normalized or "medio dia" in normalized or "noon" in normalized:
        return 12, 0
    if "medianoche" in normalized or "midnight" in normalized:
        return 0, 0
    matches = list(
        re.finditer(
            r"(?<!\d)(\d{1,2})(?::(\d{2}))?\s*(a\.?\s*m\.?|p\.?\s*m\.?|am|pm)?(?!\d)",
            text,
        )
    )
    if not matches:
        return (9, 0) if date_was_explicit else (None, None)
    chosen = None
    for match in reversed(matches):
        suffix = (match.group(3) or "").replace(" ", "").replace(".", "")
        prefix = text[max(0, match.start() - 12) : match.start()]
        if suffix or "a las" in prefix or "alas" in prefix or "hora" in prefix or "at " in prefix:
            chosen = match
            break
    chosen = chosen or matches[-1]
    hour = int(chosen.group(1))
    minute = int(chosen.group(2) or 0)
    suffix = (chosen.group(3) or "").replace(" ", "").replace(".", "")
    if suffix == "pm" and hour < 12:
        hour += 12
    elif suffix == "am" and hour == 12:
        hour = 0
    elif not suffix and ("tarde" in normalized or "noche" in normalized) and 1 <= hour < 12:
        hour += 12
    elif not suffix and 1 <= hour <= 7:
        candidate = base.replace(hour=hour, minute=minute, second=0, microsecond=0)
        afternoon = candidate + dt.timedelta(hours=12)
        if candidate <= base < afternoon:
            hour += 12
    if hour > 23 or minute > 59:
        raise ValueError("Hora fuera de rango para programar la accion.")
    return hour, minute


def parse_due_at(parameters=None):
    parameters = parameters or {}
    zone = scheduler_zone(parameters)
    base = dt.datetime.now(zone)
    for key in ["delay_seconds", "in_seconds", "seconds", "segundos"]:
        value = first_value(parameters, key, default="")
        if value not in (None, ""):
            return (base + dt.timedelta(seconds=int(float(value)))).isoformat(timespec="seconds")
    for key in ["delay_minutes", "in_minutes", "minutes", "minutos", "en_minutos"]:
        value = first_value(parameters, key, default="")
        if value not in (None, ""):
            return (base + dt.timedelta(minutes=float(value))).isoformat(timespec="seconds")
    for key in ["delay_hours", "in_hours", "hours", "horas", "en_horas"]:
        value = first_value(parameters, key, default="")
        if value not in (None, ""):
            return (base + dt.timedelta(hours=float(value))).isoformat(timespec="seconds")
    for key in ["delay_days", "in_days", "days", "dias", "en_dias"]:
        value = first_value(parameters, key, default="")
        if value not in (None, ""):
            return (base + dt.timedelta(days=float(value))).isoformat(timespec="seconds")
    raw = str(first_value(parameters, "due_at", "scheduled_at", "run_at", "datetime", "date_time", "cuando", default="") or "").strip()
    if not raw:
        date_value = str(first_value(parameters, "date", "fecha", default="") or "").strip()
        time_value = str(first_value(parameters, "time", "hora", default="") or "").strip()
        raw = f"{date_value} {time_value}".strip()
    if not raw:
        raise ValueError("Falta due_at/scheduled_at, una hora humana como 'mañana a las 9', o delay_minutes para programar la accion.")
    relative = re.search(
        r"(?:dentro de|en|in)\s+(\d+(?:\.\d+)?)\s*(segundos?|seconds?|minutos?|minutes?|horas?|hours?|dias?|días?|days?|semanas?|weeks?)",
        raw,
        flags=re.I,
    )
    if relative:
        amount = float(relative.group(1))
        unit = normalize_security_text(relative.group(2))
        if unit.startswith(("segundo", "second")):
            return (base + dt.timedelta(seconds=amount)).isoformat(timespec="seconds")
        if unit.startswith(("minuto", "minute")):
            return (base + dt.timedelta(minutes=amount)).isoformat(timespec="seconds")
        if unit.startswith(("hora", "hour")):
            return (base + dt.timedelta(hours=amount)).isoformat(timespec="seconds")
        if unit.startswith(("semana", "week")):
            return (base + dt.timedelta(weeks=amount)).isoformat(timespec="seconds")
        return (base + dt.timedelta(days=amount)).isoformat(timespec="seconds")
    parsed = scheduler_parse_iso(raw, zone)
    if parsed:
        return parsed.isoformat(timespec="seconds")
    target_date = scheduler_parse_date(raw, base)
    hour, minute = scheduler_parse_time(raw, base, date_was_explicit=bool(target_date))
    if hour is None:
        raise ValueError("No pude interpretar la hora programada. Ejemplos: 'mañana a las 9', 'hoy 5:30 pm' o '2026-05-29T17:30:00'.")
    target_date = target_date or base.date()
    parsed = dt.datetime.combine(target_date, dt.time(hour=hour, minute=minute), tzinfo=zone)
    if not scheduler_parse_date(raw, base) and parsed <= base:
        parsed = parsed + dt.timedelta(days=1)
    return parsed.isoformat(timespec="seconds")


def parse_scheduled_datetime(value, timezone_name=DEFAULT_SCHEDULER_TIMEZONE):
    zone = scheduler_zone({"timezone": timezone_name})
    parsed = scheduler_parse_iso(value, zone)
    if not parsed:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=zone)
    return parsed.astimezone(zone)


def due_at_is_ready(due_at, timezone_name=DEFAULT_SCHEDULER_TIMEZONE):
    parsed = parse_scheduled_datetime(due_at, timezone_name)
    return parsed <= dt.datetime.now(parsed.tzinfo)


def normalize_recurrence(value):
    raw = str(value or "").strip()
    normalized = normalize_security_text(raw)
    mapping = {
        "daily": "daily",
        "diario": "daily",
        "cada dia": "daily",
        "cada dia diario": "daily",
        "weekdays": "weekdays",
        "lunes a viernes": "weekdays",
        "laborales": "weekdays",
        "dias laborales": "weekdays",
        "weekly": "weekly",
        "semanal": "weekly",
        "cada semana": "weekly",
        "hourly": "hourly",
        "cada hora": "hourly",
    }
    return mapping.get(normalized, normalized if normalized in {"daily", "weekdays", "weekly", "hourly"} else "")


def next_recurrence_due_at(due_at, recurrence, timezone_name=DEFAULT_SCHEDULER_TIMEZONE):
    recurrence = normalize_recurrence(recurrence)
    if not recurrence:
        return ""
    parsed = parse_scheduled_datetime(due_at, timezone_name)
    if recurrence == "hourly":
        return (parsed + dt.timedelta(hours=1)).isoformat(timespec="seconds")
    if recurrence == "weekly":
        return (parsed + dt.timedelta(days=7)).isoformat(timespec="seconds")
    if recurrence == "weekdays":
        candidate = parsed + dt.timedelta(days=1)
        while candidate.weekday() >= 5:
            candidate += dt.timedelta(days=1)
        return candidate.isoformat(timespec="seconds")
    return (parsed + dt.timedelta(days=1)).isoformat(timespec="seconds")


def scheduled_target_from_parameters(parameters=None):
    parameters = dict(parameters or {})
    target_provider = str(first_value(parameters, "target_provider", "provider", "app", "tool", "herramienta", default="") or "").strip().lower()
    target_action = str(first_value(parameters, "target_action", "api_action", "do", "task_action", "accion", "action", default="") or "").strip().lower()
    nested = parameters.get("target_parameters")
    if not isinstance(nested, dict):
        nested = parameters.get("parameters")
    target_parameters = dict(nested or {})
    reserved = {
        "target_provider", "provider", "app", "tool", "herramienta", "target_action", "api_action", "do",
        "task_action", "accion", "action", "target_parameters", "parameters", "due_at", "scheduled_at",
        "run_at", "datetime", "date_time", "cuando", "date", "fecha", "time", "hora", "timezone", "tz",
        "zona_horaria", "delay_seconds", "in_seconds", "seconds", "segundos", "delay_minutes", "in_minutes",
        "minutes", "minutos", "en_minutos", "delay_hours", "in_hours", "hours", "horas", "en_horas",
        "delay_days", "in_days", "days", "dias", "en_dias", "recurrence", "repeat", "rrule", "repetir",
        "schedule_label", "label",
    }
    for key, value in parameters.items():
        if key not in reserved and key not in target_parameters:
            target_parameters[key] = value
    if target_provider in {"scheduler", "schedule", "time", "timer", "agenda"}:
        target_provider = ""
    if target_provider in {"", "all", "auto", "kim", "agent"}:
        resolved_provider, resolved_action, resolved_parameters = agent_action_defaults(target_action, target_parameters)
        target_provider = resolved_provider
        target_action = resolved_action
        target_parameters = resolved_parameters
    if not target_provider or not target_action:
        raise ValueError("No pude inferir que accion debe ejecutar Kim. Usa target_provider/target_action o action=send_sms, call_phone, create_task, send_email, etc.")
    if target_action in {"schedule_action", "programar_accion", "schedule_task", "agendar_tarea"}:
        raise ValueError("No se permite programar una accion programada dentro de otra.")
    return target_provider, target_action, target_parameters


def scheduled_target_preview(provider, action, parameters):
    provider = (provider or "").strip().lower()
    action = (action or "").strip().lower()
    if provider in {"twilio", "sms", "phone", "telefono", "whatsapp"} and action in {"send_sms", "sms", "text_message", "mensaje_sms"}:
        return twilio_message_preview(parameters, channel="sms")
    if provider in {"twilio", "sms", "phone", "telefono", "whatsapp"} and action in {"send_whatsapp", "whatsapp", "whatsapp_message"}:
        return twilio_message_preview(parameters, channel="whatsapp")
    if provider in {"twilio", "sms", "phone", "telefono", "whatsapp"} and action in {"call_phone", "call", "make_call", "llamar", "llamada"}:
        return twilio_call_preview(parameters)
    return {
        "provider": provider,
        "action": action,
        "parameters": sanitize_for_log(parameters),
        "to": first_value(parameters, "to", "phone", "telefono", "email", "correo", default=""),
        "from": first_value(parameters, "from", "from_number", "mailbox", "sender", default=""),
    }


def schedule_api_bridge_action(parameters=None, confirm=False):
    parameters = dict(parameters or {})
    due_at = parse_due_at(parameters)
    timezone_name = scheduler_timezone_name(parameters)
    target_provider, target_action, target_parameters = scheduled_target_from_parameters(parameters)
    recurrence = normalize_recurrence(first_value(parameters, "recurrence", "repeat", "repetir", "rrule", default=""))
    due_dt = parse_scheduled_datetime(due_at, timezone_name)
    now_dt = dt.datetime.now(due_dt.tzinfo)
    if due_dt <= now_dt:
        if recurrence:
            while due_dt <= now_dt:
                due_at = next_recurrence_due_at(due_at, recurrence, timezone_name)
                due_dt = parse_scheduled_datetime(due_at, timezone_name)
        else:
            raise ValueError(
                "La hora programada quedo en el pasado. Vuelve a indicar una hora futura, por ejemplo 'hoy 8:30 pm', 'mañana 9 am' o 'en 10 minutos'."
            )
    preview = scheduled_target_preview(target_provider, target_action, target_parameters)
    label = str(first_value(parameters, "schedule_label", "label", "title", "titulo", default="") or "").strip()
    summary = label or f"Programar {target_provider}/{target_action} para {due_at}."
    execution_parameters = {
        "target_provider": target_provider,
        "target_action": target_action,
        "target_parameters": target_parameters,
        "due_at": due_at,
        "timezone": timezone_name,
        "recurrence": recurrence,
        "schedule_label": summary,
    }
    if not confirm:
        return confirmation_preview(
            "scheduler",
            "schedule_action",
            summary,
            {**preview, "due_at": due_at, "timezone": timezone_name, "recurrence": recurrence},
            execution_parameters=execution_parameters,
        )
    contact = {}
    phone = first_value(target_parameters, "to", "phone", "telefono", "recipient", "destinatario", default="")
    email = first_value(target_parameters, "email", "correo", "to_email", default="")
    display_name = first_value(target_parameters, "contact_name", "client_name", "name", "nombre", default=phone or email)
    if phone or email or display_name:
        contact = crm_upsert_contact(
            {
                "phone": phone,
                "email": email,
                "display_name": display_name,
                "company": first_value(target_parameters, "company", "empresa", "organization", default=""),
                "contact_type": first_value(target_parameters, "contact_type", "tipo", default="client"),
                "notes": "Contacto asociado a accion programada por Kim.",
            },
            source="kim_scheduler",
        )
    schedule_id = crm_id("SC")
    now = now_iso()
    payload = {
        "_target_provider": target_provider,
        "_target_action": target_action,
        "_target_parameters": target_parameters,
        "_schedule_label": summary,
        "_recurrence": recurrence,
        "_timezone": timezone_name,
        "_created_by": "kim_live_scheduler",
    }
    to_value = first_value(target_parameters, "to", "phone", "telefono", "recipient", "destinatario", "email", "correo", default="")
    from_value = first_value(target_parameters, "from", "from_number", "mailbox", "sender", default="")
    with crm_connect() as conn:
        conn.execute(
            """
            INSERT INTO scheduled_actions
            (id, status, provider, action, due_at, timezone, contact_id, company_id, to_value, from_value, payload_json, created_at, updated_at)
            VALUES (?, 'pending', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                schedule_id,
                target_provider,
                target_action,
                due_at,
                timezone_name,
                contact.get("id"),
                contact.get("company_id"),
                normalize_call_context_value(to_value),
                normalize_call_context_value(from_value),
                json.dumps(payload, ensure_ascii=False),
                now,
                now,
            ),
        )
        conn.commit()
    event = {
        "ok": True,
        "provider": "scheduler",
        "action": "schedule_action",
        "scheduled_action_id": schedule_id,
        "target_provider": target_provider,
        "target_action": target_action,
        "due_at": due_at,
        "timezone": timezone_name,
        "recurrence": recurrence,
        "contact_id": contact.get("id"),
        "confirmed": True,
    }
    append_memory("kim_action_scheduled", event)
    return event


def schedule_twilio_action(action, parameters=None, confirm=False):
    parameters = dict(parameters or {})
    if action in {"schedule_call", "programar_llamada", "agendar_llamada"}:
        target_action = "call_phone"
    elif action in {"schedule_whatsapp", "programar_whatsapp", "agendar_whatsapp"}:
        target_action = "send_whatsapp"
    else:
        target_action = "send_sms"
    return schedule_api_bridge_action(
        {
            **parameters,
            "target_provider": "twilio",
            "target_action": target_action,
            "target_parameters": {key: value for key, value in parameters.items()},
        },
        confirm=confirm,
    )


def due_scheduled_actions(limit=10):
    with crm_connect() as conn:
        rows = [dict(row) for row in conn.execute("SELECT * FROM scheduled_actions WHERE status='pending' ORDER BY due_at ASC LIMIT ?", (limit,)).fetchall()]
    return [row for row in rows if due_at_is_ready(row["due_at"], row.get("timezone") or DEFAULT_SCHEDULER_TIMEZONE)]


def update_scheduled_action(schedule_id, status, result=None, increment_attempt=False):
    now = now_iso()
    increment = 1 if increment_attempt else 0
    with crm_connect() as conn:
        conn.execute(
            "UPDATE scheduled_actions SET status=?, result_json=?, attempts=attempts+?, updated_at=?, executed_at=? WHERE id=?",
            (status, json.dumps(result or {}, ensure_ascii=False), increment, now, now if status in {"done", "failed", "cancelled"} else "", schedule_id),
        )
        conn.commit()


def execute_confirmed_bridge_action(provider, action, parameters):
    provider = (provider or "").strip().lower()
    action = (action or "").strip().lower()
    parameters = dict(parameters or {})
    if provider in {"", "all", "auto", "kim", "agent"}:
        provider, action, parameters = agent_action_defaults(action, parameters)
    if provider in {"twilio", "sms", "phone", "telefono", "whatsapp"}:
        return run_twilio_bridge(action, parameters, confirm=True)
    if provider == "clickup":
        return run_clickup_bridge(action, parameters, confirm=True)
    if provider == "notion":
        return run_notion_bridge(action, parameters, confirm=True)
    if provider in {"hostinger", "hostinger_mail", "tesca_mail", "business_mail", "imap", "smtp", "email", "mail", "correo"}:
        return run_hostinger_mail_bridge(action, parameters, confirm=True)
    if provider in {"pipedrive", "pipe_drive", "pd"}:
        return run_pipedrive_bridge(action, parameters, confirm=True)
    if provider in {"portfolio", "ignis_portfolio", "ignis_financials", "ignis financials", "portafolio"}:
        return portfolio_cli(action, {**parameters, "confirm": True})
    if provider in {"crm", "bifrost_crm", "clients", "clientes", "contacts", "contactos"}:
        return run_crm_bridge(action, parameters, confirm=True)
    if provider in {"gmail", "google_mail"}:
        return run_gmail_bridge(action, parameters, confirm=False)
    if provider in {"google_maps", "maps", "places", "geocoding", "routes"}:
        return run_google_maps_bridge(action, parameters, confirm=False)
    raise ValueError(f"Proveedor programado no soportado: {provider}/{action}")


def scheduled_result_text(result):
    result = dict(result or {})
    provider = result.get("provider") or ""
    action = result.get("action") or ""
    if provider in {"hostinger_mail", "gmail"} and action in {"list_messages", "search_messages", "list"}:
        messages = result.get("messages") or []
        lines = [
            f"Reporte Kim: encontre {result.get('total_matches', result.get('count', len(messages)))} correos relacionados.",
        ]
        for index, item in enumerate(messages[:8], start=1):
            sender = item.get("from") or "Remitente no disponible"
            subject = item.get("subject") or "Sin asunto"
            date_value = item.get("date") or ""
            lines.append(f"{index}. {subject} | {sender} | {date_value}".strip())
        if len(messages) > 8:
            lines.append(f"... y {len(messages) - 8} mas en la consulta.")
        return "\n".join(lines)
    if result.get("summary"):
        return str(result.get("summary"))
    if result.get("message"):
        return str(result.get("message"))
    return brief(json.dumps(sanitize_for_log(result), ensure_ascii=False), 1400)


def render_scheduled_follow_up(value, result_text, result):
    if isinstance(value, dict):
        return {key: render_scheduled_follow_up(item, result_text, result) for key, item in value.items()}
    if isinstance(value, list):
        return [render_scheduled_follow_up(item, result_text, result) for item in value]
    if isinstance(value, str):
        rendered = value.replace("{{action_result}}", result_text)
        rendered = rendered.replace("{{summary}}", result_text)
        rendered = rendered.replace("{{result_json}}", brief(json.dumps(sanitize_for_log(result), ensure_ascii=False), 1800))
        if normalize_security_text(rendered) in {"dr yehoshua", "doctor yehoshua", "dr yehoshua dubai", "doctor"}:
            return DOCTOR_DUBAI_WHATSAPP_TO
        return rendered
    return value


def execute_scheduled_follow_up(target_parameters, result, parent_schedule_id=""):
    follow_up = target_parameters.get("follow_up_action")
    if not isinstance(follow_up, dict):
        return {}
    provider = str(first_value(follow_up, "target_provider", "provider", "app", "tool", default="") or "").strip().lower()
    action = str(first_value(follow_up, "target_action", "action", "api_action", "accion", default="") or "").strip().lower()
    raw_parameters = follow_up.get("target_parameters")
    if not isinstance(raw_parameters, dict):
        raw_parameters = follow_up.get("parameters")
    parameters = dict(raw_parameters or {})
    if not provider or not action:
        raise ValueError("follow_up_action requiere target_provider/provider y target_action/action.")
    result_text = scheduled_result_text(result)
    parameters = render_scheduled_follow_up(parameters, result_text, result)
    parameters.setdefault("scheduled_parent_id", parent_schedule_id)
    follow_result = execute_confirmed_bridge_action(provider, action, parameters)
    follow_result["scheduled_parent_id"] = parent_schedule_id
    record_api_bridge_action(provider, action, parameters, follow_result, session_id="kim-scheduler", transcript="")
    return follow_result


def clone_recurring_scheduled_action(row, result=None):
    payload = json.loads(row.get("payload_json") or "{}")
    recurrence = normalize_recurrence(payload.get("_recurrence") or "")
    if not recurrence:
        return None
    next_due = next_recurrence_due_at(row.get("due_at"), recurrence, row.get("timezone") or DEFAULT_SCHEDULER_TIMEZONE)
    if not next_due:
        return None
    schedule_id = crm_id("SC")
    now = now_iso()
    payload["_previous_schedule_id"] = row.get("id")
    payload["_last_result_summary"] = brief(json.dumps(result or {}, ensure_ascii=False), 500)
    with crm_connect() as conn:
        conn.execute(
            """
            INSERT INTO scheduled_actions
            (id, status, provider, action, due_at, timezone, contact_id, company_id, to_value, from_value, payload_json, created_at, updated_at)
            VALUES (?, 'pending', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                schedule_id,
                row.get("provider"),
                row.get("action"),
                next_due,
                row.get("timezone") or DEFAULT_SCHEDULER_TIMEZONE,
                row.get("contact_id"),
                row.get("company_id"),
                row.get("to_value") or "",
                row.get("from_value") or "",
                json.dumps(payload, ensure_ascii=False),
                now,
                now,
            ),
        )
        conn.commit()
    append_memory("kim_recurring_action_rescheduled", {"previous_id": row.get("id"), "next_id": schedule_id, "next_due_at": next_due, "recurrence": recurrence})
    return schedule_id


def execute_scheduled_action(row):
    payload = json.loads(row.get("payload_json") or "{}")
    target_provider = payload.get("_target_provider") or row.get("provider")
    target_action = payload.get("_target_action") or payload.get("target_action") or row.get("action")
    target_parameters = dict(payload.get("_target_parameters") or payload)
    if target_provider in {"twilio", "sms", "phone", "telefono", "whatsapp"}:
        target_parameters["from_number"] = target_parameters.get("from_number") or row.get("from_value") or twilio_default_from_number()
    result = execute_confirmed_bridge_action(target_provider, target_action, target_parameters)
    result["scheduled_action_id"] = row.get("id")
    follow_up_result = execute_scheduled_follow_up(target_parameters, result, parent_schedule_id=row.get("id"))
    if follow_up_result:
        result["follow_up_action_result"] = follow_up_result
    record_api_bridge_action(target_provider, target_action, target_parameters, result, session_id="kim-scheduler", transcript="")
    update_scheduled_action(row["id"], "done" if result.get("ok") else "failed", result)
    if result.get("ok"):
        clone_recurring_scheduled_action(row, result=result)
    return result


def recover_stale_scheduled_actions():
    cutoff = dt.datetime.now() - dt.timedelta(seconds=SCHEDULER_STALE_RUNNING_SECONDS)
    recovered = []
    with crm_connect() as conn:
        rows = [dict(row) for row in conn.execute("SELECT * FROM scheduled_actions WHERE status='running'").fetchall()]
        for row in rows:
            try:
                updated = dt.datetime.fromisoformat(str(row.get("updated_at") or row.get("created_at") or "").replace("Z", "+00:00"))
            except ValueError:
                updated = cutoff - dt.timedelta(seconds=1)
            if updated.tzinfo is not None:
                updated = updated.replace(tzinfo=None)
            if updated <= cutoff:
                conn.execute(
                    "UPDATE scheduled_actions SET status='pending', result_json=?, updated_at=? WHERE id=?",
                    (json.dumps({"recovered_from_stale_running": True, "at": now_iso()}, ensure_ascii=False), now_iso(), row.get("id")),
                )
                recovered.append(row.get("id"))
        conn.commit()
    if recovered:
        append_memory("kim_scheduler_recovered_stale_actions", {"ids": recovered})
    return recovered


def compact_scheduled_payload(value, key_name=""):
    if isinstance(value, dict):
        return {key: compact_scheduled_payload(item, key) for key, item in value.items()}
    if isinstance(value, list):
        return [compact_scheduled_payload(item, key_name) for item in value[:20]]
    if isinstance(value, str):
        lowered = key_name.lower()
        if "transcript" in lowered or "conversation" in lowered:
            return brief(value, 240)
        return brief(value, 500)
    return value


def list_scheduled_actions(status="", limit=100):
    params = []
    where = ""
    if status:
        where = "WHERE status=?"
        params.append(status)
    params.append(int(limit or 100))
    with crm_connect() as conn:
        rows = [
            dict(row)
            for row in conn.execute(
                f"SELECT * FROM scheduled_actions {where} ORDER BY due_at ASC LIMIT ?",
                params,
            ).fetchall()
        ]
    for row in rows:
        raw_payload = row.pop("payload_json", "")
        raw_result = row.pop("result_json", "")
        try:
            row["payload"] = compact_scheduled_payload(sanitize_for_log(json.loads(raw_payload or "{}")))
        except json.JSONDecodeError:
            row["payload"] = {}
        row["result_summary"] = brief(raw_result, 800)
    return rows


def cancel_scheduled_action(schedule_id):
    schedule_id = str(schedule_id or "").strip()
    if not schedule_id:
        raise ValueError("Falta scheduled_action_id para cancelar.")
    update_scheduled_action(schedule_id, "cancelled", {"cancelled_at": now_iso()}, increment_attempt=False)
    append_memory("kim_scheduled_action_cancelled", {"scheduled_action_id": schedule_id})
    return {"ok": True, "provider": "scheduler", "action": "cancel_schedule", "scheduled_action_id": schedule_id}


def run_scheduler_bridge(action, parameters=None, confirm=False):
    action = (action or "").strip().lower()
    parameters = parameters or {}
    if action in {"status", "list", "list_schedules", "scheduled_actions", "upcoming", "agenda"}:
        return {
            "ok": True,
            "provider": "scheduler",
            "action": action or "list_schedules",
            "timezone": DEFAULT_SCHEDULER_TIMEZONE,
            "actions": list_scheduled_actions(
                status=str(first_value(parameters, "status", default="") or ""),
                limit=int(first_value(parameters, "limit", default=100) or 100),
            ),
        }
    if action in {"schedule_action", "programar_accion", "schedule_task", "agendar_tarea", "hacer_luego"}:
        return schedule_api_bridge_action(parameters, confirm=confirm)
    if action in {"cancel", "cancel_schedule", "cancel_action", "cancelar", "cancelar_accion"}:
        return cancel_scheduled_action(first_value(parameters, "scheduled_action_id", "schedule_id", "id", default=""))
    raise ValueError("Accion scheduler no soportada. Usa schedule_action, list_schedules o cancel_schedule.")


def scheduler_loop():
    while True:
        try:
            recover_stale_scheduled_actions()
            for row in due_scheduled_actions():
                try:
                    update_scheduled_action(row["id"], "running", {"started_at": now_iso()}, increment_attempt=True)
                    execute_scheduled_action(row)
                except Exception as exc:
                    update_scheduled_action(row["id"], "failed", {"error": brief(str(exc), 800)})
                    append_memory("scheduled_action_error", {"id": row.get("id"), "error": brief(str(exc), 800)})
        except Exception as exc:
            append_memory("scheduler_loop_error", {"error": brief(str(exc), 800)})
        time.sleep(20)


def start_scheduler_once():
    global SCHEDULER_THREAD_STARTED, SCHEDULER_THREAD_REF
    with SCHEDULER_LOCK:
        if SCHEDULER_THREAD_STARTED:
            return
        crm_write_readme()
        crm_connect().close()
        thread = threading.Thread(target=scheduler_loop, daemon=True, name="kim-scheduler")
        thread.start()
        SCHEDULER_THREAD_REF = thread
        SCHEDULER_THREAD_STARTED = True


def codex_automation_runtime_status():
    path = pathlib.Path.home() / ".codex" / "automations" / "revisar-tareas-de-telegram-kim" / "automation.toml"
    if not path.exists():
        return {"id": "revisar-tareas-de-telegram-kim", "exists": False, "status": "missing"}
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        return {"id": "revisar-tareas-de-telegram-kim", "exists": True, "status": "unknown", "error": brief(str(exc), 300)}
    match = re.search(r'(?m)^status\s*=\s*"([^"]+)"', text)
    return {
        "id": "revisar-tareas-de-telegram-kim",
        "exists": True,
        "status": match.group(1) if match else "unknown",
        "path": str(path),
    }


def local_clock_status():
    now = scheduler_now({"timezone": DEFAULT_SCHEDULER_TIMEZONE})
    pending = list_scheduled_actions(status="pending", limit=20)
    due = due_scheduled_actions(limit=10)
    return {
        "ok": True,
        "provider": "kim_local_clock",
        "app_version": APP_VERSION,
        "timezone": DEFAULT_SCHEDULER_TIMEZONE,
        "now": now.isoformat(timespec="seconds"),
        "scheduler_thread_started": SCHEDULER_THREAD_STARTED,
        "scheduler_thread_alive": bool(SCHEDULER_THREAD_REF and SCHEDULER_THREAD_REF.is_alive()),
        "poll_interval_seconds": 20,
        "pending_count": len(pending),
        "due_count": len(due),
        "next_actions": pending[:8],
        "codex_automation": codex_automation_runtime_status(),
        "note": "Kim ejecuta scheduled_actions con el reloj local del servidor; no requiere automations de Codex.",
    }


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
        if not first_value(parameters, "to", "recipient", "phone", "telefono", "destinatario"):
            parameters = {
                **parameters,
                "to": DOCTOR_DUBAI_WHATSAPP_TO,
                "contact_name": first_value(parameters, "contact_name", "client_name", "name", default="Dr. Yehoshua Dubai"),
                "relationship": first_value(parameters, "relationship", default="doctor_control"),
                "company": first_value(parameters, "company", default="AI People"),
                "context_id": first_value(parameters, "context_id", "kim_context_id", default="DOCTOR-WHATSAPP-" + today()),
            }
        return twilio_send_message(parameters, confirm=confirm, channel="whatsapp")
    if action in {"call_phone", "call", "make_call", "llamar", "llamada"}:
        return twilio_start_call(parameters, confirm=confirm)
    if action in {
        "schedule_call",
        "programar_llamada",
        "agendar_llamada",
        "schedule_sms",
        "programar_sms",
        "agendar_sms",
        "schedule_whatsapp",
        "programar_whatsapp",
        "agendar_whatsapp",
    }:
        return schedule_twilio_action(action, parameters, confirm=confirm)
    if action in {"call_report", "latest_call", "list_calls", "get_call", "call_summary", "call_history", "reporte_llamada", "ultima_llamada"}:
        if action in {"latest_call", "ultima_llamada"}:
            parameters = {**parameters, "limit": 1}
        return twilio_call_report(parameters)
    if action in {"whatsapp_report", "list_whatsapp_threads", "whatsapp_threads", "recent_whatsapp", "whatsapp_inbox"}:
        return twilio_whatsapp_report(parameters)
    if action in {"sync_call_attempts", "reconcile_calls", "reconcile_call_attempts", "sincronizar_intentos"}:
        return twilio_reconcile_call_attempts(parameters)
    raise ValueError(f"Accion Twilio no soportada: {action}")


def run_crm_bridge(action, parameters, confirm=False):
    action = (action or "").strip().lower()
    parameters = parameters or {}
    if action in {"status", "estado"}:
        return crm_status()
    if action in {"doctor_pending_report", "pending_report", "doctor_priorities", "prioridades_doctor", "doctor_digest"}:
        return doctor_pending_report(parameters)
    if action in {"list_contacts", "contacts", "clientes", "contactos", "search_contacts"}:
        return crm_list_contacts(parameters)
    if action in {"person_context", "get_person_context", "supervise_person", "modo", "mode"}:
        return person_context_supervision_payload(
            query=first_value(parameters, "query", "q", "name", "nombre", "contact_name", "person", "persona", default=""),
            limit=int(first_value(parameters, "limit", default=1) or 1),
        )
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
            "sync_persons",
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
    canonical = re.search(r"\bcanonical_pipedrive_person_id=(\d+)\b", notes, flags=re.IGNORECASE)
    if canonical:
        return canonical.group(1)
    matches = re.findall(r"\bPipedrive\s+person_id=(\d+)\b", notes, flags=re.IGNORECASE)
    return matches[-1] if matches else ""


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


def pipedrive_person_phone_values(person):
    values = []
    if person.get("phone"):
        values.append(person.get("phone"))
    values.extend(person.get("phones") or [])
    return compact_unique(values, limit=20)


def pipedrive_person_has_phone(person, phone):
    target = twilio_lookup_phone_number(phone)
    target_digits = phone_digits(target)
    if not target_digits:
        return False
    for value in pipedrive_person_phone_values(person):
        candidate = twilio_lookup_phone_number(value)
        if candidate and candidate == target:
            return True
        if phone_digits(candidate) == target_digits:
            return True
    return False


def pipedrive_phone_index_is_fresh(payload, max_age_seconds=21600):
    try:
        updated = dt.datetime.fromisoformat(str(payload.get("updated_at") or "").replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return False
    now = dt.datetime.now(updated.tzinfo) if updated.tzinfo else dt.datetime.now()
    return (now - updated).total_seconds() <= max_age_seconds


def load_pipedrive_phone_index(max_age_seconds=21600):
    payload = read_json_file_any([RUNTIME_PIPEDRIVE_PHONE_INDEX, PIPEDRIVE_PHONE_INDEX], {})
    if payload:
        payload["stale"] = not pipedrive_phone_index_is_fresh(payload, max_age_seconds=max_age_seconds)
        return payload
    return {}


def build_pipedrive_phone_index(max_records=1000):
    index = {}
    people = []
    checked = 0
    start = 0
    page_limit = 100
    while checked < max_records:
        payload = pipedrive_request("/persons", params={"start": start, "limit": page_limit})
        data = payload.get("data") or []
        if not data:
            break
        for item in data:
            person = normalize_pipedrive_person(item)
            checked += 1
            if not person.get("id"):
                continue
            people.append(person)
            for value in pipedrive_person_phone_values(person):
                digits = phone_digits(value)
                if not digits:
                    continue
                index.setdefault(digits, []).append(person)
        pagination = ((payload.get("additional_data") or {}).get("pagination") or {})
        if not pagination.get("more_items_in_collection"):
            break
        next_start = pagination.get("next_start")
        if next_start is None:
            break
        start = int(next_start)
    payload = {
        "ok": True,
        "updated_at": now_iso(),
        "checked": checked,
        "phone_count": len(index),
        "phones": index,
    }
    write_json_file_both(PIPEDRIVE_PHONE_INDEX, RUNTIME_PIPEDRIVE_PHONE_INDEX, payload)
    append_memory("pipedrive_phone_index_refreshed", {"checked": checked, "phone_count": len(index)})
    return payload


def pipedrive_exact_phone_scan(phone, max_records=1000):
    normalized_phone = twilio_lookup_phone_number(phone)
    digits = phone_digits(normalized_phone)
    if not digits:
        return []
    payload = load_pipedrive_phone_index()
    if not payload:
        payload = build_pipedrive_phone_index(max_records=max_records)
    matches = (payload.get("phones") or {}).get(digits) or []
    if matches:
        return matches
    if payload.get("stale"):
        run_background_task("refresh-pipedrive-phone-index", build_pipedrive_phone_index, max_records)
    return []


def pipedrive_registered_person_for_phone(phone, limit=25):
    normalized_phone = twilio_lookup_phone_number(phone)
    if not normalized_phone:
        return {
            "registered": False,
            "reason": "missing_phone",
            "message": "Falta telefono para validar registro en Pipedrive.",
            "person": None,
            "candidates": [],
        }
    candidates = []
    local_contact = crm_find_contact_by_phone(normalized_phone)
    local_person_id = pipedrive_person_id_from_local_contact(local_contact)
    if local_person_id:
        try:
            payload = pipedrive_request(f"/persons/{urllib.parse.quote(str(local_person_id))}")
            person = normalize_pipedrive_person(pipedrive_payload_data(payload) or {})
            if person.get("id"):
                candidates.append(person)
        except Exception as exc:
            append_memory(
                "pipedrive_message_guard_local_lookup_error",
                {"phone": normalized_phone, "person_id": local_person_id, "error": brief(str(exc), 500)},
            )
    try:
        exact_scan = pipedrive_exact_phone_scan(normalized_phone)
        if len(exact_scan) == 1:
            return {
                "registered": True,
                "reason": "exact_pipedrive_phone_scan",
                "message": "Contacto validado en Pipedrive por telefono exacto.",
                "person": exact_scan[0],
                "candidates": exact_scan,
            }
        if len(exact_scan) > 1:
            exact_scan = sorted(exact_scan, key=lambda item: item.get("update_time") or item.get("add_time") or "", reverse=True)
            return {
                "registered": True,
                "reason": "duplicate_exact_pipedrive_phone_match",
                "message": "Contacto validado en Pipedrive por telefono exacto, pero hay duplicados que conviene limpiar.",
                "person": exact_scan[0],
                "candidates": exact_scan[:5],
            }
        search = pipedrive_search_persons({"phone": normalized_phone, "term": normalized_phone, "limit": limit})
        for person in search.get("persons") or []:
            if person.get("id") and not person.get("phones"):
                try:
                    payload = pipedrive_request(f"/persons/{urllib.parse.quote(str(person.get('id')))}")
                    person = normalize_pipedrive_person(pipedrive_payload_data(payload) or {})
                except Exception:
                    pass
            candidates.append(person)
    except Exception as exc:
        return {
            "registered": False,
            "reason": "pipedrive_lookup_error",
            "message": f"No pude validar Pipedrive antes de enviar mensaje: {brief(str(exc), 240)}",
            "person": None,
            "candidates": [],
            "error": brief(str(exc), 800),
        }
    seen = {}
    for person in candidates:
        if person.get("id") and person.get("id") not in seen:
            seen[person["id"]] = person
    candidates = list(seen.values())
    exact = [person for person in candidates if pipedrive_person_has_phone(person, normalized_phone)]
    if len(exact) == 1:
        return {
            "registered": True,
            "reason": "exact_pipedrive_phone_match",
            "message": "Contacto validado en Pipedrive por telefono exacto.",
            "person": exact[0],
            "candidates": candidates[:5],
        }
    if len(exact) > 1:
        exact = sorted(exact, key=lambda item: item.get("update_time") or item.get("add_time") or "", reverse=True)
        return {
            "registered": True,
            "reason": "duplicate_exact_pipedrive_phone_match",
            "message": "Contacto validado en Pipedrive por telefono exacto, pero hay duplicados que conviene limpiar.",
            "person": exact[0],
            "candidates": exact[:5],
        }
    return {
        "registered": False,
        "reason": "not_registered_in_pipedrive",
        "message": f"El destinatario {normalized_phone} no esta registrado en Pipedrive con telefono exacto.",
        "person": None,
        "candidates": candidates[:5],
    }


def pipedrive_registered_person_for_phone_fast(phone):
    normalized_phone = twilio_lookup_phone_number(phone)
    if not normalized_phone:
        return {
            "registered": False,
            "reason": "missing_phone",
            "message": "Falta telefono para validar registro en Pipedrive.",
            "person": None,
            "candidates": [],
        }
    local_contact = crm_find_contact_by_phone(normalized_phone)
    local_person_id = pipedrive_person_id_from_local_contact(local_contact)
    if local_person_id:
        person = {
            "id": int(local_person_id),
            "name": (local_contact or {}).get("display_name") or normalized_phone,
            "phone": normalized_phone,
            "phones": [normalized_phone],
            "organization": "",
        }
        return {
            "registered": True,
            "reason": "local_crm_pipedrive_person_id",
            "message": "Contacto validado por CRM local con Pipedrive person_id.",
            "person": person,
            "candidates": [person],
        }
    payload = load_pipedrive_phone_index(max_age_seconds=60 * 60 * 24 * 30)
    matches = ((payload.get("phones") or {}).get(phone_digits(normalized_phone)) or []) if payload else []
    if matches:
        matches = sorted(matches, key=lambda item: item.get("update_time") or item.get("add_time") or "", reverse=True)
        return {
            "registered": True,
            "reason": "cached_pipedrive_phone_index",
            "message": "Contacto validado por indice local de Pipedrive.",
            "person": matches[0],
            "candidates": matches[:5],
        }
    return {
        "registered": False,
        "reason": "not_in_fast_cache",
        "message": "El telefono no aparece en CRM local ni en el indice local de Pipedrive.",
        "person": None,
        "candidates": [],
    }


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


def pipedrive_sync_persons(parameters=None):
    parameters = parameters or {}
    term = str(first_value(parameters, "term", "query", "q", "search", default="") or "").strip()
    start = max(0, int(first_value(parameters, "start", default=0) or 0))
    limit = max(1, min(int(first_value(parameters, "limit", default=100) or 100), 300))
    if term:
        people = pipedrive_person_candidates(term, limit=limit)
    else:
        people = []
        cursor = start
        while len(people) < limit:
            page_limit = min(100, limit - len(people))
            payload = pipedrive_request("/persons", params={"start": cursor, "limit": page_limit})
            batch = [normalize_pipedrive_person(item) for item in (payload.get("data") or [])]
            if not batch:
                break
            people.extend(batch)
            cursor += len(batch)
            pagination = ((payload.get("additional_data") or {}).get("pagination") or {})
            if not pagination.get("more_items_in_collection"):
                break
    synced = []
    for person in people[:limit]:
        notes = [f"Pipedrive person_id={person.get('id')}."]
        if person.get("organization"):
            notes.append(f"Organizacion: {person.get('organization')}.")
        local_contact = crm_upsert_contact(
            {
                "display_name": person.get("name") or "Contacto Pipedrive",
                "email": person.get("email") or "",
                "phone": person.get("phone") or "",
                "company": person.get("organization") or "",
                "contact_type": first_value(parameters, "contact_type", "tipo", default="client"),
                "notes": " ".join(notes),
            },
            source="pipedrive_sync",
        )
        synced.append(
            {
                "person_id": person.get("id"),
                "name": person.get("name"),
                "phone": person.get("phone"),
                "email": person.get("email"),
                "organization": person.get("organization"),
                "local_contact_id": local_contact.get("id"),
                "local_markdown_path": local_contact.get("markdown_path"),
            }
        )
    append_daily_note(
        f"Kim CRM sync: Pipedrive -> local; synced={len(synced)}; "
        f"mode={'search' if term else 'full'}; query={term or 'all'}"
    )
    return {
        "ok": True,
        "provider": "pipedrive",
        "action": "sync_persons",
        "mode": "search" if term else "full",
        "query": term,
        "count": len(synced),
        "synced": synced[:20],
        "has_more": len(synced) > 20,
    }


def run_pipedrive_bridge(action, parameters, confirm=False):
    action = (action or "").strip().lower()
    parameters = parameters or {}
    if action in {"status", "me"}:
        return {"ok": True, "provider": "pipedrive", "action": action, "status": pipedrive_status(live=True)}
    if action in {"list_persons", "persons", "contacts", "contactos", "search_persons", "search_contacts", "buscar_personas"}:
        return pipedrive_search_persons(parameters)
    if action in {"sync_persons", "sync_contacts", "sync_local_crm", "sync_crm"}:
        return pipedrive_sync_persons(parameters)
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
    written = write_json_file_both(CLICKUP_STRUCTURE_JSON, RUNTIME_CLICKUP_STRUCTURE_JSON, snapshot)
    if not written and spaces:
        append_memory("clickup_structure_write_warning", {"error": "No pude escribir snapshot ClickUp en BIFROST ni runtime."})
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
    parameters = clickup_apply_operational_defaults(parameters)
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


def notion_default_parent_config():
    config = read_json_file_any([NOTION_DEFAULT_PARENT, RUNTIME_NOTION_DEFAULT_PARENT], {})
    return config if isinstance(config, dict) else {}


def notion_access_inventory_data():
    data = read_json_file_any(
        [MEMORY_CONTEXT_DIR / "notion_access_inventory.json", RUNTIME_CONTEXT / "notion_access_inventory.json"],
        {},
    )
    return data if isinstance(data, dict) else {}


def notion_inventory_database_map():
    items = notion_access_inventory_data().get("databases") or []
    mapping = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        if name:
            mapping[name.lower()] = item
    return mapping


def notion_inventory_database_name_for_id(database_id):
    database_id = str(database_id or "").strip()
    if not database_id:
        return ""
    for key, item in notion_inventory_database_map().items():
        if str(item.get("id") or "").strip() == database_id:
            return str(item.get("name") or key).strip()
    return ""


def notion_resolved_parent_from_config(config, source="configured_default"):
    config = config if isinstance(config, dict) else {}
    if config.get("parent_page_id"):
        resolved = {"type": "page_id", "page_id": str(config["parent_page_id"]), "source": source}
        for key in ["title_property", "date_property", "type_property", "url", "note"]:
            if config.get(key):
                resolved[key] = config.get(key)
        return resolved
    if config.get("parent_database_id"):
        resolved = {"type": "database_id", "database_id": str(config["parent_database_id"]), "source": source}
        for key in ["title_property", "date_property", "type_property", "url", "note"]:
            if config.get(key):
                resolved[key] = config.get(key)
        name = notion_inventory_database_name_for_id(config.get("parent_database_id"))
        if name:
            resolved["name"] = name
        return resolved
    return {}


def notion_resolved_parent_from_inventory(name, source="inventory_route"):
    item = notion_inventory_database_map().get(str(name or "").strip().lower())
    if not item:
        return {}
    resolved = {"type": "database_id", "database_id": str(item.get("id") or ""), "source": source, "url": item.get("url", "")}
    for key in ["title_property", "date_property", "type_property", "recommended_use"]:
        if item.get(key):
            resolved[key] = item.get(key)
    if item.get("name"):
        resolved["name"] = item.get("name")
    return resolved


def notion_event_like(parameters=None):
    parameters = parameters or {}
    blob = " ".join(
        [
            str(first_value(parameters, "title", "name", "subject", "asunto", "page_title") or ""),
            str(first_value(parameters, "content", "body", "text", "message", "description", "summary") or ""),
            str(first_value(parameters, "meeting_type", "tipo", "event_type", "type", "category") or ""),
        ]
    )
    text = normalize_security_text(blob)
    if not text:
        return False
    keywords = [
        "reunion",
        "meeting",
        "calendario",
        "calendar",
        "evento",
        "event",
        "recordatorio",
        "alarma",
        "agenda",
        "cita",
    ]
    return any(keyword in text for keyword in keywords)


def notion_infer_inventory_destination(parameters=None):
    parameters = parameters or {}
    if notion_event_like(parameters):
        return "Reuniones"

    explicit_fields = [
        str(first_value(parameters, "notion_parent_query", "parent_query", "workspace", "parent", "domain") or "").strip(),
        str(first_value(parameters, "target_database", "database_name", "destination", "bucket") or "").strip(),
    ]
    for raw in explicit_fields:
        key = raw.lower()
        if key in notion_inventory_database_map():
            return notion_inventory_database_map()[key].get("name") or raw

    blob = normalize_security_text(
        " ".join(
            [
                str(first_value(parameters, "title", "name", "subject", "asunto", "page_title") or ""),
                str(first_value(parameters, "content", "body", "text", "message", "description", "summary") or ""),
                str(first_value(parameters, "notion_parent_query", "parent_query", "workspace", "parent", "domain") or ""),
            ]
        )
    )
    if not blob:
        return "Wiki"

    if any(
        keyword in blob
        for keyword in [
            "contrato",
            "proposal",
            "propuesta",
            "reporte",
            "report",
            "documento",
            "document",
            "archivo",
            "pdf",
            "brief",
            "cotizacion",
            "cotización",
            "invoice",
        ]
    ):
        return "Documentos"
    if any(
        keyword in blob
        for keyword in [
            "project",
            "proyecto",
            "roadmap",
            "milestone",
            "hito",
            "launch",
            "lanzamiento",
            "backlog",
        ]
    ):
        return "Projects"
    return "Wiki"


def notion_parent_config_value(parameters=None, resolved=None, *keys, default=""):
    parameters = parameters or {}
    resolved = resolved or {}
    config = notion_default_parent_config()
    for source in [parameters, resolved, config]:
        for key in keys:
            value = str(source.get(key) or "").strip()
            if value:
                return value
    return default


def notion_database_title_property(parameters=None, resolved=None):
    return notion_parent_config_value(parameters, resolved, "title_property", default="Name")


def notion_bridge_database_properties(parameters=None, resolved=None):
    parameters = parameters or {}
    properties = parameters.get("properties") if isinstance(parameters.get("properties"), dict) else {}
    merged = dict(properties)
    date_property = notion_parent_config_value(parameters, resolved, "date_property", "datetime_property", "calendar_property")
    start = str(
        first_value(
            parameters,
            "start_at",
            "starts_at",
            "start",
            "date_start",
            "scheduled_for",
            "event_at",
            "datetime",
            "date",
            "hora_inicio",
            "inicio",
        )
        or ""
    ).strip()
    end = str(first_value(parameters, "end_at", "ends_at", "end", "date_end", "hora_fin", "fin") or "").strip()
    if date_property and start and date_property not in merged:
        date_payload = {"start": start}
        if end:
            date_payload["end"] = end
        merged[date_property] = {"date": date_payload}
    type_property = notion_parent_config_value(parameters, resolved, "type_property", "meeting_type_property")
    meeting_type = str(first_value(parameters, "meeting_type", "tipo", "event_type", "type", "category") or "").strip()
    if type_property and meeting_type and type_property not in merged:
        merged[type_property] = {"select": {"name": meeting_type}}
    return merged


def semantic_notion_parent(value):
    text = normalize_security_text(value)
    if not text:
        return False
    return text in {"general", "memoria", "memory", "kim", "kim live", "bifrost", "portafolio", "portfolio", "notas", "notes"}


def notion_resolve_default_parent(parameters=None):
    parameters = parameters or {}
    config = notion_default_parent_config()
    configured = notion_resolved_parent_from_config(config)
    configured_name = str(configured.get("name") or "").strip().lower()
    preferred_name = str(notion_infer_inventory_destination(parameters) or "").strip()
    preferred_key = preferred_name.lower()
    if preferred_name:
        if configured and configured_name == preferred_key:
            return configured
        resolved = notion_resolved_parent_from_inventory(preferred_name, source=f"inventory:{preferred_key}")
        if resolved:
            return resolved
    if configured:
        return configured
    query_terms = []
    if preferred_name:
        query_terms.append(preferred_name)
    if notion_event_like(parameters):
        query_terms.extend(["Meetings", "Calendario"])
    for key in ["notion_parent_query", "parent_query", "workspace", "domain"]:
        value = str(parameters.get(key) or "").strip()
        if value:
            query_terms.append(value)
    query_terms.extend(["Kim Live", "BIFROST", "AI People", "General"])
    seen = set()
    for query in query_terms:
        query_key = normalize_security_text(query)
        if not query_key or query_key in seen:
            continue
        seen.add(query_key)
        try:
            result = notion_request("/search", method="POST", payload={"query": query, "page_size": 10})
        except Exception:
            continue
        for item in result.get("results", []) or []:
            obj = item.get("object")
            item_id = item.get("id")
            if obj in {"page", "database"} and item_id:
                parent_type = "page_id" if obj == "page" else "database_id"
                resolved = {"type": parent_type, parent_type: item_id, "source": f"search:{query}", "url": item.get("url", "")}
                config_payload = {
                    "updated_at": now_iso(),
                    "parent_page_id": item_id if obj == "page" else "",
                    "parent_database_id": item_id if obj == "database" else "",
                    "source": resolved["source"],
                    "url": resolved.get("url", ""),
                    "note": "Auto default for Kim Live Notion create_page. Change this file when the doctor chooses a better Notion destination.",
                }
                if obj == "database" and query_key in {"reuniones", "meetings", "calendario", "calendar"}:
                    config_payload.update(
                        {
                            "title_property": "Nombre",
                            "date_property": "Hora",
                            "type_property": "Tipo",
                            "note": "Default meeting/calendar database for Kim Live. Adjust if the doctor later picks another Notion destination.",
                        }
                    )
                write_json_file_any([NOTION_DEFAULT_PARENT, RUNTIME_NOTION_DEFAULT_PARENT], config_payload)
                resolved.update(
                    {
                        key: config_payload[key]
                        for key in ["title_property", "date_property", "type_property"]
                        if config_payload.get(key)
                    }
                )
                return resolved
    return {}


def notion_outbox_markdown(title, parameters, reason=""):
    content = str(first_value(parameters, "content", "body", "text", "message", "description", "summary") or "").strip()
    lines = [
        f"# {title}",
        "",
        f"- Created: {now_iso()}",
        "- Provider target: Notion",
        "- Status: local_outbox_pending_parent",
    ]
    if reason:
        lines.append(f"- Reason: {reason}")
    lines.extend(["", "## Content", "", content or "Sin contenido."])
    return "\n".join(lines).strip() + "\n"


def save_notion_outbox(title, parameters, reason=""):
    safe = knowledge_slug(title)
    filename = f"{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}-{safe}.md"
    markdown = notion_outbox_markdown(title, parameters, reason=reason)
    path = write_text_file_any([NOTION_OUTBOX_DIR / today() / filename, RUNTIME_NOTION_OUTBOX_DIR / today() / filename], markdown)
    return str(path) if path else ""


def build_notion_create_page_payload(parameters):
    parameters = dict(parameters or {})
    title = str(first_value(parameters, "title", "name", "subject", "asunto", "page_title") or "").strip()
    if not title:
        source_text = str(first_value(parameters, "content", "body", "text", "message", "description", "summary") or "").strip()
        title = brief(source_text, 80) if source_text else generated_title("Nota Kim")
    parent_page_id = str(first_value(parameters, "parent_page_id", "page_id", "parent_id", "notion_page_id") or "").strip()
    parent_database_id = str(first_value(parameters, "parent_database_id", "database_id", "parent_database", "notion_database_id") or "").strip()
    resolved = {}
    if semantic_notion_parent(parent_page_id):
        parent_page_id = ""
    if semantic_notion_parent(parent_database_id):
        parent_database_id = ""
    if parent_page_id:
        parent = {"type": "page_id", "page_id": parent_page_id}
        properties = {"title": {"title": notion_rich_text(title)}}
    elif parent_database_id:
        title_property = notion_database_title_property(parameters, resolved)
        parent = {"type": "database_id", "database_id": parent_database_id}
        properties = {title_property: {"title": notion_rich_text(title)}}
    else:
        resolved = notion_resolve_default_parent(parameters)
        if not resolved:
            raise ValueError("Falta parent real de Notion. Guarde un default en notion_default_parent.json o comparta una pagina/base con la integracion.")
        if resolved.get("type") == "page_id":
            parent = {"type": "page_id", "page_id": resolved.get("page_id")}
            properties = {"title": {"title": notion_rich_text(title)}}
        else:
            title_property = notion_database_title_property(parameters, resolved)
            parent = {"type": "database_id", "database_id": resolved.get("database_id")}
            properties = {title_property: {"title": notion_rich_text(title)}}
        parameters["_notion_parent_resolution"] = resolved
    payload = {"parent": parent, "properties": properties}
    if parent.get("type") == "database_id":
        payload["properties"].update(notion_bridge_database_properties(parameters, resolved))
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
    if action in {"schedule_action", "programar_accion", "schedule_task", "agendar_tarea", "hacer_luego", "programar", "agenda"}:
        return "scheduler", "schedule_action", data
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
        if not first_value(data, "to", "recipient", "phone", "telefono", "destinatario"):
            data["to"] = DOCTOR_DUBAI_WHATSAPP_TO
            data.setdefault("contact_name", "Dr. Yehoshua Dubai")
            data.setdefault("relationship", "doctor_control")
            data.setdefault("company", "AI People")
            data.setdefault("context_id", "DOCTOR-WHATSAPP-" + today())
        return "twilio", "send_whatsapp", data
    if action in {
        "send_portfolio",
        "send_portfolio_report",
        "portfolio_report",
        "enviar_portafolio",
        "mandar_portafolio",
        "enviame_portafolio_actualizado",
        "sr_eli_portfolio",
        "send_sr_eli_portfolio",
    }:
        return "portfolio", "send_whatsapp_report", data
    if action in {
        "fundamental_report",
        "portfolio_fundamental_report",
        "reporte_fundamental",
        "reporte_fundamental_sr_eli",
        "catalizadores_portafolio",
        "sr_eli_fundamental",
    }:
        return "portfolio", "fundamental_report", data
    if action in {"call_phone", "call", "make_call", "llamar", "llamada"}:
        return "twilio", "call_phone", data
    if action in {"call_report", "latest_call", "get_call", "call_summary", "reporte_llamada", "ultima_llamada"}:
        return "twilio", "call_report", data
    if action in {"sync_call_attempts", "reconcile_calls", "sincronizar_intentos"}:
        return "twilio", "sync_call_attempts", data
    if action in {"schedule_call", "programar_llamada", "agendar_llamada"}:
        return "twilio", "schedule_call", data
    if action in {"schedule_sms", "programar_sms", "agendar_sms"}:
        return "twilio", "schedule_sms", data
    if action in {"schedule_whatsapp", "programar_whatsapp", "agendar_whatsapp"}:
        if not first_value(data, "to", "recipient", "phone", "telefono", "destinatario"):
            data["to"] = DOCTOR_DUBAI_WHATSAPP_TO
            data.setdefault("contact_name", "Dr. Yehoshua Dubai")
            data.setdefault("relationship", "doctor_control")
            data.setdefault("company", "AI People")
            data.setdefault("context_id", "DOCTOR-WHATSAPP-" + today())
        return "twilio", "schedule_whatsapp", data
    if action in {
        "create_zoom_invite",
        "send_zoom_invite",
        "zoom_invite",
        "zoom_invitation",
        "mandar_invitacion_zoom",
        "enviar_invitacion_zoom",
        "agendar_y_enviar_zoom",
        "crear_y_enviar_zoom",
    }:
        if not first_value(data, "topic", "title", "subject", "name", "asunto"):
            data["topic"] = generated_title("Reunion Zoom Kim")
        return "zoom", "create_and_send_invite", data
    if action in {"create_zoom_meeting", "schedule_zoom_meeting", "zoom_meeting", "agendar_zoom", "crear_zoom", "reunion_zoom", "reunión_zoom"}:
        if not first_value(data, "topic", "title", "subject", "name", "asunto"):
            data["topic"] = generated_title("Reunion Zoom Kim")
        return "zoom", "create_meeting", data
    if action in {"zoom_transcript", "get_zoom_transcript", "fetch_zoom_transcript", "transcript_zoom", "transcripcion_zoom", "transcripción_zoom"}:
        return "zoom", "get_transcript", data
    if action in {"send_zoom_transcript", "send_zoom_summary", "reenviar_zoom_transcript", "reenviar_resumen_zoom", "mandar_resumen_zoom", "mandar_transcript_zoom"}:
        return "zoom", "send_transcript", data
    if action in {"find_place", "text_search", "search_place", "buscar_lugar", "buscar_empresa", "maps_search"}:
        return "google_maps", "find_place", data
    if action in {"geocode", "geocode_address", "validar_direccion", "validar_dirección", "address_lookup"}:
        return "google_maps", "geocode", data
    if action in {"route_distance", "route", "directions", "distance", "distancia", "ruta"}:
        return "google_maps", "route_distance", data
    if action in {"timezone", "time_zone", "zona_horaria"}:
        return "google_maps", "timezone", data
    if action in {"save_contact", "create_contact", "upsert_contact", "guardar_contacto", "crear_contacto"}:
        return "crm", "upsert_contact", data
    if action in {"create_task", "add_task", "task", "tarea", "registrar_tarea", "crear_tarea"}:
        if not first_value(data, "name", "title", "subject", "task_name", "task", "asunto"):
            data["name"] = generated_title("Tarea Kim")
        data = clickup_apply_operational_defaults(data)
        return "clickup", "create_task", data
    if action in {"update_task", "change_task", "cambiar_tarea", "actualizar_tarea"}:
        return "clickup", "update_task", data
    if action in {"comment_task", "comentario_tarea", "comentar_tarea"}:
        return "clickup", "comment_task", data
    if action in {"create_page", "note", "nota", "notion_note", "crear_nota"}:
        if not first_value(data, "title", "name", "subject", "asunto", "page_title"):
            data["title"] = generated_title("Nota Kim")
        return "notion", "create_page", data
    if action in {"schedule_meeting", "create_meeting", "meeting", "agendar_reunion", "agendar_reunión", "crear_reunion", "crear_reunión", "agendar_cita"}:
        if not first_value(data, "title", "name", "subject", "asunto", "page_title"):
            data["title"] = generated_title("Reunion Kim")
        if not first_value(data, "meeting_type", "tipo", "event_type", "type", "category"):
            data["meeting_type"] = "Brainstorming"
        if not first_value(data, "notion_parent_query", "parent_query", "workspace", "domain", "parent_database_id", "database_id"):
            data["notion_parent_query"] = "Reuniones"
        return "notion", "create_page", data
    return "", action, data


def api_bridge_templates():
    write_clickup_operation_map_snapshot()
    return {
        "agent_action": {
            "description": "Accion de alto nivel para que Kim escriba por API sin reconstruir JSON complicado.",
            "actions": [
                "send_email",
                "reply_email",
                "send_sms",
                "send_whatsapp",
                "send_portfolio_report",
                "fundamental_report",
                "call_phone",
                "call_report",
                "sync_call_attempts",
                "schedule_action",
                "schedule_call",
                "schedule_sms",
                "schedule_whatsapp",
                "create_zoom_meeting",
                "create_zoom_invite",
                "zoom_transcript",
                "send_zoom_summary",
                "find_place",
                "geocode_address",
                "route_distance",
                "timezone",
                "save_contact",
                "mark_spam",
                "move_to_trash",
                "archive_email",
                "create_task",
                "update_task",
                "comment_task",
                "create_page",
                "pipedrive_sync_persons",
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
                    "action": "create_zoom_meeting",
                    "parameters": {
                        "topic": "Diagnostico AI People con Dr. Yehoshua",
                        "start_at": "mañana a las 11",
                        "duration": 30,
                        "timezone": "America/Mexico_City",
                        "agenda": "Llamada diagnostica para entender dolor operativo y siguiente paso.",
                    },
                    "confirm": False,
                },
                {
                    "provider": "all",
                    "action": "schedule_action",
                    "parameters": {
                        "target_provider": "twilio",
                        "target_action": "send_sms",
                        "target_parameters": {"to": "+525500000000", "body": "Recordatorio de Kim Live."},
                        "due_at": "mañana a las 9",
                    },
                    "confirm": False,
                },
                {
                    "provider": "all",
                    "action": "schedule_call",
                    "parameters": {"to": "+525500000000", "contact_name": "Cliente", "delay_minutes": 30},
                    "confirm": False,
                },
                {
                    "provider": "all",
                    "action": "schedule_whatsapp",
                    "parameters": {"to": "whatsapp:+971585943726", "body": "Recordatorio programado de Kim Live.", "delay_minutes": 10},
                    "confirm": False,
                },
            ],
        },
        "scheduler": {
            "schedule_action": {
                "required": ["target_action", "due_at or delay_minutes"],
                "aliases": {
                    "target_provider": ["provider", "app", "tool", "herramienta"],
                    "target_action": ["action", "api_action", "accion"],
                    "target_parameters": ["parameters", "payload"],
                    "due_at": ["scheduled_at", "run_at", "datetime", "cuando"],
                    "timezone": ["tz", "zona_horaria"],
                    "recurrence": ["repeat", "repetir"],
                },
                "rule": (
                    "Usa esta accion cuando el doctor diga 'haz esto a tal hora'. "
                    "Preparar con confirm=false; al confirmar queda en BIFROST/CRM/scheduled_actions y el runtime Kim Live la ejecuta aunque Codex este cerrado. "
                    "Soporta target_provider/target_action para twilio, clickup, notion, pipedrive, hostinger_mail y crm. "
                    "Horarios aceptan ISO o lenguaje humano: 'hoy 5:30 pm', 'mañana a las 9', 'lunes a las 8', 'en 2 horas'."
                ),
            },
            "list_schedules": {
                "optional": ["status", "limit"],
                "rule": "Lista acciones programadas locales sin ejecutar nada.",
            },
            "cancel_schedule": {
                "required": ["scheduled_action_id"],
                "rule": "Cancela una accion programada local.",
            },
        },
        "crm": {
            "status": {
                "rule": "Valida la base local en BIFROST/CRM sin modificar datos.",
            },
            "list_contacts": {
                "optional": ["query", "contact_type", "limit"],
                "rule": "Consulta clientes/contactos guardados en BIFROST/CRM antes de llamar, mandar SMS o registrar notas.",
            },
            "person_context": {
                "optional": ["query", "name", "phone", "limit"],
                "aliases": {
                    "query": ["q", "name", "nombre", "contact_name", "person", "persona"],
                },
                "rule": (
                    "Carga el modo de una persona: ficha BIFROST, CRM, context blocks, interacciones, transcripts y pendientes. "
                    "Usar cuando el doctor diga 'modo Naomi', 'modo Ilian' o antes de llamar/responder con contexto propio."
                ),
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
        "google_maps": {
            "status": {
                "rule": "Valida si existe API key de Google Maps sin imprimirla. Usa validate_key para una prueba viva con Geocoding.",
            },
            "find_place": {
                "required": ["query"],
                "optional": ["location", "radius_meters", "region_code", "max_results", "language"],
                "aliases": {
                    "query": ["text", "q", "place", "business", "name", "lugar", "empresa"],
                    "location": ["near", "latlng", "ubicacion", "ubicación"],
                    "radius_meters": ["radius", "radio"],
                    "region_code": ["country", "region", "pais", "país"],
                },
                "rule": (
                    "Busca negocios/lugares en Google Places. Devuelve nombre, direccion, coordenadas, Google Maps URL, telefono, web, rating y tipos cuando Google lo entregue. "
                    "No guarda en CRM por si sola; para guardar un prospecto usa despues provider=crm o pipedrive con confirmacion."
                ),
            },
            "geocode": {
                "required": ["address or latlng"],
                "aliases": {
                    "address": ["query", "q", "direccion", "dirección"],
                    "latlng": ["location", "ubicacion", "ubicación"],
                },
                "rule": "Convierte direccion a coordenadas o coordenadas a direccion. Usar para validar direcciones antes de guardar clientes o planear rutas.",
            },
            "route_distance": {
                "required": ["origin", "destination"],
                "optional": ["travel_mode", "language", "routing_preference"],
                "aliases": {
                    "origin": ["from", "origen"],
                    "destination": ["to", "destino"],
                    "travel_mode": ["mode", "modo"],
                },
                "defaults": {
                    "travel_mode": "DRIVE",
                    "routing_preference": "TRAFFIC_AWARE",
                },
                "rule": "Calcula distancia y tiempo aproximado con Routes API. Usar para coordinar visitas, logística o sugerir ubicación de reunión.",
            },
            "timezone": {
                "required": ["location or address"],
                "aliases": {
                    "location": ["latlng", "ubicacion", "ubicación"],
                    "address": ["query", "direccion", "dirección"],
                },
                "rule": "Devuelve zona horaria de coordenadas o direccion. Util para agenda/llamadas internacionales.",
            },
        },
        "portfolio": {
            "refresh_prices": {
                "optional": ["providers"],
                "rule": (
                    "Borra caches locales de precio y fuerza una nueva validacion con fuentes frescas. "
                    "Usar antes de enviar portafolio cuando el doctor pida precios actuales o diga que Kim trae precios viejos."
                ),
            },
            "client_report": {
                "optional": ["include_units", "providers", "force_refresh_prices"],
                "rule": (
                    "Genera reporte deterministico Sr. Eli: monto invertido, entrada, precio actual validado, variacion y balance. "
                    "No envia mensajes. Por defecto usa Binance, MEXC y Bybit; CoinGecko/CoinMarketCap pueden sumarse si estan disponibles."
                ),
            },
            "fundamental_report": {
                "optional": ["query", "providers", "max_queries", "dry_run"],
                "defaults": {
                    "providers": ["binance", "mexc", "bybit"],
                    "max_queries": 3,
                    "dry_run": False,
                },
                "rule": (
                    "Usar cuando el doctor pida reporte fundamental, catalizadores, oportunidades o contexto macro del Portafolio Sr. Eli. "
                    "Primero genera el client_report validado, despues investiga fuentes actuales y estructura: catalizadores internacionales, "
                    "narrativas cripto populares, catalizadores por activo, oportunidades, riesgos/fuentes y siguiente accion. "
                    "No envia WhatsApp automaticamente y no debe inventar catalizadores sin fuente reciente."
                ),
            },
            "send_whatsapp_report": {
                "optional": ["to", "providers", "dry_run", "force_refresh_prices"],
                "defaults": {
                    "to": DOCTOR_DUBAI_WHATSAPP_TO,
                    "providers": ["binance", "mexc", "bybit"],
                    "force_refresh_prices": True,
                },
                "rule": (
                    "Usar cuando el doctor diga 'enviame el portafolio actualizado' o pida mandar el portafolio Sr. Eli. "
                    "Calcula con el ledger, valida al menos dos fuentes frescas y manda lineas separadas por WhatsApp. "
                    "Si el destino es el WhatsApp Dubai del doctor, no requiere confirmacion; cualquier otro destino prepara confirmacion."
                ),
            },
        },
        "zoom": {
            "status": {
                "rule": "Valida Client ID, Client Secret, autorizacion OAuth y host disponible sin crear reuniones.",
            },
            "auth_url": {
                "rule": "Devuelve https://kim.aipeople.app/oauth/zoom/start para autorizar Zoom cuando falte refresh_token.",
            },
            "list_users": {
                "optional": ["limit", "page_size"],
                "rule": "Con OAuth de usuario devuelve /users/me; con Server-to-Server lista usuarios activos si el scope lo permite.",
            },
            "list_meetings": {
                "optional": ["type", "limit", "page_size"],
                "rule": "Lista reuniones programadas del usuario autorizado o host configurado.",
            },
            "create_meeting": {
                "required": ["topic or title", "start_at"],
                "aliases": {
                    "topic": ["title", "subject", "name", "asunto"],
                    "start_at": ["start_time", "due_at", "scheduled_at", "datetime", "cuando"],
                    "duration": ["duration_minutes", "minutes", "duracion"],
                    "agenda": ["description", "content", "body", "objective", "objetivo"],
                    "timezone": ["tz", "zona_horaria"],
                    "host_user_id": ["host_id", "host_email", "user_id", "user", "email"],
                },
                "defaults": {
                    "duration": 30,
                    "timezone": DEFAULT_SCHEDULER_TIMEZONE,
                    "settings": {"waiting_room": True, "join_before_host": False},
                },
                "rule": (
                    "Preparar con confirm=false. Al confirmar crea una reunion Zoom real y guarda meeting_id/join_url "
                    "en BIFROST/MEMORY/context/zoom_meetings.jsonl. Usa OAuth de usuario si se autorizo desde /oauth/zoom/start; "
                    "si se usa Server-to-Server, no uses 'me' y pasa host_user_id/host_email o deja que Kim elija usuario activo."
                ),
            },
                "create_and_send_invite": {
                "required": ["topic or title", "start_at"],
                "optional": ["duration", "agenda", "timezone", "whatsapp_to", "email_to", "mailbox", "contact_name", "company"],
                "aliases": {
                    "topic": ["title", "subject", "name", "asunto"],
                    "start_at": ["start_time", "due_at", "scheduled_at", "datetime", "cuando"],
                    "whatsapp_to": ["to_whatsapp", "phone", "telefono", "whatsapp"],
                    "email_to": ["to_email", "email", "correo"],
                    "mailbox": ["from", "sender", "account"],
                },
                "rule": (
                    "Preparar con confirm=false. Al confirmar crea una reunion Zoom real, formatea la invitacion con join_url, "
                    "meeting_id/passcode si existen, y la envia por WhatsApp y/o correo. WhatsApp proactivo mantiene la regla "
                    "de Pipedrive: el telefono debe pertenecer a una persona registrada salvo que sea el WhatsApp de control del doctor. "
                    "Si faltan destinatarios, crea la reunion y devuelve invite_text listo para copiar."
                ),
            },
            "get_transcript": {
                "required": ["meeting_id or meeting_uuid"],
                "aliases": {
                    "meeting_id": ["meetingId", "id", "meeting_uuid", "uuid", "recording_id"],
                },
                "rule": (
                    "Lee el transcript de una reunion Zoom y lo guarda en BIFROST/MEMORY/zoom_transcripts. "
                    "Requiere OAuth autorizado y scope de lectura de recordings/transcripts. Solo funciona si Zoom genero cloud recording "
                    "con audio transcript; si no existe, Kim debe decirlo claramente y no inventar transcript."
                ),
            },
            "send_transcript": {
                "required": ["meeting_id or meeting_uuid"],
                "optional": ["send_type", "whatsapp_to", "email_to", "mailbox", "subject", "contact_name", "company"],
                "aliases": {
                    "meeting_id": ["meetingId", "id", "meeting_uuid", "uuid", "recording_id"],
                    "send_type": ["content_type", "tipo"],
                    "whatsapp_to": ["to_whatsapp", "phone", "telefono", "whatsapp"],
                    "email_to": ["to_email", "email", "correo"],
                    "mailbox": ["from", "sender", "account"],
                },
                "defaults": {
                    "send_type": "summary",
                },
                "rule": (
                    "Preparar con confirm=false. Descarga/guarda el transcript y prepara envio de resumen por defecto. "
                    "Para email puede enviar transcript completo si send_type=transcript; para WhatsApp recorta mensajes largos y conserva ruta BIFROST. "
                    "El envio real por WhatsApp/correo requiere confirmacion."
                ),
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
            "sync_persons": {
                "optional": ["term", "query", "start", "limit", "contact_type"],
                "aliases": {
                    "term": ["query", "q", "search", "name"],
                    "contact_type": ["tipo"],
                },
                "rule": "Sin confirmacion: lee personas de Pipedrive y sincroniza el CRM local BIFROST. Usar para preparar memoria de clientes.",
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
                "required": ["to", "body or content_sid", "from or messaging_service_sid"],
                "aliases": {
                    "to": ["recipient", "phone", "telefono", "destinatario"],
                    "body": ["message", "text", "content", "mensaje"],
                    "content_sid": ["ContentSid", "template_sid"],
                    "content_variables": ["ContentVariables", "template_variables"],
                },
                "rule": "Usa formato whatsapp:+numero. Fuera de la ventana de 24h requiere template aprobado con content_sid y content_variables; texto libre solo funciona despues de mensaje inbound del usuario.",
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
                    "context_block_id": ["context_id", "kim_context_id"],
                    "parent_context_id": ["parent_block_id", "context_parent_id"],
                    "campaign_label": ["context_group", "group_name", "campaign"],
                    "context_scope": ["scope"],
                    "next_step_hint": ["post_response_action", "followup_hint"],
                },
                "defaults": {
                    "from": twilio_default_from_number() or "numero Twilio con capacidad Voice",
                    "url": "https://kim.aipeople.app/twilio/voice",
                },
                "rule": "Preparar con confirm=false. Si el doctor pide llamar a una tercera persona, SIEMPRE incluye contact_name, relationship, call_context, objective, questions y report_to_doctor. Cada llamada queda ligada a un bloque CTX-* en BIFROST/MEMORY/calls/_context_blocks. Llamar requiere confirmacion explicita; la conversacion se guarda en BIFROST/MEMORY/calls y BIFROST/CRM.",
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
            "sync_call_attempts": {
                "optional": ["since", "limit"],
                "rule": "Reconcilia callbacks Twilio ya recibidos: crea/actualiza memoria PHONE-<CallSid>, CRM local y actividad Pipedrive para intentos contestados y no contestados. No inicia llamadas nuevas.",
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
            "schedule_whatsapp": {
                "required": ["to", "body", "due_at or delay_minutes"],
                "rule": "Preparar con confirm=false. Si el destino es el doctor, usa whatsapp:+971585943726 por defecto. Al confirmar, queda programado en la base local CRM.",
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
            "routing_catalog": {
                "rule": "Kim no debe pedir IDs al doctor para tareas normales. El bridge transforma voice-of-customer a team/space/list usando el catalogo local. Si el texto menciona una lista existente, la usa; si no, enruta por dominio.",
                "default_examples": [
                    "Kim/BIFROST/API/Telegram/Twilio -> ruta operativa Kim.",
                    "Portafolio/Ignis/Eli -> Ignis Stock Financials / Investor follow-up / Khalil.",
                    "Cliente/prospecto/CRM/Isaac -> Ai people / Client Follow-up.",
                    "Shabat/personal/recordatorio -> Dr Y / Personal Life / Scheduled.",
                    "Neorgana/Tesca comercial -> Tesca Elements / Neorgana / Commercial.",
                ],
                "catalog_paths": [str(CLICKUP_OPERATION_MAP), str(RUNTIME_CLICKUP_OPERATION_MAP)],
            },
            "create_task": {
                "required": ["name"],
                "aliases": {
                    "name": ["title", "subject", "task_name", "task", "asunto"],
                    "description": ["body", "content", "message", "notes", "summary", "text"],
                    "list_name": ["list", "target_list"],
                    "space_name": ["space", "workspace", "team_space"],
                },
                "defaults": {
                    "name": "se genera desde description o 'Tarea Kim <timestamp>'",
                    "list_name": "se resuelve desde catalogo operativo si Kim no pasa lista",
                },
                "rule": "Preparar con confirm=false. No pidas list_id al doctor: pasa texto/descripcion y deja que el bridge enrute. Si el doctor dice un workspace como Tesca Elements o Ai people, el bridge lo baja a un Space/List real. Si de verdad falta destino, usa el fallback operativo y deja routing_note.",
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
                "required": ["title or content"],
                "aliases": {
                    "title": ["name", "subject", "asunto", "page_title"],
                    "content": ["body", "text", "message", "description", "summary"],
                    "parent_page_id": ["page_id", "parent_id", "notion_page_id"],
                    "parent_database_id": ["database_id", "parent_database", "notion_database_id"],
                },
                "defaults": {
                    "title": "se genera desde content o 'Nota Kim <timestamp>'",
                    "title_property": "Name para bases genericas; Nombre para la base Reuniones",
                    "date_property": "Hora para reuniones/eventos si existe start_at",
                    "type_property": "Tipo para reuniones/eventos si existe meeting_type",
                    "parent": "default configurable en BIFROST/MEMORY/context/notion_default_parent.json; si falta, se guarda outbox local.",
                },
                "rule": "No pidas IDs en conversacion normal. Para reuniones usa action agent_action/schedule_meeting o notion/create_page con title, content, start_at, end_at, meeting_type. Si falta parent real, el bridge intenta resolver Reuniones y, si Notion no tiene un destino compartido, guarda la nota en BIFROST/MEMORY/notion_outbox para no perder contexto.",
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
        "google_maps_status",
        lambda: run_google_maps_bridge("status", {}),
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
        "notion_wiki_route_payload",
        lambda: (
            lambda payload: {
                "ok": payload.get("parent", {}).get("database_id") == "10a5954b-05ab-4836-b33b-828c00fad57c",
                "parent": payload.get("parent"),
                "property_keys": sorted(payload.get("properties", {}).keys()),
            }
        )(
            build_notion_create_page_payload(
                {
                    "title": "AI Spirits - Capítulo 6",
                    "content": "Knowledge chapter sync.",
                }
            )
        ),
    )
    run_case(
        "notion_documents_route_payload",
        lambda: (
            lambda payload: {
                "ok": payload.get("parent", {}).get("database_id") == "1413f254-cf3d-4cf6-8809-88ebd0dedc70",
                "parent": payload.get("parent"),
                "property_keys": sorted(payload.get("properties", {}).keys()),
            }
        )(
            build_notion_create_page_payload(
                {
                    "title": "Contrato AI People",
                    "content": "Documento contractual para firma.",
                }
            )
        ),
    )
    run_case(
        "notion_meeting_route_payload",
        lambda: (
            lambda payload: {
                "ok": payload.get("parent", {}).get("database_id") == "f901a42b-7cd7-4a61-8efc-0b8c22128b4c",
                "parent": payload.get("parent"),
                "property_keys": sorted(payload.get("properties", {}).keys()),
            }
        )(
            build_notion_create_page_payload(
                {
                    "title": "Reunión de prueba",
                    "start_at": "2026-05-25T09:00:00",
                    "end_at": "2026-05-25T09:30:00",
                    "meeting_type": "Brainstorming",
                }
            )
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
        "clickup_workspace_auto_route",
        lambda: run_clickup_bridge(
            "create_task",
            {
                "space_name": "Tesca Elements",
                "list_name": "Nueva",
                "title": "Debe enrutar workspace a lista real",
                "content": "Dry run de ruta automatica.",
            },
            confirm=False,
        ),
    )
    ok = all(item.get("ok") for item in tests)
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
        parameters = clickup_apply_operational_defaults(parameters)
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
        title = str(first_value(parameters, "title", "name", "subject", "asunto", "page_title") or "").strip()
        if not title:
            title = brief(str(first_value(parameters, "content", "body", "text", "message", "description", "summary") or ""), 80) or "Nota Kim"
        try:
            payload = build_notion_create_page_payload(parameters)
        except ValueError as exc:
            reason = brief(str(exc), 500)
            outbox_path = save_notion_outbox(title, parameters, reason=reason)
            result = {
                "ok": True,
                "provider": "notion",
                "action": action,
                "mode": "local_outbox",
                "confirmed": False,
                "requires_notion_parent_configuration": True,
                "outbox_path": outbox_path,
                "message": "No pude crear en Notion porque falta un parent compartido/configurado; guarde la nota en outbox local BIFROST para no perder contexto.",
                "parent_config_path": str(NOTION_DEFAULT_PARENT),
                "runtime_parent_config_path": str(RUNTIME_NOTION_DEFAULT_PARENT),
            }
            append_memory("notion_outbox_saved", {"title": title, "outbox_path": outbox_path, "reason": reason})
            return result
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
    elif provider in {"scheduler", "schedule", "time", "timer", "agenda"}:
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
        result = run_scheduler_bridge(action, parameters, confirm=confirm)
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
    elif provider in {"google_maps", "maps", "places", "geocoding", "routes"}:
        result = run_google_maps_bridge(action, parameters, confirm=confirm)
    elif provider in {"zoom", "zoom_meetings", "zoom_calendar"}:
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
        result = run_zoom_bridge(action, parameters, confirm=confirm)
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
    elif provider in {"portfolio", "portafolio", "ignis_portfolio", "ignis_financials", "ignis financials", "sr_eli"}:
        send_action = action in {
            "send_whatsapp_report",
            "send_updated_portfolio",
            "send_portfolio",
            "enviar_portafolio",
            "mandar_portafolio",
            "enviame_portafolio_actualizado",
        }
        target = portfolio_default_whatsapp_target(parameters) if send_action else ""
        doctor_control_send = send_action and portfolio_target_is_doctor_control(target)
        read_only_actions = {
            "status",
            "summary",
            "refresh_prices",
            "clear_price_cache",
            "clear_market_cache",
            "client_report",
            "eli_client_report",
            "sr_eli_report",
            "fundamental_report",
            "portfolio_fundamental_report",
            "reporte_fundamental",
            "reporte_fundamental_sr_eli",
            "catalizadores_portafolio",
            "sr_eli_fundamental",
        }
        sensitive_action = action not in read_only_actions and not doctor_control_send
        if sensitive_action:
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
        result = portfolio_cli(action, {**parameters, "confirm": confirm or boolish(parameters.get("confirm"))})
    elif provider in {"paper_broker", "paper_trading", "kim_paper_broker", "tradingview"}:
        sensitive_action = action in PAPER_BROKER_CONFIRMABLE_ACTIONS
        if sensitive_action:
            security = ensure_api_security(provider, action, parameters, confirm=confirm, session_id=session_id, transcript=transcript)
            if not security.get("authorized"):
                result = {
                    "ok": False,
                    "provider": provider,
                    "action": action,
                    "requires_security_phrase": True,
                    "security": security,
                    "message": "Accion paper broker bloqueada. Di la frase de autorizacion o escribe el PIN y vuelve a confirmar.",
                }
                record = record_api_bridge_action(provider or result.get("provider"), action or result.get("action"), parameters, result, session_id, transcript)
                result["action_log"] = record
                return result
        result = paper_broker_cli(action, parameters, confirm=confirm)
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
            raise ValueError("No pude inferir proveedor para esta accion. Usa send_email, create_task, update_task, comment_task, create_page, call_phone, schedule_call, schedule_sms, save_contact, google_maps/find_place o pipedrive.")
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
        raise ValueError("Proveedor no soportado. Usa clickup, notion, pipedrive, gmail, hostinger_mail, zoom, portfolio, paper_broker, twilio, crm o all/status.")
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


def configure_paper_broker_module(module):
    runtime_root = RUNTIME_MEMORY_ROOT / "portfolios"
    bifrost_root = MEMORY_ROOT / "portfolios"
    bifrost_dir = bifrost_root / "ignis_stock_financials" / "clientes" / "manejo_de_portafolios" / "sr_eli_2026" / "paper_trading"
    runtime_dir = runtime_root / "ignis_stock_financials" / "clientes" / "manejo_de_portafolios" / "sr_eli_2026" / "paper_trading"
    if bifrost_dir.exists() and (
        not runtime_dir.exists()
        or max((p.stat().st_mtime for p in bifrost_dir.rglob("*") if p.is_file()), default=0)
        > max((p.stat().st_mtime for p in runtime_dir.rglob("*") if p.is_file()), default=0)
    ):
        copy_tree_files(bifrost_dir, runtime_dir)
    module.ROOT = runtime_root
    return runtime_root, bifrost_root


def sync_paper_broker_runtime_to_bifrost(runtime_root, bifrost_root):
    runtime_dir = runtime_root / "ignis_stock_financials" / "clientes" / "manejo_de_portafolios" / "sr_eli_2026" / "paper_trading"
    bifrost_dir = bifrost_root / "ignis_stock_financials" / "clientes" / "manejo_de_portafolios" / "sr_eli_2026" / "paper_trading"
    sync = copy_tree_files(runtime_dir, bifrost_dir)
    return {
        "runtime_root": str(runtime_root),
        "bifrost_root": str(bifrost_root),
        "paper_runtime_dir": str(runtime_dir),
        "paper_bifrost_dir": str(bifrost_dir),
        "copied_files": len(sync["copied"]),
        "failed_files": sync["failed"][:5],
    }


def import_paper_broker_module():
    spec = importlib.util.spec_from_file_location("kim_paper_broker", PAPER_BROKER_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    runtime_root, bifrost_root = configure_paper_broker_module(module)
    return module, runtime_root, bifrost_root


def tradingview_webhook_config():
    config = read_json_file_any([TRADINGVIEW_WEBHOOK_CONFIG, RUNTIME_TRADINGVIEW_WEBHOOK_CONFIG], {})
    if not isinstance(config, dict):
        config = {}
    token = str(config.get("token") or "").strip()
    if not token:
        token = secrets.token_urlsafe(28)
        config = {
            "token": token,
            "created_at": now_iso(),
            "usage": "TradingView webhook token for Kim Paper Broker alerts. Keep private.",
            "example_payload": {
                "token": "<secret>",
                "symbol": "{{ticker}}",
                "price": "{{close}}",
                "message": "TradingView alert",
            },
        }
        write_json_file_both(TRADINGVIEW_WEBHOOK_CONFIG, RUNTIME_TRADINGVIEW_WEBHOOK_CONFIG, config)
    return config


def masked_secret(value):
    text = str(value or "")
    if len(text) <= 8:
        return "***"
    return text[:4] + "..." + text[-4:]


def validate_tradingview_webhook(payload, handler=None, query_params=None):
    config = tradingview_webhook_config()
    expected = str(config.get("token") or "")
    candidates = []
    if isinstance(payload, dict):
        for key in ("token", "secret", "webhook_token", "kim_token"):
            if payload.get(key):
                candidates.append(str(payload.get(key)))
    if query_params:
        for key in ("token", "secret"):
            values = query_params.get(key) or []
            if values:
                candidates.append(str(values[-1]))
    if handler:
        header_value = handler.headers.get("X-Kim-Webhook-Token") or handler.headers.get("X-TradingView-Webhook-Token")
        if header_value:
            candidates.append(str(header_value))
    return any(hmac.compare_digest(candidate, expected) for candidate in candidates)


def paper_broker_status_with_webhook():
    config = tradingview_webhook_config()
    module, runtime_root, bifrost_root = import_paper_broker_module()
    result = module.cli("status", {})
    result["tradingview_webhook"] = {
        "url": "https://kim.aipeople.app/api/tradingview/webhook",
        "token_masked": masked_secret(config.get("token")),
        "payload_format": {
            "token": "<secret>",
            "symbol": "BINANCE:AVAXUSDT or AVAXUSDT",
            "price": 3.5,
            "message": "optional TradingView alert text",
        },
    }
    result["sync"] = {
        "runtime_root": str(runtime_root),
        "bifrost_root": str(bifrost_root),
        "copied_files": 0,
        "failed_files": [],
        "skipped": "status",
    }
    return result


def paper_broker_price_validations(symbols, providers=None):
    providers = providers or ["binance", "mexc", "bybit"]
    providers = [str(provider or "").strip().lower() for provider in providers if str(provider or "").strip()]
    warnings = []
    if "coinmarketcap" in providers and not load_keychain_secret(COINMARKETCAP_KEYCHAIN_SERVICE, required=False):
        providers = [provider for provider in providers if provider != "coinmarketcap"]
        warnings.append("CoinMarketCap omitido porque falta API key.")
    prices = {}
    errors = []
    for symbol in sorted({portfolio_normalize_symbol(symbol) for symbol in symbols if portfolio_normalize_symbol(symbol)}):
        try:
            validation = validate_market_prices(f"BINANCE:{symbol}", providers=providers)
            if validation.get("approved_for_client_report") and validation.get("reference_price") not in (None, ""):
                prices[symbol] = {
                    "price": validation.get("reference_price"),
                    "approved": True,
                    "validation": validation,
                }
            else:
                errors.append({"symbol": symbol, "reason": "price_not_approved", "validation": validation})
        except Exception as exc:
            errors.append({"symbol": symbol, "error": brief(str(exc), 500)})
    return prices, warnings, errors, providers


def paper_broker_order_key_from_pending(item):
    symbol = portfolio_normalize_symbol((item or {}).get("symbol"))
    raw_id = str((item or {}).get("id") or (item or {}).get("report_order") or (item or {}).get("label") or symbol).strip()
    safe = re.sub(r"[^A-Za-z0-9]+", "-", raw_id).strip("-").upper()[:40] or symbol
    return f"KPB-PORT-{symbol}-{safe}"


def paper_broker_bootstrap_portfolio_pending(module, status_payload):
    existing_keys = {
        str(order.get("source_portfolio_pending_id") or order.get("order_id") or "")
        for bucket in ("pending", "filled", "cancelled", "errors")
        for order in (status_payload.get(bucket) or [])
        if isinstance(order, dict)
    }
    if status_payload.get("pending"):
        return {"ok": True, "created_count": 0, "skipped": "paper_pending_exists"}
    try:
        report = portfolio_cli("client_report", {"save_standard": False, "providers": ["binance", "mexc", "bybit"]})
    except Exception as exc:
        return {"ok": False, "created_count": 0, "error": brief(str(exc), 700)}
    created = []
    for item in report.get("pending_orders") or []:
        if not isinstance(item, dict):
            continue
        symbol = portfolio_normalize_symbol(item.get("symbol"))
        amount_usd = portfolio_float(item.get("invested_usd"))
        limit_price = portfolio_float(item.get("entry_price"))
        if not symbol or amount_usd in (None, 0) or limit_price in (None, 0):
            continue
        order_id = paper_broker_order_key_from_pending(item)
        if order_id in existing_keys:
            continue
        placed = module.cli(
            "place_order",
            {
                "order_id": order_id,
                "symbol": symbol,
                "side": item.get("side") or "BUY",
                "amount_usd": amount_usd,
                "limit_price": limit_price,
                "confirm": True,
                "source": "portfolio_pending_bootstrap",
                "source_portfolio_pending_id": item.get("id") or item.get("report_order") or order_id,
                "client_id": "sr_eli",
                "client_name": "Sr. Eli",
                "notes": f"Mirror de orden pendiente del portafolio Sr. Eli: {item.get('label') or symbol}.",
            },
        )
        order = placed.get("order") or {}
        order["source_portfolio_pending_id"] = item.get("id") or item.get("report_order") or order_id
        order["portfolio_pending_snapshot"] = item
        created.append(order.get("order_id"))
        existing_keys.add(order_id)
    if created:
        module_state = module.read_state()
        module.write_state(module_state)
        append_memory("paper_broker_bootstrap_pending", {"created_count": len(created), "order_ids": created})
    return {
        "ok": True,
        "created_count": len(created),
        "order_ids": created,
        "portfolio_pending_count": len(report.get("pending_orders") or []),
    }


def paper_broker_sync(parameters=None, trigger="polling_watcher"):
    parameters = parameters or {}
    module, runtime_root, bifrost_root = import_paper_broker_module()
    current = module.cli("status", {})
    bootstrap = paper_broker_bootstrap_portfolio_pending(module, current) if boolish(parameters.get("bootstrap_portfolio_pending", True)) else {"skipped": True}
    if bootstrap.get("created_count"):
        current = module.cli("status", {})
    pending = current.get("pending") or []
    symbols = [item.get("symbol") for item in pending if isinstance(item, dict)]
    if parameters.get("symbol"):
        symbols = [parameters.get("symbol")]
    if not symbols:
        return {
            "ok": True,
            "provider": "paper_broker",
            "action": "sync",
            "trigger": trigger,
            "message": "No hay ordenes paper pendientes.",
            "filled_count": 0,
            "status": current,
            "sync": sync_paper_broker_runtime_to_bifrost(runtime_root, bifrost_root),
        }
    prices, warnings, errors, providers_used = paper_broker_price_validations(symbols, providers=parameters.get("providers"))
    evaluation = module.cli(
        "evaluate_orders",
        {
            "prices": prices,
            "symbol": parameters.get("symbol"),
            "trigger": trigger,
            "alert_id": parameters.get("alert_id"),
        },
    )
    portfolio_syncs = []
    for order in evaluation.get("filled_orders") or []:
        try:
            transaction_params = dict(order.get("portfolio_transaction") or {})
            transaction_params.setdefault("portfolio_id", "sr_eli_2026")
            transaction_params.setdefault("source", "kim_paper_broker_fill")
            portfolio_result = portfolio_cli(
                "execute_pending_order",
                {
                    "portfolio_id": transaction_params.get("portfolio_id"),
                    "symbol": transaction_params.get("symbol"),
                    "gross_amount": transaction_params.get("gross_amount"),
                    "price": transaction_params.get("price"),
                    "quantity": transaction_params.get("quantity"),
                    "source": "kim_paper_broker_fill",
                    "notes": transaction_params.get("notes"),
                    "reason": "Orden paper simulada ejecutada por cruce de precio validado.",
                    "summary": f"{transaction_params.get('symbol')} paso de pendiente a activa por Kim Paper Broker.",
                    "confirm": True,
                },
            )
            attach = module.cli(
                "attach_sync_result",
                {
                    "order_id": order.get("order_id"),
                    "portfolio_sync": {
                        "ok": True,
                        "portfolio_action": "execute_pending_order",
                        "transaction_id": (portfolio_result.get("executed_order") or {}).get("id"),
                        "result": portfolio_result,
                    },
                },
            )
            portfolio_syncs.append({"order_id": order.get("order_id"), "ok": True, "attach": attach})
        except Exception as exc:
            try:
                module.cli(
                    "attach_sync_result",
                    {
                        "order_id": order.get("order_id"),
                        "portfolio_sync": {"ok": False, "error": brief(str(exc), 700)},
                    },
                )
            except Exception:
                pass
            portfolio_syncs.append({"order_id": order.get("order_id"), "ok": False, "error": brief(str(exc), 700)})
    sync = sync_paper_broker_runtime_to_bifrost(runtime_root, bifrost_root)
    result = {
        "ok": True,
        "provider": "paper_broker",
        "action": "sync",
        "trigger": trigger,
        "providers_used": providers_used,
        "provider_warnings": warnings,
        "price_errors": errors,
        "bootstrap": bootstrap,
        "evaluation": evaluation,
        "filled_count": len(evaluation.get("filled_orders") or []),
        "portfolio_syncs": portfolio_syncs,
        "sync": sync,
    }
    if result["filled_count"]:
        append_memory(
            "paper_broker_fills",
            {
                "trigger": trigger,
                "filled_count": result["filled_count"],
                "orders": [
                    {"order_id": order.get("order_id"), "symbol": order.get("symbol"), "fill_price": order.get("fill_price")}
                    for order in evaluation.get("filled_orders") or []
                ],
            },
        )
        append_daily_note(f"Kim Paper Broker: {result['filled_count']} orden(es) simuladas ejecutadas por {trigger}.")
    return result


PAPER_BROKER_CONFIRMABLE_ACTIONS = {"place_order", "place", "buy", "sell", "cancel_order", "cancel"}
PAPER_BROKER_WATCHER_STARTED = False


def paper_broker_cli(action, parameters=None, confirm=False, internal=False):
    action = (action or "status").strip().lower()
    parameters = parameters or {}
    if action in {"status", "list", "summary"}:
        return paper_broker_status_with_webhook()
    if action in {"sync", "evaluate", "evaluate_orders", "mark_filled"}:
        return paper_broker_sync(parameters, trigger=parameters.get("trigger") or "manual_sync")
    module, runtime_root, bifrost_root = import_paper_broker_module()
    if action in {"preview", "preview_order"}:
        result = module.cli("preview_order", parameters)
    elif action in PAPER_BROKER_CONFIRMABLE_ACTIONS and not (confirm or internal or boolish(parameters.get("confirm"))):
        preview_action = "cancel_order" if action in {"cancel_order", "cancel"} else "place_order"
        preview = (
            {"order_id": parameters.get("order_id") or parameters.get("id"), "symbol": parameters.get("symbol"), "reason": parameters.get("reason") or parameters.get("notes") or ""}
            if preview_action == "cancel_order"
            else module.cli("preview_order", parameters).get("preview")
        )
        return confirmation_preview(
            "paper_broker",
            preview_action,
            "Confirmar orden paper del Sr. Eli con PIN/frase antes de registrar o cancelar.",
            preview,
            execution_parameters={**parameters, "confirm": True},
        )
    elif action in {"place_order", "place", "buy", "sell"}:
        result = module.cli("place_order", {**parameters, "confirm": confirm or boolish(parameters.get("confirm")) or internal})
    elif action in {"cancel_order", "cancel"}:
        result = module.cli("cancel_order", {**parameters, "confirm": confirm or boolish(parameters.get("confirm")) or internal})
    elif action in {"record_alert", "webhook_alert", "tradingview_alert"}:
        result = module.cli("record_alert", parameters)
    else:
        raise ValueError("Accion paper broker no soportada.")
    mutating = action not in {"preview", "preview_order"}
    result["sync"] = sync_paper_broker_runtime_to_bifrost(runtime_root, bifrost_root) if mutating else {
        "runtime_root": str(runtime_root),
        "bifrost_root": str(bifrost_root),
        "copied_files": 0,
        "failed_files": [],
        "skipped": "preview",
    }
    append_memory("paper_broker_action", {"action": action, "result": brief(json.dumps(result, ensure_ascii=False), 1200)})
    return result


def tradingview_webhook_payload(body, handler, parsed):
    query_params = urllib.parse.parse_qs(parsed.query)
    if not validate_tradingview_webhook(body, handler=handler, query_params=query_params):
        event = {
            "at": now_iso(),
            "provider": "tradingview",
            "path": parsed.path,
            "ip": handler.client_address[0] if handler.client_address else "",
            "body_preview": brief(json.dumps(body, ensure_ascii=False), 500),
        }
        append_memory("tradingview_webhook_rejected", event)
        return {"ok": False, "error": "INVALID_WEBHOOK_TOKEN", "message": "TradingView webhook rechazado por token invalido."}, 403
    alert_body = {k: v for k, v in dict(body or {}).items() if k not in {"token", "secret", "webhook_token", "kim_token"}}
    alert = paper_broker_cli("record_alert", {**alert_body, "raw": alert_body})
    sync = paper_broker_sync(
        {
            "symbol": alert.get("alert", {}).get("symbol") or alert_body.get("symbol"),
            "alert_id": alert.get("alert", {}).get("alert_id"),
        },
        trigger="tradingview_webhook",
    )
    return {"ok": True, "provider": "tradingview", "alert": alert, "sync": sync}, 200


def paper_broker_watcher_loop(interval_seconds=180):
    while True:
        time.sleep(interval_seconds)
        try:
            paper_broker_sync({"trigger": "polling_watcher"}, trigger="polling_watcher")
        except Exception as exc:
            append_memory("paper_broker_watcher_error", {"error": brief(str(exc), 700)})


def start_paper_broker_watcher_once():
    global PAPER_BROKER_WATCHER_STARTED
    if PAPER_BROKER_WATCHER_STARTED:
        return
    PAPER_BROKER_WATCHER_STARTED = True
    run_background_task("kim-paper-broker-watcher", paper_broker_watcher_loop)


PORTFOLIO_SALE_ACTIONS = {"sell_position", "close_position", "record_sale", "venta_final", "cerrar_posicion"}
PORTFOLIO_EXECUTION_ACTIONS = {"execute_pending_order", "mark_order_executed", "confirm_pending_order"}
PORTFOLIO_MANUAL_SENSITIVE_ACTIONS = {
    "manual_delete_order",
    "delete_manual_order",
    "remove_manual_order",
    "remove_order",
    "remove_portfolio_order",
    "agglomerate_manual_orders",
    "aggregate_order",
    "agglomerate_order",
    "agglomerate_orders",
    "aggregate_manual_orders",
    "consolidate_manual_orders",
    "consolidate_orders",
    "split_consolidated_order",
    "split_manual_order",
    "split_order",
    "separate_order",
    "separate_orders",
}
PORTFOLIO_CONFIRMABLE_ACTIONS = PORTFOLIO_SALE_ACTIONS | PORTFOLIO_EXECUTION_ACTIONS | PORTFOLIO_MANUAL_SENSITIVE_ACTIONS
PORTFOLIO_CLOSED_STATES = {"closed", "sold", "void", "cancelled", "canceled", "inactive", "cerrada", "vendida", "anulada"}


def portfolio_float(value, default=None):
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def portfolio_normalize_symbol(symbol):
    token = str(symbol or "").upper().strip().replace(" ", "")
    if token and ":" in token:
        token = token.split(":", 1)[1]
    if token and token.isalpha() and not token.endswith("USDT"):
        token = f"{token}USDT"
    return token


def portfolio_sale_calculation(parameters, override_config=None):
    parameters = parameters or {}
    override_config = override_config or {}
    symbol = portfolio_normalize_symbol(first_value(parameters, "symbol", "ticker", "asset", "moneda"))
    if not symbol:
        raise ValueError("Falta symbol para registrar la venta.")
    sell_price = portfolio_float(first_value(parameters, "sell_price", "sale_price", "exit_price", "price", "precio_venta"))
    if sell_price in (None, 0):
        raise ValueError("Falta sell_price/price para registrar la venta.")
    entry_price = portfolio_float(first_value(parameters, "entry_price", "buy_price", "precio_compra", "average_cost"))
    invested_usd = portfolio_float(first_value(parameters, "invested_usd", "original_amount_usd", "gross_cost_usd", "amount", "usd_amount", "gross_amount"))
    quantity = portfolio_float(first_value(parameters, "quantity", "units", "cantidad"))
    if quantity is None and invested_usd is not None and entry_price not in (None, 0):
        quantity = invested_usd / entry_price
    if invested_usd is None and quantity is not None and entry_price is not None:
        invested_usd = quantity * entry_price
    if entry_price is None and invested_usd is not None and quantity not in (None, 0):
        entry_price = invested_usd / quantity
    if quantity in (None, 0) or invested_usd in (None, 0):
        raise ValueError("Faltan quantity o invested_usd/entry_price para calcular la venta.")
    accounting = portfolio_accounting_config(override_config)
    fee_rate = portfolio_float(first_value(parameters, "fee_rate", "operation_fee_rate"), accounting.get("operation_fee_rate") or 0.012)
    fee_base_usd = portfolio_float(first_value(parameters, "fee_base_usd", "fee_base", "commission_base_usd"), invested_usd)
    gross_sale_usd = quantity * sell_price
    gross_pnl_usd = gross_sale_usd - invested_usd
    fee_usd = fee_base_usd * fee_rate
    net_pnl_usd = gross_pnl_usd - fee_usd
    return {
        "symbol": symbol,
        "entry_price": round_price(entry_price),
        "sell_price": round_price(sell_price),
        "quantity": round_opt(quantity, 8),
        "invested_usd": round_opt(invested_usd, 2),
        "gross_sale_usd": round_opt(gross_sale_usd, 2),
        "gross_pnl_usd": round_opt(gross_pnl_usd, 2),
        "fee_rate": fee_rate,
        "fee_rate_pct": round_opt(fee_rate * 100, 4),
        "fee_base_usd": round_opt(fee_base_usd, 2),
        "fee_usd": round_opt(fee_usd, 2),
        "net_pnl_usd": round_opt(net_pnl_usd, 2),
        "gross_pnl_pct": round_opt((gross_pnl_usd / invested_usd * 100) if invested_usd else None, 2),
        "net_pnl_pct": round_opt((net_pnl_usd / invested_usd * 100) if invested_usd else None, 2),
        "currency": str(first_value(parameters, "currency", default="USD") or "USD").upper(),
    }


def portfolio_sale_preview(parameters, override_config=None):
    calc = portfolio_sale_calculation(parameters, override_config)
    return {
        **calc,
        "summary": (
            f"Venta {calc['symbol']}: entrada {format_price(calc['entry_price'])}, "
            f"salida {format_price(calc['sell_price'])}, venta bruta {format_usd_amount(calc['gross_sale_usd'])} USD, "
            f"P/L bruto {signed_usd_text(calc['gross_pnl_usd'])}, fee {format_usd_amount(calc['fee_usd'])} USD "
            f"({format_usd_amount(calc['fee_rate_pct'])}% sobre {format_usd_amount(calc['fee_base_usd'])} USD), "
            f"P/L neto {signed_usd_text(calc['net_pnl_usd'])}."
        ),
    }


def portfolio_order_identifier(parameters, entry=None):
    raw = first_value(parameters or {}, "order", "report_order", "order_id", "identifier", "id_orden", "orden", default="")
    token = str(raw or "").strip().upper()
    if not token and entry:
        token = str(entry.get("identifier") or entry.get("order") or "").strip().upper()
    if token.startswith("A"):
        token = token[1:]
    try:
        return int(float(token))
    except (TypeError, ValueError):
        return None


def portfolio_entry_matches(entry, parameters, calc=None, preferred_states=None):
    entry = entry or {}
    parameters = parameters or {}
    calc = calc or {}
    symbol = calc.get("symbol") or portfolio_normalize_symbol(first_value(parameters, "symbol", "ticker", "asset", "moneda"))
    if symbol and portfolio_normalize_symbol(entry.get("symbol")) != symbol:
        return False
    if preferred_states:
        state = str(entry.get("state") or "").strip().lower()
        if state and state not in preferred_states:
            return False
    wanted_order = portfolio_order_identifier(parameters)
    entry_order = portfolio_order_identifier({}, entry)
    if wanted_order is not None:
        return entry_order == wanted_order
    wanted_entry = portfolio_float(calc.get("entry_price") or first_value(parameters, "entry_price", "buy_price", "precio_compra", "average_cost"))
    entry_price = portfolio_float(entry.get("entry_price"))
    if wanted_entry is not None and entry_price is not None and abs(entry_price - wanted_entry) > max(1e-12, abs(wanted_entry) * 1e-8):
        return False
    wanted_amount = portfolio_float(calc.get("invested_usd") or first_value(parameters, "invested_usd", "original_amount_usd", "gross_cost_usd", "amount", "usd_amount", "gross_amount"))
    entry_amount = portfolio_float(entry.get("invested_usd"))
    if wanted_amount is not None and entry_amount is not None and abs(entry_amount - wanted_amount) > 0.01:
        return False
    return bool(symbol)


def portfolio_closed_identifier(entry, parameters):
    prefix = "A"
    order = portfolio_order_identifier(parameters, entry)
    if order is not None:
        return f"{prefix}{order}"
    return str((entry or {}).get("identifier") or (parameters or {}).get("identifier") or "").strip()


def portfolio_closed_position_record(entry, parameters, calc):
    entry = entry or {}
    identifier = portfolio_closed_identifier(entry, parameters)
    label = str(first_value(parameters or {}, "label", "name", default="") or entry.get("label") or calc.get("symbol") or "").strip()
    source = str(first_value(parameters or {}, "source", default="kim_live_sale") or "kim_live_sale").strip()
    notes = str(first_value(parameters or {}, "notes", "summary", "rationale", default="") or "").strip()
    if notes:
        notes += " "
    notes += (
        f"Venta final confirmada: entrada {format_price(calc.get('entry_price'))}, "
        f"salida {format_price(calc.get('sell_price'))}; venta bruta {format_usd_amount(calc.get('gross_sale_usd'))} USD; "
        f"P/L bruto {signed_usd_text(calc.get('gross_pnl_usd'))}; fee {format_usd_amount(calc.get('fee_usd'))} USD; "
        f"P/L neto {signed_usd_text(calc.get('net_pnl_usd'))}."
    )
    record = {
        "symbol": calc.get("symbol"),
        "identifier": identifier,
        "label": label,
        "state": "sold",
        "invested_usd": calc.get("invested_usd"),
        "entry_price": calc.get("entry_price"),
        "quantity": calc.get("quantity"),
        "sell_price": calc.get("sell_price"),
        "gross_sale_usd": calc.get("gross_sale_usd"),
        "gross_pnl_usd": calc.get("gross_pnl_usd"),
        "fee_rate": calc.get("fee_rate"),
        "fee_base_usd": calc.get("fee_base_usd"),
        "fee_usd": calc.get("fee_usd"),
        "net_pnl_usd": calc.get("net_pnl_usd"),
        "source": source,
        "sold_at": first_value(parameters or {}, "sold_at", "occurred_at", "decided_at", default=now_iso()),
        "notes": notes,
    }
    order = portfolio_order_identifier(parameters, entry)
    if order is not None:
        record["order"] = order
    if entry.get("credit") is not None:
        record["credit"] = boolish(entry.get("credit"))
    return record


def portfolio_closed_duplicate(existing, record):
    if portfolio_normalize_symbol(existing.get("symbol")) != portfolio_normalize_symbol(record.get("symbol")):
        return False
    if str(existing.get("identifier") or "").strip() and str(existing.get("identifier") or "").strip() == str(record.get("identifier") or "").strip():
        return True
    return (
        portfolio_float(existing.get("entry_price")) == portfolio_float(record.get("entry_price"))
        and portfolio_float(existing.get("sell_price")) == portfolio_float(record.get("sell_price"))
        and portfolio_float(existing.get("invested_usd")) == portfolio_float(record.get("invested_usd"))
    )


def portfolio_write_override_config(payload):
    write_json_file_both(PORTFOLIO_REPORT_OVERRIDES, RUNTIME_PORTFOLIO_REPORT_OVERRIDES, payload)


def portfolio_manual_entry_key(entry):
    entry = entry or {}
    raw_id = str(entry.get("id") or "").strip()
    if raw_id:
        return raw_id
    order = entry.get("order")
    symbol = portfolio_normalize_symbol(entry.get("symbol"))
    if order not in (None, "") and symbol:
        return f"order-{order}-{symbol.lower()}"
    return symbol.lower() or "manual-entry"


def portfolio_manual_entry_matches(entry, parameters):
    entry = entry or {}
    parameters = parameters or {}
    requested_id = str(first_value(parameters, "id", "entry_id", "manual_id", default="") or "").strip()
    if requested_id and requested_id == portfolio_manual_entry_key(entry):
        return True
    requested_order = first_value(parameters, "order", "order_id", "canonical_order", default=None)
    requested_symbol = portfolio_normalize_symbol(first_value(parameters, "symbol", "ticker", "asset", default=""))
    requested_state = str(first_value(parameters, "state", "status", default="") or "").strip().lower()
    order_matches = requested_order not in (None, "") and str(entry.get("order")) == str(requested_order)
    symbol_matches = requested_symbol and portfolio_normalize_symbol(entry.get("symbol")) == requested_symbol
    state_matches = not requested_state or str(entry.get("state") or "").strip().lower() == requested_state
    if order_matches and (not requested_symbol or symbol_matches) and state_matches:
        return True
    if symbol_matches and state_matches and requested_id:
        return True
    return False


def portfolio_values_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        rows = []
        for item in value:
            rows.extend(portfolio_values_list(item))
        return rows
    text = str(value or "").strip()
    if not text:
        return []
    return [part for part in re.split(r"[,;\s]+", text) if part]


def portfolio_client_id_from_number(value):
    if value in (None, ""):
        return ""
    try:
        return f"A{int(float(value))}"
    except (TypeError, ValueError):
        return ""


def portfolio_normalize_client_id(value):
    text = str(value or "").strip().upper()
    if not text:
        return ""
    match = re.search(r"A?\s*([0-9]+)", text)
    if not match:
        return ""
    return f"A{int(match.group(1))}"


def portfolio_parse_client_ids(value):
    ids = set()
    values = portfolio_values_list(value)
    for raw in values:
        text = str(raw or "").strip().upper()
        if not text:
            continue
        range_match = re.match(r"A?\s*([0-9]+)\s*[-:]\s*A?\s*([0-9]+)$", text)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            if start > end:
                start, end = end, start
            for number in range(start, end + 1):
                ids.add(f"A{number}")
            continue
        normalized = portfolio_normalize_client_id(text)
        if normalized:
            ids.add(normalized)
    return ids


def portfolio_cast_manual_value(field, value):
    numeric_fields = {"order", "invested_usd", "entry_price", "quantity", "credit_usd", "current_price"}
    if field == "order":
        return int(float(value)) if value not in (None, "") else None
    if field in numeric_fields:
        return portfolio_float(value)
    if field == "state":
        state = str(value or "").strip().lower()
        if state in {"executed", "filled", "market", "mercado", "en_mercado"}:
            return "active"
        if state in {"open", "draft", "pending", "pendiente"}:
            return "pending"
        if state in PORTFOLIO_CLOSED_STATES:
            return state
        return state or "active"
    if field == "symbol":
        return portfolio_normalize_symbol(value)
    if field in {"credit"}:
        return boolish(value)
    return str(value or "").strip()


def portfolio_normalize_manual_entry(entry):
    entry = dict(entry or {})
    if entry.get("symbol"):
        entry["symbol"] = portfolio_normalize_symbol(entry.get("symbol"))
    entry["state"] = portfolio_cast_manual_value("state", entry.get("state") or "active")
    for field in ["order", "invested_usd", "entry_price", "quantity", "credit_usd", "current_price"]:
        if field in entry and entry.get(field) not in (None, ""):
            entry[field] = portfolio_cast_manual_value(field, entry.get(field))
    invested = portfolio_float(entry.get("invested_usd"))
    price = portfolio_float(entry.get("entry_price"))
    quantity = portfolio_float(entry.get("quantity"))
    if (quantity in (None, 0)) and invested not in (None, 0) and price not in (None, 0):
        entry["quantity"] = invested / price
    if not str(entry.get("id") or "").strip():
        entry["id"] = portfolio_manual_entry_key(entry)
    return entry


def portfolio_enforce_manual_order_states(config):
    config = dict(config or {})
    entries = config.get("manual_entries") if isinstance(config.get("manual_entries"), list) else []
    allow_active_above_base = boolish(config.get("allow_active_manual_entries_above_base_count", True))
    changed = []
    normalized = []
    for raw in entries:
        if not isinstance(raw, dict):
            continue
        entry = portfolio_normalize_manual_entry(raw)
        order = entry.get("order")
        desired = None
        if order not in (None, ""):
            desired = "active" if int(order) <= 12 else "pending"
            if allow_active_above_base and int(order) > 12 and entry.get("state") == "active":
                desired = None
        if desired and entry.get("state") != desired:
            changed.append({"id": portfolio_manual_entry_key(entry), "order": order, "from": entry.get("state"), "to": desired})
            entry["state"] = desired
        normalized.append(entry)
    config["manual_entries"] = normalized
    return config, changed


def portfolio_manual_orders(summary, parameters=None):
    parameters = parameters or {}
    config = portfolio_report_override_config(summary)
    if not config:
        return {"ok": False, "error": "override_config_missing", "manual_entries": []}
    if boolish(first_value(parameters, "normalize_states", "enforce_states", default=False)):
        config, changed = portfolio_enforce_manual_order_states(config)
        if changed:
            config["updated_at"] = now_iso()
            config["standard_version"] = "KIM-0105"
            portfolio_write_override_config(config)
    else:
        changed = []
    entries = [portfolio_normalize_manual_entry(entry) for entry in (config.get("manual_entries") or []) if isinstance(entry, dict)]
    result = {
        "ok": True,
        "provider": "portfolio",
        "action": "manual_orders",
        "portfolio_id": config.get("portfolio_id"),
        "standard_version": config.get("standard_version"),
        "manual_entries": entries,
        "active_count": sum(1 for item in entries if str(item.get("state")) == "active"),
        "pending_count": sum(1 for item in entries if str(item.get("state")) == "pending"),
        "state_changes": changed,
    }
    if boolish(first_value(parameters, "include_report", "with_report", default=False)):
        result["report"] = portfolio_client_report(summary, parameters)
    return result


def portfolio_update_manual_order(summary, parameters=None):
    parameters = parameters or {}
    config = portfolio_report_override_config(summary)
    if not config:
        return {"ok": False, "error": "override_config_missing"}
    entries = config.get("manual_entries") if isinstance(config.get("manual_entries"), list) else []
    allowed = {
        "id", "symbol", "state", "order", "label", "invested_usd", "entry_price",
        "quantity", "credit_usd", "side", "notes", "source", "current_price",
        "current_price_status", "current_price_source",
    }
    update_payload = parameters.get("updates") if isinstance(parameters.get("updates"), dict) else parameters
    matched_index = None
    for index, entry in enumerate(entries):
        if portfolio_manual_entry_matches(entry, parameters):
            matched_index = index
            break
    create_if_missing = boolish(first_value(parameters, "create_if_missing", "create", default=False))
    if matched_index is None and not create_if_missing:
        return {"ok": False, "error": "manual_entry_not_found", "parameters": parameters}
    old_entry = dict(entries[matched_index]) if matched_index is not None else {}
    entry = dict(old_entry)
    for field, value in update_payload.items():
        if field not in allowed:
            continue
        if value is None:
            continue
        entry[field] = portfolio_cast_manual_value(field, value)
    entry = portfolio_normalize_manual_entry(entry)
    entry["updated_at"] = now_iso()
    if matched_index is None:
        entries.append(entry)
    else:
        entries[matched_index] = entry
    config["manual_entries"] = entries
    config["updated_at"] = now_iso()
    config["standard_version"] = "KIM-0105"
    rules = config.get("doctor_rules") if isinstance(config.get("doctor_rules"), list) else []
    rule = "KIM-0105: el panel Paper Broker permite editar manualmente ordenes del Portafolio A; A1-A12 son mercado/ejecutadas y A13+ son pendientes salvo instruccion explicita."
    if rule not in rules:
        rules.append(rule)
        config["doctor_rules"] = rules
    portfolio_write_override_config(config)
    return {
        "ok": True,
        "provider": "portfolio",
        "action": "update_manual_order",
        "created": matched_index is None,
        "old_entry": old_entry,
        "entry": entry,
        "manual_orders": portfolio_manual_orders(summary, {"include_report": False}),
    }


def portfolio_delete_manual_order(summary, parameters=None):
    parameters = parameters or {}
    config = portfolio_report_override_config(summary)
    if not config:
        return {"ok": False, "error": "override_config_missing"}
    entries = config.get("manual_entries") if isinstance(config.get("manual_entries"), list) else []
    kept = []
    removed = []
    for entry in entries:
        if isinstance(entry, dict) and portfolio_manual_entry_matches(entry, parameters):
            removed.append(entry)
            continue
        kept.append(entry)
    if not removed:
        return {"ok": False, "error": "manual_entry_not_found", "parameters": parameters}
    config["manual_entries"] = kept
    removed_orders = config.get("removed_orders") if isinstance(config.get("removed_orders"), list) else []
    for entry in removed:
        removed_orders.append(
            {
                **dict(entry),
                "removed_at": now_iso(),
                "removed_by": str(first_value(parameters, "removed_by", "actor", default="kim_live_panel") or "kim_live_panel"),
                "remove_reason": str(first_value(parameters, "reason", "notes", default="manual_remove") or "manual_remove"),
            }
        )
    config["removed_orders"] = removed_orders
    config["updated_at"] = now_iso()
    config["standard_version"] = "KIM-0112"
    portfolio_write_override_config(config)
    append_memory("portfolio_manual_order_deleted", {"removed": removed, "parameters": parameters})
    return {
        "ok": True,
        "provider": "portfolio",
        "action": "delete_manual_order",
        "removed_count": len(removed),
        "removed": removed,
        "manual_orders": portfolio_manual_orders(summary, {"include_report": False}),
    }


def portfolio_selected_manual_entries(config, parameters=None):
    parameters = parameters or {}
    entries = config.get("manual_entries") if isinstance(config.get("manual_entries"), list) else []
    requested_ids = portfolio_parse_client_ids(first_value(parameters, "ids", "client_ids", "selected_ids", "orders", "members", default=[]))
    requested_symbols = {
        portfolio_normalize_symbol(symbol)
        for symbol in portfolio_values_list(first_value(parameters, "symbols", "symbol", "ticker", "asset", default=[]))
    }
    requested_symbols.discard("")
    requested_states = {
        str(state or "").strip().lower()
        for state in portfolio_values_list(first_value(parameters, "states", "state", "status", default=[]))
    }
    requested_states.discard("")
    matched = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        normalized = portfolio_normalize_manual_entry(entry)
        entry_ids = {
            portfolio_client_id_from_number(normalized.get("order")),
            portfolio_normalize_client_id(normalized.get("identifier")),
            portfolio_normalize_client_id(normalized.get("id")),
        }
        entry_ids.discard("")
        symbol = portfolio_normalize_symbol(normalized.get("symbol"))
        state = str(normalized.get("state") or "").strip().lower()
        id_match = bool(requested_ids and requested_ids.intersection(entry_ids))
        symbol_match = bool(requested_symbols and symbol in requested_symbols)
        state_match = not requested_states or state in requested_states
        if (id_match or symbol_match or (not requested_ids and not requested_symbols)) and state_match:
            matched.append(normalized)
    return matched


def portfolio_consolidation_preview_for_entries(entries, config):
    fee_rate = portfolio_manual_aggregation_fee_rate(config)
    total_amount = 0.0
    total_quantity = 0.0
    total_credit = 0.0
    member_rows = []
    symbols = []
    for raw in entries:
        entry = portfolio_normalize_manual_entry(raw)
        symbol = portfolio_normalize_symbol(entry.get("symbol"))
        if symbol and symbol not in symbols:
            symbols.append(symbol)
        amount = portfolio_float(entry.get("invested_usd"), 0.0) or 0.0
        price = portfolio_float(entry.get("entry_price"))
        quantity = portfolio_float(entry.get("quantity"))
        if quantity in (None, 0) and amount and price not in (None, 0):
            quantity = amount / price
        quantity = portfolio_float(quantity, 0.0) or 0.0
        total_amount += amount
        total_quantity += quantity
        total_credit += portfolio_float(entry.get("credit_usd"), 0.0) or 0.0
        member_rows.append(
            {
                "id": portfolio_manual_entry_key(entry),
                "client_id": portfolio_client_id_from_number(entry.get("order")),
                "symbol": symbol,
                "state": entry.get("state"),
                "amount_usd": round_opt(amount, 2),
                "entry_price": round_price(price),
                "quantity": round_opt(quantity, 8),
            }
        )
    raw_average = (total_amount / total_quantity) if total_quantity else None
    adjusted_average = raw_average * (1 + fee_rate) if raw_average is not None else None
    return {
        "symbols": symbols,
        "member_count": len(member_rows),
        "members": member_rows,
        "total_amount_usd": round_opt(total_amount, 2),
        "total_quantity": round_opt(total_quantity, 8),
        "total_credit_usd": round_opt(total_credit, 2),
        "raw_weighted_average_price": round_price(raw_average),
        "fee_rate": fee_rate,
        "fee_rate_pct": round_opt(fee_rate * 100, 4),
        "fee_adjusted_average_price": round_price(adjusted_average),
        "summary": (
            f"Aglomerar {len(member_rows)} tramo(s): total {format_usd_amount(total_amount)} USD, "
            f"promedio base {format_price(raw_average)}, fee {format_usd_amount(fee_rate * 100)}%, "
            f"precio visible {format_price(adjusted_average)}."
        ),
    }


def portfolio_manual_aggregation_suggestions(summary, parameters=None):
    parameters = parameters or {}
    config = portfolio_report_override_config(summary)
    if not config:
        return {"ok": False, "error": "override_config_missing", "suggestions": []}
    entries = [
        portfolio_normalize_manual_entry(entry)
        for entry in (config.get("manual_entries") or [])
        if isinstance(entry, dict) and str((entry or {}).get("state") or "").strip().lower() not in PORTFOLIO_CLOSED_STATES
    ]
    grouped = {}
    for entry in entries:
        symbol = portfolio_normalize_symbol(entry.get("symbol"))
        if not symbol:
            continue
        grouped.setdefault(symbol, []).append(entry)
    suggestions = []
    for symbol, rows in sorted(grouped.items()):
        if len(rows) < 2:
            continue
        rows = sorted(rows, key=lambda item: portfolio_float(item.get("order"), 9999) or 9999)
        states = sorted({str(item.get("state") or "").strip().lower() for item in rows if str(item.get("state") or "").strip()})
        suggestions.append(
            {
                "symbol": symbol,
                "label": portfolio_symbol_label(symbol),
                "states": states,
                "needs_confirmation": True,
                "recommended_action": "agglomerate_manual_orders",
                "preview": portfolio_consolidation_preview_for_entries(rows, config),
            }
        )
    return {
        "ok": True,
        "provider": "portfolio",
        "action": "aggregation_suggestions",
        "suggestions": suggestions,
        "count": len(suggestions),
    }


def portfolio_agglomerate_manual_orders(summary, parameters=None):
    parameters = parameters or {}
    config = portfolio_report_override_config(summary)
    if not config:
        return {"ok": False, "error": "override_config_missing"}
    selected = portfolio_selected_manual_entries(config, parameters)
    if len(selected) < 2:
        return {"ok": False, "error": "not_enough_members", "message": "Se requieren al menos dos tramos para aglomerar.", "selected": selected}
    symbols = {portfolio_normalize_symbol(item.get("symbol")) for item in selected}
    symbols.discard("")
    if len(symbols) != 1 and not boolish(first_value(parameters, "allow_mixed_symbols", default=False)):
        return {"ok": False, "error": "mixed_symbols", "symbols": sorted(symbols), "message": "No se pueden aglomerar monedas distintas sin permiso explicito."}
    preview = portfolio_consolidation_preview_for_entries(selected, config)
    canonical_order = portfolio_float(first_value(parameters, "canonical_order", "order", "base_order", default=None))
    selected_sorted = sorted(selected, key=lambda item: portfolio_float(item.get("order"), 9999) or 9999)
    canonical = dict(selected_sorted[0])
    if canonical_order is not None:
        for item in selected_sorted:
            if portfolio_float(item.get("order")) == canonical_order:
                canonical = dict(item)
                break
    selected_keys = {portfolio_manual_entry_key(item) for item in selected_sorted}
    symbol = next(iter(symbols)) if symbols else portfolio_normalize_symbol(canonical.get("symbol"))
    canonical["symbol"] = symbol
    canonical["label"] = str(first_value(parameters, "label", default=canonical.get("label") or portfolio_symbol_label(symbol)) or portfolio_symbol_label(symbol))
    canonical["state"] = str(first_value(parameters, "state", "status", default="active") or "active").strip().lower()
    canonical["invested_usd"] = preview.get("total_amount_usd")
    canonical["entry_price"] = preview.get("fee_adjusted_average_price")
    canonical["quantity"] = preview.get("total_quantity")
    canonical["credit_usd"] = preview.get("total_credit_usd")
    canonical["raw_weighted_average_price"] = preview.get("raw_weighted_average_price")
    canonical["fee_adjusted_average_price"] = preview.get("fee_adjusted_average_price")
    canonical["consumed_orders"] = [item.get("client_id") for item in preview.get("members") or [] if item.get("client_id")]
    canonical["split_members"] = [dict(item) for item in selected_sorted]
    canonical["source"] = str(first_value(parameters, "source", default="kim_live_agglomeration") or "kim_live_agglomeration")
    note = str(canonical.get("notes") or "").strip()
    agg_note = (
        f"Aglomeracion confirmada {now_iso()}: {preview.get('summary')} "
        f"Tramos consumidos: {', '.join(canonical.get('consumed_orders') or [])}."
    )
    canonical["notes"] = (note + " " + agg_note).strip()
    canonical["updated_at"] = now_iso()
    manual_entries = config.get("manual_entries") if isinstance(config.get("manual_entries"), list) else []
    kept = [
        entry
        for entry in manual_entries
        if not (isinstance(entry, dict) and portfolio_manual_entry_key(portfolio_normalize_manual_entry(entry)) in selected_keys)
    ]
    kept.append(portfolio_normalize_manual_entry(canonical))
    consumed_orders = config.get("consumed_orders") if isinstance(config.get("consumed_orders"), list) else []
    consumed_orders.append({"at": now_iso(), "action": "agglomerate_manual_orders", "canonical": canonical, "members": selected_sorted, "preview": preview})
    config["manual_entries"] = kept
    config["consumed_orders"] = consumed_orders
    config["updated_at"] = now_iso()
    config["standard_version"] = "KIM-0112"
    portfolio_write_override_config(config)
    return {
        "ok": True,
        "provider": "portfolio",
        "action": "agglomerate_manual_orders",
        "canonical_entry": canonical,
        "preview": preview,
        "manual_orders": portfolio_manual_orders(summary, {"include_report": False}),
    }


def portfolio_split_manual_order(summary, parameters=None):
    parameters = parameters or {}
    config = portfolio_report_override_config(summary)
    if not config:
        return {"ok": False, "error": "override_config_missing"}
    entries = config.get("manual_entries") if isinstance(config.get("manual_entries"), list) else []
    matched_index = None
    matched = None
    for index, entry in enumerate(entries):
        if isinstance(entry, dict) and portfolio_manual_entry_matches(entry, parameters):
            matched_index = index
            matched = portfolio_normalize_manual_entry(entry)
            break
    if matched is None:
        return {"ok": False, "error": "manual_entry_not_found", "parameters": parameters}
    split_members = matched.get("split_members") if isinstance(matched.get("split_members"), list) else []
    if not split_members:
        return {"ok": False, "error": "split_members_missing", "message": "Esta posicion no tiene tramos tecnicos guardados para separar."}
    restored = [portfolio_normalize_manual_entry(member) for member in split_members if isinstance(member, dict)]
    new_entries = [entry for index, entry in enumerate(entries) if index != matched_index]
    new_entries.extend(restored)
    config["manual_entries"] = new_entries
    config["updated_at"] = now_iso()
    config["standard_version"] = "KIM-0112"
    change_log = config.get("change_log") if isinstance(config.get("change_log"), list) else []
    change_log.append(
        {
            "at": now_iso(),
            "action": "split_manual_order",
            "removed_consolidated": matched,
            "restored_count": len(restored),
        }
    )
    config["change_log"] = change_log
    portfolio_write_override_config(config)
    return {
        "ok": True,
        "provider": "portfolio",
        "action": "split_manual_order",
        "restored_count": len(restored),
        "restored": restored,
        "manual_orders": portfolio_manual_orders(summary, {"include_report": False}),
    }


def portfolio_sync_manual_sale_to_overrides(parameters, calc):
    config = portfolio_report_override_config({"portfolio_id": (parameters or {}).get("portfolio_id") or "sr_eli_2026"})
    if not config:
        return {"updated": False, "reason": "override_config_missing"}
    manual_entries = config.get("manual_entries") if isinstance(config.get("manual_entries"), list) else []
    kept = []
    matched = []
    for entry in manual_entries:
        if portfolio_entry_matches(entry, parameters, calc, preferred_states={"pending", "active"}):
            matched.append(entry)
            continue
        kept.append(entry)
    if not matched:
        return {"updated": False, "reason": "manual_entry_not_found"}
    closed_positions = config.get("closed_positions") if isinstance(config.get("closed_positions"), list) else []
    added = []
    for entry in matched:
        record = portfolio_closed_position_record(entry, parameters, calc)
        if not any(portfolio_closed_duplicate(existing, record) for existing in closed_positions):
            closed_positions.append(record)
            added.append(record)
    config["manual_entries"] = kept
    config["closed_positions"] = closed_positions
    config["updated_at"] = now_iso()
    config["standard_version"] = "KIM-0099"
    rules = config.get("doctor_rules") if isinstance(config.get("doctor_rules"), list) else []
    rule = "KIM-0099: cuando una orden manual se vende, quitarla de manual_entries activos/pendientes, moverla a closed_positions y sumar su P/L neto realizado."
    if rule not in rules:
        rules.append(rule)
        config["doctor_rules"] = rules
    portfolio_write_override_config(config)
    return {
        "updated": True,
        "matched_count": len(matched),
        "closed_added_count": len(added),
        "closed_positions": added,
    }


def portfolio_sync_manual_execution_to_overrides(parameters):
    config = portfolio_report_override_config({"portfolio_id": (parameters or {}).get("portfolio_id") or "sr_eli_2026"})
    if not config:
        return {"updated": False, "reason": "override_config_missing"}
    manual_entries = config.get("manual_entries") if isinstance(config.get("manual_entries"), list) else []
    changed = []
    for entry in manual_entries:
        if not portfolio_entry_matches(entry, parameters, preferred_states={"pending"}):
            continue
        entry["state"] = "active"
        entry["source"] = str(first_value(parameters, "source", default="kim_live_execute_pending") or "kim_live_execute_pending")
        entry["executed_at"] = first_value(parameters, "executed_at", "occurred_at", "decided_at", default=now_iso())
        note = str(entry.get("notes") or "").strip()
        execution_note = "Orden pendiente confirmada como ejecutada por el doctor; ya no debe aparecer en pendientes."
        if execution_note not in note:
            entry["notes"] = (note + " " + execution_note).strip()
        changed.append(entry)
    if not changed:
        return {"updated": False, "reason": "manual_entry_not_found"}
    config["manual_entries"] = manual_entries
    config["updated_at"] = now_iso()
    config["standard_version"] = "KIM-0099"
    portfolio_write_override_config(config)
    return {"updated": True, "matched_count": len(changed), "executed_entries": changed}


def portfolio_execute_sale(module, ns, parameters, override_config):
    calc = portfolio_sale_calculation(parameters, override_config)
    notes = str(first_value(parameters, "notes", "summary", "rationale", default="") or "").strip()
    if notes:
        notes += "\n"
    notes += (
        f"Venta final {calc['symbol']}: entrada {format_price(calc['entry_price'])}, salida {format_price(calc['sell_price'])}; "
        f"P/L bruto {signed_usd_text(calc['gross_pnl_usd'])}; fee operativo {format_usd_amount(calc['fee_usd'])} USD; "
        f"P/L neto {signed_usd_text(calc['net_pnl_usd'])}."
    )
    cancelled_pending = None
    if boolish(first_value(parameters, "cancel_pending", "void_pending", default=True)):
        try:
            cancelled_pending = module.cancel_transaction(
                ns(
                    portfolio_id=parameters.get("portfolio_id") or module.DEFAULT_PORTFOLIO_ID,
                    transaction_id=parameters.get("pending_transaction_id") or parameters.get("draft_transaction_id"),
                    symbol=calc["symbol"],
                    status="draft",
                    reason=f"Venta final confirmada; {calc['symbol']} deja de estar pendiente.",
                )
            ).get("record")
        except Exception as exc:
            cancelled_pending = {"skipped": True, "reason": brief(str(exc), 260)}
    tx = module.add_transaction(
        ns(
            portfolio_id=parameters.get("portfolio_id") or module.DEFAULT_PORTFOLIO_ID,
            occurred_at=parameters.get("occurred_at"),
            symbol=calc["symbol"],
            side="SELL",
            quantity=calc["quantity"],
            price=calc["sell_price"],
            gross_amount=calc["gross_sale_usd"],
            fees=calc["fee_usd"],
            currency=calc["currency"],
            status="final",
            source=parameters.get("source") or "kim_live_sale",
            notes=notes,
        )
    )
    change = module.record_final_change(
        ns(
            portfolio_id=parameters.get("portfolio_id") or module.DEFAULT_PORTFOLIO_ID,
            decided_at=parameters.get("decided_at"),
            change_type="sell_position",
            summary=notes,
            rationale=parameters.get("rationale") or "Venta final confirmada por el doctor.",
            related_consultation_id=parameters.get("related_consultation_id"),
            executed=True,
            execution_ref=tx["record"]["id"],
        )
    )
    override_sync = portfolio_sync_manual_sale_to_overrides(parameters, calc)
    return {
        "ok": True,
        "action": "sell_position",
        "calculation": calc,
        "transaction": tx["record"],
        "cancelled_pending": cancelled_pending,
        "final_change": change["record"],
        "override_sync": override_sync,
        "message": portfolio_sale_preview(parameters, override_config)["summary"],
        "database": str(module.DB_PATH),
    }


def portfolio_execute_pending_order(module, ns, parameters):
    symbol = portfolio_normalize_symbol(first_value(parameters, "symbol", "new_symbol", "ticker", "asset"))
    if not symbol:
        raise ValueError("Falta symbol para ejecutar orden pendiente.")
    gross_amount = portfolio_float(first_value(parameters, "gross_amount", "amount", "usd_amount", "invested_usd"))
    price = portfolio_float(first_value(parameters, "price", "entry_price", "precio_entrada"))
    quantity = portfolio_float(first_value(parameters, "quantity", "units", "cantidad"))
    if gross_amount is None:
        raise ValueError("Falta gross_amount/amount para ejecutar orden pendiente.")
    if price in (None, 0):
        raise ValueError("Falta price/entry_price para ejecutar orden pendiente.")
    cancelled_pending = None
    if boolish(first_value(parameters, "cancel_pending", "void_pending", default=True)):
        try:
            cancelled_pending = module.cancel_transaction(
                ns(
                    portfolio_id=parameters.get("portfolio_id") or module.DEFAULT_PORTFOLIO_ID,
                    transaction_id=parameters.get("transaction_id") or parameters.get("pending_transaction_id") or parameters.get("draft_transaction_id"),
                    symbol=symbol,
                    status="draft",
                    reason=parameters.get("reason") or f"Orden pendiente {symbol} marcada como ejecutada.",
                )
            ).get("record")
        except Exception as exc:
            cancelled_pending = {"skipped": True, "reason": brief(str(exc), 260)}
    tx = module.add_transaction(
        ns(
            portfolio_id=parameters.get("portfolio_id") or module.DEFAULT_PORTFOLIO_ID,
            occurred_at=parameters.get("occurred_at"),
            symbol=symbol,
            side="BUY",
            quantity=quantity,
            price=price,
            gross_amount=gross_amount,
            fees=parameters.get("fees") or 0,
            currency=parameters.get("currency") or "USD",
            status="final",
            source=parameters.get("source") or "kim_live_execute_pending",
            notes=parameters.get("notes") or f"Orden pendiente {symbol} ejecutada por instruccion del doctor.",
        )
    )
    change = module.record_final_change(
        ns(
            portfolio_id=parameters.get("portfolio_id") or module.DEFAULT_PORTFOLIO_ID,
            decided_at=parameters.get("decided_at"),
            change_type="execute_pending_order",
            summary=parameters.get("summary") or f"{symbol} dejo de estar pendiente y quedo como posicion activa por {gross_amount} USD a {price}.",
            rationale=parameters.get("rationale") or "Ejecucion confirmada por el doctor.",
            related_consultation_id=parameters.get("related_consultation_id"),
            executed=True,
            execution_ref=tx["record"]["id"],
        )
    )
    override_sync = portfolio_sync_manual_execution_to_overrides(parameters)
    return {
        "ok": True,
        "action": "execute_pending_order",
        "executed_order": tx["record"],
        "cancelled_pending": cancelled_pending,
        "final_change": change["record"],
        "override_sync": override_sync,
        "database": str(module.DB_PATH),
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
        "aggregate_order",
        "agglomerate_order",
        "agglomerate_orders",
        "set_position",
        "manual_update_order",
        "update_manual_order",
        "edit_manual_order",
        "manual_delete_order",
        "delete_manual_order",
        "remove_manual_order",
        "normalize_manual_orders",
        *PORTFOLIO_MANUAL_SENSITIVE_ACTIONS,
        *PORTFOLIO_SALE_ACTIONS,
        *PORTFOLIO_EXECUTION_ACTIONS,
    }
    spec = importlib.util.spec_from_file_location("kim_portfolio_db", PORTFOLIO_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    runtime_root, bifrost_root = configure_portfolio_module(module)

    def ns(**values):
        return type("PortfolioArgs", (), values)()

    confirm = boolish(parameters.get("confirm"))
    if action in PORTFOLIO_SALE_ACTIONS and not confirm:
        summary = module.portfolio_summary_json()
        preview = portfolio_sale_preview(parameters, portfolio_report_override_config(summary))
        return confirmation_preview(
            "portfolio",
            "sell_position",
            "Confirmar venta final de portafolio con PIN/frase antes de cerrar la posicion.",
            preview,
            execution_parameters={**parameters, "confirm": True},
        )
    if action in PORTFOLIO_EXECUTION_ACTIONS and not confirm:
        symbol = portfolio_normalize_symbol(first_value(parameters, "symbol", "new_symbol", "ticker", "asset"))
        gross_amount = first_value(parameters, "gross_amount", "amount", "usd_amount", "invested_usd")
        price = first_value(parameters, "price", "entry_price", "precio_entrada")
        return confirmation_preview(
            "portfolio",
            "execute_pending_order",
            f"Confirmar que {symbol or 'la orden'} dejo de estar pendiente y quedara como posicion activa.",
            {
                "symbol": symbol,
                "gross_amount": gross_amount,
                "price": price,
                "notes": parameters.get("notes") or parameters.get("summary") or "",
            },
            execution_parameters={**parameters, "confirm": True},
        )
    if action in PORTFOLIO_MANUAL_SENSITIVE_ACTIONS and not confirm:
        summary = module.portfolio_summary_json()
        override_config = portfolio_report_override_config(summary)
        if action in {"agglomerate_manual_orders", "aggregate_manual_orders", "consolidate_manual_orders", "consolidate_orders"}:
            selected = portfolio_selected_manual_entries(override_config, parameters) if override_config else []
            preview = portfolio_consolidation_preview_for_entries(selected, override_config or {}) if selected else {"parameters": parameters}
            summary_text = "Confirmar aglomeracion manual del portafolio Sr. Eli."
        elif action in {"split_consolidated_order", "split_manual_order", "split_order", "separate_order", "separate_orders"}:
            selected = portfolio_selected_manual_entries(override_config, parameters) if override_config else []
            preview = {"selected": selected, "parameters": parameters}
            summary_text = "Confirmar separacion de una posicion consolidada."
        elif action in {"manual_delete_order", "delete_manual_order", "remove_manual_order", "remove_order", "remove_portfolio_order"}:
            selected = portfolio_selected_manual_entries(override_config, parameters) if override_config else []
            preview = {"selected": selected, "parameters": parameters}
            summary_text = "Confirmar eliminacion/remocion de orden manual del portafolio Sr. Eli."
        else:
            preview = {"parameters": parameters}
            summary_text = "Confirmar cambio sensible del portafolio Sr. Eli."
        return confirmation_preview(
            "portfolio",
            action,
            summary_text,
            preview,
            execution_parameters={**parameters, "confirm": True},
        )

    if action == "status":
        try:
            result = module.status_json()
        except Exception as exc:
            if "no such table" not in str(exc).lower():
                raise
            result = module.init_db()
    elif action in {"refresh_prices", "clear_price_cache", "clear_market_cache", "actualizar_precios", "borrar_cache_precios"}:
        clear_result = clear_market_price_caches(reason=action)
        providers = parameters.get("providers") or ["binance", "mexc", "bybit"]
        symbols = [
            str(entry.get("symbol") or "").upper()
            for entry in portfolio_report_override_config(module.portfolio_summary_json()).get("manual_entries", [])
            if str(entry.get("symbol") or "").strip()
        ]
        warmup = warm_market_price_sources(symbols, providers=providers)
        result = {**clear_result, "providers": providers, "symbols": symbols, "source_warmup": warmup}
    elif action == "summary":
        result = module.portfolio_summary_json()
    elif action in {"client_report", "eli_client_report", "sr_eli_report"}:
        result = portfolio_client_report(module.portfolio_summary_json(), parameters)
    elif action in {"whatsapp_preview", "preview_whatsapp_report", "compose_whatsapp_report", "portfolio_whatsapp_preview"}:
        report = portfolio_client_report(module.portfolio_summary_json(), {**parameters, "save_standard": False})
        composed = portfolio_compose_whatsapp_messages(report, {**parameters, "dry_run": True, "allow_unvalidated": True})
        result = {
            "ok": True,
            "provider": "portfolio",
            "action": "whatsapp_preview",
            "preview": composed.get("preview", {}),
            "messages": composed.get("messages", []),
            "selected_lines": composed.get("selected_lines", []),
            "report": report,
        }
    elif action in {"manual_orders", "list_manual_orders", "editable_orders", "portfolio_manual_orders"}:
        result = portfolio_manual_orders(module.portfolio_summary_json(), parameters)
    elif action in {"aggregation_suggestions", "agglomeration_suggestions", "suggest_agglomerations", "suggest_consolidations"}:
        result = portfolio_manual_aggregation_suggestions(module.portfolio_summary_json(), parameters)
    elif action in {"normalize_manual_orders", "fix_manual_order_states"}:
        result = portfolio_manual_orders(
            module.portfolio_summary_json(),
            {**parameters, "normalize_states": True},
        )
    elif action in {"manual_update_order", "update_manual_order", "edit_manual_order"}:
        result = portfolio_update_manual_order(module.portfolio_summary_json(), parameters)
    elif action in {"manual_delete_order", "delete_manual_order", "remove_manual_order"}:
        result = portfolio_delete_manual_order(module.portfolio_summary_json(), parameters)
    elif action in {"remove_order", "remove_portfolio_order"}:
        result = portfolio_delete_manual_order(module.portfolio_summary_json(), parameters)
    elif action in {"agglomerate_manual_orders", "aggregate_manual_orders", "consolidate_manual_orders", "consolidate_orders"}:
        result = portfolio_agglomerate_manual_orders(module.portfolio_summary_json(), parameters)
    elif action in {"split_consolidated_order", "split_manual_order", "split_order", "separate_order", "separate_orders"}:
        result = portfolio_split_manual_order(module.portfolio_summary_json(), parameters)
    elif action in {
        "weighted_average_breakdown",
        "weighted_average",
        "promedio_ponderado",
        "explicar_promedio_ponderado",
    }:
        result = portfolio_weighted_average_breakdown(module.portfolio_summary_json(), parameters)
    elif action in {
        "fundamental_report",
        "portfolio_fundamental_report",
        "reporte_fundamental",
        "reporte_fundamental_sr_eli",
        "catalizadores_portafolio",
        "sr_eli_fundamental",
    }:
        result = portfolio_fundamental_report(module.portfolio_summary_json(), parameters)
    elif action in {"fundamental_history", "portfolio_fundamental_history", "news_history", "historial_fundamental"}:
        result = portfolio_fundamental_history(parameters)
    elif action in {
        "send_whatsapp_report",
        "send_updated_portfolio",
        "send_portfolio",
        "enviar_portafolio",
        "mandar_portafolio",
        "enviame_portafolio_actualizado",
    }:
        result = portfolio_send_whatsapp_report(module.portfolio_summary_json(), parameters)
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
    elif action in PORTFOLIO_SALE_ACTIONS:
        result = portfolio_execute_sale(
            module,
            ns,
            parameters,
            portfolio_report_override_config(module.portfolio_summary_json()),
        )
    elif action in PORTFOLIO_EXECUTION_ACTIONS:
        result = portfolio_execute_pending_order(module, ns, parameters)
    elif action in {"aggregate_order", "agglomerate_order", "agglomerate_orders"}:
        members = parameters.get("members") or parameters.get("members_json")
        if isinstance(members, (dict, list)):
            members = json.dumps(members, ensure_ascii=False)
        result = module.aggregate_order(
            ns(
                portfolio_id=parameters.get("portfolio_id") or module.DEFAULT_PORTFOLIO_ID,
                canonical_order=parameters.get("canonical_order") or parameters.get("order_id") or parameters.get("base_order"),
                symbol=parameters.get("symbol"),
                label=parameters.get("label"),
                status=parameters.get("status") or "active",
                notes=parameters.get("notes"),
                members=members,
                member_order=parameters.get("member_order") or parameters.get("sub_order"),
                source_order=parameters.get("source_order") or parameters.get("from_order"),
                transaction_id=parameters.get("transaction_id") or parameters.get("id"),
                role=parameters.get("role") or "reinforcement",
                amount_usd=parameters.get("amount_usd") or parameters.get("gross_amount") or parameters.get("amount") or parameters.get("usd_amount"),
                price=parameters.get("price"),
                quantity=parameters.get("quantity"),
                include_in_average=not boolish(parameters.get("exclude_from_average")),
                member_status=parameters.get("member_status") or "active",
                member_notes=parameters.get("member_notes") or parameters.get("notes"),
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
        "follow up",
        "trato",
        "deal",
        "correo",
        "email",
        "llamada cliente",
        "isaac",
        "arturo",
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
        "context block",
        "bloque de contexto",
        "paquete de contexto",
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
            str(MEMORY_KNOWLEDGE),
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
            str(CLICKUP_OPERATION_MAP),
        ],
        "crm_clients": [
            str(MEMORY_CONTEXT_DIR / "pipedrive_context_latest.json"),
            str(PERSON_CONTEXT_INDEX),
            str(PERSON_CONTEXT_DIR),
            str(EXTERNAL_CALL_CONTEXT_BLOCKS),
            str(EXTERNAL_CALL_CONTEXT_BLOCKS_DIR),
            str(CRM_ROOT),
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


def knowledge_slug(value):
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^A-Za-z0-9]+", "-", text.lower()).strip("-")
    return text[:90] or "knowledge"


def write_knowledge_card(card, session_id=""):
    title = str(card.get("title") or "Conocimiento Kim").strip()[:140]
    domain = knowledge_slug(card.get("domain") or "general")
    folder = MEMORY_KNOWLEDGE / domain
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        folder = RUNTIME_KNOWLEDGE / domain
        folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{today()}-{knowledge_slug(title)}.md"
    content = (
        f"# {title}\n\n"
        f"- Dominio: {card.get('domain') or 'general'}\n"
        f"- Session ID: {session_id}\n"
        f"- Fuente: transcript literal Kim Live\n"
        f"- Confianza: {card.get('confidence', '')}\n"
        f"- Actualizado: {now_iso()}\n\n"
        "## Sintesis\n\n"
        f"{str(card.get('content') or card.get('summary') or '').strip()}\n\n"
        "## Cita Fuente\n\n"
        f"{str(card.get('source_quote') or '').strip()}\n"
    )
    path.write_text(content, encoding="utf-8")
    return str(path)


def review_prompt_for_transcript(text, session_id=""):
    return (
        "Eres el bibliotecario operativo de Kim Live. Analiza este transcript literal y decide que debe "
        "quedar en memoria, CRM local o ClickUp. Responde SOLO JSON valido, sin markdown.\n\n"
        "Buenas practicas: conserva el transcript como fuente primaria; crea tarjetas de conocimiento "
        "solo para ideas reutilizables; propone CRM solo cuando haya datos claros de persona/cliente; "
        "propone tareas solo cuando haya una accion pendiente concreta. No inventes telefonos, correos, "
        "fechas, nombres ni empresas. Usa confidence 0-1.\n\n"
        "Schema exacto:\n"
        "{\n"
        '  "knowledge_cards": [{"title": "", "domain": "general|tesca|clientes|operaciones|producto|filosofia|finanzas", "content": "", "source_quote": "", "confidence": 0.0}],\n'
        '  "crm_updates": [{"name": "", "phone": "", "email": "", "company": "", "contact_type": "client|partner|lead|vendor|family|other", "notes": "", "source_quote": "", "confidence": 0.0}],\n'
        '  "clickup_tasks": [{"title": "", "description": "", "space_name": "", "list_name": "", "source_quote": "", "confidence": 0.0}],\n'
        '  "warnings": []\n'
        "}\n\n"
        "Criterios:\n"
        "- knowledge_cards: conceptos, metodologias, decisiones de arquitectura, filosofia, instrucciones estables.\n"
        "- crm_updates: datos de personas/clientes/contactos y relaciones.\n"
        "- clickup_tasks: pendientes ejecutables para Kim/Codex/proyectos.\n"
        "- Si una accion requiere confirmacion externa, igual proponla; el sistema la dejara preparada, no confirmada.\n\n"
        f"Session ID: {session_id}\n\n"
        f"Transcript:\n{text[:60000]}"
    )


def conversation_review(text="", session_id="", mode="auto"):
    text = (text or "").strip()
    session_id = str(session_id or "").strip()
    if len(text) < 120:
        return {"ok": True, "reviewed": False, "reason": "Transcript demasiado corto para revisar."}
    prompt = review_prompt_for_transcript(text, session_id=session_id)
    response, model = openai_response_with_fallback(
        DOCUMENT_MODEL_CANDIDATES,
        {"input": prompt, "max_output_tokens": 2200},
    )
    parsed = parse_json_object_from_text(output_text_from_response(response))
    parsed.setdefault("knowledge_cards", [])
    parsed.setdefault("crm_updates", [])
    parsed.setdefault("clickup_tasks", [])
    parsed.setdefault("warnings", [])
    knowledge_saved = []
    crm_saved = []
    prepared_actions = []
    for card in parsed.get("knowledge_cards", [])[:8]:
        try:
            confidence = float(card.get("confidence") or 0)
        except (TypeError, ValueError):
            confidence = 0
        if confidence < 0.68:
            continue
        if not str(card.get("content") or card.get("summary") or "").strip():
            continue
        path = write_knowledge_card(card, session_id=session_id)
        knowledge_saved.append({"title": card.get("title"), "domain": card.get("domain"), "path": path, "confidence": confidence})
    for contact in parsed.get("crm_updates", [])[:8]:
        try:
            confidence = float(contact.get("confidence") or 0)
        except (TypeError, ValueError):
            confidence = 0
        phone = normalize_phone_number(first_value(contact, "phone", "telefono", default=""))
        email = str(first_value(contact, "email", "correo", default="") or "").strip()
        name = str(first_value(contact, "name", "display_name", default="") or "").strip()
        if confidence < 0.78 or not name or not (phone or email):
            continue
        saved = crm_upsert_contact(
            {
                "display_name": name,
                "phone": phone,
                "email": email,
                "company": contact.get("company") or "",
                "contact_type": contact.get("contact_type") or "client",
                "notes": "Auto review Kim Live. " + str(contact.get("notes") or contact.get("source_quote") or ""),
            },
            source="conversation_review",
        )
        crm_saved.append({"id": saved.get("id"), "display_name": saved.get("display_name"), "path": saved.get("markdown_path"), "confidence": confidence})
    for task in parsed.get("clickup_tasks", [])[:8]:
        try:
            confidence = float(task.get("confidence") or 0)
        except (TypeError, ValueError):
            confidence = 0
        title = str(first_value(task, "title", "name", "subject", default="") or "").strip()
        if confidence < 0.82 or not title:
            continue
        params = {
            "title": title,
            "body": str(first_value(task, "description", "body", "notes", default="") or "").strip(),
            "space_name": task.get("space_name") or "",
            "list_name": task.get("list_name") or "",
        }
        params = clickup_apply_operational_defaults(params)
        try:
            result = run_api_bridge("clickup", "create_task", params, confirm=False, session_id=session_id, transcript=text)
            if not result.get("prepared_action_id"):
                parsed.setdefault("warnings", []).append(f"ClickUp no preparo accion para '{title}': {brief(result.get('error') or result, 240)}")
                continue
            prepared_actions.append(
                {
                    "id": result.get("prepared_action_id"),
                    "provider": result.get("provider"),
                    "action": result.get("action"),
                    "summary": result.get("summary"),
                    "prepared_action_id": result.get("prepared_action_id"),
                    "preview": result.get("preview"),
                    "confidence": confidence,
                }
            )
        except Exception as exc:
            parsed.setdefault("warnings", []).append(f"No pude preparar tarea ClickUp '{title}': {brief(str(exc), 240)}")
    review = {
        "ok": True,
        "reviewed": True,
        "provider": "memory",
        "action": "conversation_review",
        "mode": mode,
        "model": model,
        "session_id": session_id,
        "knowledge_saved": knowledge_saved,
        "crm_saved": crm_saved,
        "prepared_actions": prepared_actions,
        "warnings": parsed.get("warnings", []),
        "raw_counts": {
            "knowledge_cards": len(parsed.get("knowledge_cards", [])),
            "crm_updates": len(parsed.get("crm_updates", [])),
            "clickup_tasks": len(parsed.get("clickup_tasks", [])),
        },
    }
    append_jsonl_any([MEMORY_CONTEXT_DIR / "conversation_reviews.jsonl", RUNTIME_CONTEXT / "conversation_reviews.jsonl"], review)
    append_memory(
        "conversation_review",
        {
            "session_id": session_id,
            "knowledge_saved": len(knowledge_saved),
            "crm_saved": len(crm_saved),
            "prepared_actions": len(prepared_actions),
            "warnings": review["warnings"][:3],
        },
    )
    append_daily_note(
        f"Kim librarian review: session={session_id}; knowledge={len(knowledge_saved)}; "
        f"crm={len(crm_saved)}; prepared={len(prepared_actions)}"
    )
    return review


def context_brief(limit=9000):
    parts = [
        "Identidad: Dr. Yehoshua trabaja con Kim como interfaz verbal y Codex como ejecutor.",
        "Arquitectura: BIFROST es el traje local; Notion es memoria/base de conocimiento; ClickUp es ejecucion/proyectos; Telegram notifica; Codex ejecuta.",
        "Objetivo operativo: Kim Live debe conversar con memoria local, consultar contexto, compilar tareas y enviarlas a Codex al cerrar conversacion.",
        "Version viva:\n" + version_memory_snapshot(),
    ]
    context_text = read_text_tail_any([CONTEXT_MEMORY, RUNTIME_CONTEXT / "kim_context.md"], 2200)
    if context_text:
        parts.append("Memoria contextual:\n" + context_text)
    eval_text = read_text_tail_any([NOTION_CLICKUP_EVAL, RUNTIME_CONTEXT / "notion_vs_clickup_evaluation.md"], 1200)
    if eval_text:
        parts.append("Criterio Notion/ClickUp:\n" + eval_text)
    multitenant_plan = read_text_tail_any([MULTITENANT_AGENT_PLAN, RUNTIME_MULTITENANT_AGENT_PLAN], 1800)
    if multitenant_plan:
        parts.append("Plan multiempresa Kim:\n" + multitenant_plan)
    inbound_spec = read_text_tail_any([INBOUND_CALL_PRIVACY_SPEC, RUNTIME_INBOUND_CALL_PRIVACY_SPEC], 1400)
    if inbound_spec:
        parts.append("Politica de llamadas entrantes:\n" + inbound_spec)
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
    file_knowledge = load_file_knowledge_entries(limit=6)
    if file_knowledge:
        parts.append(
            "File knowledge durable:\n"
            + "\n".join(
                f"- {item.get('domain') or 'general'} / {item.get('filename')}: {item.get('knowledge_card_path')}"
                for item in file_knowledge[-6:]
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
    backlog = kim_product_backlog_summary()
    if backlog.get("top_priority"):
        parts.append(
            "Kim product backlog:\n"
            f"- Foco: {backlog.get('focus')}\n"
            f"- Prioridad actual: {backlog.get('top_priority')} [{backlog.get('top_priority_status') or 'planned'}]"
        )
    api_spec = read_text_tail_any([API_BRIDGE_SPEC, RUNTIME_API_BRIDGE_SPEC], 1600)
    if api_spec:
        parts.append("Kim API bridge:\n" + api_spec)
    notion_inventory = read_text_tail_any([NOTION_ACCESS_INVENTORY, RUNTIME_NOTION_ACCESS_INVENTORY], 1800)
    if notion_inventory:
        parts.append("Notion access inventory:\n" + notion_inventory)
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
    backlog = load_kim_product_backlog_payload()
    sources = []
    for path in [
        CONTEXT_MEMORY,
        daily_memory_path(),
        OPERATING_MODEL,
        NOTION_CLICKUP_EVAL,
        MULTITENANT_AGENT_PLAN,
        INBOUND_CALL_PRIVACY_SPEC,
        RUNTIME_INBOUND_CALL_PRIVACY_SPEC,
        RUNTIME_MULTITENANT_AGENT_PLAN,
        CLICKUP_INVENTORY,
        CLICKUP_TASKS_JSON,
        CLICKUP_TASKS_MARKDOWN,
        RUNTIME_CLICKUP_TASKS_JSON,
        RUNTIME_CLICKUP_TASKS_MARKDOWN,
        API_BRIDGE_SPEC,
        API_BRIDGE_LOG,
        KIM_PRODUCT_BACKLOG_SPEC,
        KIM_PRODUCT_BACKLOG_JSON,
        KIM_PRODUCT_BACKLOG_MD,
        RUNTIME_KIM_PRODUCT_BACKLOG_JSON,
        RUNTIME_KIM_PRODUCT_BACKLOG_MD,
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
        "product_backlog": kim_product_backlog_summary(backlog),
        "research_sources": load_research_source_cache().get("items", [])[-12:],
        "sources": sources,
    }


def load_bifrost_export_state():
    state = read_json_file(BIFROST_EXPORT_TOKENS, {"tokens": {}})
    if not isinstance(state, dict):
        state = {"tokens": {}}
    state.setdefault("tokens", {})
    return state


def save_bifrost_export_state(state):
    BIFROST_EXPORT_TOKENS.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = now_iso()
    write_json_file(BIFROST_EXPORT_TOKENS, state)


def cleanup_bifrost_exports():
    now_ts = dt.datetime.now(dt.timezone.utc).timestamp()
    state = load_bifrost_export_state()
    changed = False
    for digest, item in list((state.get("tokens") or {}).items()):
        expired = float(item.get("expires_at_ts") or 0) <= now_ts
        exhausted = int(item.get("download_count") or 0) >= int(item.get("max_downloads") or BIFROST_EXPORT_MAX_DOWNLOADS)
        path = pathlib.Path(item.get("path") or "")
        manifest_path = pathlib.Path(item.get("manifest_path") or "")
        if expired or exhausted or not path.exists():
            state["tokens"].pop(digest, None)
            changed = True
            try:
                if path.exists() and path.is_file() and path.parent == BIFROST_EXPORT_DIR:
                    path.unlink()
            except OSError:
                pass
            try:
                if manifest_path.exists() and manifest_path.is_file() and manifest_path.parent == BIFROST_EXPORT_DIR:
                    manifest_path.unlink()
            except OSError:
                pass
    if changed:
        save_bifrost_export_state(state)


def bifrost_export_should_skip(path):
    try:
        rel = path.relative_to(BIFROST)
    except ValueError:
        return True
    if path.is_symlink():
        return True
    if any(part in BIFROST_EXPORT_SKIP_NAMES for part in rel.parts):
        return True
    if path.is_file() and path.suffix.lower() in BIFROST_EXPORT_SKIP_SUFFIXES:
        return True
    return False


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_bifrost_export_zip(label=""):
    if not BIFROST.exists():
        raise ValueError(f"No existe BIFROST en {BIFROST}.")
    cleanup_bifrost_exports()
    BIFROST_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"BIFROST-{stamp}.zip"
    manifest_filename = f"BIFROST-{stamp}-manifest.json"
    export_path = BIFROST_EXPORT_DIR / filename
    manifest_path = BIFROST_EXPORT_DIR / manifest_filename
    files = 0
    raw_bytes = 0
    manifest = {
        "created_at": now_iso(),
        "app_version": APP_VERSION,
        "manifest_name": "BIFROST_EXPORT_MANIFEST",
        "source_root": str(BIFROST),
        "archive_filename": filename,
        "label": brief(label, 120),
        "notes": [
            "This archive contains BIFROST source, memory and docs.",
            "It does not include macOS Keychain secrets, active LaunchAgents, browser sessions, ~/.kim_live or ~/.kim_telegram.",
            "Restore secrets and services using BIFROST/docs/MIGRATION_RUNBOOK.md.",
        ],
    }
    with zipfile.ZipFile(export_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("BIFROST_EXPORT_MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        for path in sorted(BIFROST.rglob("*")):
            if bifrost_export_should_skip(path) or not path.is_file():
                continue
            try:
                stat = path.stat()
            except OSError:
                continue
            archive.write(path, path.relative_to(BIFROST.parent).as_posix())
            files += 1
            raw_bytes += stat.st_size
    with zipfile.ZipFile(export_path, "r") as archive:
        bad_member = archive.testzip()
    if bad_member:
        try:
            export_path.unlink()
        except OSError:
            pass
        raise ValueError(f"El ZIP BIFROST se genero corrupto en {bad_member}.")
    size = export_path.stat().st_size
    sha256 = file_sha256(export_path)
    token = secrets.token_urlsafe(32)
    expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=BIFROST_EXPORT_TTL_SECONDS)
    manifest.update(
        {
            "generated_status": "ok",
            "archive_size_bytes": size,
            "archive_sha256": sha256,
            "source_file_count": files,
            "source_bytes": raw_bytes,
            "expires_at": expires.isoformat(),
            "ttl_seconds": BIFROST_EXPORT_TTL_SECONDS,
            "max_downloads": BIFROST_EXPORT_MAX_DOWNLOADS,
            "migration_start_here": "BIFROST/AGENT_HANDOFF.md",
        }
    )
    write_json_file(manifest_path, manifest)
    state = load_bifrost_export_state()
    state.setdefault("tokens", {})[token_hash(token)] = {
        "created_at": now_iso(),
        "expires_at": expires.isoformat(),
        "expires_at_ts": expires.timestamp(),
        "path": str(export_path),
        "manifest_path": str(manifest_path),
        "filename": filename,
        "manifest_filename": manifest_filename,
        "size_bytes": size,
        "sha256": sha256,
        "source_file_count": files,
        "source_bytes": raw_bytes,
        "download_count": 0,
        "max_downloads": BIFROST_EXPORT_MAX_DOWNLOADS,
    }
    save_bifrost_export_state(state)
    append_memory(
        "bifrost_export_created",
        {
            "filename": filename,
            "size_bytes": size,
            "source_file_count": files,
            "expires_at": expires.isoformat(),
        },
    )
    append_daily_note(f"Se genero respaldo descargable temporal de BIFROST: {filename}.")
    return {
        "ok": True,
        "filename": filename,
        "manifest_filename": manifest_filename,
        "size_bytes": size,
        "sha256": sha256,
        "source_file_count": files,
        "source_bytes": raw_bytes,
        "expires_at": expires.isoformat(),
        "ttl_seconds": BIFROST_EXPORT_TTL_SECONDS,
        "max_downloads": BIFROST_EXPORT_MAX_DOWNLOADS,
        "download_url": "/api/bifrost-export/download?token=" + urllib.parse.quote(token),
        "manifest_url": "/api/bifrost-export/manifest?token=" + urllib.parse.quote(token),
    }


def get_bifrost_export_item(token):
    cleanup_bifrost_exports()
    digest = token_hash(token)
    item = (load_bifrost_export_state().get("tokens") or {}).get(digest)
    if not item:
        raise ValueError("El enlace de descarga no existe o expiro.")
    if int(item.get("download_count") or 0) >= int(item.get("max_downloads") or BIFROST_EXPORT_MAX_DOWNLOADS):
        raise ValueError("El enlace de descarga llego al limite de descargas.")
    if float(item.get("expires_at_ts") or 0) <= dt.datetime.now(dt.timezone.utc).timestamp():
        raise ValueError("El enlace de descarga expiro.")
    path = pathlib.Path(item.get("path") or "")
    if path.parent != BIFROST_EXPORT_DIR or not path.exists() or not path.is_file():
        raise ValueError("El archivo temporal de BIFROST ya no esta disponible.")
    return item, path


def mark_bifrost_export_downloaded(token):
    digest = token_hash(token)
    state = load_bifrost_export_state()
    item = (state.get("tokens") or {}).get(digest)
    if item:
        item["last_downloaded_at"] = now_iso()
        item["download_count"] = int(item.get("download_count") or 0) + 1
        save_bifrost_export_state(state)


def send_bifrost_export_download(handler, token):
    item, path = get_bifrost_export_item(token)
    filename = item.get("filename") or path.name
    handler.send_response(200)
    handler.send_header("Content-Type", "application/zip")
    handler.send_header("Content-Disposition", f'attachment; filename="{filename}"')
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Accept-Ranges", "none")
    handler.send_header("Content-Length", str(path.stat().st_size))
    handler.end_headers()
    with path.open("rb") as handle:
        shutil.copyfileobj(handle, handler.wfile)
    mark_bifrost_export_downloaded(token)
    append_memory(
        "bifrost_export_downloaded",
        {
            "filename": filename,
            "size_bytes": item.get("size_bytes"),
            "download_count": int(item.get("download_count") or 0) + 1,
            "max_downloads": int(item.get("max_downloads") or BIFROST_EXPORT_MAX_DOWNLOADS),
        },
    )


def send_bifrost_export_manifest(handler, token):
    item, _path = get_bifrost_export_item(token)
    manifest_path = pathlib.Path(item.get("manifest_path") or "")
    if manifest_path.parent != BIFROST_EXPORT_DIR or not manifest_path.exists() or not manifest_path.is_file():
        raise ValueError("El manifest temporal de BIFROST ya no esta disponible.")
    filename = item.get("manifest_filename") or manifest_path.name
    data = manifest_path.read_bytes()
    handler.send_response(200)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Disposition", f'attachment; filename="{filename}"')
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)
    append_memory("bifrost_export_manifest_downloaded", {"filename": filename, "archive_filename": item.get("filename")})


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
        key = load_keychain_secret(OPENAI_KEYCHAIN_SERVICE, required=True)
    except ValueError as exc:
        raise ValueError(
            "No encuentro la API key de OpenAI en Keychain. "
            "Abre /setup-openai-key para guardarla."
        ) from exc
    if not key:
        raise ValueError("La API key de OpenAI esta vacia en Keychain.")
    return key


def twiml_escape(value):
    return html.escape(str(value or ""), quote=False)


def twiml_response(inner):
    return '<?xml version="1.0" encoding="UTF-8"?><Response>' + inner + "</Response>"


def twilio_say(text):
    return f'<Say language="es-MX" voice="{TWILIO_POLLY_VOICE}">{twiml_escape(text)}</Say>'


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


def iso_age_seconds(value):
    if not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    now = dt.datetime.now(parsed.tzinfo) if parsed.tzinfo else dt.datetime.now()
    return max(0.0, (now - parsed).total_seconds())


def notify_kim_live(kind, title, body="", severity="info", metadata=None):
    event = {
        "id": "NTF-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S-") + secrets.token_hex(3).upper(),
        "at": now_iso(),
        "kind": brief(kind, 80),
        "title": brief(title, 180),
        "body": brief(body, 1200),
        "severity": brief(severity, 24),
        "metadata": metadata or {},
        "acknowledged": False,
    }
    for path in [RUNTIME_KIM_LIVE_NOTIFICATIONS, KIM_LIVE_NOTIFICATIONS]:
        try:
            append_jsonl(path, event)
        except (PermissionError, OSError):
            continue
    return event


def list_kim_live_notifications(limit=25):
    try:
        limit = max(1, min(int(limit or 25), 100))
    except (TypeError, ValueError):
        limit = 25
    entries = []
    seen = set()
    for path in [RUNTIME_KIM_LIVE_NOTIFICATIONS, KIM_LIVE_NOTIFICATIONS]:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (FileNotFoundError, PermissionError, OSError):
            continue
        for line in reversed(lines):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            item_id = item.get("id") or f"{item.get('at')}:{item.get('title')}"
            if item_id in seen:
                continue
            seen.add(item_id)
            entries.append(item)
            if len(entries) >= limit:
                return entries
    return entries


def set_twilio_realtime_health(status="ok", reason="", metadata=None, notify=True):
    payload = {
        "ok": status == "ok",
        "status": status,
        "reason": brief(reason, 300),
        "metadata": metadata or {},
        "updated_at": now_iso(),
    }
    write_json_file_both(TWILIO_REALTIME_HEALTH, RUNTIME_TWILIO_REALTIME_HEALTH, payload)
    if status != "ok" and notify:
        notify_kim_live(
            "twilio_realtime_health",
            "Twilio voice fallback activated",
            f"Realtime no esta disponible para llamadas. Motivo: {payload['reason'] or status}.",
            severity="warning",
            metadata=payload,
        )
    return payload


def twilio_realtime_health_status(max_age_seconds=300):
    payload = read_json_file_any([RUNTIME_TWILIO_REALTIME_HEALTH, TWILIO_REALTIME_HEALTH], {})
    if not payload:
        return {"ok": True, "status": "unknown", "available": True, "recent": False}
    age = iso_age_seconds(payload.get("updated_at"))
    recent = age is not None and age <= max_age_seconds
    unavailable = payload.get("status") != "ok" and recent
    return {
        **payload,
        "ok": not unavailable,
        "available": not unavailable,
        "recent": recent,
        "age_seconds": age,
        "max_age_seconds": max_age_seconds,
    }


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
    caller_profile = twilio_inbound_caller_profile(caller, called)
    route = memory_router("classify", clean, session_id=session_id)
    if caller_profile.get("is_doctor"):
        phone_mode = (
            "Estas hablando por telefono con el Dr Yehoshua. "
            "Puedes asumir continuidad operativa y tomar instrucciones directas. "
            "Eres puente remoto hacia Kim Live: registra contexto, tareas y recados; notifica Kim Live; "
            "prepara acciones si corresponde, pero no afirmes ejecucion externa sin resultado confirmado."
        )
    else:
        pending_summary = caller_profile.get("pending_summary") or "Sin pendientes sintetizados todavia."
        phone_mode = (
            "Estas atendiendo una linea telefonica para terceros. "
            "Este canal comparte memoria con Kim Local/Kim Live web, pero es una recepcion telefonica distinta. "
            "No asumas que quien llama es el doctor. Presentate como Kim, asistente del Dr. Yehoshua, "
            "y usa la frase 'si necesita algo, con mucho gusto se lo puedo informar' cuando encaje. "
            "Solo puedes compartir pendientes propios del llamante. No des contexto de terceros ni "
            "pendientes generales del doctor. Si la identidad no es clara, pide nombre completo antes "
            "de compartir informacion personal. Si la llamada es general o comercial, explica servicios "
            "de forma breve.\n"
            f"Perfil conocido: {caller_profile.get('display_name')} | conocido={caller_profile.get('known_contact')} "
            f"| empresa={caller_profile.get('company_summary') or 'N/A'} | relacion={caller_profile.get('relationship_summary') or 'N/A'}\n"
            f"Pendientes propios conocidos: {pending_summary}\n"
            f"Servicios generales permitidos: {caller_profile.get('service_summary')}\n"
            f"Politica secretaria/puente: {caller_profile.get('remote_secretary_bridge_policy') or REMOTE_SECRETARY_BRIDGE_POLICY}\n"
            f"Politica relacion/buen nombre: {caller_profile.get('inbound_relationship_goodwill_policy') or INBOUND_RELATIONSHIP_GOODWILL_POLICY}\n"
            f"Playbook ventas/RP a reunion: {caller_profile.get('whatsapp_sales_pr_meeting_playbook') or WHATSAPP_SALES_PR_MEETING_PLAYBOOK}\n"
            f"Politica de privacidad: {caller_profile.get('privacy_summary')}"
        )
    prompt = (
        "Eres Kim Live hablando por telefono. "
        f"{active_voice_style()} "
        "Responde en espanol mexicano, con una frase breve y accionable, idealmente menor a 45 palabras. "
        "Si la instruccion requiere trabajo largo, confirma que la guardaras para ejecucion en Kim Live/Codex. "
        "No inventes que ya hiciste acciones externas si solo las estas recibiendo por telefono.\n\n"
        f"{phone_mode}\n\n"
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
            "caller_profile": {
                "display_name": caller_profile.get("display_name"),
                "known_contact": caller_profile.get("known_contact"),
                "is_doctor": caller_profile.get("is_doctor"),
            },
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
    caller_profile = twilio_inbound_caller_profile(caller, called)
    caller_label = twilio_inbound_caller_label(caller_profile)
    text = (
        "Canal: Twilio phone call\n"
        f"CallSid: {call_sid}\n"
        f"From: {caller}\n"
        f"To: {called}\n\n"
        f"{caller_label}: "
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
            metadata={
                "reply": reply_text,
                "session_id": session_id,
                "caller_profile": {
                    "display_name": caller_profile.get("display_name"),
                    "known_contact": caller_profile.get("known_contact"),
                    "is_doctor": caller_profile.get("is_doctor"),
                },
            },
            contact_hint={
                "display_name": caller_profile.get("display_name") if caller_profile.get("known_contact") else "",
                "company": caller_profile.get("company_summary", ""),
                "notes": caller_profile.get("pending_summary") or caller_profile.get("relationship_summary", ""),
            },
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


def twilio_voice_fallback_twiml(handler, params=None, reason="", call_context=None, caller_profile=None):
    params = dict(params or {})
    base = twilio_public_base(handler)
    session_id = phone_session_id(params)
    caller = params.get("From", "")
    called = params.get("To", "")
    profile = caller_profile or {}
    label = twilio_inbound_caller_label(profile) if profile else "la persona que llama"
    known = bool(profile.get("known_contact") or profile.get("is_doctor")) and not twilio_label_looks_like_phone(label)
    if profile.get("is_doctor"):
        intro = (
            "Hola doctor, habla Kim. Mi canal de voz inteligente esta temporalmente en modo seguro, "
            "pero puedo tomar tu instruccion y dejarla registrada."
        )
        prompt = "Dime que necesitas que deje guardado o que revise al volver el canal realtime."
    elif known:
        intro = (
            f"Hola {label}, habla Kim, asistente del Dr. Yehoshua. "
            "Tengo el canal de voz inteligente en modo seguro, pero puedo tomar tu recado."
        )
        prompt = "Por favor dime en que puedo ayudarte y que mensaje quieres que le deje al doctor."
    else:
        intro = (
            "Hola, habla Kim, asistente del Dr. Yehoshua. En Ai People ayudamos con automatizacion con IA, "
            "consultoria tecnologica, procesos, branding y analisis financiero."
        )
        prompt = "Te puedo preguntar tu nombre, empresa y motivo de tu llamada?"
    event = {
        "session_id": session_id,
        "call_sid": params.get("CallSid", ""),
        "from": caller,
        "to": called,
        "context_id": (call_context or {}).get("id") or params.get("kim_context_id", ""),
        "reason": brief(reason, 500),
        "known_contact": known,
        "label": label,
    }
    append_memory("twilio_voice_fallback", event)
    notify_kim_live(
        "twilio_voice_fallback",
        "Twilio answered in safe mode",
        f"Llamada {params.get('CallSid', '') or session_id} atendida sin Realtime. {event['reason']}",
        severity="warning",
        metadata=event,
    )
    action = f"{base}/twilio/gather"
    return twiml_response(
        twilio_say(intro)
        +
        f'<Gather input="speech" language="es-MX" speechTimeout="auto" timeout="7" '
        f'action="{twiml_escape(action)}" method="POST">'
        + twilio_say(prompt)
        + "</Gather>"
        + twilio_say("Gracias. Dejo registrada la llamada para el doctor.")
    )


def twilio_voice_twiml(handler, params=None):
    params = dict(params or {})
    query_params = {key: values[-1] for key, values in urllib.parse.parse_qs(urllib.parse.urlparse(handler.path).query).items()}
    params.update({key: value for key, value in query_params.items() if value and key not in params})
    base = twilio_public_base(handler)
    session_id = phone_session_id(params)
    caller = params.get("From", "")
    called = params.get("To", "")
    default_from = normalize_phone_number(twilio_default_from_number())
    is_outbound_leg = default_from and normalize_phone_number(caller) == default_from
    caller_profile = {} if is_outbound_leg else twilio_inbound_caller_profile(caller, called)
    context_id = params.get("kim_context_id", "")
    call_context = load_twilio_call_context(call_sid=params.get("CallSid", ""), context_id=context_id)
    if not call_context and not is_outbound_leg:
        call_context = twilio_inbound_call_context(
            caller=caller,
            called=called,
            call_sid=params.get("CallSid", ""),
            profile=caller_profile,
        )
        context_id = store_twilio_call_context(call_context)
    elif call_context and not context_id:
        context_id = call_context.get("id") or call_context.get("context_block_id") or ""
    media_ws = twilio_media_ws_url(handler, params)
    realtime_health = twilio_realtime_health_status(max_age_seconds=300)
    if not realtime_health.get("available", True):
        return twilio_voice_fallback_twiml(
            handler,
            params={**params, "kim_context_id": context_id},
            reason=f"recent realtime health: {realtime_health.get('reason') or realtime_health.get('status')}",
            call_context=call_context,
            caller_profile=caller_profile,
        )
    run_background_task(
        "phone-call-started-memory",
        append_memory,
        "phone_call_started",
        {
            "session_id": session_id,
            "caller": caller,
            "called": called,
            "context_id": context_id,
            "has_call_context": bool(call_context),
            "caller_profile": {
                "display_name": caller_profile.get("display_name"),
                "known_contact": caller_profile.get("known_contact"),
                "is_doctor": caller_profile.get("is_doctor"),
                "pending_summary": brief(caller_profile.get("pending_summary"), 240),
            },
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
    try:
        reply = kim_phone_reply(user_text, caller=caller, called=called, session_id=session_id)
    except Exception as exc:
        reply = (
            "Recibi tu mensaje. En este momento tuve un problema temporal para responder con inteligencia completa, "
            "pero la llamada quedo registrada para el Dr. Yehoshua."
        )
        notify_kim_live(
            "twilio_gather_error",
            "Twilio gather saved without AI reply",
            brief(str(exc), 700),
            severity="warning",
            metadata={"session_id": session_id, "from": caller, "to": called},
        )
        append_memory(
            "twilio_gather_reply_error",
            {"session_id": session_id, "from": caller, "to": called, "error": brief(str(exc), 800)},
        )
    append_twilio_call_record(params, user_text=user_text, reply_text=reply)
    action = f"{base}/twilio/gather"
    again = "Puedes decir otra instruccion, o colgar si terminamos."
    return twiml_response(
        twilio_say(reply)
        +
        f'<Gather input="speech" language="es-MX" speechTimeout="auto" timeout="6" '
        f'action="{twiml_escape(action)}" method="POST">'
        + twilio_say(again)
        + "</Gather>"
        + twilio_say("Listo doctor. Corto la llamada y dejo memoria local.")
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
        status_updates = {
            "twilio_status": event.get("call_status", ""),
            "last_call_status": event.get("call_status", ""),
            "duration": event.get("duration", ""),
            "error_code": event.get("error_code", ""),
            "error_message": event.get("error_message", ""),
            "last_status_at": event.get("at", ""),
        }
        if event.get("call_status"):
            status_updates["status"] = event.get("call_status", "")
        if twilio_call_status_is_terminal(event.get("call_status", "")):
            status_updates["context_consumed_at"] = event.get("at", "")
            status_updates["context_invalidated_at"] = event.get("at", "")
        update_twilio_call_context(
            call_sid=event.get("call_sid", ""),
            updates=status_updates,
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
        try:
            record_twilio_call_attempt(event)
        except Exception as exc:
            append_memory(
                "twilio_call_attempt_callback_error",
                {"call_sid": event.get("call_sid", ""), "status": event.get("call_status", ""), "error": brief(str(exc), 800)},
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


def twilio_inbound_message_channel(params):
    values = " ".join(str(params.get(key, "")) for key in ["From", "To", "MessagingServiceSid"])
    return "whatsapp" if "whatsapp:" in values.lower() else "sms"


def twilio_message_response_twiml(text):
    return twiml_response(f"<Message>{twiml_escape(text)}</Message>") if text else twiml_response("")


def whatsapp_thread_id_for_phone(phone):
    digits = phone_digits(phone)
    return f"wa-{digits}" if digits else "wa-unknown"


def whatsapp_thread_json_paths(thread_id):
    name = f"{crm_slug(thread_id)}.json"
    return WHATSAPP_THREAD_DIR / name, RUNTIME_WHATSAPP_THREAD_DIR / name


def whatsapp_thread_markdown_paths(thread_id):
    name = f"{crm_slug(thread_id)}.md"
    return WHATSAPP_THREAD_DIR / name, RUNTIME_WHATSAPP_THREAD_DIR / name


def whatsapp_company_from_person(person):
    organization = person.get("organization") if isinstance(person, dict) else ""
    if isinstance(organization, dict):
        return str(organization.get("name") or organization.get("value") or "").strip()
    return str(organization or "").strip()


def whatsapp_contact_origin(person, local_contact, caller_profile):
    sources = []
    if isinstance(person, dict) and person.get("id"):
        sources.append("pipedrive")
    if isinstance(local_contact, dict) and local_contact.get("id"):
        sources.append("crm_local")
    if isinstance(caller_profile, dict) and (
        caller_profile.get("known_contact")
        or caller_profile.get("display_name")
        or caller_profile.get("knowledge_summary")
        or caller_profile.get("pending_summary")
    ):
        sources.append("person_context")
    return compact_unique(sources or ["unknown"], limit=4)


def whatsapp_contact_company_scope(person, local_contact, caller_profile):
    scope = []
    company_name = whatsapp_company_from_person(person)
    if not company_name and isinstance(local_contact, dict):
        company_name = str(local_contact.get("company") or local_contact.get("company_name") or "").strip()
    if not company_name and isinstance(caller_profile, dict):
        company_name = str(caller_profile.get("company_summary") or "").strip()
    if company_name:
        scope.append(company_name)
    fallback = ["AI People", "Tesca Elements", "Dr. Yehoshua"]
    if "ignis" in normalize_security_text(company_name):
        fallback.insert(2, "Ignis International")
    return compact_unique(scope + fallback, limit=6)


def whatsapp_contact_seller_mode(person, local_contact, caller_profile):
    if isinstance(caller_profile, dict) and caller_profile.get("is_doctor"):
        return "doctor_control"
    if (isinstance(person, dict) and person.get("id")) or (isinstance(local_contact, dict) and local_contact.get("id")):
        return "threaded_contact"
    return "seller_generalist"


def whatsapp_contact_knowledge_sources(person, local_contact, caller_profile):
    sources = []
    if isinstance(caller_profile, dict) and caller_profile.get("knowledge_summary"):
        sources.append("person_context")
    if isinstance(local_contact, dict) and local_contact.get("id"):
        sources.append("crm_local")
    if isinstance(person, dict) and person.get("id"):
        sources.append("pipedrive")
    sources.append("seller_pack_public")
    return compact_unique(sources, limit=6)


def whatsapp_thread_stats(thread):
    events = thread.get("events") if isinstance(thread.get("events"), list) else []
    inbound = [item for item in events if item.get("direction") == "inbound"]
    outbound = [item for item in events if item.get("direction") == "outbound"]
    latest_inbound = inbound[-1] if inbound else {}
    latest_outbound = outbound[-1] if outbound else {}
    return {
        "total_messages": len(events),
        "inbound_messages": len(inbound),
        "outbound_messages": len(outbound),
        "latest_inbound_at": latest_inbound.get("at") or "",
        "latest_outbound_at": latest_outbound.get("at") or "",
        "latest_inbound_preview": brief(latest_inbound.get("body") or latest_inbound.get("reply") or "", 180),
        "latest_outbound_preview": brief(latest_outbound.get("reply") or latest_outbound.get("body") or "", 180),
    }


def list_whatsapp_thread_summaries(limit=12):
    index = read_json_file_any([WHATSAPP_THREAD_INDEX, RUNTIME_WHATSAPP_THREAD_INDEX], {"threads": []})
    if not isinstance(index, dict):
        index = {"threads": []}
    rows = []
    for item in (index.get("threads") or [])[: max(1, int(limit or 12))]:
        if not isinstance(item, dict):
            continue
        thread_id = item.get("thread_id") or ""
        primary, runtime = whatsapp_thread_json_paths(thread_id)
        thread = read_json_file_any([primary, runtime], {})
        if not isinstance(thread, dict):
            thread = {}
        contact = thread.get("contact") if isinstance(thread.get("contact"), dict) else {}
        stats = whatsapp_thread_stats(thread)
        rows.append(
            {
                "thread_id": thread_id,
                "display_name": contact.get("display_name") or item.get("display_name") or thread_id,
                "phone": contact.get("phone") or item.get("phone") or "",
                "company": contact.get("company") or item.get("company") or "",
                "known_contact": bool(contact.get("known_contact") if contact else item.get("known_contact")),
                "origin": contact.get("contact_origin") or item.get("origin") or [],
                "origin_summary": contact.get("origin_summary") or item.get("origin_summary") or "",
                "seller_mode": contact.get("seller_mode") or item.get("seller_mode") or "",
                "company_scope": contact.get("company_scope") or item.get("company_scope") or [],
                "knowledge_sources": contact.get("knowledge_sources") or item.get("knowledge_sources") or [],
                "open_items": len([row for row in (thread.get("open_items") or []) if row.get("status") in ("open", "pending_review")]),
                "latest_at": thread.get("updated_at") or item.get("latest_at") or "",
                **stats,
            }
        )
    return rows


def whatsapp_overview_text(limit=12):
    rows = list_whatsapp_thread_summaries(limit=limit)
    if not rows:
        return "No hay hilos de WhatsApp registrados todavia."
    lines = [f"Hilos WhatsApp registrados: {len(rows)}."]
    for item in rows:
        name = item.get("display_name") or item.get("thread_id")
        latest = item.get("latest_at") or "sin fecha"
        counts = f"inbound={item.get('inbound_messages', 0)} outbound={item.get('outbound_messages', 0)} open={item.get('open_items', 0)}"
        preview = item.get("latest_inbound_preview") or item.get("latest_outbound_preview") or "sin mensaje reciente"
        lines.append(f"- {name} ({item.get('phone') or 'sin telefono'}) {counts} latest={latest} :: {preview}")
    return "\n".join(lines)


def seller_context_pack_for_prompt(limit=6400):
    payload = load_seller_context_pack_payload()
    if not payload:
        return "Paquete seller aun no cargado; usar informacion publica general de Ai People, Tesca Elements e Ignis sin inventar."
    lines = []
    for key in ["mission", "positioning", "voice_style", "priority_focus", "sales_method", "guardrails"]:
        value = payload.get(key)
        if isinstance(value, list):
            value = "; ".join(str(item) for item in value if item)
        if value:
            lines.append(f"{key}: {value}")
    top_collateral = payload.get("collateral") if isinstance(payload.get("collateral"), dict) else {}
    top_links = top_collateral.get("approved_links") if isinstance(top_collateral.get("approved_links"), list) else []
    if top_links:
        rendered_links = []
        for item in top_links[:6]:
            if isinstance(item, dict) and item.get("url"):
                rendered_links.append(f"{item.get('label') or 'link'}={item.get('url')}")
        if rendered_links:
            lines.append("Approved public links: " + "; ".join(rendered_links))
    if top_collateral.get("send_policy"):
        lines.append("Collateral send policy: " + brief(top_collateral.get("send_policy") or "", 360))
    companies = payload.get("companies") if isinstance(payload.get("companies"), dict) else {}
    for name, info in companies.items():
        if not isinstance(info, dict):
            continue
        summary = info.get("summary") or ""
        offers = info.get("offers") or []
        guardrails = info.get("guardrails") or []
        line = f"{name}: {summary}"
        if offers:
            line += " Servicios: " + "; ".join(str(item) for item in offers[:7])
        if guardrails:
            line += " Limites: " + "; ".join(str(item) for item in guardrails[:4])
        lines.append(line)
    dr = payload.get("dr_yehoshua") if isinstance(payload.get("dr_yehoshua"), dict) else {}
    if dr:
        lines.append("Dr Yehoshua: " + brief(dr.get("summary") or "", 520))
        if dr.get("public_bio"):
            lines.append("Dr Yehoshua public bio: " + brief(dr.get("public_bio") or "", 620))
        credibility = dr.get("credibility_points") if isinstance(dr.get("credibility_points"), list) else []
        if credibility:
            lines.append("Dr Yehoshua credibility points: " + "; ".join(str(item) for item in credibility[:6] if item))
    response_rules = payload.get("public_response_rules") if isinstance(payload.get("public_response_rules"), list) else []
    if response_rules:
        lines.append("Public response rules: " + "; ".join(str(item) for item in response_rules[:8] if item))
    public_knowledge = payload.get("public_knowledge") if isinstance(payload.get("public_knowledge"), dict) else {}
    for name, info in public_knowledge.items():
        if not isinstance(info, dict):
            continue
        summary = info.get("summary") or ""
        talking_points = info.get("talking_points") if isinstance(info.get("talking_points"), list) else []
        line = f"{name}: {summary}"
        if talking_points:
            line += " Points: " + "; ".join(str(item) for item in talking_points[:6] if item)
        lines.append(line)
    collateral = payload.get("collateral") if isinstance(payload.get("collateral"), dict) else {}
    links = collateral.get("approved_links") if isinstance(collateral.get("approved_links"), list) else []
    if links:
        rendered_links = []
        for item in links[:6]:
            if isinstance(item, dict) and item.get("url"):
                rendered_links.append(f"{item.get('label') or 'link'}={item.get('url')} ({item.get('use') or 'public link'})")
        if rendered_links:
            lines.append("Approved public links: " + "; ".join(rendered_links))
    documents = collateral.get("available_documents") if isinstance(collateral.get("available_documents"), list) else []
    if documents:
        rendered_docs = []
        for item in documents[:6]:
            if isinstance(item, dict):
                rendered_docs.append(f"{item.get('label')}: {item.get('status')}")
        lines.append("Available collateral docs: " + "; ".join(rendered_docs))
    if collateral.get("send_policy"):
        lines.append("Collateral send policy: " + brief(collateral.get("send_policy") or "", 420))
    orbit = payload.get("mu_kim_orbit") if isinstance(payload.get("mu_kim_orbit"), dict) else {}
    if orbit:
        lines.append("Modelo Mu/Kim/Orbit: " + brief(orbit.get("summary") or "", 520))
    return brief("\n".join(lines), limit)


def media_extension_for_type(content_type, url="", fallback=".bin"):
    mime = (content_type or "").split(";", 1)[0].strip().lower()
    guessed = mimetypes.guess_extension(mime) if mime else ""
    if guessed:
        return guessed
    path_ext = pathlib.PurePosixPath(urllib.parse.urlparse(url or "").path).suffix
    if path_ext and re.fullmatch(r"\.[A-Za-z0-9]{1,8}", path_ext):
        return path_ext.lower()
    return fallback


def whatsapp_media_is_audio(content_type, url=""):
    mime = (content_type or "").split(";", 1)[0].strip().lower()
    if mime.startswith("audio/"):
        return True
    suffix = pathlib.PurePosixPath(urllib.parse.urlparse(url or "").path).suffix.lower()
    return suffix in {".ogg", ".oga", ".mp3", ".mpeg", ".m4a", ".aac", ".amr", ".wav", ".webm", ".mp4"}


def twilio_download_media(media_url):
    if not str(media_url or "").startswith("http"):
        raise RuntimeError("MediaUrl de Twilio invalido.")
    headers = twilio_headers()
    headers.pop("X-Kim-Twilio-Auth-Mode", None)
    request = urllib.request.Request(media_url, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=90) as response:
        data = response.read()
        content_type = response.headers.get("Content-Type", "") or ""
    if not data:
        raise RuntimeError("Twilio media vacio.")
    return data, content_type


def whatsapp_media_paths(direction, thread_id, message_sid, index, content_type, media_url):
    date_slug = dt.datetime.now(ZoneInfo(DEFAULT_SCHEDULER_TIMEZONE)).strftime("%Y-%m-%d")
    ext = media_extension_for_type(content_type, media_url, fallback=".bin")
    base = f"{crm_slug(thread_id)}-{crm_slug(message_sid or 'message')}-{index}{ext}"
    return (
        WHATSAPP_MEDIA_DIR / direction / date_slug / base,
        RUNTIME_WHATSAPP_MEDIA_DIR / direction / date_slug / base,
    )


def process_whatsapp_inbound_media(event, thread_id):
    media_urls = event.get("media_urls") if isinstance(event.get("media_urls"), list) else []
    media_types = event.get("media_content_types") if isinstance(event.get("media_content_types"), list) else []
    if not media_urls:
        return {"items": [], "has_audio": False}
    items = []
    first_audio = None
    for index, media_url in enumerate(media_urls):
        content_type = media_types[index] if index < len(media_types) else ""
        item = {"index": index, "url": media_url, "content_type": content_type, "is_audio": whatsapp_media_is_audio(content_type, media_url)}
        try:
            data, detected_type = twilio_download_media(media_url)
            item["downloaded"] = True
            item["bytes"] = len(data)
            item["detected_content_type"] = detected_type
            primary, runtime = whatsapp_media_paths("inbound", thread_id, event.get("message_sid", ""), index, detected_type or content_type, media_url)
            item["stored_paths"] = write_bytes_file_both(primary, runtime, data)
            if item["is_audio"] and first_audio is None:
                transcription = openai_audio_transcribe(primary.name, data, detected_type or content_type)
                item["audio_transcript"] = transcription.get("text", "")
                item["transcription_model"] = transcription.get("model", "")
                first_audio = item
        except Exception as exc:
            item["error"] = brief(str(exc), 700)
            append_memory(
                "whatsapp_media_processing_error",
                {
                    "thread_id": thread_id,
                    "message_sid": event.get("message_sid", ""),
                    "media_url": media_url,
                    "content_type": content_type,
                    "error": item["error"],
                },
            )
        items.append(item)
    return {
        "items": items,
        "has_audio": any(item.get("is_audio") for item in items),
        "audio_transcript": (first_audio or {}).get("audio_transcript", ""),
        "transcription_model": (first_audio or {}).get("transcription_model", ""),
    }


def whatsapp_public_audio_url(filename):
    public_host = (load_keychain_secret("codex.kim.public_base_url", required=False) or "https://kim.aipeople.app").rstrip("/")
    return f"{public_host}{WHATSAPP_PUBLIC_AUDIO_PATH_PREFIX}/{urllib.parse.quote(pathlib.Path(filename).name)}"


def generate_whatsapp_reply_audio(text, session_id, voice=None):
    speech = openai_audio_speech(text, voice=voice)
    filename = f"{crm_slug(session_id or 'whatsapp-reply')}-{secrets.token_hex(3)}.mp3"
    public_path = WHATSAPP_PUBLIC_AUDIO_DIR / filename
    write_bytes_file(public_path, speech.get("data") or b"")
    archive_path = WHATSAPP_MEDIA_DIR / "outbound" / dt.datetime.now(ZoneInfo(DEFAULT_SCHEDULER_TIMEZONE)).strftime("%Y-%m-%d") / filename
    write_bytes_file(archive_path, speech.get("data") or b"")
    return {
        "url": whatsapp_public_audio_url(filename),
        "public_path": str(public_path),
        "archive_path": str(archive_path),
        "model": speech.get("model"),
        "voice": speech.get("voice"),
        "content_type": speech.get("content_type"),
    }


def public_whatsapp_audio_candidates(path):
    raw = urllib.parse.unquote(str(path or "").rsplit("/", 1)[-1])
    if not raw or not re.fullmatch(r"[A-Za-z0-9_.-]+", raw):
        return []
    return [WHATSAPP_PUBLIC_AUDIO_DIR / raw]


def doctor_public_availability_summary():
    payload = read_json_file_any([DOCTOR_AVAILABILITY, RUNTIME_DOCTOR_AVAILABILITY], {})
    if not isinstance(payload, dict) or not payload:
        return (
            "No tengo una agenda confirmada en tiempo real para afirmar si el doctor esta en reunion. "
            "Puedo tomar el recado, marcarlo como prioritario y pedir horario de seguimiento."
        )
    status = normalize_security_text(payload.get("status") or payload.get("availability") or "")
    busy_until = str(payload.get("busy_until") or payload.get("until") or "").strip()
    if busy_until:
        try:
            parsed = dt.datetime.fromisoformat(busy_until.replace("Z", "+00:00"))
            now = dt.datetime.now(parsed.tzinfo) if parsed.tzinfo else dt.datetime.now()
            if parsed > now:
                return "El doctor aparece ocupado por ahora. Puedo tomar el recado y dejarlo listo para seguimiento."
        except ValueError:
            pass
    public_summary = str(payload.get("public_summary") or payload.get("summary") or "").strip()
    if public_summary:
        return brief(public_summary, 300)
    if status in {"busy", "ocupado", "in_meeting", "meeting", "reunion"}:
        return "El doctor aparece ocupado por ahora. Puedo tomar el recado sin compartir detalles de su agenda."
    if status in {"available", "free", "disponible"}:
        return "El doctor aparece disponible o sin bloqueo publico confirmado. Puedo tomar el mensaje y pedir seguimiento."
    return (
        "No tengo una lectura confiable de agenda en este momento. "
        "Puedo tomar el recado y dejarlo priorizado para el doctor."
    )


def whatsapp_classify_intent(text):
    normalized = normalize_security_text(text)
    has_any = lambda words: any(word in normalized for word in words)
    asks_availability = has_any(
        [
            "esta en reunion",
            "estas en reunion",
            "esta ocupado",
            "estas ocupado",
            "esta disponible",
            "estas disponible",
            "puede hablar",
            "te puede llamar",
            "agenda",
            "calendario",
        ]
    )
    asks_status = has_any(["estatus", "status", "seguimiento", "pendiente", "como va", "actualizacion", "update"])
    leaves_message = has_any(["avisa", "dile", "informale", "recado", "mensaje para", "por favor dile"])
    asks_action = has_any(
        [
            "agenda",
            "agendar",
            "llamame",
            "llamar",
            "manda",
            "enviar",
            "revisa",
            "cambia",
            "actualiza",
            "crear",
            "tarea",
            "cotizacion",
            "propuesta",
            "urgente",
            "follow up",
            "follow-up",
        ]
    )
    return {
        "availability_request": asks_availability,
        "status_request": asks_status,
        "message_for_doctor": leaves_message,
        "actionable": asks_action or asks_status or leaves_message,
        "labels": [
            label
            for label, active in [
                ("availability_request", asks_availability),
                ("status_request", asks_status),
                ("message_for_doctor", leaves_message),
                ("actionable", asks_action),
            ]
            if active
        ],
    }


def whatsapp_thread_contact_profile(phone, person=None, called=""):
    normalized = twilio_lookup_phone_number(phone)
    person = person or {}
    caller_profile = twilio_inbound_caller_profile(normalized, called)
    local_contact = crm_find_contact_by_phone(normalized) if normalized else {}
    local_contact = local_contact or {}
    display_name = (
        str(person.get("name") or "").strip()
        or local_contact.get("display_name")
        or caller_profile.get("display_name")
        or normalized
        or "Contacto WhatsApp"
    )
    company = whatsapp_company_from_person(person) or caller_profile.get("company_summary") or ""
    origin = whatsapp_contact_origin(person, local_contact, caller_profile)
    company_scope = whatsapp_contact_company_scope(person, local_contact, caller_profile)
    seller_mode = whatsapp_contact_seller_mode(person, local_contact, caller_profile)
    knowledge_sources = whatsapp_contact_knowledge_sources(person, local_contact, caller_profile)
    notes = []
    if local_contact.get("notes"):
        notes.append(local_contact.get("notes"))
    if caller_profile.get("pending_summary"):
        notes.append("Pendientes propios: " + caller_profile.get("pending_summary"))
    return {
        "phone": normalized,
        "display_name": display_name,
        "company": company,
        "contact_id": local_contact.get("id", ""),
        "contact_type": local_contact.get("contact_type") or (caller_profile.get("relationship_summary") or ""),
        "pipedrive_person_id": str(person.get("id") or ""),
        "pipedrive_person_name": str(person.get("name") or ""),
        "known_contact": bool(person.get("id") or local_contact or caller_profile.get("known_contact")),
        "is_doctor": bool(caller_profile.get("is_doctor")),
        "contact_origin": origin,
        "origin_summary": ", ".join(origin),
        "seller_mode": seller_mode,
        "company_scope": company_scope,
        "company_scope_summary": ", ".join(company_scope),
        "knowledge_sources": knowledge_sources,
        "pending_summary": caller_profile.get("pending_summary") or "",
        "knowledge_summary": caller_profile.get("knowledge_summary") or "",
        "notes": compact_unique(notes, limit=6),
    }


def load_whatsapp_thread(phone, person=None, called=""):
    thread_id = whatsapp_thread_id_for_phone(phone)
    primary, runtime = whatsapp_thread_json_paths(thread_id)
    thread = read_json_file_any([primary, runtime], {})
    if not isinstance(thread, dict) or not thread:
        thread = {
            "thread_id": thread_id,
            "channel": "whatsapp",
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "privacy_scope": "single_contact",
            "status": "active",
            "contact": {},
            "summary": "",
            "open_items": [],
            "events": [],
        }
    contact = whatsapp_thread_contact_profile(phone, person=person, called=called)
    current_contact = thread.get("contact") if isinstance(thread.get("contact"), dict) else {}
    merged_contact = {**current_contact, **{key: value for key, value in contact.items() if value not in ("", None, [], {})}}
    thread["contact"] = merged_contact
    thread["updated_at"] = now_iso()
    return thread


def whatsapp_thread_markdown(thread):
    contact = thread.get("contact") or {}
    open_items = thread.get("open_items") or []
    events = thread.get("events") or []
    lines = [
        f"# WhatsApp Thread - {contact.get('display_name') or thread.get('thread_id')}",
        "",
        f"- Thread ID: {thread.get('thread_id')}",
        f"- Channel: {thread.get('channel') or 'whatsapp'}",
        f"- Phone: {contact.get('phone') or ''}",
        f"- Company: {contact.get('company') or ''}",
        f"- CRM contact: {contact.get('contact_id') or ''}",
        f"- Pipedrive person: {contact.get('pipedrive_person_id') or ''}",
        f"- Known contact: {contact.get('known_contact')}",
        f"- Origin: {contact.get('origin_summary') or ''}",
        f"- Seller mode: {contact.get('seller_mode') or ''}",
        f"- Company scope: {contact.get('company_scope_summary') or ''}",
        f"- Knowledge sources: {', '.join(contact.get('knowledge_sources') or [])}",
        f"- Privacy scope: {thread.get('privacy_scope') or 'single_contact'}",
        f"- Updated: {thread.get('updated_at')}",
        "",
        "## Secretary Rule",
        "",
        "Kim may discuss only this contact's own follow-up, public service information, and non-sensitive availability. "
        "Kim must not reveal third-party context, private agenda details, financial/private information, or the doctor's internal tasks.",
        "",
        "## Summary",
        "",
        thread.get("summary") or "No summary yet.",
        "",
        "## Open Items",
        "",
    ]
    if open_items:
        for item in open_items[-12:]:
            lines.append(f"- [{item.get('status') or 'open'}] {item.get('title') or item.get('body_preview') or item.get('intent')}")
    else:
        lines.append("- No open items captured yet.")
    lines.extend(["", "## Recent Events", ""])
    for item in events[-40:]:
        direction = item.get("direction") or ""
        label = "Contact" if direction == "inbound" else "Kim"
        if direction == "system":
            label = "System"
        lines.append(f"### {item.get('at') or ''} - {label}")
        lines.append("")
        if item.get("body"):
            lines.append(item.get("body"))
            lines.append("")
        if item.get("reply"):
            lines.append("Kim reply:")
            lines.append("")
            lines.append(item.get("reply"))
            lines.append("")
        if item.get("intent"):
            lines.append(f"Intent: {', '.join(item.get('intent') or [])}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def save_whatsapp_thread(thread):
    thread = dict(thread or {})
    events = thread.get("events") if isinstance(thread.get("events"), list) else []
    thread["events"] = events[-220:]
    thread["open_items"] = (thread.get("open_items") or [])[-80:]
    thread["updated_at"] = now_iso()
    thread_id = thread.get("thread_id") or whatsapp_thread_id_for_phone((thread.get("contact") or {}).get("phone"))
    thread["thread_id"] = thread_id
    primary_json, runtime_json = whatsapp_thread_json_paths(thread_id)
    primary_md, runtime_md = whatsapp_thread_markdown_paths(thread_id)
    written_json = write_json_file_both(primary_json, runtime_json, thread)
    markdown = whatsapp_thread_markdown(thread)
    written_md = write_text_file_both(primary_md, runtime_md, markdown)
    index = read_json_file_any([WHATSAPP_THREAD_INDEX, RUNTIME_WHATSAPP_THREAD_INDEX], {"threads": []})
    if not isinstance(index, dict):
        index = {"threads": []}
    threads = [item for item in index.get("threads", []) if item.get("thread_id") != thread_id]
    contact = thread.get("contact") or {}
    stats = whatsapp_thread_stats(thread)
    threads.append(
        {
            "thread_id": thread_id,
            "display_name": contact.get("display_name"),
            "phone": contact.get("phone"),
            "company": contact.get("company"),
            "known_contact": contact.get("known_contact"),
            "origin": contact.get("contact_origin") or [],
            "origin_summary": contact.get("origin_summary") or "",
            "pipedrive_person_id": contact.get("pipedrive_person_id"),
            "seller_mode": contact.get("seller_mode") or "",
            "company_scope": contact.get("company_scope") or [],
            "knowledge_sources": contact.get("knowledge_sources") or [],
            "latest_at": thread.get("updated_at"),
            "open_items": len([item for item in thread.get("open_items") or [] if item.get("status") in ("open", "pending_review")]),
            "markdown_path": str(primary_md),
            "runtime_markdown_path": str(runtime_md),
            **stats,
        }
    )
    threads.sort(key=lambda item: item.get("latest_at") or "", reverse=True)
    write_json_file_both(
        WHATSAPP_THREAD_INDEX,
        RUNTIME_WHATSAPP_THREAD_INDEX,
        {
            "updated_at": now_iso(),
            "count": len(threads),
            "purpose": "Indice de hilos conductores WhatsApp por persona/contacto.",
            "rule": "Antes de responder por WhatsApp, Kim debe cargar el thread_id exacto y no mezclar terceros.",
            "threads": threads[:500],
        },
    )
    return {"json": written_json, "markdown": written_md, "thread": thread}


def whatsapp_thread_recent_messages(thread, limit=6):
    rows = []
    for item in (thread.get("events") or [])[-limit:]:
        direction = item.get("direction") or ""
        speaker = "contact" if direction == "inbound" else "kim"
        if direction == "system":
            speaker = "system"
        text = item.get("body") or item.get("reply") or ""
        rows.append(
            {
                "at": item.get("at") or "",
                "direction": direction or "unknown",
                "speaker": speaker,
                "text": brief(text, 280),
                "status": item.get("status") or "",
                "intent": item.get("intent") or [],
            }
        )
    return rows


def whatsapp_threads_report(limit=8, thread_id="", phone=""):
    try:
        limit = max(1, min(int(limit or 8), 50))
    except (TypeError, ValueError):
        limit = 8
    index = read_json_file_any([WHATSAPP_THREAD_INDEX, RUNTIME_WHATSAPP_THREAD_INDEX], {"threads": []})
    threads = index.get("threads", []) if isinstance(index, dict) else []
    requested_thread_id = str(thread_id or "").strip()
    requested_phone = twilio_lookup_phone_number(phone or "")
    selected = []
    for item in threads:
        candidate_thread_id = str(item.get("thread_id") or "").strip()
        candidate_phone = twilio_lookup_phone_number(item.get("phone") or "")
        if requested_thread_id and candidate_thread_id != requested_thread_id:
            continue
        if requested_phone and candidate_phone != requested_phone:
            continue
        selected.append(item)
    if not requested_thread_id and not requested_phone:
        selected = threads[:limit]
    rows = []
    for meta in selected[:limit]:
        candidate_thread_id = str(meta.get("thread_id") or "").strip()
        primary_json, runtime_json = whatsapp_thread_json_paths(candidate_thread_id)
        thread = newest_json_payload([primary_json, runtime_json])
        if not isinstance(thread, dict):
            thread = {}
        contact = thread.get("contact") if isinstance(thread.get("contact"), dict) else {}
        rows.append(
            {
                "thread_id": candidate_thread_id,
                "display_name": contact.get("display_name") or meta.get("display_name") or "",
                "phone": contact.get("phone") or meta.get("phone") or "",
                "company": contact.get("company") or meta.get("company") or "",
                "known_contact": bool(contact.get("known_contact") or meta.get("known_contact")),
                "summary": thread.get("summary") or "",
                "open_items": thread.get("open_items") or [],
                "latest_at": thread.get("updated_at") or meta.get("latest_at") or "",
                "recent_messages": whatsapp_thread_recent_messages(thread, limit=6),
                "markdown_path": meta.get("markdown_path") or "",
            }
        )
    return {
        "ok": True,
        "count": len(threads),
        "returned": len(rows),
        "purpose": "Reporte rapido de hilos conductores de WhatsApp por contacto.",
        "filters": {
            "thread_id": requested_thread_id,
            "phone": requested_phone,
            "limit": limit,
        },
        "threads": rows,
    }


def load_whatsapp_thread_index():
    payload = read_json_file_any([WHATSAPP_THREAD_INDEX, RUNTIME_WHATSAPP_THREAD_INDEX], {"threads": []})
    if not isinstance(payload, dict):
        return {"threads": []}
    if not isinstance(payload.get("threads"), list):
        payload["threads"] = []
    return payload


def whatsapp_thread_matches_query(meta, query):
    if not query:
        return True
    normalized = normalize_security_text(query)
    if not normalized:
        return True
    fields = [
        meta.get("thread_id"),
        meta.get("display_name"),
        meta.get("phone"),
        meta.get("company"),
        meta.get("pipedrive_person_id"),
    ]
    blob = " ".join(str(item or "") for item in fields)
    return normalized in normalize_security_text(blob)


def whatsapp_recent_inbound_events(thread, limit=3):
    rows = []
    for item in reversed(thread.get("events") or []):
        if item.get("direction") != "inbound":
            continue
        body = str(item.get("body") or "").strip()
        if not body:
            continue
        rows.append(
            {
                "at": item.get("at") or "",
                "status": item.get("status") or "",
                "body_preview": brief(body, 280),
                "intent": item.get("intent") or [],
                "external_sid": item.get("external_sid") or "",
            }
        )
        if len(rows) >= limit:
            break
    rows.reverse()
    return rows


def twilio_whatsapp_report(parameters=None):
    parameters = parameters or {}
    limit = max(1, min(int(first_value(parameters, "limit", "page_size", default=10) or 10), 50))
    event_limit = max(1, min(int(first_value(parameters, "event_limit", "events", default=3) or 3), 8))
    query = str(first_value(parameters, "query", "q", "phone", "contact", "name", default="") or "").strip()
    actionable_only = boolish(first_value(parameters, "actionable_only", "open_only", "pending_only", default=False))
    index = load_whatsapp_thread_index()
    rows = []
    for meta in index.get("threads", []):
        if not isinstance(meta, dict) or not whatsapp_thread_matches_query(meta, query):
            continue
        if actionable_only and int(meta.get("open_items") or 0) <= 0:
            continue
        thread_id = str(meta.get("thread_id") or "").strip()
        primary, runtime = whatsapp_thread_json_paths(thread_id)
        thread = read_json_file_any([primary, runtime], {})
        if not isinstance(thread, dict):
            thread = {}
        contact = thread.get("contact") if isinstance(thread.get("contact"), dict) else {}
        open_items = thread.get("open_items") if isinstance(thread.get("open_items"), list) else []
        rows.append(
            {
                "thread_id": thread_id,
                "display_name": contact.get("display_name") or meta.get("display_name") or "",
                "phone": contact.get("phone") or meta.get("phone") or "",
                "company": contact.get("company") or meta.get("company") or "",
                "known_contact": bool(contact.get("known_contact") if contact else meta.get("known_contact")),
                "pipedrive_person_id": contact.get("pipedrive_person_id") or meta.get("pipedrive_person_id") or "",
                "latest_at": meta.get("latest_at") or thread.get("updated_at") or "",
                "summary": thread.get("summary") or "",
                "open_items_count": len([item for item in open_items if item.get("status") in ("open", "pending_review")]),
                "open_items": [
                    {
                        "status": item.get("status") or "",
                        "title": item.get("title") or item.get("body_preview") or "",
                        "created_at": item.get("created_at") or "",
                    }
                    for item in open_items[-5:]
                ],
                "recent_inbound": whatsapp_recent_inbound_events(thread, limit=event_limit),
            }
        )
        if len(rows) >= limit:
            break
    total_threads = len(index.get("threads", []))
    actionable_threads = len([item for item in index.get("threads", []) if int((item or {}).get("open_items") or 0) > 0])
    return {
        "ok": True,
        "provider": "twilio",
        "action": "whatsapp_report",
        "count": len(rows),
        "total_threads": total_threads,
        "actionable_threads": actionable_threads,
        "query": query,
        "actionable_only": actionable_only,
        "threads": rows,
        "message": (
            f"Reporte local de WhatsApp generado desde BIFROST ({len(rows)} hilo(s) devueltos, {total_threads} total). "
            "Se basa en hilos guardados localmente, no en listado historico directo de Twilio Conversations."
        ),
    }


def whatsapp_recent_history_for_prompt(thread, limit=8):
    rows = []
    for item in (thread.get("events") or [])[-limit:]:
        direction = item.get("direction") or ""
        speaker = "Contacto" if direction == "inbound" else "Kim"
        text = item.get("body") or item.get("reply") or ""
        if text:
            rows.append(f"{item.get('at') or ''} {speaker}: {brief(text, 260)}")
    return "\n".join(rows) or "Sin historial conversacional previo en este hilo."


def whatsapp_prepare_clickup_outbox(thread, event_entry, intent):
    if not intent.get("actionable"):
        return {}
    contact = thread.get("contact") or {}
    body = event_entry.get("body") or ""
    title_prefix = "WhatsApp seguimiento"
    if intent.get("availability_request"):
        title_prefix = "WhatsApp agenda/disponibilidad"
    elif intent.get("message_for_doctor"):
        title_prefix = "WhatsApp recado para doctor"
    title = brief(f"{title_prefix} - {contact.get('display_name') or contact.get('phone')}: {body}", 120)
    description = (
        f"Fuente: WhatsApp inbound\n"
        f"Thread ID: {thread.get('thread_id')}\n"
        f"Contacto: {contact.get('display_name') or ''}\n"
        f"Telefono: {contact.get('phone') or ''}\n"
        f"Empresa: {contact.get('company') or ''}\n"
        f"Pipedrive person_id: {contact.get('pipedrive_person_id') or ''}\n"
        f"MessageSid: {event_entry.get('external_sid') or ''}\n"
        f"Intent: {', '.join(intent.get('labels') or [])}\n\n"
        f"Mensaje:\n{body}\n\n"
        "Siguiente paso sugerido: revisar desde Kim Live y sincronizar a ClickUp si corresponde."
    )
    try:
        defaults = clickup_apply_operational_defaults(
            {
                "title": title,
                "description": description,
                "space_name": "Ai people",
                "list_name": "Client Follow-up",
                "contact_name": contact.get("display_name") or "",
                "company": contact.get("company") or "",
            }
        )
    except Exception as exc:
        defaults = {"title": title, "description": description, "routing_error": brief(str(exc), 320)}
    outbox = {
        "id": "WA-CLK-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S-") + secrets.token_hex(3).upper(),
        "at": now_iso(),
        "status": "pending_review",
        "provider": "clickup",
        "action": "create_task",
        "source": "whatsapp_thread",
        "thread_id": thread.get("thread_id"),
        "contact": contact,
        "intent": intent,
        "parameters": defaults,
        "message": body,
        "external_sid": event_entry.get("external_sid") or "",
        "sync_policy": "review_in_kim_live_before_external_write",
    }
    append_jsonl_any([WHATSAPP_CLICKUP_OUTBOX, RUNTIME_WHATSAPP_CLICKUP_OUTBOX], outbox)
    notify_kim_live(
        "whatsapp_clickup_outbox",
        "WhatsApp follow-up ready for ClickUp",
        f"{contact.get('display_name') or contact.get('phone')}: {brief(body, 220)}",
        severity="info",
        metadata={"outbox_id": outbox["id"], "thread_id": thread.get("thread_id")},
    )
    return outbox


def record_whatsapp_thread_event(event, person=None, direction="inbound", reply="", status="received", metadata=None):
    event = dict(event or {})
    sender = twilio_lookup_phone_number(event.get("from", ""))
    called = twilio_lookup_phone_number(event.get("to", ""))
    thread_phone = sender if direction == "inbound" else called
    thread = load_whatsapp_thread(thread_phone, person=person, called=called)
    media_urls = event.get("media_urls") if isinstance(event.get("media_urls"), list) else []
    body = (event.get("body") or "").strip()
    if not body and media_urls:
        body = f"Mensaje de WhatsApp con {len(media_urls)} archivo(s) adjuntos."
    if direction == "outbound":
        body = ""
    event_id = (
        event.get("message_sid")
        or event.get("send_sid")
        or event.get("sid")
        or f"{direction}-{dt.datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(3)}"
    )
    existing_ids = {str(item.get("event_id") or "") for item in thread.get("events") or []}
    if event_id in existing_ids:
        thread["_last_event_saved"] = False
        return thread
    intent = whatsapp_classify_intent(body if direction == "inbound" else reply or body)
    entry = {
        "event_id": event_id,
        "at": event.get("at") or now_iso(),
        "direction": direction,
        "status": status,
        "external_sid": event.get("message_sid") or event.get("send_sid") or event.get("sid") or "",
        "from": event.get("from", ""),
        "to": event.get("to", ""),
        "body": body,
        "reply": reply,
        "intent": intent.get("labels") or [],
        "metadata": {**(metadata or {}), "media_urls": media_urls},
    }
    thread.setdefault("events", []).append(entry)
    if body and direction == "inbound":
        thread["summary"] = brief(f"Ultimo mensaje de {thread.get('contact', {}).get('display_name') or sender}: {body}", 520)
        if intent.get("actionable"):
            thread.setdefault("open_items", []).append(
                {
                    "id": "WA-OPEN-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S-") + secrets.token_hex(3).upper(),
                    "created_at": now_iso(),
                    "status": "pending_review",
                    "intent": ", ".join(intent.get("labels") or []),
                    "title": brief(body, 120),
                    "body_preview": brief(body, 400),
                    "external_sid": entry.get("external_sid"),
                }
            )
            outbox = whatsapp_prepare_clickup_outbox(thread, entry, intent)
            if outbox:
                entry["clickup_outbox_id"] = outbox.get("id")
    elif reply and direction == "outbound":
        thread["summary"] = brief(f"Kim respondio por WhatsApp: {reply}", 520)
    save_whatsapp_thread(thread)
    append_memory(
        "whatsapp_thread_event",
        {
            "thread_id": thread.get("thread_id"),
            "direction": direction,
            "status": status,
            "event_id": event_id,
            "intent": intent.get("labels") or [],
            "body_preview": brief(body or reply, 300),
        },
    )
    thread["_last_event_saved"] = True
    thread["_last_event"] = entry
    return thread


def kim_whatsapp_reply(user_text, sender="", called="", session_id="", thread=None):
    clean = (user_text or "").strip()
    if not clean:
        return "Hola, soy Kim, asistente del Dr. Yehoshua. Recibi tu mensaje y lo dejo registrado para seguimiento."
    thread = thread or load_whatsapp_thread(sender, called=called)
    contact = thread.get("contact") or {}
    route = memory_router("classify_whatsapp", clean, session_id=session_id)
    intent = whatsapp_classify_intent(clean)
    availability = doctor_public_availability_summary()
    seller_context = seller_context_pack_for_prompt()
    seller_mode = contact.get("seller_mode") or ("threaded_contact" if contact.get("known_contact") else "seller_generalist")
    seller_focus = (
        "Este contacto ya tiene hilo conductor propio. Prioriza su historial, pendientes y knowledge especifico antes de usar el paquete seller general."
        if seller_mode == "threaded_contact"
        else "Este contacto no esta plenamente identificado. Entra en modo comercial generalista: primero AI People, luego Tesca Elements si aporta contexto, y usa la trayectoria del Dr. Yehoshua solo como respaldo breve. Tu objetivo inmediato es identificar nombre, empresa y necesidad."
    )
    if contact.get("is_doctor"):
        secretary_mode = (
            "Estas hablando por WhatsApp con el Dr Yehoshua. Puedes recibir instrucciones directas, "
            "guardar contexto y preparar acciones. Si algo requiere API externa sensible, no digas que ya se ejecuto "
            "salvo que exista resultado confirmado. Eres puente remoto hacia Kim Live: registra instrucciones, "
            "recados, tareas y contexto; notifica Kim Live; y deja preparado el siguiente paso para ejecucion o revision."
        )
    else:
        pending = contact.get("pending_summary") or "Sin pendientes propios sintetizados todavia."
        secretary_mode = (
            "Estas atendiendo WhatsApp como secretaria ejecutiva del Dr. Yehoshua. "
            "Usa solo el hilo de esta persona y su contexto propio. Puedes recibir informacion, tomar recados, "
            "dar seguimiento a tareas propias del contacto, explicar servicios generales de Ai People/Tesca/Ignis "
            "sin revelar informacion privada, responder preguntas publicas sobre la trayectoria general del Dr. Yehoshua, "
            "y responder disponibilidad publica de forma no sensible. "
            "No compartas nombres de reuniones, terceros, inversionistas, clientes, agenda privada, datos financieros "
            "ni pendientes generales del doctor. Si piden saber si el doctor esta en reunion, usa el resumen de "
            "disponibilidad publica y ofrece tomar recado o pedir horario. Si el contacto no esta plenamente "
            "identificado, pide nombre completo antes de compartir cualquier seguimiento. Si piden folletos, links o documentos, "
            "ofrece enviarlos solo desde el collateral aprobado y no digas que ya los enviaste sin confirmacion tecnica.\n"
            f"Contacto: {contact.get('display_name') or sender}; empresa={contact.get('company') or 'N/A'}; "
            f"conocido={contact.get('known_contact')}; Pipedrive={contact.get('pipedrive_person_id') or 'N/A'}.\n"
            f"Origen autorizado del hilo: {contact.get('origin_summary') or 'unknown'}.\n"
            f"Modo comercial: {seller_mode}.\n"
            f"Scope comercial permitido: {contact.get('company_scope_summary') or 'AI People, Tesca Elements, Dr. Yehoshua'}.\n"
            f"Fuentes de conocimiento cargadas: {', '.join(contact.get('knowledge_sources') or ['seller_pack_public'])}.\n"
            f"Politica secretaria/puente: {REMOTE_SECRETARY_BRIDGE_POLICY}\n"
            f"Politica relacion/buen nombre: {INBOUND_RELATIONSHIP_GOODWILL_POLICY}\n"
            f"Playbook ventas/RP a reunion: {WHATSAPP_SALES_PR_MEETING_PLAYBOOK}\n"
            f"Regla de enfoque: {seller_focus}\n"
            f"Pendientes propios conocidos: {pending}\n"
            f"Disponibilidad publica del doctor: {availability}\n"
            f"Knowledge especifico: {contact.get('knowledge_summary') or 'Sin knowledge especifico.'}\n"
            f"Paquete seller autorizado:\n{seller_context}"
        )
    prompt = (
        "Eres Kim Live respondiendo por WhatsApp. Responde en espanol mexicano, como una secretaria calida, "
        "profesional, femenina y discretamente seductora en el ritmo verbal. Usa 1 a 4 frases. "
        "Si preguntan por empresas, servicios, trayectoria o filosofia, da una respuesta breve con sustancia y ofrece link, folleto o cita. "
        "Escribe para que pueda leerse en voz alta con naturalidad. No uses markdown. No prometas acciones externas ya ejecutadas "
        "si solo dejaste una tarea o recado registrado.\n\n"
        f"{secretary_mode}\n\n"
        f"Thread ID: {thread.get('thread_id')}\n"
        f"Session: {session_id}\n"
        f"Ruta de memoria detectada: {route.get('route', {}).get('domain')}\n"
        f"Intent detectado: {', '.join(intent.get('labels') or []) or 'general'}\n\n"
        "Historial reciente del hilo:\n"
        f"{whatsapp_recent_history_for_prompt(thread)}\n\n"
        f"Mensaje entrante:\n{clean}"
    )
    try:
        response, model = openai_response_with_fallback(
            PHONE_REPLY_MODEL_CANDIDATES,
            {"input": prompt, "max_output_tokens": 260},
        )
        reply = output_text_from_response(response)
        if not reply:
            raise RuntimeError("Respuesta vacia.")
    except Exception as exc:
        reply = (
            "Hola, soy Kim, asistente del Dr. Yehoshua. Recibi tu mensaje y lo dejo registrado "
            "para darle seguimiento con el doctor."
        )
        append_memory(
            "whatsapp_reply_error",
            {"session_id": session_id, "thread_id": thread.get("thread_id"), "error": brief(str(exc), 500)},
        )
    append_memory(
        "whatsapp_reply_generated",
        {
            "session_id": session_id,
            "thread_id": thread.get("thread_id"),
            "contact": contact.get("display_name"),
            "user_text": brief(clean, 400),
            "reply": brief(reply, 500),
        },
    )
    return brief(reply, 900)


def twilio_whatsapp_async_reply(event, person):
    event = dict(event or {})
    person = dict(person or {})
    sender = twilio_lookup_phone_number(event.get("from", ""))
    called = twilio_lookup_phone_number(event.get("to", ""))
    message_sid = event.get("message_sid", "")
    session_id = "WA-" + (message_sid or dt.datetime.now().strftime("%Y%m%d%H%M%S"))
    media_urls = event.get("media_urls") if isinstance(event.get("media_urls"), list) else []
    body = (event.get("body") or "").strip()
    if not body:
        body = f"Mensaje de WhatsApp con {len(media_urls)} archivo(s) adjuntos." if media_urls else "Mensaje de WhatsApp sin texto."

    def worker():
        working_event = dict(event)
        body_for_reply = body
        media_processing = {}
        if media_urls:
            thread_id = whatsapp_thread_id_for_phone(sender)
            media_processing = process_whatsapp_inbound_media(working_event, thread_id)
            transcript = str(media_processing.get("audio_transcript") or "").strip()
            if transcript:
                body_for_reply = "Audio de WhatsApp transcrito: " + transcript
                working_event["body"] = body_for_reply
            elif media_processing.get("has_audio"):
                body_for_reply = (
                    "Mensaje de WhatsApp con audio adjunto. No se pudo transcribir automaticamente; "
                    "pedir al contacto que lo envie de nuevo o que escriba el punto principal."
                )
                working_event["body"] = body_for_reply
            working_event["media_processing"] = media_processing
        thread = record_whatsapp_thread_event(
            working_event,
            person=person,
            direction="inbound",
            status="received",
            metadata={"media_processing": media_processing} if media_processing else {},
        )
        try:
            reply = kim_whatsapp_reply(body_for_reply, sender=sender, called=called, session_id=session_id, thread=thread)
        except Exception as exc:
            reply = (
                "Hola, soy Kim, asistente del Dr. Yehoshua. Recibi tu mensaje y lo dejo registrado "
                "para darle seguimiento."
            )
            append_memory(
                "twilio_whatsapp_async_reply_error",
                {"from": sender, "message_sid": message_sid, "error": brief(str(exc), 500)},
            )
        reply_audio = {}
        if media_processing.get("audio_transcript"):
            try:
                reply_audio = generate_whatsapp_reply_audio(reply, session_id)
            except Exception as exc:
                reply_audio = {"error": brief(str(exc), 700)}
                append_memory(
                    "whatsapp_reply_audio_error",
                    {"from": sender, "message_sid": message_sid, "session_id": session_id, "error": reply_audio["error"]},
                )
        outbound_event = {
            "at": now_iso(),
            "provider": "twilio",
            "kind": "async_auto_reply",
            "channel": "whatsapp",
            "from": event.get("to", ""),
            "to": event.get("from", ""),
            "body": reply,
            "in_reply_to": message_sid,
            "pipedrive_person_id": person.get("id"),
            "pipedrive_person_name": person.get("name"),
            "reply_audio": reply_audio,
            "inbound_media_processing": media_processing,
        }
        try:
            send_parameters = {
                "to": sender,
                "body": reply,
                "contact_name": person.get("name", "") or thread.get("contact", {}).get("display_name") or sender,
                "pipedrive_person_id": person.get("id", ""),
                "relationship": "whatsapp conversation",
                "company": person.get("organization", ""),
                "objective": f"Responder WhatsApp inbound {message_sid}",
                "context_id": session_id,
                "allow_unknown_contact": True,
                "allow_unknown_reason": "WhatsApp inbound reply inside user-initiated conversation window.",
            }
            if reply_audio.get("url"):
                send_parameters["media_url"] = reply_audio["url"]
            send_result = twilio_send_message(
                send_parameters,
                confirm=True,
                channel="whatsapp",
            )
            outbound_event["send_sid"] = send_result.get("sid", "")
            outbound_event["send_status"] = send_result.get("status", "")
            outbound_event["send_error_code"] = send_result.get("error_code")
            outbound_event["send_error_message"] = send_result.get("error_message")
        except Exception as exc:
            outbound_event["send_error"] = brief(str(exc), 800)
            notify_kim_live(
                "twilio_whatsapp_async_reply_failed",
                "WhatsApp async reply failed",
                f"No pude responder WhatsApp a {sender}: {brief(str(exc), 240)}",
                severity="error",
                metadata=outbound_event,
            )
        record_whatsapp_thread_event(
            {
                "at": outbound_event.get("at"),
                "from": outbound_event.get("from"),
                "to": outbound_event.get("to"),
                "body": reply,
                "send_sid": outbound_event.get("send_sid") or outbound_event.get("in_reply_to"),
            },
            person=person,
            direction="outbound",
            reply=reply,
            status=outbound_event.get("send_status", "async_auto_reply"),
            metadata=outbound_event,
        )
        append_jsonl_any([TWILIO_SMS_LOG, RUNTIME_TWILIO_SMS_LOG], outbound_event)
        append_memory("twilio_whatsapp_async_auto_reply", outbound_event)
        crm_record_interaction(
            "whatsapp",
            "outbound",
            from_value=outbound_event.get("from", ""),
            to_value=outbound_event.get("to", ""),
            status=outbound_event.get("send_status", "async_auto_reply"),
            body=reply,
            external_sid=outbound_event.get("send_sid") or message_sid,
            metadata=outbound_event,
            contact_hint={
                "display_name": person.get("name", ""),
                "company": person.get("organization", ""),
                "notes": f"Pipedrive person_id={person.get('id')}.",
            },
        )

    threading.Thread(target=worker, name=f"kim-whatsapp-reply-{message_sid or secrets.token_hex(3)}", daemon=True).start()
    append_memory(
        "twilio_whatsapp_async_reply_started",
        {
            "from": sender,
            "to": called,
            "message_sid": message_sid,
            "session_id": session_id,
            "body_preview": brief(body, 400),
            "media_count": len(media_urls),
        },
    )
    return True


def twilio_whatsapp_auto_reply(params, event):
    sender = twilio_lookup_phone_number(event.get("from", ""))
    guard = pipedrive_registered_person_for_phone_fast(sender)
    if not guard.get("registered"):
        notify_kim_live(
            "twilio_whatsapp_unknown_inbound",
            "WhatsApp inbound from new contact",
            f"{sender} escribio por WhatsApp y Kim respondera en modo publico/comercial aunque no este en Pipedrive.",
            severity="info",
            metadata={
                "from": sender,
                "to": twilio_lookup_phone_number(event.get("to", "")),
                "message_sid": event.get("message_sid", ""),
                "reason": guard.get("reason"),
                "candidates": [
                    {"id": item.get("id"), "name": item.get("name"), "phone": item.get("phone")}
                    for item in (guard.get("candidates") or [])[:5]
                ],
            },
        )
        append_memory(
            "twilio_whatsapp_inbound_unknown_contact_allowed",
            {
                "from": sender,
                "message_sid": event.get("message_sid", ""),
                "body_preview": brief(event.get("body", ""), 400),
                "reason": guard.get("reason"),
                "message": guard.get("message"),
                "policy": "WhatsApp inbound may be answered using public seller pack and isolated thread memory.",
            },
        )
        twilio_whatsapp_async_reply(event, {})
        return ""
    twilio_whatsapp_async_reply(event, guard.get("person") or {})
    return ""


def kim_sms_reply(user_text, sender="", called="", session_id=""):
    clean = (user_text or "").strip()
    profile = twilio_inbound_caller_profile(sender, called)
    intent = whatsapp_classify_intent(clean)
    route = memory_router("classify_sms", clean, session_id=session_id)
    seller_context = seller_context_pack_for_prompt(limit=3400)
    if profile.get("is_doctor"):
        mode = (
            "Estas respondiendo SMS al Dr Yehoshua. Este SMS debe funcionar como canal remoto de emergencia hacia Kim Live. "
            "Recibe instrucciones, recados, tareas y contexto; deja registro en memoria; notifica Kim Live; y si algo requiere "
            "ejecucion por API o scheduler, indica que queda preparado/registrado, no que ya se ejecuto salvo confirmacion real."
        )
        fallback = "Recibido, doctor. Lo dejo registrado en Kim Live para seguimiento."
    else:
        mode = (
            "Estas respondiendo SMS como Kim, secretaria ejecutiva del Dr Yehoshua. Usa solo el hilo propio de este numero. "
            "Puedes tomar recados, preguntar disponibilidad publica sin revelar agenda privada, orientar clientes, desarrollar "
            "relacion comercial, explicar ofertas y servicios generales de AI People, Tesca Elements e Ignis, y proponer una cita. "
            "Si no conoces a la persona, pide nombre, empresa y necesidad antes de hablar de seguimientos. No reveles datos privados."
        )
        fallback = "Hola, soy Kim, asistente del Dr. Yehoshua. Recibi tu mensaje; dime tu nombre, empresa y como puedo ayudarte."
    prompt = (
        "Eres Kim respondiendo por SMS. Responde en espanol mexicano, breve, claro y profesional. "
        "Maximo 2 frases. No uses markdown. No prometas acciones externas no confirmadas.\n\n"
        f"{mode}\n\n"
        f"Politica secretaria/puente: {REMOTE_SECRETARY_BRIDGE_POLICY}\n\n"
        f"Politica relacion/buen nombre: {INBOUND_RELATIONSHIP_GOODWILL_POLICY}\n\n"
        f"Playbook ventas/RP a reunion: {WHATSAPP_SALES_PR_MEETING_PLAYBOOK}\n\n"
        f"Perfil: {profile.get('display_name')} | conocido={profile.get('known_contact')} | doctor={profile.get('is_doctor')} "
        f"| empresa={profile.get('company_summary') or 'N/A'} | relacion={profile.get('relationship_summary') or 'N/A'}\n"
        f"Pendientes propios: {profile.get('pending_summary') or 'Sin pendientes sintetizados.'}\n"
        f"Disponibilidad publica: {doctor_public_availability_summary()}\n"
        f"Ruta de memoria detectada: {route.get('route', {}).get('domain')}\n"
        f"Intent: {', '.join(intent.get('labels') or []) or 'general'}\n"
        f"Paquete seller publico:\n{seller_context}\n\n"
        f"SMS entrante:\n{clean or '(sin texto)'}"
    )
    try:
        response, _model = openai_response_with_fallback(
            PHONE_REPLY_MODEL_CANDIDATES,
            {"input": prompt, "max_output_tokens": 140},
        )
        reply = output_text_from_response(response) or fallback
    except Exception as exc:
        reply = fallback
        append_memory("sms_reply_error", {"session_id": session_id, "from": sender, "error": brief(str(exc), 500)})
    reply = brief(reply, 500)
    append_memory(
        "sms_reply_generated",
        {
            "session_id": session_id,
            "from": sender,
            "to": called,
            "is_doctor": profile.get("is_doctor"),
            "known_contact": profile.get("known_contact"),
            "intent": intent.get("labels") or [],
            "body_preview": brief(clean, 300),
            "reply": reply,
        },
    )
    notify_kim_live(
        "sms_inbound",
        "SMS inbound handled by Kim",
        f"{profile.get('display_name') or sender}: {brief(clean, 180)}",
        severity="info",
        metadata={
            "session_id": session_id,
            "from": sender,
            "to": called,
            "is_doctor": profile.get("is_doctor"),
            "known_contact": profile.get("known_contact"),
            "reply": reply,
        },
    )
    return reply


def twilio_sms_twiml(params):
    channel = twilio_inbound_message_channel(params)
    event = {
        "at": now_iso(),
        "provider": "twilio",
        "kind": f"inbound_{channel}",
        "channel": channel,
        "message_sid": params.get("MessageSid", "") or params.get("SmsSid", ""),
        "from": params.get("From", ""),
        "to": params.get("To", ""),
        "body": params.get("Body", ""),
        "num_media": params.get("NumMedia", ""),
    }
    try:
        media_count = int(event.get("num_media") or 0)
    except (TypeError, ValueError):
        media_count = 0
    event["media_urls"] = [
        params.get(f"MediaUrl{index}", "")
        for index in range(media_count)
        if params.get(f"MediaUrl{index}", "")
    ]
    event["media_content_types"] = [
        params.get(f"MediaContentType{index}", "")
        for index in range(media_count)
        if params.get(f"MediaContentType{index}", "")
    ]
    append_jsonl_any([TWILIO_SMS_LOG, RUNTIME_TWILIO_SMS_LOG], event)
    append_memory(f"twilio_inbound_{channel}", event)
    crm_record_interaction(
        channel,
        "inbound",
        from_value=event.get("from", ""),
        to_value=event.get("to", ""),
        status="received",
        body=event.get("body", ""),
        external_sid=event.get("message_sid", ""),
        metadata=event,
    )
    if channel == "whatsapp":
        return twilio_message_response_twiml(twilio_whatsapp_auto_reply(params, event))
    session_id = "SMS-" + (event.get("message_sid") or dt.datetime.now().strftime("%Y%m%d%H%M%S"))
    reply = kim_sms_reply(
        event.get("body", ""),
        sender=event.get("from", ""),
        called=event.get("to", ""),
        session_id=session_id,
    )
    outbound_event = {
        "at": now_iso(),
        "provider": "twilio",
        "kind": "inbound_sms_twiml_reply",
        "channel": "sms",
        "from": event.get("to", ""),
        "to": event.get("from", ""),
        "body": reply,
        "in_reply_to": event.get("message_sid", ""),
        "session_id": session_id,
    }
    append_jsonl_any([TWILIO_SMS_LOG, RUNTIME_TWILIO_SMS_LOG], outbound_event)
    crm_record_interaction(
        "sms",
        "outbound",
        from_value=outbound_event.get("from", ""),
        to_value=outbound_event.get("to", ""),
        status="twiml_reply",
        body=reply,
        external_sid=event.get("message_sid", ""),
        metadata=outbound_event,
    )
    return twilio_message_response_twiml(reply)


def realtime_session_config():
    local_context = context_brief()
    return {
        "session": {
            "type": "realtime",
            "model": REALTIME_MODEL,
            "instructions": (
                "Eres Kim, asistente personal de Dr Yehoshua. "
        f"{active_voice_style()} "
                "Habla siempre en femenino, en espanol mexicano, con tono calido, directo y util. "
                "Responde breve en conversacion viva. Si el doctor te dicta una "
                "tarea, confirma la accion y sugiere guardarla o ejecutarla desde Kim Live. "
                "Cierra siempre cada turno con una oracion completa; no dejes frases a medias. "
                "Si el doctor interrumpe o la respuesta anterior quedo cortada, retoma primero la idea pendiente "
                "en una frase breve y completa antes de cambiar de tema. "
                "Si necesitas datos actuales, investigacion externa o verificacion en internet, "
                "di brevemente que vas a buscar y llama la herramienta kim_research_web. "
                "Cuando uses investigacion web, conserva fuentes para anexarlas al reporte de llamada. "
                "Cuando el doctor suba archivos, el servidor crea fichas durables en BIFROST/MEMORY/knowledge y "
                "actualiza file_knowledge_index; si pregunta por archivos, TESCA, contratos, diagnosticos o algo "
                "ya cargado, primero usa kim_memory_search y esas fichas antes de pedir que repita informacion. "
                "Para reportes del Sr. Eli o cualquier reporte a cliente, NO uses precios recordados, "
                "precios de reportes anteriores ni cierres historicos como si fueran actuales. Antes de "
                "redactar cifras de precio actual llama kim_market_snapshot y solo usa current_price si "
                "current_price_validation.approved_for_client_report=true. Si no hay al menos dos fuentes "
                "frescas en rango, di que el precio no quedo validado y pide verificacion manual. "
                "Si el doctor pide redactar una carta, propuesta, reporte o documento, llama "
                "kim_draft_document. "
                "No digas que ves la camara, la pantalla o el iframe de TradingView si no recibiste "
                "una imagen o datos. Para mercado o grafica activa, usa kim_market_snapshot con EMAs "
                "personalizadas cuando el doctor las pida, incluyendo EMA34 por temporalidad, y analiza "
                "con esos datos cuantitativos; si hace falta lectura visual de velas, pide captura. "
                "Para ClickUp, Notion, Pipedrive, portafolio o correo, usa kim_api_bridge. Si dudas del formato, llama action=templates; "
                "para probar plantillas sin escribir ni enviar, llama action=self_test. "
                "y usa el template exacto. Para ClickUp no le pidas IDs al doctor: pasa el texto, nombre, descripcion, "
                "cliente o dominio, y el bridge usara el catalogo operativo para elegir team/space/list. "
                "Si el doctor te pide actuar de forma directa, puedes usar provider=all con action send_email, "
                "create_task, update_task, comment_task, create_page, send_portfolio_report, mark_spam, move_to_trash o archive_email; "
                "el servidor enruta a la API correcta. "
                "No digas que falta subject/title/list_id/parent_id sin haber llamado la herramienta: el bridge genera "
                "subjects/titles, enruta ClickUp y guarda Notion outbox local si falta parent. "
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
                "Para Zoom usa provider zoom: status, auth_url, list_users, list_meetings, create_meeting, create_and_send_invite, get_transcript o send_transcript. "
                "Si el prospecto quiere reunion con el Dr. Yehoshua, primero captura nombre, empresa, correo, zona horaria, objetivo y dos horarios posibles; "
                "si ya hay horario claro y pide mandar invitacion, prepara provider=zoom action=create_and_send_invite con topic/start_at/duration/timezone/agenda y whatsapp_to o email_to. "
                "Si solo pide crear reunion sin avisar al cliente, usa create_meeting. "
                "No digas que hay liga Zoom hasta que Zoom devuelva join_url. Si Zoom no esta autorizado, pide abrir /oauth/zoom/start. "
                "Si el doctor pide transcript, transcripcion, resumen de reunion Zoom o reenviarlo a cliente, usa get_transcript o send_transcript con meeting_id/meeting_uuid; "
                "Zoom solo entrega transcripts cuando hubo cloud recording con audio transcript habilitado y scope de recording/transcript, asi que no inventes contenido si el bridge dice que no existe. "
                "Para llamadas, SMS y WhatsApp usa provider twilio: status, list_numbers, send_sms, send_whatsapp, "
                "call_phone, call_report, latest_call, whatsapp_report, schedule_call o schedule_sms. SMS/WhatsApp/llamadas siempre se preparan con confirm=false "
                "y requieren confirmacion explicita antes de ejecutar, excepto send_whatsapp_report del portafolio Sr. Eli al WhatsApp Dubai del doctor. Regla dura: SMS, llamadas y WhatsApp proactivo solo pueden enviarse a personas registradas "
                "en Pipedrive con telefono exacto; si no existe la persona, primero prepara provider=pipedrive action=upsert_person y no envies el mensaje. "
                "Excepcion: si una persona escribe primero por WhatsApp, Kim puede responder aunque no este en CRM/Pipedrive, usando solo el paquete publico seller y el hilo aislado de ese numero; debe pedir nombre/empresa y no revelar seguimiento privado hasta identificarla. "
                "Si el doctor pide saber quien escribio por WhatsApp o que mensajes entraron, usa action=whatsapp_report; "
                "ese reporte sale de hilos guardados en BIFROST, no de un inbox remoto de Twilio. "
                "No uses allow_unknown_contact para saltarte mensajes proactivos; solo es valido para responder un WhatsApp inbound iniciado por el usuario. Si el doctor dice que revises como lo mando por WhatsApp, "
                "primero usa kim_memory_search sobre whatsapp_threads, person_contexts o transcripts para recuperar el formato y las correcciones recientes "
                "antes de contestar. Si el destino es el propio doctor y ya existe un hilo doctor_control/is_doctor o un person_context con ese numero, "
                "no pidas registrarlo otra vez, no digas que falta CRM/Pipedrive y no pidas PIN/frase salvo que una confirmacion real devuelva "
                "requires_security_phrase. Si el doctor pide el portafolio en 11 mensajes, devuelve o prepara una linea por orden y no lo mezcles "
                "en un solo bloque narrativo. Si llamas a una tercera persona, no basta con to: "
                "primero usa kim_person_context o kim_api_bridge provider=crm action=person_context con el nombre/telefono para consultar person_contexts, context blocks y transcripts; "
                "despues debes pasar contact_name, relationship, call_context, objective, questions/report_to_doctor y cualquier mensaje "
                "que el doctor quiera transmitir; ese contexto se inyecta al prompt telefonico. "
                "Si el doctor dice 'modo Naomi', 'modo Ilian' o 'abre el modo de X', llama kim_person_context con query=X, "
                "carga active_person como unico hilo aislado y responde 'Modo X cargado' con pendientes, ultimas interacciones y ruta de memoria. "
                "Ese modo es para supervision o simulacion; no mezcles contexto de terceros ni uses candidate_summaries como memoria activa. "
                "Si el doctor pregunta cuantas personas escribieron por WhatsApp, que mensajes hay o quiere revisar un hilo puntual, "
                "llama kim_whatsapp_threads antes de responder para contar contactos y leer snippets reales del hilo. "
                "Si el doctor dice 'haz esto a tal hora', 'recuérdame', 'manda este mensaje mañana' o algo equivalente, "
                "usa kim_api_bridge con provider=all action=schedule_action y target_provider/target_action/target_parameters. "
                "Ese scheduler vive dentro de Kim Live y no depende de Codex; acepta horarios como 'mañana a las 9', "
                "'hoy 5:30 pm', 'lunes a las 8' o 'en 2 horas'. "
                "Si el doctor pregunta que paso en una llamada o pide resumen/transcripcion, llama provider=twilio action=latest_call "
                "o action=call_report con phone/call_sid/context_id antes de responder; estos reportes incluyen llamadas no contestadas, busy, failed o sin audio. "
                "Si sospechas que faltan intentos viejos, usa provider=twilio action=sync_call_attempts con since/limit; esa accion no llama a nadie. "
                "para clientes/contactos usa provider crm: status, list_contacts, upsert_contact o record_note. "
                "Para lugares, rutas, direcciones o negocios fisicos usa provider=google_maps: find_place, geocode, route_distance o timezone; "
                "Google Maps es de consulta y puede generar cargos pequenos, asi que resume resultados utiles y no hagas busquedas repetidas innecesarias. "
                "Antes de llamar o escribir a un cliente, consulta CRM si tienes duda y guarda contactos relevantes en BIFROST/CRM. "
                "No esperes a que el doctor diga 'guarda esto' cuando el contexto sea claro: si detectas datos estables de cliente, "
                "prepara actualizar CRM; si detectas un pendiente concreto, prepara tarea ClickUp; si detectas conocimiento reutilizable, "
                "apoyate en la revision bibliotecaria y en memoria literal. "
                "si Twilio responde 401, pide Auth Token correcto o API Key SID que empieza con SK. "
                "Si falta subject/title/name, usa un subject claro segun la conversacion. Enviar correo siempre requiere confirm=false, "
                "confirmacion explicita del doctor y luego confirm_prepared o confirm=true. Para Gmail, usa provider gmail en modo "
                "solo lectura: status, profile, list_messages o get_message. Si falta autorizacion OAuth, "
                "entrega el link de autorizacion y no inventes correos. "
                "Para portafolios de Ignis Stock Financials, usa kim_portfolio_record. Si el doctor pide "
                "'enviame el portafolio actualizado', 'manda el portafolio' o algo equivalente, llama "
                "primero kim_paper_trade action=sync para evaluar si alguna orden paper pendiente ya cruzo "
                "precio validado; despues llama "
                "kim_portfolio_record con action=send_whatsapp_report; por defecto lo envia al WhatsApp Dubai del doctor "
                "sin PIN ni confirmacion. Si solo pregunta por el portafolio o cuales ordenes ya entraron, llama "
                "kim_paper_trade action=sync y luego kim_portfolio_record con action=client_report. El formato por defecto es monto invertido, "
                "precio de entrada, precio actual validado y frase clara: 'Estamos por debajo por -X%' o "
                "'Estamos en ganancia por +X%'. Ordena el reporte para cliente de mayor perdida a mejor resultado; "
                "las ordenes pendientes van al final, marcadas como pendientes, con "
                "frase de distancia contra precio actual. No menciones unidades "
                "salvo que el doctor las pida. Para ordenes pendientes de compra, indica si el precio actual "
                "ya toco la entrada o sigue por encima; su distancia vs entrada no es P/L ni ganancia. Si el doctor pide reporte fundamental, catalizadores, "
                "oportunidades o vision macro del Sr. Eli, llama kim_portfolio_record con action=fundamental_report; "
                "ese reporte no envia WhatsApp por defecto y debe incluir fuentes validadas, catalizadores internacionales, "
                "narrativas cripto populares, oportunidades, riesgos e invalidaciones. No inventes catalizadores sin fuente reciente. Guarda consultas "
                "como record_consultation; solo registra record_final_change o add_transaction cuando el "
                "doctor diga que es cambio final, operacion final, compra final, venta final o equivalente. "
                "Para cancelar o sustituir una orden pendiente, usa replace_draft_order o cancel_transaction; "
                "no intentes simular una cancelacion creando varias notas sueltas. Si el doctor dice refuerzo, "
                "aglomera, promedia, agrega a la misma moneda o conserva una orden principal con subordenes, usa "
                "kim_portfolio_record action=aggregate_order con canonical_order, symbol y members. El doctor decide "
                "que ID canonico sobrevive; el promedio se calcula por costo total / unidades totales. "
                "Para nuevas ordenes paper del Sr. Eli o pendientes que deben ejecutarse cuando el precio toque, usa "
                "kim_paper_trade: place_order, cancel_order, status o sync. Estas son operaciones simuladas locales; TradingView "
                "solo manda alertas por webhook y no es fuente contable. Nunca digas que se coloco una orden en TradingView Paper Trading; "
                "di que quedo registrada en Kim Paper Broker. place_order y cancel_order requieren confirmacion humana. "
                "Si el doctor pide promedio ponderado, o dice 'solo numeros y operaciones', usa "
                "kim_portfolio_record action=weighted_average_breakdown para leer los tramos reales del ledger "
                "y no calcularlo mentalmente. Una correccion "
                "de precio, monto o aglomeracion no es venta, retiro ni devolucion salvo que el doctor diga literalmente "
                "vendimos, retirar, retiro, devolucion o venta final. Si el doctor dice que una orden ya se ejecuto, "
                "ya entro, ya no esta pendiente o quedo corriendo, usa kim_portfolio_record action=execute_pending_order "
                "con symbol, gross_amount y price; esa accion prepara confirmacion antes de volverla posicion activa. "
                "No tomes final_changes, rebalance ni texto libre como fuente contable si contradicen transactions, positions "
                "u order_aggregations. Si ves final+draft+void mezclados para la misma moneda, di explicitamente que hay "
                "discrepancia de ledger y no calcules promedio, ganancia neta ni venta asumida hasta confirmar el tramo canonico. "
                "Si el doctor dice que una posicion se vendio, usa kim_portfolio_record action=sell_position con symbol, "
                "entry_price, sell_price, invested_usd y/o quantity. La venta debe pedir PIN/frase antes de ejecutarse "
                "y debe calcular venta bruta, P/L bruto, fee operativo de 1.2% sobre el monto original/fee_base y P/L neto. "
                "Para preguntas de memoria o contexto, primero usa kim_memory_search para consultar transcripts "
                "literales y cita snippets/rutas como fuente primaria; los resumenes son derivados. Usa "
                "kim_memory_router solo para decidir dominio cuando no sepas si va a portafolio, tareas, CRM, "
                "voz remota o memoria general. No intentes cargar todo BIFROST. Si el doctor pregunta por la "
                "version de Kim Live, usa la version viva del backend incluida en el contexto; si ves notas "
                "historicas como 1.5.43 o 1.5.45, aclara que son hitos viejos y no el estado actual. "
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
                        "Lee o modifica ClickUp/Notion/Pipedrive, lee Gmail, maneja correo Hostinger, CRM local, Zoom, portafolio Ignis, prepara Twilio llamadas/SMS/WhatsApp y consulta reportes/transcripciones de llamadas desde Kim Live. Las operaciones de escritura "
                        "requieren confirmacion explicita del doctor y confirm=true."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "provider": {
                                "type": "string",
                                "description": "Proveedor: clickup, notion, pipedrive, gmail, google_maps, hostinger_mail, zoom, portfolio, twilio, scheduler, crm o all.",
                            },
                            "action": {
                                "type": "string",
                                "description": (
                                    "Accion. ClickUp: status, inventory, list_spaces, list_folders, "
                                    "list_lists, list_tasks, get_task, create_folder, create_list, "
                                    "create_task, update_task, comment_task. Notion: status, search, "
                                    "get_page, create_page, update_page_properties; para reuniones usa agent_action schedule_meeting "
                                    "o create_page con start_at/end_at/meeting_type hacia la base Reuniones. Templates: templates, self_test. Gmail: status, auth_url, "
                                    "profile, list_messages, get_message. Hostinger Mail: status, list_mailboxes, "
                                    "list_folders, list_messages, search_messages, get_message, draft_email, draft_reply, "
                                    "send_email, reply_email, move_message, mark_spam, move_to_trash, archive_message. "
                                    "Zoom: status, auth_url, list_users, list_meetings, create_meeting, create_and_send_invite, get_transcript, send_transcript. "
                                    "Google Maps: status, validate_key, find_place, geocode, route_distance, timezone. "
                                    "Pipedrive: status, search_persons, list_persons, get_person, upsert_person, list_deals, create_deal, update_deal, create_activity, create_note. "
                                    "Portfolio: client_report, fundamental_report, send_whatsapp_report, aggregate_order, execute_pending_order, sell_position. "
                                    "Paper Broker: status, preview, place_order, cancel_order, sync. "
                                    "Twilio: status, list_numbers, send_sms, send_whatsapp, call_phone, call_report, latest_call, whatsapp_report, sync_call_attempts, schedule_call, schedule_sms. "
                                    "Scheduler: schedule_action, list_schedules, cancel_schedule. "
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
                                "description": "Fuentes de precio a comparar: binance, mexc, bybit, kucoin, coinmarketcap, coingecko.",
                            },
                        },
                    },
                },
                {
                    "type": "function",
                    "name": "kim_portfolio_record",
                    "description": "Registra, consulta o envia por WhatsApp el portafolio Sr. Eli 2026 en BIFROST local.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                    "description": "status, summary, client_report, weighted_average_breakdown, fundamental_report, send_whatsapp_report, init, record_consultation, record_final_change, add_transaction, cancel_transaction, replace_draft_order, aggregate_order o set_position.",
                            },
                            "parameters": {
                                "type": "object",
                                "description": (
                                    "Campos de la accion. record_consultation acepta symbol, interval, question, "
                                    "snapshot_json, analysis, decision, is_final. record_final_change requiere summary. "
                                    "add_transaction requiere symbol y side. cancel_transaction acepta transaction_id o symbol. "
                                    "replace_draft_order requiere old_symbol, new_symbol, price y gross_amount. "
                                    "aggregate_order requiere canonical_order, symbol y members; members puede incluir member_order, source_order, amount_usd, price y quantity. "
                                    "weighted_average_breakdown acepta symbol y canonical_order para devolver tramos, unidades y operaciones exactas del promedio ponderado. "
                                    "client_report acepta include_units=true si el doctor las pide; por defecto devuelve "
                                    "monto invertido, entrada, precio actual validado, variacion porcentual y estado de ordenes pendientes. "
                                    "fundamental_report genera analisis con fuentes, catalizadores internacionales, narrativas cripto populares, oportunidades y riesgos, sin enviar mensajes por defecto. "
                                    "send_whatsapp_report calcula y manda lineas separadas al WhatsApp Dubai del doctor por defecto; "
                                    "para probar sin enviar usa dry_run=true."
                                ),
                            },
                        },
                        "required": ["action"],
                    },
                },
                {
                    "type": "function",
                    "name": "kim_paper_trade",
                    "description": "Administra el broker paper simulado local del Sr. Eli: ordenes pendientes, fills por precio validado, cancelaciones y alertas TradingView.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "status, preview, place_order, cancel_order o sync. place_order/cancel_order preparan confirmacion; sync evalua pendientes con precios frescos.",
                            },
                            "parameters": {
                                "type": "object",
                                "description": "place_order: symbol, side BUY/SELL, amount_usd, limit_price, notes. cancel_order: order_id o symbol. sync: symbol opcional.",
                            },
                            "confirm": {
                                "type": "boolean",
                                "description": "true solo despues de confirmacion explicita del doctor.",
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
                {
                    "type": "function",
                    "name": "kim_memory_search",
                    "description": "Busca en transcripts literales guardados de Kim Live/Twilio y devuelve snippets con rutas para sintetizar desde fuente primaria.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Tema, palabra clave o pregunta a buscar en transcripts.",
                            },
                            "session_id": {
                                "type": "string",
                                "description": "Opcional: abrir una sesion exacta si ya se conoce su ID.",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Numero maximo de conversaciones a devolver.",
                            },
                        },
                    },
                },
                {
                    "type": "function",
                    "name": "kim_person_context",
                    "description": "Carga el hilo aislado de una persona desde BIFROST/CRM para modo Naomi/Ilian, supervision de llamadas, pendientes y transcripts.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Nombre, alias, telefono o empresa de la persona. Ejemplos: Naomi, Nomi, Ilian.",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Numero maximo de personas candidatas. Usa 1 salvo que el doctor pida comparar candidatos.",
                            },
                        },
                        "required": ["query"],
                    },
                },
                {
                    "type": "function",
                    "name": "kim_whatsapp_threads",
                    "description": "Lista hilos conductores de WhatsApp y devuelve snippets reales de mensajes recientes por contacto.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Numero maximo de hilos a devolver.",
                            },
                            "thread_id": {
                                "type": "string",
                                "description": "Opcional: thread_id exacto como wa-52155....",
                            },
                            "phone": {
                                "type": "string",
                                "description": "Opcional: telefono para ubicar el hilo exacto.",
                            },
                        },
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
                    "voice": active_realtime_voice(),
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


def crypto_base_symbols(symbols):
    clean = []
    seen = set()
    for symbol in symbols or []:
        _, _, base, _ = normalize_crypto_ticker(str(symbol or ""))
        if base and base not in seen:
            clean.append(base)
            seen.add(base)
    return clean


def market_batch_cache_is_fresh(cache, key):
    if cache.get("key") != key:
        return False
    loaded_at = float(cache.get("loaded_at") or 0)
    return loaded_at > 0 and (time.time() - loaded_at) <= MARKET_PRICE_BATCH_CACHE_TTL_SECONDS


def clear_market_price_caches(reason="manual_refresh"):
    COINGECKO_BATCH_PRICE_CACHE.clear()
    COINGECKO_BATCH_PRICE_CACHE.update({"key": "", "loaded_at": 0.0, "items": {}})
    COINMARKETCAP_BATCH_PRICE_CACHE.clear()
    COINMARKETCAP_BATCH_PRICE_CACHE.update({"key": "", "loaded_at": 0.0, "items": {}})
    event = {"ok": True, "provider": "portfolio", "action": "refresh_prices", "reason": reason, "cleared_at": now_iso()}
    append_memory("market_price_cache_cleared", event)
    return event


def fetch_coingecko_prices_batch(bases):
    clean_bases = [str(base or "").strip().upper() for base in bases or [] if str(base or "").strip()]
    id_pairs = [(base, COINGECKO_IDS_BY_SYMBOL.get(base)) for base in clean_bases]
    id_pairs = [(base, coin_id) for base, coin_id in id_pairs if coin_id]
    if not id_pairs:
        return {}
    cache_key = ",".join(sorted({coin_id for _, coin_id in id_pairs}))
    if market_batch_cache_is_fresh(COINGECKO_BATCH_PRICE_CACHE, cache_key):
        return dict(COINGECKO_BATCH_PRICE_CACHE.get("items") or {})
    payload = api_json_request(
        "https://api.coingecko.com",
        "/api/v3/simple/price",
        {},
        params={
            "ids": ",".join(dict.fromkeys(coin_id for _, coin_id in id_pairs)),
            "vs_currencies": "usd",
            "include_last_updated_at": "true",
            "precision": "full",
        },
        timeout=20,
    )
    items = {}
    for base, coin_id in id_pairs:
        item = payload.get(coin_id) or {}
        price = item.get("usd")
        if price is None:
            continue
        items[base] = provider_price(
            "coingecko",
            price,
            updated_at=item.get("last_updated_at"),
            stale_after=MARKET_PRICE_MAX_AGE_SECONDS,
            extra={"coin_id": coin_id, "symbol": base},
        )
    COINGECKO_BATCH_PRICE_CACHE.update({"key": cache_key, "loaded_at": time.time(), "items": dict(items)})
    return items


def fetch_coinmarketcap_prices_batch(bases):
    clean_bases = [str(base or "").strip().upper() for base in bases or [] if str(base or "").strip()]
    clean_bases = list(dict.fromkeys(clean_bases))
    if not clean_bases:
        return {}
    api_key = load_keychain_secret(COINMARKETCAP_KEYCHAIN_SERVICE, required=False)
    if not api_key:
        raise RuntimeError("Falta API key de CoinMarketCap en Keychain.")
    cache_key = ",".join(sorted(clean_bases))
    if market_batch_cache_is_fresh(COINMARKETCAP_BATCH_PRICE_CACHE, cache_key):
        return dict(COINMARKETCAP_BATCH_PRICE_CACHE.get("items") or {})
    payload = api_json_request(
        "https://pro-api.coinmarketcap.com",
        "/v3/cryptocurrency/quotes/latest",
        {"X-CMC_PRO_API_KEY": api_key},
        params={"symbol": ",".join(clean_bases), "convert": "USD"},
        timeout=20,
    )
    data = payload.get("data") or {}
    rows_by_symbol = {}
    if isinstance(data, list):
        for row in data:
            rows_by_symbol.setdefault(str(row.get("symbol") or "").upper(), row)
    elif isinstance(data, dict):
        for key, value in data.items():
            symbol = str(key or "").upper()
            row = value[0] if isinstance(value, list) and value else value if isinstance(value, dict) else {}
            if isinstance(row, dict):
                rows_by_symbol.setdefault(str(row.get("symbol") or symbol).upper(), row)
    items = {}
    for base in clean_bases:
        row = rows_by_symbol.get(base) or {}
        quote = (row.get("quote") or {}).get("USD") or {}
        price = quote.get("price")
        if price is None:
            continue
        items[base] = provider_price(
            "coinmarketcap",
            price,
            updated_at=quote.get("last_updated") or row.get("last_updated"),
            stale_after=MARKET_PRICE_MAX_AGE_SECONDS,
            extra={"symbol": base, "cmc_id": row.get("id"), "name": row.get("name")},
        )
    COINMARKETCAP_BATCH_PRICE_CACHE.update({"key": cache_key, "loaded_at": time.time(), "items": dict(items)})
    return items


def warm_market_price_sources(symbols, providers=None):
    requested = {str(provider or "").strip().lower() for provider in (providers or [])}
    bases = crypto_base_symbols(symbols)
    warmed = {"coingecko": False, "coinmarketcap": False, "failures": []}
    if not requested or "coingecko" in requested:
        try:
            fetch_coingecko_prices_batch(bases)
            warmed["coingecko"] = True
        except Exception as exc:
            warmed["failures"].append({"provider": "coingecko", "error": brief(str(exc), 260)})
    if "coinmarketcap" in requested:
        try:
            fetch_coinmarketcap_prices_batch(bases)
            warmed["coinmarketcap"] = True
        except Exception as exc:
            warmed["failures"].append({"provider": "coinmarketcap", "error": brief(str(exc), 260)})
    return warmed


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


def fetch_mexc_spot_price(ticker):
    payload = api_json_request(
        "https://api.mexc.com",
        "/api/v3/ticker/price",
        {},
        params={"symbol": ticker},
        timeout=20,
    )
    price = payload.get("price")
    if price is None:
        raise RuntimeError("MEXC no devolvio precio spot.")
    return provider_price("mexc_spot", price, extra={"symbol": ticker})


def fetch_bybit_spot_price(ticker):
    payload = api_json_request(
        "https://api.bybit.com",
        "/v5/market/tickers",
        {},
        params={"category": "spot", "symbol": ticker},
        timeout=20,
    )
    rows = (payload.get("result") or {}).get("list") or []
    row = rows[0] if rows else {}
    price = row.get("lastPrice")
    if price is None:
        raise RuntimeError("Bybit no devolvio precio spot.")
    return provider_price("bybit_spot", price, extra={"symbol": ticker})


def fetch_kucoin_spot_price(ticker):
    _, normalized_ticker, base, quote = normalize_crypto_ticker(ticker)
    pair = f"{base}-{quote if quote != 'USD' else 'USDT'}"
    payload = api_json_request(
        "https://api.kucoin.com",
        "/api/v1/market/orderbook/level1",
        {},
        params={"symbol": pair},
        timeout=20,
    )
    price = (payload.get("data") or {}).get("price")
    if price is None:
        raise RuntimeError(f"KuCoin no devolvio precio spot para {pair}.")
    return provider_price("kucoin_spot", price, extra={"symbol": normalized_ticker, "pair": pair})


def fetch_coingecko_price(base):
    coin_id = COINGECKO_IDS_BY_SYMBOL.get(base)
    if not coin_id:
        raise RuntimeError(f"No tengo CoinGecko API ID para {base}.")
    cached = (COINGECKO_BATCH_PRICE_CACHE.get("items") or {}).get(base)
    if cached and (time.time() - float(COINGECKO_BATCH_PRICE_CACHE.get("loaded_at") or 0)) <= MARKET_PRICE_BATCH_CACHE_TTL_SECONDS:
        return cached
    fetched = fetch_coingecko_prices_batch([base]).get(base)
    if not fetched:
        raise RuntimeError(f"CoinGecko no devolvio precio USD para {coin_id}.")
    return fetched


def fetch_coinmarketcap_price(base):
    cached = (COINMARKETCAP_BATCH_PRICE_CACHE.get("items") or {}).get(base)
    if cached and (time.time() - float(COINMARKETCAP_BATCH_PRICE_CACHE.get("loaded_at") or 0)) <= MARKET_PRICE_BATCH_CACHE_TTL_SECONDS:
        return cached
    fetched = fetch_coinmarketcap_prices_batch([base]).get(base)
    if not fetched:
        raise RuntimeError(f"CoinMarketCap no devolvio precio USD para {base}.")
    return fetched


def validate_market_prices(symbol, providers=None):
    exchange, ticker, base, quote = normalize_crypto_ticker(symbol)
    requested = providers or ["binance", "mexc", "bybit"]
    provider_calls = {
        "binance": lambda: fetch_binance_spot_price(ticker),
        "mexc": lambda: fetch_mexc_spot_price(ticker),
        "bybit": lambda: fetch_bybit_spot_price(ticker),
        "kucoin": lambda: fetch_kucoin_spot_price(ticker),
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


def format_usd_amount(value):
    if value is None:
        return None
    value = float(value)
    if value.is_integer():
        return str(int(value))
    text = f"{value:.2f}"
    return text.rstrip("0").rstrip(".")


def signed_usd_text(value):
    if value is None:
        return "N/D"
    value = float(value)
    sign = "+" if value >= 0 else "-"
    return f"{sign}{format_usd_amount(abs(value))} USD"


def signed_percent_text(value):
    if value is None:
        return "N/D"
    rounded = round_opt(value, 2)
    return f"{rounded:+.2f}%"


def portfolio_active_client_phrase(display_pct):
    if display_pct is None:
        return "Estamos sin porcentaje validado."
    rounded = round_opt(display_pct, 2)
    if rounded < 0:
        return f"Estamos por debajo por {rounded:+.2f}%."
    if rounded > 0:
        return f"Estamos en ganancia por {rounded:+.2f}%."
    return "Estamos al mismo nivel por +0.00%."


def portfolio_pending_client_phrase(display_pct):
    if display_pct is None:
        return "Orden pendiente sin porcentaje validado."
    rounded = round_opt(display_pct, 2)
    if rounded < 0:
        return f"Estamos por debajo del precio actual por {rounded:+.2f}%."
    if rounded > 0:
        return f"Estamos por arriba del precio actual por {rounded:+.2f}%."
    return "Orden al mismo nivel del precio actual."


def portfolio_symbol_label(symbol, notes=""):
    token = str(symbol or "").upper()
    if token.endswith("USDT"):
        label = f"{token[:-4]}/USDT"
    elif token.endswith("USD"):
        label = f"{token[:-3]}/USD"
    else:
        label = token
    note_text = str(notes or "").lower()
    if token == "LUNCUSDT" and "refuerzo" in note_text:
        return "LUNC/USDT refuerzo"
    return label


def portfolio_clean_aggregation_notes(notes):
    text = str(notes or "").strip()
    if not text:
        return ""
    kept = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("AGGREGATION_METADATA:"):
            continue
        kept.append(line)
    return "\n".join(kept).strip()


def merge_pending_draft_rows(rows):
    group = [dict(row) for row in (rows or []) if row]
    if not group:
        return None
    if len(group) == 1:
        row = dict(group[0])
        row["draft_suborder_count"] = 1
        row["draft_suborder_ids"] = [row.get("id")] if row.get("id") else []
        row["notes"] = portfolio_clean_aggregation_notes(row.get("notes"))
        return row
    latest = dict(group[-1])
    total_gross = 0.0
    has_gross = False
    total_quantity = 0.0
    has_quantity = False
    deduped_notes = []
    seen_notes = set()
    for row in group:
        gross_amount = row.get("gross_amount")
        if gross_amount not in (None, ""):
            total_gross += float(gross_amount)
            has_gross = True
        quantity = row.get("quantity")
        if quantity in (None, "") and gross_amount not in (None, "", 0) and row.get("price") not in (None, "", 0):
            quantity = float(gross_amount) / float(row.get("price"))
        if quantity not in (None, ""):
            total_quantity += float(quantity)
            has_quantity = True
        note = portfolio_clean_aggregation_notes(row.get("notes"))
        if note and note not in seen_notes:
            deduped_notes.append(note)
            seen_notes.add(note)
    merged_price = latest.get("price")
    if has_gross and has_quantity and total_quantity:
        merged_price = total_gross / total_quantity
    merged = dict(latest)
    merged["gross_amount"] = round(total_gross, 12) if has_gross else latest.get("gross_amount")
    merged["quantity"] = round(total_quantity, 12) if has_quantity else latest.get("quantity")
    merged["price"] = round(float(merged_price), 12) if merged_price not in (None, "") else latest.get("price")
    merged["draft_suborder_count"] = len(group)
    merged["draft_suborder_ids"] = [row.get("id") for row in group if row.get("id")]
    merged["notes"] = "\n".join(deduped_notes).strip()
    return merged


def price_variation_pct(entry_price, current_price):
    if entry_price in (None, "", 0) or current_price in (None, ""):
        return None
    entry = float(entry_price)
    if entry == 0:
        return None
    return ((float(current_price) - entry) / entry) * 100


def pending_entry_status(side, entry_price, current_price, approved):
    if not approved or current_price in (None, "") or entry_price in (None, "", 0):
        return "precio actual no validado"
    side = str(side or "").upper()
    current = float(current_price)
    entry = float(entry_price)
    if side == "BUY":
        return "ya tocó entrada" if current <= entry else "sigue por encima de la entrada"
    if side == "SELL":
        return "ya tocó salida" if current >= entry else "sigue por debajo de la salida"
    return "sin clasificar"


def portfolio_report_override_config(summary=None):
    payload = read_json_file_any(
        [PORTFOLIO_REPORT_OVERRIDES, RUNTIME_PORTFOLIO_REPORT_OVERRIDES],
        {},
    )
    if not isinstance(payload, dict):
        return {}
    expected_portfolio = str(payload.get("portfolio_id") or "").strip()
    current_portfolio = str((summary or {}).get("portfolio_id") or "").strip()
    if expected_portfolio and current_portfolio and expected_portfolio != current_portfolio:
        return {}
    return payload


def portfolio_fundamental_report_standard():
    return {
        "purpose": "Reporte fundamental estilo noticia para Sr. Eli/Ignis con fuentes actuales, catalizadores reales, tendencia de mercado y separacion entre datos, interpretacion y riesgos.",
        "client_style": (
            "Texto editorial corrido, sobrio e intelectual, como economista profesional de mesa. "
            "Debe sonar a informe macrofinanciero, no a lista de cripto ni checklist operativo."
        ),
        "client_output_format": [
            "Para WhatsApp o texto final al cliente, iniciar con saludo tipo: Buenos dias, senor Eli. Le compartimos nuestro informe de hoy:",
            "Redactar en 2 a 4 parrafos densos y bien conectados; no usar bullets, listas numeradas, tablas ni encabezados salvo instruccion explicita del doctor.",
            "Usar causalidad economica: dato publicado -> lectura de mercado -> efecto probable en riesgo, liquidez, dolar, tasas, equities o cripto.",
            "Incluir cifras puntuales entre parentesis cuando existan en fuentes frescas: dato observado, esperado y previo.",
            "Usar solo noticias de las ultimas 24 horas; seguimiento de noticia anterior solo si sigue siendo hilo vivo que afecta al mercado hoy.",
            "Cerrar con cripto solo si hay noticia realmente material; si no la hay, decirlo en una frase breve al final.",
        ],
        "required_sections": [
            "Resumen ejecutivo",
            "Estado cuantitativo del Portafolio A",
            "Catalizadores internacionales y seguimiento de noticias",
            "Reserva Federal, tasas y liquidez",
            "Oportunidades populares en mercados",
            "Criptonoticias y origen de movimientos",
            "Noticias relevantes del portafolio",
            "Riesgos e invalidaciones",
            "Fuentes validadas",
            "Siguiente accion sugerida",
        ],
        "source_policy": [
            "No usar precios recordados ni reportes viejos como precios actuales.",
            "No presentar catalizadores como reales si no aparecen en fuentes recientes.",
            "Usar solo noticias de las ultimas 24 horas para el informe del dia.",
            "Permitir seguimiento de noticias del dia anterior o del hilo de la semana/mes solo si hoy siguen moviendo precio, flujos, riesgo o expectativas.",
            "No escribir panoramas generalistas del mes ni calendarios amplios salvo que haya evento inminente o actualizacion real del dia.",
            "Orden editorial: comenzar por el catalizador internacional mas relevante para mercados; despues Fed/tasas/liquidez; despues oportunidades populares; despues cripto; al final noticias especificas del portafolio.",
            "Identificar tendencia y efecto probable sobre mercado: risk-on, risk-off, liquidez, dolar, tasas, commodities, flujos institucionales o rotacion sectorial.",
            "No repetir todos los dias un tema de Fed, tasas, fecha macro o geopolitica si no hay avance real o proximidad de fecha; solo mencionarlo cuando afecte la tendencia o se acerque una decision relevante.",
            "No listar moneda por moneda. Mencionar activos del portafolio solo cuando exista catalizador fresco y material.",
            "Evitar frases genericas como 'sin catalizadores robustos' por activo; si no hay noticia material, condensarlo en una sola frase editorial.",
            "Distinguir hechos verificados, inferencias de Kim y puntos pendientes de validacion.",
            "Nunca describir ordenes pendientes como posiciones activas; su distancia contra entrada no es P/L ni ganancia.",
            "Priorizar fuentes primarias o reconocidas: exchanges, proyectos oficiales, reguladores, bancos centrales, medios financieros reputados y agregadores de mercado conocidos.",
            "Si las fuentes no son suficientes, declarar la brecha y pedir validacion manual.",
        ],
        "market_scope": [
            "Catalizadores internacionales: Medio Oriente, conflictos, energia, dolar, liquidez global, comercio, China/Europa/EE.UU. y eventos que cambien apetito de riesgo.",
            "Fed y tasas: decisiones FOMC, minutas, inflacion, empleo, opiniones de miembros Fed, presidentes, bancos centrales y expectativas de recortes/subidas.",
            "Oportunidades populares: monedas, acciones, sectores o narrativas con volumen, momentum, flujos o atencion institucional verificable.",
            "Criptonoticias: BTC, ETH, SOL, XRP, DOGE, ADA, memecoins, ETF/regulacion, liquidaciones, stablecoins, DeFi, AI y origen de movimientos relevantes.",
            "Portafolio A: solo incluir noticias de ADA, DOGE, FTT, XRP, LUNC, APT, DOT, TRUMP, PEPE, HBAR, NEAR, SOL, ZEC u otros activos del portafolio si hay noticia fresca y relevante.",
        ],
    }


def portfolio_standard_markdown(payload):
    active = payload.get("standard_positions", {}).get("active", [])
    pending = payload.get("standard_positions", {}).get("pending", [])
    closed = payload.get("closed_positions") or []
    lines = [
        "# Portafolio Sr. Eli - Estandar Operativo",
        "",
        f"- Version Kim Live: {payload.get('app_version')}",
        f"- Guardado: {payload.get('standard_saved_at')}",
        f"- Portfolio ID: {payload.get('portfolio_id')}",
        f"- Etiqueta: {payload.get('portfolio_label')}",
        "",
        "## Reglas Canonicas",
    ]
    for rule in payload.get("doctor_rules", []):
        lines.append(f"- {rule}")
    lines.extend(["", "## Posiciones Activas"])
    for item in active:
        marker = f" {item.get('credit_mark')}" if item.get("credit_mark") else ""
        lines.append(
            f"- {item.get('identifier')}. {item.get('label')}: {item.get('invested_usd')} USD "
            f"a {item.get('entry_price_display')}{marker}; estado precio={item.get('price_validation_status')}."
        )
        client_note = portfolio_aggregation_client_note(item, payload.get("identifier_prefix") or "A")
        if client_note:
            lines.append(f"  - {client_note}")
            continue
        if item.get("aggregation_summary"):
            lines.append(f"  - Aglomeracion: {item.get('aggregation_summary')}.")
    lines.extend(["", "## Ordenes Pendientes"])
    if pending:
        for item in pending:
            marker = f" {item.get('credit_mark')}" if item.get("credit_mark") else ""
            lines.append(
                f"- {item.get('identifier')}. {item.get('label')}: {item.get('invested_usd')} USD "
                f"a {item.get('entry_price_display')}{marker}; {item.get('entry_status')}."
            )
    else:
        lines.append("- Sin ordenes pendientes.")
    lines.extend(["", "## Posiciones Cerradas"])
    if closed:
        for item in closed:
            pieces = [
                f"- {item.get('identifier') or item.get('order') or ''}. {item.get('label') or item.get('symbol')}:".strip(),
                f"entrada {format_price(item.get('entry_price'))}" if item.get("entry_price") is not None else "",
                f"salida {format_price(item.get('sell_price'))}" if item.get("sell_price") is not None else "",
                f"P/L neto {signed_usd_text(item.get('net_pnl_usd'))}" if item.get("net_pnl_usd") is not None else "",
                str(item.get("notes") or "").strip(),
            ]
            lines.append(" ".join(part for part in pieces if part).strip())
    else:
        lines.append("- Sin posiciones cerradas registradas en el estandar.")
    lines.extend(["", "## Balance"])
    lines.append(payload.get("balance_line") or "Balance pendiente de generar.")
    lines.extend(["", "## Formato WhatsApp Estandar"])
    for item in payload.get("whatsapp_messages", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Reporte Fundamental"])
    standard = payload.get("fundamental_report_standard", {})
    lines.append(standard.get("purpose", ""))
    if standard.get("client_style"):
        lines.append(f"- Estilo cliente: {standard.get('client_style')}")
    for rule in standard.get("client_output_format", []):
        lines.append(f"- Formato cliente: {rule}")
    for section in standard.get("required_sections", []):
        lines.append(f"- {section}")
    lines.extend(["", "## Fuentes De Memoria"])
    for source in payload.get("source_memory", []):
        lines.append(f"- {source}")
    return "\n".join(lines).strip() + "\n"


def portfolio_save_current_standard(summary, report):
    override_config = portfolio_report_override_config(summary)
    identifier_prefix = str(override_config.get("identifier_prefix") or "").strip()

    def position_payload(item):
        order = item.get("resolved_report_order") or item.get("report_order")
        identifier = f"{identifier_prefix}{order}" if identifier_prefix and order not in (None, "") else str(order or "")
        return {
            "identifier": identifier,
            "canonical_report_order": item.get("canonical_report_order"),
            "symbol": item.get("symbol"),
            "label": item.get("label"),
            "state": "pending" if item.get("entry_status") is not None and item.get("current_value_usd") is None else "active",
            "invested_usd": item.get("invested_usd"),
            "entry_price": item.get("entry_price"),
            "entry_price_display": item.get("entry_price_display"),
            "credit": bool(item.get("credit")),
            "credit_usd": item.get("credit_usd"),
            "firm_usd": item.get("firm_usd"),
            "credit_mark": item.get("credit_mark"),
            "price_validation_status": item.get("price_validation_status"),
            "current_price_display": item.get("current_price_display"),
            "variation_display": item.get("variation_display"),
            "entry_status": item.get("entry_status"),
            "aggregation": item.get("aggregation"),
            "aggregation_summary": item.get("aggregation_summary"),
            "merged_with_pending": item.get("merged_with_pending"),
            "notes": item.get("notes"),
        }

    payload = {
        "app_version": APP_VERSION,
        "standard_version": override_config.get("standard_version") or "KIM-0096",
        "standard_saved_at": now_iso(),
        "portfolio_id": summary.get("portfolio_id"),
        "portfolio_label": override_config.get("portfolio_label") or "A",
        "identifier_prefix": identifier_prefix or "A",
        "default_whatsapp_target": DOCTOR_DUBAI_WHATSAPP_TO,
        "never_auto_send_without_doctor_instruction": True,
        "doctor_rules": override_config.get("doctor_rules", []),
        "report_overrides": override_config,
        "standard_positions": {
            "active": [position_payload(item) for item in report.get("active_positions", [])],
            "pending": [position_payload(item) for item in report.get("pending_orders", [])],
        },
        "closed_positions": override_config.get("closed_positions", []),
        "balance": report.get("balance", {}),
        "balance_line": report.get("balance_line", ""),
        "whatsapp_messages": report.get("whatsapp_messages", []),
        "balance_rules": [
            "total comprometido/invertido = posiciones activas ejecutadas + ordenes pendientes abiertas.",
            "saldo disponible = remanentes operativos + ganancias realizadas netas positivas.",
            "monto en firme canonico actual = capital_firme_usd indicado por el doctor + saldo disponible por ganancias/remanentes.",
            "monto a credito actual = total comprometido/invertido - monto en firme canonico ajustado cuando hay capital_firme_usd configurado.",
            "valor actual del portafolio = solo posiciones activas con precios validados.",
            "P/L bruto = P/L no realizado solo de posiciones activas con precios validados.",
            "P/L neto despues de fees = P/L bruto - fee acumulado estimado.",
            "Fee operativo = 1.2% sobre operaciones confirmadas y conversiones de fondeo MXN/USDT o USDT/MXN confirmadas; modificaciones, reemplazos y correcciones no generan fee.",
            "Las ordenes pendientes no entran al P/L hasta ejecutarse.",
        ],
        "fundamental_report_standard": portfolio_fundamental_report_standard(),
        "source_memory": [
            str(BIFROST / "docs" / "kim_0085_portafolio_a_identifiers_2026-06-02.md"),
            str(BIFROST / "docs" / "KIM-0086_portafolio_sr_eli_balance_credito.md"),
            str(MEMORY_CONTEXT_DIR / "kim_live_portafolio_a_2026-06-02.md"),
            str(PORTFOLIO_SR_ELI_MEMORY_DIR / "whatsapp_report_sends.jsonl"),
        ],
    }
    json_paths = write_json_file_both(PORTFOLIO_SR_ELI_STANDARD_JSON, RUNTIME_PORTFOLIO_SR_ELI_STANDARD_JSON, payload)
    md_paths = write_text_file_both(PORTFOLIO_SR_ELI_STANDARD_MD, RUNTIME_PORTFOLIO_SR_ELI_STANDARD_MD, portfolio_standard_markdown(payload))
    append_memory("portfolio_sr_eli_standard_saved", {"standard_version": payload["standard_version"], "json_paths": json_paths, "md_paths": md_paths})
    return {"json_paths": json_paths, "markdown_paths": md_paths, "standard_version": payload["standard_version"]}


def portfolio_override_sort_key(item, preferred):
    explicit = item.get("report_order")
    resolved = None
    if explicit not in (None, ""):
        try:
            resolved = int(explicit)
        except (TypeError, ValueError):
            resolved = None
    token = str(item.get("symbol") or "").upper()
    if resolved is None:
        try:
            resolved = preferred.index(token) + 1
        except ValueError:
            resolved = len(preferred) + 100
    try:
        canonical_index = preferred.index(token) + 1
    except ValueError:
        canonical_index = len(preferred) + 100
    return (resolved, canonical_index, token)


def portfolio_report_explicit_order(item):
    explicit = item.get("report_order")
    if explicit in (None, ""):
        return None
    try:
        return int(explicit)
    except (TypeError, ValueError):
        return None


def portfolio_freeze_report_orders(active_items, pending_items, preferred):
    combined = [*active_items, *pending_items]
    used_orders = set()
    next_index = 1
    for item in sorted(combined, key=lambda row: portfolio_override_sort_key(row, preferred)):
        explicit = portfolio_report_explicit_order(item)
        if explicit is None:
            continue
        used_orders.add(explicit)
    for item in sorted(combined, key=lambda row: portfolio_override_sort_key(row, preferred)):
        if portfolio_report_explicit_order(item) is not None:
            continue
        while next_index in used_orders:
            next_index += 1
        item["report_order"] = next_index
        used_orders.add(next_index)
        next_index += 1


def portfolio_resolve_line_identifier(item, next_index, used_orders, identifier_prefix):
    resolved = portfolio_report_explicit_order(item)
    if resolved is None or resolved in used_orders:
        resolved = next_index
        while resolved in used_orders:
            resolved += 1
    used_orders.add(resolved)
    item["resolved_report_order"] = resolved
    line_id = f"{identifier_prefix}{resolved}" if identifier_prefix else str(resolved)
    return line_id, max(next_index, resolved + 1)


def portfolio_resolve_credit_breakdown(invested_usd, credit_usd, full_mark="(c)", partial_mark="(c parcial)"):
    invested = max(0.0, float(invested_usd or 0))
    credit = max(0.0, float(credit_usd or 0))
    if invested:
        credit = min(credit, invested)
    else:
        credit = 0.0
    firm = max(0.0, invested - credit)
    if invested and credit >= invested:
        mark = full_mark
    elif credit > 0:
        mark = partial_mark
    else:
        mark = ""
    return {
        "credit": credit > 0,
        "credit_usd": round_opt(credit, 2),
        "firm_usd": round_opt(firm, 2),
        "credit_mark": mark,
    }


def portfolio_client_sort_key(item, preferred):
    display_pct = item.get("client_display_pct")
    base_key = portfolio_override_sort_key(item, preferred)
    if display_pct in (None, ""):
        return (1, float("inf"), *base_key)
    return (0, float(display_pct), *base_key)


def portfolio_presentation_config(override_config):
    return override_config.get("presentation") if isinstance(override_config.get("presentation"), dict) else {}


def portfolio_client_performance_pct(item):
    value = item.get("variation_pct")
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def portfolio_pending_distance_to_current_pct(item):
    entry = portfolio_float(item.get("entry_price"))
    current = portfolio_float(item.get("current_price"))
    if entry in (None, 0) or current in (None, 0):
        return None
    return ((entry / current) - 1.0) * 100.0


def portfolio_client_direction_phrase(item, pending=False):
    pct = portfolio_pending_distance_to_current_pct(item) if pending else portfolio_client_performance_pct(item)
    if pct is None:
        return "Precio actual no validado; no calcular porcentaje."
    display = signed_percent_text(round_opt(pct, 2))
    if pending:
        if pct < 0:
            return f"Estamos por debajo del precio actual por {display}."
        if pct > 0:
            return f"Estamos por arriba del precio actual por {display}."
        return "Estamos exactamente al precio actual."
    if pct < 0:
        return f"Estamos por debajo por {display}."
    if pct > 0:
        return f"Estamos en ganancia por {display}."
    return "Estamos sin variacion contra la entrada."


def portfolio_client_position_line(line_id, item, amount_text, pending=False):
    credit_mark = f" {item['credit_mark']}" if item.get("credit_mark") else ""
    pending_label = " pendiente" if pending and "pendiente" not in str(item.get("label") or "").lower() else ""
    lines = [
        f"{line_id}. {item['label']}{pending_label}:",
        f"{amount_text} a {item['entry_price_display']}{credit_mark}.",
    ]
    if item.get("approved_for_client_report"):
        lines.append(f"Precio actual {item['current_price_display']}.")
        lines.append(portfolio_client_direction_phrase(item, pending=pending))
    else:
        lines.append("Precio actual no validado.")
        lines.append("No calcular porcentaje hasta validar precio.")
    return "\n".join(lines)


def portfolio_aggregation_member_label(member):
    order = str((member or {}).get("member_order") or "").strip()
    source = str((member or {}).get("source_order") or "").strip()
    role = str((member or {}).get("role") or "").strip()
    if order and source and order != source:
        return f"{order} desde {source}"
    if order:
        return order
    if source:
        return source
    return role or "suborden"


def portfolio_aggregation_summary_text(aggregation):
    members = aggregation.get("members") or []
    labels = [portfolio_aggregation_member_label(member) for member in members if member]
    labels = [label for label in labels if label]
    if not labels:
        return "historial de subordenes guardado"
    return " + ".join(labels)


def portfolio_aggregation_client_note(item, identifier_prefix="A"):
    aggregation = item.get("aggregation") if isinstance(item, dict) else {}
    if not isinstance(aggregation, dict):
        aggregation = {}
    prefix = str(identifier_prefix or "").strip()
    suborders = []
    for member in aggregation.get("members") or []:
        order = str((member or {}).get("member_order") or "").strip()
        if order and "." in order:
            suborders.append(f"{prefix}{order}" if prefix and not order.startswith(prefix) else order)
    if suborders:
        return f"Refuerzo {', '.join(suborders)} ya incluido."
    if item.get("merged_with_pending") or aggregation:
        return "Refuerzo ya incluido."
    return ""


def portfolio_symbol_ledger_warnings(summary, symbol):
    token = str(symbol or "").strip().upper()
    if not token:
        return []
    buy_rows = []
    for row in [*(summary.get("final_transactions") or []), *(summary.get("draft_transactions") or [])]:
        row_symbol = str((row or {}).get("symbol") or "").strip().upper()
        if row_symbol != token:
            continue
        if str((row or {}).get("side") or "").strip().upper() != "BUY":
            continue
        buy_rows.append(
            {
                "id": row.get("id"),
                "status": "final" if row in (summary.get("final_transactions") or []) else "draft",
                "gross_amount": portfolio_float(row.get("gross_amount"), 0) or 0,
                "price": portfolio_float(row.get("price")),
            }
        )
    status_counts = {}
    signatures = {}
    for row in buy_rows:
        status = row["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
        signature = (
            round(float(row["gross_amount"] or 0), 8),
            round(float(row["price"] or 0), 12) if row["price"] not in (None, "") else None,
        )
        signatures.setdefault(status, [])
        if signature not in signatures[status]:
            signatures[status].append(signature)
    void_rows = []
    for row in summary.get("void_transactions") or []:
        row_symbol = str((row or {}).get("symbol") or "").strip().upper()
        if row_symbol != token:
            continue
        if str((row or {}).get("side") or "").strip().upper() != "BUY":
            continue
        void_rows.append(
            {
                "id": row.get("id"),
                "status": "void",
                "gross_amount": portfolio_float(row.get("gross_amount"), 0) or 0,
                "price": portfolio_float(row.get("price")),
            }
        )
    if void_rows:
        status_counts["void"] = len(void_rows)
        signatures["void"] = []
        for row in void_rows:
            signature = (
                round(float(row["gross_amount"] or 0), 8),
                round(float(row["price"] or 0), 12) if row["price"] not in (None, "") else None,
            )
            if signature not in signatures["void"]:
                signatures["void"].append(signature)
    warnings = []
    active_statuses = [status for status in ("final", "draft", "void") if status_counts.get(status)]
    if len(active_statuses) >= 2:
        fragments = []
        for status in active_statuses:
            entries = []
            for gross_amount, price in signatures.get(status, []):
                price_text = format_price(price) if price not in (None, "") else "sin precio"
                entries.append(f"{format_usd_amount(gross_amount)} USD @ {price_text}")
            fragments.append(f"{status}: {', '.join(entries) or str(status_counts.get(status, 0))}")
        warnings.append(
            f"{token} tiene tramos BUY con estados mezclados en ledger ({'; '.join(fragments)}). "
            "No consolidar promedio, P/L ni venta desde notas libres; confirmar el tramo canonico primero."
        )
    if status_counts.get("final") and status_counts.get("draft") and not any(
        str((agg or {}).get("symbol") or "").strip().upper() == token and str((agg or {}).get("status") or "active").strip().lower() == "active"
        for agg in (summary.get("order_aggregations") or [])
    ):
        warnings.append(
            f"{token} tiene compra final y draft simultaneos sin aglomeracion activa. "
            "Usar transactions/positions como fuente canonica y pedir confirmacion explicita antes de tratar el draft como ejecutado."
        )
    return warnings


def portfolio_collect_ledger_warnings(summary, symbols=None):
    chosen = []
    seen = set()
    for symbol in symbols or []:
        token = str(symbol or "").strip().upper()
        if token and token not in seen:
            chosen.append(token)
            seen.add(token)
    warnings = []
    for token in chosen:
        warnings.extend(portfolio_symbol_ledger_warnings(summary, token))
    return warnings


def portfolio_weighted_average_breakdown(summary, parameters=None):
    parameters = parameters or {}
    raw_symbol = first_value(parameters, "symbol", "ticker", "asset", default="PEPEUSDT")
    symbol = str(raw_symbol or "").strip().upper()
    if symbol and symbol.isalpha() and not symbol.endswith("USDT"):
        symbol = f"{symbol}USDT"
    canonical_order = str(first_value(parameters, "canonical_order", "order_id", "order", default="")).strip()
    include_micro_prices = boolish(first_value(parameters, "include_micro_prices", "scaled_prices", default=True))

    def format_quantity(value):
        if value is None:
            return None
        text = f"{float(value):.6f}"
        return text.rstrip("0").rstrip(".")

    components = []
    source = "transactions"
    aggregation_used = None
    for aggregation in summary.get("order_aggregations") or []:
        agg_symbol = str(aggregation.get("symbol") or "").strip().upper()
        agg_order = str(aggregation.get("canonical_order") or "").strip()
        if canonical_order and agg_order != canonical_order:
            continue
        if symbol and agg_symbol != symbol:
            continue
        if str(aggregation.get("status") or "active").strip().lower() != "active":
            continue
        aggregation_used = aggregation
        source = "order_aggregation"
        break

    if aggregation_used:
        for index, member in enumerate(aggregation_used.get("members") or [], start=1):
            if str((member or {}).get("status") or "active").strip().lower() != "active":
                continue
            if not bool((member or {}).get("include_in_average", True)):
                continue
            amount = member.get("amount_usd")
            price = member.get("price")
            quantity = member.get("quantity")
            amount = float(amount) if amount not in (None, "") else None
            price = float(price) if price not in (None, "") else None
            quantity = float(quantity) if quantity not in (None, "") else None
            if quantity is None and amount is not None and price not in (None, 0):
                quantity = amount / price
            if amount is None and quantity is not None and price not in (None, 0):
                amount = quantity * price
            if amount is None or price in (None, 0) or quantity is None:
                continue
            label = (
                str((member or {}).get("member_order") or "").strip()
                or str((member or {}).get("source_order") or "").strip()
                or str((member or {}).get("role") or "").strip()
                or f"tramo_{index}"
            )
            components.append(
                {
                    "label": label,
                    "amount_usd": amount,
                    "price": price,
                    "price_display": format_price(price),
                    "quantity": quantity,
                    "quantity_display": format_quantity(quantity),
                    "micro_price": round_opt(price * 1_000_000, 6) if include_micro_prices else None,
                    "notes": str((member or {}).get("notes") or "").strip(),
                }
            )

    if not components:
        for row in [*(summary.get("final_transactions") or []), *(summary.get("draft_transactions") or [])]:
            row_symbol = str((row or {}).get("symbol") or "").strip().upper()
            if symbol and row_symbol != symbol:
                continue
            if str((row or {}).get("side") or "").strip().upper() != "BUY":
                continue
            amount = row.get("gross_amount")
            price = row.get("price")
            quantity = row.get("quantity")
            amount = float(amount) if amount not in (None, "") else None
            price = float(price) if price not in (None, "") else None
            quantity = float(quantity) if quantity not in (None, "") else None
            if quantity is None and amount is not None and price not in (None, 0):
                quantity = amount / price
            if amount is None and quantity is not None and price not in (None, 0):
                amount = quantity * price
            if amount is None or price in (None, 0) or quantity is None:
                continue
            components.append(
                {
                    "label": str(row.get("id") or row.get("occurred_at") or f"tramo_{len(components) + 1}"),
                    "amount_usd": amount,
                    "price": price,
                    "price_display": format_price(price),
                    "quantity": quantity,
                    "quantity_display": format_quantity(quantity),
                    "micro_price": round_opt(price * 1_000_000, 6) if include_micro_prices else None,
                    "notes": str(row.get("notes") or "").strip(),
                }
            )

    if len(components) < 2:
        raise ValueError(f"No encontre suficientes tramos activos para calcular promedio ponderado de {symbol or 'la posicion'}.")

    total_amount = sum(float(item.get("amount_usd") or 0) for item in components)
    total_quantity = sum(float(item.get("quantity") or 0) for item in components)
    if total_quantity <= 0:
        raise ValueError("La cantidad total es cero; no puedo calcular el promedio ponderado.")
    average_price = total_amount / total_quantity
    amount_terms = [format_usd_amount(item["amount_usd"]) for item in components]
    quantity_terms = [item["quantity_display"] for item in components if item.get("quantity_display")]
    operations = []
    for index, item in enumerate(components, start=1):
        operations.append(
            f"q{index} = {format_usd_amount(item['amount_usd'])} / {item['price_display']} = {item['quantity_display']}"
        )
    operations.append(f"q_total = {' + '.join(quantity_terms)} = {format_quantity(total_quantity)}")
    operations.append(f"usd_total = {' + '.join(amount_terms)} = {format_usd_amount(total_amount)}")
    operations.append(
        f"promedio = {format_usd_amount(total_amount)} / {format_quantity(total_quantity)} = {format_price(average_price)}"
    )
    ledger_warnings = portfolio_collect_ledger_warnings(summary, [symbol])
    return {
        "ok": True,
        "provider": "portfolio",
        "action": "weighted_average_breakdown",
        "symbol": symbol,
        "canonical_order": canonical_order or (aggregation_used or {}).get("canonical_order"),
        "source": source,
        "components": components,
        "micro_prices": [
            {"label": item["label"], "micro_price": item.get("micro_price")}
            for item in components
            if item.get("micro_price") is not None
        ]
        if include_micro_prices
        else [],
        "total_amount_usd": round_opt(total_amount, 2),
        "total_quantity": round_opt(total_quantity, 6),
        "weighted_average_price": average_price,
        "weighted_average_price_display": format_price(average_price),
        "operations": operations,
        "ledger_warnings": ledger_warnings,
        "summary": "; ".join(
            f"{item['label']}: {format_usd_amount(item['amount_usd'])} USD @ {item['price_display']}"
            for item in components
        ),
    }


def portfolio_recompute_credit_fields(item, override_config):
    symbol = str(item.get("symbol") or "").upper()
    credit_amount_overrides = {
        str(key or "").upper(): float(value or 0)
        for key, value in (override_config.get("credit_amounts") or {}).items()
        if str(key or "").strip()
    }
    credit_symbols = {
        str(symbol_item or "").upper()
        for symbol_item in override_config.get("credit_symbols", [])
        if str(symbol_item or "").strip()
    }
    invested_usd = float(item.get("invested_usd") or 0)
    if symbol in credit_amount_overrides:
        credit_amount = credit_amount_overrides[symbol]
    elif bool(item.get("credit")) or symbol in credit_symbols:
        credit_amount = invested_usd
    else:
        credit_amount = item.get("credit_usd") or 0
    credit_mark = str(override_config.get("credit_mark") or "(c)").strip() or "(c)"
    partial_credit_mark = str(override_config.get("partial_credit_mark") or "(c parcial)").strip() or "(c parcial)"
    item.update(portfolio_resolve_credit_breakdown(invested_usd, credit_amount, credit_mark, partial_credit_mark))
    return item


def portfolio_accounting_config(override_config):
    return override_config.get("accounting") if isinstance(override_config.get("accounting"), dict) else {}


def portfolio_fee_summary(active_items, summary, override_config):
    accounting = portfolio_accounting_config(override_config)
    fee_rate = float(accounting.get("operation_fee_rate") or 0)
    confirmed_volume = sum(float(item.get("invested_usd") or 0) for item in active_items)
    funding_conversions = accounting.get("funding_conversions") if isinstance(accounting.get("funding_conversions"), list) else []
    funding_volume = sum(
        float(item.get("amount_usd") or 0)
        for item in funding_conversions
        if str((item or {}).get("status") or "confirmed").lower() == "confirmed"
    )
    excluded_event_types = [
        "modificacion",
        "modification",
        "replace",
        "replacement",
        "rebalance_note",
        "correction",
    ]
    operation_fee = confirmed_volume * fee_rate
    funding_fee = funding_volume * fee_rate
    total_fee = operation_fee + funding_fee
    return {
        "operation_fee_rate": fee_rate,
        "operation_fee_rate_pct": round_opt(fee_rate * 100, 4),
        "confirmed_operation_volume_usd": round_opt(confirmed_volume, 2),
        "confirmed_operation_fee_usd": round_opt(operation_fee, 2),
        "funding_conversion_volume_usd": round_opt(funding_volume, 2),
        "funding_conversion_fee_usd": round_opt(funding_fee, 2),
        "total_fee_usd": round_opt(total_fee, 2),
        "fee_policy": accounting.get("fee_policy")
        or "Fee de 1.2% solo sobre operaciones confirmadas y conversiones MXN/USDT/USDT/MXN confirmadas; modificaciones, reemplazos y correcciones no generan fee.",
        "excluded_event_types": excluded_event_types,
        "funding_conversions": funding_conversions,
    }


def portfolio_aggregation_transaction_ref(member):
    for key in ("transaction_id", "source_order", "member_order"):
        token = str((member or {}).get(key) or "").strip()
        if token.startswith("tx_"):
            return token
    return ""


def portfolio_active_aggregation_members(aggregation, transaction_statuses):
    valid = []
    blocked = []
    for member in aggregation.get("members") or []:
        if str((member or {}).get("status") or "active").lower() != "active":
            continue
        if not bool((member or {}).get("include_in_average", True)):
            continue
        tx_ref = portfolio_aggregation_transaction_ref(member)
        if tx_ref and transaction_statuses.get(tx_ref) != "final":
            blocked.append(
                {
                    "transaction_id": tx_ref,
                    "status": transaction_statuses.get(tx_ref) or "missing_or_void",
                    "member_order": (member or {}).get("member_order"),
                }
            )
            continue
        valid.append(member)
    return valid, blocked


def portfolio_recalculate_aggregation_totals(aggregation, members):
    total_amount = 0.0
    total_quantity = 0.0
    has_amount = False
    has_quantity = False
    for member in members:
        amount = member.get("amount_usd")
        price = member.get("price")
        quantity = member.get("quantity")
        amount = float(amount) if amount not in (None, "") else None
        price = float(price) if price not in (None, "") else None
        quantity = float(quantity) if quantity not in (None, "") else None
        if amount is None and quantity is not None and price is not None:
            amount = quantity * price
        if quantity is None and amount is not None and price not in (None, 0):
            quantity = amount / price
        if amount is not None:
            total_amount += amount
            has_amount = True
        if quantity is not None and quantity > 0:
            total_quantity += quantity
            has_quantity = True
    if not has_amount or not has_quantity or total_quantity <= 0:
        return (
            aggregation.get("total_amount_usd"),
            aggregation.get("weighted_average_price"),
            aggregation.get("total_quantity"),
        )
    return total_amount, total_amount / total_quantity, total_quantity


def portfolio_apply_order_aggregations(summary, active_items, pending_items, include_units, canonical_order, load_validation, override_config):
    aggregations = summary.get("order_aggregations") or []
    if not aggregations:
        return active_items, pending_items
    manual_override_symbols = {
        str((entry or {}).get("symbol") or "").upper().strip()
        for entry in (override_config.get("manual_entries") or [])
        if isinstance(entry, dict) and str((entry or {}).get("symbol") or "").strip()
    }
    transaction_statuses = {
        str(tx.get("id") or ""): "final"
        for tx in summary.get("final_transactions") or []
        if str(tx.get("id") or "").strip()
    }
    transaction_statuses.update(
        {
            str(tx.get("id") or ""): "draft"
            for tx in summary.get("draft_transactions") or []
            if str(tx.get("id") or "").strip()
        }
    )
    by_symbol_active = {str(item.get("symbol") or "").upper(): item for item in active_items}
    by_symbol_pending = {str(item.get("symbol") or "").upper(): item for item in pending_items}
    suppress_pending_symbols = set()
    for aggregation in aggregations:
        if str(aggregation.get("status") or "active").lower() != "active":
            continue
        symbol = str(aggregation.get("symbol") or "").upper().strip()
        if not symbol:
            continue
        if symbol in manual_override_symbols:
            continue
        valid_members, blocked_members = portfolio_active_aggregation_members(aggregation, transaction_statuses)
        if aggregation.get("members") and not valid_members:
            continue
        if blocked_members:
            aggregation = {**aggregation, "members": valid_members, "blocked_members": blocked_members}
        total_amount, average_price, total_quantity = portfolio_recalculate_aggregation_totals(aggregation, valid_members)
        if total_amount in (None, ""):
            continue
        if average_price in (None, "") and total_quantity not in (None, "", 0):
            average_price = float(total_amount) / float(total_quantity)
        if total_quantity in (None, "") and average_price not in (None, "", 0):
            total_quantity = float(total_amount) / float(average_price)
        target = by_symbol_active.get(symbol)
        state = "active"
        if target is None:
            target = by_symbol_pending.get(symbol)
            state = "pending"
        if target is None:
            validation = load_validation(symbol)
            current_price = validation.get("reference_price")
            approved = bool(validation.get("approved_for_client_report"))
            current_value_usd = (float(total_quantity) * float(current_price)) if approved and total_quantity else None
            unrealized_pnl_usd = (current_value_usd - float(total_amount)) if current_value_usd is not None else None
            target = {
                "symbol": symbol,
                "label": str(aggregation.get("label") or portfolio_symbol_label(symbol)).strip() or portfolio_symbol_label(symbol),
                "current_price": round_price(current_price) if approved else None,
                "current_price_display": validation.get("reference_price_display") if approved else None,
                "price_validation_status": validation.get("status"),
                "approved_for_client_report": approved,
                "current_value_usd": round_opt(current_value_usd, 2),
                "unrealized_pnl_usd": round_opt(unrealized_pnl_usd, 2),
                "unrealized_pnl_display": signed_usd_text(unrealized_pnl_usd),
                "sources": ["order_aggregation"],
                "transaction_ids": [],
            }
            active_items.append(target)
            by_symbol_active[symbol] = target
            state = "active"
        current_price = target.get("current_price")
        approved = bool(target.get("approved_for_client_report"))
        variation_pct = price_variation_pct(average_price, current_price if approved else None)
        current_value_usd = (float(total_quantity) * float(current_price)) if approved and total_quantity else None
        unrealized_pnl_usd = (current_value_usd - float(total_amount)) if current_value_usd is not None else None
        target.update(
            {
                "invested_usd": round_opt(total_amount, 2),
                "entry_price": round_price(average_price),
                "entry_price_display": format_price(average_price),
                "variation_pct": round_opt(variation_pct, 2),
                "variation_display": signed_percent_text(variation_pct),
                "reference_quantity": round_opt(total_quantity, 8) if include_units and total_quantity else target.get("reference_quantity"),
                "report_order": aggregation.get("canonical_order") or target.get("report_order"),
                "aggregation": aggregation,
                "aggregation_summary": portfolio_aggregation_summary_text(aggregation),
                "notes": "\n".join(
                    part
                    for part in [
                        str(target.get("notes") or "").strip(),
                        str(aggregation.get("notes") or "").strip(),
                    ]
                    if part
                ),
            }
        )
        if state == "active":
            target.update(
                {
                    "current_value_usd": round_opt(current_value_usd, 2),
                    "unrealized_pnl_usd": round_opt(unrealized_pnl_usd, 2),
                    "unrealized_pnl_display": signed_usd_text(unrealized_pnl_usd),
                    "merged_with_pending": True,
                }
            )
            suppress_pending_symbols.add(symbol)
        portfolio_recompute_credit_fields(target, override_config)
    if suppress_pending_symbols:
        pending_items = [
            item
            for item in pending_items
            if str(item.get("symbol") or "").upper() not in suppress_pending_symbols
        ]
    active_items.sort(key=lambda item: portfolio_override_sort_key(item, canonical_order))
    pending_items.sort(key=lambda item: portfolio_override_sort_key(item, canonical_order))
    return active_items, pending_items


def portfolio_manual_active_aggregation_enabled(config):
    return boolish(config.get("auto_aggregate_active_manual_entries", True))


def portfolio_manual_aggregation_fee_rate(config):
    explicit = portfolio_float(config.get("manual_active_aggregation_fee_rate"))
    if explicit is not None:
        return max(0.0, explicit)
    accounting = portfolio_accounting_config(config)
    return max(0.0, portfolio_float(accounting.get("operation_fee_rate"), 0.0) or 0.0)


def portfolio_manual_item_order_label(item):
    order = item.get("report_order")
    if order not in (None, ""):
        return f"A{order}"
    return str(item.get("id") or item.get("symbol") or "").strip()


def portfolio_aggregate_manual_active_items(active_items, config, canonical_order):
    if not portfolio_manual_active_aggregation_enabled(config):
        return active_items
    grouped = {}
    passthrough = []
    for item in active_items:
        if item.get("override_source") != "portfolio_report_overrides":
            passthrough.append(item)
            continue
        symbol = portfolio_normalize_symbol(item.get("symbol"))
        if not symbol:
            passthrough.append(item)
            continue
        grouped.setdefault(symbol, []).append(item)
    fee_rate = portfolio_manual_aggregation_fee_rate(config)
    aggregated = []
    for symbol, items in grouped.items():
        if len(items) < 2:
            aggregated.extend(items)
            continue
        total_amount = 0.0
        total_quantity = 0.0
        total_credit = 0.0
        member_rows = []
        notes = []
        sources = []
        transaction_ids = []
        current_price = None
        current_display = None
        price_status = None
        approved = False
        report_orders = []
        ordered_items = sorted(items, key=lambda row: portfolio_override_sort_key(row, canonical_order))
        for item in ordered_items:
            amount = portfolio_float(item.get("invested_usd"), 0.0) or 0.0
            entry_price = portfolio_float(item.get("entry_price"))
            quantity = portfolio_float(item.get("reference_quantity"))
            if quantity in (None, 0) and amount and entry_price not in (None, 0):
                quantity = amount / entry_price
            quantity = portfolio_float(quantity, 0.0) or 0.0
            total_amount += amount
            total_quantity += quantity
            total_credit += portfolio_float(item.get("credit_usd"), 0.0) or 0.0
            report_order = portfolio_report_explicit_order(item)
            if report_order is not None:
                report_orders.append(report_order)
            if item.get("current_price") not in (None, ""):
                current_price = item.get("current_price")
                current_display = item.get("current_price_display")
                price_status = item.get("price_validation_status")
                approved = bool(item.get("approved_for_client_report"))
            if item.get("notes"):
                notes.append(str(item.get("notes") or "").strip())
            sources.extend(item.get("sources") or [])
            transaction_ids.extend(item.get("transaction_ids") or [])
            member_rows.append(
                {
                    "member_order": portfolio_manual_item_order_label(item),
                    "role": "manual_active_execution",
                    "amount_usd": round_opt(amount, 2),
                    "price": entry_price,
                    "quantity": round_opt(quantity, 8),
                    "include_in_average": True,
                    "status": "active",
                    "notes": str(item.get("notes") or "").strip(),
                }
            )
        if total_quantity <= 0 or total_amount <= 0:
            aggregated.extend(items)
            continue
        raw_average = total_amount / total_quantity
        adjusted_average = raw_average * (1 + fee_rate) if fee_rate else raw_average
        current_value = (total_quantity * float(current_price)) if approved and current_price not in (None, "") else None
        unrealized_pnl = (current_value - total_amount) if current_value is not None else None
        variation_pct = price_variation_pct(adjusted_average, current_price if approved else None)
        report_order = min(report_orders) if report_orders else None
        credit_fields = portfolio_resolve_credit_breakdown(
            total_amount,
            total_credit,
            full_mark=str(config.get("credit_mark") or "(c)").strip() or "(c)",
            partial_mark=str(config.get("partial_credit_mark") or "(c parcial)").strip() or "(c parcial)",
        )
        aggregation = {
            "id": f"manual_agg_{symbol.lower()}",
            "portfolio_id": config.get("portfolio_id") or "sr_eli_2026",
            "canonical_order": report_order,
            "symbol": symbol,
            "label": portfolio_symbol_label(symbol),
            "status": "active",
            "notes": (
                f"Aglomeracion automatica de {len(items)} ordenes activas del mismo activo. "
                f"Promedio base {format_price(raw_average)}; fee operativo {round_opt(fee_rate * 100, 4)}% integrado al costo."
            ),
            "weighted_average_price": round_price(adjusted_average),
            "raw_weighted_average_price": round_price(raw_average),
            "total_quantity": round_opt(total_quantity, 8),
            "total_amount_usd": round_opt(total_amount, 2),
            "fee_rate": fee_rate,
            "members": member_rows,
        }
        aggregated.append(
            {
                "symbol": symbol,
                "label": portfolio_symbol_label(symbol),
                "invested_usd": round_opt(total_amount, 2),
                "entry_price": round_price(adjusted_average),
                "entry_price_display": format_price(adjusted_average),
                "current_price": round_price(current_price) if approved else None,
                "current_price_display": current_display if approved else None,
                "price_validation_status": price_status,
                "approved_for_client_report": approved,
                "variation_pct": round_opt(variation_pct, 2),
                "variation_display": signed_percent_text(variation_pct),
                "reference_quantity": round_opt(total_quantity, 8) if total_quantity else None,
                "notes": "\n".join(note for note in notes if note),
                "report_order": report_order,
                "override_source": "portfolio_report_overrides",
                "current_value_usd": round_opt(current_value, 2),
                "unrealized_pnl_usd": round_opt(unrealized_pnl, 2),
                "unrealized_pnl_display": signed_usd_text(unrealized_pnl),
                "merged_with_pending": True,
                "sources": list(dict.fromkeys([source for source in sources if source])),
                "transaction_ids": list(dict.fromkeys([tx for tx in transaction_ids if tx])),
                "aggregation": aggregation,
                "aggregation_summary": portfolio_aggregation_summary_text(aggregation),
                **credit_fields,
            }
        )
    aggregated.sort(key=lambda item: portfolio_override_sort_key(item, canonical_order))
    return [*passthrough, *aggregated]


def portfolio_apply_manual_overrides(summary, active_items, pending_items, include_units, canonical_order, load_validation):
    config = portfolio_report_override_config(summary)
    if not config:
        return active_items, pending_items, config

    suppressed_symbols = {
        str(symbol or "").upper()
        for symbol in config.get("suppress_symbols", [])
        if str(symbol or "").strip()
    }
    credit_symbols = {
        str(symbol or "").upper()
        for symbol in config.get("credit_symbols", [])
        if str(symbol or "").strip()
    }
    credit_amount_overrides = {
        str(symbol or "").upper(): float(amount or 0)
        for symbol, amount in (config.get("credit_amounts") or {}).items()
        if str(symbol or "").strip()
    }
    credit_mark = str(config.get("credit_mark") or "(c)").strip() or "(c)"
    partial_credit_mark = str(config.get("partial_credit_mark") or "(c parcial)").strip() or "(c parcial)"
    manual_entries = config.get("manual_entries") if isinstance(config.get("manual_entries"), list) else []
    manual_symbols = {
        str(entry.get("symbol") or "").upper()
        for entry in manual_entries
        if isinstance(entry, dict) and str(entry.get("symbol") or "").strip()
    }

    filtered_active = [
        item
        for item in active_items
        if str(item.get("symbol") or "").upper() not in suppressed_symbols
        and str(item.get("symbol") or "").upper() not in manual_symbols
    ]
    filtered_pending = [
        item
        for item in pending_items
        if str(item.get("symbol") or "").upper() not in suppressed_symbols
        and str(item.get("symbol") or "").upper() not in manual_symbols
    ]

    for item in [*filtered_active, *filtered_pending]:
        symbol = str(item.get("symbol") or "").upper()
        invested_usd = float(item.get("invested_usd") or 0)
        credit_amount = item.get("credit_usd")
        if credit_amount in (None, ""):
            if symbol in credit_amount_overrides:
                credit_amount = credit_amount_overrides[symbol]
            elif bool(item.get("credit")) or symbol in credit_symbols:
                credit_amount = invested_usd
            else:
                credit_amount = 0
        item.update(
            portfolio_resolve_credit_breakdown(
                invested_usd,
                credit_amount,
                full_mark=credit_mark,
                partial_mark=partial_credit_mark,
            )
        )

    for entry in manual_entries:
        if not isinstance(entry, dict):
            continue
        symbol = str(entry.get("symbol") or "").upper().strip()
        if not symbol:
            continue
        state = str(entry.get("state") or "active").strip().lower()
        if state in PORTFOLIO_CLOSED_STATES:
            continue
        notes = str(entry.get("notes") or "").strip()
        label = str(entry.get("label") or portfolio_symbol_label(symbol, notes)).strip() or symbol
        invested_raw = float(entry.get("invested_usd") or 0)
        entry_price = float(entry.get("entry_price")) if entry.get("entry_price") not in (None, "") else None
        quantity = float(entry.get("quantity") or 0)
        if not quantity and invested_raw and entry_price not in (None, 0):
            quantity = invested_raw / float(entry_price)
        validation = load_validation(symbol)
        current_price = validation.get("reference_price")
        approved = bool(validation.get("approved_for_client_report"))
        manual_current_price = portfolio_float(
            first_value(entry, "current_price", "current_price_usd", "doctor_current_price", "manual_current_price")
        )
        if manual_current_price not in (None, ""):
            current_price = manual_current_price
            approved = True
            validation = {
                **validation,
                "status": str(entry.get("current_price_status") or "manual_doctor_validated"),
                "reference_price": manual_current_price,
                "reference_price_display": format_price(manual_current_price),
                "approved_for_client_report": True,
                "manual_override": True,
                "source": str(entry.get("current_price_source") or "doctor_manual_reference"),
            }
        variation_pct = price_variation_pct(entry_price, current_price if approved else None)
        current_value_usd = (quantity * float(current_price)) if approved and quantity else None
        unrealized_pnl_usd = (current_value_usd - invested_raw) if current_value_usd is not None else None
        credit_amount = entry.get("credit_usd")
        if credit_amount in (None, ""):
            if symbol in credit_amount_overrides:
                credit_amount = credit_amount_overrides[symbol]
            elif boolish(entry.get("credit")) or symbol in credit_symbols:
                credit_amount = invested_raw
            else:
                credit_amount = 0
        credit_fields = portfolio_resolve_credit_breakdown(
            invested_raw,
            credit_amount,
            full_mark=credit_mark,
            partial_mark=partial_credit_mark,
        )
        base_item = {
            "symbol": symbol,
            "label": label,
            "invested_usd": round_opt(invested_raw, 2),
            "entry_price": round_price(entry_price),
            "entry_price_display": format_price(entry_price),
            "current_price": round_price(current_price) if approved else None,
            "current_price_display": validation.get("reference_price_display") if approved else None,
            "price_validation_status": validation.get("status"),
            "approved_for_client_report": approved,
            "variation_pct": round_opt(variation_pct, 2),
            "variation_display": signed_percent_text(variation_pct),
            "reference_quantity": round_opt(quantity, 8) if include_units and quantity else None,
            "notes": notes,
            "report_order": entry.get("order"),
            "override_source": "portfolio_report_overrides",
            **credit_fields,
        }
        if state == "pending":
            filtered_pending.append(
                {
                    **base_item,
                    "id": entry.get("id") or f"manual-{symbol.lower()}",
                    "side": str(entry.get("side") or "BUY").upper(),
                    "entry_status": str(entry.get("entry_status") or "").strip()
                    or pending_entry_status(str(entry.get("side") or "BUY").upper(), entry_price, current_price, approved),
                    "source": str(entry.get("source") or "manual_override"),
                }
            )
            continue
        filtered_active.append(
            {
                **base_item,
                "current_value_usd": round_opt(current_value_usd, 2),
                "unrealized_pnl_usd": round_opt(unrealized_pnl_usd, 2),
                "unrealized_pnl_display": signed_usd_text(unrealized_pnl_usd),
                "merged_with_pending": boolish(entry.get("merged_with_pending")),
                "sources": [str(entry.get("source") or "manual_override")],
                "transaction_ids": [str(entry.get("transaction_id") or "")] if entry.get("transaction_id") else [],
            }
        )

    filtered_active = portfolio_aggregate_manual_active_items(filtered_active, config, canonical_order)
    filtered_active.sort(key=lambda item: portfolio_override_sort_key(item, canonical_order))
    filtered_pending.sort(key=lambda item: portfolio_override_sort_key(item, canonical_order))
    return filtered_active, filtered_pending, config


def portfolio_client_report(summary, parameters=None):
    parameters = parameters or {}
    include_units = bool(parameters.get("include_units"))
    provider_warnings = []
    providers = parameters.get("providers") or ["binance", "mexc", "bybit"]
    providers = [str(provider or "").strip().lower() for provider in providers if str(provider or "").strip()]
    if "coinmarketcap" in providers and not load_keychain_secret(COINMARKETCAP_KEYCHAIN_SERVICE, required=False):
        providers = [provider for provider in providers if provider != "coinmarketcap"]
        provider_warnings.append("CoinMarketCap no se uso porque falta API key en Keychain.")
    if boolish(first_value(parameters, "force_refresh_prices", "refresh_prices", "clear_price_cache", "force_refresh", default=False)):
        clear_market_price_caches(reason="portfolio_client_report")
    canonical_order = [
        "ADAUSDT",
        "DOGEUSDT",
        "FTTUSDT",
        "XRPUSDT",
        "LUNCUSDT",
        "APTUSDT",
        "DOTUSDT",
        "TRUMPUSDT",
        "PEPEUSDT",
        "HBARUSDT",
        "NEARUSDT",
        "ONDOUSDT",
        "TRXUSDT",
        "ICPUSDT",
        "AVAXUSDT",
        "HYPEUSDT",
        "SUIUSDT",
    ]
    final_transactions = summary.get("final_transactions") or []
    draft_transactions = summary.get("draft_transactions") or []
    positions = summary.get("positions") or []
    position_map = {str(item.get("symbol") or "").upper(): item for item in positions}
    symbol_validations = {}
    merged_draft_keys = set()
    report_symbols = [
        str(tx.get("symbol") or "").upper()
        for tx in [*final_transactions, *draft_transactions, *positions]
        if str(tx.get("symbol") or "").strip()
    ]
    source_warmup = warm_market_price_sources(report_symbols, providers=providers)
    failed_warmup_providers = {str(item.get("provider") or "").lower() for item in source_warmup.get("failures") or []}
    if failed_warmup_providers:
        for failure in source_warmup.get("failures") or []:
            provider_warnings.append(f"{failure.get('provider')}: {failure.get('error')}")
        providers = [provider for provider in providers if provider not in failed_warmup_providers]

    def load_validation(symbol):
        token = str(symbol or "").upper()
        if token not in symbol_validations:
            symbol_validations[token] = validate_market_prices(f"BINANCE:{token}", providers=providers)
        return symbol_validations[token]

    def sort_key(symbol, preferred):
        token = str(symbol or "").upper()
        try:
            return (0, preferred.index(token))
        except ValueError:
            return (1, token)

    def draft_row_key(row):
        return (
            str((row or {}).get("symbol") or "").upper(),
            str((row or {}).get("occurred_at") or ""),
            str((row or {}).get("source") or ""),
            str((row or {}).get("notes") or ""),
        )

    active_by_symbol = {}
    for tx in final_transactions:
        symbol = str(tx.get("symbol") or "").upper()
        bucket = active_by_symbol.setdefault(
            symbol,
            {
                "symbol": symbol,
                "gross_amount": 0.0,
                "notes": [],
                "sources": [],
                "transaction_ids": [],
            },
        )
        if str(tx.get("side") or "").upper() == "BUY":
            bucket["gross_amount"] += float(tx.get("gross_amount") or 0)
        bucket["notes"].append(str(tx.get("notes") or ""))
        bucket["sources"].append(str(tx.get("source") or ""))
        bucket["transaction_ids"].append(str(tx.get("id") or ""))
        if tx.get("occurred_at"):
            bucket["occurred_at"] = tx.get("occurred_at")

    def can_merge_same_symbol_drafts(symbol, draft_rows):
        if not draft_rows:
            return False
        note_blob = " ".join(str(row.get("notes") or "") for row in draft_rows).lower()
        if symbol == "LUNCUSDT":
            return True
        blocking_terms = ["pendiente", "sin afectar", "no afectar", "a14"]
        if any(term in note_blob for term in blocking_terms):
            return False
        explicit_terms = ["ya incluido", "ejecutad", "confirmad", "posicion activa", "promedio ponderado"]
        return any(term in note_blob for term in explicit_terms)

    draft_rows_by_symbol = {}
    for tx in draft_transactions:
        symbol = str(tx.get("symbol") or "").upper()
        draft_rows_by_symbol.setdefault(symbol, []).append(tx)

    active_items = []
    executed_preliminary = []
    for symbol, bucket in sorted(active_by_symbol.items(), key=lambda item: sort_key(item[0], canonical_order)):
        position = position_map.get(symbol) or {}
        merged_drafts = draft_rows_by_symbol.get(symbol) or []
        merged_with_pending = can_merge_same_symbol_drafts(symbol, merged_drafts)
        total_invested = float(bucket["gross_amount"] or 0)
        total_quantity = float(position.get("quantity") or 0)
        merged_notes = [note for note in bucket["notes"] if note]
        if merged_with_pending:
            for draft_row in merged_drafts:
                merged_draft_keys.add(draft_row_key(draft_row))
                total_invested += float(draft_row.get("gross_amount") or 0)
                total_quantity += float(draft_row.get("quantity") or 0)
                if draft_row.get("notes"):
                    merged_notes.append(str(draft_row.get("notes") or ""))
        validation = load_validation(symbol)
        current_price = validation.get("reference_price")
        approved = bool(validation.get("approved_for_client_report"))
        entry_price = (total_invested / total_quantity) if total_quantity else position.get("average_cost")
        variation_pct = price_variation_pct(entry_price, current_price if approved else None)
        current_value_usd = (total_quantity * float(current_price)) if approved and total_quantity else None
        unrealized_pnl_usd = (current_value_usd - total_invested) if current_value_usd is not None else None
        notes = "\n".join(merged_notes).strip()
        sources = [source for source in bucket["sources"] if source]
        is_preliminary_fill = any("credit_filled" in source for source in sources) or "antes pendiente" in notes.lower()
        item = {
            "symbol": symbol,
            "label": portfolio_symbol_label(symbol, notes),
            "invested_usd": round_opt(total_invested, 2),
            "entry_price": round_price(entry_price),
            "entry_price_display": format_price(entry_price),
            "current_price": round_price(current_price) if approved else None,
            "current_price_display": validation.get("reference_price_display") if approved else None,
            "price_validation_status": validation.get("status"),
            "approved_for_client_report": approved,
            "variation_pct": round_opt(variation_pct, 2),
            "variation_display": signed_percent_text(variation_pct),
            "current_value_usd": round_opt(current_value_usd, 2),
            "unrealized_pnl_usd": round_opt(unrealized_pnl_usd, 2),
            "unrealized_pnl_display": signed_usd_text(unrealized_pnl_usd),
            "reference_quantity": round_opt(total_quantity, 8) if include_units else None,
            "merged_with_pending": merged_with_pending,
            "notes": notes,
            "sources": sources,
            "transaction_ids": bucket["transaction_ids"],
        }
        active_items.append(item)
        if is_preliminary_fill:
            executed_preliminary.append(item)

    grouped_pending_rows = {}
    for tx in sorted(draft_transactions, key=lambda item: sort_key(item.get("symbol"), canonical_order)):
        if draft_row_key(tx) in merged_draft_keys:
            continue
        group_key = (
            str(tx.get("symbol") or "").upper(),
            str(tx.get("side") or "").upper(),
        )
        grouped_pending_rows.setdefault(group_key, []).append(tx)

    pending_items = []
    for (_symbol, _side), grouped_rows in sorted(grouped_pending_rows.items(), key=lambda item: sort_key(item[0][0], canonical_order)):
        tx = merge_pending_draft_rows(grouped_rows)
        if not tx:
            continue
        symbol = str(tx.get("symbol") or "").upper()
        validation = load_validation(symbol)
        current_price = validation.get("reference_price")
        approved = bool(validation.get("approved_for_client_report"))
        entry_price = tx.get("price")
        variation_pct = price_variation_pct(entry_price, current_price if approved else None)
        item = {
            "id": tx.get("id"),
            "symbol": symbol,
            "label": portfolio_symbol_label(symbol, tx.get("notes")),
            "side": tx.get("side"),
            "invested_usd": round_opt(tx.get("gross_amount"), 2),
            "entry_price": round_price(entry_price),
            "entry_price_display": format_price(entry_price),
            "current_price": round_price(current_price) if approved else None,
            "current_price_display": validation.get("reference_price_display") if approved else None,
            "price_validation_status": validation.get("status"),
            "approved_for_client_report": approved,
            "variation_pct": round_opt(variation_pct, 2),
            "variation_display": signed_percent_text(variation_pct),
            "entry_status": pending_entry_status(tx.get("side"), entry_price, current_price, approved),
            "reference_quantity": round_opt(tx.get("quantity"), 8) if include_units else None,
            "notes": tx.get("notes") or "",
            "source": tx.get("source") or "",
            "draft_suborder_count": int(tx.get("draft_suborder_count") or 1),
            "draft_suborder_ids": tx.get("draft_suborder_ids") or [],
        }
        pending_items.append(item)

    active_items, pending_items, override_config = portfolio_apply_manual_overrides(
        summary,
        active_items,
        pending_items,
        include_units,
        canonical_order,
        load_validation,
    )
    active_items, pending_items = portfolio_apply_order_aggregations(
        summary,
        active_items,
        pending_items,
        include_units,
        canonical_order,
        load_validation,
        override_config,
    )
    portfolio_freeze_report_orders(active_items, pending_items, canonical_order)
    if override_config.get("provider_note"):
        provider_warnings.append(str(override_config.get("provider_note")))
    for item in active_items:
        item["client_state"] = "active"
        item["client_display_pct"] = round_opt(item.get("variation_pct"), 2) if item.get("variation_pct") not in (None, "") else None
        item["client_phrase"] = portfolio_active_client_phrase(item.get("client_display_pct"))
    for item in pending_items:
        item["client_state"] = "pending"
        item["client_display_pct"] = round_opt(portfolio_pending_distance_to_current_pct(item), 2)
        item["client_phrase"] = portfolio_pending_client_phrase(item.get("client_display_pct"))
    ledger_warnings = portfolio_collect_ledger_warnings(
        summary,
        [
            *(item.get("symbol") for item in active_items),
            *(item.get("symbol") for item in pending_items),
        ],
    )

    message_lines = []
    client_lines = []
    portfolio_title = "Portafolio Sr. Eli"
    if override_config.get("portfolio_label"):
        portfolio_title += f" - {override_config.get('portfolio_label')}"
    identifier_prefix = str(override_config.get("identifier_prefix") or "").strip()
    client_presentation_mode = str(override_config.get("client_presentation_mode") or "combined").strip().lower()
    client_sort_mode = str(override_config.get("client_sort_mode") or "loss_to_gain").strip().lower()
    lines = [portfolio_title, "", "Portafolio ordenado para cliente:"]
    used_report_orders = set()
    next_report_order = 1
    if client_sort_mode == "loss_to_gain":
        sorted_active_items = sorted(active_items, key=lambda item: portfolio_client_sort_key(item, canonical_order))
        if client_presentation_mode == "combined":
            sorted_pending_items = sorted(pending_items, key=lambda item: portfolio_client_sort_key(item, canonical_order))
        else:
            sorted_pending_items = sorted(pending_items, key=lambda item: portfolio_override_sort_key(item, canonical_order))
    else:
        sorted_active_items = list(active_items)
        sorted_pending_items = list(pending_items)
    active_items = sorted_active_items
    pending_items = sorted_pending_items
    if client_presentation_mode == "combined" and client_sort_mode == "loss_to_gain":
        display_items = sorted([*active_items, *pending_items], key=lambda item: portfolio_client_sort_key(item, canonical_order))
        lines.append("Ordenado de mayor perdida a menor perdida; las pendientes se marcan en la misma linea.")
    else:
        display_items = [*active_items, *pending_items]
        if client_sort_mode == "loss_to_gain":
            lines.append("Posiciones activas de mayor perdida a mejor resultado; ordenes pendientes al final.")
    compact_client_ordering = boolish(override_config.get("compact_client_ordering", True))
    for item in display_items:
        keep_explicit_pending_id = (
            client_sort_mode == "loss_to_gain"
            and client_presentation_mode != "combined"
            and item.get("client_state") == "pending"
            and not compact_client_ordering
        )
        if client_sort_mode == "loss_to_gain" and not keep_explicit_pending_id:
            item["canonical_report_order"] = item.get("report_order")
            item["resolved_report_order"] = next_report_order
            used_report_orders.add(next_report_order)
            line_id = f"{identifier_prefix}{next_report_order}" if identifier_prefix else str(next_report_order)
            next_report_order += 1
        else:
            line_id, next_report_order = portfolio_resolve_line_identifier(
                item,
                next_report_order,
                used_report_orders,
                identifier_prefix,
            )
        amount_text = (
            f"total {format_usd_amount(item['invested_usd'])} USD"
            if item.get("merged_with_pending")
            else f"{format_usd_amount(item['invested_usd'])} USD"
        )
        label = str(item.get("label") or item.get("symbol") or "").strip()
        if item.get("client_state") == "pending" and "pendiente" not in label.lower():
            label += " pendiente"
        credit_mark = f" {item['credit_mark']}" if item.get("credit_mark") else ""
        line_parts = [
            f"{line_id}. {label}:",
            f"{amount_text} a {item['entry_price_display']}{credit_mark}.",
        ]
        if item["approved_for_client_report"]:
            line_parts.append(f"Precio actual {item['current_price_display']}.")
            line_parts.append(item["client_phrase"])
        else:
            line_parts.append("Precio actual no validado.")
            line_parts.append(item["client_phrase"])
        line = "\n".join(line_parts)
        if item.get("client_state") == "active":
            if item.get("merged_with_pending"):
                line += f"\n{portfolio_aggregation_client_note(item, identifier_prefix)}"
            elif item.get("aggregation"):
                line += f"\nAglomeracion: {item.get('aggregation_summary')}."
        if int(item.get("draft_suborder_count") or 1) > 1 and item.get("client_state") == "pending":
            line += f"\nAglomerada de {int(item.get('draft_suborder_count') or 1)} subordenes."
        if include_units and item.get("reference_quantity") is not None:
            line += f"\nUnidades de referencia: {item['reference_quantity']}."
        message_lines.append(line)
        client_lines.append(
            {
                "id": portfolio_normalize_client_id(line_id) or str(line_id).upper(),
                "display_id": line_id,
                "order": item.get("resolved_report_order"),
                "internal_order": item.get("canonical_report_order") or item.get("report_order"),
                "source_id": item.get("id") or (item.get("transaction_ids") or [""])[0],
                "symbol": item.get("symbol"),
                "label": label,
                "state": item.get("client_state"),
                "message": line,
                "approved_for_client_report": bool(item.get("approved_for_client_report")),
                "price_validation_status": item.get("price_validation_status"),
                "current_price": item.get("current_price"),
                "current_price_display": item.get("current_price_display"),
                "entry_price": item.get("entry_price"),
                "entry_price_display": item.get("entry_price_display"),
                "variation_pct": item.get("client_display_pct"),
                "variation_display": item.get("variation_display"),
                "client_phrase": item.get("client_phrase"),
                "credit_mark": item.get("credit_mark") or "",
                "is_consolidated": bool(
                    item.get("merged_with_pending")
                    or item.get("aggregation")
                    or item.get("consumed_orders")
                    or int(item.get("draft_suborder_count") or 1) > 1
                ),
                "blocked": not bool(item.get("approved_for_client_report")),
            }
        )
        lines.append(line)
    if executed_preliminary:
        lines.append("")
        lines.append(
            "Órdenes preliminares ya ejecutadas: "
            + ", ".join(item["label"] for item in executed_preliminary)
            + "."
        )
    if ledger_warnings:
        lines.append("")
        lines.append("Alertas de ledger:")
        for warning in ledger_warnings:
            lines.append(f"- {warning}")
    lines.append("")
    approved_active = [item for item in active_items if item.get("approved_for_client_report") and item.get("current_value_usd") is not None]
    unapproved_active = [item for item in active_items if not item.get("approved_for_client_report")]
    active_invested_usd = sum(float(item.get("invested_usd") or 0) for item in active_items)
    active_current_value_usd = sum(float(item.get("current_value_usd") or 0) for item in approved_active)
    active_unrealized_pnl_usd = sum(float(item.get("unrealized_pnl_usd") or 0) for item in approved_active)
    active_unrealized_pct = (
        (active_unrealized_pnl_usd / sum(float(item.get("invested_usd") or 0) for item in approved_active) * 100)
        if approved_active
        else None
    )
    pending_total_usd = sum(float(item.get("invested_usd") or 0) for item in pending_items)
    total_portfolio_usd = active_invested_usd + pending_total_usd
    accounting_config = portfolio_accounting_config(override_config)
    fee_summary = portfolio_fee_summary(active_items, summary, override_config)
    total_fee_usd = float(fee_summary.get("total_fee_usd") or 0)
    deposits = accounting_config.get("deposits") if isinstance(accounting_config.get("deposits"), list) else []
    deposits_total_usd = sum(
        float(item.get("amount_usd") or 0)
        for item in deposits
        if str((item or {}).get("status") or "confirmed").lower() == "confirmed"
    )
    operating_remnants_usd = float(accounting_config.get("operating_remnants_usd") or 0)
    closed_positions = (
        override_config.get("closed_positions")
        if isinstance(override_config.get("closed_positions"), list)
        else []
    )
    realized_gross_pnl_usd = sum(float(item.get("gross_pnl_usd") or 0) for item in closed_positions)
    realized_fee_usd = sum(float(item.get("fee_usd") or 0) for item in closed_positions)
    realized_net_pnl_usd = sum(float(item.get("net_pnl_usd") or 0) for item in closed_positions)
    available_balance_usd = operating_remnants_usd + max(0.0, realized_net_pnl_usd)
    configured_firm_capital = accounting_config.get("firm_capital_usd")
    if configured_firm_capital not in (None, ""):
        base_firm_capital_usd = float(configured_firm_capital)
        total_firm_usd = min(total_portfolio_usd, base_firm_capital_usd + available_balance_usd)
        total_credit_usd = max(0.0, total_portfolio_usd - total_firm_usd)
        base_only_credit_usd = max(0.0, total_portfolio_usd - base_firm_capital_usd)
        credit_source = "firm_capital_plus_available_realized_profit"
    else:
        base_firm_capital_usd = None
        total_credit_usd = sum(float(item.get("credit_usd") or 0) for item in [*active_items, *pending_items])
        total_firm_usd = max(0.0, total_portfolio_usd - total_credit_usd)
        base_only_credit_usd = total_credit_usd
        credit_source = "position_credit_marks"
    net_pnl_after_fees = active_unrealized_pnl_usd - total_fee_usd
    total_pnl_after_fees = net_pnl_after_fees + realized_net_pnl_usd
    gross_margin_total_pct = (
        (active_unrealized_pnl_usd / total_portfolio_usd * 100)
        if total_portfolio_usd
        else None
    )
    gross_margin_firm_pct = (
        (active_unrealized_pnl_usd / total_firm_usd * 100)
        if total_firm_usd
        else None
    )
    net_margin_total_pct = (
        (net_pnl_after_fees / total_portfolio_usd * 100)
        if total_portfolio_usd
        else None
    )
    net_margin_firm_pct = (
        (net_pnl_after_fees / total_firm_usd * 100)
        if total_firm_usd
        else None
    )
    total_margin_total_pct = (
        (total_pnl_after_fees / total_portfolio_usd * 100)
        if total_portfolio_usd
        else None
    )
    total_margin_firm_pct = (
        (total_pnl_after_fees / total_firm_usd * 100)
        if total_firm_usd
        else None
    )
    balance = {
        "portfolio_total_usd": round_opt(total_portfolio_usd, 2),
        "invested_total_usd": round_opt(total_portfolio_usd, 2),
        "credit_total_usd": round_opt(total_credit_usd, 2),
        "credit_base_only_usd": round_opt(base_only_credit_usd, 2),
        "firm_total_usd": round_opt(total_firm_usd, 2),
        "base_firm_capital_usd": round_opt(base_firm_capital_usd, 2) if base_firm_capital_usd is not None else None,
        "available_balance_usd": round_opt(available_balance_usd, 2),
        "credit_source": credit_source,
        "deposits_total_usd": round_opt(deposits_total_usd, 2),
        "deposits": deposits,
        "operating_remnants_usd": round_opt(operating_remnants_usd, 2),
        "operating_remnants_note": accounting_config.get("operating_remnants_note") or "",
        "active_invested_usd": round_opt(active_invested_usd, 2),
        "portfolio_current_value_usd_validated_only": round_opt(active_current_value_usd, 2),
        "portfolio_unrealized_pnl_usd_validated_only": round_opt(active_unrealized_pnl_usd, 2),
        "gross_margin_total_pct_validated_only": round_opt(gross_margin_total_pct, 2),
        "gross_margin_firm_pct_validated_only": round_opt(gross_margin_firm_pct, 2),
        "margin_total_pct_validated_only": round_opt(net_margin_total_pct, 2),
        "margin_firm_pct_validated_only": round_opt(net_margin_firm_pct, 2),
        "net_pnl_after_fees_usd": round_opt(net_pnl_after_fees, 2),
        "net_margin_total_pct_after_fees": round_opt(net_margin_total_pct, 2),
        "net_margin_firm_pct_after_fees": round_opt(net_margin_firm_pct, 2),
        "realized_closed_count": len(closed_positions),
        "realized_gross_pnl_usd": round_opt(realized_gross_pnl_usd, 2),
        "realized_fee_usd": round_opt(realized_fee_usd, 2),
        "realized_net_pnl_usd": round_opt(realized_net_pnl_usd, 2),
        "total_pnl_after_fees_usd": round_opt(total_pnl_after_fees, 2),
        "total_margin_total_pct_after_fees": round_opt(total_margin_total_pct, 2),
        "total_margin_firm_pct_after_fees": round_opt(total_margin_firm_pct, 2),
        "fees": fee_summary,
        "active_current_value_usd_validated_only": round_opt(active_current_value_usd, 2),
        "active_unrealized_pnl_usd_validated_only": round_opt(active_unrealized_pnl_usd, 2),
        "active_unrealized_pct_validated_only": round_opt(active_unrealized_pct, 2),
        "pending_orders_usd": round_opt(pending_total_usd, 2),
        "approved_active_count": len(approved_active),
        "active_count": len(active_items),
        "unapproved_active_symbols": [item.get("label") or item.get("symbol") for item in unapproved_active],
    }
    balance_line = (
        "Balance validado Sr. Eli: "
        f"total invertido/comprometido {format_usd_amount(balance['invested_total_usd'])} USD; "
        f"monto a crédito {format_usd_amount(balance['credit_total_usd'])} USD; "
        f"monto en firme {format_usd_amount(balance['firm_total_usd'])} USD; "
        f"saldo disponible {format_usd_amount(balance['available_balance_usd'])} USD; "
        f"depositos/fondeo confirmado {format_usd_amount(balance['deposits_total_usd'])} USD; "
        f"remanentes operativos {format_usd_amount(balance['operating_remnants_usd'])} USD; "
        f"valor actual del portafolio {format_usd_amount(balance['portfolio_current_value_usd_validated_only'])} USD; "
        f"P/L bruto {signed_usd_text(balance['portfolio_unrealized_pnl_usd_validated_only'])}; "
        f"fee operativo estimado {format_usd_amount(fee_summary['total_fee_usd'])} USD "
        f"({format_usd_amount(fee_summary['operation_fee_rate_pct'])}% sobre operaciones confirmadas; modificaciones no generan fee); "
        f"P/L abierto neto despues de fees {signed_usd_text(balance['net_pnl_after_fees_usd'])}; "
        f"P/L realizado neto {signed_usd_text(balance['realized_net_pnl_usd'])}; "
        f"P/L total neto {signed_usd_text(balance['total_pnl_after_fees_usd'])}; "
        f"margen neto sobre portafolio {signed_percent_text(balance['net_margin_total_pct_after_fees'])}; "
        f"margen neto sobre monto en firme {signed_percent_text(balance['net_margin_firm_pct_after_fees'])}; "
        f"margen total neto sobre portafolio {signed_percent_text(balance['total_margin_total_pct_after_fees'])}; "
        f"margen total neto sobre monto en firme {signed_percent_text(balance['total_margin_firm_pct_after_fees'])}."
    )
    if pending_items:
        balance_line += (
            f" Pendientes abiertos {format_usd_amount(balance['pending_orders_usd'])} USD; "
            "no entran al P/L hasta ejecutarse."
        )
    if unapproved_active:
        balance_line += " Balance parcial: faltan precios validados para " + ", ".join(balance["unapproved_active_symbols"]) + "."
    if ledger_warnings:
        balance_line += (
            f" Hay {len(ledger_warnings)} alerta(s) de ledger; revisa la seccion 'Alertas de ledger' "
            "antes de consolidar promedios, P/L o ventas."
        )
    lines.append(balance_line)
    lines.append("Regla de salida: no reportar unidades salvo que el doctor las pida.")

    result = {
        "ok": True,
        "report_type": "sr_eli_client_report",
        "generated_at": utc_now().isoformat(),
        "portfolio_id": summary.get("portfolio_id"),
        "hide_units_by_default": not include_units,
        "providers_used": providers,
        "provider_warnings": provider_warnings,
        "ledger_warnings": ledger_warnings,
        "source_warmup": source_warmup,
        "report_overrides": override_config,
        "active_positions": active_items,
        "executed_preliminary_orders": executed_preliminary,
        "pending_orders": pending_items,
        "balance": balance,
        "balance_line": balance_line,
        "client_lines": client_lines,
        "message_lines": message_lines,
        "whatsapp_messages": [*message_lines, balance_line],
        "summary": "\n".join(lines),
        "portfolio_summary": summary,
    }
    if boolish(first_value(parameters, "save_standard", "guardar_estandar", default=True)):
        result["portfolio_standard"] = portfolio_save_current_standard(summary, result)
    return result


def portfolio_fundamental_report_queries(report, parameters=None):
    parameters = parameters or {}
    symbols = []
    for item in [*(report.get("active_positions") or []), *(report.get("pending_orders") or [])]:
        symbol = str(item.get("symbol") or "").upper()
        if symbol and symbol not in symbols:
            symbols.append(symbol.replace("USDT", ""))
    portfolio_tokens = ", ".join(symbols or ["ADA", "DOGE", "FTT", "XRP", "LUNC", "APT", "DOT", "TRUMP", "PEPE", "HBAR", "NEAR"])
    date_label = dt.datetime.now(ZoneInfo(DEFAULT_SCHEDULER_TIMEZONE)).strftime("%Y-%m-%d")
    custom_query = str(first_value(parameters, "query", "question", "pregunta", "tema", default="")).strip()
    queries = [
        (
            f"{date_label} last 24 hours top international market catalysts Middle East geopolitics oil dollar risk appetite "
            "global liquidity markets latest trend follow-up from yesterday only if still moving markets"
        ),
        (
            f"{date_label} last 24 hours Federal Reserve interest rates inflation jobs FOMC officials comments treasury yields "
            "market expectations latest only material updates"
        ),
        (
            f"{date_label} last 24 hours most popular crypto market narratives opportunities BTC ETH SOL XRP DOGE ADA "
            "memecoins DeFi AI ETF regulation stocks popular market opportunities only fresh news"
        ),
        (
            f"{date_label} last 24 hours relevant news catalysts risks for portfolio tokens {portfolio_tokens} "
            "Aptos Polkadot Hedera Near Pepe Official Trump Terra Luna Classic only fresh material news"
        ),
    ]
    if custom_query:
        queries.insert(0, f"{date_label} {custom_query}")
    return queries


def portfolio_fundamental_fallback_text(report, research_results):
    source_count = sum(len(item.get("sources") or []) for item in research_results if isinstance(item, dict))
    balance = report.get("balance_line") or "El balance cuantitativo del portafolio queda pendiente de generar."
    return (
        "Buenos dias, senor Eli. Le compartimos nuestro informe de hoy:\n\n"
        "La base cuantitativa del Portafolio A ya quedo preparada, pero las fuentes de mercado disponibles "
        "en este intento no son suficientes para construir una lectura fundamental completa sin riesgo de "
        "reciclar informacion vieja. Por disciplina, no conviene presentar como catalizador aquello que no "
        "esta confirmado por fuentes recientes.\n\n"
        f"En el corte interno del portafolio, {balance} La lectura macro debe iniciar por el catalizador "
        "internacional mas importante del dia, continuar con Fed, tasas y liquidez solo si hay un evento "
        "realmente relevante, y cerrar con cripto unicamente cuando exista una noticia material para el "
        "mercado o para algun activo del portafolio.\n\n"
        f"Fuentes registradas en este intento: {source_count}. Si no se alcanza una validacion suficiente, "
        "la noticia debe marcarse como pendiente antes de enviarse al cliente."
    )


def portfolio_fundamental_report(summary, parameters=None):
    parameters = dict(parameters or {})
    report = portfolio_client_report(summary, {**parameters, "save_standard": True})
    dry_run = boolish(first_value(parameters, "dry_run", "preview_only", "solo_preview", "skip_research", default=False))
    try:
        max_queries = int(first_value(parameters, "max_queries", "research_queries", default=3) or 3)
    except (TypeError, ValueError):
        max_queries = 3
    max_queries = max(1, min(max_queries, 5))
    queries = portfolio_fundamental_report_queries(report, parameters)[:max_queries]
    research_results = []
    if not dry_run:
        for query in queries:
            try:
                research_results.append(research_with_openai(query, session_id=str(parameters.get("session_id") or "portfolio_sr_eli_fundamental")))
            except Exception as exc:
                research_results.append({"query": query, "error": brief(str(exc), 500), "sources": []})

    sources = []
    seen_urls = set()
    for item in research_results:
        for source in item.get("sources") or []:
            url = str(source.get("url") or "").strip()
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            sources.append({"title": source.get("title") or url, "url": url})

    if dry_run:
        synthesis_model = "local-preview"
        fundamental_text = portfolio_fundamental_fallback_text(report, research_results)
    else:
        prompt = (
            "Redacta un reporte fundamental profesional para el Dr. Yehoshua sobre el Portafolio A del Sr. Eli. "
            "Responde en español, claro y ejecutivo. No des asesoria financiera personalizada ni prometas rendimientos. "
            "Usa solo el reporte cuantitativo y la investigacion incluida. Si un catalizador no esta sustentado por fuente, "
            "marcalo como pendiente o no lo incluyas. Separa hechos verificados, inferencias y riesgos. "
            "Regla critica: las ordenes pendientes no son posiciones activas, no entran al P/L y su 'distancia vs entrada' "
            "no debe describirse como ganancia/rendimiento. NEAR A11 sigue pendiente hasta que el ledger diga lo contrario. "
            "Salida cliente obligatoria: redacta como texto listo para WhatsApp al Sr. Eli, con estilo de economista profesional e intelectual. "
            "Inicia exactamente con un saludo tipo 'Buenos dias, senor Eli. Le compartimos nuestro informe de hoy:'. "
            "No uses encabezados, bullets, listas numeradas, tablas ni desglose moneda por moneda salvo que el doctor lo pida explicitamente. "
            "Regla temporal critica: usa solo noticias de las ultimas 24 horas, o seguimiento de una noticia del dia anterior/hilo semanal/mensual "
            "solo si sigue moviendo el mercado hoy. No hagas panoramas generalistas del mes ni repitas contexto viejo como noticia de hoy. "
            "Escribe 2 a 4 parrafos corridos, densos y bien conectados. Usa estructura macro como guion interno: primero el catalizador internacional "
            "mas relevante y su tendencia; despues Fed/tasas/liquidez solo si hay evento real o fecha cercana; despues oportunidades populares en monedas, acciones o sectores; "
            "despues cripto y origen de movimientos; finalmente una frase de portafolio solo si hay noticia fresca y material para sus activos. "
            "Si no hay noticia relevante en cripto o en el portafolio, dilo con una frase breve, sin listar activos. "
            "Incluye cifras puntuales entre parentesis cuando esten disponibles en las fuentes, por ejemplo observado vs esperado vs previo. "
            "No repitas todos los dias Fed, tasas o geopolitica si no hay avance real. "
            "El objetivo es que suene como informe macrofinanciero serio, no como resumen de internet ni checklist operativo.\n\n"
            "REPORTE CUANTITATIVO:\n"
            f"{brief(report.get('summary', ''), 9000)}\n\n"
            "ESTADO ESTRUCTURADO DE POSICIONES:\n"
            f"{brief(json.dumps({'active_positions': report.get('active_positions', []), 'pending_orders': report.get('pending_orders', []), 'balance': report.get('balance', {})}, ensure_ascii=False), 9000)}\n\n"
            "INVESTIGACION Y FUENTES:\n"
            f"{brief(json.dumps(research_results, ensure_ascii=False), 18000)}\n\n"
            "ESTANDAR FUNDAMENTAL:\n"
            f"{json.dumps(portfolio_fundamental_report_standard(), ensure_ascii=False, indent=2)}"
        )
        try:
            response, synthesis_model = openai_response_with_fallback(
                DOCUMENT_MODEL_CANDIDATES,
                {"input": prompt, "max_output_tokens": 2200},
            )
            fundamental_text = output_text_from_response(response) or portfolio_fundamental_fallback_text(report, research_results)
        except Exception as exc:
            synthesis_model = "local-fallback"
            fundamental_text = portfolio_fundamental_fallback_text(report, research_results)
            research_results.append({"query": "synthesis", "error": brief(str(exc), 500), "sources": []})

    report_id = "sr_eli_fundamental_" + re.sub(r"[^0-9A-Za-z]+", "_", utc_now().isoformat()).strip("_")
    markdown = (
        f"# Reporte Fundamental Sr. Eli\n\n"
        f"- Report ID: {report_id}\n"
        f"- Generado: {now_iso()}\n"
        f"- Modelo sintesis: {synthesis_model}\n"
        f"- Fuentes validadas: {len(sources)}\n\n"
        f"{fundamental_text.strip()}\n\n"
        "## Fuentes\n"
        + "\n".join(f"- [{source.get('title')}]({source.get('url')})" for source in sources)
        + "\n"
    )
    md_paths = write_text_file_both(
        PORTFOLIO_SR_ELI_MEMORY_DIR / f"{report_id}.md",
        RUNTIME_PORTFOLIO_SR_ELI_MEMORY_DIR / f"{report_id}.md",
        markdown,
    )
    result = {
        "ok": True,
        "provider": "portfolio",
        "action": "fundamental_report",
        "report_id": report_id,
        "generated_at": now_iso(),
        "dry_run": dry_run,
        "portfolio_report": report,
        "queries": queries,
        "research_results": research_results,
        "sources": sources,
        "source_count": len(sources),
        "fundamental_report": fundamental_text,
        "markdown_paths": md_paths,
        "standard": portfolio_fundamental_report_standard(),
    }
    append_jsonl_any([PORTFOLIO_SR_ELI_FUNDAMENTAL_LOG, RUNTIME_PORTFOLIO_SR_ELI_FUNDAMENTAL_LOG], {k: v for k, v in result.items() if k != "portfolio_report"})
    append_memory("portfolio_fundamental_report", {"report_id": report_id, "source_count": len(sources), "dry_run": dry_run, "markdown_paths": md_paths})
    return result


def portfolio_fundamental_history(parameters=None):
    parameters = parameters or {}
    try:
        limit = int(first_value(parameters, "limit", "count", default=12) or 12)
    except (TypeError, ValueError):
        limit = 12
    limit = max(1, min(limit, 50))
    rows = []
    for path in [
        PORTFOLIO_SR_ELI_FUNDAMENTAL_LOG,
        LEGACY_PORTFOLIO_SR_ELI_MEMORY_DIR / "fundamental_reports.jsonl",
        RUNTIME_PORTFOLIO_SR_ELI_FUNDAMENTAL_LOG,
    ]:
        try:
            if not path.exists():
                continue
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError as exc:
            append_memory("portfolio_fundamental_history_read_error", {"path": str(path), "error": brief(str(exc), 500)})
            continue
        for line in lines:
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            report_id = item.get("report_id")
            if report_id and any(existing.get("report_id") == report_id for existing in rows):
                continue
            rows.append(item)
    rows.sort(key=lambda item: item.get("generated_at") or "", reverse=True)
    history = []
    for item in rows[:limit]:
        history.append(
            {
                "report_id": item.get("report_id"),
                "generated_at": item.get("generated_at"),
                "source_count": item.get("source_count"),
                "dry_run": item.get("dry_run"),
                "fundamental_report": item.get("fundamental_report"),
                "sources": item.get("sources") or [],
                "markdown_paths": item.get("markdown_paths") or {},
                "queries": item.get("queries") or [],
            }
        )
    return {
        "ok": True,
        "provider": "portfolio",
        "action": "fundamental_history",
        "count": len(history),
        "reports": history,
    }


def portfolio_default_whatsapp_target(parameters=None):
    parameters = parameters or {}
    raw = first_value(parameters, "to", "recipient", "phone", "telefono", "destinatario", default=DOCTOR_DUBAI_WHATSAPP_TO)
    target = str(raw or DOCTOR_DUBAI_WHATSAPP_TO).strip()
    if target and not target.startswith("whatsapp:"):
        normalized = normalize_phone_number(target)
        target = f"whatsapp:{normalized}" if normalized else target
    return target or DOCTOR_DUBAI_WHATSAPP_TO


def portfolio_target_is_doctor_control(target):
    return twilio_lookup_phone_number(target) == DOCTOR_DUBAI_WHATSAPP_NUMBER


def portfolio_client_lines_from_report(report):
    rows = []
    structured = report.get("client_lines") if isinstance(report.get("client_lines"), list) else []
    if structured:
        for item in structured:
            if not isinstance(item, dict):
                continue
            row = dict(item)
            row["id"] = portfolio_normalize_client_id(row.get("id") or row.get("display_id")) or str(row.get("id") or "").upper()
            rows.append(row)
        return rows
    for index, message in enumerate(report.get("message_lines") or [], start=1):
        rows.append(
            {
                "id": f"A{index}",
                "display_id": f"A{index}",
                "order": index,
                "message": str(message or ""),
                "approved_for_client_report": "precio actual no validado" not in str(message or "").lower(),
                "state": "",
                "symbol": "",
                "blocked": "precio actual no validado" in str(message or "").lower(),
            }
        )
    return rows


def portfolio_whatsapp_scope_from_parameters(parameters):
    parameters = parameters or {}
    scope = str(first_value(parameters, "send_scope", "scope", "selection_mode", "mode", default="all") or "all").strip().lower()
    has_ids = bool(portfolio_parse_client_ids(first_value(parameters, "ids", "client_ids", "selected_ids", "orders", default=[])))
    has_range = bool(first_value(parameters, "range", "id_range", "client_range", "from_to", default=""))
    has_symbols = bool(portfolio_values_list(first_value(parameters, "symbols", "symbol", "ticker", "asset", default=[])))
    has_state = bool(str(first_value(parameters, "state", "status", default="") or "").strip())
    if scope in {"all", "todo", "full", "complete"}:
        if has_range:
            return "range"
        if has_ids:
            return "ids"
        if has_symbols:
            return "symbols"
        if has_state:
            return "state"
    aliases = {
        "selected": "ids",
        "selection": "ids",
        "manual_selection": "ids",
        "seleccion": "ids",
        "rango": "range",
        "correccion": "correction",
        "correction_only": "correction",
        "pendientes": "state",
        "pending": "state",
        "activas": "state",
        "active": "state",
        "simbolos": "symbols",
        "symbols": "symbols",
    }
    return aliases.get(scope, scope or "all")


def portfolio_selected_client_lines(report, parameters=None):
    parameters = parameters or {}
    lines = portfolio_client_lines_from_report(report)
    scope = portfolio_whatsapp_scope_from_parameters(parameters)
    selected_ids = portfolio_parse_client_ids(first_value(parameters, "ids", "client_ids", "selected_ids", "orders", default=[]))
    range_ids = portfolio_parse_client_ids(first_value(parameters, "range", "id_range", "client_range", "from_to", default=[]))
    from_id = portfolio_normalize_client_id(first_value(parameters, "from_id", "start_id", "desde", default=""))
    to_id = portfolio_normalize_client_id(first_value(parameters, "to_id", "end_id", "hasta", default=""))
    if from_id and to_id:
        range_ids.update(portfolio_parse_client_ids(f"{from_id}-{to_id}"))
    symbols = {
        portfolio_normalize_symbol(symbol)
        for symbol in portfolio_values_list(first_value(parameters, "symbols", "symbol", "ticker", "asset", default=[]))
    }
    symbols.discard("")
    state = str(first_value(parameters, "state", "status", default="") or "").strip().lower()
    if scope == "pending" and not state:
        state = "pending"
        scope = "state"
    if scope == "active" and not state:
        state = "active"
        scope = "state"
    if scope == "range":
        selected_ids = range_ids
    elif scope == "correction":
        if range_ids:
            selected_ids = range_ids
            scope = "range"
        elif selected_ids:
            scope = "ids"
        elif symbols:
            scope = "symbols"
        else:
            raise ValueError("Para mandar una correccion necesito ids, rango o simbolos afectados; no voy a reenviar todo.")
    if scope == "all":
        selected = lines
    elif scope in {"ids", "range"}:
        if not selected_ids:
            raise ValueError("No hay IDs seleccionados para enviar por WhatsApp.")
        selected = [line for line in lines if portfolio_normalize_client_id(line.get("id")) in selected_ids]
    elif scope == "symbols":
        if not symbols:
            raise ValueError("No hay simbolos seleccionados para enviar por WhatsApp.")
        selected = [line for line in lines if portfolio_normalize_symbol(line.get("symbol")) in symbols]
    elif scope == "state":
        if state in {"pendiente", "pendientes"}:
            state = "pending"
        if state in {"activa", "activas", "mercado", "market"}:
            state = "active"
        if state not in {"active", "pending"}:
            raise ValueError("Estado no soportado para WhatsApp dinamico; usa active o pending.")
        selected = [line for line in lines if str(line.get("state") or "").strip().lower() == state]
    else:
        raise ValueError(f"Scope de WhatsApp no soportado: {scope}.")
    selected_ids_out = [str(line.get("id") or "").upper() for line in selected]
    missing_ids = sorted(selected_ids - set(selected_ids_out)) if selected_ids and scope in {"ids", "range"} else []
    return scope, selected, selected_ids_out, missing_ids


def portfolio_compose_whatsapp_messages(report, parameters=None):
    parameters = parameters or {}
    scope, selected, selected_ids, missing_ids = portfolio_selected_client_lines(report, parameters)
    if not selected:
        raise ValueError("La seleccion no genero lineas de portafolio para enviar.")
    allow_unvalidated = boolish(first_value(parameters, "allow_unvalidated", "permit_unvalidated", default=False))
    blocked_lines = [
        {
            "id": line.get("id"),
            "symbol": line.get("symbol"),
            "reason": line.get("price_validation_status") or "precio_actual_no_validado",
        }
        for line in selected
        if line.get("blocked")
        or not line.get("approved_for_client_report")
        or "precio actual no validado" in str(line.get("message") or "").lower()
    ]
    if blocked_lines and not allow_unvalidated:
        blocked_text = ", ".join(str(line.get("id") or line.get("symbol") or "?") for line in blocked_lines)
        raise ValueError(f"Reporte bloqueado: faltan precios validados para {blocked_text}.")
    include_balance_param = first_value(parameters, "include_balance", "balance", "include_totals", default=None)
    include_balance = boolish(include_balance_param) if include_balance_param is not None else scope == "all"
    messages = [str(line.get("message") or "").strip() for line in selected if str(line.get("message") or "").strip()]
    if include_balance and report.get("balance_line"):
        messages.append(str(report.get("balance_line")))
    preview = {
        "scope": scope,
        "selected_ids": selected_ids,
        "missing_ids": missing_ids,
        "include_balance": include_balance,
        "message_count": len(messages),
        "blocked_lines": blocked_lines,
        "first_message": messages[0] if messages else "",
        "balance_line": report.get("balance_line", "") if include_balance else "",
    }
    return {
        "messages": messages,
        "selected_lines": selected,
        "selected_ids": selected_ids,
        "missing_ids": missing_ids,
        "scope": scope,
        "include_balance": include_balance,
        "blocked_lines": blocked_lines,
        "preview": preview,
    }


def portfolio_send_whatsapp_report(summary, parameters=None):
    parameters = dict(parameters or {})
    parameters.setdefault("force_refresh_prices", True)
    target = portfolio_default_whatsapp_target(parameters)
    doctor_control = portfolio_target_is_doctor_control(target)
    dry_run = boolish(first_value(parameters, "dry_run", "preview_only", "solo_preview", default=False))
    confirmed = doctor_control or boolish(first_value(parameters, "confirm", "confirmed", "confirmed_by_doctor", "allow_send", default=False))
    report = portfolio_client_report(summary, {**parameters, "save_standard": False})
    compose_parameters = dict(parameters)
    if dry_run:
        compose_parameters.setdefault("allow_unvalidated", True)
    composed = portfolio_compose_whatsapp_messages(report, compose_parameters)
    messages = list(composed.get("messages") or [])
    if not messages:
        raise ValueError("No se generaron lineas de portafolio para enviar.")
    preview = {
        "to": target,
        "doctor_control_recipient": doctor_control,
        "message_count": len(messages),
        **composed.get("preview", {}),
        "providers_used": report.get("providers_used", []),
        "provider_warnings": report.get("provider_warnings", []),
    }
    if dry_run:
        return {
            "ok": True,
            "provider": "portfolio",
            "action": "send_whatsapp_report",
            "dry_run": True,
            "preview": preview,
            "messages": messages,
            "selected_lines": composed.get("selected_lines", []),
            "report": report,
        }
    if not confirmed:
        return confirmation_preview(
            "portfolio",
            "send_whatsapp_report",
            f"Enviar reporte actualizado Sr. Eli por WhatsApp a {target}.",
            preview,
            execution_parameters={**parameters, "to": target, "confirm": True},
        )
    context_id = str(first_value(parameters, "context_id", "kim_context_id", default="PORTFOLIO-SR-ELI-" + today()) or "").strip()
    send_results = []
    errors = []
    for index, message in enumerate(messages, start=1):
        try:
            event = twilio_send_message(
                {
                    "to": target,
                    "body": message,
                    "from": first_value(parameters, "from", "from_number", "sender", default=""),
                    "messaging_service_sid": first_value(parameters, "messaging_service_sid", "service_sid", default=""),
                    "context_id": context_id,
                    "contact_name": first_value(parameters, "contact_name", "client_name", "name", default="Dr. Yehoshua"),
                    "relationship": first_value(parameters, "relationship", default="doctor_control"),
                    "company": first_value(parameters, "company", default="Ignis Stock Financials"),
                    "objective": first_value(parameters, "objective", default="Enviar portafolio actualizado del Sr. Eli."),
                    "next_step_hint": first_value(parameters, "next_step_hint", default="Revisar reporte recibido en WhatsApp Dubai."),
                },
                confirm=True,
                channel="whatsapp",
            )
            send_results.append({"index": index, "sid": event.get("sid"), "status": event.get("status"), "to": event.get("to")})
            time.sleep(0.2)
        except Exception as exc:
            errors.append({"index": index, "error": brief(str(exc), 500), "message": brief(message, 220)})
            break
    delivery_results = []
    if send_results:
        time.sleep(float(first_value(parameters, "delivery_poll_delay_seconds", "poll_delay_seconds", default=1.2) or 1.2))
    for item in send_results:
        sid = item.get("sid")
        if not sid:
            continue
        try:
            status = twilio_request(f"/Messages/{sid}.json")
            delivery = {
                "index": item.get("index"),
                "sid": sid,
                "to": status.get("to") or item.get("to"),
                "status": status.get("status") or item.get("status"),
                "error_code": status.get("error_code"),
                "error_message": status.get("error_message"),
                "date_sent": status.get("date_sent"),
                "date_updated": status.get("date_updated"),
            }
            delivery_results.append(delivery)
            if delivery.get("status") in {"failed", "undelivered"}:
                errors.append(
                    {
                        "index": item.get("index"),
                        "sid": sid,
                        "status": delivery.get("status"),
                        "error_code": delivery.get("error_code"),
                        "error_message": delivery.get("error_message") or "Twilio accepted the request but WhatsApp did not deliver it.",
                    }
                )
        except Exception as exc:
            delivery_results.append({"index": item.get("index"), "sid": sid, "status": item.get("status"), "poll_error": brief(str(exc), 500)})
    accepted_statuses = {"accepted", "queued", "sending", "sent", "delivered", "read"}
    delivered_statuses = {"delivered", "read"}
    rejected_statuses = {"failed", "undelivered"}
    accepted_count = sum(1 for item in delivery_results if item.get("status") in accepted_statuses) or len(send_results)
    delivered_count = sum(1 for item in delivery_results if item.get("status") in delivered_statuses)
    rejected_count = sum(1 for item in delivery_results if item.get("status") in rejected_statuses)
    result = {
        "ok": not errors and rejected_count == 0,
        "provider": "portfolio",
        "action": "send_whatsapp_report",
        "to": target,
        "doctor_control_recipient": doctor_control,
        "context_id": context_id,
        "scope": composed.get("scope"),
        "selected_ids": composed.get("selected_ids", []),
        "message_count": len(messages),
        "messages": messages,
        "selected_lines": composed.get("selected_lines", []),
        "accepted_count": accepted_count,
        "sent_count": len(send_results),
        "delivered_count": delivered_count,
        "rejected_count": rejected_count,
        "send_results": send_results,
        "delivery_results": delivery_results,
        "errors": errors,
        "report": report,
        "sent_at": now_iso(),
    }
    append_jsonl_any(
        [
            MEMORY_ROOT / "portfolios" / "ignis_stock_financials" / "clientes" / "manejo_de_portafolios" / "sr_eli_2026" / "whatsapp_report_sends.jsonl",
            RUNTIME_MEMORY_ROOT / "portfolios" / "sr_eli_2026_whatsapp_report_sends.jsonl",
        ],
        result,
    )
    append_memory("portfolio_whatsapp_report_sent", {k: v for k, v in result.items() if k != "report"})
    return result


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
    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/oauth/zoom/start":
            try:
                url = zoom_oauth_start_url(self)
                self.send_response(302)
                self.send_header("Location", url)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
            except Exception:
                self.send_response(500)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
            return
        if parsed.path in {"/", "/index.html", "/oauth/zoom/callback", "/api/auth/status", "/twilio/health"}:
            self.send_response(200)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        if parsed.path in PUBLIC_ASSETS or parsed.path.startswith("/assets/kim/"):
            self.send_response(200)
            self.send_header("Cache-Control", "public, max-age=86400")
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()

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
        if parsed.path in PUBLIC_ASSETS:
            write_file_response(self, PUBLIC_ASSETS[parsed.path])
            return
        if parsed.path.startswith("/assets/kim/"):
            candidates = public_kim_asset_candidates(parsed.path)
            if candidates:
                write_file_response(self, candidates)
                return
        if parsed.path.startswith(WHATSAPP_PUBLIC_AUDIO_PATH_PREFIX + "/"):
            candidates = public_whatsapp_audio_candidates(parsed.path)
            if candidates:
                write_file_response(self, candidates, content_type="audio/mpeg", cache_control="public, max-age=86400")
                return
        if parsed.path == "/api/auth/status":
            status = site_auth_status(self)
            write_json(
                self,
                {
                    "ok": True,
                    "requires_auth": True,
                    "authenticated": bool(status.get("authenticated")),
                    "label": status.get("label", ""),
                    "expires_at": status.get("expires_at", ""),
                    "version": APP_VERSION,
                },
            )
            return
        if parsed.path.startswith("/api/") and not is_public_get_path(parsed.path) and not site_auth_is_valid(self):
            write_json(self, {"ok": False, "error": "AUTH_REQUIRED"}, status=401)
            return
        if parsed.path == "/api/bifrost-export/download":
            params = urllib.parse.parse_qs(parsed.query)
            token = (params.get("token") or [""])[0]
            try:
                send_bifrost_export_download(self, token)
            except Exception as exc:
                write_json(self, {"ok": False, "error": str(exc)}, status=403)
            return
        if parsed.path == "/api/bifrost-export/manifest":
            params = urllib.parse.parse_qs(parsed.query)
            token = (params.get("token") or [""])[0]
            try:
                send_bifrost_export_manifest(self, token)
            except Exception as exc:
                write_json(self, {"ok": False, "error": str(exc)}, status=403)
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
        if parsed.path == "/oauth/zoom/start":
            try:
                url = zoom_oauth_start_url(self)
            except Exception as exc:
                write_text(
                    self,
                    f"<h1>No pude iniciar Zoom OAuth</h1><p>{html.escape(str(exc))}</p>",
                    status=500,
                    content_type="text/html; charset=utf-8",
                )
                return
            self.send_response(302)
            self.send_header("Location", url)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        if parsed.path == "/oauth/zoom/callback":
            zoom_oauth_callback(self, parsed)
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
                    "realtime_voice": active_realtime_voice(),
                    "voice_profile": active_voice_profile(),
                },
            )
            return
        if parsed.path == "/twilio/voice":
            params = {key: values[-1] for key, values in urllib.parse.parse_qs(parsed.query).items()}
            try:
                response = twilio_voice_twiml(self, params)
            except Exception as exc:
                append_memory(
                    "twilio_voice_twiml_error",
                    {
                        "call_sid": params.get("CallSid", ""),
                        "from": params.get("From", ""),
                        "to": params.get("To", ""),
                        "method": "GET",
                        "error": brief(str(exc), 800),
                    },
                )
                response = twilio_voice_fallback_twiml(self, params, reason=brief(str(exc), 500))
            write_xml(self, response)
            return
        if parsed.path == "/twilio/status":
            params = {key: values[-1] for key, values in urllib.parse.parse_qs(parsed.query).items()}
            run_background_task("twilio-status-callback", twilio_status_callback, params)
            write_text(self, "", content_type="text/plain; charset=utf-8")
            return
        if parsed.path == "/twilio/health":
            write_json(self, {"ok": True, "service": "kim_twilio", "version": APP_VERSION, "realtime": twilio_realtime_health_status()})
            return
        if parsed.path == "/twilio/realtime-health":
            write_json(self, {"ok": True, "service": "kim_twilio_realtime", "version": APP_VERSION, "realtime": twilio_realtime_health_status()})
            return
        if parsed.path == "/api/openai-status":
            model = openai_json(f"/models/{REALTIME_MODEL}")
            write_json(
                self,
                {
                    "ok": True,
                    "configured": True,
                    "model": model.get("id", REALTIME_MODEL),
                    "realtime_voice": active_realtime_voice(),
                    "voice_profile": active_voice_profile(),
                },
            )
            return
        if parsed.path == "/api/voice-profile":
            write_json(self, {"ok": True, "profile": active_voice_profile(), "options": KIM_VOICE_OPTIONS})
            return
        if parsed.path == "/api/context":
            write_json(self, load_context_bundle())
            return
        if parsed.path == "/api/api-bridge/status":
            write_json(self, {"ok": True, "status": api_bridge_config_status(live=True)})
            return
        if parsed.path == "/api/paper-trading":
            write_json(self, {"ok": True, "result": paper_broker_cli("status", {})})
            return
        if parsed.path == "/api/local-clock":
            write_json(self, local_clock_status())
            return
        if parsed.path == "/api/schedules":
            params = urllib.parse.parse_qs(parsed.query)
            write_json(
                self,
                {
                    "ok": True,
                    "timezone": DEFAULT_SCHEDULER_TIMEZONE,
                    "schedules": list_scheduled_actions(
                        status=(params.get("status") or [""])[0],
                        limit=int((params.get("limit") or ["100"])[0] or 100),
                    ),
                },
            )
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
        if parsed.path == "/api/person-context":
            params = urllib.parse.parse_qs(parsed.query)
            query = (params.get("query") or params.get("q") or params.get("name") or [""])[0]
            limit = int((params.get("limit") or ["1"])[0] or 1)
            write_json(self, person_context_supervision_payload(query=query, limit=limit))
            return
        if parsed.path == "/api/whatsapp/threads":
            params = urllib.parse.parse_qs(parsed.query)
            write_json(
                self,
                whatsapp_threads_report(
                    limit=(params.get("limit") or ["8"])[0],
                    thread_id=(params.get("thread_id") or [""])[0],
                    phone=(params.get("phone") or params.get("from") or [""])[0],
                ),
            )
            return
        if parsed.path == "/api/notifications":
            params = urllib.parse.parse_qs(parsed.query)
            limit = int((params.get("limit") or ["25"])[0] or 25)
            write_json(self, {"ok": True, "notifications": list_kim_live_notifications(limit=limit)})
            return
        if parsed.path == "/api/whatsapp-summary":
            params = urllib.parse.parse_qs(parsed.query)
            limit = int((params.get("limit") or ["12"])[0] or 12)
            rows = list_whatsapp_thread_summaries(limit=limit)
            write_json(
                self,
                {
                    "ok": True,
                    "generated_at": now_iso(),
                    "count": len(rows),
                    "overview": whatsapp_overview_text(limit=limit),
                    "threads": rows,
                },
            )
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
                {"model": REALTIME_MODEL, "voice": active_realtime_voice()},
            )
            write_json(self, token)
            return
        self.send_error(404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        try:
            if parsed.path == "/api/auth/login":
                body = read_body(self)
                token, payload, status = login_site_user(self, body)
                data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
                self.send_response(status)
                if token:
                    send_auth_cookie(self, token)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            if parsed.path == "/api/auth/logout":
                token = cookie_token(self)
                if token:
                    state = load_site_auth_state()
                    state.get("sessions", {}).pop(token_hash(token), None)
                    save_site_auth_state(state)
                data = json.dumps({"ok": True, "authenticated": False}, ensure_ascii=False, indent=2).encode("utf-8")
                self.send_response(200)
                send_auth_cookie(self, "", max_age=0)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            if parsed.path == "/api/public-lead":
                body = read_body(self)
                lead = record_public_lead(self, body)
                write_json(self, {"ok": True, "lead": lead})
                return
            if parsed.path == "/api/tradingview/webhook":
                body = read_body(self)
                payload, status = tradingview_webhook_payload(body, self, parsed)
                write_json(self, payload, status=status)
                return
            if parsed.path.startswith("/api/") and not is_public_post_path(parsed.path) and not site_auth_is_valid(self):
                write_json(self, {"ok": False, "error": "AUTH_REQUIRED"}, status=401)
                return
            if parsed.path == "/twilio/voice":
                params = read_form(self)
                try:
                    response = twilio_voice_twiml(self, params)
                except Exception as exc:
                    append_memory(
                        "twilio_voice_twiml_error",
                        {
                            "call_sid": params.get("CallSid", ""),
                            "from": params.get("From", ""),
                            "to": params.get("To", ""),
                            "error": brief(str(exc), 800),
                        },
                )
                    response = twilio_voice_fallback_twiml(self, params, reason=brief(str(exc), 500))
                write_xml(self, response)
                return
            if parsed.path == "/twilio/gather":
                params = read_form(self)
                write_xml(self, twilio_gather_twiml(self, params))
                return
            if parsed.path == "/twilio/status":
                params = read_form(self)
                run_background_task("twilio-status-callback", twilio_status_callback, params)
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
                    {"model": REALTIME_MODEL, "voice": active_realtime_voice(), "transport": "unified"},
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
            if parsed.path == "/api/bifrost-export":
                validate_bifrost_export_authorization(
                    pin=body.get("pin", ""),
                    phrase=body.get("phrase", ""),
                )
                result = create_bifrost_export_zip(label=body.get("label", "Kim Live secure export"))
                write_json(self, result)
                return
            if parsed.path == "/api/voice-profile":
                profile = save_voice_profile(body)
                write_json(self, {"ok": True, "profile": profile, "options": KIM_VOICE_OPTIONS})
                return
            if parsed.path == "/api/voice-preview":
                voice = str(body.get("voice") or active_tts_voice()).strip()
                text = str(body.get("text") or "Hola, soy Kim. Esta es una prueba breve de mi voz.").strip()
                audio = generate_whatsapp_reply_audio(brief(text, 420), "VOICE-PREVIEW-" + secrets.token_hex(3).upper(), voice=voice)
                write_json(self, {"ok": True, "audio": audio, "voice": voice_option(voice)})
                return
            if parsed.path == "/api/say":
                text = body.get("text", "")
                speak(text)
                append_memory("spoken_reply", {"text": text})
                write_json(self, {"ok": True})
                return
            if parsed.path == "/api/save":
                text = body.get("text", "")
                silent = bool(body.get("silent"))
                path = None if silent else append_memory("conversation_note", {"text": text})
                call_path = None
                call_entry = None
                if body.get("session_id"):
                    call_path, call_entry = save_call_record(body)
                if not silent:
                    append_daily_note(text)
                write_json(
                    self,
                    {
                        "ok": True,
                        "saved_to": str(path) if path else None,
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
            if parsed.path == "/api/schedules/cancel":
                result = cancel_scheduled_action(body.get("scheduled_action_id") or body.get("schedule_id") or body.get("id"))
                write_json(self, {"ok": True, "result": result})
                return
            if parsed.path == "/api/portfolio":
                try:
                    portfolio_action = str(body.get("action", "status") or "status").strip().lower()
                    portfolio_parameters = body.get("parameters") or {}
                    portfolio_confirm = bool(body.get("confirm", False)) or boolish(portfolio_parameters.get("confirm"))
                    if portfolio_action in PORTFOLIO_CONFIRMABLE_ACTIONS:
                        result = run_api_bridge(
                            "portfolio",
                            portfolio_action,
                            portfolio_parameters,
                            confirm=portfolio_confirm,
                            session_id=body.get("session_id", ""),
                            transcript=body.get("transcript", ""),
                        )
                    else:
                        result = portfolio_cli(portfolio_action, portfolio_parameters)
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
            if parsed.path == "/api/paper-trading":
                try:
                    paper_action = str(body.get("action", "status") or "status").strip().lower()
                    paper_parameters = body.get("parameters") or {}
                    paper_confirm = bool(body.get("confirm", False)) or boolish(paper_parameters.get("confirm"))
                    if paper_action in PAPER_BROKER_CONFIRMABLE_ACTIONS:
                        result = run_api_bridge(
                            "paper_broker",
                            paper_action,
                            paper_parameters,
                            confirm=paper_confirm,
                            session_id=body.get("session_id", ""),
                            transcript=body.get("transcript", ""),
                        )
                    else:
                        result = paper_broker_cli(paper_action, paper_parameters, confirm=paper_confirm)
                except Exception as exc:
                    result = {
                        "ok": False,
                        "provider": "paper_broker",
                        "action": body.get("action", "status"),
                        "error": str(exc),
                        "message": "No pude completar la accion del paper broker.",
                    }
                    append_memory("paper_broker_error", result)
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
            if parsed.path == "/api/memory-search":
                result = search_memory_transcripts(
                    query=body.get("query", ""),
                    session_id=body.get("session_id", ""),
                    limit=body.get("limit", 6),
                    max_chars=body.get("max_chars", 1600),
                )
                write_json(self, {"ok": True, "result": result})
                return
            if parsed.path == "/api/person-context":
                result = person_context_supervision_payload(
                    query=body.get("query") or body.get("name") or body.get("text") or "",
                    limit=body.get("limit", 1),
                )
                write_json(self, {"ok": True, "result": result})
                return
            if parsed.path == "/api/whatsapp/threads":
                result = whatsapp_threads_report(
                    limit=body.get("limit", 8),
                    thread_id=body.get("thread_id") or body.get("id") or "",
                    phone=body.get("phone") or body.get("from") or "",
                )
                write_json(self, {"ok": True, "result": result})
                return
            if parsed.path == "/api/conversation-review":
                result = conversation_review(
                    text=body.get("text", ""),
                    session_id=body.get("session_id", ""),
                    mode=body.get("mode", "auto"),
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
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception as exc:
            write_json(self, {"ok": False, "error": str(exc)}, status=500)

    def log_message(self, fmt, *args):
        stamp = now_iso()
        print(f"{stamp} {self.address_string()} {fmt % args}", flush=True)


class KimThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def main():
    MEMORY_INBOX.mkdir(parents=True, exist_ok=True)
    start_scheduler_once()
    start_paper_broker_watcher_once()
    server = KimThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Kim Live running at http://{HOST}:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
