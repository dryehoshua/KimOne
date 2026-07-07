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
        identity_instruction = (
            f"The caller matches a known profile: greet {label} by name and continue that contact's prior thread; "
            "confirm identity gently only if there is uncertainty.\n"
            if known
            else "The caller does not match a known profile: briefly explain AI People and ask first for their name, then company and reason for calling.\n"
        )
        mission = (
            "INBOUND RECEPTION / EXECUTIVE SECRETARY MODE.\n"
            "The person is calling Kim/Dr. Yehoshua's number. Act as an executive receptionist, "
            "not as an IVR. Your job is to listen, orient and register.\n"
            "First greet in English as Kim, Dr. Yehoshua's assistant. "
            f"{identity_instruction}"
            "You may handle clients, providers, investors or people interested in Tesca Elements, Ignis, AI People or other projects. "
            "Give general service information and take messages, but do not invent specific details. "
            "Allowed commercial areas include AI automation, technology and business consulting, branding, processes, human development, "
            "financial analysis, portfolio operation, hedge fund and venture capital.\n"
            "If the call is commercial for AI People, sell as a professional consultant: listen with empathy, ask about the pain, "
            "deepen around the cost of staying the same, contrast incomplete solutions, show the desired outcome and propose a meeting with Dr. Yehoshua. "
            "Do not promise ROI, returns or guaranteed results; mention indicative ranges only if the conversation asks for them.\n"
            "Privacy rule: you can only discuss the caller's own pending items if identity is clear. "
            "Do not reveal third-party tasks, other client data or the doctor's general pending items. If they ask for something sensitive, "
            "say you will register it for the doctor to review.\n\n"
            f"Posicionamiento Ai People: {getattr(kim, 'AI_PEOPLE_SALES_POSITIONING', '')}\n"
            f"Playbook comercial Ai People: {getattr(kim, 'AI_PEOPLE_SALES_PLAYBOOK', '')}\n"
            f"Discovery comercial Ai People: {getattr(kim, 'AI_PEOPLE_DISCOVERY_FLOW', '')}\n"
            f"Guardrails comerciales: {getattr(kim, 'AI_PEOPLE_COMMERCIAL_GUARDRAILS', '')}\n\n"
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
            "THIRD-PARTY CONTEXTUAL CALL MODE.\n"
            "The person who answers is NOT necessarily the doctor. Do not greet them as doctor.\n"
            "Introduce yourself in English as Kim, Dr. Yehoshua's assistant, and execute the concrete mission.\n"
            "Your first phrase should greet the recipient by name if available and say you are Kim, "
            "Dr. Yehoshua's assistant. Never start with 'hello doctor' in this mode.\n"
            "Do not say you lack context; the context is below. Ask clear questions, listen to the answer, "
            "thank them and close naturally. Do not read the full context aloud: use it to act. "
            "At the end, the call will be saved to report back to the doctor.\n\n"
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
            "You are Kim Live speaking by phone with Dr Yehoshua. "
            "Speak in English by default from the first turn. Listen for instructions, keep the conversation brief, "
            "and when the doctor requests a task, confirm that it is registered in BIFROST/Kim Live. Do not sound like an IVR. "
            "If you cannot execute an action directly from the call, clearly say that you are saving it for execution."
        )
    return {
        "type": "session.update",
        "session": {
            "type": "realtime",
            "model": kim.REALTIME_MODEL,
            "output_modalities": ["audio"],
            "instructions": (
                f"{getattr(kim, 'active_voice_style', lambda: 'Speak in a feminine, natural and fluid English voice by default.')()} "
                "This call is coming through Twilio Media Streams: it shares memory and tone with local Kim, "
                "but it is a phone channel distinct from the local/web interface. "
                "Default to English unless the caller explicitly requests Spanish or another language. "
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
                    "voice": getattr(kim, "active_realtime_voice", lambda: kim.REALTIME_VOICE)(),
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
                "Greet Dr. Yehoshua naturally in English as Kim. Tell him you are in phone mode "
                "and ask what he wants to review or execute now."
            )
        elif profile.get("known_contact"):
            greeting_instruction = (
                "Answer in English as an executive assistant and use this person's prior context. "
                f"Greet them by name: 'Hi, {label}, this is Kim, Dr. Yehoshua's assistant. "
                "Good to hear from you again. Should we continue what we had pending, or how can I help today?' "
                "Continue that person's own thread and pending items. If there is commercial interest, guide discovery: pain, "
                "cost of staying the same, previous attempts, ideal outcome and a meeting with the doctor. "
                "Do not reveal sensitive data or third-party pending items; if identity is uncertain, confirm gently before sharing details."
            )
        else:
            greeting_instruction = (
                "Answer in English as an executive assistant without sounding like an IVR: "
                "'Hi, this is Kim, Dr. Yehoshua's assistant. At AI People we help companies with AI automation, "
                "technology consulting, processes, branding and financial analysis. May I ask your name?' "
                "After they give their name, use it and continue naturally: "
                "'Nice to meet you, Jorge. To understand you well, what operational or commercial problem would you like to solve with AI?' "
                "Then identify company, role, reason for calling, and whether they are calling about Tesca Elements, Ignis, AI People or another project. "
                "If they are an AI People prospect, tactfully deepen around pain, cost of staying the same, failed solutions, ideal outcome and two times for a meeting with Dr. Yehoshua."
            )
    elif call_context:
        opening = (call_context.get("message_to_deliver") or "").strip()
        opening_instruction = (
            f"Empieza con esta frase o una version natural muy cercana: '{opening}'. "
            if opening
            else "Recommended first phrase: 'Hi, this is Kim, Dr. Yehoshua's assistant.' "
        )
        greeting_instruction = (
            "This call is for a third party. Introduce yourself in English as Kim, Dr. Yehoshua's assistant. "
            f"La persona objetivo es {call_context.get('contact_name') or 'el destinatario'}. "
            f"Ejecuta esta mision desde el primer turno: {call_context.get('objective') or call_context.get('instructions') or call_context.get('call_context')}. "
            f"{opening_instruction}"
            "No digas 'hola doctor' salvo que confirmes que quien contesta es el doctor."
        )
    else:
        greeting_instruction = (
            "Greet the doctor in English with one brief sentence. "
            "Tell him this is the Realtime phone version and he can speak now."
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
    saved = False
    try:
        async with websockets.connect(REALTIME_WS, additional_headers=headers) as openai_ws:
            kim.set_twilio_realtime_health(
                "ok",
                reason="openai_realtime_connected",
                metadata={"session_id": session_id, "call_sid": call_sid, "context_id": context_id},
                notify=False,
            )
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
                        if event_type == "error":
                            log(f"OpenAI event error {json.dumps(response.get('error') or response, ensure_ascii=False)[:1600]}")
                        else:
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
                saved = True
                log(f"Saved session={session_id}")
    except Exception as exc:
        if isinstance(exc, websockets.exceptions.ConnectionClosedOK) or "received 1000 (OK)" in str(exc):
            log(f"OpenAI bridge closed normally session={session_id}")
            return
        error_text = kim.brief(str(exc), 800)
        reason = "insufficient_quota" if "insufficient_quota" in error_text else "openai_realtime_bridge_error"
        if reason == "insufficient_quota" or "api.openai.com" in error_text or "401" in error_text:
            kim.set_twilio_realtime_health(
                "unavailable",
                reason=reason,
                metadata={"session_id": session_id, "call_sid": call_sid, "context_id": context_id, "error": error_text},
            )
        else:
            kim.notify_kim_live(
                "twilio_realtime_bridge_error",
                "Twilio realtime bridge closed",
                error_text,
                severity="warning",
                metadata={"session_id": session_id, "call_sid": call_sid, "context_id": context_id},
            )
        transcript.append(f"[system] OpenAI Realtime error: {error_text}")
        kim.append_memory(
            "twilio_realtime_openai_error",
            {"session_id": session_id, "call_sid": call_sid, "context_id": context_id, "error": error_text},
        )
        log(f"OpenAI bridge error session={session_id} error={error_text}")
        if not saved:
            await save_twilio_realtime_call(session_id, caller, called, transcript, call_sid, context_id=context_id, call_context=call_context)
            log(f"Saved session={session_id}")


async def main():
    async with websockets.serve(handle_media_stream, HOST, PORT, ping_interval=20, ping_timeout=20):
        log(f"Kim Twilio Realtime bridge running ws://{HOST}:{PORT}/twilio/media")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
