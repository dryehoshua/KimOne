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


def bridge_session_config(call_sid="", caller="", called=""):
    local_context = kim.context_brief()
    return {
        "type": "session.update",
        "session": {
            "type": "realtime",
            "model": kim.REALTIME_MODEL,
            "output_modalities": ["audio"],
            "instructions": (
                "Eres Kim Live hablando por telefono con Dr Yehoshua. "
                "Habla en espanol mexicano, femenino, natural y fluido. "
                "Esta llamada viene por Twilio Media Streams y debe sentirse como Kim Live local. "
                "Escucha instrucciones, conversa breve, y cuando el doctor pida una tarea confirma que queda "
                "registrada en BIFROST/Kim Live. No uses tono de IVR. Si no puedes ejecutar una accion "
                "directamente desde la llamada, di claramente que la guardas para ejecucion.\n\n"
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


def initial_greeting_event():
    return {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": (
                        "Saluda al doctor en español con una frase breve. "
                        "Dile que esta es la version Realtime por telefono y que ya puede hablarte."
                    ),
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


async def save_twilio_realtime_call(session_id, caller, called, transcript, call_sid):
    text = (
        "Canal: Twilio Media Streams + OpenAI Realtime\n"
        f"CallSid: {call_sid}\n"
        f"From: {caller}\n"
        f"To: {called}\n\n"
        + "\n".join(transcript).strip()
    )
    try:
        kim.save_call_record(
            {
                "session_id": session_id,
                "text": text,
                "started_at": kim.now_iso(),
                "title": f"Twilio Realtime call {caller or 'unknown'}",
            }
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
    session_id = kim.phone_session_id({"CallSid": call_sid}) if call_sid else "PHONE-RT-" + kim.now_iso()

    stream_sid = None
    latest_media_timestamp = 0
    last_assistant_item = None
    response_start_timestamp_twilio = None
    mark_queue = []
    transcript = []

    kim.append_memory(
        "twilio_realtime_connected",
        {"session_id": session_id, "caller": caller, "called": called, "call_sid": call_sid},
    )
    log(f"Twilio connected session={session_id}")

    headers = {
        "Authorization": f"Bearer {kim.load_openai_key()}",
        "OpenAI-Safety-Identifier": "dr-yehoshua-kim-twilio-realtime",
    }
    async with websockets.connect(REALTIME_WS, additional_headers=headers) as openai_ws:
        await openai_ws.send(json.dumps(bridge_session_config(call_sid=call_sid, caller=caller, called=called)))
        await openai_ws.send(json.dumps(initial_greeting_event()))
        await openai_ws.send(json.dumps({"type": "response.create"}))

        async def receive_from_twilio():
            nonlocal stream_sid, latest_media_timestamp, response_start_timestamp_twilio, last_assistant_item
            async for message in twilio_ws:
                data = json.loads(message)
                event = data.get("event")
                if event == "start":
                    stream_sid = data.get("start", {}).get("streamSid")
                    call = data.get("start", {}).get("callSid") or call_sid
                    if call and not transcript:
                        transcript.append(f"[system] Twilio Media Stream iniciado: {call}")
                    response_start_timestamp_twilio = None
                    latest_media_timestamp = 0
                    last_assistant_item = None
                    log(f"Stream started {stream_sid}")
                elif event == "media":
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
            await save_twilio_realtime_call(session_id, caller, called, transcript, call_sid)
            log(f"Saved session={session_id}")


async def main():
    async with websockets.serve(handle_media_stream, HOST, PORT, ping_interval=20, ping_timeout=20):
        log(f"Kim Twilio Realtime bridge running ws://{HOST}:{PORT}/twilio/media")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
