# Kim Live

Kim Live is the local conversation surface for BIFROST.

## URL

```text
http://127.0.0.1:8765
```

## Current Capabilities

- Branded local browser page: Tesca Elements Kim Live.
- Simplified conversation controls: Conversar, Terminar conversacion, Guardar en memoria, Convertir en tarea y ejecutar.
- Chat-style sections for Kim Live Conversations and Codex handoff notes.
- Large microphone visual, Kim avatar, and listening/speaking wave states.
- Speaker-labeled conversation compilation for Dr. Yehoshua and Kim.
- Browser dictation when Web Speech is available.
- OpenAI Realtime voice through browser WebRTC.
- Realtime input transcription through `gpt-4o-mini-transcribe`.
- OpenAI API key stored in macOS Keychain, not in page code.
- Save notes to `BIFROST/MEMORY/inbox`.
- Convert a conversation into a Telegram/Codex task.

## Current Limits

- Realtime voice still needs the user to approve microphone access in the browser.
- Safari may not support dictation the same way Chrome does.
- Conversation-to-execution remains explicit: save or convert to task before Codex runs work.

## Local Endpoints

```text
/api/status
/api/openai-status
/api/realtime-token
/api/save
/api/execute
```

## Runtime

```text
/Users/dryehoshuapython/Library/LaunchAgents/com.codex.kim.live.plist
```
