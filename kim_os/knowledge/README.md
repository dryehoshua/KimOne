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

