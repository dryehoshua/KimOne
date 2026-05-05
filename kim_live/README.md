# Kim Live

Kim Live is the local conversation surface for BIFROST.

Current version: `1.4.0`

## URL

```text
http://127.0.0.1:8765
```

## Current Capabilities

- Branded local browser page: Tesca Elements Kim Live.
- GPT-like conversation layout with current session and saved conversations on the left.
- Simplified conversation controls: Conversar, Terminar conversacion, Guardar en memoria, Redactar documento, Convertir en tarea y ejecutar.
- Large microphone visual, Kim avatar, and listening/speaking wave states.
- Speaker-labeled conversation compilation for Dr. Yehoshua and Kim.
- Browser dictation when Web Speech is available.
- OpenAI Realtime voice through browser WebRTC.
- Realtime input transcription through `gpt-4o-mini-transcribe`.
- Realtime tool calling for `kim_research_web` and `kim_draft_document`.
- OpenAI API key stored in macOS Keychain, not in page code.
- Save notes to `BIFROST/MEMORY/inbox`.
- Save full calls to `BIFROST/MEMORY/calls/YYYY-MM-DD`.
- Show saved conversation history from `/api/conversations`.
- Read saved conversations by unique session ID from `/api/conversation`.
- Drag-and-drop or browse file upload while a conversation is active.
- File uploads are copied to `BIFROST/MEMORY/uploads/YYYY-MM-DD`, text is extracted when possible, summarized, classified, and added to the conversation context.
- OpenAI Responses API with `web_search` is used for internal research; there is no manual search panel in the frontend.
- Drafted documents are saved to `BIFROST/MEMORY/documents/YYYY-MM-DD`.
- Convert a conversation into a Telegram/Codex task.

## Current Limits

- Realtime voice still needs the user to approve microphone access in the browser.
- Safari may not support dictation the same way Chrome does.
- Conversation-to-execution remains explicit: save or convert to task before Codex runs work.
- Memory analytics were intentionally deferred after the v1.4 frontend cleanup.
- PDF extraction depends on available local Python PDF libraries; text-like files, Markdown, CSV, JSON, HTML, DOCX, XLSX, and PPTX have built-in extraction paths.

## Local Endpoints

```text
/api/status
/api/context
/api/conversations
/api/conversation
/api/memory-analytics
/api/openai-status
/api/realtime-token
/api/research-agent
/api/draft-document
/api/upload-memory-file
/api/save
/api/execute
```

## Runtime

```text
/Users/dryehoshuapython/Library/LaunchAgents/com.codex.kim.live.plist
```
