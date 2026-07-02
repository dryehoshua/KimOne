# BIFROST Docs Manifest

Last updated: 2026-07-02

This Git repo contains the Kim Live source, not the entire BIFROST operating
folder. The full portable memory/docs folder lives outside this repo:

```text
/Users/dryehoshuapython/Documents/BIFROST
```

## Current Source

```text
/Users/dryehoshuapython/Documents/BIFROST/repos/KimOne/kim_live
```

Runtime:

```text
/Users/dryehoshuapython/.kim_live
```

Current backend version:

```text
1.5.70
```

## Must-Copy BIFROST Docs

If moving to another machine or reconstructing from backup, copy the whole
`BIFROST` folder. Minimum docs to read:

- `BIFROST/README.md`
- `BIFROST/AGENT_HANDOFF.md`
- `BIFROST/docs/CURRENT_STATE_SUMMARY_FOR_NEW_CODEX.md`
- `BIFROST/docs/MIGRATION_RUNBOOK.md`
- `BIFROST/docs/DOCUMENTATION_INDEX_2026-06-07.md`
- `BIFROST/docs/GITHUB_ACCESS_AND_SYNC.md`
- `BIFROST/information/credentials_map.md`
- `BIFROST/information/programs.md`
- `BIFROST/information/channels.md`
- `BIFROST/MEMORY/MIU/README.md`
- `BIFROST/KNOWLEDGE/MIU/README.md`
- `KimOne/kim_os/README.md`
- `KimOne/intelligences/miu/README.md`
- `KimOne/kimtools/ignis_financials/README.md`

## Modular Architecture

Kim is being separated into:

- Kim OS kernel.
- Behavior prompt.
- MIU loaded intelligence.
- Knowledge libraries.
- Tools.
- External libraries.

`server.py` remains production compatibility glue while modules are extracted.

## Recent Critical Memory

- `BIFROST/MEMORY/context/kim_0096_sr_eli_order_state_and_sale_confirmation_2026-06-05.md`
- `BIFROST/MEMORY/context/kim_0097_google_maps_bridge_2026-06-05.md`
- `BIFROST/MEMORY/context/kim_0098_bifrost_documentation_refresh_2026-06-07.md`

## Current GitHub Sync

As of 2026-06-07, GitHub SSH access is configured and
`bifrost/kim-live-initial` is synced through:

```text
3e6f184 Update BIFROST documentation handoff
```

Remote:

```text
git@github.com:dryehoshua/KimOne.git
```

See the full local doc:

```text
BIFROST/docs/GITHUB_ACCESS_AND_SYNC.md
```

## Secret Rule

Do not commit Keychain secrets, API keys, passwords, tokens, PINs or OAuth
client secrets. BIFROST docs record service names only.
