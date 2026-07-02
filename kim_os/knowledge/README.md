# Kim OS Knowledge Layer

The knowledge layer routes memory without mixing it with tools or kernel code.

## Knowledge Types

- `miu_loaded_intelligence`: Dr. Yehoshua's unique loaded intelligence.
- `company_knowledge`: Tesca, Ignis, AI People and future companies.
- `client_preferences`: Sr. Eli report style, Naomi thread, family privacy, etc.
- `operational_standards`: how to prepare reports, confirmations, follow-up loops.
- `external_references`: docs, websites, APIs, public material.
- `transient_context`: recent conversation window, not permanent truth.

## Canonical Storage

Portable BIFROST roots:

```text
BIFROST/MEMORY/MIU
BIFROST/KNOWLEDGE/MIU
BIFROST/MEMORY/knowledge
BIFROST/MEMORY/context
```

Runtime may cache knowledge under:

```text
/Users/dryehoshuapython/.kim_live/MEMORY
```

Runtime cache is not the canonical portable source unless mirrored into BIFROST.

## Rule

Tools may read knowledge, but tools must not become knowledge.

Example:

- The Ignis tool can read that Sr. Eli wants a Balance de Crédito at the end.
- The Ignis tool should not store Tesca philosophy.
- MIU stores the preference; the tool executes the report format.

## Automatic Update Policy

After every meaningful conversation, Kim OS should run the post-conversation learning loop:

`kim_os/knowledge/post_conversation_learning_loop.md`

The loop must decide whether new information updates behavior, MIU, knowledge, tools, tasks, ledgers or only transient context.

This is mandatory because conversations are noisy. Kim should not operate from raw chat fragments when a distilled card, ledger event or tool contract exists.

Priority order for operational truth:

1. Structured ledger, database or API confirmation.
2. Tool manifest, schema or README.
3. Fresh MIU or knowledge card.
4. Recent transcript evidence.
5. Older memory only if not superseded.
