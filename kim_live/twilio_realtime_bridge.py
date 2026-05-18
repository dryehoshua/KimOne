#!/usr/bin/env python3
"""
Twilio Media Streams <-> OpenAI Realtime bridge for Kim Live.
"""

import asyncio
import json
import pathlib
import urllib.parse

import websockets

import server as kim


HOST = "127.0.0.1"
PORT = 8766
REALTIME_WS = f"wss://api.openai.com/v1/realtime?model={kim.REALTIME_MODEL}"
LOG_PATH = pathlib.Path("/Users/dryehoshuapython/.kim_live/twilio_realtime_bridge.log")

LOG_EVENT_TYPES = {
    "error",
    "session.created",
    "session.updated",
    "input_audio_buffer.committed",
    "input_audio_buffer.speech_started",
    "input_audio_buffer.speech_stopped",
    "conversation.item.input_audio_transcription.completed",
    "response.done",
    "rate_limits.updated",
}


def log(message):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(f"{kim.now_iso()} {message}\n")
    print(message, flush=True)


def inbound_profile_from_context(call_context=None):
    call_context = call_context or {}
    profile = call_context.get("inbound_caller_profile") or {}
    return profile if isinstance(profile, dict) else {}


def inbound_contact_label(call_context=None, fallback=""):
    profile = inbound_profile_from_context(call_context)
    if profile.get("is_doctor"):
        return "Dr. Yehoshua"
    return call_context.get("contact_name") or profile.get("display_name") or fallback or "la persona que llama"


def bridge_session_config(call_sid="", caller="", called="", call_context=None):
    local_context = kim.context_brief()
    call_context = call_context or {}
    if call_context and call_context.get("direction") == "inbound":
        profile = inbound_profile_from_context(call_context)
        known = bool(profile.get("known_contact") or profile.get("is_doctor"))
        label = inbound_contact_label(call_context, caller)
        mission = (
            "MODO RECEPCION / SECRETARIA ENTRANTE.\n"
            "La persona esta llamando al numero de Kim/Dr. Yehoshua. Actua como secretaria ejecutiva de recepcion, "
            "no como IVR. Tu trabajo es escuchar, orientar y registrar.\n"
            "Primero saluda como Kim, asistente del Dr. Yehoshua. Si el numero coincide con un perfil conocido, "
            f"confirma con suavidad si hablas con {label}; si no coincide, pide nombre completo, empresa y motivo.\n"
            "Puedes atender clientes, proveedores, inversionistas o interesados en Tesca Elements, Ignis, Ai People u otros proyectos. "
            "Da informacion general de servicios y toma recados, pero no inventes datos especificos.\n"
            "Regla de privacidad: solo puedes hablar de pendientes propios del llamante si la identidad es clara. "
            "No reveles tareas de terceros, datos de otros clientes ni pendientes generales del doctor. Si piden algo sensible, "
            "di que lo registras para que el doctor lo revise.\n\n"
            f"Numero reconocido: {'si' if known else 'no'}\n"
            f"Perfil esperado: {label}\n"
            f"Relacion: {call_context.get('relationship', '')}\n"
            f"Empresa: {call_context.get('company', '')}\n"
            f"Contexto permitido: {call_context.get('call_context', '')}\n"
            f"Objetivo: {call_context.get('objective', '')}\n"
            f"Preguntas que debes hacer: {call_context.get('questions', '')}\n"
            f"Que debes reportar al doctor: {call_context.get('report_to_doctor', '')}\n"
            f"Criterio de exito: {call_context.get('success_criteria', '')}\n"
            f"Tono: {call_context.get('tone', '')}\n"
        )
    elif call_context:
        mission = (
            "MODO LLAMADA CON CONTEXTO A TERCERO.\n"
            "La persona que contesta NO necesariamente es el doctor. No la saludes como doctor.\n"
            "Presentate como Kim, asistente del Dr. Yehoshua, y ejecuta la mision concreta.\n"
            "Tu primera frase debe saludar al destinatario por nombre si lo tienes y decir que eres Kim, "
            "asistente del Dr. Yehoshua. Nunca arranques con 'hola doctor' en este modo.\n"
            "No digas que no sabes el contexto; el contexto esta abajo. Haz preguntas claras, escucha la respuesta, "
            "agradece y cierra con naturalidad. No leas el contexto completo en voz alta: usalo para actuar. "
            "Al final la llamada se guardara para reportar al doctor.\n\n"
            f"Destinatario: {call_context.get('contact_name') or called}\n"
            f"Relacion: {call_context.get('relationship', '')}\n"
            f"Empresa: {call_context.get('company', '')}\n"
            f"Contexto: {call_context.get('call_context', '')}\n"
            f"Objetivo: {call_context.get('objective', '')}\n"
            f"Mensaje a transmitir: {call_context.get('message_to_deliver', '')}\n"
            f"Preguntas que debes hacer: {call_context.get('questions', '')}\n"
            f"Que debes reportar al doctor: {call_context.get('report_to_doctor', '')}\n"
            f"Criterio de exito: {call_context.get('success_criteria', '')}\n"
            f"Tono: {call_context.get('tone', '')}\n"
            f"Extracto de conversacion que origino la llamada: {call_context.get('conversation_excerpt', '')}\n"
        )
    else:
        mission = (
            "Eres Kim Live hablando por telefono con Dr Yehoshua. "
            "Escucha instrucciones, conversa breve, y cuando el doctor pida una tarea confirma que queda "
            "registrada en BIFROST/Kim Live. No uses tono de IVR. Si no puedes ejecutar una accion "
            "directamente desde la llamada, di claramente que la guardas para ejecucion."
        )
    return {
        "type": "session.update",
        "session": {
            "type": "realtime",
            "model": kim.REALTIME_MODEL,
            "output_modalities": ["audio"],
            "instructions": (
                "Habla en espanol mexicano, femenino, natural y fluido. "
                "Esta llamada viene por Twilio Media Streams: comparte memoria y tono con Kim Local, "
                "pero es un canal telefonico distinto de la interfaz local/web. "
                f"{mission}\n\n"
                f"CallSid: {call_sid}\nFrom: {caller}\nTo: {called}\n\n"
                f"MEMORIA LOCAL BIFROST:\n{local_context}"
            ),
            "audio": {
                "input": {
                    "format": {"type": "audio/pcmu"},
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 650,
                    },
                    "transcription": {
                        "model": "gpt-4o-mini-transcribe",
                        "language": "es",
                    },
                },
                "output": {
                    "format": {"type": "audio/pcmu"},
                    "voice": kim.REALTIME_VOICE,
                },
            },
        },
    }


def initial_greeting_event(call_context=None):
    call_context = call_context or {}
    if call_context and call_context.get("direction") == "inbound":
        profile = inbound_profile_from_context(call_context)
        label = inbound_contact_label(call_context)
        if profile.get("is_doctor"):
            greeting_instruction = (
                "Saluda al Dr. Yehoshua con naturalidad como Kim. Dile que estas en modo llamada telefonica "
                "y pregunta que necesita revisar o ejecutar ahora."
            )
        elif profile.get("known_contact"):
            greeting_instruction = (
                "Contesta como secretaria ejecutiva: 'Hola, habla Kim, asistente del Dr. Yehoshua. "
                f"¿Tengo el gusto de hablar con {label}?'. Despues pregunta en que puedes ayudar. "
                "No reveles pendientes hasta que confirme identidad."
            )
        else:
            greeting_instruction = (
                "Contesta como secretaria ejecutiva: 'Hola, habla Kim, asistente del Dr. Yehoshua. "
                "¿Con quien tengo el gusto y en que puedo ayudarle?'. Pide empresa, motivo y si llama por Tesca Elements, Ignis, Ai People u otro proyecto."
            )
    elif call_context:
        greeting_instruction = (
            "Esta llamada es para una tercera persona. Presentate como Kim, asistente del Dr. Yehoshua. "
            f"La persona objetivo es {call_context.get('contact_name') or 'el destinatario'}. "
            f"Ejecuta esta mision desde el primer turno: {call_context.get('objective') or call_context.get('instructions') or call_context.get('call_context')}. "
            "Primera frase recomendada: 'Hola, soy Kim, asistente del Dr. Yehoshua'. "
            "No digas 'hola doctor' salvo que confirmes que quien contesta es el doctor."
        )
    else:
        greeting_instruction = (
            "Saluda al doctor en español con una frase breve. "
            "Dile que esta es la version Realtime por telefono y que ya puede hablarte."
        )
    return {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": greeting_instruction,
                }
            ],
        },
    }


async def send_mark(twilio_ws, stream_sid, mark_queue):
    if not stream_sid:
        return
    await twilio_ws.send(
        json.dumps(
            {
                "event": "mark",
                "streamSid": stream_sid,
                "mark": {"name": "kim-response"},
            }
        )
    )
    mark_queue.append("kim-response")


async def save_twilio_realtime_call(session_id, caller, called, transcript, call_sid, context_id="", call_context=None):
    call_context = call_context or {}
    profile = inbound_profile_from_context(call_context)
    speaker_label = inbound_contact_label(call_context, "Llamante") if call_context.get("direction") == "inbound" else "Dr. Yehoshua"
    rendered_transcript = []
    for line in transcript:
        if call_context.get("direction") == "inbound" and line.startswith("Dr. Yehoshua:"):
            rendered_transcript.append(line.replace("Dr. Yehoshua:", f"{speaker_label}:", 1))
        else:
            rendered_transcript.append(line)
    text = (
        "Canal: Twilio Media Streams + OpenAI Realtime\n"
        f"CallSid: {call_sid}\n"
        f"From: {caller}\n"
        f"To: {called}\n\n"
        + (
            "## Call Context\n"
            f"- Context ID: {context_id}\n"
            f"- Contact: {call_context.get('contact_name', '')}\n"
            f"- Direction: {call_context.get('direction', '')}\n"
            f"- Known caller: {profile.get('known_contact', '')}\n"
            f"- Objective: {call_context.get('objective', '')}\n"
            f"- Report requested: {call_context.get('report_to_doctor', '')}\n\n"
            if call_context
            else ""
        )
        + "\n".join(rendered_transcript).strip()
    )
    try:
        call_path, entry = kim.save_call_record(
            {
                "session_id": session_id,
                "text": text,
                "started_at": kim.now_iso(),
                "title": f"Twilio Realtime call {call_context.get('contact_name') or caller or 'unknown'}",
            }
        )
        kim.complete_twilio_call_context(
            call_sid=call_sid or "",
            context_id=context_id or call_context.get("id", ""),
            transcript_path=str(call_path),
            summary=entry.get("summary", ""),
            status="transcribed",
        )
        kim.crm_record_interaction(
            "call",
            "inbound" if caller and caller != kim.twilio_default_from_number() else "outbound",
            from_value=caller or "",
            to_value=called or "",
            status="transcribed",
            body=kim.brief(text, 1800),
            external_sid=call_sid or "",
            transcript_path=str(call_path),
            metadata={
                "source": "twilio_realtime_bridge",
                "session_id": session_id,
                "call_number": entry.get("call_number"),
                "context_id": context_id or call_context.get("id", ""),
                "call_context": call_context,
            },
            contact_hint={
                "display_name": call_context.get("contact_name") or profile.get("display_name", ""),
                "company": call_context.get("company", ""),
                "notes": call_context.get("relationship") or call_context.get("call_context", ""),
            },
        )
    except Exception as exc:
        kim.append_memory(
            "twilio_realtime_save_error",
            {"session_id": session_id, "error": kim.brief(str(exc), 500)},
        )


async def handle_media_stream(twilio_ws):
    request_path = getattr(getattr(twilio_ws, "request", None), "path", "/twilio/media")
    query = urllib.parse.parse_qs(urllib.parse.urlparse(request_path).query)
    caller = (query.get("from") or [""])[0]
    called = (query.get("to") or [""])[0]
    call_sid = (query.get("callSid") or [""])[0]
    context_id = (query.get("kim_context_id") or [""])[0]
    call_context = kim.load_twilio_call_context(call_sid=call_sid, context_id=context_id)
    session_id = kim.phone_session_id({"CallSid": call_sid}) if call_sid else "PHONE-RT-" + kim.now_iso()

    stream_sid = None
    latest_media_timestamp = 0
    last_assistant_item = None
    response_start_timestamp_twilio = None
    mark_queue = []
    transcript = []

    kim.append_memory(
        "twilio_realtime_connected",
        {"session_id": session_id, "caller": caller, "called": called, "call_sid": call_sid, "context_id": context_id, "has_call_context": bool(call_context)},
    )
    log(f"Twilio connected session={session_id}")

    headers = {
        "Authorization": f"Bearer {kim.load_openai_key()}",
        "OpenAI-Safety-Identifier": "dr-yehoshua-kim-twilio-realtime",
    }
    async with websockets.connect(REALTIME_WS, additional_headers=headers) as openai_ws:
        configured = False

        async def configure_openai_session():
            nonlocal configured
            if configured:
                return
            await openai_ws.send(
                json.dumps(
                    bridge_session_config(
                        call_sid=call_sid,
                        caller=caller,
                        called=called,
                        call_context=call_context,
                    )
                )
            )
            await openai_ws.send(json.dumps(initial_greeting_event(call_context=call_context)))
            await openai_ws.send(json.dumps({"type": "response.create"}))
            configured = True
            log(
                "OpenAI session configured "
                f"call_sid={call_sid or '-'} context_id={context_id or '-'} has_context={bool(call_context)}"
            )

        async def receive_from_twilio():
            nonlocal stream_sid, latest_media_timestamp, response_start_timestamp_twilio, last_assistant_item, caller, called, call_sid, session_id, context_id, call_context
            async for message in twilio_ws:
                data = json.loads(message)
                event = data.get("event")
                if event == "start":
                    start = data.get("start", {})
                    stream_sid = start.get("streamSid")
                    custom = start.get("customParameters") or {}
                    call_sid = start.get("callSid") or custom.get("callSid") or call_sid
                    caller = caller or custom.get("from", "")
                    called = called or custom.get("to", "")
                    context_id = context_id or custom.get("kim_context_id", "")
                    if not call_context and (call_sid or context_id):
                        call_context = kim.load_twilio_call_context(call_sid=call_sid, context_id=context_id)
                    if call_sid and session_id.startswith("PHONE-RT-"):
                        session_id = kim.phone_session_id({"CallSid": call_sid})
                    call = call_sid
                    if call and not transcript:
                        transcript.append(f"[system] Twilio Media Stream iniciado: {call}")
                    response_start_timestamp_twilio = None
                    latest_media_timestamp = 0
                    last_assistant_item = None
                    await configure_openai_session()
                    log(f"Stream started {stream_sid}")
                elif event == "media":
                    if not configured:
                        await configure_openai_session()
                    latest_media_timestamp = int(data.get("media", {}).get("timestamp") or 0)
                    payload = data.get("media", {}).get("payload")
                    if payload:
                        await openai_ws.send(
                            json.dumps({"type": "input_audio_buffer.append", "audio": payload})
                        )
                elif event == "mark":
                    if mark_queue:
                        mark_queue.pop(0)
                elif event == "stop":
                    log(f"Stream stopped {stream_sid}")
                    break
            await openai_ws.close()

        async def send_to_twilio():
            nonlocal last_assistant_item, response_start_timestamp_twilio, stream_sid
            async for raw in openai_ws:
                response = json.loads(raw)
                event_type = response.get("type")
                if event_type in LOG_EVENT_TYPES:
                    log(f"OpenAI event {event_type}")
                if event_type == "response.output_audio.delta" and response.get("delta") and stream_sid:
                    await twilio_ws.send(
                        json.dumps(
                            {
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {"payload": response["delta"]},
                            }
                        )
                    )
                    if response.get("item_id") and response.get("item_id") != last_assistant_item:
                        response_start_timestamp_twilio = latest_media_timestamp
                        last_assistant_item = response["item_id"]
                    await send_mark(twilio_ws, stream_sid, mark_queue)
                elif event_type == "input_audio_buffer.speech_started":
                    if last_assistant_item and mark_queue and response_start_timestamp_twilio is not None:
                        elapsed = max(0, latest_media_timestamp - response_start_timestamp_twilio)
                        await openai_ws.send(
                            json.dumps(
                                {
                                    "type": "conversation.item.truncate",
                                    "item_id": last_assistant_item,
                                    "content_index": 0,
                                    "audio_end_ms": elapsed,
                                }
                            )
                        )
                        if stream_sid:
                            await twilio_ws.send(json.dumps({"event": "clear", "streamSid": stream_sid}))
                        mark_queue.clear()
                        last_assistant_item = None
                        response_start_timestamp_twilio = None
                elif event_type == "conversation.item.input_audio_transcription.completed":
                    text = (response.get("transcript") or "").strip()
                    if text:
                        transcript.append(f"Dr. Yehoshua: {text}")
                elif event_type == "response.output_audio_transcript.done":
                    text = (response.get("transcript") or "").strip()
                    if text:
                        transcript.append(f"Kim: {text}")

        try:
            await asyncio.gather(receive_from_twilio(), send_to_twilio())
        finally:
            await save_twilio_realtime_call(session_id, caller, called, transcript, call_sid, context_id=context_id, call_context=call_context)
            log(f"Saved session={session_id}")


async def main():
    async with websockets.serve(handle_media_stream, HOST, PORT, ping_interval=20, ping_timeout=20):
        log(f"Kim Twilio Realtime bridge running ws://{HOST}:{PORT}/twilio/media")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
