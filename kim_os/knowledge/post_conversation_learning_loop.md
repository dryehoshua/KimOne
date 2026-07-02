# Post-Conversation Learning Loop

This is the standard for turning conversations into useful Kim memory without contaminating tools, kernel code or financial ledgers.

## Purpose

Every meaningful interaction can teach Kim something. The system must not save everything blindly. It must classify, distill and route the learning.

## Inputs

- Kim Live text conversations.
- WhatsApp threads.
- Twilio calls and transcripts.
- Meetings and meeting summaries.
- Telegram tasks.
- Codex implementation sessions.
- Uploaded documents, screenshots and receipts.

## Classification

The librarian pass must classify each candidate into exactly one primary destination:

- `behavior_update`: how Kim should act, speak, follow up, confirm, sell or protect privacy.
- `miu_update`: intelligence unique to Dr. Yehoshua, his companies, clients, doctrine, preferences, standards and terminology.
- `knowledge_update`: reusable facts, references, methods or domain concepts.
- `tool_update`: API formats, required fields, retry rules, schemas, command contracts or executable capabilities.
- `task_update`: one-off or scheduled action.
- `ledger_update`: structured financial/accounting event; never rely only on chat memory.
- `transient_only`: useful now, not permanent.
- `secret_rejected`: credentials, private keys or sensitive material that must not enter docs.

## Routing Rules

- If it changes how Kim behaves, update `kim_os/behavior`.
- If it is part of Dr. Yehoshua's loaded intelligence, update `intelligences/miu` and the portable MIU roots in BIFROST.
- If it is stable domain knowledge, update the relevant BIFROST knowledge library.
- If it tells Kim how to use a tool, update the tool README, manifest, schema or test fixtures.
- If it is a financial operation, update the ledger/tool source of truth first; memory may summarize after.
- If it contradicts old memory, mark the old item as `superseded` instead of leaving both as active truth.
- If it is a secret, reject it from markdown memory and store only a non-sensitive reference to where secure storage should be used.

## Output Contract

A learning pass should produce:

```json
{
  "source": "conversation|call|whatsapp|meeting|codex",
  "source_id": "stable source id when available",
  "date": "YYYY-MM-DD",
  "classification": "miu_update",
  "destination": "BIFROST/MEMORY/MIU/...",
  "summary": "what changed",
  "evidence": "short pointer to transcript or artifact",
  "supersedes": ["optional old ids"],
  "requires_action": false
}
```

## Acceptance Criteria

- Kim can explain where the learned item lives.
- Kim can distinguish current truth from superseded context.
- Kim does not use old conversation fragments when a structured ledger, tool registry or fresh MIU card says otherwise.
- A new Codex session can read BIFROST and understand what Kim learned without replaying the whole chat history.

