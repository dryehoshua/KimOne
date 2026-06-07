# Kim Live

Last updated: 2026-06-07

Kim Live is the local/web conversation surface for BIFROST.

Current backend version:

```text
1.5.70
```

## URLs

```text
http://127.0.0.1:8765
https://kim.aipeople.app
```

Private `/api/*` endpoints require web login. A direct unauthenticated terminal
request may return `AUTH_REQUIRED`.

Public health for phone bridge:

```text
http://127.0.0.1:8765/twilio/health
```

## Current Capabilities

- Public AI People landing and private authenticated Kim Live app.
- GPT-like saved conversations and active live session UI.
- Web/local voice through OpenAI Realtime where browser microphone permissions
  and API quota allow it.
- Conversation transcripts and autosave into BIFROST.
- Memory search across transcripts and real BIFROST files.
- File upload and file knowledge cards.
- Secure BIFROST export with ZIP plus manifest.
- Local CRM, person contexts and context blocks.
- Twilio inbound/outbound calls, SMS and WhatsApp.
- WhatsApp thread memory and default doctor WhatsApp routing.
- Pipedrive people/deals/activities/notes with confirmation.
- ClickUp task/comment/update actions with confirmation.
- Notion routing by access inventory and local outbox fallback.
- Hostinger mailboxes for read/send/reply with confirmation.
- Gmail OAuth path for Google mail, scope dependent.
- Zoom meeting/invite/transcript workflow.
- Google Maps place/geocode/route/timezone bridge.
- Market price validation and Sr. Eli portfolio reporting safeguards.

## Current Runtime

```text
/Users/dryehoshuapython/.kim_live
```

LaunchAgents:

```text
/Users/dryehoshuapython/Library/LaunchAgents/com.codex.kim.live.plist
/Users/dryehoshuapython/Library/LaunchAgents/com.codex.kim.twilio-realtime.plist
```

## Source Of Truth

This folder in the KimOne repo is source of truth:

```text
/Users/dryehoshuapython/Documents/BIFROST/repos/KimOne/kim_live
```

Do not use the old helper copy under `BIFROST/kimtools/voice/kim_live` as
current source unless it has been rebuilt from this repo.

## Important Files

- `server.py`: main HTTP server, API bridge, frontend endpoints and integrations.
- `twilio_realtime_bridge.py`: Twilio media stream to OpenAI realtime bridge.
- `index.html`: public/private UI.
- `API_BRIDGE.md`: bridge capability spec and version history.
- `context/portfolio_report_overrides.json`: portfolio/report overrides.

## Compile And Restart

```bash
cd /Users/dryehoshuapython/Documents/BIFROST/repos/KimOne
python3 -m py_compile kim_live/server.py kim_live/twilio_realtime_bridge.py
cp kim_live/server.py /Users/dryehoshuapython/.kim_live/server.py
cp kim_live/twilio_realtime_bridge.py /Users/dryehoshuapython/.kim_live/twilio_realtime_bridge.py
launchctl kickstart -k gui/$(id -u)/com.codex.kim.live
```

## Current Limits

- OpenAI Realtime quota/saldo can break phone/voice before Twilio is at fault.
- Zoom OAuth requires exact redirect URL on the same app credentials.
- Notion direct writes require shared pages/databases.
- Third-party sends/calls/writes require confirmation.
- GitHub push is blocked until credentials are restored.
